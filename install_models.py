#!/usr/bin/env python3
"""
ULTIMATE CERBERUS - Model Installation Script
Downloads all required models for the 6-stage processing pipeline
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def install_package(package):
    """Install Python package"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def download_model(url, filepath):
    """Download model file"""
    print(f"Downloading {filepath.name}...")
    urllib.request.urlretrieve(url, filepath)
    print(f"✅ Downloaded {filepath.name}")

def setup_models():
    """Download and setup all required models"""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    print("ULTIMATE CERBERUS - Installing Models")
    print("=" * 50)
    
    # Install required packages
    packages = [
        "sentence-transformers",
        "transformers", 
        "torch",
        "xgboost",
        "lightgbm",
        "ultralytics",
        "paddlepaddle",
        "paddleocr"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            install_package(package)
            print(f"✅ Installed {package}")
        except Exception as e:
            print(f"⚠️ Warning: Could not install {package}: {e}")
    
    # Download YOLOv8 model
    try:
        from ultralytics import YOLO
        print("Downloading YOLOv8n model...")
        model = YOLO('yolov8n.pt')
        # Move to models directory
        import shutil
        if os.path.exists('yolov8n.pt'):
            shutil.move('yolov8n.pt', models_dir / 'yolov8n.pt')
        print("✅ YOLOv8n model ready")
    except Exception as e:
        print(f"⚠️ YOLOv8 download failed: {e}")
    
    # Initialize sentence transformers (auto-downloads)
    try:
        from sentence_transformers import SentenceTransformer
        print("Initializing sentence transformers...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence transformers ready")
    except Exception as e:
        print(f"⚠️ Sentence transformers failed: {e}")
    
    # Initialize transformers models
    try:
        from transformers import AutoTokenizer, AutoModel
        print("Initializing DistilBERT...")
        tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')
        model = AutoModel.from_pretrained('distilbert-base-uncased')
        print("✅ DistilBERT ready")
    except Exception as e:
        print(f"⚠️ DistilBERT failed: {e}")
    
    # Initialize PaddleOCR
    try:
        from paddleocr import PaddleOCR
        print("Initializing PaddleOCR...")
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        print("✅ PaddleOCR ready")
    except Exception as e:
        print(f"⚠️ PaddleOCR failed: {e}")
    
    print("\n🏆 Model installation completed!")
    print("Total estimated size: ~195MB")
    print("All models ready for ULTIMATE CERBERUS processing")

if __name__ == "__main__":
    setup_models()