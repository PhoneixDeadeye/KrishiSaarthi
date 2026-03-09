from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from .models import FieldData

from shapely.geometry import Polygon
from pyproj import CRS, Transformer
from shapely.ops import transform

from .services.ee_service import fetchEEData_safe

def fetchEEData(user=None, field_id=None, field_instance=None, start_date=None, end_date=None):
    """
    Proxy to new safe Earth Engine service.
    Maintained for backward compatibility.
    """
    return fetchEEData_safe(user, field_id, field_instance, start_date, end_date)


def get_utm_crs(lon, lat):
    """
    Calculate the correct EPSG code for the UTM zone of a given point.
    """
    zone = int((lon + 180) / 6) + 1
    base = 32600 if lat >= 0 else 32700
    return f"EPSG:{base + zone}"


def calculate_area_in_hectares(coords_list):
    """
    Calculate area of a polygon in hectares using dynamic UTM projection.
    
    Args:
        coords_list: List of coordinate pairs [[[lon, lat], ...]] (GeoJSON Ring)
    """
    try:
        if not coords_list or len(coords_list) < 3:
            return 0.0

        # Create shapely Polygon
        polygon_geom = Polygon(coords_list)
        
        # Get centroid to determine UTM zone
        centroid = polygon_geom.centroid
        lon, lat = centroid.x, centroid.y
        
        # Get dynamic CRS
        target_crs = get_utm_crs(lon, lat)
        
        # Define projection
        # Source is WGS 84 (EPSG:4326)
        project = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True).transform

        # Apply projection
        projected_polygon = transform(project, polygon_geom)

        # Calculate area
        area_sq_meters = projected_polygon.area
        
        # Convert to hectares
        area_hectares = area_sq_meters / 10000

        return area_hectares
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Area calculation failed: %s", e)
        return 0.0