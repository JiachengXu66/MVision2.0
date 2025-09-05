import os
import gi
gi.require_version('Gst','1.0')
from gi.repository import Gst, GLib
import signal
Gst.init(None)

import asyncio
import json
import threading
from modules.classes import PipelineStorage

pipelines = PipelineStorage()

async def InitialiseGStreamer():
    """Function to initialise the GStreamer mainloop
       1. Create GSTloop object
       2. Run GSTloop within a separate thread
    """
    Gst.init(None)
    loop = GLib.MainLoop()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    thread = threading.Thread(target=loop.run)
    thread.start()
    return loop

async def UpdateSystemCameras(cameras):
    """Function to get connected and available cameras
       1. Create GSTdevicemonitor
       2. Add filter to only monitor video devices
       3. Retrieve display name from each device object
       4. If there are any difference between the existing cameras array and the newCameras then the cameras array is cleared and set to match newCameras
       5. Repeats every 10 seconds
       Args:
        cameras array: current camera names
    """
    while True:
        newCameras = []
        monitor = Gst.DeviceMonitor()
        videoFilter = Gst.Caps.from_string("video/x-raw")
        monitor.add_filter("Video/Source", videoFilter)
        monitor.start()
        for device in monitor.get_devices():
            newCameras.append(device.get_display_name())
        monitor.stop()
        if set(newCameras) != set(cameras):
            cameras.clear()
            cameras.extend(newCameras) 

        await asyncio.sleep(10)

def GetPipelineState(pipeline):
    """Function to get pipelines CURRENT state
       1. Get all pipeline States
       2. Return current states
       Args:
        pipeline GSTpipeline: pipeline to check the state of
       Returns:
        GSTstate object: state of pipeline
    """
    stateChange, currentState, pendingState = pipeline.get_state(Gst.CLOCK_TIME_NONE)
    return currentState

def AddSink(pipeline, deploymentName, tee, gloopState):
    """Function to get add appsink to a current pipeline. 
       If gloopState is True then it returns False as to not repeat the loop.
       If gloopState is False then pipeline is initialising so the pipeline itself is returned
       1. Create queue and set its properties
       2. Create videoconvert
       3. Create videoscale 
       4. Create appsink and set its properties
       5. Add all elements to the pipeline
       6. Link all elements in chain
       7. Get a new tee src pad
       8. Get the queues sink pad
       9. Link the tees src pad to the queues sink pad
       10.Set all elements to autosync with the pipelines current STATE
       11.Return False or pipeline dependant on gloopState
       Args:
        pipeline GSTpipeline: pipeline to add sink to
        deploymentName string: name to label the elements as
        tee GSTtee: tee object existing on the given pipeline
        gloopState bool: indicates whether this action is performing in the GLOOP or not
       Returns:
        bool: whether GLOOP should repeat or not (false so it shouldnt)
        pipeline: pipeline object for initialisation
    """
    queue = Gst.ElementFactory.make("queue", f"queue_{deploymentName}")
    queue.set_property("leaky", 2)
    queue.set_property("max-size-buffers", 5)
    queue.set_property("max-size-time", 16000000)

    videoconvert = Gst.ElementFactory.make("videoconvert", f"videoconvert_{deploymentName}")
    videoscale = Gst.ElementFactory.make("videoscale", f"videoscale_{deploymentName}")
    
    sink = Gst.ElementFactory.make("appsink", f"sink_{deploymentName}")
    sink.set_property("emit-signals", True)  
    sink.set_property("sync", False)
    sink.set_property("max-buffers", 5)  
    sink.set_property("drop", True) 


    if not all([queue, videoconvert, videoscale, sink]):
        print("Failed to create elements for new sink")
        return

    pipeline.add(queue)
    pipeline.add(videoconvert)
    pipeline.add(videoscale)
    pipeline.add(sink)

    if not queue.link(videoconvert):
        print("Failed to link queue to videoconvert")
    if not videoconvert.link(videoscale):
        print("Failed to link videoconvert to videoscale")
    if not videoscale.link(sink):
        print("Failed to link videoscale to sink")

    padTemplate = tee.get_pad_template("src_%u")
    srcPad = tee.request_pad(padTemplate, None, None)
    sinkPad = queue.get_static_pad("sink")
    if srcPad.link(sinkPad) != Gst.PadLinkReturn.OK:
        print("Failed to link tee to queue")
    
    ret = queue.sync_state_with_parent()
    print(f"Syncing queue state with parent returned: {ret}")
    ret = videoconvert.sync_state_with_parent()
    print(f"Syncing videoconvert state with parent returned: {ret}")
    ret = videoscale.sync_state_with_parent()
    print(f"Syncing videoscale state with parent returned: {ret}")
    ret = sink.sync_state_with_parent()
    print(f"Syncing sink state with parent returned: {ret}")
    if gloopState:
        return False
    else:
        return pipeline

