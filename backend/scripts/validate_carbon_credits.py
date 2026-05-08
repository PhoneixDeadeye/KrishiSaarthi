"""
AWD & Carbon Credit Validation
================================
Tests AWD detection and carbon credit calculation with real/sample NDWI data.
Generates Section D outputs: water saved, carbon credits, INR value.

Usage:
    python scripts/validate_carbon_credits.py
"""

import os
import sys
import json
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

from ml_engine.awd import detect_awd_from_ndwi, calculate_awd_score
from ml_engine.cc import calculate_carbon_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = os.path.join(BACKEND_DIR, "evaluation_results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def test_awd_detection():
    """Test AWD detection with various NDWI patterns."""
    patterns = {
        "Strong AWD (3 cycles)": [
            {"date": "2026-01-01", "NDWI": 0.35},
            {"date": "2026-01-08", "NDWI": 0.38},
            {"date": "2026-01-15", "NDWI": 0.15},  # Dry
            {"date": "2026-01-22", "NDWI": 0.12},
            {"date": "2026-01-29", "NDWI": 0.36},  # Wet
            {"date": "2026-02-05", "NDWI": 0.40},
            {"date": "2026-02-12", "NDWI": 0.14},  # Dry
            {"date": "2026-02-19", "NDWI": 0.10},
            {"date": "2026-02-26", "NDWI": 0.33},  # Wet
            {"date": "2026-03-05", "NDWI": 0.37},
            {"date": "2026-03-12", "NDWI": 0.16},  # Dry
            {"date": "2026-03-19", "NDWI": 0.34},  # Wet
        ],
        "Weak AWD (1 cycle)": [
            {"date": "2026-01-01", "NDWI": 0.32},
            {"date": "2026-01-08", "NDWI": 0.34},
            {"date": "2026-01-15", "NDWI": 0.18},  # Dry
            {"date": "2026-01-22", "NDWI": 0.31},  # Wet
            {"date": "2026-01-29", "NDWI": 0.30},
            {"date": "2026-02-05", "NDWI": 0.28},
        ],
        "No AWD (always wet)": [
            {"date": "2026-01-01", "NDWI": 0.38},
            {"date": "2026-01-08", "NDWI": 0.42},
            {"date": "2026-01-15", "NDWI": 0.35},
            {"date": "2026-01-22", "NDWI": 0.40},
            {"date": "2026-01-29", "NDWI": 0.37},
            {"date": "2026-02-05", "NDWI": 0.44},
        ],
        "No AWD (always dry)": [
            {"date": "2026-01-01", "NDWI": 0.10},
            {"date": "2026-01-08", "NDWI": 0.08},
            {"date": "2026-01-15", "NDWI": 0.12},
            {"date": "2026-01-22", "NDWI": 0.09},
            {"date": "2026-01-29", "NDWI": 0.11},
            {"date": "2026-02-05", "NDWI": 0.07},
        ],
    }

    results = {}
    for name, series in patterns.items():
        result = detect_awd_from_ndwi(series)
        score = calculate_awd_score(result)
        results[name] = {
            "awd_detected": result["awd_detected"],
            "cycles": result["cycles_count"],
            "dry_ratio": result.get("dry_ratio", 0),
            "water_savings_pct": result.get("estimated_water_savings_percent", 0),
            "methane_reduction_pct": result.get("estimated_methane_reduction_percent", 0),
            "awd_score": score,
            "recommendation": result["recommendation"][:100],
        }

    return results


def test_carbon_credits():
    """Test carbon credit calculation for representative fields."""
    fields = [
        {
            "name": "Small rice paddy (Telangana)",
            "area_hectare": 1.5,
            "ndwi_series": [0.35, 0.38, 0.15, 0.12, 0.36, 0.40, 0.14, 0.10, 0.33, 0.37, 0.16, 0.34],
            "ndwi_dates": [f"2026-{m:02d}-{d:02d}" for m, d in
                          [(1,1),(1,8),(1,15),(1,22),(1,29),(2,5),(2,12),(2,19),(2,26),(3,5),(3,12),(3,19)]],
            "crop_days": 120,
        },
        {
            "name": "Large rice field (Punjab)",
            "area_hectare": 5.0,
            "ndwi_series": [0.40, 0.42, 0.18, 0.15, 0.38, 0.41, 0.16, 0.13, 0.35, 0.39],
            "ndwi_dates": [f"2026-{m:02d}-{d:02d}" for m, d in
                          [(6,1),(6,15),(7,1),(7,15),(8,1),(8,15),(9,1),(9,15),(10,1),(10,15)]],
            "crop_days": 140,
        },
        {
            "name": "Non-AWD field (continuously flooded)",
            "area_hectare": 2.0,
            "ndwi_series": [0.38, 0.42, 0.35, 0.40, 0.37, 0.44, 0.39, 0.41],
            "ndwi_dates": [f"2026-{m:02d}-01" for m in range(1, 9)],
            "crop_days": 100,
        },
    ]

    results = []
    for field in fields:
        cc_result = calculate_carbon_metrics(
            area_hectare=field["area_hectare"],
            ndwi_series=field["ndwi_series"],
            ndwi_dates=field["ndwi_dates"],
            crop_days=field["crop_days"],
        )

        results.append({
            "field_name": field["name"],
            "area_hectare": field["area_hectare"],
            "crop_days": field["crop_days"],
            "awd_detected": cc_result["awd_detected"],
            "awd_effective_fraction": cc_result["awd_effective_fraction"],
            "water_saved_mm": cc_result["water_saved_mm"],
            "water_saved_cubic_m": cc_result["water_saved_cubic_m"],
            "water_saved_litres_per_ha": round(cc_result["water_saved_mm"] * 10000 / field["area_hectare"], 0) if field["area_hectare"] > 0 else 0,
            "methane_reduction_kg": cc_result["methane_reduction_kg"],
            "co2e_reduction_ton": cc_result["co2e_reduction_ton"],
            "carbon_credits": cc_result["carbon_credits"],
            "estimated_value_inr": cc_result["estimated_value_inr"],
        })

    return results


def main():
    logger.info("=" * 60)
    logger.info("AWD & Carbon Credit Validation")
    logger.info("=" * 60)

    awd_results = test_awd_detection()
    cc_results = test_carbon_credits()

    metrics = {
        "formulas": {
            "water_saved_cubic_m": "water_saved_mm * area_hectare * 10",
            "methane_baseline_kg": "ch4_baseline_kg_per_ha_per_day (1.3) * area_ha * crop_days",
            "methane_reduction_kg": "methane_baseline * awd_eff * awd_reduction_factor (0.35)",
            "co2e_reduction_ton": "methane_reduction_kg * ch4_to_co2e (27.2) / 1000",
            "carbon_credits": "co2e_reduction_ton (1 credit = 1 tonne CO2e)",
            "value_inr": "carbon_credits * 1245 INR (= 15 USD * 83 INR/USD)",
            "simplified": "carbon_credits * 15 * 83 = INR value",
        },
        "awd_detection_tests": awd_results,
        "carbon_credit_outputs": cc_results,
    }

    output_path = os.path.join(RESULTS_DIR, "carbon_credit_results.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Results saved to %s", output_path)

    # Print summary
    print("\n" + "=" * 70)
    print("AWD DETECTION RESULTS")
    print("=" * 70)
    print(f"{'Pattern':<30} {'AWD?':>5} {'Cycles':>7} {'DryRatio':>9} {'WaterSav%':>10}")
    print("-" * 70)
    for name, data in awd_results.items():
        awd = "Yes" if data["awd_detected"] else "No"
        print(f"{name:<30} {awd:>5} {data['cycles']:>7} {data['dry_ratio']:>9.3f} {data['water_savings_pct']:>9.1f}%")

    print("\n" + "=" * 90)
    print("CARBON CREDIT OUTPUTS (Section D)")
    print("=" * 90)
    print(f"{'Field':<35} {'Area':>5} {'WaterSaved':>12} {'CO2e(t)':>8} {'Credits':>8} {'INR':>10}")
    print("-" * 90)
    for r in cc_results:
        print(f"{r['field_name']:<35} {r['area_hectare']:>4.1f}ha {r['water_saved_cubic_m']:>10.0f}m3 "
              f"{r['co2e_reduction_ton']:>8.3f} {r['carbon_credits']:>8.3f} Rs{r['estimated_value_inr']:>8.0f}")
    print("\nFormula: carbon_credits x 15 USD x 83 INR/USD = INR value")


if __name__ == "__main__":
    main()
