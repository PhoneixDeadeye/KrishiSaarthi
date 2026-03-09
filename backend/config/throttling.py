"""
Rate limiting configuration for Django REST Framework
Protects API endpoints from abuse
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """Allow burst of requests for authenticated users"""
    scope = 'burst'
    rate = '60/min'


class SustainedRateThrottle(UserRateThrottle):
    """Sustained rate limit for authenticated users"""
    scope = 'sustained'
    rate = '1000/day'


class AnonymousBurstRateThrottle(AnonRateThrottle):
    """Burst rate limit for anonymous users"""
    scope = 'anon_burst'
    rate = '20/min'


class AnonymousSustainedRateThrottle(AnonRateThrottle):
    """Sustained rate limit for anonymous users"""
    scope = 'anon_sustained'
    rate = '100/day'


# ----- Endpoint-specific throttles -----

class MLInferenceThrottle(UserRateThrottle):
    """Strict limit for expensive ML inference endpoints (pest detection, risk)"""
    scope = 'ml_inference'
    rate = '30/hour'


class GeminiChatThrottle(UserRateThrottle):
    """Limit for Gemini AI chat requests (token-costly)"""
    scope = 'gemini_chat'
    rate = '60/hour'


class EarthEngineThrottle(UserRateThrottle):
    """Limit for Google Earth Engine satellite data requests"""
    scope = 'earth_engine'
    rate = '20/hour'


class LoginRateThrottle(AnonRateThrottle):
    """Strict limit for login attempts to prevent brute-force"""
    scope = 'login'
    rate = '5/min'


class PasswordResetThrottle(AnonRateThrottle):
    """Strict limit for password reset requests"""
    scope = 'password_reset'
    rate = '3/hour'
