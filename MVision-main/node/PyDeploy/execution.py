import json
import configparser
import sys
from aiohttp import web
import asyncio
import getpass
from jtop import jtop
import datetime
import gi
gi.require_version('Gst','1.0')
from gi.repository import Gst
Gst.init(None)

from modules.gstreamer import UpdateSystemCameras, ManagePipelines, InitialiseGStreamer, PlayPipelines, AddNewSink, RemoveExistingSink
from modules.connection import ConfigureConnection, ConnectDevices
from modules.inference import FinaliseInference
from modules.deployments import RetrieveActiveDeployments, GetModel, GatherModelInformation, ExtractList
from modules.classes import PipelineStorage
from modules.monitoring import DumpLogs, CompilePerformanceEntry, RecurringMonitoring


"""Globals:
   Variables initialised to allow global use in endpoints
   Args:
        cameras array: holds all camera names at current time
        pipelines PipelineStorage: custom object to hold ALL generated pipelines at startup. 
                                    indexed via camera name (1 pipeline per camera) followed by an array of variables and GStreamer objects.
        deploymentCount int: holds current number of deployments
        csvLog array: holds current log lines to be printed to CSV
        jetson JTOP object: declares jetson as a global so that when initialised in "main" it can be used throughout the script.
                            Allows for jetson utilisation stats to be accessed
    """
cameras = []
pipelines = PipelineStorage()
deploymentCount = 0
csvLog = []
global jetson

async def InterceptLaunchInference(request):
    """Function called from endpoint "/node/deployments/initialise"
       Aims to initialise a new deployment on an existing pipeline.
    1. Retrieves the deployment information
    2. Retrieve relevant PipelineObject to the deployment based on device name
    3. Retrieve GSTtee object from the PipelineObject
    4. Retrieve GSTpipeline from the PipelineObject
    5. Check if GSTappsink for deployment already exists on GSTpipeline
    6. If GSTappsink exists return "Inference active"
    7. Else Launch inference for deployment

    Args:
        request: http object recieved from endpoint
    Returns:
        Web.response: Inference already active, or set to active
    """
    body = await request.json()
    global jetson
    global csvLog
    global pipeline
    deployment = body['deployment_information'][0]
    pipelineEntry = pipelines.get_pipeline(deployment['device_name'])
    tee = pipelineEntry['tee']
    pipeline = pipelineEntry['pipeline']
    appsink = pipeline.get_by_name(f"sink_deployment_{deployment['deployment_id']}")
    if appsink:
        return web.Response(status=500, text=f"Inference already active for deployment ID: {deployment['deployment_id']}", content_type='application/json')
    loggingTask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f"Launching inference for {deployment['device_name']}"))
    inferenceTask = loop.create_task(LaunchInference(deployment['deployment_id'], deployment['model_id'], pipeline, deployment['device_name'], tee))
    await inferenceTask
    return web.Response(status=200, text="Inference launched", content_type='application/json')

async def InterceptStopInference(request):
    """Function called from endpoint "/node/deployments/stop"
       Aims to stop an existing deployment on an existing pipeline.
    1. Retrieves the deployment information
    2. Retrieve relevant PipelineObject to the deployment based on device name
    3. Retrieve GSTtee object from the PipelineObject
    4. Retrieve GSTpipeline from the PipelineObject
    5. Check if GSTappsink for deployment already exists on GSTpipeline
    6. If GSTappsink doesnt exist return "Inference stopped"
    7. Else Remove existing sink
    8. Check that all elements are no longer present

    Args:
        request: http object recieved from endpoint
    Returns:
        Web.response: Inference already active, or set to active
    """
    body = await request.json()
    global jetson
    global csvLog
    global pipeline
    deployment = body['deployment_information'][0]
    pipelineEntry = pipelines.get_pipeline(deployment['device_name'])
    tee = pipelineEntry['tee']
    pipeline = pipelineEntry['pipeline']
    appsink = pipeline.get_by_name(f"sink_deployment_{deployment['deployment_id']}")
    if not appsink:
        return web.Response(status=500, text=f"Inference already stopped for deployment ID: {deployment['deployment_id']}", content_type='application/json')
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f"Stopping inference for {deployment['device_name']}"))
    removeSinkTask = loop.create_task(RemoveExistingSink(pipeline,f"deployment_{deployment['deployment_id']}",tee))
    while True:
        appsink = pipeline.get_by_name(f"sink_deployment_{deployment['deployment_id']}")
        videoscale = pipeline.get_by_name(f"videoscale_deployment_{deployment['deployment_id']}")
        videoconvert = pipeline.get_by_name(f"videoconvert_deployment_{deployment['deployment_id']}")
        queue = pipeline.get_by_name(f"queue_deployment_{deployment['deployment_id']}")
        if appsink or videoscale or videoconvert or queue:
            print("Items Still Linked")
        else:
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f"Sink successfully removed"))
            break
        await asyncio.sleep(1)
    return web.Response(status=200, text="Inference Stopped", content_type='application/json')

