import requests
import json

def UpdateTaskStatus(taskID, statusValue):
    """Function to update task status
    1. Convert parameters to body format
    2. Send API post to change status
    3. Display response to console

    Args:
        taskID int: task ID of current task that is executing
        statusValue string: the status value to set the task status as
    """
    url = f"http://localhost:3000/tasks/update"
    body = {
        'task_id':taskID,
        'status_value':statusValue
    }
    jsonBody = json.dumps(body)
    headers = {'Content-Type':'application/json'}
    updateResponse = requests.post(url,data=jsonBody,headers=headers)
    print(updateResponse.json()[0]['update_model_task_status'])

async def CreateModelEntry(taskID, folderName):
    """Function to update create model
    1. Convert parameters to body format
    2. Send API post to create model from task
    3. Return whether creation Failed (False) or Succeeded (True)

    Args:
        taskID int: task ID of current task that is executing
        folderName string: name of location in the model repo where the triton model directory is contained
    """
    url = f"http://localhost:3000/models/create"
    body = {
        'task_id':taskID,
        'location_name':folderName
    }
    jsonBody = json.dumps(body)
    headers = {'Content-Type':'application/json'}
    try:
        creationResponse = requests.post(url,data=jsonBody,headers=headers)
        print(creationResponse.json()[0]['insert_models'])
        return True
    except:
        return False