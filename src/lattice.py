"""
D3Q19 Lattice Structure for Lattice Boltzmann Method

This module defines the D3Q19 lattice velocity set, weights, and connectivity
for both velocity and temperature fields.
"""

import numpy as np


class D3Q19:
    """
    D3Q19 lattice model for 3D Lattice Boltzmann Method.
    
    The D3Q19 model uses 19 discrete velocity directions:
    - 1 rest particle (0,0,0)
    - 6 face-connected neighbors (±1,0,0), (0,±1,0), (0,0,±1)
    - 12 edge-connected neighbors (±1,±1,0), (±1,0,±1), (0,±1,±1)
    """
    
    def __init__(self):
        """Initialize D3Q19 lattice parameters."""
        self.Q = 19  # Number of discrete velocities
        self.D = 3   # Number of dimensions
        
        # Lattice velocities (Q x D)
        self.e = np.array([
            [0, 0, 0],    # 0: rest
            [1, 0, 0],    # 1: +x
            [-1, 0, 0],   # 2: -x
            [0, 1, 0],    # 3: +y
            [0, -1, 0],   # 4: -y
            [0, 0, 1],    # 5: +z
            [0, 0, -1],   # 6: -z
            [1, 1, 0],    # 7: +x+y
            [-1, -1, 0],  # 8: -x-y
            [1, -1, 0],   # 9: +x-y
            [-1, 1, 0],   # 10: -x+y
            [1, 0, 1],    # 11: +x+z
            [-1, 0, -1],  # 12: -x-z
            [1, 0, -1],   # 13: +x-z
            [-1, 0, 1],   # 14: -x+z
            [0, 1, 1],    # 15: +y+z
            [0, -1, -1],  # 16: -y-z
            [0, 1, -1],   # 17: +y-z
            [0, -1, 1]    # 18: -y+z
        ], dtype=np.int32)
        
        # Lattice weights
        self.w = np.array([
            1.0/3.0,      # 0: rest
            1.0/18.0,     # 1-6: face neighbors
            1.0/18.0,
            1.0/18.0,
            1.0/18.0,
            1.0/18.0,
            1.0/18.0,
            1.0/36.0,     # 7-18: edge neighbors
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0,
            1.0/36.0
        ], dtype=np.float64)
        
        # Opposite directions (for bounce-back)
        self.opp = np.array([0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15, 18, 17], 
                           dtype=np.int32)
        
        # Speed of sound squared
        self.cs2 = 1.0/3.0
        self.cs = np.sqrt(self.cs2)
        
    def get_equilibrium(self, rho, u):
        """
        Calculate equilibrium distribution function.
        
        Parameters:
        -----------
        rho : ndarray
            Density field (nx, ny, nz)
        u : ndarray
            Velocity field (nx, ny, nz, 3)
            
        Returns:
        --------
        feq : ndarray
            Equilibrium distribution (nx, ny, nz, Q)
        """
        nx, ny, nz = rho.shape
        feq = np.zeros((nx, ny, nz, self.Q), dtype=np.float64)
        
        # Calculate u·u
        u_sq = np.sum(u**2, axis=3, keepdims=True)  # (nx, ny, nz, 1)
        
        for i in range(self.Q):
            # e_i · u
            eu = np.sum(self.e[i] * u, axis=3)  # (nx, ny, nz)
            
            # Equilibrium distribution
            feq[:, :, :, i] = self.w[i] * rho * (
                1.0 + 3.0 * eu + 4.5 * eu**2 - 1.5 * u_sq[:, :, :, 0]
            )
            
        return feq
    
    def get_macroscopic(self, f):
        """
        Calculate macroscopic variables from distribution function.
        
        Parameters:
        -----------
        f : ndarray
            Distribution function (nx, ny, nz, Q)
            
        Returns:
        --------
        rho : ndarray
            Density field (nx, ny, nz)
        u : ndarray
            Velocity field (nx, ny, nz, 3)
        """
        # Density: sum over all directions
        rho = np.sum(f, axis=3)
        
        # Velocity: momentum / density
        u = np.zeros((*f.shape[:3], 3), dtype=np.float64)
        for i in range(self.Q):
            for d in range(3):
                u[:, :, :, d] += f[:, :, :, i] * self.e[i, d]
        
        # Avoid division by zero
        rho_safe = np.where(rho > 1e-10, rho, 1.0)
        u = u / rho_safe[:, :, :, np.newaxis]
        
        return rho, u
    
    def stream(self, f):
        """
        Streaming step: propagate distributions along lattice velocities.
        
        Parameters:
        -----------
        f : ndarray
            Distribution function (nx, ny, nz, Q)
            
        Returns:
        --------
        f_streamed : ndarray
            Streamed distribution function (nx, ny, nz, Q)
        """
        f_new = np.zeros_like(f)
        
        for i in range(self.Q):
            f_new[:, :, :, i] = np.roll(f[:, :, :, i], 
                                       shift=(self.e[i, 0], self.e[i, 1], self.e[i, 2]),
                                       axis=(0, 1, 2))
        
        return f_new


# Global instance for easy access
lattice_d3q19 = D3Q19()
