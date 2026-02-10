"""
Caching utilities and decorators
"""
from functools import wraps
from django.core.cache import cache
from django.conf import settings
import hashlib
import json


def cache_key(*args, **kwargs):
    """Generate a cache key from arguments"""
    key_data = f"{args}:{kwargs}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_response(timeout=300, key_prefix='view'):
    """
    Decorator to cache view responses
    
    Usage:
        @cache_response(timeout=600, key_prefix='weather')
        def get_weather(lat, lon):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{key_prefix}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(key_pattern):
    """
    Invalidate cache entries matching pattern
    
    Usage:
        invalidate_cache('weather:*')
    """
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(key_pattern)
        else:
            # Fallback for cache backends that don't support pattern deletion
            pass
    except Exception:
        pass


class CacheManager:
    """Centralized cache management"""
    
    # Cache timeouts (in seconds)
    TIMEOUT_SHORT = 60          # 1 minute
    TIMEOUT_MEDIUM = 300        # 5 minutes
    TIMEOUT_LONG = 3600         # 1 hour
    TIMEOUT_DAY = 86400         # 24 hours
    
    @staticmethod
    def get_weather_data(lat, lon):
        """Get cached weather data"""
        key = f"weather:{lat}:{lon}"
        return cache.get(key)
    
    @staticmethod
    def set_weather_data(lat, lon, data, timeout=TIMEOUT_MEDIUM):
        """Cache weather data"""
        key = f"weather:{lat}:{lon}"
        cache.set(key, data, timeout)
    
    @staticmethod
    def get_satellite_data(field_id):
        """Get cached satellite data"""
        key = f"satellite:{field_id}"
        return cache.get(key)
    
    @staticmethod
    def set_satellite_data(field_id, data, timeout=TIMEOUT_DAY):
        """Cache satellite data"""
        key = f"satellite:{field_id}"
        cache.set(key, data, timeout)
    
    @staticmethod
    def get_risk_score(field_id):
        """Get cached risk score"""
        key = f"risk:{field_id}"
        return cache.get(key)
    
    @staticmethod
    def set_risk_score(field_id, score, timeout=TIMEOUT_LONG):
        """Cache risk score"""
        key = f"risk:{field_id}"
        cache.set(key, score, timeout)
    
    @staticmethod
    def get_field_analytics(field_id, period):
        """Get cached analytics"""
        key = f"analytics:{field_id}:{period}"
        return cache.get(key)
    
    @staticmethod
    def set_field_analytics(field_id, period, data, timeout=TIMEOUT_LONG):
        """Cache analytics data"""
        key = f"analytics:{field_id}:{period}"
        cache.set(key, data, timeout)
    
    @staticmethod
    def invalidate_field_cache(field_id):
        """Invalidate all cache for a specific field"""
        patterns = [
            f"satellite:{field_id}",
            f"risk:{field_id}",
            f"analytics:{field_id}:*",
        ]
        for pattern in patterns:
            invalidate_cache(pattern)
    
    @staticmethod
    def clear_all():
        """Clear all cache"""
        cache.clear()
