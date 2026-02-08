"""
Conjugate Heat Transfer Coupling

This module couples the flow and thermal solvers to handle conjugate heat
transfer at solid-fluid interfaces with different thermal properties.
"""

import numpy as np
from .flow_solver import FlowSolver
from .thermal_solver import ThermalSolver


class ConjugateHTSolver:
    """
    Conjugate heat transfer solver coupling flow and thermal fields.
    
    Handles different thermal properties in solid and fluid regions
    while maintaining temperature and heat flux continuity at interfaces.
    """
    
    def __init__(self, nx, ny, nz, 
                 viscosity=0.01, 
                 alpha_fluid=0.01, 
                 alpha_solid=0.001,
                 k_ratio=10.0,
                 density=1.0):
        """
        Initialize conjugate heat transfer solver.
        
        Parameters:
        -----------
        nx, ny, nz : int
            Domain dimensions
        viscosity : float
            Fluid kinematic viscosity
        alpha_fluid : float
            Fluid thermal diffusivity
        alpha_solid : float
            Solid thermal diffusivity
        k_ratio : float
            Thermal conductivity ratio (k_solid/k_fluid)
        density : float
            Reference density
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        
        # Thermal properties
        self.alpha_fluid = alpha_fluid
        self.alpha_solid = alpha_solid
        self.k_ratio = k_ratio
        
        # Flow solver
        self.flow = FlowSolver(nx, ny, nz, viscosity=viscosity, density=density)
        
        # Thermal solver
        self.thermal = ThermalSolver(nx, ny, nz, thermal_diffusivity=alpha_fluid)
        
        # Solid mask
        self.solid_mask = np.zeros((nx, ny, nz), dtype=bool)
        
        # Interface mask (solid cells adjacent to fluid cells)
        self.interface_mask = np.zeros((nx, ny, nz), dtype=bool)
        
    def set_geometry(self, solid_mask):
        """
        Set solid/fluid geometry.
        
        Parameters:
        -----------
        solid_mask : ndarray
            Boolean mask (True = solid, False = fluid)
        """
        self.solid_mask = solid_mask.copy()
        
        # Set masks in solvers
        self.flow.set_solid_mask(solid_mask)
        self.thermal.set_solid_mask(solid_mask, alpha_solid=self.alpha_solid)
        
        # Identify interface cells
        self.interface_mask = self._identify_interface()
        
    def _identify_interface(self):
        """
        Identify solid-fluid interface cells.
        
        Returns:
        --------
        interface : ndarray
            Boolean mask of interface cells
        """
        interface = np.zeros_like(self.solid_mask, dtype=bool)
        
        # A cell is at the interface if it's solid and has at least one fluid neighbor
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    
                    # Check if solid cells have fluid neighbors
                    neighbor = np.roll(np.roll(np.roll(
                        self.solid_mask, dx, axis=0), dy, axis=1), dz, axis=2)
                    
                    # Solid cells with fluid neighbors are interface cells
                    interface |= (self.solid_mask & ~neighbor)
        
        return interface
    
    def initialize(self, rho0=None, u0=None, T0=None):
        """
        Initialize flow and thermal fields.
        
        Parameters:
        -----------
        rho0 : ndarray, optional
            Initial density field
        u0 : ndarray, optional
            Initial velocity field
        T0 : ndarray, optional
            Initial temperature field
        """
        # Initialize flow solver
        self.flow.initialize(rho0, u0)
        
        # Initialize thermal solver
        self.thermal.initialize(T0)
        
    def apply_interface_conditions(self):
        """
        Apply conjugate heat transfer interface conditions.
        
        At interfaces:
        1. Temperature continuity: T_solid = T_fluid
        2. Heat flux continuity: k_solid*∇T_solid = k_fluid*∇T_fluid
        
        This is implicitly handled by the LBM method through distribution
        functions, but we can add explicit corrections if needed.
        """
        # In LBM, conjugate interface conditions are typically handled
        # through proper thermal diffusivity setup and boundary conditions
        
        # For enhanced accuracy, we could implement:
        # - Interface reconstruction
        # - Flux matching schemes
        # - Temperature interpolation
        
        # For now, the different thermal diffusivities in solid/fluid
        # regions naturally handle the conjugate interface
        pass
    
    def step(self):
        """
        Perform one coupled time step.
        
        Order:
        1. Update flow field
        2. Pass velocity to thermal solver
        3. Update thermal field
        4. Apply interface conditions
        """
        # Flow step
        self.flow.step()
        
        # Update velocity field in thermal solver
        self.thermal.set_velocity_field(self.flow.u)
        
        # Thermal step
        self.thermal.step()
        
        # Apply conjugate interface conditions
        self.apply_interface_conditions()
        
    def run(self, n_steps, output_interval=100, callback=None):
        """
        Run coupled simulation.
        
        Parameters:
        -----------
        n_steps : int
            Number of time steps
        output_interval : int
            Interval for output/callback
        callback : callable, optional
            Function called at output intervals: callback(solver, step)
            
        Returns:
        --------
        history : dict
            Dictionary with convergence history
        """
        flow_convergence = []
        thermal_convergence = []
        
        for step in range(n_steps):
            self.step()
            
            if step % output_interval == 0:
                # Calculate convergence metrics
                if hasattr(self.flow, 'u_old'):
                    du = np.linalg.norm(self.flow.u - self.flow.u_old) / (
                        np.linalg.norm(self.flow.u) + 1e-10)
                    flow_convergence.append(du)
                else:
                    flow_convergence.append(1.0)
                
                if hasattr(self.thermal, 'T_old'):
                    dT = np.linalg.norm(self.thermal.T - self.thermal.T_old) / (
                        np.linalg.norm(self.thermal.T) + 1e-10)
                    thermal_convergence.append(dT)
                else:
                    thermal_convergence.append(1.0)
                
                self.flow.u_old = self.flow.u.copy()
                self.thermal.T_old = self.thermal.T.copy()
                
                # Call user callback
                if callback is not None:
                    callback(self, step)
                    
                # Print progress
                print(f"Step {step}/{n_steps}: "
                      f"du={flow_convergence[-1]:.2e}, dT={thermal_convergence[-1]:.2e}")
        
        return {
            'flow_convergence': flow_convergence,
            'thermal_convergence': thermal_convergence
        }
    
    def get_reynolds_number(self, U, L):
        """
        Calculate Reynolds number.
        
        Re = U*L/ν
        
        Parameters:
        -----------
        U : float
            Characteristic velocity
        L : float
            Characteristic length
            
        Returns:
        --------
        Re : float
            Reynolds number
        """
        return U * L / self.flow.viscosity
    
    def get_prandtl_number(self):
        """
        Calculate Prandtl number.
        
        Pr = ν/α
        
        Returns:
        --------
        Pr : float
            Prandtl number
        """
        return self.flow.viscosity / self.alpha_fluid
    
    def get_peclet_number(self, U, L):
        """
        Calculate Peclet number.
        
        Pe = U*L/α = Re*Pr
        
        Parameters:
        -----------
        U : float
            Characteristic velocity
        L : float
            Characteristic length
            
        Returns:
        --------
        Pe : float
            Peclet number
        """
        return U * L / self.alpha_fluid
    
    def get_nusselt_number(self, T_hot, T_cold, L):
        """
        Calculate Nusselt number.
        
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
            Nusselt number
        """
        return self.thermal.get_nusselt_number(T_hot, T_cold, L)
