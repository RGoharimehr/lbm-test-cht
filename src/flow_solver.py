"""
Fluid Flow LBM Solver with MRT Collision

This module implements the fluid flow solver using Multiple Relaxation Time
(MRT) collision scheme with forcing for stable high Reynolds number simulations.
"""

import numpy as np
from .lattice import lattice_d3q19
from .mrt import mrt_d3q19
from .shan_chen import shan_chen_forcing


class FlowSolver:
    """
    Lattice Boltzmann fluid flow solver with MRT collision.
    """
    
    def __init__(self, nx, ny, nz, viscosity=0.01, density=1.0, 
                 forcing=None, force_scheme='guo'):
        """
        Initialize flow solver.
        
        Parameters:
        -----------
        nx, ny, nz : int
            Domain dimensions
        viscosity : float
            Kinematic viscosity
        density : float
            Reference density
        forcing : ndarray, optional
            External force field (nx, ny, nz, 3)
        force_scheme : str
            Forcing scheme ('guo', 'edm', 'he')
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.viscosity = viscosity
        self.density0 = density
        self.force_scheme = force_scheme
        
        # Lattice and collision operator
        self.lattice = lattice_d3q19
        self.mrt = mrt_d3q19
        
        # Forcing scheme
        self.forcing_model = shan_chen_forcing
        self.external_force = forcing if forcing is not None else np.zeros((nx, ny, nz, 3))
        
        # Relaxation time from viscosity
        # ν = cs²(τ - 0.5)
        self.tau = 0.5 + viscosity / self.lattice.cs2
        
        # Collision matrix
        self.S = self.mrt.get_collision_matrix(self.tau)
        
        # Distribution functions
        self.f = None
        self.f_post = None
        
        # Macroscopic variables
        self.rho = None
        self.u = None
        
        # Solid mask (True = solid, False = fluid)
        self.solid_mask = np.zeros((nx, ny, nz), dtype=bool)
        
    def initialize(self, rho0=None, u0=None):
        """
        Initialize distribution functions.
        
        Parameters:
        -----------
        rho0 : ndarray, optional
            Initial density field (nx, ny, nz)
        u0 : ndarray, optional
            Initial velocity field (nx, ny, nz, 3)
        """
        if rho0 is None:
            rho0 = np.ones((self.nx, self.ny, self.nz)) * self.density0
        if u0 is None:
            u0 = np.zeros((self.nx, self.ny, self.nz, 3))
        
        self.rho = rho0.copy()
        self.u = u0.copy()
        
        # Initialize with equilibrium distribution
        self.f = self.lattice.get_equilibrium(self.rho, self.u)
        
    def set_solid_mask(self, mask):
        """
        Set solid region mask.
        
        Parameters:
        -----------
        mask : ndarray
            Boolean mask (True = solid, False = fluid)
        """
        self.solid_mask = mask.copy()
        
    def set_external_force(self, force):
        """
        Set external force field.
        
        Parameters:
        -----------
        force : ndarray
            Force field (nx, ny, nz, 3)
        """
        self.external_force = force.copy()
        
    def collide(self):
        """
        MRT collision step with forcing.
        """
        if self.force_scheme == 'edm':
            # EDM forcing: modify equilibrium velocity
            u_eq = self.forcing_model.guo_forcing_velocity(
                self.u, self.external_force, self.rho, self.tau
            )
            # Collide with modified equilibrium
            self.f_post = self.mrt.collide(self.f, self.rho, u_eq, self.S)
            
        else:
            # Standard collision
            self.f_post = self.mrt.collide(self.f, self.rho, self.u, self.S)
            
            # Add forcing term
            if self.force_scheme == 'guo':
                S_force = self.forcing_model.forcing_term(
                    self.external_force, self.u, force_scheme='guo'
                )
                # Scale by (1 - 1/(2τ))
                S_force *= (1.0 - 1.0/(2.0*self.tau))
                self.f_post += S_force
            elif self.force_scheme == 'he':
                S_force = self.forcing_model.forcing_term(
                    self.external_force, self.u, force_scheme='he'
                )
                self.f_post += S_force
        
    def stream(self):
        """
        Streaming step.
        """
        self.f = self.lattice.stream(self.f_post)
        
    def apply_boundary_conditions(self, bc_dict):
        """
        Apply boundary conditions.
        
        Parameters:
        -----------
        bc_dict : dict
            Dictionary of boundary conditions
            Keys: 'type', 'location', 'value', etc.
        """
        # This will be implemented with boundary_conditions module
        pass
        
    def apply_bounce_back(self):
        """
        Apply bounce-back boundary condition on solid nodes.
        """
        for i in range(self.lattice.Q):
            # Swap with opposite direction
            opp_i = self.lattice.opp[i]
            self.f[self.solid_mask, i] = self.f_post[self.solid_mask, opp_i]
    
    def update_macroscopic(self):
        """
        Update macroscopic variables from distribution functions.
        """
        self.rho, u_temp = self.lattice.get_macroscopic(self.f)
        
        # Correct velocity with forcing (for schemes that require it)
        if self.force_scheme == 'guo' or self.force_scheme == 'he':
            # u = u_temp + F/(2ρ)
            rho_safe = np.where(self.rho > 1e-10, self.rho, 1.0)
            self.u = u_temp + self.external_force / (2.0 * rho_safe[:, :, :, np.newaxis])
        else:
            self.u = u_temp
        
        # Zero out velocity in solid regions
        self.u[self.solid_mask] = 0.0
        
    def step(self):
        """
        Perform one time step (collision + streaming + BC).
        """
        self.collide()
        self.stream()
        self.apply_bounce_back()
        self.update_macroscopic()
        
    def run(self, n_steps, output_interval=100, callback=None):
        """
        Run simulation for multiple time steps.
        
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
                # Calculate convergence metric (change in velocity)
                if hasattr(self, 'u_old'):
                    du = np.linalg.norm(self.u - self.u_old) / (np.linalg.norm(self.u) + 1e-10)
                    convergence_history.append(du)
                else:
                    convergence_history.append(1.0)
                
                self.u_old = self.u.copy()
                
                # Call user callback
                if callback is not None:
                    callback(self, step)
                    
        return convergence_history
    
    def get_velocity_magnitude(self):
        """Get velocity magnitude field."""
        return np.sqrt(np.sum(self.u**2, axis=3))
    
    def get_vorticity(self):
        """
        Calculate vorticity field.
        
        Returns:
        --------
        omega : ndarray
            Vorticity vector field (nx, ny, nz, 3)
        """
        omega = np.zeros_like(self.u)
        
        # ω = ∇ × u
        # ω_x = ∂u_z/∂y - ∂u_y/∂z
        omega[:, :, :, 0] = (
            np.roll(self.u[:, :, :, 2], -1, axis=1) - np.roll(self.u[:, :, :, 2], 1, axis=1) -
            np.roll(self.u[:, :, :, 1], -1, axis=2) + np.roll(self.u[:, :, :, 1], 1, axis=2)
        ) / 2.0
        
        # ω_y = ∂u_x/∂z - ∂u_z/∂x
        omega[:, :, :, 1] = (
            np.roll(self.u[:, :, :, 0], -1, axis=2) - np.roll(self.u[:, :, :, 0], 1, axis=2) -
            np.roll(self.u[:, :, :, 2], -1, axis=0) + np.roll(self.u[:, :, :, 2], 1, axis=0)
        ) / 2.0
        
        # ω_z = ∂u_y/∂x - ∂u_x/∂y
        omega[:, :, :, 2] = (
            np.roll(self.u[:, :, :, 1], -1, axis=0) - np.roll(self.u[:, :, :, 1], 1, axis=0) -
            np.roll(self.u[:, :, :, 0], -1, axis=1) + np.roll(self.u[:, :, :, 0], 1, axis=1)
        ) / 2.0
        
        return omega
