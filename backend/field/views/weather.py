import logging
import requests
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

class WeatherView(APIView):
    """Proxy for OpenWeather API to keep API key server-side"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        
        if not lat or not lon:
            return Response(
                {"error": "lat and lon query parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get API key from environment
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        if not api_key:
             return Response(
                {"error": "Weather service not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        try:
            # Current weather
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            weather_res = requests.get(weather_url, timeout=5)
            
            if not weather_res.ok:
                logger.error(f"Weather API error: {weather_res.status_code} - {weather_res.text}")
                return Response({"error": "Failed to fetch weather data"}, status=weather_res.status_code)

            weather_data = weather_res.json()
            
            # Forecast
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            forecast_res = requests.get(forecast_url, timeout=5)
            forecast_data = forecast_res.json().get('list', []) if forecast_res.ok else []
            
            return Response({
                "current": weather_data,
                "forecast": forecast_data
            })
        except requests.RequestException as e:
            logger.error(f"Weather request failed: {e}", exc_info=True)
            return Response(
                {"error": "Weather service unreachable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            logger.exception("Unexpected error in WeatherView")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
