import os
import getpass
import requests
import docker
from time import sleep
import shutil
import asyncio

async def GetTaskData(taskID):
    """Function to retrieve model data from the given id:
    1. Retrieves the response
    2. Extracts the .json and its sub structure to get the task data
    3. Returns task data json

    Args:
        taskID int: task ID of current task that is executing

    Returns:
        json: task
    """
    task_result = requests.get(f"http://localhost:3000/tasks/id/{taskID}")
    task = task_result.json()[0]['get_task'][0]
    return task

def CheckForImage(imageTag, client):
    """Function to check if the container image exists already
    1. Checks all containers for provided container image tag (must be 'latest')
    2. Returns True if it exists Returns False if it doesn't

    Args:
        image_tag string: name of the image to be checked for
        client: docker client object
    
    Returns:
        bool: True or False
    """
    images = client.images.list()
    for image in images:
        try:
            if(f'{imageTag}:latest' == str(image.attrs['RepoTags'][0])):
                return True
        except:
            pass
        return False

def BuildImage(client, imageTag):
    """Function to build missing/updated image
    1. Builds image from Docker file present in the current directory
    2. Returns response of the build command.

    Args:
        image_tag string: name of the image to be checked for
        client: docker client object
    
    Returns:
        tuple: (image object, build logs) 
    """
    response = client.images.build(path=".", tag=imageTag, rm=True)
    return response

async def LaunchContainer(imageTag, taskID, folderName):
    """Function to launch a model training container, taking in the image_tag, taskID and folderName. 
    The function:
    1. Retrieves the task data (i.e hyper perameters).
    2. Formats the entry_cmd based on the task data
    3. Creates the volume maps for the container to be connected to the model_repo and source folder
    4. Attempts to login to NVIDIA container repository
    5. Attempts to build container if necessary
    6. Runs the container 
    7. Waits for the container to finish by detecting its final output (confusion matrix file)
    8. Stops and removes the container
    9. Returns True for task status and the modelName

    Args:
        image_tag string: name of the current docker container being used
        taskID int: task ID of current task that is executing
        folderName string: folder name of the source folder which contains /train /test /validation data

    Returns:
        tuple: (TASK STATUS, modelName)
    """
    client = docker.from_env()

    task = await GetTaskData(taskID)

    absPath = f'/home/{getpass.getuser()}/Desktop/MVision/master/PyTrain'
    keyPath = f'/home/{getpass.getuser()}/api.key'
    modelName = f"{task['model_name']}_{taskID}"

    entryCMD = ["python3", "train_model.py",
             "--model_name", modelName,
             "--epochs", str(task['epochs']),
             "--num_frames", str(task['num_frames']),
             "--shuffle_size", str(task['shuffle_size']),
             "--batch_size", str(task['batch_size'])]
    
    volumeMapping = {
                  f"{absPath}/model_tasks/{folderName}": {'bind': '/mnt', 'mode': 'rw'},  
                  f"{absPath}/model_repo": {'bind': '/model_repo', 'mode': 'rw'},
    }
    
    debugMode = False

    try:
        response = client.login(registry="https://nvcr.io", username="$oauthtoken", password=(open(keyPath, "r").read()))

        if debugMode or not CheckForImage(imageTag,client):
            print("Building cudatf image...")
            buildResult = BuildImage(client, imageTag)
        
        container = client.containers.run(f"{imageTag}:latest", 
                            name=modelName, 
                            detach=True,
                            device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])],
                            tty=True, 
                            stdin_open=True, 
                            entrypoint=entryCMD,
                            volumes=volumeMapping)
        
        file = f'{modelName}_training_confusion.png'
        fileStatus = False

        while not fileStatus:
            path = f'../model_repo/{modelName}/1/model.savedmodel/assets/{file}'
            if os.path.exists(path):
                if os.path.isfile(path):
                    fileStatus = True
                else:
                    asyncio.sleep(5)
                    print("files missing")
            else:
                sleep(5)
                print("files missing")
        container.stop()
        container.remove()
        return [True,modelName]
    
    except docker.errors.ContainerError as e:
        print(f"Container run error: {e}")
        return [False,modelName]
    except docker.errors.ImageNotFound as e:
        print(f"Image not found error: {e}")
        return [False,modelName]
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
        return [False,modelName]