def GetCameraPath(camera):
    """Function to retrieve the system path of a camera based on its display name
    1. Create a device monitor
    2. Set a filter for video sources only
    3. For each device check if it matches camera name
    4. Retrieve the properties of the matched device
    5. Extract the device path from the properties of the device
    6. Return the camera system path
    Args:
        camera string: The display name of the camera
    Returns:
        string: The system path of the camera, or None if missing
    """
    monitor = Gst.DeviceMonitor()
    videoFilter = Gst.Caps.from_string("video/x-raw")
    monitor.add_filter("Video/Source", videoFilter)
    monitor.start()
    deviceObject = None
    for device in monitor.get_devices():
        if device.get_display_name() == camera:
            deviceObject = device
            break
    monitor.stop()
    props = deviceObject.get_properties()
    cameraPath = props.get_string("device.path")
    return cameraPath

def RemoveSink(pipeline, deploymentName, tee):
    """Function to remove pipeline elements for a given deployment
       1. Retrieve elements by name from the pipeline
       2. Set the state of each retrieved element to NULL
       3. Bottom to top, unlink each element
       4. Release the request pad from the tee and unlink it from the queue
       5. Remove elements from the pipeline
       6. Return False to indicate completed
    Args:
        pipeline GSTpipeline: pipeline to add sink to
        deploymentName string: name to label the elements as
        tee GSTtee: tee object existing on the given pipeline
    Returns:
        bool: False to indicate to stop loop (external)
"""
    queue = pipeline.get_by_name(f"queue_{deploymentName}")
    videoconvert = pipeline.get_by_name(f"videoconvert_{deploymentName}")
    videoscale = pipeline.get_by_name(f"videoscale_{deploymentName}")
    sink = pipeline.get_by_name(f"sink_{deploymentName}")
    for element in (sink, videoscale, videoconvert, queue):
        if element:
            print(element)
            element.set_state(Gst.State.NULL)
    if sink and videoscale:
        videoscale.unlink(sink)
    if videoconvert and videoscale:
        videoconvert.unlink(videoscale)
    if queue and videoconvert:
        queue.unlink(videoconvert)
    if tee and queue:
        sinkPad = queue.get_static_pad("sink")
        teeSrcPad = sinkPad.get_peer()
        if teeSrcPad:
            tee.release_request_pad(teeSrcPad)
            teeSrcPad.unlink(sinkPad)

    for element in (sink, videoscale, videoconvert, queue):
        if element:
            pipeline.remove(element)
    return False

async def AddNewSink(pipeline, deploymentName, tee):
    """Function to invoke AddSink within the GLoop
    Args:
       pipeline GSTpipeline: pipeline to add sink to
       deploymentName string: name to label the elements as
       tee GSTtee: tee object existing on the given pipeline
    """
    GLib.timeout_add_seconds(1, AddSink, pipeline, deploymentName, tee, True)

