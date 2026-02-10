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

from .awd import detect_awd_from_ndwi, calculate_awd_score
from .cc import calculate_carbon_metrics
from .cnn import predict_health, get_model as get_cnn_model
from .lstm import predict_risk_from_values, get_model_and_scaler as get_lstm_model
from .health_score import get_health_score, compute_health_score, get_health_rating

__all__ = [
    # AWD Detection
    'detect_awd_from_ndwi',
    'calculate_awd_score',
    
    # Carbon Credits
    'calculate_carbon_metrics',
    
    # CNN (Image-based health detection)
    'predict_health',
    'get_cnn_model',
    
    # LSTM (Time-series risk prediction)
    'predict_risk_from_values',
    'get_lstm_model',
    
    # Health Score (Fusion)
    'get_health_score',
    'compute_health_score',
    'get_health_rating',
]

__version__ = '2.0.0'
