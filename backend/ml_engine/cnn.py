"""
CNN Model for Crop Health Detection
=====================================
Uses MobileNetV2 to classify crop images as Healthy or Infested.
"""
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Get the directory where this file is located for robust path resolution
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
# Models are stored in ml_models directory (sibling to ml_engine)
_MODELS_DIR = os.path.join(os.path.dirname(_MODULE_DIR), "ml_models")
_DEFAULT_MODEL_PATH = os.path.join(_MODELS_DIR, "crop_health_model.pth")

# Image preprocessing pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Lazy-loaded model instance
_model: Optional[nn.Module] = None
_model_loaded: bool = False
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_model(model_path: str = _DEFAULT_MODEL_PATH, device: str = DEVICE) -> Optional[nn.Module]:
    """
    Load the crop health CNN model from disk.
    
    Args:
        model_path: Path to the .pth model file
        device: Device to load model on ('cpu' or 'cuda')
    
    Returns:
        Loaded model or None if loading fails
    """
    if not os.path.exists(model_path):
        logger.warning(f"Model file not found at {model_path}. Health prediction will return fallback values.")
        return None
    
    try:
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(model.last_channel, 1)
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
        model.eval()
        logger.info(f"CNN model loaded successfully from {model_path}")
        return model.to(device)
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        return None


def get_model() -> Optional[nn.Module]:
    """
    Get the loaded model instance (lazy loading pattern).
    """
    global _model, _model_loaded
    
    if not _model_loaded:
        _model = load_model(_DEFAULT_MODEL_PATH, DEVICE)
        _model_loaded = True
    
    return _model


def predict_health(img_path: str, device: str = DEVICE) -> Dict[str, Any]:
    """
    Predict crop health from an image.
    
    Args:
        img_path: Path to the image file
        device: Device to run inference on
    
    Returns:
        Dictionary with prediction results:
        - probability: float (0-1, where 1 = healthy)
        - class: "Healthy" or "Infested"
        - confidence: str ("High", "Medium", "Low")
        Or error dict if prediction fails
    """
    model = get_model()
    
    if model is None:
        logger.warning("Model not loaded. Returning fallback prediction.")
        return {
            "error": "Model not available",
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None",
            "fallback": True
        }
    
    # Validate image path
    if not img_path or not os.path.exists(img_path):
        return {
            "error": f"Image file not found: {img_path}",
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None"
        }
    
    try:
        # Load and preprocess image
        img = Image.open(img_path).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            output = model(img_tensor)
            prob = torch.sigmoid(output).item()
        
        # Determine confidence level
        if prob > 0.8 or prob < 0.2:
            confidence = "High"
        elif prob > 0.65 or prob < 0.35:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return {
            "probability": float(prob),
            "class": "Healthy" if prob > 0.5 else "Infested",
            "confidence": confidence,
            "device": device
        }
        
    except Exception as e:
        logger.error(f"Prediction failed for {img_path}: {e}")
        return {
            "error": str(e),
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None"
        }


# For backward compatibility - preload on import if model exists
# This is optional and can be enabled/disabled based on preference
# _model = get_model()  # Uncomment to enable eager loading
