"""
KrishiSaarthi - Smart Agriculture Management Platform
"""
from __future__ import absolute_import, unicode_literals

# Import Celery app to ensure it's loaded when Django starts
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery not installed or configured, skip loading
    celery_app = None
    __all__ = ()
