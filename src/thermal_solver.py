"""
Thermal LBM Solver with Double Distribution Function

This module implements the thermal solver using a separate distribution
function for temperature, enabling conjugate heat transfer simulations.
"""

import numpy as np
from .lattice import lattice_d3q19
from .mrt import mrt_d3q19


class ThermalSolver:
    """
    Lattice Boltzmann thermal solver with double distribution function.
    
    Uses a separate distribution function for temperature to handle
    different thermal diffusivities in solid and fluid regions.
    """
    
    def __init__(self, nx, ny, nz, thermal_diffusivity=0.01, 
                 velocity_field=None):
        """
        Initialize thermal solver.
        
        Parameters:
        -----------
        nx, ny, nz : int
            Domain dimensions
        thermal_diffusivity : float
            Thermal diffusivity (α = k/(ρ*cp))
        velocity_field : ndarray, optional
            Velocity field for advection (nx, ny, nz, 3)
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.alpha = thermal_diffusivity
        
        # Lattice and collision operator
        self.lattice = lattice_d3q19
        self.mrt = mrt_d3q19
        
        # Velocity field (from flow solver)
        self.u = velocity_field if velocity_field is not None else np.zeros((nx, ny, nz, 3))
        
        # Thermal relaxation time
        # α = cs²(τ_T - 0.5)
        self.tau_T = 0.5 + thermal_diffusivity / self.lattice.cs2
        
        # Thermal collision matrix
        self.S_T = self.mrt.get_collision_matrix(self.tau_T)
        
        # Thermal distribution functions
        self.g = None
        self.g_post = None
        
        # Temperature field
        self.T = None
        
        # Solid mask and thermal properties
        self.solid_mask = np.zeros((nx, ny, nz), dtype=bool)
        self.alpha_field = np.ones((nx, ny, nz)) * thermal_diffusivity
        
    def initialize(self, T0=None):
        """
        Initialize thermal distribution functions.
        
        Parameters:
        -----------
        T0 : ndarray, optional
            Initial temperature field (nx, ny, nz)
        """
        if T0 is None:
            T0 = np.ones((self.nx, self.ny, self.nz))
        
        self.T = T0.copy()
        
        # Initialize with equilibrium distribution
        # For thermal LBM, we use T as the "density"
        self.g = self.lattice.get_equilibrium(self.T, self.u)
        
    def set_solid_mask(self, mask, alpha_solid=None):
        """
        Set solid region mask and thermal diffusivity.
        
        Parameters:
        -----------
        mask : ndarray
            Boolean mask (True = solid, False = fluid)
        alpha_solid : float, optional
            Thermal diffusivity in solid region
        """
        self.solid_mask = mask.copy()
        
        if alpha_solid is not None:
            # Set different thermal diffusivity in solid regions
            self.alpha_field[mask] = alpha_solid
            
    def set_velocity_field(self, u):
        """
        Set velocity field for advection.
        
        Parameters:
        -----------
        u : ndarray
            Velocity field (nx, ny, nz, 3)
        """
        self.u = u.copy()
        
    def get_thermal_equilibrium(self, T, u):
        """
        Calculate thermal equilibrium distribution.
        
        For passive scalar transport, equilibrium is:
        g_i^eq = w_i * T * [1 + 3(e_i·u)/cs² + 9(e_i·u)²/(2cs⁴) - 3u²/(2cs²)]
        
        Parameters:
        -----------
        T : ndarray
            Temperature field (nx, ny, nz)
        u : ndarray
            Velocity field (nx, ny, nz, 3)
            
        Returns:
        --------
        geq : ndarray
            Thermal equilibrium distribution (nx, ny, nz, Q)
        """
        # Use lattice equilibrium with T as density
        geq = self.lattice.get_equilibrium(T, u)
        return geq
    
    def collide(self):
        """
        Thermal MRT collision step.
        """
        # Get equilibrium with current temperature and velocity
        geq = self.get_thermal_equilibrium(self.T, self.u)
        
        # MRT collision
        # For simplicity, use BGK-style collision in velocity space
        # Could be upgraded to full MRT in moment space
        omega_T = 1.0 / self.tau_T
        self.g_post = self.g - omega_T * (self.g - geq)
        
    def stream(self):
        """
        Thermal streaming step.
        """
        self.g = self.lattice.stream(self.g_post)
        
    def apply_thermal_boundary_conditions(self, bc_dict):
        """
        Apply thermal boundary conditions.
        
        Parameters:
        -----------
        bc_dict : dict
            Dictionary of thermal boundary conditions
        """
        # This will be implemented with boundary_conditions module
        pass
        
    def apply_conjugate_interface(self):
        """
        Apply conjugate heat transfer interface conditions.
        
        At solid-fluid interfaces, enforce:
        - Temperature continuity: T_fluid = T_solid
        - Heat flux continuity: k_fluid * ∇T_fluid = k_solid * ∇T_solid
        """
        # Interface reconstruction will be handled by conjugate_ht module
        pass
    
    def update_temperature(self):
        """
        Update temperature from thermal distribution functions.
        """
        # Temperature is the zeroth moment: T = Σ g_i
        self.T = np.sum(self.g, axis=3)
        
    def step(self):
        """
        Perform one thermal time step.
        """
        self.collide()
        self.stream()
        self.update_temperature()
        
    def run(self, n_steps, output_interval=100, callback=None):
        """
        Run thermal simulation for multiple time steps.
        
        Parameters:
        -----------
        n_steps : int
            Number of time steps
        output_interval : int
            Interval for output/callback
        callback : callable, optional
            Function called at output intervals
            
        Returns:
        --------
        convergence_history : list
            List of convergence metrics
        """
        convergence_history = []
        
        for step in range(n_steps):
            self.step()
            
            if step % output_interval == 0:
                # Calculate convergence metric
                if hasattr(self, 'T_old'):
                    dT = np.linalg.norm(self.T - self.T_old) / (np.linalg.norm(self.T) + 1e-10)
                    convergence_history.append(dT)
                else:
                    convergence_history.append(1.0)
                
                self.T_old = self.T.copy()
                
                # Call user callback
                if callback is not None:
                    callback(self, step)
                    
        return convergence_history
    
    def get_heat_flux(self):
        """
        Calculate heat flux field.
        
        q = -k * ∇T
        
        Returns:
        --------
        q : ndarray
            Heat flux vector field (nx, ny, nz, 3)
        """
        q = np.zeros((self.nx, self.ny, self.nz, 3), dtype=np.float64)
        
        # Numerical gradient using central differences
        # q_x = -k * ∂T/∂x
        q[:, :, :, 0] = -(
            np.roll(self.T, -1, axis=0) - np.roll(self.T, 1, axis=0)
        ) / 2.0
        
        # q_y = -k * ∂T/∂y
        q[:, :, :, 1] = -(
            np.roll(self.T, -1, axis=1) - np.roll(self.T, 1, axis=1)
        ) / 2.0
        
        # q_z = -k * ∂T/∂z
        q[:, :, :, 2] = -(
            np.roll(self.T, -1, axis=2) - np.roll(self.T, 1, axis=2)
        ) / 2.0
        
        # Scale by thermal conductivity (k = α * ρ * cp, assume ρ*cp=1)
        q *= self.alpha_field[:, :, :, np.newaxis]
        
        return q
    
    def get_nusselt_number(self, T_hot, T_cold, L):
        """
        Calculate average Nusselt number.
        
        Nu = h*L/k = (q*L)/(k*(T_hot - T_cold))
        
        Parameters:
        -----------
        T_hot : float
            Hot wall temperature
        T_cold : float
            Cold wall temperature
        L : float
            Characteristic length
            
        Returns:
        --------
        Nu : float
            Average Nusselt number
        """
        q = self.get_heat_flux()
        q_mag = np.sqrt(np.sum(q**2, axis=3))
        
        # Average heat flux
        q_avg = np.mean(q_mag)
        
        # Nusselt number
        Nu = q_avg * L / (self.alpha * (T_hot - T_cold))
        
        return Nu
