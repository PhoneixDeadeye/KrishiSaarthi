"""
Validation utilities for field data
"""
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def validate_polygon(polygon: Any) -> Tuple[bool, str]:
    """
    Validate GeoJSON polygon structure.
    
    Args:
        polygon: The polygon data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(polygon, dict):
        return False, "Polygon must be a dictionary"
    
    if 'coordinates' not in polygon:
        return False, "Polygon must contain 'coordinates' key"
    
    coords = polygon.get('coordinates')
    if not coords or not isinstance(coords, list):
        return False, "Coordinates must be a non-empty list"
    
    if len(coords) == 0:
        return False, "Coordinates array cannot be empty"
    
    # Check first ring
    if not isinstance(coords[0], list) or len(coords[0]) < 3:
        return False, "Polygon must have at least 3 points"
    
    # Validate coordinate format
    for ring in coords:
        if not isinstance(ring, list):
            return False, "Each ring must be a list"
        for point in ring:
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                return False, "Each point must have at least [lon, lat]"
            try:
                lon, lat = float(point[0]), float(point[1])
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    return False, f"Invalid coordinates: ({lon}, {lat})"
            except (ValueError, TypeError):
                return False, "Coordinates must be numeric"
    
    return True, ""


def validate_field_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate field creation/update data.
    
    Args:
        data: Dictionary containing field data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['polygon']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate polygon
    is_valid, error = validate_polygon(data['polygon'])
    if not is_valid:
        return False, f"Invalid polygon: {error}"
    
    # Validate crop type if provided
    if 'cropType' in data and data['cropType']:
        if not isinstance(data['cropType'], str):
            return False, "Crop type must be a string"
        if len(data['cropType']) > 32:
            return False, "Crop type too long (max 32 characters)"
    
    # Validate name if provided
    if 'name' in data and data['name']:
        if not isinstance(data['name'], str):
            return False, "Name must be a string"
        if len(data['name']) > 100:
            return False, "Name too long (max 100 characters)"
    
    return True, ""


def sanitize_coordinates(coords: List) -> List:
    """
    Sanitize and normalize coordinate values.
    
    Args:
        coords: List of coordinates
        
    Returns:
        Sanitized coordinates
    """
    def sanitize_point(point):
        try:
            lon = max(-180, min(180, float(point[0])))
            lat = max(-90, min(90, float(point[1])))
            return [lon, lat]
        except (ValueError, TypeError, IndexError):
            logger.warning(f"Invalid point in coordinates: {point}")
            return point
    
    sanitized = []
    for ring in coords:
        sanitized_ring = [sanitize_point(p) for p in ring]
        sanitized.append(sanitized_ring)
    
    return sanitized
