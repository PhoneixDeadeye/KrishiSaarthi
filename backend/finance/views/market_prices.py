"""
Market Prices views for KrishiSaarthi.

Strategy: Try live data.gov.in API first → fallback to MSP-based estimates.
The response always includes a `data_source` field so the frontend can show
whether the user is seeing live mandi data or reference estimates.
"""

import logging
from collections import defaultdict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone

from ..services.live_data import fetch_live_mandi_prices, fetch_live_market_prices

logger = logging.getLogger(__name__)





def _build_live_prices(records, crop=None):
    """
    Aggregate live mandi records into per-crop price cards.
    Multiple mandi entries for the same crop are merged (min of mins, max of maxes).
    """
    grouped = defaultdict(lambda: {"mins": [], "maxes": [], "modals": []})
    for rec in records:
        name = rec["crop"]
        grouped[name]["mins"].append(rec["min_price"])
        grouped[name]["maxes"].append(rec["max_price"])
        grouped[name]["modals"].append(rec["modal_price"])

    cards = []
    for crop_name, vals in grouped.items():
        low = min(vals["mins"])
        high = max(vals["maxes"])
        # We no longer have static MSP_DATA to look up. 
        # Only using live APMC data.
        msp = None
        cards.append({
            "crop": crop_name,
            "msp": msp,
            "estimated_range": {"low": low, "high": high},
            "unit": "quintal",
        })
    return cards


class MarketPricesView(APIView):
    """
    GET: Returns market price data.
    Tries live data.gov.in API first, falls back to MSP-based estimates.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        crop = request.query_params.get("crop", None)
        state = request.query_params.get("state", None)

        try:
            # ---------- Try live API ----------
            live_records = fetch_live_mandi_prices(crop=crop, state=state)

            if live_records:
                price_cards = _build_live_prices(live_records, crop)
                data_source = "data.gov.in (Live Mandi Data)"
                is_live = True
                disclaimer = (
                    "Prices shown are live mandi arrival data from data.gov.in. "
                    "Cached for up to 1 hour. Always verify at your local APMC."
                )
                logger.info("Serving LIVE market prices (%d cards)", len(price_cards))
                
                return Response({
                    "date": timezone.now().date().isoformat(),
                    "state": state,
                    "data_source": data_source,
                    "is_live_data": is_live,
                    "disclaimer": disclaimer,
                    "prices": price_cards,
                    "live_news": fetch_live_market_prices(crop, state) if crop else None,
                    "tips": self._get_tips(crop),
                })
            else:
                return Response({
                    "error": "Live market data unavailable at this moment."
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error("Error in market prices: %s", e)
            return Response(
                {"error": "Failed to load market price data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_tips(self, crop):
        """Fetch custom market tips using Gemini"""
        import os
        import json
        import re
        import logging
        import google.generativeai as genai
        
        
        fallback_tips = []
        
        if crop:
            try:
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    prompt = f"""
                    You are an agricultural market expert in India. Give 2-3 dynamic, real-world actionable tips for selling '{crop}' right now. 
                    Consider seasonal timing, market trends, and where to sell. 

                    Respond correctly formatted in this exact JSON array structure (no markdown tags, no extra words):
                    [
                      {{ "type": "timing", "icon": "⏰", "text": "Short actionable tip max 120 chars." }}
                    ]

                    Valid types: "info", "tip", "msp", "timing". Valid icons: 📈, 💡, 🏛️, ⏰, etc.
                    """
                    
                    response = model.generate_content(prompt)
                    text = response.text.replace("```json", "").replace("```", "").strip()
                    
                    match = re.search(r"\[.*\]", text, re.DOTALL)
                    if match:
                        ai_tips = json.loads(match.group(0))
                        valid_tips = [t for t in ai_tips if isinstance(t, dict) and "type" in t and "icon" in t and "text" in t]
                        if valid_tips:
                            return valid_tips
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to generate dynamic tips with Gemini: {e}")

        return fallback_tips
