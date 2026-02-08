"""
LBM solver for conjugate heat transfer
"""
import numpy as np


class LBMSolver:
    """
    Lattice Boltzmann Method solver for conjugate heat transfer.
    
    Implements D3Q19 lattice for fluid flow and thermal transport.
    """
    
    # D3Q19 lattice velocities
    C = np.array([
        [0, 0, 0],    # 0
        [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1],  # 1-6
        [1, 1, 0], [-1, -1, 0], [1, -1, 0], [-1, 1, 0],  # 7-10
        [1, 0, 1], [-1, 0, -1], [1, 0, -1], [-1, 0, 1],  # 11-14
        [0, 1, 1], [0, -1, -1], [0, 1, -1], [0, -1, 1],  # 15-18
    ], dtype=float)
    
    # D3Q19 weights
    W = np.array([
        1.0/3.0,  # 0
        1.0/18.0, 1.0/18.0, 1.0/18.0, 1.0/18.0, 1.0/18.0, 1.0/18.0,  # 1-6
        1.0/36.0, 1.0/36.0, 1.0/36.0, 1.0/36.0,  # 7-10
        1.0/36.0, 1.0/36.0, 1.0/36.0, 1.0/36.0,  # 11-14
        1.0/36.0, 1.0/36.0, 1.0/36.0, 1.0/36.0,  # 15-18
    ], dtype=float)
    
    def __init__(self, geometry, fluid_material, solid_material, dx=1.0, dt=1.0):
        """
        Initialize LBM solver.
        
        Args:
            geometry: Geometry object defining the domain
            fluid_material: Material object for fluid
            solid_material: Material object for solid
            dx: Lattice spacing (m)
            dt: Time step (s)
        """
        self.geometry = geometry
        self.fluid_material = fluid_material
        self.solid_material = solid_material
        self.dx = dx
        self.dt = dt
        
        # Get grid dimensions
        self.nx, self.ny, self.nz = geometry.get_dimensions()
        
        # Get masks
        self.fluid_mask = geometry.get_fluid_mask()
        self.solid_mask = geometry.get_solid_mask()
        
        # Initialize distribution functions for fluid flow
        self.f = np.zeros((19, self.nx, self.ny, self.nz))
        self.f_new = np.zeros_like(self.f)
        
        # Initialize distribution functions for temperature
        self.g = np.zeros((19, self.nx, self.ny, self.nz))
        self.g_new = np.zeros_like(self.g)
        
        # Macroscopic variables
        self.rho = np.ones((self.nx, self.ny, self.nz)) * fluid_material.density
        self.u = np.zeros((3, self.nx, self.ny, self.nz))
        self.T = np.ones((self.nx, self.ny, self.nz)) * 300.0  # Initial temperature
        
        # Relaxation parameters
        self.calculate_relaxation_parameters()
        
        # Initialize equilibrium distributions
        self.initialize_distributions()
    
    def calculate_relaxation_parameters(self):
        """Calculate relaxation parameters from physical properties."""
        # Kinematic viscosity
        nu = self.fluid_material.get_kinematic_viscosity()
        
        # Relaxation time for momentum (BGK)
        self.tau_f = 0.5 + 3.0 * nu * self.dt / (self.dx ** 2)
        
        # Thermal diffusivity
        alpha_fluid = self.fluid_material.get_thermal_diffusivity()
        alpha_solid = self.solid_material.get_thermal_diffusivity()
        
        # Relaxation time for temperature
        self.tau_g_fluid = 0.5 + 3.0 * alpha_fluid * self.dt / (self.dx ** 2)
        self.tau_g_solid = 0.5 + 3.0 * alpha_solid * self.dt / (self.dx ** 2)
        
        # Create relaxation time field for temperature
        self.tau_g = np.where(self.fluid_mask, self.tau_g_fluid, self.tau_g_solid)
    
    def initialize_distributions(self):
        """Initialize distribution functions to equilibrium."""
        for i in range(19):
            self.f[i] = self.W[i] * self.rho
            self.g[i] = self.W[i] * self.T
    
    def equilibrium_f(self, i, rho, u):
        """Calculate equilibrium distribution for fluid flow."""
        cu = np.sum(self.C[i, :, None, None, None] * u, axis=0)
        u_sq = np.sum(u * u, axis=0)
        
        f_eq = self.W[i] * rho * (
            1.0 + 3.0 * cu + 4.5 * cu ** 2 - 1.5 * u_sq
        )
        return f_eq
    
    def equilibrium_g(self, i, T, u):
        """Calculate equilibrium distribution for temperature."""
        cu = np.sum(self.C[i, :, None, None, None] * u, axis=0)
        
        g_eq = self.W[i] * T * (1.0 + 3.0 * cu)
        return g_eq
    
    def collision(self):
        """Perform collision step."""
        # Fluid flow collision (only in fluid region)
        for i in range(19):
            f_eq = self.equilibrium_f(i, self.rho, self.u)
            self.f[i] = np.where(
                self.fluid_mask,
                self.f[i] - (self.f[i] - f_eq) / self.tau_f,
                self.f[i]  # No collision in solid
            )
        
        # Temperature collision (in both fluid and solid)
        for i in range(19):
            g_eq = self.equilibrium_g(i, self.T, self.u)
            self.g[i] = self.g[i] - (self.g[i] - g_eq) / self.tau_g[None, :, :, :]
    
    def streaming(self):
        """Perform streaming step."""
        for i in range(19):
            # Stream f (fluid flow)
            cx, cy, cz = self.C[i].astype(int)
            self.f_new[i] = np.roll(self.f[i], (cx, cy, cz), axis=(0, 1, 2))
            
            # Stream g (temperature)
            self.g_new[i] = np.roll(self.g[i], (cx, cy, cz), axis=(0, 1, 2))
        
        # Swap arrays
        self.f, self.f_new = self.f_new, self.f
        self.g, self.g_new = self.g_new, self.g
    
    def boundary_conditions(self):
        """Apply boundary conditions."""
        # Bounce-back for velocity at solid walls
        for i in range(1, 19):
            # Find opposite direction
            opp = self.get_opposite_direction(i)
            
            # Bounce-back at solid-fluid interface
            self.f[i][self.solid_mask] = self.f[opp][self.solid_mask]
    
    def get_opposite_direction(self, i):
        """Get opposite direction index for bounce-back."""
        # Opposite directions for D3Q19
        opposites = [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15, 18, 17]
        return opposites[i]
    
    def compute_macroscopic(self):
        """Compute macroscopic variables from distributions."""
        # Density and velocity (only in fluid)
        self.rho = np.sum(self.f, axis=0)
        
        for d in range(3):
            self.u[d] = np.sum(self.f * self.C[:, d, None, None, None], axis=0) / self.rho
        
        # Zero velocity in solid
        for d in range(3):
            self.u[d] = np.where(self.fluid_mask, self.u[d], 0.0)
        
        # Temperature (in both fluid and solid)
        self.T = np.sum(self.g, axis=0)
    
    def step(self):
        """Perform one time step."""
        self.collision()
        self.streaming()
        self.boundary_conditions()
        self.compute_macroscopic()
    
    def run(self, num_steps, callback=None):
        """
        Run simulation for specified number of steps.
        
        Args:
            num_steps: Number of time steps
            callback: Optional callback function called after each step
        """
        for step in range(num_steps):
            self.step()
            
            if callback is not None:
                callback(step, self)
    
    def get_temperature(self):
        """Get temperature field."""
        return self.T.copy()
    
    def get_velocity(self):
        """Get velocity field."""
        return self.u.copy()
    
    def get_density(self):
        """Get density field."""
        return self.rho.copy()
