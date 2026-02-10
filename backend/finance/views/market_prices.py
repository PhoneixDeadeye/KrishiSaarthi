"""
Market Prices views for KrishiSaarthi.
Mandi price tracking and market intelligence.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import logging
import random

logger = logging.getLogger(__name__)


# Base mandi prices (INR per quintal)
BASE_PRICES = {
    'Rice': {'min': 2100, 'max': 2800, 'msp': 2183},
    'Wheat': {'min': 1800, 'max': 2400, 'msp': 2125},
    'Cotton': {'min': 5500, 'max': 7500, 'msp': 6620},
    'Sugarcane': {'min': 300, 'max': 400, 'msp': 315},
    'Maize': {'min': 1600, 'max': 2200, 'msp': 1962},
    'Soybean': {'min': 3800, 'max': 5200, 'msp': 4600},
    'Groundnut': {'min': 5000, 'max': 6500, 'msp': 5850},
    'Pulses': {'min': 5500, 'max': 7000, 'msp': 6600},
    'Potato': {'min': 800, 'max': 2000, 'msp': None},
    'Onion': {'min': 600, 'max': 3500, 'msp': None},
    'Tomato': {'min': 500, 'max': 4000, 'msp': None},
}

# Major mandis by state
MANDIS = {
    'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda'],
    'Haryana': ['Karnal', 'Hisar', 'Rohtak', 'Ambala', 'Sirsa'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Meerut'],
    'Maharashtra': ['Mumbai', 'Pune', 'Nashik', 'Nagpur', 'Aurangabad'],
    'Gujarat': ['Ahmedabad', 'Rajkot', 'Surat', 'Vadodara', 'Junagadh'],
    'Madhya Pradesh': ['Indore', 'Bhopal', 'Jabalpur', 'Gwalior', 'Ujjain'],
    'Kerala': ['Kochi', 'Kozhikode', 'Thiruvananthapuram', 'Thrissur', 'Palakkad'],
}


class MarketPricesView(APIView):
    """
    GET: Returns market prices for crops
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        crop = request.query_params.get('crop', None)
        state = request.query_params.get('state', 'Punjab')
        
        # Get mandis for state
        mandis = MANDIS.get(state, MANDIS['Punjab'])
        
        # Generate price data for each mandi
        mandi_prices = []
        for mandi in mandis:
            prices = self._generate_mandi_prices(crop, mandi)
            mandi_prices.append(prices)
        
        # Get price trends
        trends = self._generate_price_trends(crop)
        
        # Get all crops summary
        crops_summary = self._get_all_crops_summary()
        
        return Response({
            'state': state,
            'crop': crop,
            'date': timezone.now().date().isoformat(),
            'mandi_prices': mandi_prices,
            'price_trends': trends,
            'crops_summary': crops_summary if not crop else None,
            'market_tips': self._get_market_tips(crop)
        })
    
    def _generate_mandi_prices(self, crop, mandi):
        """Generate prices for a specific mandi"""
        if crop and crop in BASE_PRICES:
            crops = [crop]
        else:
            crops = list(BASE_PRICES.keys())[:5]  # Top 5 crops
        
        prices = []
        for c in crops:
            base = BASE_PRICES.get(c, {'min': 1000, 'max': 2000, 'msp': None})
            
            # Add variation for different mandis
            variation = random.uniform(-0.1, 0.1)
            min_price = int(base['min'] * (1 + variation))
            max_price = int(base['max'] * (1 + variation))
            modal_price = int((min_price + max_price) / 2)
            
            # Determine trend
            trend_val = random.choice([-1, 0, 1])
            trend = 'up' if trend_val > 0 else ('down' if trend_val < 0 else 'stable')
            
            prices.append({
                'crop': c,
                'min_price': min_price,
                'max_price': max_price,
                'modal_price': modal_price,
                'msp': base['msp'],
                'vs_msp': round((modal_price / base['msp'] - 1) * 100, 1) if base['msp'] else None,
                'trend': trend,
                'unit': 'quintal'
            })
        
        return {
            'mandi': mandi,
            'prices': prices,
            'arrivals': random.randint(100, 5000),  # quintals
            'last_updated': timezone.now().isoformat()
        }
    
    def _generate_price_trends(self, crop):
        """Generate 7-day price trend data"""
        target_crop = crop or 'Rice'
        base = BASE_PRICES.get(target_crop, {'min': 1500, 'max': 2500})
        
        trends = []
        today = timezone.now().date()
        base_price = (base['min'] + base['max']) / 2
        
        for i in range(7, 0, -1):
            date = today - timedelta(days=i)
            # Generate random walk
            change = random.uniform(-0.02, 0.02)
            base_price = base_price * (1 + change)
            
            trends.append({
                'date': date.isoformat(),
                'price': round(base_price),
                'day': date.strftime('%a')
            })
        
        # Today's price
        trends.append({
            'date': today.isoformat(),
            'price': round(base_price * (1 + random.uniform(-0.01, 0.01))),
            'day': 'Today'
        })
        
        return {
            'crop': target_crop,
            'data': trends,
            'change_7d': round((trends[-1]['price'] / trends[0]['price'] - 1) * 100, 1)
        }
    
    def _get_all_crops_summary(self):
        """Get summary of all crop prices"""
        summary = []
        for crop, base in BASE_PRICES.items():
            variation = random.uniform(-0.05, 0.05)
            modal = int((base['min'] + base['max']) / 2 * (1 + variation))
            
            summary.append({
                'crop': crop,
                'modal_price': modal,
                'msp': base['msp'],
                'trend': random.choice(['up', 'down', 'stable']),
                'change': round(random.uniform(-5, 5), 1)
            })
        
        return sorted(summary, key=lambda x: x['modal_price'], reverse=True)
    
    def _get_market_tips(self, crop):
        """Get market intelligence tips"""
        tips = [
            {
                'type': 'info',
                'icon': '📈',
                'text': 'Check prices at multiple mandis before selling for best rates.'
            },
            {
                'type': 'tip',
                'icon': '💡',
                'text': 'Government procurement centers often offer MSP - check local APMC.'
            }
        ]
        
        if crop:
            base = BASE_PRICES.get(crop, {})
            if base.get('msp'):
                tips.append({
                    'type': 'msp',
                    'icon': '🏛️',
                    'text': f'MSP for {crop}: ₹{base["msp"]}/quintal. Sell at government centers if market price is lower.'
                })
        
        tips.append({
            'type': 'timing',
            'icon': '⏰',
            'text': 'Prices typically peak 2-3 months after harvest when supply reduces.'
        })
        
        return tips
