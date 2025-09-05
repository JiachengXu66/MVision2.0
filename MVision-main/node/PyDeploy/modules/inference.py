import cv2
import numpy as np
import tritonclient.http as httpclient
from tritonclient.utils import InferenceServerException
from collections import deque
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import getpass
import asyncio

import gi
gi.require_version('Gst','1.0')
from gi.repository import Gst, GLib
Gst.init(None)

from .gstreamer import GetPipelineState
from .monitoring import CompilePerformanceEntry, CompileInferenceResult, DumpInference

def PreProcessFrameRGBA(frame, WIDTH, HEIGHT):
    """Function to preprocess RGBA frame to correct size, format and type
    1. Resize frame to correct size
    2. Convert frame to RGB
    3. Normalise frame
    Args:
        frame: frame to preprocess
        WIDTH int: width of model input
        HEIGHT int: height of model input
    Returns:
        float32: preprocessed frame
    """
    frameResized = cv2.resize(frame, (WIDTH, HEIGHT))
    frameRGB = cv2.cvtColor(frameResized, cv2.COLOR_RGBA2RGB)
    return frameRGB.astype('float32') / 255.0  

def PreProcessFrameRGB(frame, WIDTH, HEIGHT):
    """Function to preprocess RGB frame to correct size, format and type
    1. Resize frame to correct size
    2. Normalise frame
    Args:
        frame: frame to preprocess
        WIDTH int: width of model input
        HEIGHT int: height of model input
    Returns:
        float32: preprocessed frame
    """
    frameResized = cv2.resize(frame, (WIDTH, HEIGHT))
    frameRGB = cv2.cvtColor(frameResized, cv2.COLOR_BGR2RGB)
    return frameRGB.astype('float32') / 255.0  

def LoadDataRGB(mappedData, inputHeight, inputWidth, width, height, deploymentID, OUTPUT):
    """Function to load RGB frame from RGBA mapped data and optionally save to file
    1. Load frame from mapped data
    2. Optionally save frame to file
    3. Return preprocessed frame
    Args:
        mappedData buffer: mapped data from buffer
        inputHeight int: height of input frame
        inputWidth int: width of input frame
        width int: width of model input
        height int: height of model input
        deploymentID int: deployment ID
        OUTPUT bool: flag to save frame to file
    Returns:
        float32: preprocessed frame
    """
    bufferedData = np.frombuffer(mappedData, dtype=np.uint8)
    if OUTPUT:
        img = Image.frombytes("RGB", (inputWidth, inputHeight), bufferedData)
        img.save(f"deployment_{deploymentID}.png")
    frame = bufferedData.reshape((inputHeight, inputWidth, 3))
    return PreProcessFrameRGB(frame, width, height)  

def LoadDataRGBA(mappedData, inputHeight, inputWidth, width, height, deploymentID, OUTPUT):
    """Function to load RGB frame from RGBA mapped data and optionally save to file
    1. Load frame from mapped data
    2. Optionally save frame to file
    3. Return preprocessed frame
    Args:
        mappedData buffer: mapped data from buffer
        inputHeight int: height of input frame
        inputWidth int: width of input frame
        width int: width of model input
        height int: height of model input
        deploymentID int: deployment ID
        OUTPUT bool: flag to save frame to file
    Returns:
        float32: preprocessed frame
    """
    bufferedData = np.frombuffer(mappedData, dtype=np.uint8)
    if OUTPUT:
        img = Image.frombytes("RGBA", (inputWidth, inputHeight), bufferedData)
        imgRGB = img.convert("RGB")
        imgRGB.save(f"deployment_{deploymentID}.jpg")
    frame = bufferedData.reshape((inputHeight, inputWidth, 4))
    return PreProcessFrameRGBA(frame, width, height)  

