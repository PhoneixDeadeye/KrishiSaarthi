from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides structured error responses
    and logs unhandled exceptions.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Log the exception details
    path = context['request'].path if 'request' in context else 'unknown'
    method = context['request'].method if 'request' in context else 'unknown'
    
    if response is not None:
        # Expected error (e.g. validation error, 404, 403)
        if response.status_code >= 500:
            logger.error(f"Server Error {response.status_code} at {method} {path}: {exc}", exc_info=True)
        else:
            logger.warning(f"Client Error {response.status_code} at {method} {path}: {exc}")
            
        # Standardize the error format
        # If 'detail' is present, wrap it. If 'error' is present, keep it.
        # If validation errors (dict), wrap in 'details'.
        
        if 'detail' in response.data:
            response.data = {
                'error': response.data['detail'],
                'status': response.status_code
            }
        elif isinstance(response.data, dict) and 'error' not in response.data:
             # Likely validation errors
             response.data = {
                 'error': 'Validation Error',
                 'details': response.data,
                 'status': response.status_code
             }
            
    else:
        # Unhandled exception (500)
        logger.error(f"Unhandled Exception at {method} {path}: {exc}", exc_info=True)
        
        from django.conf import settings
        details = str(exc) if settings.DEBUG else 'An unexpected error occurred.'
        
        response = Response({
            'error': 'Internal Server Error',
            'details': details
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
