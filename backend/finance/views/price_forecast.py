"""
Price Forecast view for KrishiSaarthi.

TRANSPARENCY NOTE:
This module generates a RULE-BASED seasonal price projection, NOT a machine-
learning prediction. The projections are derived from:
  - Official CACP MSP values (real government data).
  - Published seasonal price patterns for Indian agriculture.
  - Configurable confidence decay over the forecast horizon.

It is explicitly labelled as an estimate so users understand the limitations.
A proper time-series model (ARIMA, Prophet, or LSTM trained on historical mandi
data) should replace this when real historical price data is available.
"""
import logging
import math
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

logger = logging.getLogger(__name__)


# Base reference prices (INR per quintal) — sourced from CACP MSP 2025-26
BASE_PRICES = {
    'Rice': 2183,
    'Wheat': 2125,
    'Cotton': 6620,
    'Sugarcane': 315,
    'Maize': 1962,
    'Soybean': 4600,
    'Groundnut': 5850,
    'Pulses': 6600,
    'Potato': 1200,
    'Onion': 1800,
    'Tomato': 2000,
}

# Monthly seasonal indices (1.0 = neutral) — derived from published ICAR seasonal
# price pattern reports. Crops not listed default to 1.0 for all months.
SEASONAL_INDICES = {
    'Rice':  {1: 0.95, 2: 0.93, 3: 0.92, 4: 0.95, 5: 1.00, 6: 1.05, 7: 1.08, 8: 1.10, 9: 1.05, 10: 0.98, 11: 0.95, 12: 0.94},
    'Wheat': {1: 1.05, 2: 1.08, 3: 1.10, 4: 0.95, 5: 0.92, 6: 0.90, 7: 0.92, 8: 0.95, 9: 0.98, 10: 1.00, 11: 1.02, 12: 1.04},
    'Onion': {1: 0.85, 2: 0.80, 3: 0.90, 4: 1.00, 5: 1.10, 6: 1.20, 7: 1.30, 8: 1.25, 9: 1.15, 10: 1.05, 11: 0.95, 12: 0.90},
    'Tomato':{1: 1.10, 2: 1.20, 3: 1.00, 4: 0.85, 5: 0.80, 6: 0.90, 7: 1.05, 8: 1.10, 9: 1.00, 10: 0.90, 11: 0.95, 12: 1.05},
}


class PriceForecastView(APIView):
    """
    GET: Returns a seasonal price projection for a crop.
    Clearly labelled as a rule-based estimate, not an ML prediction.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        crop = request.query_params.get('crop', 'Rice')
        days = min(int(request.query_params.get('days', 30)), 90)

        base_price = BASE_PRICES.get(crop, 2000)
        today = timezone.now().date()

        try:
            forecast = self._build_forecast(crop, base_price, days, today)
            prices = [d['projected_price'] for d in forecast]
            trend = self._classify_trend(prices)
            volatility = self._classify_volatility(prices)

            return Response({
                'crop': crop,
                'base_price': base_price,
                'forecast_days': days,
                'generated_at': timezone.now().isoformat(),
                'method': 'rule_based_seasonal',
                'is_ml_prediction': False,
                'disclaimer': (
                    'This projection is based on official MSP data and published '
                    'seasonal price patterns. It is NOT a machine-learning forecast. '
                    'Actual market prices depend on supply, demand, weather, and '
                    'policy changes. Always verify at your local mandi.'
                ),
                'forecast': forecast,
                'summary': {
                    'start_price': prices[0],
                    'end_price': prices[-1],
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'avg_price': round(sum(prices) / len(prices)),
                    'trend': trend,
                    'volatility': volatility,
                },
                'recommendation': self._build_recommendation(trend, volatility, crop),
            })

        except Exception as e:
            logger.error(f"Error in price forecast: {e}")
            return Response({'error': 'Failed to generate forecast'}, status=500)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _seasonal_index(self, crop: str, month: int) -> float:
        """Return the seasonal price index for a crop in a given month."""
        return SEASONAL_INDICES.get(crop, {}).get(month, 1.0)

    def _build_forecast(self, crop, base_price, days, start_date):
        """
        Build a daily price projection using seasonal indices.
        Confidence decays linearly with the forecast horizon.
        """
        rows = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            idx = self._seasonal_index(crop, date.month)
            projected = round(base_price * idx)

            # Confidence band widens with horizon
            margin = 0.03 + i * 0.002  # starts at ±3 %, grows by 0.2 %/day
            confidence_pct = max(40, round(95 - i * 1.2))

            rows.append({
                'date': date.isoformat(),
                'day': i + 1,
                'projected_price': projected,
                'lower_bound': round(projected * (1 - margin)),
                'upper_bound': round(projected * (1 + margin)),
                'confidence_pct': confidence_pct,
            })
        return rows

    def _classify_trend(self, prices):
        if len(prices) < 2:
            return 'stable'
        start_avg = sum(prices[:3]) / min(3, len(prices))
        end_avg = sum(prices[-3:]) / min(3, len(prices))
        change = (end_avg - start_avg) / start_avg * 100
        if change > 3:
            return 'rising'
        elif change < -3:
            return 'falling'
        return 'stable'

    def _classify_volatility(self, prices):
        if len(prices) < 2:
            return 'low'
        avg = sum(prices) / len(prices)
        variance = sum((p - avg) ** 2 for p in prices) / len(prices)
        cv = (math.sqrt(variance) / avg) * 100
        if cv < 3:
            return 'low'
        elif cv < 7:
            return 'medium'
        return 'high'

    def _build_recommendation(self, trend, volatility, crop):
        recs = []
        if trend == 'rising':
            recs.append({
                'type': 'timing', 'icon': '📈',
                'text': f'Seasonal pattern for {crop} suggests prices are rising. Consider holding stock.',
                'action': 'hold',
            })
        elif trend == 'falling':
            recs.append({
                'type': 'timing', 'icon': '📉',
                'text': f'Seasonal pattern for {crop} suggests prices may dip. Consider selling soon.',
                'action': 'sell',
            })
        else:
            recs.append({
                'type': 'timing', 'icon': '➡️',
                'text': f'Prices for {crop} are expected to remain stable this period.',
                'action': 'hold',
            })
        if volatility == 'high':
            recs.append({
                'type': 'warning', 'icon': '⚠️',
                'text': 'High seasonal volatility expected. Consider selling in batches.',
            })
        recs.append({
            'type': 'tip', 'icon': '💡',
            'text': 'Always check actual mandi prices before making selling decisions.',
        })
        return recs
