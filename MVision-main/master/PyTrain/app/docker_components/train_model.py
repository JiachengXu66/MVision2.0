import tensorflow as tf
from keras import layers, losses, optimizers, Sequential

import pathlib
import argparse
import os

from load_data import FrameGenerator
from visualise_results import PlotHistory, GetConfusionResults, PlotConfusionMatrix
from triton_packaging import CreateTritonPackage

def ExtractData(folderPath, frameCount):
    """Function to set retrieve datasets in a tfDataset format
       1. Define expected Output Signature of the dataset for the particular model chosen
       2. Load in trainDS, takes additional "training=True" flag to enable data shuffle
       3. Load in valDS and testDS without shuffle
       4. Return datasets
    Args:
        folderPath string: path of dataset location
        frameCount tfDataset: number of frames to be extracted from each video
    Return:
        tfDataset: trainDS, valDS, testDS
    """  
    outputSignature = (tf.TensorSpec(shape = (None, None, None, 3), dtype = tf.float32),
                        tf.TensorSpec(shape = (), dtype = tf.int16))
    
    trainDS = tf.data.Dataset.from_generator(FrameGenerator(pathlib.Path(folderPath+"/train"), frameCount, training=True),
                                                output_signature = outputSignature)                                       
    valDS = tf.data.Dataset.from_generator(FrameGenerator(pathlib.Path(folderPath+"/validation"), frameCount),
                                                output_signature = outputSignature)
    testDS = tf.data.Dataset.from_generator(FrameGenerator(pathlib.Path(folderPath+"/test"), frameCount),
                                                output_signature = outputSignature)
    
    return trainDS, valDS, testDS

def InitialiseCache(trainDS, valDS, testDS):
    """Function to set cache location of each dataset
    Args:
        trainDS tfDataset: training dataset
        valDS tfDataset: validation dataset
        testDS tfDataset: testing dataset
    Return:
        tfDataset: trainDS, valDS, testDS
    """
    trainDS = trainDS.cache(filename="./cache/train_cache")
    valDS = valDS.cache(filename="./cache/val_cache")
    testDS = testDS.cache(filename="./cache/test_cache")
    
    return trainDS, valDS, testDS

def PrefetchDataSet(trainDS, valDS, testDS, AUTOTUNE, shuffleSize=100):
    """Function to set shufflesize of each dataset
    Args:
        trainDS tfDataset: training dataset
        valDS tfDataset: validation dataset
        testDS tfDataset: testing dataset
        AUTOTUNE data.AUTOTUNE: flag for setting autotune for shuffle size
        shuffleSize int: shuffle size value  
    Return:
        tfDataset: trainDS, valDS, testDS
    """
    trainDS = trainDS.shuffle(shuffleSize).prefetch(buffer_size = AUTOTUNE)
    valDS = valDS.shuffle(shuffleSize).prefetch(buffer_size = AUTOTUNE)
    testDS = testDS.shuffle(shuffleSize).prefetch(buffer_size = AUTOTUNE)

    return trainDS, valDS, testDS

def InitialiseBatch(trainDS, valDS, testDS, batchSize):
    """Function to set batchsize of each dataset
    Args:
        trainDS tfDataset: training dataset
        valDS tfDataset: validation dataset
        testDS tfDataset: testing dataset
        batchSize int: batch size value  
    Return:
        tfDataset: trainDS, valDS, testDS
    """
    trainDS = trainDS.batch(batchSize)
    valDS = valDS.batch(batchSize)
    testDS = testDS.batch(batchSize)

    return trainDS, valDS, testDS

def CreateModel(frameCount, height, width, path):
    """Function to create the structure of the model
    1. Initialise the inputShape based on specified frameCount, height and width
    2. Generate model as Sequential
    3. Add required layers
    4. Retrieve number of classes that the model will be trained on
    5. Condense the model to make sure output matches number of classes

    Args:
        height int: height of video to crop to
        width int: width of video to crop to
        frameCount int: amount of frames to take from each video     
    Return:
        keras.Sequential: model
    """
    inputShape = (frameCount, height, width, 3)

    model = Sequential()

    model.add(layers.ConvLSTM2D(filters = 4, kernel_size = (3, 3), activation = 'tanh',data_format = "channels_last",
                            recurrent_dropout=0.2, return_sequences=True, input_shape = inputShape))
        
    model.add(layers.MaxPooling3D(pool_size=(1, 2, 2), padding='same', data_format='channels_last'))
    model.add(layers.TimeDistributed(layers.Dropout(0.2)))
    
    model.add(layers.ConvLSTM2D(filters = 8, kernel_size = (3, 3), activation = 'tanh', data_format = "channels_last",
                            recurrent_dropout=0.2, return_sequences=True))
        
    model.add(layers.MaxPooling3D(pool_size=(1, 2, 2), padding='same', data_format='channels_last'))
    model.add(layers.TimeDistributed(layers.Dropout(0.2)))
        
    model.add(layers.ConvLSTM2D(filters = 14, kernel_size = (3, 3), activation = 'tanh', data_format = "channels_last",
                            recurrent_dropout=0.2, return_sequences=True))
        
    model.add(layers.MaxPooling3D(pool_size=(1, 2, 2), padding='same', data_format='channels_last'))
    model.add(layers.TimeDistributed(layers.Dropout(0.2)))
        
    model.add(layers.ConvLSTM2D(filters = 16, kernel_size = (3, 3), activation = 'tanh', data_format = "channels_last",
                            recurrent_dropout=0.2, return_sequences=True))
        
    model.add(layers.MaxPooling3D(pool_size=(1, 2, 2), padding='same', data_format='channels_last'))
        
    model.add(layers.Flatten()) 
    classCount = sum(1 for _ in pathlib.Path(path+"/train").iterdir() if _.is_dir())
    model.add(layers.Dense(classCount, activation = "softmax"))
    #model.summary()
    return model

