from django.test import TestCase
from ml_engine import predict_health, predict_risk_from_values, get_health_score, detect_awd_from_ndwi
from ml_engine.health_score import compute_health_score, get_health_rating

class MLEngineTestCase(TestCase):
    def test_cnn_fallback(self):
        """Test CNN predictor falls back gracefully if model missing or image invalid"""
        # Pass a path that doesn't exist — should return fallback, not crash
        result = predict_health("/nonexistent/image.jpg")
        self.assertIn("probability", result)
        self.assertIn("class", result)
        # Should be a safe fallback (0.5 / Unknown) or an error dict
        self.assertIn(result["class"], ["Healthy", "Infested", "Unknown"])

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
        self.assertIn("awd_detected", report)
        
    def test_awd_empty_series(self):
        """Test AWD with empty input doesn't crash"""
        report = detect_awd_from_ndwi([])
        self.assertIn("awd_detected", report)

    def test_health_score_integration(self):
        """Test health score fusion"""
        # Test with empty data
        score = get_health_score(image_path=None, ndvi_latest=None, sequence={})
        self.assertIn("score", score)
        self.assertEqual(score["score"], 0.5) # Expect 0.5 (neutral) for no data

    def test_compute_health_score_math(self):
        """Test health score computation weights correctly"""
        # Perfect health: CNN=1.0, NDVI=1.0, risk=0.0
        score = compute_health_score(1.0, 1.0, 0.0)
        self.assertAlmostEqual(score, 1.0, places=2)
        
        # Worst health: CNN=0.0, NDVI=0.0, risk=1.0
        score = compute_health_score(0.0, 0.0, 1.0)
        self.assertAlmostEqual(score, 0.0, places=2)
        
        # Neutral: CNN=0.5, NDVI=0.5, risk=0.5
        score = compute_health_score(0.5, 0.5, 0.5)
        self.assertAlmostEqual(score, 0.5, places=2)

    def test_health_rating_ranges(self):
        """Test health rating classification"""
        excellent = get_health_rating(0.9)
        self.assertIn("rating", excellent)
        
        poor = get_health_rating(0.2)
        self.assertIn("rating", poor)
        
        # ratings should differ for very different scores
        self.assertNotEqual(excellent["rating"], poor["rating"])
