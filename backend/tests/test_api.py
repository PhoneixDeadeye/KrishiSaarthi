"""
API Integration Tests for KrishiSaarthi
Tests the main API endpoints to ensure they work correctly
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
        response = self.client.post('/api/signup/', self.test_user)
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.json())
        
        # Verify user was created
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_login(self):
        """Test user login"""
        # Create user first
        User.objects.create_user(**self.test_user)
        
        # Test login
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json())
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        User.objects.create_user(**self.test_user)
        
        response = self.client.post('/api/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 400)


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
        """Test creating a new field"""
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
            '/api/save-polygon/',
            json.dumps(field_data),
            content_type='application/json',
            **self.auth_header
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('field_id', response.json())
        
        # Verify field was created
        field = FieldData.objects.get(user=self.user)
        self.assertEqual(field.name, 'Test Field')
        self.assertEqual(field.cropType, 'Wheat')
    
    def test_list_fields(self):
        """Test listing user's fields"""
        # Create test field
        FieldData.objects.create(
            user=self.user,
            name='Field 1',
            cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )
        
        response = self.client.get('/api/fields/', **self.auth_header)
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
            f'/api/fields/delete/{field.id}/',
            **self.auth_header
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify field was deleted
        self.assertFalse(FieldData.objects.filter(id=field.id).exists())


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
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('database', data)
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
                'coordinates': [[]]  # Empty coordinates
            }
        }
        
        response = self.client.post(
            '/api/save-polygon/',
            json.dumps(invalid_field),
            content_type='application/json',
            **self.auth_header
        )
        
        self.assertNotEqual(response.status_code, 201)
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected"""
        incomplete_field = {
            'name': 'Incomplete Field'
            # Missing cropType and polygon
        }
        
        response = self.client.post(
            '/api/save-polygon/',
            json.dumps(incomplete_field),
            content_type='application/json',
            **self.auth_header
        )
        
        self.assertEqual(response.status_code, 400)
