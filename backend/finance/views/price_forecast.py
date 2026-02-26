"""
Price Forecast view for KrishiSaarthi.
Predicts crop prices for the next 30 days using trend analysis.
"""
import hashlib
import logging
import math
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

logger = logging.getLogger(__name__)


# Base prices for prediction (INR per quintal)
BASE_PRICES = {
    'Rice': 2450,
    'Wheat': 2200,
    'Cotton': 6500,
    'Sugarcane': 350,
    'Maize': 1900,
    'Soybean': 4800,
    'Groundnut': 5500,
    'Pulses': 6200,
    'Potato': 1200,
    'Onion': 1800,
    'Tomato': 2000,
}

# Seasonal factors (multipliers based on month)
SEASONAL_FACTORS = {
    'Rice': {1: 0.95, 2: 0.93, 3: 0.92, 4: 0.95, 5: 1.0, 6: 1.05, 7: 1.08, 8: 1.1, 9: 1.05, 10: 0.98, 11: 0.95, 12: 0.94},
    'Wheat': {1: 1.05, 2: 1.08, 3: 1.1, 4: 0.95, 5: 0.92, 6: 0.9, 7: 0.92, 8: 0.95, 9: 0.98, 10: 1.0, 11: 1.02, 12: 1.04},
}


class PriceForecastView(APIView):
    """
    GET: Returns 30-day price forecast for a crop
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        crop = request.query_params.get('crop', 'Rice')
        days = int(request.query_params.get('days', 30))
        days = min(days, 60)  # Cap at 60 days
        
        base_price = BASE_PRICES.get(crop, 2000)
        today = timezone.now().date()
        current_month = today.month
        
        # Get seasonal factor
        seasonal = SEASONAL_FACTORS.get(crop, {}).get(current_month, 1.0)
        
        # Generate forecast
        forecast = self._generate_forecast(crop, base_price, seasonal, days, today)
        
        # Calculate metrics
        prices = [day['predicted_price'] for day in forecast]
        trend = self._calculate_trend(prices)
        volatility = self._calculate_volatility(prices)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(trend, volatility, crop)
        
        return Response({
            'crop': crop,
            'base_price': base_price,
            'forecast_days': days,
            'generated_at': timezone.now().isoformat(),
            'forecast': forecast,
            'summary': {
                'current_price': forecast[0]['predicted_price'],
                'end_price': forecast[-1]['predicted_price'],
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': round(sum(prices) / len(prices)),
                'trend': trend,
                'volatility': volatility,
                'confidence': self._calculate_confidence(days),
            },
            'recommendation': recommendation,
        })
    
    def _seed_from(self, *parts):
        """Deterministic seed from string parts."""
        key = '-'.join(str(p) for p in parts)
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (10**8)

    def _generate_forecast(self, crop, base_price, seasonal, days, start_date):
        """Generate deterministic price forecast using seeded daily changes"""
        forecast = []
        
        # Deterministic initial variation
        init_seed = self._seed_from(crop, start_date.isoformat(), 'init')
        current_price = base_price * seasonal
        current_price *= (0.95 + (init_seed % 100) / 1000)  # 0.95 to 1.05
        
        # Deterministic drift
        drift_seed = self._seed_from(crop, start_date.isoformat(), 'drift')
        drift = ((drift_seed % 40) - 10) / 10000  # -0.001 to 0.003
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            
            # Deterministic daily change
            day_seed = self._seed_from(crop, date.isoformat(), 'day', i)
            daily_change = drift + ((day_seed % 300) - 150) / 10000  # drift ± 0.015
            current_price *= (1 + daily_change)
            
            current_price = max(base_price * 0.7, min(base_price * 1.4, current_price))
            
            confidence = max(50, 95 - (i * 1.5))
            
            forecast.append({
                'date': date.isoformat(),
                'day': i + 1,
                'predicted_price': round(current_price),
                'lower_bound': round(current_price * (1 - (0.02 + i * 0.002))),
                'upper_bound': round(current_price * (1 + (0.02 + i * 0.002))),
                'confidence': round(confidence),
            })
        
        return forecast
    
    def _calculate_trend(self, prices):
        """Calculate price trend direction"""
        if len(prices) < 2:
            return 'stable'
        
        start_avg = sum(prices[:3]) / 3
        end_avg = sum(prices[-3:]) / 3
        change = (end_avg - start_avg) / start_avg * 100
        
        if change > 3:
            return 'bullish'
        elif change < -3:
            return 'bearish'
        else:
            return 'stable'
    
    def _calculate_volatility(self, prices):
        """Calculate price volatility"""
        if len(prices) < 2:
            return 'low'
        
        avg = sum(prices) / len(prices)
        variance = sum((p - avg) ** 2 for p in prices) / len(prices)
        std_dev = math.sqrt(variance)
        cv = (std_dev / avg) * 100  # Coefficient of variation
        
        if cv < 3:
            return 'low'
        elif cv < 7:
            return 'medium'
        else:
            return 'high'
    
    def _calculate_confidence(self, days):
        """Calculate overall forecast confidence"""
        if days <= 7:
            return 'high'
        elif days <= 15:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendation(self, trend, volatility, crop):
        """Generate buy/sell/hold recommendation"""
        recommendations = []
        
        if trend == 'bullish':
            recommendations.append({
                'type': 'timing',
                'icon': '📈',
                'text': f'Prices for {crop} are expected to rise. Consider holding stock for better prices.',
                'action': 'hold'
            })
        elif trend == 'bearish':
            recommendations.append({
                'type': 'timing',
                'icon': '📉',
                'text': f'Prices for {crop} may decline. Consider selling soon if you have stock.',
                'action': 'sell'
            })
        else:
            recommendations.append({
                'type': 'timing',
                'icon': '➡️',
                'text': f'Prices for {crop} are expected to remain stable. Sell based on your storage capacity.',
                'action': 'hold'
            })
        
        if volatility == 'high':
            recommendations.append({
                'type': 'warning',
                'icon': '⚠️',
                'text': 'High price volatility expected. Consider hedging or selling in batches.',
            })
        
        recommendations.append({
            'type': 'tip',
            'icon': '💡',
            'text': 'Check mandi prices before selling. Government MSP is always available as a floor price.',
        })
        
        return recommendations
