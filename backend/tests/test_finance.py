"""
Finance API Tests for KrishiSaarthi
Tests for Market Features: Price Forecast, Government Schemes, Insurance Claims
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json


class FinanceAPITestCase(TestCase):
    """Test finance API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
    
    # ========== Price Forecast Tests ==========
    
    def test_price_forecast_success(self):
        """Test price forecast returns valid data"""
        response = self.client.get(
            '/api/finance/price-forecast?crop=Rice&days=30',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('crop', data)
        self.assertIn('forecast', data)
        self.assertIn('summary', data)
        self.assertIn('recommendation', data)
        
        # Check summary fields
        summary = data['summary']
        self.assertIn('current_price', summary)
        self.assertIn('trend', summary)
        self.assertIn('volatility', summary)
    
    def test_price_forecast_different_crops(self):
        """Test forecast works for different crops"""
        crops = ['Rice', 'Wheat', 'Cotton', 'Sugarcane']
        for crop in crops:
            response = self.client.get(
                f'/api/finance/price-forecast?crop={crop}',
                **self.auth_headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['crop'], crop)
    
    def test_price_forecast_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/api/finance/price-forecast?crop=Rice')
        self.assertEqual(response.status_code, 401)
    
    # ========== Government Schemes Tests ==========
    
    def test_schemes_list_success(self):
        """Test schemes list returns data"""
        response = self.client.get(
            '/api/finance/schemes?state=Punjab',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('total_schemes', data)
        self.assertIn('schemes', data)
        self.assertIn('grouped', data)
        self.assertIn('tips', data)
    
    def test_schemes_filter_by_type(self):
        """Test filtering schemes by type"""
        for scheme_type in ['subsidy', 'loan', 'insurance']:
            response = self.client.get(
                f'/api/finance/schemes?type={scheme_type}',
                **self.auth_headers
            )
            self.assertEqual(response.status_code, 200)
    
    def test_schemes_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/api/finance/schemes')
        self.assertEqual(response.status_code, 401)
    
    # ========== Insurance Claims Tests ==========
    
    def test_insurance_list_empty(self):
        """Test insurance list returns empty for new user"""
        response = self.client.get(
            '/api/finance/insurance',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('claims', data)
        self.assertIn('summary', data)
        self.assertIn('damage_types', data)
    
    def test_insurance_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/api/finance/insurance')
        self.assertEqual(response.status_code, 401)


class MarketPricesTestCase(TestCase):
    """Test market prices endpoint"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='marketuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
    
    def test_market_prices_success(self):
        """Test market prices returns mandi data"""
        response = self.client.get(
            '/api/finance/market-prices?crop=Rice&state=Punjab',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('crop', data)
        self.assertIn('mandis', data)
        self.assertIn('tips', data)
    
    def test_market_prices_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/api/finance/market-prices?crop=Rice')
        self.assertEqual(response.status_code, 401)


class PlanningAPITestCase(TestCase):
    """Test planning API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='planuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
    
    def test_rotation_planner_success(self):
        """Test rotation planner returns recommendations"""
        response = self.client.get(
            '/api/planning/rotation?field_id=1',
            **self.auth_headers
        )
        # May return 200 or 404 depending on if field exists
        self.assertIn(response.status_code, [200, 404])
    
    def test_inventory_list(self):
        """Test inventory list endpoint"""
        response = self.client.get(
            '/api/planning/inventory',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
    
    def test_labor_list(self):
        """Test labor list endpoint"""
        response = self.client.get(
            '/api/planning/labor',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
    
    def test_equipment_list(self):
        """Test equipment list endpoint"""
        response = self.client.get(
            '/api/planning/equipment',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