async def FinaliseInference(pipeline, deploymentID, height, width, classList, frameCounts, modelName, deploymentCount, jetson, csvLog, loop, inputName, outputName):
    """Function to finalise inference tasks for deployment
    1. Initialise Triton client
    2. Retrieve appsink from pipeline
    3. Create frames queue
    4. Check pipeline state
    5. Start monitoring task
    6. Start inference task (parallel or linear can be chosen parallel allows realtime fast processing, linear allows for sequential processing which is equivalent to 1 second per frame)
    Args:
        pipeline Gst.Pipeline: pipeline for deployment
        deploymentID int: deployment ID
        height int: height of model input
        width int: width of model input
        classList array: list of classes for model
        frameCounts int: number of frames to process
        modelName string: name of model
        deploymentCount int: deployment count
        jetson JTOP: allows for jetson utilisation stats to be accessed
        csvLog string: path to log file
        loop asyncio: event loop
        inputName string: name of model input
        outputName string: name of model output
    Returns:
        int: deployment count
    """
    tritonURL = 'localhost:8000'
    tritonClient = httpclient.InferenceServerClient(url=tritonURL)
    if not isinstance(pipeline, Gst.Pipeline):
        print("The provided argument is not a Gst.Pipeline instance.")
        return

    appsink = pipeline.get_by_name(f"sink_deployment_{deploymentID}")
    if not appsink:
        print("Appsink not found.")
        return

    framesQueue = deque(maxlen=frameCounts)
    if GetPipelineState(pipeline) != Gst.State.PLAYING:
        print("Pipeline in incorrect state restart the node")
        return
    inferenceData = []
    print("Pipeline and sink were correctly retrieved")
    print(f"Inference for deployment_{deploymentID} with model {modelName} is occuring")
    filePath = f"/home/{getpass.getuser()}/Desktop/MVision/node/PyDeploy/results/Results_deployment_{deploymentID}_{datetime.now().strftime('%Y_%m_%d')}.csv"
    monitoringTask = loop.create_task(DumpInference(inferenceData, filePath, deploymentID, loop, frameCounts))
    ###Uncomment for parallel processing
    GLib.timeout_add_seconds(1, PullFrameParallel, pipeline, appsink, deploymentID, framesQueue, int(width), int(height), frameCounts, tritonClient, modelName, classList, jetson, csvLog, loop, inferenceData, inputName, outputName)
    ###Uncomment for linear processing
    #GLib.timeout_add_seconds(1, PullFrameLinear, pipeline, appsink, deploymentID, framesQueue, int(width), int(height), frameCounts, tritonClient, modelName, classList, jetson, csvLog, loop, inferenceData, inputName, outputName)
    deploymentCount = deploymentCount+1
    return deploymentCount

def PullFrameLinear(pipeline, appsink, deploymentID, framesQueue, width, height, frameCounts, tritonClient, modelName, classList, jetson, csvLog, loop, inferenceData, inputName, outputName):
    """Function to extract and process frames in a sequential order
    1. Extract frame from appsink
    2. Load frame data
    3. Append frame to frames queue
    4. Check if frames queue is full
    5. If full, stack frames and create input tensor
    6. Infer on model
    7. Log inference data
    8. Clear frames queue
    9. Return True if successful (keeps it looping in GLOOP)
    Args:
        pipeline Gst.Pipeline: pipeline for deployment
        appsink Gst.AppSink: appsink for deployment
        deploymentID int: deployment ID
        framesQueue deque: queue to store frames
        width int: width of model input
        height int: height of model input
        frameCounts int: number of frames to process
        tritonClient httpclient: triton client for inference
        modelName string: name of model
        classList array: list of classes for model
        jetson JTOP: allows for jetson utilisation stats to be accessed
        csvLog string: path to log file
        loop asyncio: event loop
        inferenceData array: array to store inference data
        inputName string: name of model input
        outputName string: name of model output
    Returns:
        bool: True if successful
    """
    sample = appsink.emit("pull-sample")
    if sample is None:
        print(f"No more frames or sink unavailable for deployment_{deploymentID}")
        loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'No Frames Stopping Deployment: deployment_{deploymentID} Stopping'))
        return False
    try:
        buffer = sample.get_buffer()
        inputWidth = 1920
        inputHeight = 1080
        success, mapInfo = buffer.map(Gst.MapFlags.READ)
        if not success:
            print("Failed to map buffer")
            return True

        ##Uncomment for optimal collection settings for i3d-kinetics type model (beta tested)
        #processedFrame = LoadDataI3(mapInfo.data, inputHeight, inputWidth, width, height, deploymentID, False)

        ###Uncomment if pipeline is initialised with GPU
        processedFrame = LoadDataRGBA(mapInfo.data, inputHeight, inputWidth, width, height, deploymentID, False)      

        ##Uncomment if pipeline is initialised with CPU
        #processedFrame = LoadDataRGB(mapInfo.data, inputHeight, inputWidth, width, height, deploymentID, False)
        framesQueue.append(processedFrame)
    finally:
        if 'mapInfo' in locals() and mapInfo:
            buffer.unmap(mapInfo)

    if len(framesQueue) == frameCounts:
        inputBatch = np.stack(list(framesQueue), axis=0)
        inputBatch = np.expand_dims(inputBatch, axis=0)
        loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'Batch of {frameCounts} Gathered for deployment: deployment_{deploymentID}'))
        try:
            inputTensor = httpclient.InferInput(inputName, inputBatch.shape, "FP32")
            inputTensor.set_data_from_numpy(inputBatch)
            response = tritonClient.infer(modelName, inputs=[inputTensor])                
            outputData = response.as_numpy(outputName)
            confidencePercentage = FormatConfidence(outputData)
            predictedClass = classList[np.argmax(outputData)]
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'Inference for deployment: deployment_{deploymentID}'))
            inferencetask = loop.create_task(CompileInferenceResult(inferenceData, predictedClass, confidencePercentage))
            print(f"{str(datetime.now().strftime('%H:%M:%S'))} - Deployment: deployment_{deploymentID} Predicted class: {predictedClass}")
        except InferenceServerException as e:
            print(f"InferenceServerException: {str(e)}")
        framesQueue.clear() 
    return True  

