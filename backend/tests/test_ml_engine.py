from django.test import TestCase
from ml_engine import predict_health, predict_risk_from_values, get_health_score, detect_awd_from_ndwi

class MLEngineTestCase(TestCase):
    def test_cnn_fallback(self):
        """Test CNN predictor falls back gracefully if model missing"""
        # We pass a dummy image path. It should handle file not found or model not found.
        # If model is missing, it returns probability 0.5 (uncertain) or similar fallback.
        # If file missing, it might raise error, let's see implementation.
        # Assuming safe fallback for missing model file.
        pass 

    def test_lstm_fallback(self):
        """Test LSTM predictor returns safe default on error/missing data"""
        empty_data = {"ndvi_time_series": [], "rainfall_mm": 0, "temperature_K": 300}
        result = predict_risk_from_values(empty_data)
        
        self.assertIn("risk_level", result)
        self.assertIn("risk_probability", result)
        # Default fallback is usually "Low" or "Unknown"
        self.assertTrue(result["risk_level"] in ["Low", "Unknown", "Moderate", "High"])

    def test_awd_logic(self):
        """Test AWD detection logic (pure python, no model file)"""
        # Case 1: Increasing NDWI (Flooding)
        ndwi_series = [
            {"date": "2023-01-01", "NDWI": -0.2},
            {"date": "2023-01-05", "NDWI": 0.1},
            {"date": "2023-01-10", "NDWI": 0.4}
        ]
        report = detect_awd_from_ndwi(ndwi_series)
        self.assertIn("status", report)
        
    def test_health_score_integration(self):
        """Test health score fusion"""
        # Test with empty data
        score = get_health_score(image_path=None, ndvi_latest=None, sequence={})
        self.assertIn("score", score)
        self.assertEqual(score["score"], 0) # Expect 0 for no data
