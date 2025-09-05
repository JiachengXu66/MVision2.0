import tensorflow as tf
from keras import layers, losses, optimizers, Sequential, Model
from keras.applications import EfficientNetB0
import pathlib
import argparse
import os
import numpy as np

from load_data import FrameGenerator
from visualise_results import PlotHistory, GetConfusionResults, PlotConfusionMatrix
from triton_packaging import CreateTritonPackage

class MultiHeadAttention(layers.Layer):
    """Customised Multi Attention Layers"""
    def __init__(self, d_model, num_heads):
        super(MultiHeadAttention, self).__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        
        assert d_model % self.num_heads == 0
        
        self.depth = d_model // self.num_heads
        
        self.wq = layers.Dense(d_model)
        self.wk = layers.Dense(d_model)
        self.wv = layers.Dense(d_model)
        
        self.dense = layers.Dense(d_model)
        
    def split_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    
    def call(self, v, k, q, mask=None):
        batch_size = tf.shape(q)[0]
        
        q = self.wq(q)
        k = self.wk(k)
        v = self.wv(v)
        
        q = self.split_heads(q, batch_size)
        k = self.split_heads(k, batch_size)
        v = self.split_heads(v, batch_size)
        
        scaled_attention, attention_weights = self.scaled_dot_product_attention(q, k, v, mask)
        
        scaled_attention = tf.transpose(scaled_attention, perm=[0, 2, 1, 3])
        
        concat_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model))
        
        output = self.dense(concat_attention)
        
        return output, attention_weights
    
    def scaled_dot_product_attention(self, q, k, v, mask):
        matmul_qk = tf.matmul(q, k, transpose_b=True)
        
        dk = tf.cast(tf.shape(k)[-1], tf.float32)
        scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)
        
        if mask is not None:
            scaled_attention_logits += (mask * -1e9)
        
        attention_weights = tf.nn.softmax(scaled_attention_logits, axis=-1)
        
        output = tf.matmul(attention_weights, v)
        
        return output, attention_weights

class ResidualBlock(layers.Layer):
    """residual block (physics)"""
    def __init__(self, filters, kernel_size=(3, 3)):
        super(ResidualBlock, self).__init__()
        self.conv1 = layers.ConvLSTM2D(filters, kernel_size, activation='tanh', 
                                      return_sequences=True, padding='same')
        self.conv2 = layers.ConvLSTM2D(filters, kernel_size, activation='tanh', 
                                      return_sequences=True, padding='same')
        self.dropout = layers.TimeDistributed(layers.Dropout(0.2))
        self.batch_norm = layers.TimeDistributed(layers.BatchNormalization())
        
    def call(self, inputs):
        x = self.conv1(inputs)
        x = self.dropout(x)
        x = self.batch_norm(x)
        x = self.conv2(x)
        
        # residual link
        if inputs.shape[-1] == x.shape[-1]:
            return layers.Add()([inputs, x])
        else:
            # If dimensions don't match, use 1x1 convolutional adjustment
            shortcut = layers.ConvLSTM2D(x.shape[-1], (1, 1), 
                                       return_sequences=True, padding='same')(inputs)
            return layers.Add()([shortcut, x])

def CreateOptimizedModel(frameCount, height, width, path, use_pretrained=True):
    """Creating an optimised model architecture"""
    inputShape = (frameCount, height, width, 3)
    
    # input layer
    inputs = layers.Input(shape=inputShape, name='time_distributed_input')
    
    if use_pretrained:
        # Using pre-trained EfficientNet as a feature extractor
        base_model = EfficientNetB0(weights='imagenet', include_top=False, 
                                   input_shape=(height, width, 3))
        base_model.trainable = False  # Freeze pre-training weights
        
        # Apply pre-trained model to each frame
        x = layers.TimeDistributed(base_model)(inputs)
        x = layers.TimeDistributed(layers.GlobalAveragePooling2D())(x)
        x = layers.TimeDistributed(layers.Dense(512, activation='relu'))(x)
    else:
        # Original ConvLSTM Architecture + Residual Connection
        x = layers.ConvLSTM2D(filters=64, kernel_size=(3, 3), activation='tanh',
                             data_format="channels_last", recurrent_dropout=0.2, 
                             return_sequences=True)(inputs)
        x = layers.MaxPooling3D(pool_size=(1, 2, 2), padding='same', 
                               data_format='channels_last')(x)
        
        # Adding a residual block
        x = ResidualBlock(128)(x)
        x = layers.MaxPooling3D(pool_size=(1, 2, 2), padding='same', 
                               data_format='channels_last')(x)
        
        x = ResidualBlock(256)(x)
        x = layers.MaxPooling3D(pool_size=(1, 2, 2), padding='same', 
                               data_format='channels_last')(x)
        
        x = ResidualBlock(512)(x)
        x = layers.GlobalAveragePooling3D()(x)
        x = layers.Reshape((frameCount, -1))(x)
    
    # Adding Attention Mechanisms
    attention_layer = MultiHeadAttention(d_model=512, num_heads=8)
    attention_output, _ = attention_layer(x, x, x)
    
    # chronological modelling
    x = layers.LSTM(256, return_sequences=True, dropout=0.3)(attention_output)
    x = layers.LSTM(128, dropout=0.3)(x)
    
    # taxon
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.3)(x)
    
    # Number of access categories
    classCount = sum(1 for _ in pathlib.Path(path+"/train").iterdir() if _.is_dir())
    outputs = layers.Dense(classCount, activation="softmax", name='dense')(x)
    
    model = Model(inputs=inputs, outputs=outputs)
    return model

