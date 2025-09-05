#!/bin/bash

cat ~/api.key | docker login nvcr.io --username '$oauthtoken' --password-stdin
docker build -t "cudatf:latest" .
#docker run --runtime="nvidia" --gpus all -it --name nvidia_check cudatf:Dockerfile
``