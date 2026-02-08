"""
Unit tests for MRT module
"""

import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mrt import MRT_D3Q19, mrt_d3q19
from src.lattice import lattice_d3q19


class TestMRT(unittest.TestCase):
    """Test cases for MRT collision operator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mrt = MRT_D3Q19()
        self.lattice = lattice_d3q19
        
    def test_transformation_matrix(self):
        """Test transformation matrix properties."""
        # M should be 19x19
        self.assertEqual(self.mrt.M.shape, (19, 19))
        
        # M * M_inv should be identity
        identity = np.dot(self.mrt.M, self.mrt.M_inv)
        self.assertTrue(np.allclose(identity, np.eye(19), atol=1e-10))
    
    def test_equilibrium_moments(self):
        """Test equilibrium moments calculation."""
        rho = np.ones((5, 5, 5)) * 1.0
        u = np.zeros((5, 5, 5, 3))
        
        meq = self.mrt.get_equilibrium_moments(rho, u)
        
        # Check shape
        self.assertEqual(meq.shape, (5, 5, 5, 19))
        
        # At rest, density moment should equal rho
        self.assertTrue(np.allclose(meq[:, :, :, 0], rho))
        
        # At rest, momentum moments should be zero
        self.assertTrue(np.allclose(meq[:, :, :, 3], 0))  # jx
        self.assertTrue(np.allclose(meq[:, :, :, 4], 0))  # jy
        self.assertTrue(np.allclose(meq[:, :, :, 5], 0))  # jz
    
    def test_collision_matrix(self):
        """Test collision matrix properties."""
        tau = 1.0
        S = self.mrt.get_collision_matrix(tau)
        
        # S should be 19x19 diagonal
        self.assertEqual(S.shape, (19, 19))
        self.assertTrue(np.allclose(S, np.diag(np.diag(S))))
        
        # Conserved moments should have zero relaxation
        self.assertEqual(S[0, 0], 0.0)  # density
        self.assertEqual(S[3, 3], 0.0)  # jx
        self.assertEqual(S[4, 4], 0.0)  # jy
        self.assertEqual(S[5, 5], 0.0)  # jz
    
    def test_collision_preserves_mass(self):
        """Test that MRT collision preserves mass."""
        f = np.random.rand(5, 5, 5, 19)
        rho, u = self.lattice.get_macroscopic(f)
        
        tau = 1.0
        S = self.mrt.get_collision_matrix(tau)
        
        f_post = self.mrt.collide(f, rho, u, S)
        
        # Total mass should be conserved
        mass_before = np.sum(f)
        mass_after = np.sum(f_post)
        
        self.assertAlmostEqual(mass_before, mass_after, places=10)


if __name__ == '__main__':
    unittest.main()
