"""
Modified Shan-Chen Method with Exact Difference Method (EDM) Forcing

This module implements the Shan-Chen multi-component/multi-phase model
with improved forcing schemes for better momentum conservation and
stability at high Reynolds numbers.
"""

import numpy as np
from .lattice import lattice_d3q19


class ShanChenForcing:
    """
    Modified Shan-Chen forcing with Exact Difference Method (EDM).
    
    Implements forcing terms that work with MRT collision scheme for
    stable simulations at high Reynolds numbers.
    """
    
    def __init__(self, lattice=None):
        """
        Initialize Shan-Chen forcing scheme.
        
        Parameters:
        -----------
        lattice : D3Q19, optional
            Lattice object (default: lattice_d3q19)
        """
        self.lattice = lattice if lattice is not None else lattice_d3q19
        
    def interaction_potential(self, rho, psi_type='ideal'):
        """
        Calculate interaction potential ψ(ρ).
        
        Parameters:
        -----------
        rho : ndarray
            Density field
        psi_type : str
            Type of potential ('ideal', 'carnahan-starling', 'constant')
            
        Returns:
        --------
        psi : ndarray
            Interaction potential
        """
        if psi_type == 'ideal':
            # Ideal gas: ψ = ρ
            psi = rho
        elif psi_type == 'carnahan-starling':
            # Carnahan-Starling: ψ = ρ₀[1 - exp(-ρ/ρ₀)]
            rho0 = 1.0
            psi = rho0 * (1.0 - np.exp(-rho / rho0))
        elif psi_type == 'constant':
            # Constant: ψ = 1
            psi = np.ones_like(rho)
        else:
            raise ValueError(f"Unknown potential type: {psi_type}")
            
        return psi
    
    def calculate_force(self, psi, G=-1.0, solid_mask=None):
        """
        Calculate Shan-Chen interaction force.
        
        Parameters:
        -----------
        psi : ndarray
            Interaction potential field (nx, ny, nz)
        G : float
            Interaction strength (negative for attraction)
        solid_mask : ndarray, optional
            Boolean mask for solid regions (nx, ny, nz)
            
        Returns:
        --------
        F : ndarray
            Force field (nx, ny, nz, 3)
        """
        nx, ny, nz = psi.shape
        F = np.zeros((nx, ny, nz, 3), dtype=np.float64)
        
        # Calculate force based on neighboring densities
        for i in range(1, self.lattice.Q):  # Skip rest particle
            # Shift potential in direction e_i
            psi_neighbor = np.roll(psi, 
                                  shift=tuple(self.lattice.e[i]),
                                  axis=(0, 1, 2))
            
            # If solid mask provided, zero out solid regions
            if solid_mask is not None:
                psi_neighbor = np.where(solid_mask, 0.0, psi_neighbor)
            
            # Accumulate force: F = -G * ψ(x) * Σ w_i * ψ(x+e_i) * e_i
            for d in range(3):
                F[:, :, :, d] += (self.lattice.w[i] * psi * psi_neighbor * 
                                 self.lattice.e[i, d])
        
        F *= -G
        return F
    
    def guo_forcing_velocity(self, u, F, rho, tau):
        """
        Calculate modified velocity for equilibrium using Guo forcing scheme.
        
        The Guo forcing scheme modifies the equilibrium velocity as:
        u_eq = u + τ*F/ρ
        
        Parameters:
        -----------
        u : ndarray
            Velocity field (nx, ny, nz, 3)
        F : ndarray
            Force field (nx, ny, nz, 3)
        rho : ndarray
            Density field (nx, ny, nz)
        tau : float
            Relaxation time
            
        Returns:
        --------
        u_eq : ndarray
            Modified velocity for equilibrium (nx, ny, nz, 3)
        """
        # Avoid division by zero
        rho_safe = np.where(rho > 1e-10, rho, 1.0)
        
        # u_eq = u + τ*F/ρ
        u_eq = u + tau * F / rho_safe[:, :, :, np.newaxis]
        
        return u_eq
    
    def forcing_term(self, F, u, force_scheme='guo'):
        """
        Calculate forcing term in distribution function space.
        
        Parameters:
        -----------
        F : ndarray
            Force field (nx, ny, nz, 3)
        u : ndarray
            Velocity field (nx, ny, nz, 3)
        force_scheme : str
            Forcing scheme ('guo', 'edm', 'he')
            
        Returns:
        --------
        S : ndarray
            Forcing term in distribution space (nx, ny, nz, Q)
        """
        nx, ny, nz, _ = F.shape
        S = np.zeros((nx, ny, nz, self.lattice.Q), dtype=np.float64)
        
        if force_scheme == 'guo':
            # Guo forcing: S_i = w_i * (1 - 1/(2τ)) * [(e_i - u)/cs² + (e_i·u)e_i/cs⁴] · F
            for i in range(self.lattice.Q):
                # e_i · F
                eF = np.sum(self.lattice.e[i] * F, axis=3)
                
                # e_i · u
                eu = np.sum(self.lattice.e[i] * u, axis=3)
                
                # u · F
                uF = np.sum(u * F, axis=3)
                
                # Forcing term
                S[:, :, :, i] = self.lattice.w[i] * (
                    (eF - uF) / self.lattice.cs2 +
                    3.0 * eu * eF / self.lattice.cs2
                )
        
        elif force_scheme == 'edm':
            # Exact Difference Method (EDM)
            # S_i = f_i^eq(ρ, u+F/ρ) - f_i^eq(ρ, u)
            # This is computed outside in the solver
            pass
        
        elif force_scheme == 'he':
            # He forcing scheme
            for i in range(self.lattice.Q):
                eF = np.sum(self.lattice.e[i] * F, axis=3)
                S[:, :, :, i] = self.lattice.w[i] * eF / self.lattice.cs2
        
        else:
            raise ValueError(f"Unknown forcing scheme: {force_scheme}")
        
        return S
    
    def edm_forcing(self, rho, u, F, tau):
        """
        Exact Difference Method (EDM) forcing.
        
        Calculates the forcing term as the difference between equilibrium
        distributions with and without force.
        
        Parameters:
        -----------
        rho : ndarray
            Density field (nx, ny, nz)
        u : ndarray
            Velocity field (nx, ny, nz, 3)
        F : ndarray
            Force field (nx, ny, nz, 3)
        tau : float
            Relaxation time
            
        Returns:
        --------
        S : ndarray
            EDM forcing term (nx, ny, nz, Q)
        """
        # Calculate modified velocity
        u_force = self.guo_forcing_velocity(u, F, rho, tau)
        
        # Calculate equilibrium with and without force
        feq_with = self.lattice.get_equilibrium(rho, u_force)
        feq_without = self.lattice.get_equilibrium(rho, u)
        
        # EDM forcing: difference between equilibria
        S = feq_with - feq_without
        
        return S
    
    def apply_temperature_dependent_force(self, F, T, T_ref=1.0, beta=1.0):
        """
        Modify force based on temperature (buoyancy).
        
        Parameters:
        -----------
        F : ndarray
            Base force field (nx, ny, nz, 3)
        T : ndarray
            Temperature field (nx, ny, nz)
        T_ref : float
            Reference temperature
        beta : float
            Thermal expansion coefficient
            
        Returns:
        --------
        F_modified : ndarray
            Temperature-modified force (nx, ny, nz, 3)
        """
        # Boussinesq approximation: F = F_base + ρ*g*β*(T - T_ref)
        buoyancy_factor = beta * (T - T_ref)
        
        F_modified = F.copy()
        # Apply buoyancy in vertical direction (z-direction)
        F_modified[:, :, :, 2] += buoyancy_factor
        
        return F_modified


# Global instance
shan_chen_forcing = ShanChenForcing()