async def LaunchInference(deploymentID, modelID, pipeline, name, tee):
    """Function called to launch inference
       Aims to add a sink to the relevant pipeline to allow for the deployment inference to initialise
    1. Retrieves model information from API
    2. Retrieves model information from model_repo PyTrain config
    3. Adds new sink
    4. Waits for new sink to be detected
    5. Will time out if longer than "wait" time
    6. Inference is begun
    7. Deployment count is logged 

    Args:
        deploymentID int: deployment ID for deployment
        modelID int: model ID used by the deployment
        pipeline GSTpipeline: pipeline for the device used by the deploymentID
        name string: name of the deployment
        tee GSTtee: tee of the pipeline
    """
    global deploymentCount
    global jetson
    global csvLog
    absolutePath = f'/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/node.conf'
    nodeConfig = configparser.ConfigParser()
    nodeConfig.read(absolutePath)

    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Retrieving model"))
    modelInformation = await GetModel(modelID, nodeConfig)
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Model data retrieved"))

    frameCounts = modelInformation['num_frames']
    tritonLocationName = modelInformation['location_name']
    deploymentName = f"deployment_{deploymentID}"

    height, width, configClasses, inputName, outputName = await GatherModelInformation(tritonLocationName)   
    classList = await ExtractList(configClasses)
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f"Attempting to add sink"))
    createSinkTask = loop.create_task(AddNewSink(pipeline, deploymentName, tee))
    waits = 0
    while True:
        appsink = pipeline.get_by_name(f'sink_{deploymentName}')
        if waits == 60:
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f"Failed to add sink"))
            return
        elif not appsink:
            print("Appsink not found.")
            waits = waits+1
        else:
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f"Sink successfully added"))
            break
        await asyncio.sleep(1)
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Finalising inference"))
    inference_task = loop.create_task(FinaliseInference(pipeline, deploymentID, int(height), int(width), classList, frameCounts, tritonLocationName, deploymentCount, jetson, csvLog, loop, inputName, outputName))
    await inference_task
    deploymentCount = inference_task.result()
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'Inference launched for {name}, Total Deployments: {deploymentCount}'))
    return

async def AvailableNode(request):
    """Function to recieve polling from API
    Args:
        request: http object recieved from endpoint
    Returns:
        Web.response: Available i.e server still online
    """
    return web.Response(text="Available")

async def GetCameras(request):
    """Function to recieve current list of cameras detected by the node
       1. Retrieve nodeID to report back what node the cameras are connected to.
       2. Form jsonBody
       3. Return with response object if an api call
       4. Return with jsonBody if from an internal call
    Args:
        request: http object recieved from endpoint OR "manual" string
    Returns:
        Web.response: Camera jsonBody
        JSON: Camera jsonBody
    """
    global cameras
    absolutePath = f'/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/node.conf'
    nodeConfig = configparser.ConfigParser()
    nodeConfig.read(absolutePath)
    if not request == "manual":
        body =  {
            "get_cameras":{"node_id":nodeConfig['NODE_INFO']['node_id'],
                        "cameras":cameras}
        }
        jsonBody = json.dumps(body)  
        return web.Response(body=jsonBody, content_type='application/json')
    else:
        body =  {"node_id":nodeConfig['NODE_INFO']['node_id'],
                    "cameras":cameras
                    }
        jsonBody = json.dumps(body)  
        return jsonBody

