import matplotlib.pyplot as plt
import tensorflow as tf
from keras import Model
import seaborn as sns
import numpy as np

def PlotHistory(history, modelName, folderPath):
  """Function to plot accuracy and loss curves for the model
      1. Defines plots
      2. Plot loss and val_loss from history object
      3. Plot accuracy and val_accuracy from history object
      4. Save to model tasks folder
  Args:
      history History: History object for completed training
      modelName string: model name
      folderPath string: path for model folder in model_tasks
  """  
  fig, (ax1, ax2) = plt.subplots(2)

  fig.set_size_inches(18.5, 10.5)

  ax1.set_title('Loss')
  ax1.plot(history.history['loss'], label = 'train')
  ax1.plot(history.history['val_loss'], label = 'test')
  ax1.set_ylabel('Loss')

  max_loss = max(history.history['loss'] + history.history['val_loss'])

  ax1.set_ylim([0, np.ceil(max_loss)])
  ax1.set_xlabel('Epoch')
  ax1.legend(['Train', 'Validation'])

  ax2.set_title('Accuracy')
  ax2.plot(history.history['accuracy'],  label = 'train')
  ax2.plot(history.history['val_accuracy'], label = 'test')
  ax2.set_ylabel('Accuracy')
  ax2.set_ylim([0, 1])
  ax2.set_xlabel('Epoch')
  ax2.legend(['Train', 'Validation'])
  plt.savefig(f"{folderPath}/{modelName}_history.png")
  plt.close(fig)


def GetConfusionResults(model, dataset): 
  actual = [labels for _, labels in dataset.unbatch()]
  predicted = model.predict(dataset)
  actual = tf.stack(actual, axis=0)
  predicted = tf.concat(predicted, axis=0)
  predicted = tf.argmax(predicted, axis=1)

  return actual, predicted

def PlotConfusionMatrix(actual, predicted, labels, dsType, modelName, folderPath):
    """Function to plot confusion matrix 
      1. Defines plots
      2. Generate confusion matrix Tensor
      3. Plot matrix
      4. Save to model tasks folder
      Args:
      actual array: array holding the actual classes
      predicted array: array holding the predicted classes from the model
      labels array: holds the names of the classes (indexed)
      dsType string: whether the results are for the validation or training set 
      modelName string: model name
      folderPath string: path for model folder in model_tasks
  """  
    sns.set(rc={'figure.figsize':(len(labels)*5, len(labels)*5)})
    sns.set(font_scale=1.8)
    cm = tf.math.confusion_matrix(actual, predicted)
    figure_confusion, ax = plt.subplots()
    ax = sns.heatmap(cm, annot=True, fmt='g')
    ax.set_title('Confusion matrix of action recognition for ' + dsType)
    ax.set_xlabel('Predicted Action')
    ax.set_ylabel('Actual Action')
    ax.set_xticklabels(labels, rotation=90)
    ax.set_yticklabels(labels, rotation=0)
    plt.savefig(f"{folderPath}/{modelName}_{dsType}_confusion.png")
    plt.close(figure_confusion)
