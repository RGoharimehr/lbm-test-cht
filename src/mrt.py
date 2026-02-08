"""
Multiple Relaxation Time (MRT) Collision Operator for D3Q19 Lattice

This module implements the MRT collision scheme with transformation matrices
for improved stability at high Reynolds numbers.
"""

import numpy as np
from .lattice import lattice_d3q19


class MRT_D3Q19:
    """
    Multiple Relaxation Time collision operator for D3Q19 lattice.
    
    The MRT scheme uses moment space instead of velocity space for collision,
    providing better stability and allowing independent control of different
    physical processes.
    """
    
    def __init__(self):
        """Initialize MRT transformation matrices for D3Q19."""
        self.lattice = lattice_d3q19
        self.Q = self.lattice.Q
        
        # Transformation matrix M (moments from distribution functions)
        # Based on D'Humières (2002) formulation
        self.M = self._construct_transformation_matrix()
        self.M_inv = np.linalg.inv(self.M)
        
    def _construct_transformation_matrix(self):
        """
        Construct the transformation matrix M for D3Q19.
        
        Based on d'Humières (2002) formulation for D3Q19.
        """
        e = self.lattice.e
        M = np.array([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [-30, -11, -11, -11, -11, -11, -11, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
            [12, -4, -4, -4, -4, -4, -4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [0, 1, -1, 0, 0, 0, 0, 1, -1, 1, -1, 1, -1, 1, -1, 0, 0, 0, 0],
            [0, -4, 4, 0, 0, 0, 0, 1, -1, 1, -1, 1, -1, 1, -1, 0, 0, 0, 0],
            [0, 0, 0, 1, -1, 0, 0, 1, -1, -1, 1, 0, 0, 0, 0, 1, -1, 1, -1],
            [0, 0, 0, -4, 4, 0, 0, 1, -1, -1, 1, 0, 0, 0, 0, 1, -1, 1, -1],
            [0, 0, 0, 0, 0, 1, -1, 0, 0, 0, 0, 1, -1, -1, 1, 1, -1, -1, 1],
            [0, 0, 0, 0, 0, -4, 4, 0, 0, 0, 0, 1, -1, -1, 1, 1, -1, -1, 1],
            [0, 2, 2, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, -2, -2, -2, -2],
            [0, -4, -4, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, -2, -2, -2, -2],
            [0, 0, 0, 1, 1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 0, 0, 0, 0],
            [0, 0, 0, -2, -2, 2, 2, 1, 1, 1, 1, -1, -1, -1, -1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, -1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, -1, -1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, -1, 1, -1, -1, 1, -1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, -1, 1, 1, -1, 0, 0, 0, 0, 1, -1, 1, -1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, -1, 1, -1, 1, 1, -1]
        ], dtype=np.float64)
        
        return M
    
    def get_equilibrium_moments(self, rho, u):
        """
        Calculate equilibrium moments.
        
        Parameters:
        -----------
        rho : ndarray
            Density field (nx, ny, nz)
        u : ndarray
            Velocity field (nx, ny, nz, 3)
            
        Returns:
        --------
        meq : ndarray
            Equilibrium moments (nx, ny, nz, Q)
        """
        nx, ny, nz = rho.shape
        meq = np.zeros((nx, ny, nz, self.Q), dtype=np.float64)
        
        ux, uy, uz = u[:, :, :, 0], u[:, :, :, 1], u[:, :, :, 2]
        u2 = ux**2 + uy**2 + uz**2
        
        # Equilibrium moments based on D'Humières formulation
        meq[:, :, :, 0] = rho
        meq[:, :, :, 1] = -11.0 * rho + 19.0 * rho * u2
        meq[:, :, :, 2] = 3.0 * rho - 5.5 * rho * u2
        meq[:, :, :, 3] = rho * ux
        meq[:, :, :, 4] = rho * uy
        meq[:, :, :, 5] = rho * uz
        meq[:, :, :, 6] = -2.0/3.0 * rho * ux
        meq[:, :, :, 7] = -2.0/3.0 * rho * uy
        meq[:, :, :, 8] = -2.0/3.0 * rho * uz
        meq[:, :, :, 9] = rho * (2.0 * ux**2 - uy**2 - uz**2)
        meq[:, :, :, 10] = rho * (uy**2 - uz**2)
        meq[:, :, :, 11] = rho * (ux**2 - uy**2)
        meq[:, :, :, 12] = rho * ux * uy
        meq[:, :, :, 13] = rho * uy * uz
        meq[:, :, :, 14] = rho * ux * uz
        meq[:, :, :, 15] = 0.0
        meq[:, :, :, 16] = 0.0
        meq[:, :, :, 17] = 0.0
        meq[:, :, :, 18] = 0.0
        
        return meq
    
    def get_collision_matrix(self, tau, tau_e=None, tau_eps=None, tau_q=None):
        """
        Create diagonal relaxation matrix S.
        
        Parameters:
        -----------
        tau : float
            Relaxation time for momentum (related to viscosity)
        tau_e : float, optional
            Relaxation time for energy mode (default: tau)
        tau_eps : float, optional
            Relaxation time for epsilon mode (default: tau)
        tau_q : float, optional
            Relaxation time for heat flux (default: tau)
            
        Returns:
        --------
        S : ndarray
            Diagonal relaxation matrix (Q, Q)
        """
        if tau_e is None:
            tau_e = tau
        if tau_eps is None:
            tau_eps = tau
        if tau_q is None:
            tau_q = tau
            
        # Relaxation parameters (inverse relaxation times)
        s = np.zeros(self.Q, dtype=np.float64)
        
        s[0] = 0.0        # conserved: density
        s[1] = 1.0/tau_e  # energy
        s[2] = 1.0/tau_eps # energy squared
        s[3] = 0.0        # conserved: jx
        s[4] = 0.0        # conserved: jy
        s[5] = 0.0        # conserved: jz
        s[6] = 1.0/tau_q  # qx
        s[7] = 1.0/tau_q  # qy
        s[8] = 1.0/tau_q  # qz
        s[9] = 1.0/tau    # 3pxx
        s[10] = 1.0/tau   # 3pixx
        s[11] = 1.0/tau   # pww
        s[12] = 1.0/tau   # pxy (shear viscosity)
        s[13] = 1.0/tau   # pyz
        s[14] = 1.0/tau   # pxz
        s[15] = 1.0/tau   # mx
        s[16] = 1.0/tau   # my
        s[17] = 1.0/tau   # mz
        s[18] = 1.0/tau   # m
        
        return np.diag(s)
    
    def collide(self, f, rho, u, S):
        """
        MRT collision step.
        
        Parameters:
        -----------
        f : ndarray
            Distribution function (nx, ny, nz, Q)
        rho : ndarray
            Density field (nx, ny, nz)
        u : ndarray
            Velocity field (nx, ny, nz, 3)
        S : ndarray
            Collision matrix (Q, Q)
            
        Returns:
        --------
        f_post : ndarray
            Post-collision distribution (nx, ny, nz, Q)
        """
        nx, ny, nz, Q = f.shape
        
        # Transform to moment space
        m = np.zeros_like(f)
        for i in range(Q):
            for j in range(Q):
                m[:, :, :, i] += self.M[i, j] * f[:, :, :, j]
        
        # Get equilibrium moments
        meq = self.get_equilibrium_moments(rho, u)
        
        # Collision in moment space
        m_post = m.copy()
        for i in range(Q):
            m_post[:, :, :, i] -= S[i, i] * (m[:, :, :, i] - meq[:, :, :, i])
        
        # Transform back to velocity space
        f_post = np.zeros_like(f)
        for i in range(Q):
            for j in range(Q):
                f_post[:, :, :, i] += self.M_inv[i, j] * m_post[:, :, :, j]
        
        return f_post


# Global instance
mrt_d3q19 = MRT_D3Q19()