def PullFrameParallel(pipeline, appsink, deploymentID, framesQueue, width, height, frameCounts, tritonClient, modelName, classList, jetson, csvLog, loop, inferenceData, inputName, outputName):
    frames = GatherFrames(appsink, frameCounts)
    ProcessAppendFrames(framesQueue, frames, width, height, deploymentID)
    if len(framesQueue) == frameCounts:
        inputBatch = np.stack(list(framesQueue), axis=0)
        inputBatch = np.expand_dims(inputBatch, axis=0)
        try:
            inputTensor = httpclient.InferInput(inputName, inputBatch.shape, "FP32")
            inputTensor.set_data_from_numpy(inputBatch)
            response = tritonClient.infer(modelName, inputs=[inputTensor])                
            outputData = response.as_numpy(outputName)
            confidencePercentage = FormatConfidence(outputData)
            predictedClass = classList[np.argmax(outputData)]
            loggingtask = loop.create_task(CompilePerformanceEntry(jetson, csvLog, f'Inference for deployment: deployment_{deploymentID}'))
            inferencetask = loop.create_task(CompileInferenceResult(inferenceData, predictedClass, confidencePercentage))
            print(f"{str(datetime.now().strftime('%H:%M:%S'))} - Deployment: deployment_{deploymentID} Predicted class: {predictedClass}")
        except InferenceServerException as e:
            print(f"InferenceServerException: {str(e)}")
        framesQueue.clear() 
    return True

def ProcessFrame(sample, index, width, height, deploymentID):
    """Function to process frame data for use in parallel processing
        1. Get buffer from sample
        2. Get caps format from sample
        3. Map buffer
        4. Load data from mapped buffer
        5. Unmap buffer
        6. Return index and processed frame
    Args:
        sample Gst.Sample: sample to process
        index int: index of frame
        width int: width of model input
        height int: height of model input
        deploymentID int: deployment ID
    Returns:
        tuple: index and processed frame
    """
    try:
        buffer = sample.get_buffer()
        capsFormat = sample.get_caps().get_structure(0)
        inputWidth = 1920
        inputHeight = 1080
        success, mapInfo = buffer.map(Gst.MapFlags.READ)
        if success:
            pass
        else:
            print("Failed to map buffer")
    finally:
        if 'mapInfo' in locals() and mapInfo:
            buffer.unmap(mapInfo)
    ##Uncomment for optimal collection settings for i3d-kinetics type model
    #return (index, LoadDataI3(mapInfo.data, inputHeight, inputWidth, width, height, deploymentID, False))
    
    return (index, LoadDataRGBA(mapInfo.data, inputHeight, inputWidth, width, height, deploymentID, False))

