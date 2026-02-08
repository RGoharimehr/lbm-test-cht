"""
Unit tests for lattice module
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lattice import D3Q19, lattice_d3q19


class TestD3Q19(unittest.TestCase):
    """Test cases for D3Q19 lattice."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lattice = D3Q19()
        
    def test_lattice_parameters(self):
        """Test basic lattice parameters."""
        self.assertEqual(self.lattice.Q, 19)
        self.assertEqual(self.lattice.D, 3)
        self.assertEqual(self.lattice.e.shape, (19, 3))
        self.assertEqual(self.lattice.w.shape, (19,))
        
    def test_weights_sum_to_one(self):
        """Test that weights sum to 1."""
        self.assertAlmostEqual(np.sum(self.lattice.w), 1.0)
        
    def test_opposite_directions(self):
        """Test opposite direction indices."""
        for i in range(self.lattice.Q):
            opp_i = self.lattice.opp[i]
            # e_i + e_opp_i should be zero
            self.assertTrue(np.allclose(
                self.lattice.e[i] + self.lattice.e[opp_i], 0
            ))
    
    def test_equilibrium_at_rest(self):
        """Test equilibrium distribution for fluid at rest."""
        rho = np.ones((10, 10, 10))
        u = np.zeros((10, 10, 10, 3))
        
        feq = self.lattice.get_equilibrium(rho, u)
        
        # At rest, f_eq = w_i * rho
        for i in range(self.lattice.Q):
            expected = self.lattice.w[i] * rho
            self.assertTrue(np.allclose(feq[:, :, :, i], expected))
    
    def test_macroscopic_conservation(self):
        """Test that macroscopic variables are conserved."""
        rho_in = np.ones((10, 10, 10)) * 1.5
        u_in = np.random.rand(10, 10, 10, 3) * 0.1
        
        # Get equilibrium
        feq = self.lattice.get_equilibrium(rho_in, u_in)
        
        # Recover macroscopic variables
        rho_out, u_out = self.lattice.get_macroscopic(feq)
        
        # Check conservation
        self.assertTrue(np.allclose(rho_in, rho_out))
        self.assertTrue(np.allclose(u_in, u_out, rtol=1e-6))
    
    def test_streaming(self):
        """Test streaming operation."""
        f = np.random.rand(10, 10, 10, 19)
        f_streamed = self.lattice.stream(f)
        
        # Shape should be preserved
        self.assertEqual(f.shape, f_streamed.shape)
        
        # Mass should be conserved (with periodic BC)
        self.assertAlmostEqual(np.sum(f), np.sum(f_streamed))


if __name__ == '__main__':
    unittest.main()
