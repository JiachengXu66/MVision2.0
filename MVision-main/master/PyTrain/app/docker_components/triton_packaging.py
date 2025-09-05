import tensorflow as tf
import os 
import configparser
import shutil

def CompileNumber(currentNumber):
    """Function to compile an array of digits into a complete number
    Args:
        currentNumber array: array of digits that form a number
    Returns:
        string: Compiled number
    """
    number = ""
    for char in currentNumber:
        number += char
    return number

def GetDimensions(shape):
    """Function to create an array that is equivalent to the shape of the input/output of the model.
       Creates array from a string which contains a shape variable.
       1. Initialise empty dimensions array for final shape
       2. Loop through the original TF shape format aiming to identify where a digit is found.
       3. If a digit is found check its following arguments and take action accordingly
       4. Once the next item attempts fails (array complete), return dimensions
    Args:
        shape string: line containing the shape object
    Returns:
        array: the shape that is to be placed in the config file. (dims)
    """
    dimensions = []
    currentNumber = []
    i = 0
    while i  < len(shape):
        char = shape[i]
        try:
            next = shape[i+1]
        except:
            return dimensions
        match char:
            case '(':
                pass
            case ')':
                pass
            case ',':
                pass
            case char if char.isdigit() and next.isdigit():
                currentNumber.append(char)
            case char if char.isdigit() and next == ',':
                currentNumber.append(char)
                fullNumber = CompileNumber(currentNumber)
                dimensions.append(int(fullNumber))
                currentNumber = []
            case char if char.isdigit() and next == ')':
                currentNumber.append(char)
                fullNumber = CompileNumber(currentNumber)
                dimensions.append(int(fullNumber))
                currentNumber = []
            case _:
                pass
        i += 1

def CollectModelConfiguration(modelPath):
    """Function to load the model and get the relevant variables to curate the Triton and PyTrain config files correctly.
       1. Load the model from the given location
       2. Select its default serving mode
       3. Select its input items and extract: name, shape and type
       4. Select its output items and extract: name, shape and type
       5. Return all extracted variables
    Args:
        modelPath string: location of model directory to load the model from
    Returns:
        string: model input name
        string: model input type
        string: model input shape (unformatted format)
        string: model output name
        string: model output type
        string: model output shape (unformatted format)
    """
    loadedModel = tf.saved_model.load(modelPath)
    servedModel = loadedModel.signatures['serving_default']

    for inputName, inputTensor in servedModel.structured_input_signature[1].items():
            modelInputName = inputName
            modelInputShape = inputTensor.shape
            modelInputType = inputTensor.dtype

    for outputName, outputTensor in servedModel.structured_outputs.items():
            modelOutputName = outputName
            modelOutputShape = outputTensor.shape
            modelOutputType = outputTensor.dtype

    return modelInputName, modelInputType, modelInputShape, modelOutputName, modelOutputType, modelOutputShape

def WriteConfig(configLines, folderPath):
    """Function to write the Triton configuration content to a file
    Args:
        configLines array: lines to be written to the Triton configuration file
        folderPath string: location of where the config.pbtxt file must be placed
    """
    with open(f"{folderPath}/config.pbtxt", "w") as file:
        for line in configLines:
            file.write(line + "\n")
    print("Config file created")
    return

def CreateTritonConfig(modelName, folderPath):
    """Function to compile given data into the Triton configuration file format
    1. Initialise model path
    2. Collect required parameters from the loaded path
    3. Compile config into array
    4. Write config
    5. Return input name and output name for PyTrain config
    Args:
        configLines array: lines to be written to the Triton configuration file
        folderPath string: location of where the config.pbtxt file must be placed
    Return:
        string: input name for the model
        string: output name for the model
    """
    modelPath = os.path.join(folderPath,modelName)
    inputName, inputType, inputShape, outputName, outputType, outputShape = CollectModelConfiguration(modelPath)

    typeMap = {
        tf.bool: "TYPE_BOOL",
        tf.uint8: "TYPE_UINT8",
        tf.uint16: "TYPE_UINT16",
        tf.uint32: "TYPE_UINT32",
        tf.uint64: "TYPE_UINT64",
        tf.int8: "TYPE_INT8",
        tf.int16: "TYPE_INT16",
        tf.int32: "TYPE_INT32",
        tf.int64: "TYPE_INT64",
        tf.half: "TYPE_FP16",
        tf.float32: "TYPE_FP32",
        tf.float64: "TYPE_FP64",
        tf.string: "TYPE_STRING"
    }

    configLines = [
        f"name: \"{modelName}\"",
        f"dynamic_batching {{ }}",
        "platform: \"tensorflow_savedmodel\"",
        "max_batch_size: 8",  
        "input [",
        f"  {{",
        f"    name: \"{inputName}\"",
        f"    data_type: {typeMap[inputType]}",
        f"    dims: {GetDimensions(str(inputShape))}",
        f"  }}",
        "]",
        "output [",
        f"  {{",
        f"    name: \"{outputName}\"",
        f"    data_type: {typeMap[outputType]}",
        f"    dims: {GetDimensions(str(outputShape))}",
        f"  }}",
        "]",
    ]
    WriteConfig(configLines, folderPath)
    return inputName, outputName

