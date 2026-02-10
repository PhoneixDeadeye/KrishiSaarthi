"""
Crop Yield Prediction views for KrishiSaarthi.
Rule-based yield prediction using NDVI trends and crop-specific models.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import logging

from field.models import FieldData

logger = logging.getLogger(__name__)


# Crop yield models: base yield (kg/hectare) at optimal NDVI (0.7)
CROP_YIELD_MODELS = {
    'Rice': {'base_yield': 4500, 'ndvi_factor': 1.2, 'water_sensitive': True},
    'Wheat': {'base_yield': 3500, 'ndvi_factor': 1.1, 'water_sensitive': False},
    'Cotton': {'base_yield': 1800, 'ndvi_factor': 1.0, 'water_sensitive': False},
    'Sugarcane': {'base_yield': 70000, 'ndvi_factor': 0.9, 'water_sensitive': True},
    'Maize': {'base_yield': 5000, 'ndvi_factor': 1.15, 'water_sensitive': True},
    'Soybean': {'base_yield': 2000, 'ndvi_factor': 1.1, 'water_sensitive': False},
    'Groundnut': {'base_yield': 1500, 'ndvi_factor': 1.0, 'water_sensitive': False},
    'Potato': {'base_yield': 25000, 'ndvi_factor': 1.1, 'water_sensitive': True},
    'Onion': {'base_yield': 20000, 'ndvi_factor': 1.0, 'water_sensitive': True},
    'Tomato': {'base_yield': 30000, 'ndvi_factor': 1.15, 'water_sensitive': True},
    'default': {'base_yield': 3000, 'ndvi_factor': 1.0, 'water_sensitive': False},
}

# Regional average yields for comparison (kg/hectare)
REGIONAL_AVERAGES = {
    'Rice': 3800,
    'Wheat': 3100,
    'Cotton': 1500,
    'Sugarcane': 65000,
    'Maize': 4200,
    'default': 2500,
}


class YieldPredictionView(APIView):
    """
    GET: Returns yield prediction for a field based on NDVI and crop type
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        field_id = request.query_params.get('field_id')
        
        if not field_id:
            return Response({'error': 'field_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            field = FieldData.objects.get(id=field_id, user=request.user)
        except FieldData.DoesNotExist:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get field size from polygon (approximate)
        field_area_hectares = self._calculate_field_area(field.polygon)
        
        # Get NDVI data (mock for now - would come from Earth Engine)
        ndvi_data = self._get_ndvi_data(field)
        
        # Get crop model
        crop_type = field.cropType
        model = CROP_YIELD_MODELS.get(crop_type, CROP_YIELD_MODELS['default'])
        
        # Calculate prediction
        prediction = self._calculate_yield(ndvi_data, model, field_area_hectares)
        
        # Get regional comparison
        regional_avg = REGIONAL_AVERAGES.get(crop_type, REGIONAL_AVERAGES['default'])
        
        return Response({
            'field_id': field.id,
            'field_name': field.name,
            'crop_type': crop_type,
            'field_area_hectares': round(field_area_hectares, 2),
            'prediction': {
                'yield_per_hectare': round(prediction['yield_per_hectare']),
                'total_yield': round(prediction['total_yield']),
                'unit': 'kg',
                'confidence': prediction['confidence'],
                'range': {
                    'low': round(prediction['yield_per_hectare'] * 0.85),
                    'high': round(prediction['yield_per_hectare'] * 1.15)
                }
            },
            'ndvi': {
                'current': ndvi_data['current'],
                'trend': ndvi_data['trend'],
                'status': self._get_health_status(ndvi_data['current']),
                'time_series': ndvi_data['time_series']
            },
            'comparison': {
                'regional_average': regional_avg,
                'vs_regional': round((prediction['yield_per_hectare'] / regional_avg - 1) * 100),
                'rating': self._get_yield_rating(prediction['yield_per_hectare'], regional_avg)
            },
            'factors': prediction['factors'],
            'recommendations': self._get_recommendations(ndvi_data, model, crop_type)
        })
    
    def _calculate_field_area(self, polygon):
        """Approximate field area in hectares from polygon coordinates"""
        if not polygon or not isinstance(polygon, list) or len(polygon) < 3:
            return 1.0  # Default 1 hectare
        
        try:
            # Simple polygon area calculation using Shoelace formula
            n = len(polygon)
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                lat1 = polygon[i].get('lat', 0)
                lng1 = polygon[i].get('lng', 0)
                lat2 = polygon[j].get('lat', 0)
                lng2 = polygon[j].get('lng', 0)
                area += lat1 * lng2
                area -= lat2 * lng1
            area = abs(area) / 2.0
            
            # Convert to hectares (rough approximation: 1 degree ≈ 111km)
            area_km2 = area * (111 ** 2)
            area_hectares = area_km2 * 100
            
            return max(0.1, min(area_hectares, 1000))  # Clamp to reasonable range
        except:
            return 1.0
    
    def _get_ndvi_data(self, field):
        """Get NDVI time series for field (mock data for MVP)"""
        import random
        
        # Generate mock NDVI time series for last 12 weeks
        base_ndvi = 0.55 + random.random() * 0.2  # 0.55 - 0.75
        time_series = []
        
        today = timezone.now().date()
        for i in range(12, 0, -1):
            date = today - timedelta(weeks=i)
            # Add some variation
            ndvi = base_ndvi + (random.random() - 0.5) * 0.1
            ndvi = max(0.1, min(0.9, ndvi))  # Clamp
            time_series.append({
                'date': date.isoformat(),
                'ndvi': round(ndvi, 3)
            })
        
        # Current NDVI (most recent)
        current = time_series[-1]['ndvi'] if time_series else 0.5
        
        # Trend (comparing last 4 weeks vs previous 4 weeks)
        recent_avg = sum(t['ndvi'] for t in time_series[-4:]) / 4 if len(time_series) >= 4 else current
        older_avg = sum(t['ndvi'] for t in time_series[-8:-4]) / 4 if len(time_series) >= 8 else current
        trend = 'increasing' if recent_avg > older_avg + 0.02 else ('decreasing' if recent_avg < older_avg - 0.02 else 'stable')
        
        return {
            'current': round(current, 3),
            'trend': trend,
            'time_series': time_series
        }
    
    def _calculate_yield(self, ndvi_data, model, field_area):
        """Calculate predicted yield based on NDVI and crop model"""
        current_ndvi = ndvi_data['current']
        base_yield = model['base_yield']
        ndvi_factor = model['ndvi_factor']
        
        # NDVI-based yield adjustment
        # Optimal NDVI is around 0.7, scale down for lower values
        ndvi_multiplier = (current_ndvi / 0.7) ** ndvi_factor
        ndvi_multiplier = max(0.3, min(1.3, ndvi_multiplier))  # Clamp
        
        # Trend adjustment
        trend_factor = 1.0
        if ndvi_data['trend'] == 'increasing':
            trend_factor = 1.05
        elif ndvi_data['trend'] == 'decreasing':
            trend_factor = 0.95
        
        # Calculate final yield
        yield_per_hectare = base_yield * ndvi_multiplier * trend_factor
        total_yield = yield_per_hectare * field_area
        
        # Confidence based on NDVI stability and data availability
        confidence = min(85, 50 + int(current_ndvi * 40))
        
        return {
            'yield_per_hectare': yield_per_hectare,
            'total_yield': total_yield,
            'confidence': confidence,
            'factors': {
                'ndvi_impact': round((ndvi_multiplier - 1) * 100),
                'trend_impact': round((trend_factor - 1) * 100),
                'base_yield': base_yield
            }
        }
    
    def _get_health_status(self, ndvi):
        """Get crop health status from NDVI"""
        if ndvi >= 0.7:
            return {'status': 'Excellent', 'color': 'green', 'icon': '🌿'}
        elif ndvi >= 0.5:
            return {'status': 'Good', 'color': 'lime', 'icon': '🌱'}
        elif ndvi >= 0.3:
            return {'status': 'Moderate', 'color': 'yellow', 'icon': '🌾'}
        else:
            return {'status': 'Poor', 'color': 'red', 'icon': '⚠️'}
    
    def _get_yield_rating(self, predicted, regional_avg):
        """Rate yield vs regional average"""
        ratio = predicted / regional_avg
        if ratio >= 1.2:
            return {'rating': 'Excellent', 'stars': 5}
        elif ratio >= 1.1:
            return {'rating': 'Above Average', 'stars': 4}
        elif ratio >= 0.9:
            return {'rating': 'Average', 'stars': 3}
        elif ratio >= 0.75:
            return {'rating': 'Below Average', 'stars': 2}
        else:
            return {'rating': 'Poor', 'stars': 1}
    
    def _get_recommendations(self, ndvi_data, model, crop_type):
        """Generate recommendations based on prediction factors"""
        recommendations = []
        
        if ndvi_data['current'] < 0.5:
            recommendations.append({
                'type': 'warning',
                'icon': '⚠️',
                'text': 'NDVI indicates crop stress. Check for pest/disease or nutrient deficiency.'
            })
        
        if ndvi_data['trend'] == 'decreasing':
            recommendations.append({
                'type': 'action',
                'icon': '📉',
                'text': 'Vegetation health decreasing. Consider soil testing and foliar spray.'
            })
        
        if model.get('water_sensitive') and ndvi_data['current'] < 0.6:
            recommendations.append({
                'type': 'irrigation',
                'icon': '💧',
                'text': f'{crop_type} is water-sensitive. Ensure adequate irrigation.'
            })
        
        if ndvi_data['current'] >= 0.7:
            recommendations.append({
                'type': 'positive',
                'icon': '✅',
                'text': 'Excellent crop health! Continue current management practices.'
            })
        
        return recommendations