async def RemoveExistingSink(pipeline, deploymentName, tee):
    """Function to invoke RemoveSink within the GLoop
    Args:
       pipeline GSTpipeline: pipeline to add sink to
       deploymentName string: name to label the elements as
       tee GSTtee: tee object existing on the given pipeline
    """
    GLib.timeout_add_seconds(1, RemoveSink, pipeline, deploymentName, tee)

async def InitialisePipeline(camera, gloop):
    """Initialises a new GStreamer pipeline for a given camera.
       1. Retrieves camera path (/dev/video0 etc)
       2. Generates pipeline
       3. Adds sink to the pipeline
       4. Adds Gstpipeline to global Pipeline object
    Args:
        camera string: Display name of the camera to initialise a pipeline for
        gloop bool: Legacy
    Returns:
        GstPipeline: New pipeline object
    """
    global pipelines

    name = "initialisation"
    cameraPath = GetCameraPath(camera)
    pipeline, tee = GeneratePipeline(cameraPath)
    pipeline = AddSink(pipeline,name, tee, False)
    pipelines.AddPipeline(camera, name, pipeline, tee)
    return

##Pipeline involving GPU optimised transition between UVYV to RGBA
##UNCOMMENT FOR GPU ACCELERATION
def GeneratePipeline(cameraPath):
    """Function to get add generate section 1 of the pipeline for a given cameraPath.
       This function is specifically utilising NVIDIA Gstreamer Plugins for hardware acceleration, there is also a CPU version
    1. Create pipeline
    2. Create source and set its properties
    3. Create nvvidconv
    4. Create UYVYcapsfilter and set its properties
    5. Create nvvidconv
    6. Create RGBAcapsfilter and set its properties
    7. Create tee
    8. Add all elements to the pipeline
    9. Link all elements in chain
    10.Return pipeline and tee
    Args:
    cameraPath string: camera path of device to create pipeline for
    Returns:
    GSTpipeline object: pipeline created
    GSTtee object: tee of given pipeline
"""
    pipeline = Gst.Pipeline.new(f"dynamic-pipeline-{cameraPath}")
    source = Gst.ElementFactory.make("nvv4l2camerasrc", "source")
    source.set_property("device", cameraPath)

    nvvidconvUYVY = Gst.ElementFactory.make("nvvidconv", "nvvidconv_UYVY")

    capsfilterUYVY = Gst.ElementFactory.make("capsfilter", "caps")
    caps = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=(string)UYVY, width=(int)1920, height=(int)1080, framerate=(fraction)30/1")
    capsfilterUYVY.set_property("caps", caps)

    nvvidconvRGBA = Gst.ElementFactory.make("nvvidconv", "nvvidconv_RGBA")
    capsfilterRGBA = Gst.ElementFactory.make("capsfilter", "RGBA_caps")
    capsRGBA = Gst.Caps.from_string("video/x-raw, format=(string)RGBA")
    capsfilterRGBA.set_property("caps", capsRGBA)

    tee = Gst.ElementFactory.make("tee", "tee")

    pipeline.add(source)
    pipeline.add(nvvidconvUYVY)
    pipeline.add(capsfilterUYVY)
    pipeline.add(nvvidconvRGBA)
    pipeline.add(capsfilterRGBA)
    pipeline.add(tee)

    if not source.link(nvvidconvUYVY):
        print("Failed to link source to nvvidconv_UYVY")
    elif not nvvidconvUYVY.link(capsfilterUYVY):
        print("Failed to link nvvidconv_UYVY to capsfilter_UYVY")
    elif not capsfilterUYVY.link(nvvidconvRGBA):
        print("Failed to link capsfilter_UYVY to nvvidconv_RGBA")
    elif not nvvidconvRGBA.link(capsfilterRGBA):
        print("Failed to link nvvidconv_RGBA to capsfilter_RGBA")
    elif not capsfilterRGBA.link(tee):
        print("Failed to link capsfilter_RGBA to tee")
    else:
        print("Elements linked successfully")
    return pipeline, tee


