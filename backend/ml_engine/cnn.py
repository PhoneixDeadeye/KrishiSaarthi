"""
CNN Model for Crop Disease Detection (38-Class)
=================================================
Uses MobileNetV2 to classify crop images into 38 PlantVillage disease classes.
Falls back to binary model if 38-class model not found.
Supports both single and batch inference.
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_MODELS_DIR = os.path.join(os.path.dirname(_MODULE_DIR), "ml_models")
_MULTICLASS_MODEL_PATH = os.path.join(_MODELS_DIR, "crop_disease_model_38class.pth")
_BINARY_MODEL_PATH = os.path.join(_MODELS_DIR, "crop_health_model.pth")
_CLASS_NAMES_PATH = os.path.join(_MODELS_DIR, "class_names_38.json")

# Image preprocessing pipeline (same for both model types)
transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)

# Lazy-loaded instances
_model: Optional[nn.Module] = None
_model_loaded: bool = False
_model_type: str = "none"  # "multiclass", "binary", or "none"
_class_names: List[str] = []
_healthy_indices: set = set()

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def _load_class_names() -> tuple:
    """Load class names and healthy indices from JSON."""
    global _class_names, _healthy_indices
    if os.path.exists(_CLASS_NAMES_PATH):
        with open(_CLASS_NAMES_PATH) as f:
            data = json.load(f)
            _class_names = data.get("classes", [])
            _healthy_indices = set(data.get("healthy_indices", []))
    else:
        # Default PlantVillage classes
        _class_names = [
            "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
            "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew",
            "Cherry_(including_sour)___healthy",
            "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
            "Corn_(maize)___Common_rust_", "Corn_(maize)___Northern_Leaf_Blight",
            "Corn_(maize)___healthy", "Grape___Black_rot", "Grape___Esca_(Black_Measles)",
            "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
            "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot",
            "Peach___healthy", "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy",
            "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
            "Raspberry___healthy", "Soybean___healthy", "Squash___Powdery_mildew",
            "Strawberry___Leaf_scorch", "Strawberry___healthy", "Tomato___Bacterial_spot",
            "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
            "Tomato___Septoria_leaf_spot",
            "Tomato___Spider_mites Two-spotted_spider_mite",
            "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
            "Tomato___Tomato_mosaic_virus", "Tomato___healthy",
        ]
        _healthy_indices = {i for i, n in enumerate(_class_names) if "healthy" in n.lower()}
    return _class_names, _healthy_indices


def load_model(device: str = DEVICE) -> Optional[nn.Module]:
    """
    Load the best available crop health model.
    Priority: 38-class multiclass > binary model > None
    """
    global _model_type

    # Try 38-class model first
    if os.path.exists(_MULTICLASS_MODEL_PATH):
        try:
            ckpt = torch.load(_MULTICLASS_MODEL_PATH, map_location=device, weights_only=False)
            num_classes = ckpt.get("num_classes", 38)
            model = models.mobilenet_v2(weights=None)
            model.classifier = nn.Sequential(
                nn.Dropout(p=0.2),
                nn.Linear(model.last_channel, num_classes),
            )
            model.load_state_dict(ckpt["state_dict"])
            model.eval()
            _model_type = "multiclass"
            _load_class_names()
            logger.info("38-class CNN model loaded successfully (%d classes)", num_classes)
            return model.to(device)
        except Exception as e:
            logger.error("Failed to load 38-class model: %s", e)

    # Fall back to binary model
    if os.path.exists(_BINARY_MODEL_PATH):
        try:
            model = models.mobilenet_v2(weights=None)
            model.classifier[1] = nn.Linear(model.last_channel, 1)
            model.load_state_dict(
                torch.load(_BINARY_MODEL_PATH, map_location=device, weights_only=True)
            )
            model.eval()
            _model_type = "binary"
            logger.info("Binary CNN model loaded (fallback)")
            return model.to(device)
        except Exception as e:
            logger.error("Failed to load binary model: %s", e)

    logger.warning("No CNN model found. Predictions will return fallback values.")
    _model_type = "none"
    return None


def get_model() -> Optional[nn.Module]:
    """Get the loaded model instance (lazy loading pattern)."""
    global _model, _model_loaded
    if not _model_loaded:
        _model = load_model(DEVICE)
        _model_loaded = True
    return _model


def get_model_type() -> str:
    """Return the type of loaded model: 'multiclass', 'binary', or 'none'."""
    get_model()  # ensure loaded
    return _model_type


def predict_health(img_path: str, device: str = DEVICE) -> Dict[str, Any]:
    """
    Predict crop health/disease from an image.

    For 38-class model: returns disease class, confidence, and healthy probability.
    For binary model: returns healthy probability and class.
    """
    model = get_model()

    if model is None:
        return {
            "error": "Model not available",
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None",
            "fallback": True,
        }

    if not img_path or not os.path.exists(img_path):
        return {
            "error": f"Image file not found: {img_path}",
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None",
        }

    try:
        img = Image.open(img_path).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(img_tensor)

        if _model_type == "multiclass":
            # Multi-class: softmax probabilities
            probs = torch.softmax(output, dim=1).squeeze(0)
            top_prob, top_idx = probs.max(0)
            top_prob = top_prob.item()
            top_idx = top_idx.item()

            predicted_class = _class_names[top_idx] if top_idx < len(_class_names) else f"class_{top_idx}"
            is_healthy = top_idx in _healthy_indices

            # Compute total healthy probability (sum of all healthy class probs)
            healthy_prob = sum(probs[i].item() for i in _healthy_indices if i < len(probs))

            # Top-3 predictions
            top3_probs, top3_indices = probs.topk(min(3, len(probs)))
            top3 = [
                {"class": _class_names[idx.item()] if idx.item() < len(_class_names) else f"class_{idx.item()}",
                 "probability": round(p.item(), 4)}
                for p, idx in zip(top3_probs, top3_indices)
            ]

            # Confidence level
            if top_prob > 0.8:
                confidence = "High"
            elif top_prob > 0.5:
                confidence = "Medium"
            else:
                confidence = "Low"

            # Extract crop and disease from class name
            parts = predicted_class.split("___")
            crop_name = parts[0].replace("_", " ") if parts else "Unknown"
            disease_name = parts[1].replace("_", " ") if len(parts) > 1 else "Unknown"

            return {
                "probability": round(healthy_prob, 4),
                "class": "Healthy" if is_healthy else "Infested",
                "predicted_disease": predicted_class,
                "crop_detected": crop_name,
                "disease_name": disease_name if not is_healthy else "None",
                "confidence": confidence,
                "confidence_score": round(top_prob, 4),
                "top_predictions": top3,
                "model_type": "multiclass_38",
                "device": device,
            }

        else:
            # Binary model path
            prob = torch.sigmoid(output).item()
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
                "model_type": "binary",
                "device": device,
            }

    except Exception as e:
        logger.error("Prediction failed for %s: %s", img_path, e, exc_info=True)
        return {
            "error": "Prediction failed",
            "probability": 0.5,
            "class": "Unknown",
            "confidence": "None",
        }


def predict_health_batch(
    img_paths: List[str], device: str = DEVICE
) -> List[Dict[str, Any]]:
    """Predict crop health for a batch of images."""
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

    results: List[Dict[str, Any]] = [None] * len(img_paths)
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

    if tensors:
        try:
            batch = torch.stack(tensors).to(device)
            with torch.no_grad():
                outputs = model(batch)

            if _model_type == "multiclass":
                all_probs = torch.softmax(outputs, dim=1)
                for i, idx in enumerate(valid_indices):
                    probs = all_probs[i]
                    top_prob, top_idx = probs.max(0)
                    top_prob, top_idx = top_prob.item(), top_idx.item()
                    predicted_class = _class_names[top_idx] if top_idx < len(_class_names) else f"class_{top_idx}"
                    is_healthy = top_idx in _healthy_indices
                    healthy_prob = sum(probs[j].item() for j in _healthy_indices if j < len(probs))

                    if top_prob > 0.8:
                        confidence = "High"
                    elif top_prob > 0.5:
                        confidence = "Medium"
                    else:
                        confidence = "Low"

                    results[idx] = {
                        "probability": round(healthy_prob, 4),
                        "class": "Healthy" if is_healthy else "Infested",
                        "predicted_disease": predicted_class,
                        "confidence": confidence,
                        "confidence_score": round(top_prob, 4),
                        "model_type": "multiclass_38",
                        "device": device,
                    }
            else:
                probs = torch.sigmoid(outputs).cpu().squeeze(-1).tolist()
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
                        "model_type": "binary",
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
