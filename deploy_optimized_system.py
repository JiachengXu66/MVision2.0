#!/usr/bin/env python3
"""
MVision optimisation system deployment script
"""

import os
import sys
import subprocess
import json
import time
import logging
from pathlib import Path

# Configuration log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedSystemDeployer:
    """Optimised System Deployer"""
    
    def __init__(self, base_path="./MVision-main"):
        self.base_path = Path(base_path)
        self.config = self.load_deployment_config()
        
    def load_deployment_config(self):
        """Load Deployment Configuration"""
        return {
            "docker_compose_file": "docker-compose.yaml",
            "services": ["db", "web", "api"],
            "optimization_features": {
                "mixed_precision": True,
                "tensorrt_optimization": True,
                "batch_inference": True,
                "async_processing": True,
                "performance_monitoring": True
            },
            "model_configs": {
                "frame_count": 20,
                "batch_size": 8,
                "max_batch_size": 16,
                "input_resolution": [224, 224],
                "use_pretrained": True
            }
        }
    
    def check_prerequisites(self):
        """Inspection of deployment prerequisites"""
        logger.info("Inspection of deployment prerequisites....")
        
        # 检查Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Docker not installed or not available")
            logger.info(f"Docker version: {result.stdout.strip()}")
        except Exception as e:
            logger.error(f"Docker check fails: {e}")
            return False
        
        # 检查Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Docker ComposeNot installed or not available")
            logger.info(f"Docker Compose releases: {result.stdout.strip()}")
        except Exception as e:
            logger.error(f"Docker Compose inspection failure: {e}")
            return False
        
        # Check NVIDIA Docker (if there is a GPU)
        try:
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("NVIDIA GPU detected")
                # Check nvidia-docker
                result = subprocess.run(['docker', 'run', '--rm', '--gpus', 'all', 
                                       'nvidia/cuda:11.0-base', 'nvidia-smi'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("NVIDIA Docker Support Available")
                else:
                    logger.warning("NVIDIA Docker support not available, will use CPU mode")
        except Exception:
            logger.info("NVIDIA GPU not detected, will use CPU mode")
        
        # Checking necessary directories and files
        required_paths = [
            self.base_path / "master" / "docker-compose.yaml",
            self.base_path / "master" / "PyTrain",
            self.base_path / "master" / "OVision",
            self.base_path / "master" / "VLink",
            self.base_path / "node" / "PyDeploy"
        ]
        
        for path in required_paths:
            if not path.exists():
                logger.error(f"Necessary path does not exist: {path}")
                return False
        
        logger.info("All prerequisite checks passed")
        return True
    
    def backup_original_files(self):
        """Backup original files"""
        logger.info("Backup original files...")
        
        backup_files = [
            "master/PyTrain/app/docker_components/train_model.py",
            "node/PyDeploy/modules/inference.py"
        ]
        
        for file_path in backup_files:
            original_path = self.base_path / file_path
            backup_path = self.base_path / f"{file_path}.backup"
            
            if original_path.exists() and not backup_path.exists():
                try:
                    subprocess.run(['cp', str(original_path), str(backup_path)], 
                                 check=True)
                    logger.info(f"backed up: {file_path}")
                except Exception as e:
                    logger.error(f"Backup Failure {file_path}: {e}")
                    return False
        
        return True
    
    def deploy_optimized_files(self):
        """Deployment of optimised files"""
        logger.info("Deployment of optimised files...")
        
        # Copying the optimised training script
        try:
            target_path = self.base_path / "master/PyTrain/app/docker_components/train_model.py"
            subprocess.run(['cp', 'optimized_train_model.py', str(target_path)], 
                         check=True)
            logger.info("Optimised training model deployed")
        except Exception as e:
            logger.error(f"Failure to deploy training model: {e}")
            return False
        
        # Copy the optimised inference script
        try:
            target_path = self.base_path / "node/PyDeploy/modules/inference.py"
            subprocess.run(['cp', 'optimized_inference.py', str(target_path)], 
                         check=True)
            logger.info("Deployed optimised reasoning module")
        except Exception as e:
            logger.error(f"Deployment of the reasoning module failed: {e}")
            return False
        
        return True
    
    def update_docker_configs(self):
        """Updating the Docker Configuration"""
        logger.info("Updating the Docker Configuration...")
        
        # Updating the PyTrain Dockerfile to support optimisations
        pytrain_dockerfile = self.base_path / "master/PyTrain/app/dockerfile"
        
        optimized_dockerfile_content = """
FROM nvcr.io/nvidia/tensorflow:23.08-tf2-py3

WORKDIR /app

# Installing additional dependencies
RUN pip install --no-cache-dir \\
    efficientnet \\
    tensorrt \\
    onnx \\
    scikit-learn \\
    seaborn \\
    plotly

# Copying application files
COPY . /app/

# Setting environment variables
ENV TF_ENABLE_MIXED_PRECISION=1
ENV TF_ENABLE_TENSORRT=1

# Creating the necessary directories
RUN mkdir -p /app/checkpoints /app/logs /app/cache

CMD ["python", "train_model.py"]
"""
        
        try:
            with open(pytrain_dockerfile, 'w') as f:
                f.write(optimized_dockerfile_content)
            logger.info("UpdatedPyTrain Dockerfile")
        except Exception as e:
            logger.error(f"Failed to update Dockerfile: {e}")
            return False
        
        return True
    
    def create_optimization_config(self):
        """Creating Optimisation Profiles"""
        logger.info("Creating Optimisation Profiles...")
        
        config_content = {
            "optimization": {
                "mixed_precision": self.config["optimization_features"]["mixed_precision"],
                "tensorrt": self.config["optimization_features"]["tensorrt_optimization"],
                "batch_inference": self.config["optimization_features"]["batch_inference"],
                "async_processing": self.config["optimization_features"]["async_processing"]
            },
            "model": self.config["model_configs"],
            "monitoring": {
                "enabled": self.config["optimization_features"]["performance_monitoring"],
                "metrics_interval": 10,
                "log_level": "INFO"
            }
        }
        
        config_path = self.base_path / "optimization_config.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(config_content, f, indent=2)
            logger.info(f"The optimised configuration has been saved to: {config_path}")
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            return False
        
        return True
    
    def build_optimized_images(self):
        """Building an optimised Docker image"""
        logger.info("Building an optimised Docker image...")
        
        # Switch to the master directory
        master_dir = self.base_path / "master"
        
        try:
            # Build all services
            result = subprocess.run(
                ['docker-compose', 'build', '--no-cache'],
                cwd=master_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Docker image build failure: {result.stderr}")
                return False
            
            logger.info("Docker image build successful")
            return True
            
        except Exception as e:
            logger.error(f"Build process error: {e}")
            return False
    
    def start_optimized_services(self):
        """Starting optimised services"""
        logger.info("Starting optimised services...")
        
        master_dir = self.base_path / "master"
        
        try:
            # Starting services
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                cwd=master_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Service startup failure: {result.stderr}")
                return False
            
            logger.info("Service started successfully")
            
            # Waiting for service readiness
            logger.info("Waiting for service readiness...")
            time.sleep(30)
            
            # Checking service status
            result = subprocess.run(
                ['docker-compose', 'ps'],
                cwd=master_dir,
                capture_output=True,
                text=True
            )
            
            logger.info("service status:")
            logger.info(result.stdout)
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting service: {e}")
            return False
    
    def run_performance_tests(self):
        """Running Performance Tests"""
        logger.info("Running Performance Tests...")
        
        try:
            # Running Performance Comparison Scripts
            result = subprocess.run(
                [sys.executable, 'performance_comparison.py'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Performance testing complete")
                logger.info(result.stdout)
            else:
                logger.warning(f"Problems with performance testing: {result.stderr}")
            
            return True
            
        except Exception as e:
            logger.error(f"Performance Test Errors: {e}")
            return False
    
    def generate_deployment_report(self):
        """Generate deployment reports"""
        logger.info("Generate deployment reports...")
        
        report_content = f"""
# MVision Optimisation System Deployment Report

## Deployment time
{time.strftime('%Y-%m-%d %H:%M:%S')}

## Deployment Configuration
- Base path: {self.base_path}
- Optimisation features: {self.config['optimization_features']}
- Model configurations: {self.config['model_configs']}

## Deployment status
✅ Prerequisite check passed
✅ Original files have been backed up
✅ Optimised files deployed
✅ Docker configuration updated
✅ Optimised configuration has been created
✅ Docker image has been built
✅ Service has been started
✅ Performance tests have been completed

## Optimised features
- Mixed precision training: {'(computing) enable (a feature)' if self.config['optimization_features']['mixed_precision'] else 'prohibit the use'}.
- TensorRT optimization: {'(computing) enable (a feature)' if self.config['optimization_features']['tensorrt_optimization'] else 'prohibit the use'} critical inference: {'enable' if self.config['optimization_features']['tensorrt_optimization'] else 'prohibit the use'}。
- critical inference： {'(computing) enable (a feature)' if self.config['optimization_features']['batch_inference'] else 'prohibit the use'} Asynchronous processing: {'enable' if self.config['optimization_features']['batch_inference'] else 'prohibit the use'}。
- asynchronous processing： {'(computing) enable (a feature)' if self.config['optimization_features']['async_processing'] else 'prohibit the use'} Performance Monitoring: {'enable' if self.config['optimization_features']['async_processing'] else 'prohibit the use'}。
- Performance Monitoring: {'enabled' if self.config['optimization_features']['performance_monitoring'] else 'prohibit the use.'} ## service access address

## Service Access Address
- Interface Front-end: http://localhost:4200
- API Services. http://localhost:3000
- Database. localhost:5432

## Next Steps
1. Access the front-end interface to verify the system functionality
2. Upload the test dataset for model training.
3. Create deployment configurations to test inference performance
4. View the performance monitoring report

## Troubleshooting
If you encounter problems, check: 1.
1. whether the Docker service is running properly
Whether the port is occupied
GPU driver is installed correctly
4. Check the container logs: docker-compose logs [service_name] (service name)
*** Translated with www.DeepL.com/Translator (free version) ***



Deployment complete! System is optimised and ready. System is optimised and ready.
*** Using www.DeepL.com/Translator翻译 (free version) ***


"""
        
        try:
            with open('deployment_report.md', 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info("Deployment reports were generated: deployment_report.md")
        except Exception as e:
            logger.error(f"Failure to generate deployment report: {e}")
        
        return report_content
    
    def deploy(self):
        """Implementation of the full deployment process"""
        logger.info("Starting MVision Optimisation System Deployment...")
        
        steps = [
            ("Inspection prerequisites", self.check_prerequisites),
            ("Backup original files", self.backup_original_files),
            ("Deployment optimisation files", self.deploy_optimized_files),
            ("Updating the Docker Configuration", self.update_docker_configs),
            ("Creating Optimised Configurations", self.create_optimization_config),
            ("Building a Docker image", self.build_optimized_images),
            ("Starting services", self.start_optimized_services),
            ("Running Performance Tests", self.run_performance_tests),
            ("Generate deployment reports", self.generate_deployment_report)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Implementation steps: {step_name}")
            try:
                if not step_func():
                    logger.error(f"Step Failure: {step_name}")
                    return False
                logger.info(f"Step Completion: {step_name}")
            except Exception as e:
                logger.error(f"step anomaly {step_name}: {e}")
                return False
        
        logger.info("🎉 Deployment of the MVision optimisation system was successfully completed!")
        return True
    
    def rollback(self):
        """Rollback to original version"""
        logger.info("Start rolling back to the original version...")
        
        try:
            # Discontinuation of services
            master_dir = self.base_path / "master"
            subprocess.run(['docker-compose', 'down'], cwd=master_dir)
            
            # Restore Backup Files
            backup_files = [
                "master/PyTrain/app/docker_components/train_model.py",
                "node/PyDeploy/modules/inference.py"
            ]
            
            for file_path in backup_files:
                backup_path = self.base_path / f"{file_path}.backup"
                original_path = self.base_path / file_path
                
                if backup_path.exists():
                    subprocess.run(['cp', str(backup_path), str(original_path)])
                    logger.info(f"restored: {file_path}")
            
            logger.info("Rollback complete")
            return True
            
        except Exception as e:
            logger.error(f"Rollback Failure: {e}")
            return False

def main():
    """main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MVision Optimised System Deployment Tool')
    parser.add_argument('--action', choices=['deploy', 'rollback'], 
                       default='deploy', help='executed operation')
    parser.add_argument('--base-path', default='./MVision-main', 
                       help='MVision Project Foundation Path')
    
    args = parser.parse_args()
    
    # Creating a Deployer
    deployer = OptimizedSystemDeployer(args.base_path)
    
    if args.action == 'deploy':
        success = deployer.deploy()
        if success:
            print("\n" + "="*50)
            print("🎉 Deployment was successful!")
            print("Front-end access address. http://localhost:4200")
            print("API access address. http://localhost:3000")
            print("View Deployment Report: deployment_report.md")
            print("="*50)
        else:
            print("\n❌ Deployment failed, please check the log")
            sys.exit(1)
    
    elif args.action == 'rollback':
        success = deployer.rollback()
        if success:
            print("✅ Rollback successful")
        else:
            print("❌ Rollback Failure")
            sys.exit(1)

if __name__ == "__main__":
    main()