async def ExecuteDeploymentPipeline(name, pipeline, tee):
    """Function to cycle through each deployment initialisation for a given camera
       1. Retrieve deployments for the camera name supplied
       2. For each deployment launch inference
    Args:
        name string: camera name
        pipeline GSTpipeline: pipeline for the camera
        tee GSTtee: tee for the pipeline
    """
    global jetson
    global csvLog
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'Retrieving Deployments for {name}'))
    nodeDeploymentTask = loop.create_task(RetrieveActiveDeployments(name))
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f"Deployments retrieved"))
    await nodeDeploymentTask                    
    deployments = nodeDeploymentTask.result()
    print(deployments)
    if deployments:
        for deployment in deployments:
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'Launching inference for {name}'))
            inferenceTask = loop.create_task(LaunchInference(deployment['deployment_id'], deployment['model_id'], pipeline, name, tee))
            await inferenceTask
        return
    else:
        print(f"No active deployments for camera: {name}")
    return

async def ServerUp():
    """Function to begin server initialisation
       1. Create initial log
       2. Create recurring "Dump logs" task
       3. Create recurring "Monitoring" task
       4. Attempt to connect to the VLink api (fails then quit)
       5. Get cameras currently available
       6. Update status of node cameras (fails then quit)
       7  Initialise GSTLoop
       8. Initialise GSTpipeline for each camera
       9. Set all pipeline states to "playing" (fails then quit)
       10. Foreach pipeline execute deployment initialisation
    """
    global cameras
    global pipelines
    global jetson
    global csvLog

    filePath = f"/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/analytics/Logs/PyDeploy_Run_{datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')}.csv"
    await CompilePerformanceEntry(jetson, csvLog, "Initialising Logging")
    
    server = '0.0.0.0'
    port = 2500
    app = web.Application()
    app.add_routes([web.post('/node/deployments/initialise', InterceptLaunchInference)])
    app.add_routes([web.post('/node/deployments/stop', InterceptStopInference)])
    app.add_routes([web.get('/node/available', AvailableNode)])
    app.add_routes([web.get('/node/cameras', GetCameras)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, server, port)
    await site.start()
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Server Initialised"))

    monitoringTask = loop.create_task(DumpLogs(csvLog, filePath))
    cameraTask = loop.create_task(UpdateSystemCameras(cameras))
    recurringLoggingTask = loop.create_task(RecurringMonitoring(jetson, csvLog, "Logging tick", 3))
    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Configuring Connection"))
    connectionTask =  loop.create_task(ConfigureConnection())
    await connectionTask 
    
    if connectionTask.result() == 'isolated':
        print("The node cannot connect securely with the master server") 
        loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Failed to Establish Connection"))
        sys.exit(1)
    
    elif connectionTask.result() == 'remote':
        loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Connection Established"))
        print("The node has connected securely with the master server")    

        nodeDevices = await GetCameras("manual")
        
        loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Connecting Devices To Master Server"))
        deviceConnectionTask = loop.create_task(ConnectDevices(nodeDevices))
        await deviceConnectionTask
        
        if deviceConnectionTask.result() == 'Synced':
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Connection Established"))

            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Initialising Gstreamer"))
            gStreamerTask = loop.create_task(InitialiseGStreamer())
            await gStreamerTask
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Gstreamer Initialised"))
            gloop = gStreamerTask.result()
            
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Creating Pipelines"))
            pipelineTask = loop.create_task(ManagePipelines(nodeDevices, gloop))
            await pipelineTask
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Pipelines Created"))

            pipelines = pipelineTask.result()
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Set Pipelines State"))
            displayTask = loop.create_task(PlayPipelines(pipelines))

            await displayTask
            if displayTask.result() == 'Displayed':
                loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Pipelines State set to Playing"))
            
                for name, info in pipelines.items():
                    print("Processing deployment pipeline: "+name)
                    loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'Processing Pipeline {name}'))
                    
                    pipeline = info['pipeline'] 
                    tee = info['tee']
                    deploymentPipelines = loop.create_task(ExecuteDeploymentPipeline(name, pipeline, tee))
                    await deploymentPipelines      
            else:
                loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Pipelines State failed to set"))
                for error in displayTask.result():
                    print(error)
                sys.exit(1)
        else:
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, "Failed to Establish Connection"))
            print(f"Initial devices have failed to sync with the master service")
            sys.exit(1)
    else:
        print("Server could not be configured")
        sys.exit(1)
    
async def main():
    await ServerUp()


if __name__ == "__main__":
    with jtop() as jetson: 
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.run_forever()