"""
Live data services for KrishiSaarthi finance module.

Fetches real-time agricultural market prices from data.gov.in,
government scheme news, and insurance updates.
"""

import logging
import time
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

# Free public API key from data.gov.in
DATA_GOV_IN_API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"

# Simple in-memory cache: { cache_key: (timestamp, data) }
_price_cache = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


def _cache_key(crop, state):
    return f"{crop or 'all'}:{state or 'all'}"


def fetch_live_mandi_prices(crop=None, state=None):
    """
    Fetches LIVE mandi prices from data.gov.in API.

    Returns a list of dicts with keys:
        crop, market, state, min_price, max_price, modal_price, arrival_date
    Returns None on failure (caller should use fallback).
    """
    key = _cache_key(crop, state)

    # Check cache first
    if key in _price_cache:
        cached_time, cached_data = _price_cache[key]
        if time.time() - cached_time < CACHE_TTL_SECONDS:
            logger.info("Returning cached mandi prices for %s", key)
            return cached_data

    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    params = {
        "api-key": DATA_GOV_IN_API_KEY,
        "format": "json",
        "limit": 50,
    }
    if crop:
        params["filters[commodity]"] = crop
    if state:
        params["filters[state]"] = state

    try:
        r = requests.get(url, params=params, timeout=4)
        if r.status_code == 200:
            data = r.json()
            records = data.get("records", [])
            if records:
                results = []
                for rec in records:
                    try:
                        results.append({
                            "crop": rec.get("commodity", ""),
                            "market": rec.get("market", ""),
                            "state": rec.get("state", ""),
                            "min_price": int(float(rec.get("min_price", 0))),
                            "max_price": int(float(rec.get("max_price", 0))),
                            "modal_price": int(float(rec.get("modal_price", 0))),
                            "arrival_date": rec.get("arrival_date", ""),
                        })
                    except (ValueError, TypeError):
                        continue
                if results:
                    _price_cache[key] = (time.time(), results)
                    logger.info("Fetched %d live records from data.gov.in", len(results))
                    return results
        logger.warning("data.gov.in returned status %s or no records", r.status_code)
    except requests.exceptions.Timeout:
        logger.warning("data.gov.in API timed out (4s limit)")
    except Exception as e:
        logger.error("Error fetching from data.gov.in: %s", e)

    return None


def fetch_live_market_prices(crop, state=None):
    """
    Fetches live market price news/context for a single crop.
    Used for the 'live_news' supplementary panel.
    Falls back to DuckDuckGo web search if data.gov.in fails.
    """
    # Try data.gov.in first
    try:
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": DATA_GOV_IN_API_KEY,
            "format": "json",
            "limit": 10,
            "filters[commodity]": crop,
        }
        if state:
            params["filters[state]"] = state

        r = requests.get(url, params=params, timeout=4)
        if r.status_code == 200:
            data = r.json()
            if "records" in data and len(data["records"]) > 0:
                results = []
                for record in data["records"]:
                    results.append({
                        "title": f"{record.get('commodity')} at {record.get('market')}, {record.get('state')}",
                        "body": (
                            f"Min: ₹{record.get('min_price')}/Q, "
                            f"Max: ₹{record.get('max_price')}/Q, "
                            f"Modal: ₹{record.get('modal_price')}/Q. "
                            f"Date: {record.get('arrival_date')}"
                        ),
                        "source": "data.gov.in",
                    })
                return results
    except Exception as e:
        logger.error("data.gov.in news fetch failed: %s", e)

    # Fallback to DuckDuckGo
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        query = f"{crop} current mandi market price {state if state else 'India'} today"
        results = list(ddgs.text(query, max_results=5))
        if results:
            return [
                {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "source": r.get("href", ""),
                }
                for r in results
            ]
    except Exception as e:
        logger.error("DuckDuckGo fallback also failed: %s", e)

    return None


def fetch_live_schemes(crop=None, state=None):
    """Fetches latest government agriculture schemes dynamically."""
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        query = f"latest agriculture government schemes subsidy {crop if crop else ''} {state if state else 'India'}"
        results = list(ddgs.news(query, max_results=5))
        if not results:
            results = list(ddgs.text(query, max_results=5))
        return [
            {
                "title": r.get("title", ""),
                "description": r.get("body", ""),
                "date": r.get("date", datetime.today().isoformat()),
                "source": r.get("url", r.get("href", "")),
            }
            for r in results
        ]
    except Exception as e:
        logger.error("Error fetching live schemes data: %s", e)
        return []


def fetch_live_insurance_policies():
    """Fetches latest PMFBY and crop insurance news/policies dynamically."""
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        query = "PMFBY crop insurance latest updates policies India"
        results = list(ddgs.news(query, max_results=5))
        if not results:
            results = list(ddgs.text(query, max_results=5))
        return [
            {
                "title": r.get("title", ""),
                "description": r.get("body", ""),
                "date": r.get("date", datetime.today().isoformat()),
                "source": r.get("url", r.get("href", "")),
            }
            for r in results
        ]
    except Exception as e:
        logger.error("Error fetching live insurance data: %s", e)
        return []
