"""
Unit tests for Shan-Chen forcing module
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.shan_chen import ShanChenForcing
from src.lattice import lattice_d3q19


class TestShanChen(unittest.TestCase):
    """Test cases for Shan-Chen forcing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.forcing = ShanChenForcing()
        
    def test_interaction_potential(self):
        """Test interaction potential calculation."""
        rho = np.ones((5, 5, 5))
        
        # Ideal gas potential
        psi = self.forcing.interaction_potential(rho, psi_type='ideal')
        self.assertTrue(np.allclose(psi, rho))
        
        # Constant potential
        psi = self.forcing.interaction_potential(rho, psi_type='constant')
        self.assertTrue(np.allclose(psi, 1.0))
    
    def test_force_calculation(self):
        """Test force calculation."""
        psi = np.ones((5, 5, 5))
        F = self.forcing.calculate_force(psi, G=-1.0)
        
        # Check shape
        self.assertEqual(F.shape, (5, 5, 5, 3))
        
        # For uniform density, force should be small (periodic BC)
        self.assertTrue(np.allclose(F, 0, atol=1e-10))
    
    def test_guo_forcing_velocity(self):
        """Test Guo forcing velocity modification."""
        u = np.zeros((5, 5, 5, 3))
        F = np.ones((5, 5, 5, 3)) * 0.1
        rho = np.ones((5, 5, 5))
        tau = 1.0
        
        u_eq = self.forcing.guo_forcing_velocity(u, F, rho, tau)
        
        # Modified velocity should be u + tau*F/rho
        expected = u + tau * F / rho[:, :, :, np.newaxis]
        self.assertTrue(np.allclose(u_eq, expected))
    
    def test_forcing_term_shape(self):
        """Test forcing term has correct shape."""
        F = np.ones((5, 5, 5, 3)) * 0.1
        u = np.zeros((5, 5, 5, 3))
        
        S = self.forcing.forcing_term(F, u, force_scheme='guo')
        
        # Should have shape (nx, ny, nz, Q)
        self.assertEqual(S.shape, (5, 5, 5, 19))


if __name__ == '__main__':
    unittest.main()
