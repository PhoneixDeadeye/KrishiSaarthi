"""
Finance API Tests for KrishiSaarthi
Tests for Market Features: Price Forecast, Government Schemes, Insurance Claims
Updated to match honest API responses (no fake data).
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
        """Test price forecast returns valid data with honesty flags"""
        response = self.client.get(
            '/finance/price-forecast?crop=Rice&days=30',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('crop', data)
        self.assertIn('forecast', data)
        self.assertIn('summary', data)
        self.assertIn('recommendation', data)
        
        # Honesty flags must be present
        self.assertIn('method', data)
        self.assertEqual(data['method'], 'rule_based_seasonal')
        self.assertIn('is_ml_prediction', data)
        self.assertFalse(data['is_ml_prediction'])
        self.assertIn('disclaimer', data)
        
        # Check summary fields use honest naming
        summary = data['summary']
        self.assertIn('start_price', summary)
        self.assertIn('trend', summary)
        self.assertIn('volatility', summary)
    
    def test_price_forecast_different_crops(self):
        """Test forecast works for different crops"""
        crops = ['Rice', 'Wheat', 'Onion', 'Tomato']
        for crop in crops:
            response = self.client.get(
                f'/finance/price-forecast?crop={crop}',
                **self.auth_headers
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['crop'], crop)
    
    def test_price_forecast_unknown_crop(self):
        """Test forecast handles unknown crops gracefully"""
        response = self.client.get(
            '/finance/price-forecast?crop=Mango',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        # Unknown crop should still return a result (with generic defaults)
    
    def test_price_forecast_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/finance/price-forecast?crop=Rice')
        self.assertEqual(response.status_code, 401)
    
    # ========== Government Schemes Tests ==========
    
    def test_schemes_list_success(self):
        """Test schemes list returns data"""
        response = self.client.get(
            '/finance/schemes?state=Punjab',
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
                f'/finance/schemes?type={scheme_type}',
                **self.auth_headers
            )
            self.assertEqual(response.status_code, 200)
    
    def test_schemes_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/finance/schemes')
        self.assertEqual(response.status_code, 401)
    
    # ========== Insurance Claims Tests ==========
    
    def test_insurance_list_empty(self):
        """Test insurance list returns empty for new user"""
        response = self.client.get(
            '/finance/insurance',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('claims', data)
        self.assertIn('summary', data)
        self.assertIn('damage_types', data)
    
    def test_insurance_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/finance/insurance')
        self.assertEqual(response.status_code, 401)


class MarketPricesTestCase(TestCase):
    """Test market prices endpoint - now returns honest MSP reference data"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='marketuser',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}
    
    def test_market_prices_success(self):
        """Test market prices returns honest MSP reference data"""
        response = self.client.get(
            '/finance/market-prices?crop=Rice&state=Punjab',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('prices', data)
        self.assertIn('tips', data)
        
        # Honesty flags
        self.assertIn('is_live_data', data)
        self.assertFalse(data['is_live_data'])
        self.assertIn('data_source', data)
        self.assertIn('disclaimer', data)
        
        # Prices list structure
        self.assertGreater(len(data['prices']), 0)
        first = data['prices'][0]
        self.assertIn('crop', first)
        self.assertIn('msp', first)
        self.assertIn('estimated_range', first)
    
    def test_market_prices_unknown_crop(self):
        """Test unknown crop returns all crops"""
        response = self.client.get(
            '/finance/market-prices?crop=Mango',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should still return data with all MSP prices
        self.assertIn('prices', data)
    
    def test_market_prices_requires_auth(self):
        """Test endpoint requires authentication"""
        response = self.client.get('/finance/market-prices?crop=Rice')
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
    
    def test_rotation_planner_no_field(self):
        """Test rotation planner returns 404 for non-existent field"""
        response = self.client.get(
            '/planning/rotation?field_id=99999',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 404)
    
    def test_inventory_list(self):
        """Test inventory list endpoint"""
        response = self.client.get(
            '/planning/inventory',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
    
    def test_labor_list(self):
        """Test labor list endpoint"""
        response = self.client.get(
            '/planning/labor',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
    
    def test_equipment_list(self):
        """Test equipment list endpoint"""
        response = self.client.get(
            '/planning/equipment',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)


class ChatAuthTestCase(TestCase):
    """Test chat endpoints require authentication"""
    
    def setUp(self):
        self.client = Client()
    
    def test_chat_requires_auth(self):
        """Test chat endpoint requires authentication"""
        response = self.client.post(
            '/api/a',
            json.dumps({'question': 'test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
    
    def test_chat_history_requires_auth(self):
        """Test chat history endpoint requires authentication"""
        response = self.client.get('/api/a/history/test_session')
        self.assertEqual(response.status_code, 401)
