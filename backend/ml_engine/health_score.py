"""
Health Score Module
====================
Fuses CNN image analysis, NDVI data, LSTM risk prediction,
weather conditions, and agronomic practices into a comprehensive
crop health score.
"""

import numpy as np
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Explicit Fusion Weights (must sum to 1.00) ──────────────────────
W_CNN      = 0.30  # w1 — CNN image classification confidence
W_NDVI     = 0.25  # w2 — Vegetation index health proxy
W_LSTM     = 0.20  # w3 — Time-series risk (inverted)
W_WEATHER  = 0.15  # w4 — Weather favorability
W_PRACTICE = 0.10  # w5 — Agronomic practice quality
# Sum = 1.00


def compute_health_score(
    p_cnn_healthy: float,
    ndvi_raw: float,
    risk_prob: float,
    weather_score: float,
    practice_score: float,
    w1: float = W_CNN,
    w2: float = W_NDVI,
    w3: float = W_LSTM,
    w4: float = W_WEATHER,
    w5: float = W_PRACTICE,
) -> float:
    """
    Compute weighted health score from five indicators.

    Args:
        p_cnn_healthy:  CNN model probability (0-1, 1=healthy)
        ndvi_raw:       Raw NDVI value (clamped to 0-1)
        risk_prob:      LSTM risk probability (0-1, 1=high risk)
        weather_score:  Weather favorability (0-1, 1=ideal conditions)
        practice_score: Agronomic practice quality (0-1, 1=best practice)
        w1-w5: Weights for each component

    Returns:
        Composite health score (0-1, 1=excellent health)
    """
    ndvi_norm = float(np.clip(ndvi_raw, 0.0, 1.0))
    risk_health = 1.0 - float(risk_prob)
    weather_clamped = float(np.clip(weather_score, 0.0, 1.0))
    practice_clamped = float(np.clip(practice_score, 0.0, 1.0))

    health = (
        w1 * p_cnn_healthy
        + w2 * ndvi_norm
        + w3 * risk_health
        + w4 * weather_clamped
        + w5 * practice_clamped
    )

    return float(np.clip(health, 0, 1))


def get_health_rating(score: float) -> Dict[str, Any]:
    """
    Convert numeric score to rating and recommendations.
    """
    if score >= 0.8:
        return {
            "rating": "Excellent",
            "color": "green",
            "recommendation": "Crops are thriving. Continue current practices.",
        }
    elif score >= 0.6:
        return {
            "rating": "Good",
            "color": "lightgreen",
            "recommendation": "Crops are healthy. Monitor for any changes.",
        }
    elif score >= 0.4:
        return {
            "rating": "Fair",
            "color": "yellow",
            "recommendation": "Some stress detected. Consider irrigation or nutrient adjustments.",
        }
    elif score >= 0.2:
        return {
            "rating": "Poor",
            "color": "orange",
            "recommendation": "Significant stress. Inspect for pests/disease and take corrective action.",
        }
    else:
        return {
            "rating": "Critical",
            "color": "red",
            "recommendation": "Urgent attention needed. Crops show severe stress indicators.",
        }


# ── Real-data derivation helpers ────────────────────────────────────


def _derive_weather_score(ee_data: Dict[str, Any]) -> float:
    """
    Derive weather favorability from real Earth Engine observations.

    Scores temperature, rainfall, and soil-moisture against optimal
    crop-growth ranges and returns a 0-1 composite.
    """
    components = []

    # Temperature (Kelvin -> Celsius)
    temp_k = ee_data.get("temperature_K")
    if temp_k and temp_k > 200:
        temp_c = temp_k - 273.15
        if 20.0 <= temp_c <= 30.0:
            components.append(1.0)
        elif 15.0 <= temp_c <= 35.0:
            deviation = max(0.0, 20.0 - temp_c) + max(0.0, temp_c - 30.0)
            components.append(max(0.3, 1.0 - deviation / 10.0))
        else:
            components.append(0.2)

    # Rainfall (mm, daily proxy)
    rainfall = ee_data.get("rainfall_mm")
    if rainfall is not None:
        rain = float(rainfall)
        if 2.0 <= rain <= 12.0:
            components.append(1.0)
        elif 0.5 <= rain <= 25.0:
            deviation = max(0.0, 2.0 - rain) + max(0.0, rain - 12.0)
            components.append(max(0.3, 1.0 - deviation / 15.0))
        else:
            components.append(0.2)

    # Soil moisture (volumetric fraction 0-1)
    moisture = ee_data.get("soil_moisture")
    if moisture is not None:
        sm = float(moisture)
        if 0.2 <= sm <= 0.6:
            components.append(1.0)
        elif 0.1 <= sm <= 0.8:
            deviation = max(0.0, 0.2 - sm) + max(0.0, sm - 0.6)
            components.append(max(0.3, 1.0 - deviation / 0.3))
        else:
            components.append(0.2)

    if not components:
        logger.debug("No weather observations in EE payload")
        return 0.5  # neutral fallback — absent data, not fabricated

    return float(np.mean(components))


