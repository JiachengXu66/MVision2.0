import tensorflow as tf
import cv2
import random
import numpy as np 

class FrameGenerator:
  """Class to handle frame extraction into tf.dataframe acceptable format
    Args:
        path string: path of videos to intake 
        frameCount int: how many frames should be gathered from each video
        training bool: indicates if training collection or not, if it is, order file collection is shuffled

        Based off of the following TensorFlow Tutorial: https://github.com/tensorflow/docs/blob/master/site/en/tutorials/load_data/video.ipynb
  """
  def __init__(self, path, frameCount, training = False):
    self.path = path
    self.frameCount = frameCount
    self.training = training
    self.classNames = sorted(set(p.name for p in self.path.iterdir() if p.is_dir()))
    self.classNameIDs = dict((name, idx) for idx, name in enumerate(self.classNames))

  def GetFilesandClasses(self):
    videoPaths = list(self.path.glob('*/*.mp4'))
    classes = [p.parent.name for p in videoPaths] 
    return videoPaths, classes

  def __call__(self):
    videoPaths, classes = self.GetFilesandClasses()

    pairs = list(zip(videoPaths, classes))

    if self.training:
      random.shuffle(pairs)

    for path, name in pairs:
      videoFrames = FramesFromFile(path, self.frameCount) 
      label = self.classNameIDs[name] 
      yield videoFrames, label


def FormatFrames(frame, outputSize):
  frame = tf.image.convert_image_dtype(frame, tf.float32)
  frame = tf.image.resize_with_pad(frame, *outputSize)
  return frame

def FramesFromFile(videoPath, frameCount, outputSize = (224,224), frameStep = 5):
  result = []
  src = cv2.VideoCapture(str(videoPath))  
  length = src.get(cv2.CAP_PROP_FRAME_COUNT)
  requiredLength = 1 + (frameCount - 1) * frameStep
  if requiredLength > length:
    start = 0
  else:
    maxstart = length - requiredLength
    start = random.randint(0, maxstart + 1)

  src.set(cv2.CAP_PROP_POS_FRAMES, start)
  ret, frame = src.read()
  result.append(FormatFrames(frame, outputSize))

  for _ in range(frameCount - 1):
    for _ in range(frameStep):
      ret, frame = src.read()
    if ret:
      frame = FormatFrames(frame, outputSize)
      result.append(frame)
    else:
      result.append(np.zeros_like(result[0]))
  src.release()
  result = np.array(result)[..., [2, 1, 0]]

  return result

