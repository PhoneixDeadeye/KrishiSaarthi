import numpy as np
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def detect_awd_from_ndwi(
    ndwi_series: List[float],
    dates: List[str] = None,
    wet_threshold: float = 0.30,
    dry_threshold: float = 0.20,
    min_dry_days_for_awd: int = 3,
    min_cycles: int = 1,
    min_dry_fraction: float = 0.05
) -> Dict[str, Any]:
    """
    Detect AWD from an NDWI time series using dry-day counts and wet-dry cycles.
    """
    ndwi = np.array(ndwi_series, dtype=float)
    n = len(ndwi)
    if n == 0:
        return {
            "awd_detected": False, 
            "cycles_count": 0, 
            "dry_spells": [], 
            "total_dry_days_count": 0, 
            "dry_fraction": 0.0, 
            "notes": "empty series"
        }

    # classify each acquisition: 'wet', 'dry', or 'neutral'
    state_arr = np.array(["neutral"] * n)
    state_arr[ndwi >= wet_threshold] = "wet"
    state_arr[ndwi <= dry_threshold] = "dry"

    # find dry spells (consecutive dry indices)
    dry_spells = []
    i = 0
    while i < n:
        if state_arr[i] == "dry":
            start = i
            j = i + 1
            while j < n and state_arr[j] == "dry":
                j += 1
            length = j - start
            dry_spells.append({
                "start_idx": start, 
                "end_idx": j - 1, 
                "length": length,
                "start_date": (dates[start] if dates else None),
                "end_date": (dates[j-1] if dates and j-1 < len(dates) else None)
            })
            i = j
        else:
            i += 1

    total_dry_days_count = sum(sp["length"] for sp in dry_spells)
    dry_fraction = total_dry_days_count / n

    # count wet->dry->wet cycles
    meaningful = []
    for s in state_arr:
        if s == "neutral":
            continue
        if not meaningful or meaningful[-1] != s:
            meaningful.append(s)

    cycles = 0
    for idx in range(len(meaningful) - 2):
        if meaningful[idx] == "wet" and meaningful[idx + 1] == "dry" and meaningful[idx + 2] == "wet":
            cycles += 1

    cycles_alt = 0
    for sp in dry_spells:
        s, e = sp["start_idx"], sp["end_idx"]
        left_wet = (s - 1 >= 0 and state_arr[s - 1] == "wet")
        right_wet = (e + 1 < n and state_arr[e + 1] == "wet")
        if left_wet and right_wet:
            cycles_alt += 1

    cycles = max(cycles, cycles_alt)
    long_enough_dry = any(sp["length"] >= min_dry_days_for_awd for sp in dry_spells)
    awd_detected = (cycles >= min_cycles) and long_enough_dry and (dry_fraction >= min_dry_fraction)

    notes = []
    if not long_enough_dry:
        notes.append(f"No dry spell >= {min_dry_days_for_awd} acquisitions.")
    if cycles < min_cycles:
        notes.append(f"Only {cycles} wet-dry-wet cycles found; need >= {min_cycles}.")
    if dry_fraction < min_dry_fraction:
        notes.append(f"Dry fraction too low ({dry_fraction:.2f}); threshold {min_dry_fraction}.")
    
    final_notes = "; ".join(notes) if notes else "AWD pattern passes all thresholds."

    return {
        "awd_detected": bool(awd_detected),
        "cycles_count": int(cycles),
        "dry_spells": dry_spells,
        "total_dry_days_count": int(total_dry_days_count),
        "dry_fraction": float(round(dry_fraction, 3)),
        "notes": final_notes
    }

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

    # Basic input cleaning
    if not ndwi_series:
        ndwi_series = []

    awd_result = detect_awd_from_ndwi(ndwi_series, dates=ndwi_dates, **ndwi_params)

    eff = 0.0
    if awd_result["awd_detected"]:
        if awd_result["cycles_count"] >= 2 and awd_result["dry_fraction"] >= 0.2:
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