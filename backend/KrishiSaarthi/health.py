"""
Health check and monitoring endpoints
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """
    Basic health check endpoint for load balancers and monitoring
    """
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        """Check if the service is alive"""
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    """
    Readiness check - verifies all dependencies are available
    """
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        """
        Check if the service is ready to accept requests
        Verifies: database, ML models, Earth Engine
        """
        checks = {
            "database": False,
            "ml_models": False,
            "earth_engine": False,
        }
        
        all_ready = True
        
        # Check database
        try:
            connection.ensure_connection()
            checks["database"] = True
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            all_ready = False
        
        # Check ML models
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'crop_health_model.pth')
        lstm_path = os.path.join(settings.BASE_DIR, 'ml_models', 'risk_lstm_final.pth')
        checks["ml_models"] = os.path.exists(model_path) and os.path.exists(lstm_path)
        if not checks["ml_models"]:
            logger.warning("ML models not found")
        
        # Check Earth Engine
        try:
            import ee
            ee.Initialize()
            checks["earth_engine"] = True
        except Exception as e:
            logger.warning(f"Earth Engine check failed: {e}")
            checks["earth_engine"] = False
        
        response_status = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response({
            "status": "ready" if all_ready else "not_ready",
            "checks": checks
        }, status=response_status)


class MetricsView(APIView):
    """
    Basic metrics endpoint for monitoring
    """
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        """Return basic application metrics"""
        from django.contrib.auth.models import User
        from field.models import FieldData, Pest, FieldLog
        
        try:
            metrics = {
                "users_total": User.objects.count(),
                "fields_total": FieldData.objects.count(),
                "pest_reports_total": Pest.objects.count(),
                "field_logs_total": FieldLog.objects.count(),
            }
            
            return Response(metrics, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return Response(
                {"error": "Failed to collect metrics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
