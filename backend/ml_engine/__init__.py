"""
ML Models Package for KrishiSaarthi
====================================
Contains PyTorch-based models and analysis algorithms for:

- CNN: Crop health/pest detection from images (MobileNetV2)
- LSTM: Risk prediction from NDVI/weather time series
- AWD: Alternate wetting-drying irrigation detection
- Carbon Credits: Emission reduction calculations
- Health Score: Multi-factor crop health scoring fusion

All models support lazy loading to prevent startup failures
when model files are not present.

Usage:
    from ml_engine import predict_health, predict_risk_from_values
    from ml_engine import detect_awd_from_ndwi, calculate_carbon_metrics
    from ml_engine import get_health_score
"""

import importlib as _importlib


def __getattr__(name):
    """Lazy import to avoid loading torch/torchvision at package init time."""
    _lazy_map = {
        # AWD (pure Python)
        "detect_awd_from_ndwi": (".awd", "detect_awd_from_ndwi"),
        "calculate_awd_score": (".awd", "calculate_awd_score"),
        # Carbon Credits (pure Python)
        "calculate_carbon_metrics": (".cc", "calculate_carbon_metrics"),
        # CNN (requires torch)
        "predict_health": (".cnn", "predict_health"),
        "predict_health_batch": (".cnn", "predict_health_batch"),
        "get_cnn_model": (".cnn", "get_model"),
        # LSTM (requires torch)
        "predict_risk_from_values": (".lstm", "predict_risk_from_values"),
        "get_lstm_model": (".lstm", "get_model_and_scaler"),
        # Health Score (pure Python, but get_health_score lazily imports cnn/lstm)
        "get_health_score": (".health_score", "get_health_score"),
        "compute_health_score": (".health_score", "compute_health_score"),
        "get_health_rating": (".health_score", "get_health_rating"),
        # Registry (requires torch)
        "model_registry": (".registry", "registry"),
    }

    if name in _lazy_map:
        module_path, attr_name = _lazy_map[name]
        module = _importlib.import_module(module_path, __package__)
        return getattr(module, attr_name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # AWD Detection
    "detect_awd_from_ndwi",
    "calculate_awd_score",
    # Carbon Credits
    "calculate_carbon_metrics",
    # CNN (Image-based health detection)
    "predict_health",
    "predict_health_batch",
    "get_cnn_model",
    # LSTM (Time-series risk prediction)
    "predict_risk_from_values",
    "get_lstm_model",
    # Health Score (Fusion)
    "get_health_score",
    "compute_health_score",
    "get_health_rating",
    # Model Registry
    "model_registry",
]

__version__ = "2.1.0"
