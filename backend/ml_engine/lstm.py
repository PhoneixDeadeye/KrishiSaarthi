"""
LSTM Model for Crop Risk Prediction
=====================================
Uses LSTM to predict pest/disease risk from time series data.
"""
import torch
import torch.nn as nn
import numpy as np
import os
import logging
from typing import Optional, Dict, Any, List, Union

logger = logging.getLogger(__name__)

# Get the directory where this file is located for robust path resolution
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
# Models are stored in ml_models directory (sibling to ml_engine)
_MODELS_DIR = os.path.join(os.path.dirname(_MODULE_DIR), "ml_models")
_DEFAULT_MODEL_PATH = os.path.join(_MODELS_DIR, "risk_lstm_final.pth")
_DEFAULT_SCALER_PATH = os.path.join(_MODELS_DIR, "risk_scaler.save")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


class RiskLSTM(nn.Module):
    """LSTM model for predicting crop disease/pest risk."""
    
    def __init__(self, input_size: int = 4, hidden_size: int = 64, 
                 num_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0
        )
        self.fc = nn.Linear(hidden_size, 1)
        self.act = nn.Sigmoid()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        out = out[:, -1, :]  # Take last timestep
        out = self.fc(out)
        return self.act(out)


# Lazy-loaded model and scaler
_risk_model: Optional[RiskLSTM] = None
_risk_scaler: Optional[Any] = None
_model_loaded: bool = False


def load_risk_model(model_path: str = _DEFAULT_MODEL_PATH, 
                    scaler_path: str = _DEFAULT_SCALER_PATH,
                    device: str = DEVICE):
    """
    Load the LSTM risk model and scaler from disk.
    
    Args:
        model_path: Path to the .pth model file
        scaler_path: Path to the .save scaler file
        device: Device to load model on
    
    Returns:
        Tuple of (model, scaler) or (None, None) if loading fails
    """
    import joblib
    
    if not os.path.exists(model_path):
        logger.warning(f"Risk model not found at {model_path}. Risk prediction will return fallback values.")
        return None, None
    
    if not os.path.exists(scaler_path):
        logger.warning(f"Risk scaler not found at {scaler_path}. Risk prediction will return fallback values.")
        return None, None
    
    try:
        model = RiskLSTM(input_size=4, hidden_size=64, num_layers=2).to(device)
        ckpt = torch.load(model_path, map_location=device, weights_only=True)
        model.load_state_dict(ckpt['state_dict'])
        model.eval()
        
        scaler = joblib.load(scaler_path)
        logger.info(f"LSTM model and scaler loaded successfully")
        return model, scaler
        
    except Exception as e:
        logger.error(f"Failed to load risk model or scaler: {e}")
        return None, None


def get_model_and_scaler():
    """
    Get the loaded model and scaler instances (lazy loading pattern).
    """
    global _risk_model, _risk_scaler, _model_loaded
    
    if not _model_loaded:
        _risk_model, _risk_scaler = load_risk_model()
        _model_loaded = True
    
    return _risk_model, _risk_scaler


def predict_risk_from_values(
    sequence: Union[List, Dict], 
    device: str = DEVICE
) -> Dict[str, Any]:
    """
    Predict crop risk from time series data.
    
    Args:
        sequence: Either:
            - List of [ndvi, rainfall, temp, humidity] arrays
            - Dict with keys: ndvi_time_series, rainfall_mm, temperature_K, soil_moisture
        device: Device to run inference on
    
    Returns:
        Dictionary with prediction results:
        - risk_probability: float (0-1)
        - risk_level: "High", "Medium", or "Low"
        - recommendation: str
        Or error dict if prediction fails
    """
    model, scaler = get_model_and_scaler()
    
    # Check if model is available
    if model is None or scaler is None:
        logger.warning("LSTM model not loaded. Returning fallback prediction.")
        return {
            "error": "Risk model not available",
            "risk_probability": 0.5,
            "risk_level": "Unknown",
            "recommendation": "Model unavailable - please check your fields manually",
            "fallback": True
        }
    
    try:
        # Parse input data
        if isinstance(sequence, dict):
            seq_array = _parse_dict_sequence(sequence)
        else:
            seq_array = sequence
        
        # Validate sequence
        if not seq_array or len(seq_array) == 0:
            return {
                "error": "Empty sequence provided",
                "risk_probability": 0.5,
                "risk_level": "Unknown",
                "recommendation": "Insufficient data for risk assessment"
            }
        
        # Convert and scale
        seq_array = np.array(seq_array).astype(np.float32)
        
        # Handle NaN values
        seq_array = np.nan_to_num(seq_array, nan=0.0)
        
        seq_scaled = scaler.transform(seq_array)
        input_tensor = torch.tensor(seq_scaled).unsqueeze(0).to(device)
        
        # Run inference
        with torch.no_grad():
            prob = float(model(input_tensor).cpu().item())
        
        # Determine risk level and recommendation
        if prob > 0.7:
            risk_level = "High"
            recommendation = "Immediate attention required. Inspect fields for pest/disease signs and consider preventive treatment."
        elif prob > 0.4:
            risk_level = "Medium"
            recommendation = "Monitor closely. Check crop health regularly and prepare preventive measures."
        else:
            risk_level = "Low"
            recommendation = "Conditions appear favorable. Continue regular maintenance."
        
        return {
            "risk_probability": round(prob, 4),
            "risk_level": risk_level,
            "recommendation": recommendation,
            "data_points": len(seq_array)
        }
        
    except Exception as e:
        logger.error(f"Risk prediction failed: {e}", exc_info=True)
        return {
            "error": "Risk prediction failed",
            "risk_probability": 0.5,
            "risk_level": "Unknown",
            "recommendation": "Prediction failed - please try again"
        }


def _parse_dict_sequence(payload: Dict) -> List:
    """
    Parse a dictionary payload into a sequence array.
    
    Expected payload format:
    {
        "ndvi_time_series": [{"NDVI": 0.5}, ...],
        "rainfall_mm": 10.0,
        "temperature_K": 300,
        "soil_moisture": 0.3
    }
    """
    ndvi_series = payload.get("ndvi_time_series", [])
    
    if not ndvi_series:
        return []
    
    # Convert temperature from Kelvin to Celsius
    temp_k = payload.get("temperature_K", 300)
    temp_c = (temp_k - 273.15) if temp_k and temp_k > 200 else 25.0
    
    # Get other values with defaults
    rainfall = payload.get("rainfall_mm", 0.0) or 0.0
    humidity = payload.get("soil_moisture", 0.0) or 0.0
    
    seq_array = []
    for row in ndvi_series:
        if isinstance(row, dict):
            ndvi = row.get("NDVI", 0.0) or 0.0
        else:
            ndvi = float(row) if row else 0.0
        seq_array.append([ndvi, rainfall, temp_c, humidity])
    
    return seq_array
