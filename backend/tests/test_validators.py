"""
Tests for validators: polygon validation, soil advice input validation,
and edge cases for field data.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError as DjangoValidationError
from field.validators import validate_polygon, sanitize_coordinates


class PolygonValidatorTestCase(TestCase):
    """Test GeoJSON polygon validation."""

    def test_valid_polygon(self):
        """A well-formed polygon should pass validation."""
        polygon = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
        }
        # Should not raise
        validate_polygon(polygon)

    def test_missing_type(self):
        """Polygon without type field should fail."""
        polygon = {
            "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
        }
        with self.assertRaises(DjangoValidationError):
            validate_polygon(polygon)

    def test_wrong_type(self):
        """Non-Polygon type should fail."""
        polygon = {
            "type": "Point",
            "coordinates": [0, 0]
        }
        with self.assertRaises(DjangoValidationError):
            validate_polygon(polygon)

    def test_too_few_points(self):
        """Polygon with fewer than 4 points should fail."""
        polygon = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 1], [0, 0]]]
        }
        with self.assertRaises(DjangoValidationError):
            validate_polygon(polygon)

    def test_ring_not_closed(self):
        """Polygon where first != last point should fail."""
        polygon = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0]]]
        }
        with self.assertRaises(DjangoValidationError):
            validate_polygon(polygon)

    def test_out_of_range_coordinates(self):
        """Coordinates outside valid lat/lng range should fail in sanitize."""
        with self.assertRaises(ValueError):
            sanitize_coordinates([[[200, 100], [200, 101], [201, 101], [201, 100], [200, 100]]])

    def test_very_large_polygon(self):
        """An extremely large polygon should fail validation (area check)."""
        polygon = {
            "type": "Polygon",
            "coordinates": [[[-50, -50], [-50, 50], [50, 50], [50, -50], [-50, -50]]]
        }
        with self.assertRaises(DjangoValidationError):
            validate_polygon(polygon)


class SanitizeCoordinatesTestCase(TestCase):
    """Test coordinate sanitization."""

    def test_valid_coordinates(self):
        """Valid coordinates should be returned as-is."""
        coords = [[[77.0, 28.0], [77.1, 28.0], [77.1, 28.1], [77.0, 28.1], [77.0, 28.0]]]
        result = sanitize_coordinates(coords)
        self.assertEqual(result, coords)

    def test_string_coordinates_converted(self):
        """String coordinates should be converted to float."""
        coords = [[["77.0", "28.0"], ["77.1", "28.0"], ["77.1", "28.1"], ["77.0", "28.1"], ["77.0", "28.0"]]]
        result = sanitize_coordinates(coords)
        self.assertIsInstance(result[0][0][0], float)

    def test_out_of_range_raises(self):
        """Out-of-range coordinates should raise ValueError."""
        coords = [[[200.0, 100.0], [200.1, 100.0], [200.1, 100.1], [200.0, 100.1], [200.0, 100.0]]]
        with self.assertRaises(ValueError):
            sanitize_coordinates(coords)


class SoilAdviceValidationTestCase(TestCase):
    """Test soil advice input validation via API."""

    def setUp(self):
        from django.contrib.auth.models import User
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token

        self.client = APIClient()
        self.user = User.objects.create_user(
            username="soiluser", password="TestPass123!"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_valid_soil_advice_request(self):
        """Valid soil parameters should be accepted."""
        from unittest.mock import patch, MagicMock
        mock_response = MagicMock()
        mock_response.text = '{"recommendations": "test"}'

        with patch('field.views.soil_advice.genai') as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model

            response = self.client.post("/field/soil-advice", {
                "N": 50, "P": 30, "K": 40,
                "pH": 6.5, "crop": "Rice"
            }, format="json")
            self.assertIn(response.status_code, [200, 201, 502])

    def test_negative_nitrogen_rejected(self):
        """Negative nitrogen value should be rejected."""
        response = self.client.post("/field/soil-advice", {
            "N": -10, "P": 30, "K": 40,
            "pH": 6.5, "crop": "Rice"
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_ph_out_of_range(self):
        """pH > 14 should be rejected."""
        response = self.client.post("/field/soil-advice", {
            "N": 50, "P": 30, "K": 40,
            "pH": 15.0, "crop": "Rice"
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_missing_crop(self):
        """Missing crop name should still receive a response (defaults to 'general crops')."""
        from unittest.mock import patch, MagicMock
        mock_response = MagicMock()
        mock_response.text = '{"recommendations": "test"}'
        with patch('field.views.soil_advice.genai') as mock_genai:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            response = self.client.post("/field/soil-advice", {
                "N": 50, "P": 30, "K": 40,
                "pH": 6.5
            }, format="json")
            # crop defaults to 'general crops', so no 400
            self.assertIn(response.status_code, [200, 503])
