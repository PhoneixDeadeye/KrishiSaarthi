"""
Celery Tasks Tests for KrishiSaarthi
Tests background task logic without requiring external services.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from field.models import FieldData, FieldLog, FieldAlert
from django.utils import timezone
from datetime import timedelta


class WeatherTaskTestCase(TestCase):
    """Test weather update task"""

    def setUp(self):
        self.user = User.objects.create_user(username='taskuser', password='testpass')
        self.field = FieldData.objects.create(
            user=self.user, name='Task Field', cropType='Rice',
            polygon={
                'type': 'Polygon',
                'coordinates': [[[77.5, 28.5], [77.51, 28.5], [77.51, 28.51], [77.5, 28.51], [77.5, 28.5]]]
            }
        )

    @patch.dict('os.environ', {'OPENWEATHER_API_KEY': ''})
    def test_weather_task_skips_without_api_key(self):
        """Test that weather task skips gracefully without API key"""
        from field.tasks import update_weather_data
        result = update_weather_data()
        self.assertEqual(result, 0)

    @patch('requests.get')
    @patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'test-key'})
    def test_weather_task_handles_api_error(self, mock_get):
        """Test that weather task handles API errors"""
        mock_get.return_value = MagicMock(status_code=500)
        from field.tasks import update_weather_data
        result = update_weather_data()
        self.assertEqual(result, 0)

    def test_weather_task_skips_fields_with_empty_polygon(self):
        """Test that weather task skips fields with empty polygon coordinates"""
        self.field.polygon = {'type': 'Polygon', 'coordinates': []}
        self.field.save()
        
        with patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'test-key'}):
            from field.tasks import update_weather_data
            result = update_weather_data()
            self.assertEqual(result, 0)


class DailyReportTaskTestCase(TestCase):
    """Test daily report generation task"""

    def setUp(self):
        self.user = User.objects.create_user(username='reportuser', password='testpass')
        self.field = FieldData.objects.create(
            user=self.user, name='Report Field', cropType='Wheat',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_daily_reports_generates_alerts_for_inactive_fields(self):
        """Test that daily reports create alerts for fields with no recent activity"""
        # Create a log from 10 days ago
        old_date = timezone.now().date() - timedelta(days=10)
        FieldLog.objects.create(
            user=self.user,
            field=self.field,
            activity='Watering',
            details='Old activity',
            date=old_date
        )

        from field.tasks import generate_daily_reports
        result = generate_daily_reports()
        self.assertGreaterEqual(result, 1)

        # Check alert was created
        alerts = FieldAlert.objects.filter(user=self.user, field=self.field)
        self.assertTrue(alerts.exists())

    def test_daily_reports_skips_users_without_fields(self):
        """Test that report generation skips users without fields"""
        # Create a user with no fields
        User.objects.create_user(username='empty_user', password='testpass')
        
        from field.tasks import generate_daily_reports
        result = generate_daily_reports()
        # Should still complete without error
        self.assertIsInstance(result, int)


class CleanupTaskTestCase(TestCase):
    """Test cleanup task"""

    def setUp(self):
        self.user = User.objects.create_user(username='cleanupuser', password='testpass')
        self.field = FieldData.objects.create(
            user=self.user, name='Cleanup Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_cleanup_deletes_old_logs(self):
        """Test that cleanup removes logs older than 2 years"""
        old_date = timezone.now().date() - timedelta(days=800)
        FieldLog.objects.create(
            user=self.user,
            field=self.field,
            activity='Watering',
            details='Very old log',
            date=old_date
        )

        from field.tasks import cleanup_old_logs
        deleted = cleanup_old_logs()
        self.assertEqual(deleted, 1)
        self.assertEqual(FieldLog.objects.filter(user=self.user).count(), 0)

    def test_cleanup_keeps_recent_logs(self):
        """Test that cleanup preserves recent logs"""
        FieldLog.objects.create(
            user=self.user,
            field=self.field,
            activity='Watering',
            details='Recent log',
            date=timezone.now().date()
        )

        from field.tasks import cleanup_old_logs
        deleted = cleanup_old_logs()
        self.assertEqual(deleted, 0)
        self.assertEqual(FieldLog.objects.filter(user=self.user).count(), 1)


class AnalyticsTaskTestCase(TestCase):
    """Test analytics generation task"""

    def setUp(self):
        self.user = User.objects.create_user(username='analyticsuser', password='testpass')
        self.field = FieldData.objects.create(
            user=self.user, name='Analytics Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_generate_analytics_for_existing_field(self):
        """Test analytics generation for a valid field"""
        from field.tasks import generate_field_analytics
        result = generate_field_analytics(self.field.id)
        self.assertIn('field_id', result)
        self.assertEqual(result['field_name'], 'Analytics Field')

    def test_generate_analytics_for_missing_field(self):
        """Test analytics returns error for non-existent field"""
        from field.tasks import generate_field_analytics
        result = generate_field_analytics(99999)
        self.assertIn('error', result)