def CreateLearningRateScheduler():
    """Creating a learning rate scheduler"""
    def scheduler(epoch, lr):
        if epoch < 10:
            return lr
        elif epoch < 20:
            return lr * 0.5
        else:
            return lr * 0.1
    
    return tf.keras.callbacks.LearningRateScheduler(scheduler)

def CreateEarlyStoppingCallback():
    """Creating an Early Stop Retracement"""
    return tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=5,
        restore_best_weights=True,
        verbose=1
    )

def CreateModelCheckpointCallback(modelName):
    """Creating model checkpoint callbacks"""
    return tf.keras.callbacks.ModelCheckpoint(
        filepath=f'./checkpoints/{modelName}_best.h5',
        monitor='val_accuracy',
        save_best_only=True,
        save_weights_only=False,
        verbose=1
    )

def CreateReduceLRCallback():
    """Creating Learning Rate Decay Callbacks"""
    return tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=3,
        min_lr=1e-7,
        verbose=1
    )

def MixedPrecisionTraining():
    """Enable mixed precision training"""
    policy = tf.keras.mixed_precision.Policy('mixed_float16')
    tf.keras.mixed_precision.set_global_policy(policy)

def DataAugmentation():
    """data enhancement layer"""
    return tf.keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.1),
        layers.RandomBrightness(0.1)
    ])

def OptimizedTraining(model, trainDS, valDS, testDS, epochs, modelName, folderPath):
    """Optimised training processes"""
    
    # Enable mixed precision training
    MixedPrecisionTraining()
    
    # Creating Callback Functions
    callbacks = [
        CreateEarlyStoppingCallback(),
        CreateModelCheckpointCallback(modelName),
        CreateLearningRateScheduler(),
        CreateReduceLRCallback(),
        tf.keras.callbacks.TensorBoard(log_dir=f'./logs/{modelName}', histogram_freq=1)
    ]
    
    # Using the AdamW Optimiser
    optimizer = tf.keras.optimizers.AdamW(
        learning_rate=0.001,
        weight_decay=0.0001
    )
    
    # compilation model
    model.compile(
        loss=losses.SparseCategoricalCrossentropy(from_logits=False),
        optimizer=optimizer,
        metrics=['accuracy', 'top_k_categorical_accuracy']
    )
    
    # Training Models
    history = model.fit(
        x=trainDS,
        epochs=epochs,
        validation_data=valDS,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def main():
    """Optimised main function"""
    with tf.device('/GPU:0'):
        parser = argparse.ArgumentParser()
        parser.add_argument('--model_name', type=str, default="optimized_model")
        parser.add_argument('--epochs', type=int, default=50)
        parser.add_argument('--num_frames', type=int, default=20)
        parser.add_argument('--shuffle_size', type=int, default=300)
        parser.add_argument('--batch_size', type=int, default=4)
        parser.add_argument('--use_pretrained', type=bool, default=True)
        args = parser.parse_args()
        
        modelName = args.model_name
        epochs = args.epochs
        frameCount = args.num_frames
        shuffleSize = args.shuffle_size
        batchSize = args.batch_size
        use_pretrained = args.use_pretrained
        
        height = 224
        width = 224
        folderPath = "/mnt"
        repoPath = "/model_repo"
        
        # Create the necessary directories
        os.makedirs('./checkpoints', exist_ok=True)
        os.makedirs('./logs', exist_ok=True)
        
        # Data loading and pre-processing
        trainDS, valDS, testDS = ExtractData(folderPath, frameCount)
        AUTOTUNE = tf.data.AUTOTUNE
        
        trainDS, valDS, testDS = InitialiseCache(trainDS, valDS, testDS)
        trainDS, valDS, testDS = PrefetchDataSet(trainDS, valDS, testDS, AUTOTUNE, shuffleSize)
        trainDS, valDS, testDS = InitialiseBatch(trainDS, valDS, testDS, batchSize)
        
        # Creating optimised models
        model = CreateOptimizedModel(frameCount, height, width, folderPath, use_pretrained)
        
        print(f"Number of model parameters: {model.count_params():,}")
        
        # Optimising the training process
        history = OptimizedTraining(model, trainDS, valDS, testDS, epochs, modelName, folderPath)
        
        # Visualisation results
        PlotHistory(history, modelName, folderPath)
        
        # assessment model
        test_results = model.evaluate(testDS, return_dict=True)
        print(f"Testing accuracy: {test_results['accuracy']:.4f}")
        print(f"Top-K Accuracy: {test_results['top_k_categorical_accuracy']:.4f}")
        
        # Generate Confusion Matrix
        labels = GetClassMaps(folderPath, frameCount)
        
        actual, predicted = GetConfusionResults(model, trainDS)
        PlotConfusionMatrix(actual, predicted, labels, 'training', modelName, folderPath)
        
        actual, predicted = GetConfusionResults(model, testDS)
        PlotConfusionMatrix(actual, predicted, labels, 'test', modelName, folderPath)
        
        # Save the model
        model.save(os.path.join(folderPath, modelName), save_format='tf')
        
        # Creating a Triton Package
        CreateTritonPackage(labels, modelName, folderPath, repoPath, epochs, 
                          frameCount, shuffleSize, batchSize, height, width)
        
        print("Model training complete！")
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()