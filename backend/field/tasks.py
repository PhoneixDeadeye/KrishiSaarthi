"""
Celery tasks for background processing.
All tasks use actual model fields from field.models.
"""
from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Default log retention in days (configurable via Django settings)
LOG_RETENTION_DAYS = 730


def task_lock(timeout=600):
    """Decorator to prevent concurrent runs of the same task using Redis lock."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lock_id = f'celery-lock-{func.__name__}'
            acquired = cache.add(lock_id, 'locked', timeout)
            if not acquired:
                logger.info("Task %s skipped — already running.", func.__name__)
                return None
            try:
                return func(*args, **kwargs)
            finally:
                cache.delete(lock_id)
        return wrapper
    return decorator


@shared_task(
    name='field.tasks.update_weather_data',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    rate_limit='10/m',
)
def update_weather_data(self):
    """
    Update weather data for all active fields.
    Runs every 6 hours. Stores results in FieldLog entries.
    Delegates to _update_weather_data_impl which holds a Redis lock.
    """
    return _update_weather_data_impl(self)


@task_lock(timeout=1200)
def _update_weather_data_impl(self):
    from field.models import FieldData, FieldLog
    import os
    import requests

    logger.info("Starting weather data update...")

    api_key = os.environ.get('OPENWEATHER_API_KEY')
    if not api_key:
        logger.warning("OPENWEATHER_API_KEY not set. Skipping weather update.")
        return 0

    fields = FieldData.objects.select_related('user').all()
    updated_count = 0

    for field in fields:
        try:
            polygon = field.polygon
            if not polygon:
                continue

            coords = polygon.get('coordinates', [])
            if not coords or not coords[0]:
                continue

            ring = coords[0]
            lons = [p[0] for p in ring if len(p) >= 2]
            lats = [p[1] for p in ring if len(p) >= 2]
            if not lons or not lats:
                continue

            lat = sum(lats) / len(lats)
            lon = sum(lons) / len(lons)

            url = (
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            )
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                weather_data = response.json()
                temp = weather_data.get('main', {}).get('temp', 'N/A')
                humidity = weather_data.get('main', {}).get('humidity', 'N/A')
                description = weather_data.get('weather', [{}])[0].get('description', 'N/A')
                FieldLog.objects.create(
                    user=field.user,
                    field=field,
                    date=timezone.now().date(),
                    activity='other',
                    details=f"Weather update: {description}, Temp: {temp}\u00b0C, Humidity: {humidity}%",
                )
                updated_count += 1
            else:
                logger.warning("Weather API returned %d for field %d", response.status_code, field.id)

        except requests.exceptions.RequestException as exc:
            logger.error("Network error updating weather for field %d: %s", field.id, exc)
            continue
        except Exception as exc:
            logger.error("Error updating weather for field %d: %s", field.id, exc)
            continue

    logger.info("Weather update completed: %d fields updated", updated_count)
    return updated_count


@shared_task(
    name='field.tasks.update_satellite_data',
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def update_satellite_data(self):
    """
    Update satellite imagery and indices for all fields.
    Runs daily at 2 AM.
    """
    from field.models import FieldData
    from field.utils import fetchEEData

    logger.info("Starting satellite data update...")

    fields = FieldData.objects.all()
    updated_count = 0

    for field in fields:
        try:
            if not field.polygon:
                continue

            ee_data = fetchEEData(field_instance=field)
            if 'error' not in ee_data:
                updated_count += 1

        except Exception as exc:
            logger.error("Error updating satellite data for field %d: %s", field.id, exc)
            continue

    logger.info("Satellite data update completed: %d fields updated", updated_count)
    return updated_count


@shared_task(
    name='field.tasks.calculate_risk_scores',
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def calculate_risk_scores(self):
    """
    Calculate and update risk scores for all fields.
    Runs daily at 3 AM. Stores results in FieldAlert entries.
    """
    from field.models import FieldData, FieldAlert
    from field.utils import fetchEEData
    from ml_engine.lstm import predict_risk_from_values

    logger.info("Starting risk score calculation...")

    fields = FieldData.objects.select_related('user').all()
    updated_count = 0

    for field in fields:
        try:
            if not field.polygon:
                continue

            ee_data = fetchEEData(field_instance=field)
            if 'error' in ee_data:
                continue

            ndvi_series = ee_data.get('ndvi_time_series', [])
            if len(ndvi_series) >= 7:
                result = predict_risk_from_values(ee_data)
                if 'error' not in result or result.get('fallback'):
                    risk_level = result.get('risk_level', 'unknown')
                    risk_score = result.get('risk_score', 0)

                    # Store risk alert if score is concerning
                    if risk_score > 0.6:
                        FieldAlert.objects.get_or_create(
                            user=field.user,
                            field=field,
                            date=timezone.now().date(),
                            message=f"High risk detected for {field.name}: {risk_level} (score: {risk_score:.2f})",
                            defaults={'is_read': False},
                        )

                    updated_count += 1

        except Exception as exc:
            logger.error("Error calculating risk for field %d: %s", field.id, exc)
            continue

    logger.info("Risk calculation completed: %d fields updated", updated_count)
    return updated_count


@shared_task(name='field.tasks.generate_daily_reports')
def generate_daily_reports():
    """
    Generate daily summary reports for active fields.
    Runs daily at 6 AM.
    """
    from field.models import FieldData, FieldLog, FieldAlert
    from django.contrib.auth.models import User

    logger.info("Starting daily report generation...")

    users = User.objects.filter(is_active=True)
    reports_generated = 0

    for user in users:
        try:
            fields = FieldData.objects.filter(user=user)
            if not fields.exists():
                continue

            # Create auto-alerts for fields with no recent activity
            for field in fields:
                last_log = FieldLog.objects.filter(
                    user=user, field=field
                ).order_by('-date').first()

                if last_log:
                    days_since = (timezone.now().date() - last_log.date).days
                    if days_since >= 7:
                        FieldAlert.objects.get_or_create(
                            user=user,
                            field=field,
                            date=timezone.now().date(),
                            message=f"No activity logged for {field.name} in {days_since} days",
                            defaults={'is_read': False}
                        )

            reports_generated += 1

        except Exception as exc:
            logger.error("Error generating report for user %d: %s", user.id, exc)
            continue

    logger.info("Daily reports completed: %d reports generated", reports_generated)
    return reports_generated


@shared_task(name='field.tasks.cleanup_old_logs')
def cleanup_old_logs():
    """
    Clean up old logs and temporary data.
    Runs weekly on Sunday at 1 AM.
    """
    from field.models import FieldLog

    logger.info("Starting cleanup of old logs...")

    # Delete logs older than configured retention period
    from django.conf import settings
    retention_days = getattr(settings, 'LOG_RETENTION_DAYS', LOG_RETENTION_DAYS)
    cutoff_date = timezone.now().date() - timedelta(days=retention_days)

    deleted_count, _ = FieldLog.objects.filter(
        date__lt=cutoff_date
    ).delete()

    logger.info("Cleanup completed: %d old logs deleted", deleted_count)
    return deleted_count


@shared_task(name='field.tasks.generate_field_analytics')
def generate_field_analytics(field_id, start_date=None, end_date=None):
    """
    Generate comprehensive analytics for a field.
    """
    from field.models import FieldData, FieldLog
    from django.db.models import Count

    logger.info("Generating analytics for field %s", field_id)

    try:
        field = FieldData.objects.get(id=field_id)

        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()

        logs = FieldLog.objects.filter(
            field=field,
            date__range=[start_date, end_date]
        )

        analytics = {
            'field_id': field_id,
            'field_name': field.name,
            'crop_type': field.cropType,
            'period': f"{start_date} to {end_date}",
            'total_activities': logs.count(),
            'activity_breakdown': list(
                logs.values('activity').annotate(count=Count('id'))
            ),
        }

        logger.info("Analytics generated for field %s", field_id)
        return analytics

    except FieldData.DoesNotExist:
        logger.error("Field %s not found", field_id)
        return {'error': f'Field {field_id} not found'}
    except Exception as e:
        logger.error("Error generating analytics: %s", e)
        raise
