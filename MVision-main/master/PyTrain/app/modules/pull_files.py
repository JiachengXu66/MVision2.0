import os
import fnmatch
import random
import shutil
from datetime import datetime
import requests

def FindClasses(parentPath, classNames):
    """Function to collate the class directories that begin with the class name
       Add remaining folder paths to the "Other" class
    1. For each item in the folder directory
    2. If its a folder
    3. Check if it matches any of the class names selected for the task
       if it matches confirm by setting matched to True
    4. If no match then the path should be appended to "Other"
    5. Repeat until all items are cycled through

    Args:
        parentPath string: path of parent folder (source folder)
        classNames: array of all class names needing to be selected
    
    Returns:
        dict: classDirectories 
        """
    classDirectories = {className: [] for className in classNames}
    classDirectories["Other"] = []  
    for item in os.listdir(parentPath):
        itemPath = os.path.join(parentPath, item)
        if os.path.isdir(itemPath):
            
            matched = False
            for className in classNames:
                if item.lower().startswith(className.lower()):
                    classDirectories[className].append(itemPath)
                    matched = True
                    break
            if not matched:
                classDirectories["Other"].append(itemPath)
    return classDirectories

def FindDirectories(sources, directoryPath, classes):
    """Function to collate classes from each chosen source
    1. For each source
    2. If source is a directory
    3. Find the classes for that directory
    4. Append the found class directories to the class paths dictionary 
    5. Repeat until all items are cycled through

    Args:
        sources string: name of source folder (identical to source)
        directoryPath string: directory path to the source location
        classes: array of all class names needing to be selected
    
    Returns:
        dict: classPaths 
        """
    classPaths = {"Other": []}  
    for className in classes:  
        classPaths[className] = []
    for source in sources:
        sourcePath = os.path.join(directoryPath, source)
        print(f"Processing source path: {sourcePath}")
        if os.path.exists(sourcePath):
            
            foundDirectories = FindClasses(sourcePath, classes)
            
            for key, paths in foundDirectories.items():
                classPaths[key].extend(paths)

    return classPaths

def FindFiles(classPaths):
    """Function to collate all mp4 files from each folder location and add them to classFiles dict
    1. For each class
    2. Get directories that feature said class
    3. Find mp4 files in those directories
    4. Check if given class is already part of the classFiles dict
    5. Add files paths to the dict
    6. Repeat until all items are cycled through

    Args:
        classPaths dict: dictionary of class keys and values of the folder directory that their videos are stored in
    
    Returns:
        dict: classFiles 
        """
    classFiles = {}
    for classType in classPaths:
        directories = classPaths[classType]
        for directory in directories:
            files = fnmatch.filter(os.listdir(directory), "*.mp4")
            if files:  
                if classType not in classFiles:
                    classFiles[classType] = {}
                classFiles[classType][directory] = files
    return classFiles

def DisplayTree(classFiles):
        for classType, directories in classFiles.items():
            print(f"Class: {classType}")
            for directory, files in directories.items():
                print(f"  ├─ Directory: {directory}")
                displayedFiles = files[:10]
                for file in displayedFiles[:-1]:
                    print(f"  │   ├─ {file}")
                if displayedFiles:
                    if len(files) > 10:
                        print(f"  │   ├─ {displayedFiles[-1]}")
                        print(f"  │   └─ ... (and {len(files) - 10} more files)")
                    else:
                        print(f"  │   └─ {displayedFiles[-1]}")
            print() 

def AdjustCount(classDirectories, trainingAmount):
    """Function to attempt to sort files into the correct amount for the desired training, testing, validation total
       It attempts to taken an even amount of samples from each folder to try and improve generability of the model
    1. For class and array of directories in the classDirectories dict
    2. Set the requirements and check the amount of videos that should attempt to be sourced from each directory
    3. Check if there are enough files available
    4. If not reduce the amount of files to collect
    5. For each path
    6. Check how many videos remain and are needed, select the needed amount and reduce the remaining videos required
    7. Repeat for each directory path & class

    Args:
        classDirectories dict: dictionary of class keys and values of the paths to video files for that class
        trainingAmount int: total amount of video required 
    Returns:
        dict: reducedFiles 
        """
    reducedFiles = {}
    for className, directories in classDirectories.items():
        reducedFiles[className] = {}
        requiredCount = trainingAmount
        initialCount = trainingAmount // len(directories)
        totalCount = sum(len(os.listdir(path)) for path in directories)
        if totalCount < trainingAmount:
            print(f"Warning: Not enough videos for class {className}. Available: {totalCount}, Needed: {trainingAmount}")
            requiredCount = totalCount
        for path in directories:
            availableVideos = os.listdir(path)  
            neededVideos = min(len(availableVideos), initialCount if requiredCount >= initialCount else requiredCount)
            selectedVideos = random.sample(availableVideos, neededVideos)
            reducedFiles[className][path] = selectedVideos
            requiredCount -= neededVideos
            remainingCount = len(directories) - len(reducedFiles[className])
            if remainingCount > 0:
                initialCount = requiredCount // remainingCount
    return reducedFiles

