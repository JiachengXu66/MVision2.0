import os
import getpass
import uuid
import requests
import json
import configparser
import platform 
from datetime import datetime

def CheckUUID(key):
    """Function to check if key is a valid UUID
       1. Check if key is a valid UUID
       2. Return True if it is, False if not
    Args:
        key string: api key from config to check
    Returns:
        bool: True if key is a valid UUID, False if not
    """
    try:
        uuid = uuid.UUID(key, version=4)
        return True
    except ValueError:
        return False

def Reconnect(nodeConfig):
    """Function to reconnect to master server
         1. Create body for request
         2. Send request to master server
    Args:
        nodeConfig ConfigParser: config data for the ndoe
    Returns:
        response: response from master server if successful
    """
    body = {
        "node_key_value":nodeConfig['CONNECTION']['key'],
        "node_id":nodeConfig['NODE_INFO']['node_id']
    }
    jsonBody = json.dumps(body)
    headers = {'Content-Type':'application/json'}
    try:
        return requests.post(f"http://{nodeConfig['CONNECTION']['master_ip']}:{nodeConfig['CONNECTION']['master_port']}/nodes/connect",data=jsonBody,headers=headers)
    except:
        return
    
def Connect(nodeConfig):
    """Function to connect to master server
         1. Create body for request
         2. Send request to master server
    Args:
        nodeConfig ConfigParser: config data for the ndoe
    Returns:
        response: response from master server if successful
    """
    body = {
        "node_key_value":nodeConfig['CONNECTION']['key'],
        "node_name":platform.node(),
        "creation_date":datetime.now().isoformat()
    }
    jsonBody = json.dumps(body)
    headers = {'Content-Type':'application/json'}
    try:
        return requests.post(f"http://{nodeConfig['CONNECTION']['master_ip']}:{nodeConfig['CONNECTION']['master_port']}/nodes/connect",data=jsonBody,headers=headers)
    except:
        return

async def ConnectDevices(jsonBody):
    """Function to connect all devices to master server
         1. Get node config
         2. Send request to master server with camera jsonBody
    Args:
        jsonBody JSON: camera data
    Returns:
        response: response from master server if successful
        string: error message if not successful
    """
    absolutePath = f'/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/node.conf'
    nodeConfig = configparser.ConfigParser()
    nodeConfig.read(absolutePath)
    headers = {'Content-Type':'application/json'}
    response = requests.post(f"http://{nodeConfig['CONNECTION']['master_ip']}:{nodeConfig['CONNECTION']['master_port']}/nodes/connect/devices",data=jsonBody,headers=headers)
    if response and response.json()['status']:
        return response.json()['status']
    else:
        return "Error"
    
async def ConfigureConnection():
    """Function to connect node to master server, based on whether it has been previously connected and initialised or not
         1. Get node config
         2. Check if config contains the node ID for current node and its API key
         3. If so reconnect to master server, if not connect to master server
         4. Returns string to indicate if node is connected or isolated (where isolated means it couldnt connect)
    Returns:
        string: remote if connected, isolated if not connected
    """
    absolutePath = f'/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/node.conf'
    nodeConfig = configparser.ConfigParser()
    nodeConfig.read(absolutePath)
    if os.path.isfile(absolutePath) and CheckUUID(nodeConfig['CONNECTION']['key']):
        if nodeConfig['NODE_INFO']['node_id']:
            connectionResponse = Reconnect(nodeConfig)
            if connectionResponse and connectionResponse.json()['status'] == "Connected":
                return "remote"
            else:
                return "isolated"
        else:
            connectionResponse = Connect(nodeConfig)
            if connectionResponse and connectionResponse.json()['status'] == "Connected":
                nodeConfig['NODE_INFO']['node_id'] = connectionResponse.json()['node_id']
                nodeConfig['NODE_INFO']['node_name'] = platform.node()
                with open(absolutePath, 'w') as oldConfig:
                    nodeConfig.write(oldConfig)
                return "remote"
            else:
                return "isolated"
    else:
        return "isolated"

async def SendResults(body):
    """Function to send inference result to master server
         1. Get node config
         2. Send request to master server with inference jsonBody
    Args:
        jsonBody JSON: inference data
    """
    absolutePath = f'/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/node.conf'
    nodeConfig = configparser.ConfigParser()
    nodeConfig.read(absolutePath)
    jsonBody = json.dumps(body)
    headers = {'Content-Type':'application/json'}
    response = requests.post(f"http://{nodeConfig['CONNECTION']['master_ip']}:{nodeConfig['CONNECTION']['master_port']}/nodes/results",data=jsonBody,headers=headers)