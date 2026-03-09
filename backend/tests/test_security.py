"""
Security & Serializer Tests for KrishiSaarthi
Verifies password is write-only, auth is enforced, and data is properly validated.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from KrishiSaarthi.serializers import UserSerializer
import json


class UserSerializerSecurityTestCase(TestCase):
    """Test UserSerializer security properties"""

    def test_password_not_in_serialized_output(self):
        """CRITICAL: Password must never be returned in API responses"""
        user = User.objects.create_user(
            username='secureuser',
            email='secure@test.com',
            password='secretpassword123'
        )
        serializer = UserSerializer(instance=user)
        data = serializer.data

        self.assertNotIn('password', data)
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('email', data)

    def test_password_is_write_only(self):
        """Test that password field is write-only in serializer"""
        serializer = UserSerializer()
        field = serializer.fields['password']
        self.assertTrue(field.write_only)

    def test_signup_does_not_return_password(self):
        """Test that signup response does not contain password"""
        client = Client()
        response = client.post(
            '/signup',
            json.dumps({
                'username': 'nopwduser',
                'email': 'nopwd@test.com',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        # Check nested user object
        user_data = data.get('user', data)
        self.assertNotIn('password', user_data)

    def test_login_does_not_return_password(self):
        """Test that login response does not contain password"""
        User.objects.create_user(
            username='loginuser',
            password='testpass123'
        )
        client = Client()
        response = client.post(
            '/login',
            json.dumps({
                'username': 'loginuser',
                'password': 'testpass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        user_data = data.get('user', data)
        self.assertNotIn('password', user_data)


class EndpointAuthenticationTestCase(TestCase):
    """Test that all protected endpoints properly require authentication"""

    def setUp(self):
        self.client = Client()

    def _assert_requires_auth(self, method, url, data=None):
        """Helper to verify an endpoint returns 401 without auth"""
        kwargs = {}
        if data:
            kwargs['data'] = json.dumps(data)
            kwargs['content_type'] = 'application/json'

        if method == 'GET':
            response = self.client.get(url, **kwargs)
        elif method == 'POST':
            response = self.client.post(url, **kwargs)
        elif method == 'DELETE':
            response = self.client.delete(url, **kwargs)
        else:
            response = self.client.get(url, **kwargs)

        self.assertIn(
            response.status_code, [401, 403],
            f"{method} {url} should require auth but returned {response.status_code}"
        )

    def test_field_endpoints_require_auth(self):
        """Test all field endpoints require authentication"""
        self._assert_requires_auth('GET', '/field/data')
        self._assert_requires_auth('POST', '/field/set_polygon', {'name': 'Test'})
        self._assert_requires_auth('GET', '/field/ee')
        self._assert_requires_auth('GET', '/field/awd')
        self._assert_requires_auth('GET', '/field/cc')
        self._assert_requires_auth('GET', '/field/healthscore')
        self._assert_requires_auth('GET', '/field/logs')
        self._assert_requires_auth('GET', '/field/alerts')
        self._assert_requires_auth('GET', '/field/weather?lat=28&lon=77')
        self._assert_requires_auth('GET', '/field/irrigation-logs')
        self._assert_requires_auth('POST', '/field/irrigation-schedule')

    def test_finance_endpoints_require_auth(self):
        """Test all finance endpoints require authentication"""
        self._assert_requires_auth('GET', '/finance/costs')
        self._assert_requires_auth('GET', '/finance/revenue')
        self._assert_requires_auth('GET', '/finance/seasons')
        self._assert_requires_auth('GET', '/finance/pnl')
        self._assert_requires_auth('GET', '/finance/market-prices')
        self._assert_requires_auth('GET', '/finance/price-forecast?crop=Rice')
        self._assert_requires_auth('GET', '/finance/schemes')
        self._assert_requires_auth('GET', '/finance/insurance')

    def test_planning_endpoints_require_auth(self):
        """Test all planning endpoints require authentication"""
        self._assert_requires_auth('GET', '/planning/calendar')
        self._assert_requires_auth('GET', '/planning/inventory')
        self._assert_requires_auth('GET', '/planning/labor')
        self._assert_requires_auth('GET', '/planning/equipment')
        self._assert_requires_auth('GET', '/planning/rotation')

    def test_chat_endpoints_require_auth(self):
        """Test chat endpoints require authentication"""
        self._assert_requires_auth('POST', '/api/chat', {'question': 'test'})

    def test_public_endpoints_allow_anonymous(self):
        """Test that public endpoints work without auth"""
        # Health check should be public
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        # Login should be public (returns 401 for bad creds, not 403)
        response = self.client.post(
            '/login',
            json.dumps({'username': 'none', 'password': 'none'}),
            content_type='application/json'
        )
        # 401 = auth failed (endpoint is accessible), not 403 = forbidden
        self.assertIn(response.status_code, [401, 404])
