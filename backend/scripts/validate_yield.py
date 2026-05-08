"""
Yield Prediction Validation
=============================
Tests the rule-based yield prediction module across all crop models.
Demonstrates NDVI source effect (real vs estimated).

Usage:
    python scripts/validate_yield.py
"""

import os
import sys
import json
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = os.path.join(BACKEND_DIR, "evaluation_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Import from yield_prediction view
CROP_YIELD_MODELS = {
    "Rice": {"base_yield": 4500, "ndvi_factor": 1.2, "water_sensitive": True},
    "Wheat": {"base_yield": 3500, "ndvi_factor": 1.1, "water_sensitive": False},
    "Cotton": {"base_yield": 1800, "ndvi_factor": 1.0, "water_sensitive": False},
    "Sugarcane": {"base_yield": 70000, "ndvi_factor": 0.9, "water_sensitive": True},
    "Maize": {"base_yield": 5000, "ndvi_factor": 1.15, "water_sensitive": True},
    "Soybean": {"base_yield": 2000, "ndvi_factor": 1.1, "water_sensitive": False},
    "Groundnut": {"base_yield": 1500, "ndvi_factor": 1.0, "water_sensitive": False},
    "Potato": {"base_yield": 25000, "ndvi_factor": 1.1, "water_sensitive": True},
    "Onion": {"base_yield": 20000, "ndvi_factor": 1.0, "water_sensitive": True},
    "Tomato": {"base_yield": 30000, "ndvi_factor": 1.15, "water_sensitive": True},
}

REGIONAL_AVERAGES = {
    "Rice": 3800, "Wheat": 3100, "Cotton": 1500, "Sugarcane": 65000,
    "Maize": 4200, "default": 2500,
}


def calculate_yield(ndvi_current, model, trend="stable"):
    """Replicate yield calculation from the view."""
    base_yield = model["base_yield"]
    ndvi_factor = model["ndvi_factor"]

    ndvi_multiplier = (ndvi_current / 0.7) ** ndvi_factor
    ndvi_multiplier = max(0.3, min(1.3, ndvi_multiplier))

    trend_factor = 1.0
    if trend == "increasing":
        trend_factor = 1.05
    elif trend == "decreasing":
        trend_factor = 0.95

    yield_per_hectare = base_yield * ndvi_multiplier * trend_factor
    confidence = min(85, 50 + int(ndvi_current * 40))

    return {
        "yield_per_hectare": round(yield_per_hectare),
        "confidence": confidence,
        "ndvi_multiplier": round(ndvi_multiplier, 3),
        "trend_factor": trend_factor,
    }


def test_all_crops():
    """Test yield prediction for all 10 crop models at various NDVI levels."""
    ndvi_levels = [0.3, 0.45, 0.55, 0.65, 0.70, 0.80]
    results = {}

    for crop, model in CROP_YIELD_MODELS.items():
        crop_results = []
        for ndvi in ndvi_levels:
            pred = calculate_yield(ndvi, model, "stable")
            regional = REGIONAL_AVERAGES.get(crop, REGIONAL_AVERAGES["default"])
            vs_regional = round((pred["yield_per_hectare"] / regional - 1) * 100)

            crop_results.append({
                "ndvi": ndvi,
                "predicted_yield_kg_ha": pred["yield_per_hectare"],
                "confidence": pred["confidence"],
                "regional_avg": regional,
                "vs_regional_pct": vs_regional,
            })
        results[crop] = {
            "base_yield": model["base_yield"],
            "ndvi_factor": model["ndvi_factor"],
            "water_sensitive": model["water_sensitive"],
            "predictions": crop_results,
        }

    return results


def test_ndvi_source_effect():
    """Compare predictions when NDVI source is real vs estimated."""
    crop = "Rice"
    model = CROP_YIELD_MODELS[crop]

    scenarios = [
        {
            "source": "earth_engine",
            "ndvi": 0.72,
            "trend": "increasing",
            "desc": "Real Sentinel-2 NDVI (3-month avg, 12 observations)",
        },
        {
            "source": "estimated",
            "ndvi": 0.63,
            "trend": "stable",
            "desc": "Deterministic fallback (hash-based, no satellite data)",
        },
        {
            "source": "earth_engine",
            "ndvi": 0.48,
            "trend": "decreasing",
            "desc": "Real NDVI showing crop stress (declining trend)",
        },
        {
            "source": "estimated",
            "ndvi": 0.58,
            "trend": "stable",
            "desc": "Estimated fallback for stressed field (always stable trend)",
        },
    ]

    results = []
    for sc in scenarios:
        pred = calculate_yield(sc["ndvi"], model, sc["trend"])
        results.append({
            "ndvi_source": sc["source"],
            "ndvi_value": sc["ndvi"],
            "trend": sc["trend"],
            "predicted_yield_kg_ha": pred["yield_per_hectare"],
            "confidence": pred["confidence"],
            "description": sc["desc"],
        })

    return results


def test_trend_impact():
    """Show how trend direction affects yield prediction."""
    crop = "Rice"
    model = CROP_YIELD_MODELS[crop]
    ndvi = 0.65

    results = []
    for trend in ["increasing", "stable", "decreasing"]:
        pred = calculate_yield(ndvi, model, trend)
        results.append({
            "trend": trend,
            "predicted_yield": pred["yield_per_hectare"],
            "trend_factor": pred["trend_factor"],
            "impact_pct": round((pred["trend_factor"] - 1) * 100),
        })

    return results


def main():
    logger.info("=" * 60)
    logger.info("Yield Prediction Validation")
    logger.info("=" * 60)

    all_crops = test_all_crops()
    source_effect = test_ndvi_source_effect()
    trend_impact = test_trend_impact()

    metrics = {
        "method": "rule_based_ndvi",
        "is_ml_prediction": False,
        "transparency_note": "Yield is estimated by applying ICAR base yields scaled by NDVI, NOT by a trained ML model.",
        "formula": "yield = base_yield * (ndvi / 0.7)^ndvi_factor * trend_factor",
        "all_crops": all_crops,
        "ndvi_source_effect": source_effect,
        "trend_impact": trend_impact,
    }

    output_path = os.path.join(RESULTS_DIR, "yield_validation.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Results saved to %s", output_path)

    # Print crop table
    print("\n" + "=" * 80)
    print("YIELD PREDICTION - ALL CROPS (at NDVI = 0.70)")
    print("=" * 80)
    print(f"{'Crop':<15} {'Base(kg/ha)':>12} {'Predicted':>12} {'Regional':>10} {'vs Reg':>8}")
    print("-" * 60)
    for crop, data in all_crops.items():
        # Find prediction at NDVI=0.70
        at_70 = [p for p in data["predictions"] if p["ndvi"] == 0.70][0]
        print(f"{crop:<15} {data['base_yield']:>12,} {at_70['predicted_yield_kg_ha']:>12,} "
              f"{at_70['regional_avg']:>10,} {at_70['vs_regional_pct']:>7}%")

    print("\n" + "=" * 80)
    print("NDVI SOURCE EFFECT (Section E)")
    print("=" * 80)
    print(f"{'Source':<16} {'NDVI':>6} {'Trend':<12} {'Yield(kg/ha)':>13} {'Conf':>5}")
    print("-" * 56)
    for r in source_effect:
        print(f"{r['ndvi_source']:<16} {r['ndvi_value']:>6.2f} {r['trend']:<12} "
              f"{r['predicted_yield_kg_ha']:>13,} {r['confidence']:>4}%")


if __name__ == "__main__":
    main()