##Pipeline involving CPU optimised transition between UVYV to RGB
##UNCOMMENT FOR NO GPU ACCELERATION
def GeneratePipelineCPU(cameraPath):
    """Function to get add generate section 1 of the pipeline for a given cameraPath.
       This function is specifically using standard GStreamer functionality with no NVIDIA plugins and no hardware acceleration, there is a GPU version
        1. Create pipeline
        2. Create source and set its properties
        3. Create UYVYcapsfilter and set its properties
        4. Create videoconvert
        5. Create RGBcapsfilter and set its properties
        6. Create tee
        7. Add all elements to the pipeline
        8. Link all elements in chain
        9. Return pipeline and tee
    Args:
        cameraPath string: camera path of device to create pipeline for
    Returns:
        GSTpipeline object: pipeline created
        GSTtee object: tee of given pipeline
    """
    pipeline = Gst.Pipeline.new(f"dynamic-pipeline-{cameraPath}")
    source = Gst.ElementFactory.make("v4l2src", "source")
    source.set_property("device", cameraPath)
    videoConvertInitialise = Gst.ElementFactory.make("videoconvert", "videoconvert")
    capsFilter = Gst.ElementFactory.make("capsfilter", "caps")
    caps = Gst.Caps.from_string("video/x-raw, format=(string)UYVY, width=(int)1920, height=(int)1080, framerate=(fraction)30/1")
    capsFilter.set_property("caps", caps)
    videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert2")
    rgbCapsFilter = Gst.ElementFactory.make("capsfilter", "rgb_caps")
    rgbCaps = Gst.Caps.from_string("video/x-raw, format=(string)RGB")
    rgbCapsFilter.set_property("caps", rgbCaps)
    tee = Gst.ElementFactory.make("tee", "tee")

    pipeline.add(source)
    pipeline.add(videoConvertInitialise)
    pipeline.add(capsFilter)
    pipeline.add(videoconvert)
    pipeline.add(rgbCapsFilter)
    pipeline.add(tee)

    if not source.link(videoConvertInitialise):
        print("Failed to link source to capsfilter")
    elif not videoConvertInitialise.link(capsFilter):
        print("Failed to link capsfilter to nvvidconv")
    elif not capsFilter.link(videoconvert):
        print("Failed to link nvvidconv to videoconvert")
    elif not videoconvert.link(rgbCapsFilter):
        print("Failed to link videoconvert to rgb_capsfilter")
    elif not rgbCapsFilter.link(tee):
        print("Failed to link rgb_capsfilter to tee")
    else:
        print("Elements linked successfully")
    return pipeline, tee

async def ManagePipelines(nodeDevices, gloop):
    """Function to manage the generation of each pipeline for each device in cameras
        1. Get cameras
        2. For each camera initialise its pipeline
        3. Return the global Pipelines object
    Args:
        nodeDevices string: Stringified JSON which contains the "cameras" array for the node
        gloop bool: Legacy
    Returns:
        Pipeline object: Custom pipeline object with all newly initialised pipelines
    """
    global pipelines
    cameras = json.loads(nodeDevices)["cameras"]
    for camera in cameras:
         if not pipelines.get_pipeline(camera):
            await InitialisePipeline(camera, gloop)
    return pipelines

async def PlayPipelines(pipelines):
    """Function to set each pipeline to playing
        1. Extract pipelines from Pipeline Object
        2. For each pipeline set its state to playing
        3. Catch any errors and return them failing the initialisation
        4. Return "Displayed" meaning success
    Args:
        pipelines Pipeline object: Custom pipeline object with all newly initialised pipelines
    Returns:
        string: "Displayed" indicates success
        array: array of errors thrown on attempts to set pipeline to playing
    """
    initialisationErrors = []
    for pipelineName, pipelineInfo in pipelines.items():
        try:
            gstPipeline = pipelineInfo['pipeline'] 
            gstPipeline.set_state(Gst.State.PLAYING)
        except Exception as e:
            initialisationErrors.append(e)
    if initialisationErrors:
        return initialisationErrors
    return "Displayed"

