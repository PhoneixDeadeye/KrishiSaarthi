"""
CNN Model for Crop Health Detection
=====================================
Uses MobileNetV2 to classify crop images as Healthy or Infested.
Supports both single and batch inference.
"""
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import logging
from typing import Optional, Dict, Any, List

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
        logger.warning("Model file not found at %s. Health prediction will return fallback values.", model_path)
        return None
    
    try:
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(model.last_channel, 1)
        model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
        model.eval()
        logger.info("CNN model loaded successfully from %s", model_path)
        return model.to(device)
    except Exception as e:
        logger.error("Failed to load model from %s: %s", model_path, e)
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
        logger.error("Prediction failed for %s: %s", img_path, e, exc_info=True)
        return {
            "error": "Prediction failed",
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None"
        }


# For backward compatibility - preload on import if model exists
# This is optional and can be enabled/disabled based on preference
# _model = get_model()  # Uncomment to enable eager loading


def predict_health_batch(img_paths: List[str], device: str = DEVICE) -> List[Dict[str, Any]]:
    """
    Predict crop health for a batch of images in a single forward pass.

    Args:
        img_paths: List of paths to image files
        device: Device to run inference on

    Returns:
        List of result dicts (same schema as predict_health)
    """
    model = get_model()

    if model is None:
        fallback = {
            "error": "Model not available",
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None",
            "fallback": True,
        }
        return [dict(fallback) for _ in img_paths]

    results: List[Dict[str, Any]] = [None] * len(img_paths)  # type: ignore[assignment]
    valid_indices: List[int] = []
    tensors: List[torch.Tensor] = []

    for idx, path in enumerate(img_paths):
        if not path or not os.path.exists(path):
            results[idx] = {
                "error": f"Image file not found: {path}",
                "probability": 0.5,
                "class": "Unknown",
                "confidence": "None",
            }
            continue
        try:
            img = Image.open(path).convert("RGB")
            tensors.append(transform(img))
            valid_indices.append(idx)
        except Exception as exc:
            logger.error("Failed to load image %s: %s", path, exc)
            results[idx] = {
                "error": "Image load failed",
                "probability": 0.5,
                "class": "Unknown",
                "confidence": "None",
            }

    # Run batch inference on all valid images at once
    if tensors:
        try:
            batch = torch.stack(tensors).to(device)
            with torch.no_grad():
                outputs = model(batch)
                probs = torch.sigmoid(outputs).cpu().squeeze(-1).tolist()

            # Handle single-result case (tolist returns a scalar)
            if isinstance(probs, float):
                probs = [probs]

            for i, prob in enumerate(probs):
                idx = valid_indices[i]
                if prob > 0.8 or prob < 0.2:
                    confidence = "High"
                elif prob > 0.65 or prob < 0.35:
                    confidence = "Medium"
                else:
                    confidence = "Low"
                results[idx] = {
                    "probability": float(prob),
                    "class": "Healthy" if prob > 0.5 else "Infested",
                    "confidence": confidence,
                    "device": device,
                }
        except Exception as exc:
            logger.error("Batch inference failed: %s", exc, exc_info=True)
            for i in valid_indices:
                if results[i] is None:
                    results[i] = {
                        "error": "Batch prediction failed",
                        "probability": 0.5,
                        "class": "Unknown",
                        "confidence": "None",
                    }

    return results
