import cv2
import numpy as np
import tritonclient.http as httpclient
from tritonclient.utils import InferenceServerException
from collections import deque
from PIL import Image
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import time
import logging
from typing import List, Tuple, Optional
import threading
import queue

# Configuration log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedInferenceEngine:
    """Optimised inference engine"""
    
    def __init__(self, triton_url: str = 'localhost:8000', max_batch_size: int = 8):
        self.triton_url = triton_url
        self.max_batch_size = max_batch_size
        self.triton_client = httpclient.InferenceServerClient(url=triton_url)
        self.frame_buffer = {}  # Frame buffer per deployment
        self.inference_queue = queue.Queue(maxsize=100)
        self.result_cache = {}  # Results Cache
        self.performance_stats = {
            'total_inferences': 0,
            'total_time': 0,
            'avg_latency': 0,
            'throughput': 0
        }
        
        # Start the reasoning worker thread
        self.inference_thread = threading.Thread(target=self._inference_worker, daemon=True)
        self.inference_thread.start()
    
    def _inference_worker(self):
        """Reasoning Work Thread"""
        batch_requests = []
        last_batch_time = time.time()
        
        while True:
            try:
                # batch file
                timeout = 0.01  # 10ms timeout
                try:
                    request = self.inference_queue.get(timeout=timeout)
                    batch_requests.append(request)
                except queue.Empty:
                    pass
                
                current_time = time.time()
                
                # If the batch is full or times out, perform reasoning
                if (len(batch_requests) >= self.max_batch_size or 
                    (batch_requests and current_time - last_batch_time > 0.05)):
                    
                    self._process_batch(batch_requests)
                    batch_requests = []
                    last_batch_time = current_time
                    
            except Exception as e:
                logger.error(f"Reasoning about work thread errors: {e}")
                batch_requests = []
    
    def _process_batch(self, requests: List[dict]):
        """Processing Batch Reasoning Requests"""
        if not requests:
            return
        
        try:
            start_time = time.time()
            
            # Grouping requests by model
            model_groups = {}
            for req in requests:
                model_name = req['model_name']
                if model_name not in model_groups:
                    model_groups[model_name] = []
                model_groups[model_name].append(req)
            
            # Perform batch inference for each model
            for model_name, model_requests in model_groups.items():
                self._batch_inference(model_name, model_requests)
            
            # Updating performance statistics
            inference_time = time.time() - start_time
            self.performance_stats['total_inferences'] += len(requests)
            self.performance_stats['total_time'] += inference_time
            self.performance_stats['avg_latency'] = (
                self.performance_stats['total_time'] / 
                self.performance_stats['total_inferences']
            )
            self.performance_stats['throughput'] = (
                self.performance_stats['total_inferences'] / 
                self.performance_stats['total_time']
            )
            
        except Exception as e:
            logger.error(f"Batch reasoning to handle errors: {e}")
    
    def _batch_inference(self, model_name: str, requests: List[dict]):
        """执行批量推理"""
        try:
            # Preparing for batch entry
            batch_data = []
            for req in requests:
                batch_data.append(req['input_data'])
            
            if not batch_data:
                return
            
            # Stacking for batch input
            batch_input = np.stack(batch_data, axis=0)
            
            # Creating an input tensor
            input_name = requests[0]['input_name']
            output_name = requests[0]['output_name']
            
            input_tensor = httpclient.InferInput(input_name, batch_input.shape, "FP32")
            input_tensor.set_data_from_numpy(batch_input)
            
            # executive reasoning
            response = self.triton_client.infer(model_name, inputs=[input_tensor])
            output_data = response.as_numpy(output_name)
            
            # Distribution of results
            for i, req in enumerate(requests):
                result = {
                    'deployment_id': req['deployment_id'],
                    'prediction': output_data[i],
                    'timestamp': datetime.now(),
                    'confidence': self._calculate_confidence(output_data[i]),
                    'predicted_class': req['class_list'][np.argmax(output_data[i])]
                }
                
                # Calling Callback Functions
                if 'callback' in req:
                    req['callback'](result)
                
        except InferenceServerException as e:
            logger.error(f"Triton Reasoning Error: {e}")
        except Exception as e:
            logger.error(f"Batch reasoning error: {e}")
    
    def _calculate_confidence(self, output_data: np.ndarray) -> float:
        """Calculate the confidence level"""
        max_value = np.max(output_data)
        if max_value < 1:
            return np.round(max_value * 100, decimals=4)
        else:
            return np.round(max_value, decimals=4)
    
    def submit_inference(self, deployment_id: int, input_data: np.ndarray, 
                        model_name: str, class_list: List[str], 
                        input_name: str, output_name: str, 
                        callback=None) -> bool:
        """Submission of reasoning requests"""
        try:
            request = {
                'deployment_id': deployment_id,
                'input_data': input_data,
                'model_name': model_name,
                'class_list': class_list,
                'input_name': input_name,
                'output_name': output_name,
                'callback': callback,
                'timestamp': time.time()
            }
            
            self.inference_queue.put(request, block=False)
            return True
            
        except queue.Full:
            logger.warning(f"Reasoning queue is full, discarding deployment {deployment_id} such requests")
            return False
        except Exception as e:
            logger.error(f"Submit reasoning request error: {e}")
            return False
    
    def get_performance_stats(self) -> dict:
        """Getting Performance Statistics"""
        return self.performance_stats.copy()

