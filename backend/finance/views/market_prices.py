"""
Market Prices views for KrishiSaarthi.
Mandi price tracking and market intelligence.
"""
import hashlib
import logging
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone

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
    
    def _seed_from(self, *parts):
        """Create deterministic seed from string parts (stable within same day)."""
        key = '-'.join(str(p) for p in parts) + '-' + timezone.now().date().isoformat()
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (10**8)

    def _generate_mandi_prices(self, crop, mandi):
        """Generate deterministic prices for a specific mandi"""
        if crop and crop in BASE_PRICES:
            crops = [crop]
        else:
            crops = list(BASE_PRICES.keys())[:5]
        
        prices = []
        for c in crops:
            base = BASE_PRICES.get(c, {'min': 1000, 'max': 2000, 'msp': None})
            seed = self._seed_from(mandi, c)
            
            variation = ((seed % 200) - 100) / 1000  # -0.1 to 0.1
            min_price = int(base['min'] * (1 + variation))
            max_price = int(base['max'] * (1 + variation))
            modal_price = int((min_price + max_price) / 2)
            
            trend_val = (seed % 3) - 1  # -1, 0, or 1
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
            'arrivals': 500 + (self._seed_from(mandi, 'arrivals') % 4500),
            'last_updated': timezone.now().isoformat()
        }
    
    def _generate_price_trends(self, crop):
        """Generate deterministic 7-day price trend data"""
        target_crop = crop or 'Rice'
        base = BASE_PRICES.get(target_crop, {'min': 1500, 'max': 2500})
        
        trends = []
        today = timezone.now().date()
        base_price = (base['min'] + base['max']) / 2
        
        for i in range(7, 0, -1):
            date = today - timedelta(days=i)
            seed = self._seed_from(target_crop, date.isoformat(), 'trend')
            change = ((seed % 40) - 20) / 1000  # -0.02 to 0.02
            base_price = base_price * (1 + change)
            
            trends.append({
                'date': date.isoformat(),
                'price': round(base_price),
                'day': date.strftime('%a')
            })
        
        seed_today = self._seed_from(target_crop, today.isoformat(), 'trend')
        change_today = ((seed_today % 20) - 10) / 1000
        trends.append({
            'date': today.isoformat(),
            'price': round(base_price * (1 + change_today)),
            'day': 'Today'
        })
        
        return {
            'crop': target_crop,
            'data': trends,
            'change_7d': round((trends[-1]['price'] / trends[0]['price'] - 1) * 100, 1)
        }
    
    def _get_all_crops_summary(self):
        """Get deterministic summary of all crop prices"""
        summary = []
        for crop_name, base in BASE_PRICES.items():
            seed = self._seed_from(crop_name, 'summary')
            variation = ((seed % 100) - 50) / 1000  # -0.05 to 0.05
            modal = int((base['min'] + base['max']) / 2 * (1 + variation))
            
            trend_options = ['up', 'down', 'stable']
            summary.append({
                'crop': crop_name,
                'modal_price': modal,
                'msp': base['msp'],
                'trend': trend_options[seed % 3],
                'change': round(((seed % 100) - 50) / 10, 1)
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
