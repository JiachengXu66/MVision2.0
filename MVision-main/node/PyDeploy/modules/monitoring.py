from jtop import jtop
import aiofiles
import datetime
import asyncio
from aiocsv import AsyncDictWriter, AsyncDictReader
import os

from .connection import SendResults

async def CompilePerformanceEntry(jetson, csvLog, description):
    """Function to create log data
       1. Create dict of log information
       2. Append dict to the csvLog array
    Args:
       jetson JTOP: allows for jetson utilisation stats to be accessed
       csvLog array: array containing all unwritten log data
       description string: event description to go with log
    """
    logDict = {"Timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),"Event":description,"Total CPU utilisation %":jetson.cpu['total']['user']+jetson.cpu['total']['nice']+jetson.cpu['total']['system'],"Total CPU RAM utilisation %":(jetson.memory['RAM']['used']/jetson.memory['RAM']['tot'])*100,"Total GPU utilisation %":jetson.gpu['gv11b']['status']['load'],"Total GPU RAM utilisation %":(jetson.memory['RAM']['shared']/jetson.memory['RAM']['tot'])*100,"Total Swap Utilisation %":(jetson.memory['SWAP']['used']/jetson.memory['SWAP']['tot'])*100}
    csvLog.append(logDict)

async def CompileInferenceResult(csvLog, inference, confidencePercentage):
    """Function to create inference data
       1. Create dict of inference information
       2. Append dict to the csvLog array
    Args:
       csvLog array: array containing all unwritten inference data
       inference string: class with highest confidence percentage (inferred class)
       confidencePercentage string: % confidence for given inference 
    """
    logDict = {"Timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),"Inference":inference, "Confidence %":confidencePercentage}
    csvLog.append(logDict)

async def GetLastLine(fileName):
    """Function to get last line of inference CSV
       1. Read in the file
       2. Jump to last row of the read in array
       3. Return said last line
    Args:
       fileName: path of file to load and read in
    Return:
        string: last line of CSV
    """
    async with aiofiles.open(fileName, "r", encoding="utf-8") as file:
        lines = await file.readlines()
        lastLine = lines[-1] if lines else ""
    return lastLine.strip()
    
async def DumpInference(csvLog, fileName, deploymentID, loop, frameCounts):
    """Function to dump inference array into its dedicated CSV
       1. Initialise dumping loops 
       2. Check if file exists
       3. Get last line of CSV
       4. Check if last line is older than 10 minutes, Set loop variable to False if so
       5. Write to CSV
       6. Check if iterator is factor of difference, if so create task to send latest inference data
    Args:
       csvLog array: array containing all unwritten log data
       fileName: path of file to load and read in
       deploymentID: for the given inference
       loop: asyncio loop to create tasks
       frameCounts: legacy (could be set to calculate difference as higher frames means lower inference per minute etc)
    """
    print(f"Dumping Inference {fileName}")
    inferenceActive = True
    iterator = 0
    difference = 12
    while inferenceActive:
        fileExists = os.path.isfile(fileName)
        fields = ["Timestamp","Inference","Confidence %"]
        if fileExists and os.path.getsize(fileName) > 200:
            lastLine = await GetLastLine(fileName)
            latestTimeStamp = lastLine.split(",")[0]
            latestTime = datetime.datetime.strptime(latestTimeStamp, '%Y-%m-%d %H:%M:%S.%f')
            currentTime = datetime.datetime.now()
            timeDifference = (currentTime - latestTime).total_seconds()
            if timeDifference > 600000:
                inferenceActive = False
        async with aiofiles.open(fileName, mode='a') as log:
            writer = AsyncDictWriter(log, fieldnames=fields)
            if not fileExists:
                await writer.writeheader()
            for row in csvLog:
                await writer.writerow(row)
            csvLog.clear()
        if(iterator%difference==0):
            monitoringTask = loop.create_task(RecurringSendData(fileName, deploymentID, difference, loop))
        iterator = iterator + 3
        await asyncio.sleep(3)

async def DumpLogs(csvLog, fileName):
    """Function to dump logs array into its dedicated CSV
       1. Initialise dumping loops 
       2. Check if file exists
       3. Write to CSV
    Args:
       csvLog array: array containing all unwritten log data
       fileName: path of file to load and read in
    """
    print(f"Dumping logs {fileName}")
    while True:
        fileExists = os.path.isfile(fileName)
        fields = ["Timestamp","Event","Total CPU utilisation %","Total CPU RAM utilisation %","Total GPU utilisation %","Total GPU RAM utilisation %","Total Swap Utilisation %"]
        async with aiofiles.open(fileName, mode='a') as log:
            writer = AsyncDictWriter(log, fieldnames=fields)
            if not fileExists:
                await writer.writeheader()
            for row in csvLog:
                await writer.writerow(row)
            csvLog.clear()
        await asyncio.sleep(3)

async def RecurringMonitoring(jetson, csvLog, description, frequency):
    """Function to create log data at a regular frequency
        1. Create log data via CompilePerformanceEntry function
        2. Wait set frequency
    Args:
        jetson JTOP: allows for jetson utilisation stats to be accessed
        csvLog array: array containing all unwritten log data
        description string: event description to go with log
        frequency int: frequency to create log data
    """
    while True:
        await CompilePerformanceEntry(jetson, csvLog, description)
        await asyncio.sleep(frequency)

async def RecurringSendData(fileName, deploymentID, timeDifference, loop):
    """Function to send data that has accumulated since previous sending task
        1. Check file exists and is not empty
        2. Get time threshold and initialise jsonBody string
        3. Read in file and append any data sooner than time threshold
        4. Given that something new has been written to the CSV, create a task for sending results to VLink
    Args:
        fileName: path of file to load and read in
        deploymentID: for the given inference
        timeDifference int: time difference to check for new data
        loop: asyncio loop to create tasks
    """
    if os.path.exists(fileName) and os.path.getsize(fileName) > 0:
        currentDateTime = datetime.datetime.now()
        pastTime = currentDateTime - datetime.timedelta(seconds=timeDifference)
        outputData = {"deployment_id": deploymentID,
                        "data": []}

    async with aiofiles.open(fileName, mode='r', newline='') as file:
        reader = AsyncDictReader(file)
        async for row in reader:
            timestamp = row["Timestamp"]
            dateTime = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

            if dateTime > pastTime:
                dataPoint = {
                    "timestamp": row["Timestamp"],
                    "class": row["Inference"],
                    "confidence": row["Confidence %"]
                }
                outputData['data'].append(dataPoint)
    if outputData['data']:
        print(outputData['data'])
        loop.create_task(SendResults(outputData))
        