class AdvancedFrameProcessor:
    """Advanced Frame Processor"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.frame_cache = {}
        
    def preprocess_frame_optimized(self, frame: np.ndarray, 
                                 deployment_id: int) -> np.ndarray:
        """Optimised frame pre-processing"""
        try:
            # cache key
            cache_key = f"{deployment_id}_{frame.shape}"
            
            # Check if pre-processing parameters need to be recalculated
            if cache_key not in self.frame_cache:
                self.frame_cache[cache_key] = self._calculate_preprocess_params(frame.shape)
            
            params = self.frame_cache[cache_key]
            
            # Application preprocessing
            if len(frame.shape) == 4:  # RGBA
                frame_resized = cv2.resize(frame, (self.width, self.height))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_RGBA2RGB)
            else:  # RGB
                frame_resized = cv2.resize(frame, (self.width, self.height))
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            
            # normalisation
            normalized_frame = frame_rgb.astype('float32') / 255.0
            
            # Optional data augmentation (not normally used in reasoning)
            # normalized_frame = self._apply_inference_augmentation(normalized_frame)
            
            return normalized_frame
            
        except Exception as e:
            logger.error(f"frame prep error: {e}")
            return None
    
    def _calculate_preprocess_params(self, input_shape: tuple) -> dict:
        """Calculation of pre-processing parameters"""
        return {
            'input_height': input_shape[0] if len(input_shape) > 0 else 1080,
            'input_width': input_shape[1] if len(input_shape) > 1 else 1920,
            'channels': input_shape[2] if len(input_shape) > 2 else 3
        }
    
    def _apply_inference_augmentation(self, frame: np.ndarray) -> np.ndarray:
        """Lightweight enhancements for reasoning (optional)"""
        # Usually inference is done without data augmentation, but some normalisation can be added
        return frame

class SmartFrameBuffer:
    """Intelligent Frame Buffer Manager"""
    
    def __init__(self, max_deployments: int = 50):
        self.max_deployments = max_deployments
        self.buffers = {}
        self.buffer_stats = {}
        self.lock = threading.Lock()
    
    def add_frame(self, deployment_id: int, frame: np.ndarray, 
                  max_frames: int = 20) -> bool:
        """Adding frames to the buffer"""
        with self.lock:
            if deployment_id not in self.buffers:
                self.buffers[deployment_id] = deque(maxlen=max_frames)
                self.buffer_stats[deployment_id] = {
                    'total_frames': 0,
                    'dropped_frames': 0,
                    'last_update': time.time()
                }
            
            # Check if the buffer is full
            if len(self.buffers[deployment_id]) >= max_frames:
                self.buffer_stats[deployment_id]['dropped_frames'] += 1
                return False
            
            self.buffers[deployment_id].append(frame)
            self.buffer_stats[deployment_id]['total_frames'] += 1
            self.buffer_stats[deployment_id]['last_update'] = time.time()
            return True
    
    def get_frames(self, deployment_id: int, num_frames: int) -> Optional[np.ndarray]:
        """Get the specified number of frames"""
        with self.lock:
            if deployment_id not in self.buffers:
                return None
            
            buffer = self.buffers[deployment_id]
            if len(buffer) < num_frames:
                return None
            
            # Get the latest frame
            frames = list(buffer)[-num_frames:]
            return np.stack(frames, axis=0)
    
    def clear_buffer(self, deployment_id: int):
        """Empty the buffer for a given deployment"""
        with self.lock:
            if deployment_id in self.buffers:
                self.buffers[deployment_id].clear()
    
    def get_buffer_stats(self, deployment_id: int) -> Optional[dict]:
        """Getting Buffer Statistics"""
        with self.lock:
            return self.buffer_stats.get(deployment_id, None)
    
    def cleanup_old_buffers(self, max_age: float = 300.0):
        """Cleaning up long unused buffers"""
        current_time = time.time()
        with self.lock:
            to_remove = []
            for deployment_id, stats in self.buffer_stats.items():
                if current_time - stats['last_update'] > max_age:
                    to_remove.append(deployment_id)
            
            for deployment_id in to_remove:
                if deployment_id in self.buffers:
                    del self.buffers[deployment_id]
                if deployment_id in self.buffer_stats:
                    del self.buffer_stats[deployment_id]
                logger.info(f"Clearance deployment {deployment_id} old buffer")

class PerformanceMonitor:
    """Performance Monitor"""
    
    def __init__(self):
        self.metrics = {
            'inference_count': 0,
            'total_inference_time': 0.0,
            'avg_inference_time': 0.0,
            'max_inference_time': 0.0,
            'min_inference_time': float('inf'),
            'fps': 0.0,
            'gpu_utilization': 0.0,
            'memory_usage': 0.0,
            'queue_size': 0,
            'error_count': 0
        }
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def record_inference(self, inference_time: float):
        """Recording Reasoning Time"""
        with self.lock:
            self.metrics['inference_count'] += 1
            self.metrics['total_inference_time'] += inference_time
            self.metrics['avg_inference_time'] = (
                self.metrics['total_inference_time'] / 
                self.metrics['inference_count']
            )
            self.metrics['max_inference_time'] = max(
                self.metrics['max_inference_time'], inference_time
            )
            self.metrics['min_inference_time'] = min(
                self.metrics['min_inference_time'], inference_time
            )
            
            # Calculate FPS
            elapsed_time = time.time() - self.start_time
            if elapsed_time > 0:
                self.metrics['fps'] = self.metrics['inference_count'] / elapsed_time
    
    def record_error(self):
        """recording error"""
        with self.lock:
            self.metrics['error_count'] += 1
    
    def update_system_metrics(self, gpu_util: float, memory_usage: float, 
                            queue_size: int):
        """Updating of system indicators"""
        with self.lock:
            self.metrics['gpu_utilization'] = gpu_util
            self.metrics['memory_usage'] = memory_usage
            self.metrics['queue_size'] = queue_size
    
    def get_metrics(self) -> dict:
        """Getting Performance Metrics"""
        with self.lock:
            return self.metrics.copy()
    
    def reset_metrics(self):
        """reset indicator"""
        with self.lock:
            self.metrics = {
                'inference_count': 0,
                'total_inference_time': 0.0,
                'avg_inference_time': 0.0,
                'max_inference_time': 0.0,
                'min_inference_time': float('inf'),
                'fps': 0.0,
                'gpu_utilization': 0.0,
                'memory_usage': 0.0,
                'queue_size': 0,
                'error_count': 0
            }
            self.start_time = time.time()

# Optimised inference function
async def OptimizedInference(pipeline, deployment_id: int, height: int, width: int, 
                           class_list: List[str], frame_count: int, model_name: str, 
                           input_name: str, output_name: str, 
                           inference_engine: OptimizedInferenceEngine,
                           frame_processor: AdvancedFrameProcessor,
                           frame_buffer: SmartFrameBuffer,
                           performance_monitor: PerformanceMonitor):
    """Optimised reasoning process"""
    
    def inference_callback(result):
        """Inference result callback"""
        logger.info(f"deployments {result['deployment_id']}: "
                   f"Type of projection {result['predicted_class']}, "
                   f"confidence level (math.) {result['confidence']:.2f}%")
        
        # Here you can add the result processing logic
        # Examples: saving to database, sending notifications, etc.
    
    try:
        # Obtain the app sink
        appsink = pipeline.get_by_name(f"sink_deployment_{deployment_id}")
        if not appsink:
            logger.error(f"Can't find deployment {deployment_id} 的 appsink")
            return
        
        logger.info(f"Commencement of deployment {deployment_id} Optimal reasoning")
        
        # main reasoning cycle
        while True:
            try:
                # pull frame
                sample = appsink.emit("pull-sample")
                if sample is None:
                    logger.warning(f"deployments {deployment_id} No more frames")
                    await asyncio.sleep(0.1)
                    continue
                
                # processing frame
                start_time = time.time()
                
                buffer = sample.get_buffer()
                success, map_info = buffer.map(Gst.MapFlags.READ)
                
                if not success:
                    logger.error("Buffer mapping failure")
                    continue
                
                try:
                    # Load and preprocess frames
                    input_height, input_width = 1080, 1920
                    buffered_data = np.frombuffer(map_info.data, dtype=np.uint8)
                    frame = buffered_data.reshape((input_height, input_width, 4))
                    
                    processed_frame = frame_processor.preprocess_frame_optimized(
                        frame, deployment_id
                    )
                    
                    if processed_frame is None:
                        continue
                    
                    # Add to frame buffer
                    if not frame_buffer.add_frame(deployment_id, processed_frame, frame_count):
                        continue
                    
                    # Check if there are enough frames for inference
                    frames_batch = frame_buffer.get_frames(deployment_id, frame_count)
                    if frames_batch is not None:
                        # Submission of reasoning requests
                        input_batch = np.expand_dims(frames_batch, axis=0)
                        
                        success = inference_engine.submit_inference(
                            deployment_id=deployment_id,
                            input_data=input_batch,
                            model_name=model_name,
                            class_list=class_list,
                            input_name=input_name,
                            output_name=output_name,
                            callback=inference_callback
                        )
                        
                        if success:
                            # Empty the buffer
                            frame_buffer.clear_buffer(deployment_id)
                            
                            # Recording performance
                            processing_time = time.time() - start_time
                            performance_monitor.record_inference(processing_time)
                        else:
                            performance_monitor.record_error()
                
                finally:
                    buffer.unmap(map_info)
                
                # Short hibernation to avoid excessive CPU usage
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"inference loop error: {e}")
                performance_monitor.record_error()
                await asyncio.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Inference initialisation error: {e}")

# usage example
async def main():
    """Main Function Example"""
    
    # Initialising components
    inference_engine = OptimizedInferenceEngine(
        triton_url='localhost:8000',
        max_batch_size=8
    )
    
    frame_processor = AdvancedFrameProcessor(width=224, height=224)
    frame_buffer = SmartFrameBuffer(max_deployments=50)
    performance_monitor = PerformanceMonitor()
    
    # Simulation of deployment parameters
    deployment_configs = [
        {
            'deployment_id': 1,
            'model_name': 'optimized_model',
            'class_list': ['Other', 'cooking', 'drinking', 'eating', 'pouring'],
            'frame_count': 20,
            'input_name': 'time_distributed_input',
            'output_name': 'dense'
        }
    ]
    
    # Initiating reasoning tasks
    tasks = []
    for config in deployment_configs:
        # The actual pipeline object is needed here
        # pipeline = create_gstreamer_pipeline(config['deployment_id'])
        
        task = OptimizedInference(
            pipeline=None,  # In practice, you need to pass in the pipeline
            deployment_id=config['deployment_id'],
            height=224,
            width=224,
            class_list=config['class_list'],
            frame_count=config['frame_count'],
            model_name=config['model_name'],
            input_name=config['input_name'],
            output_name=config['output_name'],
            inference_engine=inference_engine,
            frame_processor=frame_processor,
            frame_buffer=frame_buffer,
            performance_monitor=performance_monitor
        )
        tasks.append(task)
    
    # Starting Performance Monitoring Tasks
    async def monitor_performance():
        while True:
            await asyncio.sleep(10)  # Output performance statistics every 10 seconds
            metrics = performance_monitor.get_metrics()
            engine_stats = inference_engine.get_performance_stats()
            
            logger.info("=== Performance statistics ===")
            logger.info(f"Number of inferences: {metrics['inference_count']}")
            logger.info(f"Average reasoning time: {metrics['avg_inference_time']:.3f}s")
            logger.info(f"FPS: {metrics['fps']:.2f}")
            logger.info(f"Number of errors: {metrics['error_count']}")
            logger.info(f"engine throughput: {engine_stats['throughput']:.2f} req/s")
            logger.info("================")
    
    tasks.append(monitor_performance())
    
    # Run all tasks
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down....")
    except Exception as e:
        logger.error(f"main loop error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
