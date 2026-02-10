"""
AWD (Alternate Wetting and Drying) Detection Module
=====================================================
Analyzes NDWI time series to detect AWD irrigation patterns 
and estimate water savings potential.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def detect_awd_from_ndwi(
    ndwi_series: List[Dict], 
    wet_threshold: float = 0.3, 
    dry_threshold: float = 0.2, 
    min_cycles: int = 1
) -> Dict[str, Any]:
    """
    Detect AWD (Alternate Wetting and Drying) patterns from NDWI time series.
    
    AWD is a water-saving irrigation technique for rice paddies where fields are 
    alternately flooded and allowed to dry, reducing water usage and methane emissions.
    
    Args:
        ndwi_series: List of dicts with 'date' and 'NDWI' keys
                     e.g., [{"date": "2026-01-01", "NDWI": 0.35}, ...]
        wet_threshold: NDWI value above which field is considered wet/flooded
        dry_threshold: NDWI value below which field is considered dry
        min_cycles: Minimum wet-dry cycles required to confirm AWD practice
    
    Returns:
        Dictionary with detection results and recommendations
    """
    if not ndwi_series or len(ndwi_series) < 3:
        return {
            "awd_detected": False,
            "error": "Insufficient data for AWD detection (need at least 3 data points)",
            "recommendation": "Collect more satellite imagery data for accurate analysis"
        }
    
    # Track state transitions
    state = None  # 'wet' or 'dry'
    cycles = 0
    wet_periods = []
    dry_periods = []
    current_period_start = None
    
    dry_days_count = 0
    wet_days_count = 0
    
    for i, entry in enumerate(ndwi_series):
        val = entry.get("NDWI", 0)
        date = entry.get("date", f"day_{i}")
        
        if val is None:
            continue
        
        # Determine current state
        if val > wet_threshold:
            if state == "dry":
                # Transition from dry to wet = complete cycle
                cycles += 1
                if current_period_start:
                    dry_periods.append({
                        "start": current_period_start,
                        "end": date,
                        "type": "dry"
                    })
            if state != "wet":
                current_period_start = date
            state = "wet"
            wet_days_count += 1
            
        elif val < dry_threshold:
            if state == "wet" and current_period_start:
                wet_periods.append({
                    "start": current_period_start,
                    "end": date,
                    "type": "wet"
                })
            if state != "dry":
                current_period_start = date
            state = "dry"
            dry_days_count += 1
    
    # AWD detection
    awd_detected = cycles >= min_cycles
    
    # Calculate water savings estimate (based on typical AWD research)
    # AWD typically saves 15-30% of irrigation water
    total_observations = len(ndwi_series)
    dry_ratio = dry_days_count / total_observations if total_observations > 0 else 0
    
    # Estimate water savings (rough calculation)
    base_water_savings_percent = 0
    if awd_detected:
        # More dry periods = more water saved
        base_water_savings_percent = min(30, 10 + (dry_ratio * 25))
    
    # Calculate methane reduction potential
    # AWD can reduce methane emissions by 30-50%
    methane_reduction_percent = base_water_savings_percent * 1.5 if awd_detected else 0
    
    # NDWI statistics
    ndwi_values = [e.get("NDWI") for e in ndwi_series if e.get("NDWI") is not None]
    avg_ndwi = float(np.mean(ndwi_values)) if ndwi_values else 0
    ndwi_variance = float(np.var(ndwi_values)) if ndwi_values else 0
    
    # Generate recommendations
    if awd_detected:
        if cycles >= 3:
            recommendation = "Excellent AWD practice detected! Your irrigation management shows regular wet-dry cycles, maximizing water savings and reducing emissions."
        else:
            recommendation = "AWD pattern detected. Consider increasing the frequency of drying periods to optimize water usage."
    else:
        if avg_ndwi > wet_threshold:
            recommendation = "Field appears consistently wet. Consider implementing AWD by allowing periodic drying to save 15-30% water."
        elif avg_ndwi < dry_threshold:
            recommendation = "Field appears consistently dry. Ensure adequate irrigation for crop health."
        else:
            recommendation = "Irrigation pattern unclear. Monitor NDWI trends and consider structured wet-dry cycles."
    
    return {
        "awd_detected": awd_detected,
        "cycles_count": cycles,
        "dry_days_detected": dry_days_count,
        "wet_days_detected": wet_days_count,
        "total_observations": total_observations,
        "dry_ratio": round(dry_ratio, 3),
        "estimated_water_savings_percent": round(base_water_savings_percent, 1),
        "estimated_methane_reduction_percent": round(methane_reduction_percent, 1),
        "statistics": {
            "avg_ndwi": round(avg_ndwi, 4),
            "ndwi_variance": round(ndwi_variance, 4),
            "thresholds": {
                "wet": wet_threshold,
                "dry": dry_threshold
            }
        },
        "periods": {
            "wet": wet_periods[:5],  # Limit to last 5 for response size
            "dry": dry_periods[:5]
        },
        "recommendation": recommendation,
        "benefits": {
            "water_savings": f"~{round(base_water_savings_percent)}% reduction in irrigation water" if awd_detected else "Potential 15-30% savings with AWD",
            "emissions": f"~{round(methane_reduction_percent)}% reduction in methane emissions" if awd_detected else "Potential 30-50% reduction with AWD",
            "yield": "Studies show AWD maintains or improves yields when properly managed"
        }
    }


def calculate_awd_score(awd_result: Dict) -> float:
    """
    Convert AWD detection result to a sustainability score (0-1).
    
    Higher scores indicate better water management practices.
    """
    if not awd_result.get("awd_detected"):
        return 0.3  # Base score for non-AWD fields
    
    cycles = awd_result.get("cycles_count", 0)
    dry_ratio = awd_result.get("dry_ratio", 0)
    
    # Score components
    cycle_score = min(1.0, cycles / 5)  # Max out at 5 cycles
    ratio_score = min(1.0, dry_ratio * 2)  # Optimal around 50% dry
    
    # Penalize if too dry (crops need water!)
    if dry_ratio > 0.6:
        ratio_score *= 0.8
    
    return round(0.5 + (cycle_score * 0.3) + (ratio_score * 0.2), 3)


# Example usage
if __name__ == "__main__":
    # Sample NDWI series for testing
    sample_data = [
        {"date": "2026-01-01", "NDWI": 0.35},
        {"date": "2026-01-08", "NDWI": 0.32},
        {"date": "2026-01-15", "NDWI": 0.18},  # Dry
        {"date": "2026-01-22", "NDWI": 0.15},  # Dry
        {"date": "2026-01-29", "NDWI": 0.34},  # Wet again
        {"date": "2026-02-05", "NDWI": 0.38},
        {"date": "2026-02-12", "NDWI": 0.17},  # Dry
        {"date": "2026-02-19", "NDWI": 0.35},  # Wet
    ]
    
    result = detect_awd_from_ndwi(sample_data)
    print(f"AWD Detected: {result['awd_detected']}")
    print(f"Cycles: {result['cycles_count']}")
    print(f"Recommendation: {result['recommendation']}")