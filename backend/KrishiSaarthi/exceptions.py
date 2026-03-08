"""
Custom exception handling for KrishiSaarthi REST API.

Provides:
- Structured JSON error responses
- Domain-specific exception classes
- Centralised logging of all errors
"""
from __future__ import annotations

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


# ── Domain-Specific Exceptions ───────────────────────────────────────────────

class ServiceUnavailableError(APIException):
    """Raised when an external service (EE, Gemini, Weather) is down."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "External service temporarily unavailable."
    default_code = "service_unavailable"


class EarthEngineError(ServiceUnavailableError):
    """Google Earth Engine specific failure."""
    default_detail = "Satellite data service temporarily unavailable."
    default_code = "earth_engine_error"


class MLModelError(APIException):
    """Raised when an ML model fails to load or predict."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "ML model inference failed."
    default_code = "ml_model_error"


class InvalidPolygonError(APIException):
    """Raised when a supplied GeoJSON polygon is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The supplied polygon geometry is invalid."
    default_code = "invalid_polygon"


class RateLimitExceededError(APIException):
    """Explicit rate-limit error for custom throttle feedback."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = "Request rate limit exceeded. Please try again later."
    default_code = "rate_limit_exceeded"


class ResourceNotFoundError(APIException):
    """Raised when a requested resource does not exist."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Requested resource not found."
    default_code = "not_found"


class PermissionDeniedError(APIException):
    """Raised when a user attempts to access a resource they don't own."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to access this resource."
    default_code = "permission_denied"


# ── Global Exception Handler ────────────────────────────────────────────────

def custom_exception_handler(exc: Exception, context: dict) -> Response:
    """
    Custom exception handler for DRF that provides structured error responses
    and logs unhandled exceptions.
    """
    response = exception_handler(exc, context)

    path = context['request'].path if 'request' in context else 'unknown'
    method = context['request'].method if 'request' in context else 'unknown'

    if response is not None:
        if response.status_code >= 500:
            logger.error(
                "Server Error %s at %s %s: %s",
                response.status_code, method, path, exc,
                exc_info=True,
            )
        elif response.status_code >= 400:
            logger.warning(
                "Client Error %s at %s %s: %s",
                response.status_code, method, path, exc,
            )

        # Standardise envelope
        if 'detail' in response.data:
            response.data = {
                'error': str(response.data['detail']),
                'code': getattr(exc, 'default_code', 'error'),
                'status': response.status_code,
            }
        elif isinstance(response.data, dict) and 'error' not in response.data:
            response.data = {
                'error': 'Validation Error',
                'code': 'validation_error',
                'details': response.data,
                'status': response.status_code,
            }
    else:
        # Unhandled exception → 500
        logger.error(
            "Unhandled Exception at %s %s: %s",
            method, path, exc,
            exc_info=True,
        )

        from django.conf import settings
        details = str(exc) if settings.DEBUG else 'An unexpected error occurred.'

        response = Response(
            {
                'error': 'Internal Server Error',
                'code': 'internal_error',
                'details': details,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
