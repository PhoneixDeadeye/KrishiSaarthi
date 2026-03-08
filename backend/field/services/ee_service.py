import ee
import time
import logging
import traceback
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from ..models import FieldData

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def allow_request(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("Circuit breaker probing (HALF-OPEN)")
                return True
            return False
        return True

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")

    def record_success(self):
        if self.state == "HALF-OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            logger.info("Circuit breaker CLOSED (Recovered)")
        elif self.state == "CLOSED":
            self.failure_count = 0

# Global circuit breaker instance
ee_breaker = CircuitBreaker()

def fetchEEData_safe(user=None, field_id=None, field_instance=None, start_date=None, end_date=None):
    """
    Wrapper for fetchEEData that strictly enforces circuit breaker logic.
    """
    if not ee_breaker.allow_request():
        logger.warning("Earth Engine request blocked by circuit breaker")
        return {
            "error": "Service temporarily unavailable",
            "details": "Please try again later",
            "fallback": True
        }

    try:
        data = _fetch_ee_data_impl(user, field_id, field_instance, start_date, end_date)
        ee_breaker.record_success()
        return data
    except Exception as e:
        ee_breaker.record_failure()
        logger.error(f"EE Service Failure: {e}", exc_info=True)
        return {
            "error": "Satellite data unavailable",
            "details": "Please try again later",
            "fallback": True
        }

def _fetch_ee_data_impl(user, field_id, field_instance, start_date, end_date):
    """
    Implementation of Earth Engine data path.
    """
    # Initialize date range - default to last 90 days
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    # Fetch polygon for the user
    if field_instance:
        field_data = field_instance
    elif field_id and user:
        field_data = get_object_or_404(FieldData, id=field_id, user=user)
    elif user:
        # Fallback to first field if no specific field requested
        field_data = FieldData.objects.filter(user=user).first()
        if not field_data:
            return {"error": "No fields found"} 
    else:
        return {"error": "User or field required"}

    coords = field_data.polygon
    # Ensure coords is a valid geometry or list of lists
    if isinstance(coords, dict) and 'coordinates' in coords:
        geom = coords['coordinates']
    else:
        geom = coords
        
    aoi = ee.Geometry.Polygon(geom)

    # --- Vegetation Indices ---
    sentinel = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .median()
    )

    ndvi = sentinel.normalizedDifference(["B8", "B4"]).rename("NDVI")
    evi = sentinel.expression(
        "2.5 * ((NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1))",
        {
            "NIR": sentinel.select("B8"),
            "RED": sentinel.select("B4"),
            "BLUE": sentinel.select("B2"),
        },
    ).rename("EVI")
    savi = sentinel.expression(
        "((NIR - RED) / (NIR + RED + 0.5)) * (1.5)",
        {"NIR": sentinel.select("B8"), "RED": sentinel.select("B4")},
    ).rename("SAVI")

    veg_stats = (
        ee.Image.cat([ndvi, evi, savi])
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=10,
            bestEffort=True,
        )
        .getInfo()
        or {}
    )

    # --- Crop Type ---
    worldcover = ee.Image("ESA/WorldCover/v100/2020")
    crop_class = (
        worldcover.reduceRegion(
            reducer=ee.Reducer.mode(),
            geometry=aoi,
            scale=10,
            bestEffort=True,
        ).getInfo()
        or {}
    )
    crop_type = crop_class.get("Map")

    # --- Rainfall ---
    rainfall = (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .mean()
        .reduceRegion(ee.Reducer.mean(), aoi, 5000)
        .getInfo()
        or {}
    )
    rainfall_val = rainfall.get("precipitation")

    # --- Temperature ---
    lst = (
        ee.ImageCollection("MODIS/061/MOD11A2")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .mean()
        .select("LST_Day_1km")
        .multiply(0.02)
        .reduceRegion(ee.Reducer.mean(), aoi, 1000)
        .getInfo()
        or {}
    )
    temp_val = lst.get("LST_Day_1km")

    # --- Soil Moisture ---
    soil = (
        ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_RAW")
        .filterDate(start_date, end_date)
        .mean()
        .select("volumetric_soil_water_layer_1")
        .reduceRegion(ee.Reducer.mean(), aoi, 10000)
        .getInfo()
        or {}
    )
    soil_val = soil.get("volumetric_soil_water_layer_1")

    # --- NDVI Time Series ---
    ndvi_ts = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .map(
            lambda img: img.normalizedDifference(["B8", "B4"])
            .rename("NDVI")
            .set("date", img.date().format("YYYY-MM-dd"))
        )
        .select("NDVI")
    )

    ndvi_series = ndvi_ts.map(
        lambda img: ee.Feature(
            None,
            {
                "date": img.get("date"),
                "NDVI": img.reduceRegion(
                    ee.Reducer.mean(), aoi, 10
                ).get("NDVI"),
            },
        )
    )

    ndvi_list = ndvi_series.aggregate_array("NDVI").getInfo()
    date_list = ndvi_series.aggregate_array("date").getInfo()
    time_series = []
    if ndvi_list and date_list:
        for d, v in zip(date_list, ndvi_list):
            if v is not None:
                time_series.append({"date": d, "NDVI": v})

    # --- NDWI Time Series ---
    ndwi_ts = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .map(
            lambda img: img.normalizedDifference(["B3", "B8"])
            .rename("NDWI")
            .set("date", img.date().format("YYYY-MM-dd"))
        )
        .select("NDWI")
    )

    ndwi_series = ndwi_ts.map(
        lambda img: ee.Feature(
            None,
            {
                "date": img.get("date"),
                "NDWI": img.reduceRegion(
                    ee.Reducer.mean(), aoi, 10
                ).get("NDWI"),
            },
        )
    )

    ndwi_list = ndwi_series.aggregate_array("NDWI").getInfo()
    ndwi_date_list = ndwi_series.aggregate_array("date").getInfo()
    ndwi_time_series = []
    if ndwi_list and ndwi_date_list:
        for d, v in zip(ndwi_date_list, ndwi_list):
            if v is not None:
                ndwi_time_series.append({"date": d, "NDWI": v})

    return {
        "NDVI": veg_stats.get("NDVI"),
        "EVI": veg_stats.get("EVI"),
        "SAVI": veg_stats.get("SAVI"),
        "crop_type_class": crop_type,
        "rainfall_mm": rainfall_val,
        "temperature_K": temp_val,
        "soil_moisture": soil_val,
        "ndvi_time_series": time_series,
        "ndwi_time_series": ndwi_time_series,
    }