def GetClassMaps(path, frameCount):
    """Function to get the class labels
    1. Reload training sets FrameGenerator object
    2. Extract classNameID dict
    3. Extract array of class names
    4. Return class names (labels)

    Args:
        path string: path to training folder
        frameCount int: amount of frames to take from each video     
    Return:
        array: labels
    """
    fg = FrameGenerator(pathlib.Path(path+"/train"), frameCount, training=True)
    classes= fg.classNameIDs
    labels = list(classes.keys())
    return labels

def main():
    """Function to execute model training functionality
    1. Declared arguments from docker RUN command
    2. Extracts data into TF Dataset objects
    3. Initialises the cache for data storage external to RAM
    4. PrefetchDataset for faster loading
    5. Preinitialise batch sizes
    6. Create the model based on input arguments 
    7. Initialise early stopping for degradation of accuracy 
    8. Compile model
    9. Plot results of training (loss + accuracy)
    10.Evaluate model on test dataset
    11.Get labels
    12.Get results and plot confusion matrix for both test and validation data
    13.Save the model to given model_task directory
    14.Compile config files and copy relevant model_task data into the model_repo for use with Triton
    15.Hold on input() until PyTrain detects all files and removes containers

    Args:
        modelName string: name of the model
        epochs int: number of epochs to run for
        frameCount int: how many frames should be gathered out of a video
        shuffleSize int: how many videos are to be shuffled
        batchSize int: how many sets of frames should be batched to train in parallel           
    """
    with tf.device('/GPU:0'):
        parser = argparse.ArgumentParser()
        parser.add_argument('--model_name', type=str, default="test1")
        parser.add_argument('--epochs', type=int, default=15)
        parser.add_argument('--num_frames', type=int, default=10)
        parser.add_argument('--shuffle_size', type=int, default=200)
        parser.add_argument('--batch_size', type=int, default=3)
        args = parser.parse_args()
        modelName = args.model_name
        epochs = args.epochs
        frameCount = args.num_frames
        shuffleSize = args.shuffle_size
        batchSize = args.batch_size 

        height = 224
        width = 224

        folderPath = "/mnt"
        repoPath = "/model_repo"

        trainDS, valDS, testDS = ExtractData(folderPath, frameCount)

        AUTOTUNE = tf.data.AUTOTUNE

        trainDS, valDS, testDS = InitialiseCache(trainDS, valDS, testDS)

        trainDS, valDS, testDS = PrefetchDataSet(trainDS, valDS, testDS, AUTOTUNE, shuffleSize)

        trainDS, valDS, testDS = InitialiseBatch(trainDS, valDS, testDS, batchSize)

        model = CreateModel(frameCount, height, width, folderPath)
        
        callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3)

        model.compile(loss = losses.SparseCategoricalCrossentropy(from_logits=False), 
                    optimizer = optimizers.Adam(learning_rate = 0.0001), 
                    metrics = ['accuracy'])

        history = model.fit(x = trainDS,
                            epochs = epochs, 
                            validation_data = valDS,
                            batch_size=batchSize,
                            callbacks=[callback])
        PlotHistory(history, modelName, folderPath)
            
        model.evaluate(testDS, return_dict=True)
            
        labels = GetClassMaps(folderPath, frameCount)

        actual, predicted = GetConfusionResults(model, trainDS)
        PlotConfusionMatrix(actual, predicted, labels, 'training', modelName, folderPath)

        actual, predicted = GetConfusionResults(model, testDS)
        PlotConfusionMatrix(actual, predicted, labels, 'test', modelName, folderPath)

        model.save(os.path.join(folderPath, modelName), save_format='tf')
        
        CreateTritonPackage(labels, modelName, folderPath, repoPath, epochs, frameCount, shuffleSize, batchSize, height, width)
        input()

if __name__ == "__main__":
    main()