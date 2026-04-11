"""
Health Score Validation
========================
Tests the health score fusion module with various input scenarios.
Generates the comparison table: CNN+NDVI blend vs NDVI-only vs fallback.

Usage:
    python scripts/validate_health_score.py
"""

import os
import sys
import json
import time
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

from ml_engine.health_score import compute_health_score, get_health_rating, get_health_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = os.path.join(BACKEND_DIR, "evaluation_results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def test_score_computation():
    """Test raw score computation with various inputs."""
    test_cases = [
        {"p_cnn": 0.92, "ndvi": 0.75, "risk": 0.15, "desc": "Healthy crop, low risk"},
        {"p_cnn": 0.85, "ndvi": 0.68, "risk": 0.35, "desc": "Good crop, medium risk"},
        {"p_cnn": 0.45, "ndvi": 0.42, "risk": 0.72, "desc": "Stressed crop, high risk"},
        {"p_cnn": 0.20, "ndvi": 0.25, "risk": 0.88, "desc": "Severely stressed, very high risk"},
        {"p_cnn": 0.50, "ndvi": 0.60, "risk": 0.50, "desc": "Neutral/uncertain all inputs"},
        {"p_cnn": 0.95, "ndvi": 0.85, "risk": 0.05, "desc": "Optimal conditions"},
        {"p_cnn": 0.10, "ndvi": 0.15, "risk": 0.95, "desc": "Critical conditions"},
    ]

    results = []
    for tc in test_cases:
        score = compute_health_score(tc["p_cnn"], tc["ndvi"], tc["risk"])
        rating = get_health_rating(score)
        results.append({
            "description": tc["desc"],
            "inputs": {"p_cnn_healthy": tc["p_cnn"], "ndvi_raw": tc["ndvi"], "risk_prob": tc["risk"]},
            "health_score": round(score, 4),
            "score_percent": round(score * 100, 1),
            "rating": rating["rating"],
            "color": rating["color"],
        })

    return results


def test_source_comparison():
    """
    Compare health scores with different data availability scenarios.
    This generates the table from Section C of the report.
    """
    scenarios = [
        {
            "input_type": "Crop image + NDVI + LSTM",
            "cnn_available": True,
            "image_path": None,  # No actual image, will use p_cnn value
            "p_cnn": 0.88,
            "ndvi": 0.72,
            "risk": 0.22,
            "source": "CNN + NDVI + LSTM blend",
        },
        {
            "input_type": "NDVI + LSTM only",
            "cnn_available": False,
            "p_cnn": None,  # CNN unavailable, NDVI used as proxy
            "ndvi": 0.65,
            "risk": 0.40,
            "source": "NDVI estimate (no image)",
        },
        {
            "input_type": "NDVI only (no LSTM, no image)",
            "cnn_available": False,
            "p_cnn": None,
            "ndvi": 0.58,
            "risk": 0.50,  # default when no LSTM
            "source": "NDVI-only fallback",
        },
        {
            "input_type": "Image + NDVI (no LSTM)",
            "cnn_available": True,
            "p_cnn": 0.82,
            "ndvi": 0.70,
            "risk": 0.50,  # default when no LSTM
            "source": "CNN + NDVI (no risk data)",
        },
        {
            "input_type": "All data - stressed field",
            "cnn_available": True,
            "p_cnn": 0.35,
            "ndvi": 0.30,
            "risk": 0.78,
            "source": "CNN + NDVI + LSTM blend",
        },
    ]

    results = []
    for sc in scenarios:
        if sc["cnn_available"] and sc["p_cnn"] is not None:
            p_cnn = sc["p_cnn"]
        else:
            # When CNN unavailable, NDVI used as proxy for CNN score
            p_cnn = max(0.0, min(1.0, sc["ndvi"]))

        score = compute_health_score(p_cnn, sc["ndvi"], sc["risk"])
        rating = get_health_rating(score)

        results.append({
            "input_type": sc["input_type"],
            "cnn_available": sc["cnn_available"],
            "health_score": round(score, 2),
            "score_percent": round(score * 100, 1),
            "rating": rating["rating"],
            "source": sc["source"],
            "weights_used": {"cnn": 0.4, "ndvi": 0.35, "risk_inv": 0.25},
        })

    return results


def test_weight_sensitivity():
    """Test how health score changes with different weight configurations."""
    base_inputs = {"p_cnn": 0.75, "ndvi": 0.60, "risk": 0.40}

    weight_configs = [
        {"w1": 0.40, "w2": 0.35, "w3": 0.25, "name": "Default (CNN-heavy)"},
        {"w1": 0.33, "w2": 0.34, "w3": 0.33, "name": "Equal weights"},
        {"w1": 0.20, "w2": 0.50, "w3": 0.30, "name": "NDVI-heavy"},
        {"w1": 0.50, "w2": 0.25, "w3": 0.25, "name": "CNN-dominant"},
        {"w1": 0.25, "w2": 0.25, "w3": 0.50, "name": "Risk-heavy"},
    ]

    results = []
    for wc in weight_configs:
        score = compute_health_score(
            base_inputs["p_cnn"], base_inputs["ndvi"], base_inputs["risk"],
            w1=wc["w1"], w2=wc["w2"], w3=wc["w3"]
        )
        results.append({
            "config_name": wc["name"],
            "weights": {"cnn": wc["w1"], "ndvi": wc["w2"], "risk_inv": wc["w3"]},
            "health_score": round(score, 4),
            "score_percent": round(score * 100, 1),
        })

    return results


def main():
    logger.info("=" * 60)
    logger.info("Health Score Validation")
    logger.info("=" * 60)

    # Run all tests
    score_tests = test_score_computation()
    source_comparison = test_source_comparison()
    weight_sensitivity = test_weight_sensitivity()

    metrics = {
        "formula": "health_score = w1 * p_cnn_healthy + w2 * ndvi_norm + w3 * (1 - risk_prob)",
        "default_weights": {"w1_cnn": 0.4, "w2_ndvi": 0.35, "w3_risk_inv": 0.25},
        "score_tests": score_tests,
        "source_comparison": source_comparison,
        "weight_sensitivity": weight_sensitivity,
    }

    output_path = os.path.join(RESULTS_DIR, "health_score_validation.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Results saved to %s", output_path)

    # Print comparison table
    print("\n" + "=" * 90)
    print("HEALTH SCORE SOURCE COMPARISON (Section C)")
    print("=" * 90)
    print(f"{'Input Type':<35} {'CNN?':>5} {'Score':>7} {'Rating':<12} {'Source'}")
    print("-" * 90)
    for r in source_comparison:
        cnn = "Yes" if r["cnn_available"] else "No"
        print(f"{r['input_type']:<35} {cnn:>5} {r['health_score']:>7.2f} {r['rating']:<12} {r['source']}")

    print("\nScore Tests:")
    print(f"{'Description':<40} {'Score':>7} {'Rating':<12}")
    print("-" * 62)
    for r in score_tests:
        print(f"{r['description']:<40} {r['health_score']:>7.4f} {r['rating']:<12}")


if __name__ == "__main__":
    main()
