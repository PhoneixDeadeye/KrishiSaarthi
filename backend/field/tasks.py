"""
Celery tasks for background processing.
All tasks use actual model fields from field.models.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='field.tasks.update_weather_data')
def update_weather_data():
    """
    Update weather data for all active fields.
    Runs every 6 hours.
    """
    from field.models import FieldData
    import os
    import requests

    logger.info("Starting weather data update...")

    api_key = os.environ.get('OPENWEATHER_API_KEY')
    if not api_key:
        logger.warning("OPENWEATHER_API_KEY not set. Skipping weather update.")
        return 0

    fields = FieldData.objects.all()
    updated_count = 0

    for field in fields:
        try:
            polygon = field.polygon
            if not polygon:
                continue

            coords = polygon.get('coordinates', [])
            if not coords or not coords[0]:
                continue

            # Calculate centroid from GeoJSON polygon
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
                updated_count += 1

        except Exception as e:
            logger.error(f"Error updating weather for field {field.id}: {e}")
            continue

    logger.info(f"Weather update completed: {updated_count} fields updated")
    return updated_count


@shared_task(name='field.tasks.update_satellite_data')
def update_satellite_data():
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

        except Exception as e:
            logger.error(f"Error updating satellite data for field {field.id}: {e}")
            continue

    logger.info(f"Satellite data update completed: {updated_count} fields updated")
    return updated_count


@shared_task(name='field.tasks.calculate_risk_scores')
def calculate_risk_scores():
    """
    Calculate and update risk scores for all fields.
    Runs daily at 3 AM.
    """
    from field.models import FieldData
    from field.utils import fetchEEData
    from ml_engine.lstm import predict_risk_from_values

    logger.info("Starting risk score calculation...")

    fields = FieldData.objects.all()
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
                    updated_count += 1

        except Exception as e:
            logger.error(f"Error calculating risk for field {field.id}: {e}")
            continue

    logger.info(f"Risk calculation completed: {updated_count} fields updated")
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

            yesterday = timezone.now().date() - timedelta(days=1)
            daily_logs = FieldLog.objects.filter(
                user=user,
                date=yesterday
            )

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

        except Exception as e:
            logger.error(f"Error generating report for user {user.id}: {e}")
            continue

    logger.info(f"Daily reports completed: {reports_generated} reports generated")
    return reports_generated


@shared_task(name='field.tasks.cleanup_old_logs')
def cleanup_old_logs():
    """
    Clean up old logs and temporary data.
    Runs weekly on Sunday at 1 AM.
    """
    from field.models import FieldLog

    logger.info("Starting cleanup of old logs...")

    # Delete logs older than 2 years
    cutoff_date = timezone.now().date() - timedelta(days=730)

    deleted_count, _ = FieldLog.objects.filter(
        date__lt=cutoff_date
    ).delete()

    logger.info(f"Cleanup completed: {deleted_count} old logs deleted")
    return deleted_count


@shared_task(name='field.tasks.generate_field_analytics')
def generate_field_analytics(field_id, start_date=None, end_date=None):
    """
    Generate comprehensive analytics for a field.
    """
    from field.models import FieldData, FieldLog
    from django.db.models import Count

    logger.info(f"Generating analytics for field {field_id}")

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

        logger.info(f"Analytics generated for field {field_id}")
        return analytics

    except FieldData.DoesNotExist:
        logger.error(f"Field {field_id} not found")
        return {'error': f'Field {field_id} not found'}
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise
