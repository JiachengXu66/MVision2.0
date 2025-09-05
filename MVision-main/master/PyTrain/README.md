# PyTrain

PyTrain relies on three things: 
- NVIDIA nvcr.io API key at ~/api.key
- Datasets contained in the source folder
- Being run from the app folder

The following folders also need to be present:
./app/docker_components/cache
./app/sources
./model_repo
./model_tasks
./results

PyTrain outputs config files, one of Triton format and one of its own custom format, these are explained below.

## NVIDIA API KEY
Can be generated from your NVIDIA developer account and placed into the given file

## Datasets
Datasets of mp4 file type need to be placed within the sources folder.
The file structure should be of:
```tree
/app
    /sources
            /dataset1Name
                /class1_subclass1
                /class1_subclass2
                /class1_subclass3
                /class2_subclass1
                /class3_subclass1
            /dataset2Name
                /class1_subclass1
                /class1_subclass2
                /class1_subclass3
                /class2_subclass1
                /class3_subclass1
```
Here dataset1Name should be = to the source name in the PostgresDB
Additionally PyTrain extracts only the class name prior to the _, this allows functionality of segregation between subsets:
i.e cooking_cuttingbread holds videos only cutting bread. However when cooking is selected this will be combined with cooking_peelingpotatoes
Folders MUST be of this format otherwise Pytrain wont be able to successfully segregate the classes
## Run from app folder
This is just because of how some of the paths are coded (./sources being one of them), you could fix this if you wanted

## Config format

Both triton config.pbtxt and modelName.config examples around found in the "examples" folder.
Tritons can be looked at via their documentation.

PyTrains config looks as follows:

```ini
[PREDICTION]
num_frames = 20
class_list = ['Other', 'cooking', 'drinking', 'eating', 'pouring']
height = 224
width = 224
input_name = time_distributed_input
output_name = dense

[TRAINING]
epochs = 50
shuffle_size = 300
batch_size = 4
```
- num_frames: dictates number of frames gathered per inference
- class_list: the labels for the given model
- height: height video should be cropped to for inference
- width: width video should be cropped to for inference
- input_name: input name for shape to be supplied to model
- output_name: output name for result to be retrieved from model
- epochs: number of epochs model was trained on
- shuffle_size: shuffle size model was trained on 
- batch_size: batch size model was trained on

## Extra

/app/container_up.sh is just a bash script to run the container without requiring to run the entire PyTrain pipeline (api call, gather data etc)
It is purely a rebuilding and debugging tool.