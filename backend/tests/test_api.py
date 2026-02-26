"""
API Integration Tests for KrishiSaarthi
Tests the main API endpoints to ensure they work correctly.
URLs match actual urls.py configuration.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from field.models import FieldData
import json


class AuthenticationTestCase(TestCase):
    """Test authentication endpoints"""

    def setUp(self):
        self.client = Client()
        self.test_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

    def test_signup(self):
        """Test user registration"""
        response = self.client.post(
            '/signup',
            json.dumps(self.test_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_signup_duplicate(self):
        """Test that duplicate signup fails"""
        User.objects.create_user(**self.test_user)
        response = self.client.post(
            '/signup',
            json.dumps(self.test_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        """Test user login"""
        User.objects.create_user(**self.test_user)

        response = self.client.post(
            '/login',
            json.dumps({
                'username': 'testuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())

    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        User.objects.create_user(**self.test_user)

        response = self.client.post(
            '/login',
            json.dumps({
                'username': 'testuser',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 404])


class FieldManagementTestCase(TestCase):
    """Test field management endpoints"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='farmer',
            password='farmerpass'
        )
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_create_field(self):
        """Test creating a new field via set_polygon"""
        field_data = {
            'name': 'Test Field',
            'cropType': 'Wheat',
            'polygon': {
                'type': 'Polygon',
                'coordinates': [[
                    [77.5, 28.5],
                    [77.51, 28.5],
                    [77.51, 28.51],
                    [77.5, 28.51],
                    [77.5, 28.5]
                ]]
            }
        }

        response = self.client.post(
            '/field/set_polygon',
            json.dumps(field_data),
            content_type='application/json',
            **self.auth_header
        )

        self.assertEqual(response.status_code, 200)

        field = FieldData.objects.get(user=self.user)
        self.assertEqual(field.name, 'Test Field')
        self.assertEqual(field.cropType, 'Wheat')

    def test_list_fields(self):
        """Test listing user's fields"""
        FieldData.objects.create(
            user=self.user,
            name='Field 1',
            cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

        response = self.client.get('/field/data', **self.auth_header)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Field 1')

    def test_delete_field(self):
        """Test deleting a field"""
        field = FieldData.objects.create(
            user=self.user,
            name='To Delete',
            cropType='Maize',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

        response = self.client.delete(
            f'/field/data/{field.id}',
            **self.auth_header
        )
        self.assertEqual(response.status_code, 204)

        self.assertFalse(FieldData.objects.filter(id=field.id).exists())

    def test_list_fields_unauthenticated(self):
        """Test that unauthenticated access is denied"""
        response = self.client.get('/field/data')
        self.assertIn(response.status_code, [401, 403])


class HealthCheckTestCase(TestCase):
    """Test health check endpoints"""

    def setUp(self):
        self.client = Client()

    def test_health_endpoint(self):
        """Test basic health check"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data['status'], 'healthy')

    def test_ready_endpoint(self):
        """Test readiness check"""
        response = self.client.get('/ready')
        # May be 200 or 503 depending on ML models / EE availability
        self.assertIn(response.status_code, [200, 503])

        data = response.json()
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
        self.assertIn('status', data)


class ValidationTestCase(TestCase):
    """Test input validation"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test', password='test')
        self.token = Token.objects.create(user=self.user)
        self.auth_header = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_invalid_polygon(self):
        """Test that invalid polygons are rejected"""
        invalid_field = {
            'name': 'Invalid Field',
            'cropType': 'Wheat',
            'polygon': {
                'type': 'Polygon',
                'coordinates': [[]]
            }
        }

        response = self.client.post(
            '/field/set_polygon',
            json.dumps(invalid_field),
            content_type='application/json',
            **self.auth_header
        )

        self.assertNotEqual(response.status_code, 200)

    def test_missing_required_fields(self):
        """Test that missing required fields are rejected"""
        incomplete_field = {
            'name': 'Incomplete Field'
        }

        response = self.client.post(
            '/field/set_polygon',
            json.dumps(incomplete_field),
            content_type='application/json',
            **self.auth_header
        )

        self.assertEqual(response.status_code, 400)
