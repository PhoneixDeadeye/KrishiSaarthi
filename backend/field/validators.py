"""
Validation utilities for field data
"""
from typing import Dict, List, Any, Tuple
import logging
import math

logger = logging.getLogger(__name__)

# Maximum field area in square degrees (~111km per degree)
MAX_FIELD_AREA_SQ_DEG = 1.0  # Roughly 12,000 hectares at the equator


def _ring_area(ring: List) -> float:
    """Calculate area of a ring using the Shoelace formula (in square degrees)."""
    n = len(ring)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += ring[i][0] * ring[j][1]
        area -= ring[j][0] * ring[i][1]
    return abs(area) / 2.0


def validate_polygon(polygon: Any) -> None:
    """
    Validate GeoJSON polygon structure.
    Raises ``django.core.exceptions.ValidationError`` when the polygon is invalid.

    Can be used as a Django model/field validator or called directly.
    """
    from django.core.exceptions import ValidationError as DjangoValidationError

    if not isinstance(polygon, dict):
        raise DjangoValidationError("Polygon must be a dictionary")

    # GeoJSON type is required and must be 'Polygon'
    geo_type = polygon.get('type')
    if geo_type is None:
        raise DjangoValidationError("Missing required 'type' field. Expected 'Polygon'.")
    if geo_type != 'Polygon':
        raise DjangoValidationError(f"Expected GeoJSON type 'Polygon', got '{geo_type}'")

    if 'coordinates' not in polygon:
        raise DjangoValidationError("Polygon must contain 'coordinates' key")

    coords = polygon.get('coordinates')
    if not coords or not isinstance(coords, list):
        raise DjangoValidationError("Coordinates must be a non-empty list")

    if len(coords) == 0:
        raise DjangoValidationError("Coordinates array cannot be empty")

    # A valid polygon ring needs at least 4 points (3 unique + closure)
    if not isinstance(coords[0], list) or len(coords[0]) < 4:
        raise DjangoValidationError("Polygon must have at least 4 points (3 vertices + closure)")

    # Validate coordinate format
    for ring_idx, ring in enumerate(coords):
        if not isinstance(ring, list):
            raise DjangoValidationError("Each ring must be a list")
        for point in ring:
            if not isinstance(point, (list, tuple)) or len(point) < 2:
                raise DjangoValidationError("Each point must have at least [lon, lat]")
            try:
                lon, lat = float(point[0]), float(point[1])
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    raise DjangoValidationError(f"Invalid coordinates: ({lon}, {lat})")
            except (ValueError, TypeError):
                raise DjangoValidationError("Coordinates must be numeric")

        # Validate ring closure (first point must equal last point)
        if len(ring) >= 3:
            first, last = ring[0], ring[-1]
            if (float(first[0]) != float(last[0])) or (float(first[1]) != float(last[1])):
                raise DjangoValidationError(f"Ring {ring_idx} is not closed (first and last points must match)")

    # Check that polygon area is reasonable (not unreasonably large)
    exterior = coords[0]
    area = _ring_area([[float(p[0]), float(p[1])] for p in exterior])
    if area > MAX_FIELD_AREA_SQ_DEG:
        raise DjangoValidationError(f"Polygon area too large ({area:.4f} sq degrees). Max allowed: {MAX_FIELD_AREA_SQ_DEG}")

    # Check for self-intersection (simplified check: no duplicate consecutive points)
    for ring in coords:
        for i in range(len(ring) - 1):
            if (float(ring[i][0]) == float(ring[i + 1][0]) and
                    float(ring[i][1]) == float(ring[i + 1][1])):
                raise DjangoValidationError("Ring contains duplicate consecutive points")


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
    from django.core.exceptions import ValidationError as DjangoValidationError
    try:
        validate_polygon(data['polygon'])
    except DjangoValidationError as e:
        return False, f"Invalid polygon: {e.message}"
    
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
    Sanitize and validate coordinate values.
    Rejects invalid coordinates instead of silently clamping them.
    
    Args:
        coords: List of coordinate rings
        
    Returns:
        Sanitized coordinates
        
    Raises:
        ValueError: If any coordinate is out of valid range
    """
    sanitized = []
    for ring in coords:
        sanitized_ring = []
        for point in ring:
            try:
                lon = float(point[0])
                lat = float(point[1])
                if not (-180 <= lon <= 180):
                    raise ValueError(f"Longitude {lon} out of range [-180, 180]")
                if not (-90 <= lat <= 90):
                    raise ValueError(f"Latitude {lat} out of range [-90, 90]")
                sanitized_ring.append([lon, lat])
            except (ValueError, TypeError, IndexError) as exc:
                logger.warning("Invalid point in coordinates: %s — %s", point, exc)
                raise ValueError(f"Invalid coordinate point: {point}") from exc
        sanitized.append(sanitized_ring)
    
    return sanitized
