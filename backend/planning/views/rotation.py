"""
Crop Rotation Planner views for KrishiSaarthi.
Rule-based rotation suggestions using agronomic best practices.

The rotation matrix scores are derived from published ICAR crop rotation
guidelines. Crop history is pulled from the user's actual SeasonCalendar
records; if no history exists, the response says so honestly.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import logging

from field.models import FieldData
from planning.models import SeasonCalendar

logger = logging.getLogger(__name__)


# Crop rotation compatibility matrix
# Score: 1-5 (1=poor, 5=excellent)
ROTATION_MATRIX = {
    'Rice': {
        'Wheat': 5, 'Pulses': 5, 'Mustard': 4, 'Potato': 3, 'Vegetables': 4,
        'Rice': 1, 'Sugarcane': 2, 'Cotton': 3, 'Maize': 4, 'Groundnut': 4
    },
    'Wheat': {
        'Rice': 4, 'Pulses': 5, 'Cotton': 4, 'Sugarcane': 3, 'Vegetables': 4,
        'Wheat': 1, 'Maize': 3, 'Groundnut': 4, 'Soybean': 5, 'Mustard': 3
    },
    'Cotton': {
        'Wheat': 5, 'Pulses': 5, 'Groundnut': 4, 'Soybean': 4, 'Maize': 4,
        'Cotton': 1, 'Rice': 2, 'Sugarcane': 2, 'Vegetables': 3
    },
    'Sugarcane': {
        'Rice': 4, 'Wheat': 4, 'Pulses': 5, 'Vegetables': 4, 'Groundnut': 4,
        'Sugarcane': 1, 'Cotton': 2, 'Maize': 3
    },
    'Maize': {
        'Pulses': 5, 'Wheat': 4, 'Soybean': 5, 'Groundnut': 4, 'Vegetables': 4,
        'Maize': 2, 'Rice': 3, 'Cotton': 4
    },
    'Pulses': {
        'Rice': 5, 'Wheat': 5, 'Cotton': 5, 'Maize': 5, 'Vegetables': 5,
        'Pulses': 2, 'Sugarcane': 4, 'Groundnut': 3
    },
    'Vegetables': {
        'Pulses': 5, 'Rice': 4, 'Wheat': 4, 'Maize': 4, 'Groundnut': 4,
        'Vegetables': 2, 'Cotton': 3
    },
    'default': {
        'Pulses': 5, 'Vegetables': 4, 'Maize': 4, 'Wheat': 4, 'Rice': 3
    }
}

# Crop benefits for soil
CROP_BENEFITS = {
    'Pulses': {'nitrogen_fix': True, 'soil_structure': 'improves', 'pest_break': True},
    'Rice': {'nitrogen_fix': False, 'soil_structure': 'compacts', 'pest_break': False},
    'Wheat': {'nitrogen_fix': False, 'soil_structure': 'neutral', 'pest_break': True},
    'Cotton': {'nitrogen_fix': False, 'soil_structure': 'depletes', 'pest_break': False},
    'Sugarcane': {'nitrogen_fix': False, 'soil_structure': 'depletes', 'pest_break': False},
    'Maize': {'nitrogen_fix': False, 'soil_structure': 'neutral', 'pest_break': True},
    'Vegetables': {'nitrogen_fix': False, 'soil_structure': 'varies', 'pest_break': True},
    'Groundnut': {'nitrogen_fix': True, 'soil_structure': 'improves', 'pest_break': True},
    'Soybean': {'nitrogen_fix': True, 'soil_structure': 'improves', 'pest_break': True},
}

# Seasonal crop mapping
SEASONAL_CROPS = {
    'Kharif': ['Rice', 'Cotton', 'Maize', 'Groundnut', 'Soybean', 'Sugarcane'],
    'Rabi': ['Wheat', 'Mustard', 'Pulses', 'Potato', 'Vegetables'],
    'Zaid': ['Vegetables', 'Watermelon', 'Cucumber', 'Muskmelon']
}


class RotationPlannerView(APIView):
    """
    GET: Returns crop rotation suggestions for a field
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        field_id = request.query_params.get('field_id')
        
        if not field_id:
            return Response({'error': 'field_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            field = FieldData.objects.get(id=field_id, user=request.user)
        except FieldData.DoesNotExist:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)
        
        current_crop = field.cropType
        
        # Get rotation suggestions
        suggestions = self._get_rotation_suggestions(current_crop)
        
        # Get current season
        current_season = self._get_current_season()
        
        # Build rotation timeline (3 seasons ahead)
        timeline = self._build_rotation_timeline(current_crop, current_season)
        
        return Response({
            'field_id': field.id,
            'field_name': field.name,
            'current_crop': current_crop,
            'current_season': current_season,
            'crop_history': self._get_crop_history(field, request.user),
            'suggestions': suggestions,
            'timeline': timeline,
            'soil_health_tips': self._get_soil_tips(current_crop)
        })
    
    def _get_rotation_suggestions(self, current_crop):
        """Get ranked rotation suggestions for next crop"""
        matrix = ROTATION_MATRIX.get(current_crop, ROTATION_MATRIX['default'])
        
        suggestions = []
        for crop, score in sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:5]:
            benefits = CROP_BENEFITS.get(crop, {})
            
            reasons = []
            if benefits.get('nitrogen_fix'):
                reasons.append('Fixes nitrogen in soil')
            if benefits.get('pest_break'):
                reasons.append('Breaks pest/disease cycle')
            if benefits.get('soil_structure') == 'improves':
                reasons.append('Improves soil structure')
            if score >= 4:
                reasons.append(f'Excellent rotation after {current_crop}')
            
            suggestions.append({
                'crop': crop,
                'score': score,
                'rating': self._score_to_rating(score),
                'reasons': reasons if reasons else ['Compatible rotation option'],
                'season': self._get_best_season(crop),
                'benefits': benefits
            })
        
        return suggestions
    
    def _score_to_rating(self, score):
        """Convert score to star rating"""
        if score >= 5: return {'stars': 5, 'label': 'Excellent'}
        if score >= 4: return {'stars': 4, 'label': 'Very Good'}
        if score >= 3: return {'stars': 3, 'label': 'Good'}
        if score >= 2: return {'stars': 2, 'label': 'Fair'}
        return {'stars': 1, 'label': 'Poor'}
    
    def _get_best_season(self, crop):
        """Get best season to plant this crop"""
        for season, crops in SEASONAL_CROPS.items():
            if crop in crops:
                return season
        return 'Any'
    
    def _get_current_season(self):
        """Determine current agricultural season"""
        month = timezone.now().month
        if 6 <= month <= 10:  # June-October
            return 'Kharif'
        elif month >= 11 or month <= 3:  # November-March
            return 'Rabi'
        else:  # April-May
            return 'Zaid'
    
    def _build_rotation_timeline(self, current_crop, current_season):
        """Build a 3-season rotation timeline"""
        seasons_order = ['Kharif', 'Rabi', 'Zaid']
        current_idx = seasons_order.index(current_season) if current_season in seasons_order else 0
        
        timeline = [{
            'season': current_season,
            'year': timezone.now().year,
            'crop': current_crop,
            'status': 'current',
            'icon': '🌾'
        }]
        
        # Suggest next 3 seasons
        year = timezone.now().year
        prev_crop = current_crop
        
        for i in range(1, 4):
            next_idx = (current_idx + i) % 3
            season = seasons_order[next_idx]
            if next_idx <= current_idx:
                year += 1
            
            # Get best crop for this season after prev_crop
            matrix = ROTATION_MATRIX.get(prev_crop, ROTATION_MATRIX['default'])
            seasonal_options = SEASONAL_CROPS.get(season, [])
            
            best_crop = None
            best_score = 0
            for crop, score in matrix.items():
                if crop in seasonal_options and score > best_score:
                    best_crop = crop
                    best_score = score
            
            if not best_crop and seasonal_options:
                best_crop = seasonal_options[0]
            
            timeline.append({
                'season': season,
                'year': year,
                'crop': best_crop or 'Recommended',
                'status': 'suggested',
                'score': best_score,
                'icon': '🌱'
            })
            prev_crop = best_crop or prev_crop
        
        return timeline
    
    def _get_crop_history(self, field, user):
        """
        Return real crop history from SeasonCalendar records for this field.
        If no records exist, return an empty list with an explanatory note.
        """
        events = (
            SeasonCalendar.objects
            .filter(field=field, user=user)
            .order_by('-start_date')[:10]
        )
        if not events.exists():
            return {
                'records': [],
                'note': 'No planting history found. Add calendar events to improve rotation suggestions.',
            }
        return {
            'records': [
                {
                    'year': e.start_date.year,
                    'season': self._date_to_season(e.start_date.month),
                    'crop': e.title,
                    'activity': e.activity_type,
                    'start_date': e.start_date.isoformat(),
                    'end_date': e.end_date.isoformat(),
                }
                for e in events
            ],
            'note': None,
        }

    @staticmethod
    def _date_to_season(month):
        """Map a calendar month to an Indian agricultural season."""
        if 6 <= month <= 10:
            return 'Kharif'
        elif month >= 11 or month <= 3:
            return 'Rabi'
        return 'Zaid'
    
    def _get_soil_tips(self, current_crop):
        """Get soil health tips based on current crop"""
        tips = []
        
        benefits = CROP_BENEFITS.get(current_crop, {})
        
        if benefits.get('soil_structure') == 'depletes':
            tips.append({
                'type': 'warning',
                'icon': '⚠️',
                'text': f'{current_crop} depletes soil nutrients. Consider legume rotation next.'
            })
        
        if not benefits.get('nitrogen_fix'):
            tips.append({
                'type': 'info',
                'icon': '💡',
                'text': 'Plant pulses/legumes next season to naturally replenish nitrogen.'
            })
        
        tips.append({
            'type': 'tip',
            'icon': '🌿',
            'text': 'Avoid planting the same crop family consecutively to prevent pest buildup.'
        })
        
        tips.append({
            'type': 'tip',
            'icon': '🔄',
            'text': 'Follow deep-rooted crops with shallow-rooted ones to utilize different soil layers.'
        })
        
        return tips
