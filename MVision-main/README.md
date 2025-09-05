# Project Overview

This repository contains the content for a proof of concept implementation of computer vision systems in industry. The project explores scalability and performance using the NVIDIA ecosystem, aiming to create an example scaffold for implementing a system accessible to non-technical users.

---

## Image Demos

### Model Deployment Configuration 
This shows the deployment creation interface, with the overall deployment summarised on the right of the screen.

![DeploymentCreationInterface](imgs/Deployment%20Configuration.png)

### Report Configuration
This shows the report creation interface, with the future report preview on the right of the screen.
![ReportCreationInterface](imgs/Report%20Configuration.png)

### Visulisation of Deployment Data Recieved
This shows a visualisation of the prediction on a given set of cameras. Each camera holds 3 deployments utilising 3 different CV models.
![DeploymentVisualisation](imgs/Deployment%20Visualisation.png)

### Live Report Data
This shows a report displaying data from an active deployment.
![LiveReport](imgs/Live%20Deployment%20Report.png)

---

## Hardware Used

### Host Machine
- Machine: Personal Computer
- CPU: Ryzen 5600X
- GPU: EVGA RTX 2070 Super 8GB
- RAM: 16 GB DDR4
- OS: Ubuntu 22.04

#### Drivers
- CUDA Version: **12.3**
- CuDNN: **8**
- Driver Version: **545.23.08**

### Client Machine 1
- Machine: CONNECTTECH Rudi AGX Xavier
- CPU: ARMv8
- GPU: iGPU 
- RAM: 32 GB
- OS: Jetpack **4.6.2** (L4T **32.7.2**)

### Client Machine 2
- Machine: Jetson Nano 2GB Dev Board
- RAM: 2 GB
- OS: Jetpack **4.6.2** (L4T **32.7.2**)

Note: This was only used to test PyDeploy and Triton, not to dev on.
Currently due to the low ram the board cannot support both Triton and PyDeploy whilst running the GPU for inference.
It can however run the camera pipeline and frame extraction and redirect inferencing to an existing Triton server on a running Xavier.

#### Drivers
- CUDA Version: **10.2**
- CuDNN: **8**
- TensorRT: **8.2.1.8**

---

## Software Implementations

### Host Machine

#### <span style="color:#005F99">PyTrain</span>
- **Function:** Automation Of Model Creation
- **Supported Frameworks:** 
  - **<span style="color:#008000">Tensorflow2</span>**
  - **<span style="color:#FF0000">Tensorflow1</span>**
  - **<span style="color:#FF0000">PyTorch</span>**
  - **<span style="color:#FF0000">TensorRT</span>**
  - **<span style="color:#FF0000">ONNX</span>**
- **Language:** Python, Docker

#### <span style="color:#005F99">OVision</span>
- **Function:** Host Frontend CV Management System
- **Framework:** Angular **16**
- **Language:** HTML, SASS, TypeScript, Docker

#### <span style="color:#005F99">Postgres</span>
- **Function:** Host Database Implementation
- **Framework:** PostgreSQL **16.2**
- **Language:** PSQL, bash, Docker

#### <span style="color:#005F99">VLink</span>
- **Function:** Host API For Communication Between Instances
- **Framework:** NodeJS **16**
- **Language:** TS (written), JS (compiled)

### Client Machine

#### <span style="color:#008000">Triton</span>
- **Function:** Host Triton Inference Server For Model Serving
- **Language:** Docker


