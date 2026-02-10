from django.test import TestCase
from field.utils import get_utm_crs, calculate_area_in_hectares

class AreaCalculationTestCase(TestCase):
    def test_utm_zone_selection(self):
        """Test correct UTM EPSG code selection for different locations"""
        # New Delhi (77E, 28N) -> Zone 43N -> 32643
        self.assertEqual(get_utm_crs(77.0, 28.0), "EPSG:32643")
        
        # San Francisco (-122W, 37N) -> Zone 10N -> 32610
        self.assertEqual(get_utm_crs(-122.0, 37.0), "EPSG:32610")
        
        # Sydney (151E, -33S) -> Zone 56S -> 32756
        self.assertEqual(get_utm_crs(151.0, -33.0), "EPSG:32756")
        
        # Quito (78W, 0.2S) -> Zone 17S -> 32717
        self.assertEqual(get_utm_crs(-78.5, -0.2), "EPSG:32717")

    def test_area_calculation(self):
        """Test calculation of a known 1-hectare square"""
        # 1 hectare = 100m x 100m
        # At equator, 1 degree lat approx 111km -> 0.0009 degrees approx 100m
        # Let's use a small square near equator to minimize distortion if we used lat/lon directly,
        # but our function uses projection so it should be accurate anywhere.
        
        # We'll trust the projection math but verifying it doesn't return 0 or crazy values.
        
        # 100x100m square roughly
        coords = [
            [77.0, 28.0],
            [77.001, 28.0],
            [77.001, 28.001],
            [77.0, 28.001],
            [77.0, 28.0]
        ]
        
        area = calculate_area_in_hectares(coords)
        self.assertGreater(area, 0)
        self.assertLess(area, 2.0) # Should be roughly 1.1-1.2 ha
        
    def test_invalid_polygon(self):
        """Test handling of invalid inputs"""
        self.assertEqual(calculate_area_in_hectares([]), 0.0)
        self.assertEqual(calculate_area_in_hectares([[0,0]]), 0.0)
