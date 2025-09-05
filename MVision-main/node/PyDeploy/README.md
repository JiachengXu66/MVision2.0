# PyDeploy

PyDeploy relies on three things: 
- Triton docker container service
- The Node Config File
- Mounted model_repo from PyTrain at /mnt/model_repo

The following folders also need to be present:
./analytics/Logs
./results

## Node config
An example is placed in the examples folder to show the format.

It should consist of the master:
- Master ip address
- Master port
- API key (fresh for new nodes)
Other values are generated on first initialisation.

## Triton Service
Can be run via "docker compose up" in the /node directory

## Mounted model_repo
This can be done using nfs mounting. This is also required for Triton to mount model_repo to its container

