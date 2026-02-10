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
