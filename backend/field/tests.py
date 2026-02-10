from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import FieldData
from unittest.mock import patch, MagicMock
import os

class FieldDataModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_field_data_creation(self):
        field_data = FieldData.objects.create(
            user=self.user,
            polygon={"coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]},
            cropType="Wheat"
        )
        self.assertEqual(field_data.user, self.user)
        self.assertEqual(field_data.cropType, "Wheat")
        self.assertIsNotNone(field_data.polygon)

class FieldDataAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        FieldData.objects.create(
            user=self.user,
            polygon={"coordinates": [[[77.1, 28.5], [77.2, 28.5], [77.2, 28.6], [77.1, 28.6], [77.1, 28.5]]]},
            cropType="Rice"
        )

    def test_get_field_data_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/field/data') # Matching field/urls.py path structure usually prefixed with /api
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AnalyticsAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testanalytics', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.field = FieldData.objects.create(
            user=self.user,
            name="Test Field",
            cropType="Rice",
            polygon={"coordinates": [[[77.0, 28.0], [77.1, 28.0], [77.1, 28.1], [77.0, 28.1], [77.0, 28.0]]]}
        )
        self.ee_data_mock = {
            "ndvi_time_series": [{"date": "2023-01-01", "NDVI": 0.5}],
            "ndwi_time_series": [{"date": "2023-01-01", "NDWI": 0.2}],
            "NDVI": 0.5,
            "EVI": 0.4,
            "rainfall_mm": 10.0,
            "temperature_K": 300.0,
            "soil_moisture": 0.3
        }

    @patch('field.views.fetchEEData')
    def test_ee_analysis_view(self, mock_fetch):
        mock_fetch.return_value = self.ee_data_mock
        response = self.client.get(reverse('fieldAnalysis'), {'field_id': self.field.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['NDVI'], 0.5)

    @patch('field.views.fetchEEData')
    @patch('field.views.detect_awd_from_ndwi')
    def test_awd_report_view(self, mock_detect, mock_fetch):
        mock_fetch.return_value = self.ee_data_mock
        mock_detect.return_value = {"is_awd": True, "cycles_count": 2}
        
        response = self.client.get(reverse('AWDreport'), {'field_id': self.field.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_awd'])

    @patch('field.views.fetchEEData')
    @patch('field.views.calculate_carbon_metrics')
    def test_carbon_credit_view(self, mock_calc, mock_fetch):
        mock_fetch.return_value = self.ee_data_mock
        mock_calc.return_value = {"carbon_credits": 10.5, "area_hectare": 1.0}
        
        response = self.client.get(reverse('CarbonCredit'), {'field_id': self.field.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['carbon_credits'], 10.5)

    @patch('field.views.fetchEEData')
    @patch('field.views.get_health_score')
    def test_health_score_view(self, mock_score, mock_fetch):
        mock_fetch.return_value = self.ee_data_mock
        mock_score.return_value = {"score": 85, "rating": "Excellent"}
        
        response = self.client.get(reverse('HealthScore'), {'field_id': self.field.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85)

    @patch('requests.get')
    def test_weather_view(self, mock_get):
        # Mock current weather
        mock_resp_current = MagicMock()
        mock_resp_current.ok = True
        mock_resp_current.json.return_value = {"main": {"temp": 25}, "weather": [{"main": "Clear"}]}
        
        # Mock forecast
        mock_resp_forecast = MagicMock()
        mock_resp_forecast.ok = True
        mock_resp_forecast.json.return_value = {"list": []}

        mock_get.side_effect = [mock_resp_current, mock_resp_forecast]
        
        with patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'testkey'}):
            response = self.client.get(reverse('weather'), {'lat': 28.0, 'lon': 77.0})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['current']['main']['temp'], 25)


class SoilAdviceAPITest(TestCase):
    """Test Soil Advice endpoint with Gemini AI integration"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testsoil', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    @patch('field.views.soil_advice.genai.GenerativeModel')
    def test_soil_advice_success(self, mock_model_class):
        """Test successful soil advice request"""
        # Mock the Gemini response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''{
            "overall_status": "Moderate",
            "recommendations": [
                "Apply nitrogen fertilizer at 50 kg/ha",
                "Add phosphorus supplement"
            ],
            "fertilizer_suggestion": "NPK 20-10-10",
            "timing": "Before sowing",
            "caution": null
        }'''
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        response = self.client.post(
            reverse('soilAdvice'),
            {'N': 80, 'P': 40, 'K': 60, 'pH': 6.5, 'crop': 'rice'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['soil_values']['N'], 80)
        self.assertEqual(response.data['advice']['overall_status'], 'Moderate')
        self.assertIn('recommendations', response.data['advice'])
    
    def test_soil_advice_invalid_input(self):
        """Test soil advice with invalid input values"""
        response = self.client.post(
            reverse('soilAdvice'),
            {'N': 'invalid', 'P': 40, 'K': 60, 'pH': 6.5},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    @patch('field.views.soil_advice.genai.GenerativeModel')
    def test_soil_advice_ai_error_fallback(self, mock_model_class):
        """Test fallback when AI service fails"""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        response = self.client.post(
            reverse('soilAdvice'),
            {'N': 80, 'P': 40, 'K': 60, 'pH': 6.5},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn('error', response.data)
    
    def test_soil_advice_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse('soilAdvice'),
            {'N': 80, 'P': 40, 'K': 60, 'pH': 6.5},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
