"""
Tests for improvements implemented across Phases 1-10.
Covers: task_lock, bulk mark-read, InsuranceClaimSerializer,
batch inference, DELETE 204, logging, ML registry, and more.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from datetime import timedelta
import json


# ─── Task Lock Decorator ─────────────────────────────────────────────────────

class TaskLockTestCase(TestCase):
    """Test the task_lock decorator prevents concurrent execution."""

    def setUp(self):
        cache.clear()

    def test_lock_prevents_concurrent_runs(self):
        from field.tasks import task_lock

        call_count = 0

        @task_lock(timeout=10)
        def my_task():
            nonlocal call_count
            call_count += 1
            return "done"

        # Manually occupy the lock
        cache.add('celery-lock-my_task', 'locked', 10)

        result = my_task()
        self.assertIsNone(result)
        self.assertEqual(call_count, 0)

    def test_lock_allows_run_when_free(self):
        from field.tasks import task_lock

        call_count = 0

        @task_lock(timeout=10)
        def my_task2():
            nonlocal call_count
            call_count += 1
            return "done"

        result = my_task2()
        self.assertEqual(result, "done")
        self.assertEqual(call_count, 1)

    def test_lock_released_after_completion(self):
        from field.tasks import task_lock

        @task_lock(timeout=10)
        def my_task3():
            return "ok"

        my_task3()
        # Lock should be released, so we can acquire it again
        self.assertTrue(cache.add('celery-lock-my_task3', 'x', 10))

    def tearDown(self):
        cache.clear()


# ─── Bulk Mark-All-Read Alerts ───────────────────────────────────────────────

class BulkMarkReadTestCase(TestCase):
    """Test PATCH /field/alerts/all marks all alerts as read."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='alertbulk', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        from field.models import FieldData, FieldAlert
        self.field = FieldData.objects.create(
            user=self.user, name='Alert Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )
        # Create 3 unread alerts
        for i in range(3):
            FieldAlert.objects.create(
                user=self.user, field=self.field,
                date=timezone.now().date(),
                message=f'Alert {i}', is_read=False,
            )

    def test_mark_all_read(self):
        from field.models import FieldAlert
        response = self.client.patch(
            '/field/alerts/all',
            json.dumps({'is_read': True}),
            content_type='application/json',
        )
        # Expect 200 with count
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('marked_read'), 3)

        # Verify all are actually read
        unread = FieldAlert.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread, 0)


# ─── Insurance Claim Serializer Validation ───────────────────────────────────

class InsuranceClaimSerializerTestCase(TestCase):
    """Test InsuranceClaimSerializer field validation."""

    def setUp(self):
        from field.models import FieldData
        self.user = User.objects.create_user(username='claimuser', password='testpass')
        self.field = FieldData.objects.create(
            user=self.user, name='Claim Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_valid_claim_data(self):
        from finance.serializers import InsuranceClaimSerializer
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'area_affected_acres': 2.5,
            'damage_date': '2026-01-10',
            'damage_description': 'Flood damage',
            'estimated_loss': 100000,
        }
        serializer = InsuranceClaimSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_negative_area_rejected(self):
        from finance.serializers import InsuranceClaimSerializer
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'area_affected_acres': -1,
            'damage_date': '2026-01-10',
            'damage_description': 'Flood',
            'estimated_loss': 100000,
        }
        serializer = InsuranceClaimSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('area_affected_acres', serializer.errors)

    def test_negative_estimated_loss_rejected(self):
        from finance.serializers import InsuranceClaimSerializer
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'area_affected_acres': 2.5,
            'damage_date': '2026-01-10',
            'damage_description': 'Flood',
            'estimated_loss': -500,
        }
        serializer = InsuranceClaimSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('estimated_loss', serializer.errors)

    def test_invalid_ifsc_rejected(self):
        from finance.serializers import InsuranceClaimSerializer
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'area_affected_acres': 2.5,
            'damage_date': '2026-01-10',
            'damage_description': 'Flood',
            'estimated_loss': 100000,
            'ifsc_code': 'INVALID',
        }
        serializer = InsuranceClaimSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ifsc_code', serializer.errors)

    def test_valid_ifsc_accepted(self):
        from finance.serializers import InsuranceClaimSerializer
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'area_affected_acres': 2.5,
            'damage_date': '2026-01-10',
            'damage_description': 'Flood',
            'estimated_loss': 100000,
            'ifsc_code': 'SBIN0001234',
        }
        serializer = InsuranceClaimSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


# ─── Configurable Log Retention ──────────────────────────────────────────────

