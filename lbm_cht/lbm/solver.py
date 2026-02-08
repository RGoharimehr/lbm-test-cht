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
    
    # D3Q19 opposite directions for bounce-back
    OPPOSITE_DIRECTIONS = [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15, 18, 17]
    
    def __init__(self, geometry, fluid_material, solid_material, dx=1.0, dt=1.0, T_initial=300.0,
                 n_inlet=None, n_outlet=None):
        """
        Initialize LBM solver.
        
        Args:
            geometry: Geometry object defining the domain
            fluid_material: Material object for fluid
            solid_material: Material object for solid
            dx: Lattice spacing (m)
            dt: Time step (s)
            T_initial: Initial temperature (K), default: 300.0
            n_inlet: Number of lattice nodes for inlet region (default: auto-calculate)
            n_outlet: Number of lattice nodes for outlet region (default: auto-calculate)
        """
        self.geometry = geometry
        self.fluid_material = fluid_material
        self.solid_material = solid_material
        self.dx = dx
        self.dt = dt
        
        # Get grid dimensions
        self.nx, self.ny, self.nz = geometry.get_dimensions()
        
        # Calculate or set inlet/outlet regions
        if n_inlet is None:
            # Auto-calculate: 8% of nx, minimum 5 nodes
            self.n_inlet = max(5, int(0.08 * self.nx))
        else:
            self.n_inlet = n_inlet
            
        if n_outlet is None:
            # Auto-calculate: 8% of nx, minimum 5 nodes
            self.n_outlet = max(5, int(0.08 * self.nx))
        else:
            self.n_outlet = n_outlet
        
        # Validate inlet/outlet sizes
        self._validate_boundary_regions()
        
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
        self.T = np.ones((self.nx, self.ny, self.nz)) * T_initial
        
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
    
    def _validate_boundary_regions(self):
        """Validate that inlet/outlet regions are appropriately sized."""
        import warnings
        
        # Check minimum size
        if self.n_inlet < 3:
            warnings.warn(
                f"Inlet region ({self.n_inlet} nodes) is very small. "
                "Recommended: at least 5 nodes for stability.",
                UserWarning
            )
        
        if self.n_outlet < 3:
            warnings.warn(
                f"Outlet region ({self.n_outlet} nodes) is very small. "
                "Recommended: at least 5 nodes for stability.",
                UserWarning
            )
        
        # Check that inlet/outlet don't overlap
        if self.n_inlet + self.n_outlet >= self.nx:
            raise ValueError(
                f"Inlet ({self.n_inlet}) + outlet ({self.n_outlet}) regions "
                f"overlap or exceed domain size ({self.nx}). "
                "Reduce inlet/outlet sizes or increase domain."
            )
        
        # Check reasonable proportions
        inlet_fraction = self.n_inlet / self.nx
        outlet_fraction = self.n_outlet / self.nx
        
        if inlet_fraction > 0.2:
            warnings.warn(
                f"Inlet region is {inlet_fraction*100:.1f}% of domain (>{self.n_inlet} nodes). "
                "Consider reducing to 5-10% for efficiency.",
                UserWarning
            )
        
        if outlet_fraction > 0.2:
            warnings.warn(
                f"Outlet region is {outlet_fraction*100:.1f}% of domain ({self.n_outlet} nodes). "
                "Consider reducing to 5-10% for efficiency.",
                UserWarning
            )
    
    def set_inlet_temperature(self, T_inlet):
        """
        Set inlet temperature boundary condition.
        
        Args:
            T_inlet: Temperature at inlet (K)
        """
        self.T[:self.n_inlet, :, :] = T_inlet
        print(f"Inlet temperature set to {T_inlet}K over {self.n_inlet} nodes "
              f"(x ∈ [0, {self.n_inlet}), {self.n_inlet/self.nx*100:.1f}% of domain)")
    
    def set_outlet_temperature(self, T_outlet):
        """
        Set outlet temperature boundary condition.
        
        Args:
            T_outlet: Temperature at outlet (K)
        """
        self.T[-self.n_outlet:, :, :] = T_outlet
        print(f"Outlet temperature set to {T_outlet}K over {self.n_outlet} nodes "
              f"(x ∈ [{self.nx - self.n_outlet}, {self.nx}), "
              f"{self.n_outlet/self.nx*100:.1f}% of domain)")
    
    def set_inlet_velocity(self, u_inlet):
        """
        Set inlet velocity boundary condition.
        
        Args:
            u_inlet: Velocity at inlet in x-direction (m/s)
        """
        self.u[0, :self.n_inlet, :, :] = u_inlet
        print(f"Inlet velocity set to {u_inlet} m/s in x-direction "
              f"over {self.n_inlet} nodes")
    
    def get_inlet_region(self):
        """
        Get the inlet region indices.
        
        Returns:
            tuple: (x_start, x_end) for inlet region
        """
        return (0, self.n_inlet)
    
    def get_outlet_region(self):
        """
        Get the outlet region indices.
        
        Returns:
            tuple: (x_start, x_end) for outlet region
        """
        return (self.nx - self.n_outlet, self.nx)
    
    def print_boundary_info(self):
        """Print information about boundary regions."""
        print("\n" + "="*60)
        print("Boundary Region Information")
        print("="*60)
        print(f"Domain size: {self.nx} × {self.ny} × {self.nz}")
        print(f"Lattice spacing: {self.dx*1000:.3f} mm")
        print(f"\nInlet region:")
        print(f"  Nodes: {self.n_inlet} ({self.n_inlet/self.nx*100:.1f}% of nx)")
        print(f"  Physical length: {self.n_inlet * self.dx * 1000:.2f} mm")
        print(f"  Location: x ∈ [0, {self.n_inlet})")
        print(f"\nOutlet region:")
        print(f"  Nodes: {self.n_outlet} ({self.n_outlet/self.nx*100:.1f}% of nx)")
        print(f"  Physical length: {self.n_outlet * self.dx * 1000:.2f} mm")
        print(f"  Location: x ∈ [{self.nx - self.n_outlet}, {self.nx})")
        print(f"\nMain domain:")
        print(f"  Nodes: {self.nx - self.n_inlet - self.n_outlet}")
        print(f"  Physical length: {(self.nx - self.n_inlet - self.n_outlet) * self.dx * 1000:.2f} mm")
        print("="*60 + "\n")
    
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
        return self.OPPOSITE_DIRECTIONS[i]
    
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