def GenerateTrainingConfig(labels, modelName, folderPath, epochs, frameCount, shuffleSize, batchSize, height, 
width, inputName, outputName):
    """Function to compile config with training data for use with PyDeploy
    1. Initialise config
    2. Add 'PREDICTION' configuration elements
    3. Add 'TRAINING' configuration elements
    4. Write config
    Args:
        labels array: array of label names
        modelName string: model name
        folderPath string: folder path for the model folder
        epochs int: number of epochs used
        frameCount int: number of frames taken from videos
        shuffleSize int: number of frame sets to shuffle
        batchSize int: number of frame sets to batch process together
        height int: height for the video to be reformatted to
        width int: width for the video to be reformatted to 
        inputName string: input name for model shape input
        outputName string: out name for model results output
    """
    config = configparser.ConfigParser()
    config['PREDICTION'] = {
        'num_frames': frameCount,
        'class_list': labels,
        'height': height,
        'width': width,
        'input_name':inputName,
        'output_name':outputName
    }
    config['TRAINING'] = {
        'epochs': epochs,
        'shuffle_size': shuffleSize,
        'batch_size': batchSize
    }
    with open(f'{folderPath}/{modelName}.config', 'w') as configfile:
        config.write(configfile)

def ReorganiseFolder(modelName, folderPath, repoPath):
    """Function to reorganise files contained in the model_task/{modelName} folder to be within the model_repo folder and fit the Triton file structure
    1. Define directories
    2. Create required directories
    3. Move variable files
    4. Move model files
    5. Remove excess directories
    6. Move PyTrain config and model training results files to assets (extras folder in Triton)
    Args:
        modelName string: model name
        folderPath string: path for the task folder
        repoPath string: path to the model_repo folder
    """
    variableFiles = os.listdir(f"{folderPath}/{modelName}/variables")
    baseFiles = os.listdir(f"{folderPath}/{modelName}")
    directoriesPath = f"{folderPath}/{modelName}/1/model.savedmodel/variables"
    assetsPath = f"{folderPath}/{modelName}/1/model.savedmodel/assets"
    os.makedirs(directoriesPath)
    os.makedirs(assetsPath)
    for file in variableFiles:
        print(file)
        os.replace(f"{folderPath}/{modelName}/variables/{file}", f"{folderPath}/{modelName}/1/model.savedmodel/variables/{file}")
    for file in baseFiles:
        print(file)
        if file != "variables" and file != "assets":
            os.replace(f"{folderPath}/{modelName}/{file}", f"{folderPath}/{modelName}/1/model.savedmodel/{file}") 
    os.replace(f"{folderPath}/config.pbtxt", f"{folderPath}/{modelName}/config.pbtxt")
    os.removedirs(f"{folderPath}/{modelName}/assets")
    os.removedirs(f"{folderPath}/{modelName}/variables")
    shutil.copytree(f"{folderPath}/{modelName}", f"{repoPath}/{modelName}")
    shutil.move(f"{folderPath}/{modelName}.config", f"{repoPath}/{modelName}/1/model.savedmodel/assets")
    shutil.move(f"{folderPath}/{modelName}_history.png", f"{repoPath}/{modelName}/1/model.savedmodel/assets")
    shutil.move(f"{folderPath}/{modelName}_test_confusion.png", f"{repoPath}/{modelName}/1/model.savedmodel/assets")
    shutil.move(f"{folderPath}/{modelName}_training_confusion.png", f"{repoPath}/{modelName}/1/model.savedmodel/assets")

def CreateTritonPackage(labels, modelName, folderPath, repoPath, epochs, frameCount, shuffleSize, batchSize, height, width):
    """Function to create required configuration files and compile the Triton compatible directory in model_repo
    1. Create the triton config.pbtxt
    2. Create the PyTrain modelname.conf
    3. Reorganise folder structure for placement in model_repo and compatible Triton folder structure
    Args:
        labels array: array of label names
        modelName string: model name
        folderPath string: folder path for the model folder
        repoPath string: path to the model_repo folder
        epochs int: number of epochs used
        frameCount int: number of frames taken from videos
        shuffleSize int: number of frame sets to shuffle
        batchSize int: number of frame sets to batch process together
        height int: height for the video to be reformatted to
        width int: width for the video to be reformatted to 
    """
    inputName, outputName = CreateTritonConfig(modelName, folderPath)
    GenerateTrainingConfig(labels, modelName, folderPath, epochs, frameCount, shuffleSize, batchSize, height, width, inputName, outputName)
    ReorganiseFolder(modelName, folderPath, repoPath)