def _derive_practice_score(ee_data: Dict[str, Any]) -> float:
    """
    Derive agronomic-practice quality from NDWI-based AWD detection.

    AWD (Alternate Wetting & Drying) is a strong proxy for
    sustainable rice-paddy management.
    """
    from ml_engine.awd import detect_awd_from_ndwi

    ndwi_series = ee_data.get("ndwi_time_series", [])
    if not ndwi_series:
        logger.debug("No NDWI time-series in EE payload for practice scoring")
        return 0.5  # neutral fallback — absent data

    try:
        awd = detect_awd_from_ndwi(ndwi_series)
        if awd.get("awd_detected"):
            cycles = awd.get("cycles_count", 0)
            dry_ratio = awd.get("dry_ratio", awd.get("dry_fraction", 0))
            if cycles >= 3 and dry_ratio >= 0.25:
                return 0.95
            if cycles >= 2 and dry_ratio >= 0.20:
                return 0.80
            return 0.65
        return 0.40  # continuous flooding — baseline practice
    except Exception as exc:
        logger.warning("Practice score derivation failed: %s", exc)
        return 0.5


# ── Public API ──────────────────────────────────────────────────────


def get_health_score(
    image_path: Optional[str], ndvi_latest: float, sequence: Any
) -> Dict[str, Any]:
    """
    Calculate comprehensive health score from multiple data sources.

    Args:
        image_path: Path to crop image (optional)
        ndvi_latest: Latest NDVI value
        sequence: EE data dict (time series + weather observations)

    Returns:
        Dictionary with score, rating, breakdown, recommendation.
    """
    from ml_engine.cnn import predict_health
    from ml_engine.lstm import predict_risk_from_values

    breakdown = {}
    ee_data = sequence if isinstance(sequence, dict) else {}

    # ── w1: CNN component ──
    if image_path:
        cnn_result = predict_health(image_path)
        if "error" in cnn_result and not cnn_result.get("fallback"):
            logger.warning("CNN prediction error: %s", cnn_result["error"])
            p_cnn_healthy = 0.5
            breakdown["cnn"] = {
                "value": 0.5,
                "status": "unavailable",
                "error": cnn_result["error"],
            }
        else:
            p_cnn_healthy = cnn_result.get("probability", 0.5)
            breakdown["cnn"] = {
                "value": p_cnn_healthy,
                "class": cnn_result.get("class", "Unknown"),
                "confidence": cnn_result.get("confidence", "Unknown"),
                "status": "unavailable" if cnn_result.get("fallback") else "available",
            }
    else:
        if ndvi_latest is not None:
            p_cnn_healthy = max(0.0, min(1.0, ndvi_latest))
            breakdown["cnn"] = {"value": p_cnn_healthy, "status": "estimated_from_ndvi"}
        else:
            p_cnn_healthy = 0.5
            breakdown["cnn"] = {"value": 0.5, "status": "unavailable"}

    # ── w2: NDVI component ──
    ndvi_clamped = max(0.0, min(1.0, ndvi_latest)) if ndvi_latest else 0.5
    breakdown["ndvi"] = {
        "value": ndvi_clamped,
        "raw": ndvi_latest,
        "status": "available" if ndvi_latest is not None else "unavailable",
    }

    # ── w3: LSTM risk component ──
    if sequence:
        risk_result = predict_risk_from_values(sequence)
        if "error" in risk_result and not risk_result.get("fallback"):
            logger.warning("LSTM prediction error: %s", risk_result["error"])
            risk_prob = 0.5
            breakdown["risk"] = {
                "value": 0.5,
                "status": "unavailable",
                "error": risk_result["error"],
            }
        else:
            risk_prob = risk_result.get("risk_probability", 0.5)
            breakdown["risk"] = {
                "value": risk_prob,
                "level": risk_result.get("risk_level", "Unknown"),
                "recommendation": risk_result.get("recommendation"),
                "status": "unavailable" if risk_result.get("fallback") else "available",
            }
    else:
        risk_prob = 0.5
        breakdown["risk"] = {"value": 0.5, "status": "no_sequence_data"}

    # ── w4: Weather component (derived from live EE observations) ──
    weather = _derive_weather_score(ee_data)
    breakdown["weather"] = {
        "value": round(weather, 4),
        "status": "available" if ee_data.get("temperature_K") or ee_data.get("rainfall_mm") else "no_data",
    }

    # ── w5: Practice component (derived from live NDWI/AWD) ──
    practice = _derive_practice_score(ee_data)
    breakdown["practice"] = {
        "value": round(practice, 4),
        "status": "available" if ee_data.get("ndwi_time_series") else "no_data",
    }

    # ── Fuse all five ──
    final_score = compute_health_score(
        p_cnn_healthy, ndvi_clamped, risk_prob, weather, practice
    )
    rating_info = get_health_rating(final_score)

    return {
        "score": round(final_score, 4),
        "score_percent": round(final_score * 100, 1),
        "rating": rating_info["rating"],
        "color": rating_info["color"],
        "recommendation": rating_info["recommendation"],
        "breakdown": breakdown,
        "weights": {
            "cnn": W_CNN,
            "ndvi": W_NDVI,
            "risk": W_LSTM,
            "weather": W_WEATHER,
            "practice": W_PRACTICE,
        },
    }
