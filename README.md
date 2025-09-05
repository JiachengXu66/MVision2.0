# MVision 2.0: Optimized Industrial Computer Vision System

## 📌 Project Overview
MVision 2.0 is an optimized industrial computer vision management system.  
It builds upon the baseline MVision framework and introduces key **model, system, and deployment improvements** to achieve **higher accuracy, faster inference, and better resource efficiency**.

This repository provides:
- Source code for optimized model training & inference
- Scripts for deployment and benchmarking
- Performance comparison charts and reports

---

## 🚀 Key Improvements
1. **Hybrid Attention Mechanism**  
   Combines spatial and channel attention → accuracy ↑ 6.9% (85.2% → 92.1%).

2. **Intelligent Batch Inference Engine**  
   Dynamic batch scheduling & asynchronous pipelines → inference speed ↑ 37.8% (45ms → 28ms).

3. **Optimized Residual Connections**  
   Depthwise separable convolutions + residual links → model size ↓ 37.3% (156.7MB → 98.3MB).

4. **Mixed Precision Training**  
   Adaptive precision scaling + gradient optimization → training time ↓ 27.1% (8.5h → 6.2h).

---

## 📊 Performance Summary
| Metric         | Baseline | Optimized | Change   |
|----------------|----------|-----------|----------|
| Accuracy       | 85.2%    | 92.1%     | +6.9%    |
| Inference Time | 45ms     | 28ms      | -37.8%   |
| Memory Usage   | 2.1GB    | 1.4GB     | -33.3%   |
| Throughput     | 15 FPS   | 28 FPS    | +86.7%   |
| GPU Utilization| 65%      | 89%       | +24.0%   |

📂 See `/figures` for detailed charts (accuracy, efficiency, radar plots, etc.).

---

## 🖥️ Hardware & Software Environment

### Hardware
- **GPU**: NVIDIA RTX 3080  
- **Memory**: 16GB DDR4  
- **Storage**: 500GB SSD  

### Software
- **Operating System**: Ubuntu 20.04 LTS  
- **Python**: 3.8+  
- **CUDA**: 11.2+  
- **Docker**: 20.10+  

---

## File List

### Core Optimization Files
- `optimized_train_model.py` - Optimized training model
- `optimized_inference.py` - Optimized inference engine
- `performance_comparison.py` - Performance comparison and analysis tool
- `deploy_optimized_system.py` - Automated deployment script,including system setup and deployment-related functionalities
