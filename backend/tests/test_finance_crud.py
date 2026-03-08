"""
Comprehensive Finance CRUD Tests for KrishiSaarthi
Tests cost, revenue, season, and P&L operations.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from field.models import FieldData
import json


class CostCRUDTestCase(TestCase):
    """Test finance cost CRUD operations"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='costuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
        self.field = FieldData.objects.create(
            user=self.user, name='Cost Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_create_cost(self):
        """Test creating a cost entry"""
        data = {
            'field': self.field.id,
            'category': 'seeds',
            'amount': 5000,
            'description': 'Wheat seeds',
            'date': '2026-01-15'
        }
        response = self.client.post(
            '/finance/costs',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])

    def test_list_costs(self):
        """Test listing costs"""
        response = self.client.get('/finance/costs', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_cost_summary(self):
        """Test cost summary endpoint"""
        response = self.client.get('/finance/costs/summary', **self.auth)
        self.assertEqual(response.status_code, 200)

    def test_costs_require_auth(self):
        """Test costs require authentication"""
        response = self.client.get('/finance/costs')
        self.assertEqual(response.status_code, 401)


class RevenueCRUDTestCase(TestCase):
    """Test finance revenue CRUD operations"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='revuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
        self.field = FieldData.objects.create(
            user=self.user, name='Revenue Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_create_revenue(self):
        """Test creating a revenue entry"""
        data = {
            'field': self.field.id,
            'crop': 'Rice',
            'quantity_sold': 1000,
            'price_per_unit': 25,
            'total_amount': 25000,
            'unit': 'kg',
            'date': '2026-03-01'
        }
        response = self.client.post(
            '/finance/revenue',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])

    def test_list_revenue(self):
        """Test listing revenue"""
        response = self.client.get('/finance/revenue', **self.auth)
        self.assertEqual(response.status_code, 200)


class SeasonCRUDTestCase(TestCase):
    """Test finance season CRUD operations"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='seasonuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_list_seasons(self):
        """Test listing seasons"""
        response = self.client.get('/finance/seasons', **self.auth)
        self.assertEqual(response.status_code, 200)


class PnLDashboardTestCase(TestCase):
    """Test P&L dashboard endpoint"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='pnluser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_pnl_dashboard(self):
        """Test P&L dashboard returns structured data"""
        response = self.client.get('/finance/pnl', **self.auth)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('summary', data)
        self.assertIn('total_costs', data['summary'])
        self.assertIn('total_revenue', data['summary'])

    def test_pnl_requires_auth(self):
        """Test P&L requires authentication"""
        response = self.client.get('/finance/pnl')
        self.assertEqual(response.status_code, 401)


class InsuranceClaimCRUDTestCase(TestCase):
    """Test insurance claim CRUD operations"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='insuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
        self.field = FieldData.objects.create(
            user=self.user, name='Insurance Field', cropType='Rice',
            polygon={'type': 'Polygon', 'coordinates': [[[77.5, 28.5]]]}
        )

    def test_create_insurance_claim(self):
        """Test creating an insurance claim"""
        data = {
            'field_id': self.field.id,
            'crop': 'Rice',
            'damage_type': 'flood',
            'area_affected_acres': 2.5,
            'damage_date': '2026-01-10',
            'damage_description': 'Flood damage to rice crop',
            'estimated_loss': 100000
        }
        response = self.client.post(
            '/finance/insurance',
            json.dumps(data),
            content_type='application/json',
            **self.auth
        )
        self.assertIn(response.status_code, [200, 201])

    def test_list_insurance_claims(self):
        """Test listing insurance claims"""
        response = self.client.get('/finance/insurance', **self.auth)
        self.assertEqual(response.status_code, 200)
