"""
Unit tests for geometry generation module
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.geometry import GyroidGenerator, generate_gyroid


class TestGeometry(unittest.TestCase):
    """Test cases for geometry generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = GyroidGenerator(32, 32, 32)
        
    def test_gyroid_generation(self):
        """Test basic gyroid generation."""
        solid_mask = self.generator.generate_gyroid(threshold=0.0, scale=1.0)
        
        # Check shape
        self.assertEqual(solid_mask.shape, (32, 32, 32))
        
        # Check type
        self.assertEqual(solid_mask.dtype, bool)
        
        # Should have both solid and fluid regions
        self.assertTrue(np.any(solid_mask))
        self.assertTrue(np.any(~solid_mask))
    
    def test_porosity_calculation(self):
        """Test porosity calculation."""
        solid_mask = self.generator.generate_gyroid(threshold=0.0, scale=1.0)
        porosity = self.generator.calculate_porosity(solid_mask)
        
        # Porosity should be between 0 and 1
        self.assertGreater(porosity, 0)
        self.assertLess(porosity, 1)
    
    def test_threshold_adjustment(self):
        """Test threshold adjustment for target porosity."""
        # Use larger domain for more accurate threshold adjustment
        gen_large = GyroidGenerator(64, 64, 64)
        target_porosity = 0.5  # More achievable target
        threshold, solid_mask = gen_large.adjust_threshold_for_porosity(
            target_porosity, scale=1.0, tolerance=0.1, max_iterations=20
        )
        
        actual_porosity = gen_large.calculate_porosity(solid_mask)
        
        # Should be reasonably close to target
        self.assertAlmostEqual(actual_porosity, target_porosity, delta=0.15)
    
    def test_channel_generation(self):
        """Test channel geometry generation."""
        solid_mask = self.generator.generate_channel(channel_height=20)
        
        # Check that there are walls at top and bottom
        self.assertTrue(np.all(solid_mask[:, :, 0]))  # Bottom wall
        self.assertTrue(np.all(solid_mask[:, :, -1]))  # Top wall
        
        # Check that there is fluid in the middle
        mid_z = solid_mask.shape[2] // 2
        self.assertTrue(np.any(~solid_mask[:, :, mid_z]))
    
    def test_sphere_generation(self):
        """Test sphere generation."""
        center = (16, 16, 16)
        radius = 8
        solid_mask = self.generator.generate_sphere(center=center, radius=radius)
        
        # Center should be solid
        self.assertTrue(solid_mask[center])
        
        # Point far from center should be fluid
        self.assertFalse(solid_mask[0, 0, 0])
    
    def test_convenience_function(self):
        """Test convenience function for gyroid generation."""
        solid_mask = generate_gyroid(32, 32, 32, threshold=0.0, scale=1.0)
        
        self.assertEqual(solid_mask.shape, (32, 32, 32))
        self.assertEqual(solid_mask.dtype, bool)


if __name__ == '__main__':
    unittest.main()