def CopyFiles(finalFiles, splits, modelName):
    """Function to create the model_task entry and transfer all the chosen video files to the correct file structure for processing.
       Differentiate tasks with the same name by labelling the timestamp at which they are created.
       Should create a file structure with a train, validation and test folder
       It attempts to taken an even amount of samples from each folder to try and improve generability of the model
    1. Create directory paths based on split names (train, validation, test)
    2. Sort through each class name and generate array of os.path types.
    3. Shuffle the paths to mix their order so that any splits are not dictated by initial loading order
    4. Allocate files to each type of split. Order of train, validation and test.
    5. Copy the given files to the new folder locations
    6. Return the name of the new folder in model_tasks

    Args:
        finalFiles dict: dictionary of class keys and values of the reduced number of paths to files
        splits dict: dict of train, validation and test amounts
        modelName: name of the model that will be produced
    Returns:
        string: baseDirectory 
        """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    baseDirectory = f"../model_tasks/{modelName}_{timestamp}"
    os.makedirs(baseDirectory, exist_ok=True)
    
    splitDirectories = {split: os.path.join(baseDirectory, split) for split in splits.keys()}
    for splitDirectories in splitDirectories.values():
        os.makedirs(splitDirectories, exist_ok=True)

    for className, directories in finalFiles.items():
        allFiles = []
        for directory, filenames in directories.items():
            for filename in filenames:
                allFiles.append(os.path.join(directory, filename))

        random.shuffle(allFiles)

        for split, count in splits.items():
            splitDirectories = splitDirectories[split]
            
            classDir = os.path.join(splitDirectories, className)
            os.makedirs(classDir, exist_ok=True)
            
            splitFiles = allFiles[:count]
            allFiles = allFiles[count:]  
            
            for filePath in splitFiles:
                destPath = os.path.join(classDir, os.path.basename(filePath))
                shutil.copy(filePath, destPath)
                print(f"Copied {filePath} to {destPath}")
    return baseDirectory

def GetModelParameters(taskID):
    """Function to get model name, class, source and split distribution
    1. Get classes
    2. Get sources
    3. Get task information
    4. Retrieve information from result bodies
    5. Return classes, sources, splits, modelName
    Args:
        taskID int: task ID of current task that is executing
    Returns:
        array: classes
        array: sources
        splits: dict
        modelName: string
    """
    try:
        classesResult = requests.get(f"http://localhost:3000/tasks/{taskID}/classes")
        sourcesResult = requests.get(f"http://localhost:3000/tasks/{taskID}/sources")
        taskResult = requests.get(f"http://localhost:3000/tasks/id/{taskID}")
        classes = classesResult.json()[0]['get_task_classes']["classes"]
        sources = sourcesResult.json()[0]['get_task_sources']["sources"]
        task = taskResult.json()[0]['get_task'][0]
        splits = {"train": task['train'], "validation":task['verification'], "test":task['test']}
        modelName = task['model_name']
        return classes, sources, splits, modelName
    except:
        print("Change status to failed")

def GetClassMaps(classes):
    """Function to get class map of IDs to Names
    1. Get class maps
    2. Reduce JSON to map element
    3. For each classID get its name in the map and save to an array
    5. Return classNames
    Args:
        classes array: class IDs for current task
    Returns:
        array: classNames
    """
    classResult = requests.get(f"http://localhost:3000/maps/class")
    classMap = classResult.json()[0]['get_class_map']
    classNames = []
    for classID in classes:
        classNames.append(classMap[f"{classID}"])
    return classNames

def GetSourceMaps(sources):
    """Function to get source map of IDs to Names
    1. Get source maps
    2. Reduce JSON to map element
    3. For each sourceID get its name in the map and save to an array
    5. Return sourceNames
    Args:
        sources array: source IDs for current task
    Returns:
        array: sourceNames
    """
    sourceResult = requests.get(f"http://localhost:3000/maps/source")
    sourceMap = sourceResult.json()[0]['get_source_map']
    sourceNames = []
    for sourceID in sources:
        sourceNames.append(sourceMap[f"{sourceID}"])
    return sourceNames

async def PullFiles(taskID):
    """Function to pull the class videos and organise them into the correct folders of training
       testing and validation with the correct video amounts.
    1. Retrieve model parameters: Array of classes, Source of Videos, Training/Test/Validation Splits and the Model Name
    2. Retrieve Class Maps to get Names from IDs
    3. Retrieve Source Maps to get Names from IDs
    4. Sets directory for where the sources can be found
    5. Finds the directories that match the classes and collate directories for the "Other" class
    6. Find the files from the classes in classPaths
    7. Display the totally compiled classFiles
    8. 

    Args:
        request: http object recieved from endpoint
    
    Returns:
        """
    classes, sources, splits, modelName = GetModelParameters(taskID)
    classes = GetClassMaps(classes)
    sources = GetSourceMaps(sources)
    directoryPath = "./sources"
    classPaths = FindDirectories(sources, directoryPath, classes)
    classFiles = FindFiles(classPaths)
    DisplayTree(classFiles)
    finalFiles = AdjustCount(classFiles,sum(splits.values()))
    DisplayTree(finalFiles)
    taskDirectory = CopyFiles(finalFiles, splits, modelName)
    print(f"Files Moved to {taskDirectory}")
    return taskDirectory  