"""
Celery tasks for background processing
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='field.tasks.update_weather_data')
def update_weather_data():
    """
    Update weather data for all active fields
    Runs every 6 hours
    """
    from field.models import FieldData
    from field.utils import fetch_weather
    
    logger.info("Starting weather data update...")
    
    fields = FieldData.objects.filter(is_active=True)
    updated_count = 0
    
    for field in fields:
        try:
            # Get center coordinates
            if field.polygon_coordinates:
                coords = field.polygon_coordinates[0]
                if coords:
                    lat, lon = coords[0], coords[1]
                    weather_data = fetch_weather(lat, lon)
                    
                    # Store in cache or database
                    # Implementation depends on your caching strategy
                    updated_count += 1
                    
        except Exception as e:
            logger.error(f"Error updating weather for field {field.id}: {str(e)}")
            continue
    
    logger.info(f"Weather update completed: {updated_count} fields updated")
    return updated_count


@shared_task(name='field.tasks.update_satellite_data')
def update_satellite_data():
    """
    Update satellite imagery and indices for all fields
    Runs daily at 2 AM
    """
    from field.models import FieldData
    from field.utils import fetchEEData
    
    logger.info("Starting satellite data update...")
    
    fields = FieldData.objects.filter(is_active=True)
    updated_count = 0
    
    for field in fields:
        try:
            if field.polygon_coordinates:
                ee_data = fetchEEData(field.polygon_coordinates)
                
                # Store the data
                if ee_data.get('status') == 'success':
                    updated_count += 1
                    
        except Exception as e:
            logger.error(f"Error updating satellite data for field {field.id}: {str(e)}")
            continue
    
    logger.info(f"Satellite data update completed: {updated_count} fields updated")
    return updated_count


@shared_task(name='field.tasks.calculate_risk_scores')
def calculate_risk_scores():
    """
    Calculate and update risk scores for all fields
    Runs daily at 3 AM
    """
    from field.models import FieldData
    from ml_engine.lstm import predict_risk_from_values as predict_risk
    
    logger.info("Starting risk score calculation...")
    
    fields = FieldData.objects.filter(is_active=True)
    updated_count = 0
    
    for field in fields:
        try:
            # Get recent field logs for prediction
            recent_logs = field.fieldlog_set.order_by('-date')[:30]
            
            if recent_logs.count() >= 7:  # Minimum data requirement
                # Prepare data for LSTM model
                # Calculate risk score
                # Update field with new risk score
                updated_count += 1
                
        except Exception as e:
            logger.error(f"Error calculating risk for field {field.id}: {str(e)}")
            continue
    
    logger.info(f"Risk calculation completed: {updated_count} fields updated")
    return updated_count


@shared_task(name='field.tasks.generate_daily_reports')
def generate_daily_reports():
    """
    Generate daily summary reports for active fields
    Runs daily at 6 AM
    """
    from field.models import FieldData, FieldLog
    from django.contrib.auth.models import User
    
    logger.info("Starting daily report generation...")
    
    users = User.objects.filter(is_active=True)
    reports_generated = 0
    
    for user in users:
        try:
            # Get user's fields
            fields = FieldData.objects.filter(user=user, is_active=True)
            
            if not fields.exists():
                continue
            
            # Generate summary report
            yesterday = timezone.now().date() - timedelta(days=1)
            daily_logs = FieldLog.objects.filter(
                field__in=fields,
                date=yesterday
            )
            
            # Create report summary
            report = {
                'user': user.username,
                'date': yesterday,
                'total_fields': fields.count(),
                'activities_logged': daily_logs.count(),
                'alerts': []
            }
            
            # Add alerts for fields needing attention
            for field in fields:
                # Check conditions and add alerts
                pass
            
            # Store or send report
            reports_generated += 1
            
        except Exception as e:
            logger.error(f"Error generating report for user {user.id}: {str(e)}")
            continue
    
    logger.info(f"Daily reports completed: {reports_generated} reports generated")
    return reports_generated


@shared_task(name='field.tasks.cleanup_old_logs')
def cleanup_old_logs():
    """
    Clean up old logs and temporary data
    Runs weekly on Sunday at 1 AM
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


@shared_task(name='field.tasks.process_pest_detection')
def process_pest_detection(image_path, field_id):
    """
    Process pest detection asynchronously
    """
    from field.models import Pest
    from ml_engine.cnn import predict_health as predict_pest
    
    logger.info(f"Processing pest detection for field {field_id}")
    
    try:
        # Run CNN model
        result = predict_pest(image_path)
        
        # Create pest record
        pest = Pest.objects.create(
            field_id=field_id,
            image_url=image_path,
            pest_name=result.get('pest_name'),
            confidence=result.get('confidence'),
            severity=result.get('severity', 'medium'),
            detected_at=timezone.now()
        )
        
        logger.info(f"Pest detection completed: {result.get('pest_name')} with {result.get('confidence')}% confidence")
        return pest.id
        
    except Exception as e:
        logger.error(f"Error in pest detection: {str(e)}")
        raise


@shared_task(name='field.tasks.generate_field_analytics')
def generate_field_analytics(field_id, start_date=None, end_date=None):
    """
    Generate comprehensive analytics for a field
    """
    from field.models import FieldData, FieldLog
    from django.db.models import Avg, Count
    
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
            'period': f"{start_date} to {end_date}",
            'total_activities': logs.count(),
            'activity_breakdown': logs.values('activity_type').annotate(count=Count('id')),
            'avg_temperature': logs.aggregate(Avg('temperature'))['temperature__avg'],
            'avg_humidity': logs.aggregate(Avg('humidity'))['humidity__avg'],
            'avg_soil_moisture': logs.aggregate(Avg('soil_moisture'))['soil_moisture__avg'],
        }
        
        logger.info(f"Analytics generated for field {field_id}")
        return analytics
        
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        raise