class LogRetentionTestCase(TestCase):
    """Test that cleanup_old_logs respects settings.LOG_RETENTION_DAYS."""

    def setUp(self):
        self.user = User.objects.create_user(username='retuser', password='testpass')
        from field.models import FieldData, FieldLog
        self.field = FieldData.objects.create(
            user=self.user, name='Ret Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )
        # Create a log that is 100 days old
        FieldLog.objects.create(
            user=self.user, field=self.field,
            date=timezone.now().date() - timedelta(days=100),
            activity='watering', details='Old watering',
        )

    @override_settings(LOG_RETENTION_DAYS=90)
    def test_custom_retention_deletes_old(self):
        from field.tasks import cleanup_old_logs
        deleted = cleanup_old_logs()
        self.assertEqual(deleted, 1)

    @override_settings(LOG_RETENTION_DAYS=365)
    def test_longer_retention_keeps_log(self):
        from field.tasks import cleanup_old_logs
        deleted = cleanup_old_logs()
        self.assertEqual(deleted, 0)


# ─── Planning DELETE Endpoints Return 204 ────────────────────────────────────

class PlanningDelete204TestCase(TestCase):
    """Verify all planning DELETE endpoints return 204 No Content."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='del204user', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        from field.models import FieldData
        self.field = FieldData.objects.create(
            user=self.user, name='Del Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_labor_delete_204(self):
        from planning.models import LaborEntry
        entry = LaborEntry.objects.create(
            user=self.user, field=self.field,
            worker_name='Test', work_type='Sowing',
            hours_worked=8, hourly_rate=100, date=timezone.now().date(),
        )
        response = self.client.delete(f'/planning/labor/{entry.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_inventory_delete_204(self):
        from planning.models import InventoryItem
        item = InventoryItem.objects.create(
            user=self.user, name='Seeds', category='seeds',
            quantity=10, unit='kg',
        )
        response = self.client.delete(f'/planning/inventory/{item.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_calendar_delete_204(self):
        from planning.models import SeasonCalendar
        event = SeasonCalendar.objects.create(
            user=self.user, field=self.field,
            title='Sowing', activity_type='sowing',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=1),
        )
        response = self.client.delete(f'/planning/calendar/{event.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


# ─── Inventory Quantity Non-Negative Constraint ──────────────────────────────

class InventoryQuantityConstraintTestCase(TestCase):
    """Test that InventoryItem.quantity cannot go negative (DB constraint)."""

    def setUp(self):
        self.user = User.objects.create_user(username='invqty', password='testpass')

    def test_negative_quantity_rejected(self):
        from planning.models import InventoryItem
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            InventoryItem.objects.create(
                user=self.user, name='Bad Item', category='seeds',
                quantity=-5, unit='kg',
            )


# ─── ML Engine Registry ─────────────────────────────────────────────────────

class MLRegistryTestCase(TestCase):
    """Test ML model registry metadata and integrity checks."""

    def test_registry_lists_models(self):
        from ml_engine.registry import registry
        models = registry.list_models()
        self.assertIn('cnn_crop_health', models)
        self.assertIn('lstm_risk', models)
        self.assertIn('lstm_risk_scaler', models)

    def test_registry_status(self):
        from ml_engine.registry import registry
        stat = registry.status()
        for name in ('cnn_crop_health', 'lstm_risk', 'lstm_risk_scaler'):
            self.assertIn(name, stat)
            self.assertIn('version', stat[name])
            self.assertIn('file_exists', stat[name])

    def test_registry_integrity_check(self):
        from ml_engine.registry import registry
        results = registry.verify_integrity()
        self.assertIsInstance(results, dict)
        for name, ok in results.items():
            self.assertIsInstance(ok, bool)


# ─── Batch CNN Inference ─────────────────────────────────────────────────────

class BatchInferenceTestCase(TestCase):
    """Test predict_health_batch for multiple images."""

    def test_batch_with_missing_images(self):
        from ml_engine.cnn import predict_health_batch
        results = predict_health_batch(['/nonexistent/a.jpg', '/nonexistent/b.jpg'])
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIn('error', r)
            self.assertEqual(r['class'], 'Unknown')

    def test_batch_empty_list(self):
        from ml_engine.cnn import predict_health_batch
        results = predict_health_batch([])
        self.assertEqual(results, [])


# ─── Health Score Edge Cases ─────────────────────────────────────────────────

class HealthScoreEdgeCasesTestCase(TestCase):
    """Test health score with edge-case inputs."""

    def test_negative_ndvi(self):
        from ml_engine.health_score import compute_health_score
        # Negative NDVI should be clamped to 0
        score = compute_health_score(0.5, -0.5, 0.5)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_all_ones(self):
        from ml_engine.health_score import compute_health_score
        score = compute_health_score(1.0, 1.0, 0.0)
        self.assertAlmostEqual(score, 1.0, places=2)

    def test_all_zeros(self):
        from ml_engine.health_score import compute_health_score
        score = compute_health_score(0.0, 0.0, 1.0)
        self.assertAlmostEqual(score, 0.0, places=2)


# ─── Carbon Credits AWD Detection ───────────────────────────────────────────

class CarbonCreditsTestCase(TestCase):
    """Test carbon credit calculation with AWD detection."""

    def test_carbon_metrics_with_awd(self):
        from ml_engine.cc import calculate_carbon_metrics
        ndwi_series = [0.35, 0.32, 0.15, 0.12, 0.35, 0.38, 0.14, 0.36]
        result = calculate_carbon_metrics(
            area_hectare=2.0,
            ndwi_series=ndwi_series,
            crop_days=100,
        )
        self.assertIn('awd_detected', result)
        self.assertIn('co2e_reduction_ton', result)
        self.assertIn('estimated_value_inr', result)
        self.assertGreaterEqual(result['co2e_reduction_ton'], 0)

    def test_carbon_metrics_no_data(self):
        from ml_engine.cc import calculate_carbon_metrics
        result = calculate_carbon_metrics(
            area_hectare=1.0,
            ndwi_series=[],
        )
        self.assertIn('awd_detected', result)
        self.assertFalse(result['awd_detected'])


# ─── Logging Configuration ──────────────────────────────────────────────────

class LoggingConfigTestCase(TestCase):
    """Test that logging configuration loads without errors."""

    def test_logging_config_importable(self):
        from config.logging_config import LOGGING
        self.assertIn('version', LOGGING)
        self.assertEqual(LOGGING['version'], 1)
        self.assertIn('handlers', LOGGING)
        self.assertIn('loggers', LOGGING)

    def test_json_formatter(self):
        from config.logging_config import JSONFormatter
        import logging
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='', lineno=0,
            msg='Test message', args=(), exc_info=None,
        )
        output = formatter.format(record)
        import json as json_mod
        parsed = json_mod.loads(output)
        self.assertEqual(parsed['message'], 'Test message')
        self.assertEqual(parsed['level'], 'INFO')


# ─── Throttle Classes Exist ─────────────────────────────────────────────────

class ThrottleClassesTestCase(TestCase):
    """Test that all custom throttle classes are importable."""

    def test_all_throttles_importable(self):
        from config.throttling import (
            BurstRateThrottle,
            SustainedRateThrottle,
            AnonymousBurstRateThrottle,
            AnonymousSustainedRateThrottle,
            MLInferenceThrottle,
            GeminiChatThrottle,
            EarthEngineThrottle,
            LoginRateThrottle,
            PasswordResetThrottle,
        )
        self.assertEqual(MLInferenceThrottle.scope, 'ml_inference')
        self.assertEqual(GeminiChatThrottle.scope, 'gemini_chat')
        self.assertEqual(EarthEngineThrottle.scope, 'earth_engine')
        self.assertEqual(LoginRateThrottle.scope, 'login')
        self.assertEqual(PasswordResetThrottle.scope, 'password_reset')


# ─── Seed Schemes Management Command ────────────────────────────────────────

class SeedSchemesCommandTestCase(TestCase):
    """Test the seed_schemes management command."""

    def test_seed_schemes_creates_records(self):
        from django.core.management import call_command
        from finance.models import GovernmentScheme
        call_command('seed_schemes', verbosity=0)
        self.assertGreater(GovernmentScheme.objects.count(), 0)

    def test_seed_schemes_idempotent(self):
        from django.core.management import call_command
        from finance.models import GovernmentScheme
        call_command('seed_schemes', verbosity=0)
        count1 = GovernmentScheme.objects.count()
        call_command('seed_schemes', verbosity=0)
        count2 = GovernmentScheme.objects.count()
        self.assertEqual(count1, count2)


# ─── Revenue Auto-Recalculation ─────────────────────────────────────────────

class RevenueRecalcTestCase(TestCase):
    """Test that Revenue always recalculates total_amount."""

    def setUp(self):
        self.user = User.objects.create_user(username='revcalc', password='testpass')
        from finance.models import Season
        from field.models import FieldData
        self.field = FieldData.objects.create(
            user=self.user, name='Rev Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )
        self.season = Season.objects.create(
            user=self.user, name='Kharif 2026', season_type='kharif',
            year=2026, start_date='2026-06-01', end_date='2026-10-01',
            field=self.field,
        )

    def test_total_recalculated_even_when_zero(self):
        from finance.models import Revenue
        rev = Revenue.objects.create(
            user=self.user, field=self.field, season=self.season,
            crop='Rice', quantity_sold=100, price_per_unit=25,
            total_amount=0, date='2026-09-01',
        )
        # save() should have recalculated to 2500
        rev.refresh_from_db()
        self.assertEqual(rev.total_amount, 2500)


# ─── Schemes View Returns Setup Required ─────────────────────────────────────

class SchemesViewNoAutoSeedTestCase(TestCase):
    """Test that SchemesView no longer auto-seeds at runtime."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='schemuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_empty_schemes_returns_setup_hint(self):
        from finance.models import GovernmentScheme
        # Ensure no schemes exist
        GovernmentScheme.objects.all().delete()
        response = self.client.get('/finance/schemes')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should either have a setup_required hint or empty list
        total = data.get('total_schemes', len(data.get('schemes', [])))
        self.assertEqual(total, 0)
