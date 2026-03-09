"""
Planning & Irrigation Tests for KrishiSaarthi
Tests planning CRUD, calendar, irrigation, and field log/alert operations.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from field.models import FieldData, FieldLog, FieldAlert
import json


class SeasonCalendarTestCase(TestCase):
    """Test season calendar CRUD"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='caluser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_list_calendar(self):
        """Test listing calendar events"""
        response = self.client.get('/planning/calendar', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_create_calendar_event(self):
        """Test creating a calendar event"""
        field = FieldData.objects.create(
            user=self.user, name='Cal Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )
        data = {
            'field': field.id,
            'title': 'Sowing Day',
            'start_date': '2026-06-15',
            'end_date': '2026-06-15',
            'activity_type': 'sowing',
            'status': 'planned'
        }
        response = self.client.post(
            '/planning/calendar',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])

    def test_calendar_requires_auth(self):
        """Test calendar requires authentication"""
        response = self.client.get('/planning/calendar')
        self.assertEqual(response.status_code, 401)


class InventoryTestCase(TestCase):
    """Test inventory management"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='invuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_list_inventory(self):
        """Test listing inventory items"""
        response = self.client.get('/planning/inventory', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_create_inventory_item(self):
        """Test creating inventory item"""
        data = {
            'name': 'NPK Fertilizer',
            'category': 'fertilizer',
            'quantity': 50,
            'unit': 'kg',
            'reorder_level': 10
        }
        response = self.client.post(
            '/planning/inventory',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])


class LaborTestCase(TestCase):
    """Test labor management"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='labuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_list_labor(self):
        """Test listing labor entries"""
        response = self.client.get('/planning/labor', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_create_labor_entry(self):
        """Test creating a labor entry"""
        field = FieldData.objects.create(
            user=self.user, name='Labor Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )
        data = {
            'field': field.id,
            'worker_name': 'Ram Singh',
            'work_type': 'Harvesting',
            'date': '2026-02-15',
            'hours_worked': 8,
            'hourly_rate': 100
        }
        response = self.client.post(
            '/planning/labor',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])


class EquipmentTestCase(TestCase):
    """Test equipment management"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='equipuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_list_equipment(self):
        """Test listing equipment"""
        response = self.client.get('/planning/equipment', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_create_equipment(self):
        """Test creating equipment"""
        data = {
            'name': 'Tractor',
            'equipment_type': 'vehicle',
            'status': 'available'
        }
        response = self.client.post(
            '/planning/equipment',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])


class FieldLogTestCase(TestCase):
    """Test field log operations"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='loguser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
        self.field = FieldData.objects.create(
            user=self.user, name='Log Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_list_field_logs(self):
        """Test listing field logs"""
        response = self.client.get('/field/logs', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_create_field_log(self):
        """Test creating a field log entry"""
        data = {
            'field_id': self.field.id,
            'activity': 'watering',
            'details': 'Irrigated the entire field',
            'date': '2026-02-28'
        }
        response = self.client.post(
            '/field/logs',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])

    def test_field_logs_require_auth(self):
        """Test field logs require authentication"""
        response = self.client.get('/field/logs')
        self.assertEqual(response.status_code, 401)


class FieldAlertTestCase(TestCase):
    """Test field alert operations"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alertuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_list_field_alerts(self):
        """Test listing field alerts"""
        response = self.client.get('/field/alerts', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_field_alerts_require_auth(self):
        """Test field alerts require authentication"""
        response = self.client.get('/field/alerts')
        self.assertEqual(response.status_code, 401)


class IrrigationTestCase(TestCase):
    """Test irrigation endpoints"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='irriguser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_irrigation_logs_list(self):
        """Test listing irrigation logs"""
        response = self.client.get('/field/irrigation-logs', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_irrigation_requires_auth(self):
        """Test irrigation endpoints require authentication"""
        response = self.client.get('/field/irrigation-logs')
        self.assertEqual(response.status_code, 401)

    def test_irrigation_schedule_requires_auth(self):
        """Test irrigation schedule requires authentication"""
        response = self.client.post('/field/irrigation-schedule')
        self.assertEqual(response.status_code, 401)


class WeatherTestCase(TestCase):
    """Test weather endpoint"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='weatheruser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_weather_requires_auth(self):
        """Test weather endpoint requires authentication"""
        response = self.client.get('/field/weather?lat=28.5&lon=77.5')
        self.assertEqual(response.status_code, 401)

    def test_weather_missing_params(self):
        """Test weather returns 400 without lat/lon"""
        response = self.client.get('/field/weather', **self.auth)
        self.assertEqual(response.status_code, 400)


class RotationPlannerTestCase(TestCase):
    """Test rotation planner endpoint"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='rotuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_rotation_planner(self):
        """Test rotation planner returns data"""
        response = self.client.get('/planning/rotation', **self.auth)
        # 200 with data or 400 if field_id required
        self.assertIn(response.status_code, [200, 400])

    def test_rotation_requires_auth(self):
        """Test rotation requires authentication"""
        response = self.client.get('/planning/rotation')
        self.assertEqual(response.status_code, 401)