def GatherFrames(appsink, frameCount):
    """Function to gather frame data for use in parallel processing
        1. Get sample from appsink
        2. Append sample to frames
        3. Sleep for 0.05 seconds (slightly delay the gathering so frames are not all gathered instantly needs to be fine tuned per model really)
        4. Return frames
    Args:
        appsink Gst.AppSink: appsink to gather frames from
        frameCount int: number of frames to gather
    Returns:
        array: array of frames
    """
    frames = []
    while len(frames) < frameCount:
        sample = appsink.emit("pull-sample")
        if sample is None:
            print("No more frames or sink unavailable.")
            break  
        frames.append(sample)
        asyncio.sleep(0.05)
    return frames

def ProcessAppendFrames(framesQueue, frames, width, height, deploymentID):
    """Function to process frame data in parallel whilst keeping their order in the queue correct
        1. Create executor
        2. Submit frames to executor
        3. Sort results in order
        4. Append processed frames to frames queue
        5. Return frames queue
    Args:
        framesQueue deque: queue to store frames
        frames array: array of frames to process
        width int: width of model input
        height int: height of model input
        deploymentID int: deployment ID
    Returns:
        deque: frames queue
    """
    with ThreadPoolExecutor() as executor:
        futureToFrame = {executor.submit(ProcessFrame, sample, i, width, height, deploymentID): i for i, sample in enumerate(frames)}
        resultsInOrder = sorted([future.result() for future in futureToFrame], key=lambda x: x[0])
        for _, processedFrame in resultsInOrder:
            framesQueue.append(processedFrame)
        return framesQueue
            
def FormatConfidence(outputData):
    """Function to format confidence to percentage based on whether the is model set to output a percentage or not
        1. Get max value from output data
        2. Check if max value is less than 1
        3. Given format set as percentage and round to 4 decimal places
    Args:
        outputData array: array of output data
    Returns:
        string: confidence percentage
    """
    maxValue = np.max(outputData)
    if maxValue < 1:
        confidencePercentage = np.round(maxValue * 100, decimals=4)
    else:
        confidencePercentage = np.round(maxValue, decimals=4)
    return confidencePercentage

def PreProcessFrame(inputHeight, inputWidth, width, height, frame):
    """Function to preprocess frame to correct size, format and type Specifically for I3D-Kinetics model
        1. Resize frame to correct size
        2. Convert frame to RGB
        3. Crop frame to focus on centre portion
    Args:
        inputHeight int: height of input frame
        inputWidth int: width of input frame
        width int: width of model input
        height int: height of model input
        frame array: frame to preprocess
    Returns:
        float32: preprocessed frame
    """
    targetHeight = 256
    aspectRatio = inputWidth / inputHeight
    newWidth = int(targetHeight * aspectRatio)

    resizedFrame = cv2.resize(frame, (newWidth, targetHeight), interpolation=cv2.INTER_LINEAR)
    resizedFrame = cv2.cvtColor(resizedFrame, cv2.COLOR_RGBA2RGB)
    x = (aspectRatio - width) // 2
    y = (targetHeight - height) // 2

    croppedFrame = resizedFrame[y:y + width, x:x + height]
    return croppedFrame.astype('float32') / 255.0  

def LoadDataI3(mappedData, inputHeight, inputWidth, width, height, deploymentID, OUTPUT):
    """Function to load frame data specifically for I3D-Kinetics model
        1. Load frame from mapped data
        2. Optionally save frame to file
        3. Return preprocessed frame
    Args:
        mappedData buffer: mapped data from buffer
        inputHeight int: height of input frame
        inputWidth int: width of input frame
        width int: width of model input
        height int: height of model input
        deploymentID int: deployment ID
        OUTPUT bool: flag to save frame to file
    Returns:
        float32: preprocessed frame
    """
    bufferedData = np.frombuffer(mappedData, dtype=np.uint8)
    if OUTPUT:
        img = Image.frombytes("RGBA", (inputWidth, inputHeight), bufferedData)
        imgRGB = img.convert("RGB")
        imgRGB.save(f"deployment_{deploymentID}.jpg")
    frame = bufferedData.reshape((inputHeight, inputWidth, 4))
    return PreProcessFrame(inputHeight, inputWidth, width, height, frame)