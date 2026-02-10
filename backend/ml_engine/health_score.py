"""
Health Score Module
====================
Fuses CNN image analysis, NDVI data, and LSTM risk prediction 
into a comprehensive crop health score.
"""
import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def compute_health_score(
    p_cnn_healthy: float, 
    ndvi_raw: float, 
    risk_prob: float, 
    w1: float = 0.4, 
    w2: float = 0.35, 
    w3: float = 0.25
) -> float:
    """
    Compute weighted health score from multiple indicators.
    
    Args:
        p_cnn_healthy: CNN model probability (0-1, 1=healthy)
        ndvi_raw: Raw NDVI value (typically -1 to 1, clamped to 0-1)
        risk_prob: LSTM risk probability (0-1, 1=high risk)
        w1: Weight for CNN score
        w2: Weight for NDVI score
        w3: Weight for risk score
    
    Returns:
        Composite health score (0-1, 1=excellent health)
    """
    # Normalize NDVI to 0-1 range
    ndvi_norm = float(np.clip(ndvi_raw, 0.0, 1.0))
    
    # Invert risk probability (high risk = low health)
    risk_health = 1.0 - float(risk_prob)
    
    # Weighted combination
    health_score = w1 * p_cnn_healthy + w2 * ndvi_norm + w3 * risk_health
    
    return float(np.clip(health_score, 0, 1))


def get_health_rating(score: float) -> Dict[str, Any]:
    """
    Convert numeric score to rating and recommendations.
    """
    if score >= 0.8:
        return {
            "rating": "Excellent",
            "color": "green",
            "recommendation": "Crops are thriving. Continue current practices."
        }
    elif score >= 0.6:
        return {
            "rating": "Good",
            "color": "lightgreen",
            "recommendation": "Crops are healthy. Monitor for any changes."
        }
    elif score >= 0.4:
        return {
            "rating": "Fair",
            "color": "yellow",
            "recommendation": "Some stress detected. Consider irrigation or nutrient adjustments."
        }
    elif score >= 0.2:
        return {
            "rating": "Poor",
            "color": "orange",
            "recommendation": "Significant stress. Inspect for pests/disease and take corrective action."
        }
    else:
        return {
            "rating": "Critical",
            "color": "red",
            "recommendation": "Urgent attention needed. Crops show severe stress indicators."
        }


def get_health_score(
    image_path: Optional[str], 
    ndvi_latest: float, 
    sequence: Any
) -> Dict[str, Any]:
    """
    Calculate comprehensive health score from multiple data sources.
    
    Args:
        image_path: Path to crop image (optional, can be None)
        ndvi_latest: Latest NDVI value
        sequence: Time series data for LSTM (list or dict format)
    
    Returns:
        Dictionary with:
        - score: float (0-1)
        - rating: str (Excellent/Good/Fair/Poor/Critical)
        - breakdown: dict with individual scores
        - recommendation: str
    """
    from ml_engine.cnn import predict_health
    from ml_engine.lstm import predict_risk_from_values
    
    breakdown = {}
    
    # CNN Health Score (if image provided)
    if image_path:
        cnn_result = predict_health(image_path)
        if "error" in cnn_result and not cnn_result.get("fallback"):
            # Hard error - but continue with other metrics
            logger.warning(f"CNN prediction error: {cnn_result['error']}")
            p_cnn_healthy = 0.5  # Neutral value
            breakdown["cnn"] = {"value": 0.5, "status": "unavailable", "error": cnn_result["error"]}
        else:
            p_cnn_healthy = cnn_result.get('probability', 0.5)
            breakdown["cnn"] = {
                "value": p_cnn_healthy,
                "class": cnn_result.get("class", "Unknown"),
                "confidence": cnn_result.get("confidence", "Unknown"),
                "status": "available"
            }
    else:
        # No image provided - use NDVI as proxy
        p_cnn_healthy = max(0.0, min(1.0, ndvi_latest))
        breakdown["cnn"] = {"value": p_cnn_healthy, "status": "estimated_from_ndvi"}
    
    # NDVI Score
    ndvi_clamped = max(0.0, min(1.0, ndvi_latest)) if ndvi_latest else 0.5
    breakdown["ndvi"] = {
        "value": ndvi_clamped,
        "raw": ndvi_latest,
        "status": "available" if ndvi_latest is not None else "unavailable"
    }
    
    # LSTM Risk Score
    if sequence:
        risk_result = predict_risk_from_values(sequence)
        if "error" in risk_result and not risk_result.get("fallback"):
            logger.warning(f"LSTM prediction error: {risk_result['error']}")
            risk_prob = 0.5
            breakdown["risk"] = {"value": 0.5, "status": "unavailable", "error": risk_result["error"]}
        else:
            risk_prob = risk_result.get('risk_probability', 0.5)
            breakdown["risk"] = {
                "value": risk_prob,
                "level": risk_result.get("risk_level", "Unknown"),
                "recommendation": risk_result.get("recommendation"),
                "status": "available"
            }
    else:
        risk_prob = 0.5
        breakdown["risk"] = {"value": 0.5, "status": "no_sequence_data"}
    
    # Calculate composite score
    final_score = compute_health_score(p_cnn_healthy, ndvi_clamped, risk_prob)
    rating_info = get_health_rating(final_score)
    
    return {
        "score": round(final_score, 4),
        "score_percent": round(final_score * 100, 1),
        "rating": rating_info["rating"],
        "color": rating_info["color"],
        "recommendation": rating_info["recommendation"],
        "breakdown": breakdown,
        "weights": {"cnn": 0.4, "ndvi": 0.35, "risk": 0.25}
    }