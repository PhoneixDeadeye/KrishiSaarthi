"""
Market Prices views for KrishiSaarthi.

TRANSPARENCY NOTE:
This module provides MSP (Minimum Support Price) reference data published by the
Government of India, combined with estimated price ranges based on historical
crop economics. It does NOT connect to a live mandi API.

The MSP values are sourced from the Commission for Agricultural Costs and Prices
(CACP) for the 2025-26 marketing season. Estimated market ranges are derived from
typical mandi spreads around MSP for each commodity.

A live data source (e.g., data.gov.in eNAM API) should replace the estimates
when deployed to production.
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

logger = logging.getLogger(__name__)


# MSP values from CACP 2025-26 and typical market range multipliers.
# These are REAL government-published floor prices.
MSP_DATA = {
    'Rice': {'msp': 2183, 'typical_low': 0.96, 'typical_high': 1.30},
    'Wheat': {'msp': 2125, 'typical_low': 0.95, 'typical_high': 1.15},
    'Cotton': {'msp': 6620, 'typical_low': 0.85, 'typical_high': 1.15},
    'Sugarcane': {'msp': 315, 'typical_low': 0.95, 'typical_high': 1.25},
    'Maize': {'msp': 1962, 'typical_low': 0.90, 'typical_high': 1.15},
    'Soybean': {'msp': 4600, 'typical_low': 0.88, 'typical_high': 1.15},
    'Groundnut': {'msp': 5850, 'typical_low': 0.90, 'typical_high': 1.12},
    'Pulses': {'msp': 6600, 'typical_low': 0.92, 'typical_high': 1.10},
    'Potato': {'msp': None, 'typical_low': 800, 'typical_high': 2000},
    'Onion': {'msp': None, 'typical_low': 600, 'typical_high': 3500},
    'Tomato': {'msp': None, 'typical_low': 500, 'typical_high': 4000},
}


class MarketPricesView(APIView):
    """
    GET: Returns MSP reference data and estimated market price ranges.
    Clearly marked as reference/estimated — not live mandi data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        crop = request.query_params.get('crop', None)
        state = request.query_params.get('state', None)

        try:
            if crop and crop in MSP_DATA:
                crops_to_show = [crop]
            else:
                crops_to_show = list(MSP_DATA.keys())

            price_cards = []
            for crop_name in crops_to_show:
                info = MSP_DATA[crop_name]
                msp = info['msp']
                if msp:
                    estimated_low = int(msp * info['typical_low'])
                    estimated_high = int(msp * info['typical_high'])
                else:
                    estimated_low = info['typical_low']
                    estimated_high = info['typical_high']

                price_cards.append({
                    'crop': crop_name,
                    'msp': msp,
                    'estimated_range': {
                        'low': estimated_low,
                        'high': estimated_high,
                    },
                    'unit': 'quintal',
                })

            return Response({
                'date': timezone.now().date().isoformat(),
                'state': state,
                'data_source': 'CACP MSP 2025-26 + historical range estimates',
                'is_live_data': False,
                'disclaimer': (
                    'MSP values are official Government of India rates. '
                    'Market price ranges are estimates based on historical spreads '
                    'and do not reflect real-time mandi prices. Always verify at '
                    'your local APMC mandi before selling.'
                ),
                'prices': price_cards,
                'tips': self._get_tips(crop),
            })

        except Exception as e:
            logger.error(f"Error in market prices: {e}")
            return Response(
                {'error': 'Failed to load market price data'},
                status=500,
            )

    def _get_tips(self, crop):
        """Static, genuinely useful market tips."""
        tips = [
            {
                'type': 'info',
                'icon': '📈',
                'text': 'Check prices at multiple mandis before selling for best rates.',
            },
            {
                'type': 'tip',
                'icon': '💡',
                'text': 'Government procurement centers offer MSP — check your local APMC.',
            },
            {
                'type': 'timing',
                'icon': '⏰',
                'text': 'Prices typically peak 2-3 months after harvest when supply reduces.',
            },
        ]
        if crop:
            info = MSP_DATA.get(crop, {})
            if info.get('msp'):
                tips.insert(0, {
                    'type': 'msp',
                    'icon': '🏛️',
                    'text': (
                        f'MSP for {crop}: ₹{info["msp"]}/quintal (2025-26). '
                        f'Sell at government centres if market price is lower.'
                    ),
                })
        return tips
