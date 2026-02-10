"""
Request/Response Logging Middleware
Logs all API requests and responses for debugging and monitoring
"""
import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all incoming requests and outgoing responses.
    Useful for debugging and monitoring API usage.
    """
    
    def process_request(self, request):
        """Log incoming request details"""
        import uuid
        request.start_time = time.time()
        
        # Generate or get request ID
        request_id = request.META.get('HTTP_X_REQUEST_ID') or str(uuid.uuid4())
        request.request_id = request_id

        
        # Log request details
        log_data = {
            'request_id': request.request_id,
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            'ip': self.get_client_ip(request),
        }
        
        # Log query parameters for GET requests
        if request.method == 'GET' and request.GET:
            log_data['query_params'] = dict(request.GET)
        
        logger.info(f"Request: {json.dumps(log_data)}")
        
    def process_response(self, request, response):
        """Log response details"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'request_id': getattr(request, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            }

            # Return request ID to client
            if hasattr(request, 'request_id'):
                response['X-Request-ID'] = request.request_id
            
            # Color code based on status
            if 200 <= response.status_code < 300:
                logger.info(f"Response: {json.dumps(log_data)}")
            elif 400 <= response.status_code < 500:
                logger.warning(f"Response: {json.dumps(log_data)}")
            else:
                logger.error(f"Response: {json.dumps(log_data)}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions"""
        log_data = {
            'method': request.method,
            'path': request.path,
            'exception': str(exception),
            'type': type(exception).__name__,
        }
        logger.error(f"Exception: {json.dumps(log_data)}", exc_info=True)
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
