import requests
import json
import configparser
import getpass
import ast

async def ExtractList(configString):
    """Function to extract list from a configParser string
    Args:
        configString string: array from config in string form
    Returns:
        array: array from config in list form or blank if failed
    """
    try:
        return ast.literal_eval(configString)
    except ValueError:
        return []

async def GetDeviceID(camera, nodeConfig):
    """Function to get device ID from master server given camera name
    Args:
        camera string: camera name
        nodeConfig ConfigParser: config data for the ndoe
    Returns:
        response: response from master server if successful
    """
    params = {"deviceName":camera}
    headers = {'Content-Type':'application/json'}
    try:
        return requests.get(f"http://{nodeConfig['CONNECTION']['master_ip']}:{nodeConfig['CONNECTION']['master_port']}/nodes/device/name",params=params,headers=headers)
    except:
        return
    
async def GetDeploymentModels(cameraID, nodeConfig):
    """Function to get deploymentID and modelID from master server given cameraID
    Args:
        cameraID string: camera ID
        nodeConfig ConfigParser: config data for the ndoe
    Returns:
        response: response from master server if successful
    """
    params = {"node_id":nodeConfig['NODE_INFO']['node_id'], "device_id":cameraID}
    headers = {'Content-Type':'application/json'}
    try:
        return requests.get(f"http://{nodeConfig['CONNECTION']['master_ip']}:{nodeConfig['CONNECTION']['master_port']}/nodes/deployments/active",params=params,headers=headers)
    except:
        return

async def GetModel(modelID, nodeConfig):
    """Function to get model data from master server given modelID
    Args:
        modelID string: model ID
        nodeConfig ConfigParser: config data for the ndoe
    Returns:
        response: response from master server if successful
    """
    headers = {'Content-Type':'application/json'}
    response = requests.get(f"http://{nodeConfig['CONNECTION']['master_ip']}:{nodeConfig['CONNECTION']['master_port']}/models/id/{modelID}",headers=headers)
    body = response.json()
    print(body)
    return body[0]['get_model'][0]

async def RetrieveActiveDeployments(camera):
    """Function to get active deployments from master server given camera name
    Args:
        camera string: camera name
    Returns:
        response: response from master server if successful
    """
    absolutePath = f'/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/node.conf'
    nodeConfig = configparser.ConfigParser()
    nodeConfig.read(absolutePath)
    response = await GetDeviceID(camera, nodeConfig)
    body = response.json()
    cameraID = body[0]['get_device_from_name']['device_id']
    response = await GetDeploymentModels(cameraID, nodeConfig)
    body = response.json()
    return body[0]['get_nodes_deployment_models']['deployments']

async def GatherModelInformation(locationName):
    """Function to get model information from PyTrain config file for model
    Args:
        locationName string: name of model
    Returns:
        height int: height of model input
        width int: width of model input
        classList array: list of classes for model
        inputName string: name of model input
        outputName string: name of model output
    """
    absolutePath = f'/mnt/model_repo/{locationName}/1/model.savedmodel/assets/{locationName}.config'
    modelConfig = configparser.ConfigParser()
    modelConfig.read(absolutePath)
    height = modelConfig['PREDICTION']['height']
    width = modelConfig['PREDICTION']['width']
    classList = modelConfig['PREDICTION']['class_list']
    inputName = modelConfig['PREDICTION']['input_name']
    outputName = modelConfig['PREDICTION']['output_name']
    return height, width, classList, inputName, outputName
