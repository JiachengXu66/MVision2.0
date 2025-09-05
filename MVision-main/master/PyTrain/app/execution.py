from aiohttp import web
import asyncio

from modules.pull_files import PullFiles
from modules.dockerise_model import LaunchContainer
from modules.task_orders import UpdateTaskStatus, CreateModelEntry

async def CreateModel(request):
    """Function to initialise the creation of a model. 
       Called via endpoint of the server at /model/create
    1. Pulls out the task ID supplied in the JSON request body
    2. Updates the task status with "gathering" & creates task to pull files for the dataset
    3. Changes file path to only indicate the folder name (not ./models_task/model_name)
    4. Update the task status and initiate container creation task
    5. Handles the result of the container task. 
       If the result returns an error it sets the task to failed
       If the result returns True in Tuple sets the task to trained
    6. Given a successfully trained task a model entry is created for said new model

    Args:
        request: http object recieved from endpoint
    
    Returns:
        Web.response: Task failure or success
    """
    body = await request.json()
    taskID = body[0]['insert_model_task']
    UpdateTaskStatus(taskID,"gathering")
    imageTag = "cudatf"  
    filesTask = asyncio.create_task(PullFiles(taskID))
    await filesTask
    folderPath = filesTask.result()
    parts = folderPath.split("/")
    folderName = "/".join(parts[2:])
    UpdateTaskStatus(taskID,"training")
    containerTask = asyncio.create_task(LaunchContainer(imageTag, taskID, folderName))
    await containerTask
    if(containerTask.result()[0]):
        UpdateTaskStatus(taskID,"trained")
        print("Success")
    else:
        UpdateTaskStatus(taskID,"failed")
        return web.Response(text=f"Task {taskID} has failed")
    creationTask = asyncio.create_task(CreateModelEntry(taskID, containerTask.result()[1]))
    await creationTask
    if(creationTask.result()):
        UpdateTaskStatus(taskID,"trained")
        print("Success")
    else:
        UpdateTaskStatus(taskID,"failed")
        return web.Response(text=f"Task {taskID} has failed")
    return web.Response(text=f"Task {taskID} has succeeded") 

async def ServerUp():
    """Function to initialise the Server. 
    
        1. Initialises web application
        2. Adds all endpoint routes
        3. Starts server
    """
    server = '0.0.0.0'
    port = 8080
    app = web.Application()
    app.add_routes([web.post('/model/create', CreateModel)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, server, port)
    await site.start()
    print(f"Server ready to recieve model requests http://{server}:{port}")

async def main():
    await ServerUp()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
