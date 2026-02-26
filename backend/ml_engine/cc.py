import numpy as np
import logging
from typing import List, Dict, Any, Optional

from ml_engine.awd import detect_awd_from_ndwi

logger = logging.getLogger(__name__)


def calculate_carbon_metrics(
    area_hectare: float,
    ndwi_series: List[float],
    ndwi_dates: List[str] = None,
    crop_days: int = 100,
    baseline_water_mm: float = 1200.0,
    ch4_baseline_kg_per_ha_per_day: float = 1.3,
    awd_reduction_factor: float = 0.35,
    ch4_to_co2e: float = 27.2,
    credit_price_inr: float = 900.0,
    ndwi_params: dict = None
) -> Dict[str, Any]:
    """
    Compute water saved, methane reduction and carbon credits using NDWI-based AWD detection.
    """
    if ndwi_params is None:
        ndwi_params = {}

    if not ndwi_series:
        ndwi_series = []

    # Convert raw float list + dates list into [{date, NDWI}] format for awd.detect_awd_from_ndwi
    ndwi_dicts = []
    for i, val in enumerate(ndwi_series):
        entry = {"NDWI": float(val)}
        if ndwi_dates and i < len(ndwi_dates):
            entry["date"] = ndwi_dates[i]
        else:
            entry["date"] = f"day_{i}"
        ndwi_dicts.append(entry)

    # Filter ndwi_params to only pass supported kwargs (wet_threshold, dry_threshold, min_cycles)
    supported_params = {k: v for k, v in ndwi_params.items()
                        if k in ('wet_threshold', 'dry_threshold', 'min_cycles')}
    awd_result = detect_awd_from_ndwi(ndwi_dicts, **supported_params)

    eff = 0.0
    if awd_result.get("awd_detected"):
        cycles = awd_result.get("cycles_count", 0)
        dry_ratio = awd_result.get("dry_ratio", awd_result.get("dry_fraction", 0))
        if cycles >= 2 and dry_ratio >= 0.2:
            eff = 1.0
        else:
            eff = 0.5

    water_saving_fraction = 0.35
    actual_water_mm = baseline_water_mm * (1 - eff * water_saving_fraction)
    water_saved_mm = baseline_water_mm - actual_water_mm
    water_saved_cubic_m = water_saved_mm * area_hectare * 10.0

    methane_baseline_total_kg = ch4_baseline_kg_per_ha_per_day * area_hectare * crop_days
    methane_reduction_kg = methane_baseline_total_kg * (eff * awd_reduction_factor)

    co2e_reduction_kg = methane_reduction_kg * ch4_to_co2e
    co2e_reduction_ton = co2e_reduction_kg / 1000.0

    carbon_credits = co2e_reduction_ton
    estimated_value_inr = carbon_credits * credit_price_inr

    return {
        "awd_result": awd_result,
        "area_hectare": round(area_hectare, 4),
        "awd_effective_fraction": round(eff, 3),
        "actual_water_mm": round(actual_water_mm, 2),
        "water_saved_mm": round(water_saved_mm, 2),
        "water_saved_cubic_m": round(water_saved_cubic_m, 2),
        "methane_reduction_kg": round(methane_reduction_kg, 2),
        "co2e_reduction_ton": round(co2e_reduction_ton, 3),
        "carbon_credits": round(carbon_credits, 3),
        "estimated_value_inr": round(estimated_value_inr, 2),
        "awd_detected": awd_result["awd_detected"]
    }