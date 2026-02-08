"""
Unit converter for dimensionless scaling in LBM simulations.

This module provides tools to convert between physical and lattice units
while maintaining correct dimensionless numbers (Reynolds, Mach, Prandtl).
"""
import numpy as np
import warnings


class DimensionlessScaling:
    """
    Handles conversion between physical and lattice units for LBM simulations.
    
    The key insight is that in LBM we have constraints:
    - Lattice velocity should be Ma < 0.3 (u_lattice < 0.173)
    - Relaxation time tau > 0.5 (ideally > 0.6 for stability)
    
    But we have freedom to adjust:
    - Domain size N (number of lattice nodes)
    - Grid spacing dx
    - Time step dt
    
    This class calculates optimal lattice parameters to achieve target
    physical Reynolds number while respecting LBM constraints.
    """
    
    def __init__(self, Re_target, L_ref, u_ref, nu_ref, 
                 Ma_target=0.1, tau_target=0.7, N_min=10):
        """
        Initialize dimensionless scaling.
        
        Args:
            Re_target: Target Reynolds number (dimensionless)
            L_ref: Reference length in physical units (m)
            u_ref: Reference velocity in physical units (m/s)
            nu_ref: Kinematic viscosity in physical units (m^2/s)
            Ma_target: Target Mach number in lattice (default: 0.1)
            tau_target: Target relaxation time (default: 0.7)
            N_min: Minimum domain size in lattice units (default: 10)
        
        Note: Reynolds number calculated as Re = u_ref * L_ref / nu_ref
        """
        self.Re_target = Re_target
        self.L_ref = L_ref
        self.u_ref = u_ref
        self.nu_ref = nu_ref
        self.Ma_target = Ma_target
        self.tau_target = tau_target
        self.N_min = N_min
        
        # LBM constants
        self.c_s = 1.0 / np.sqrt(3.0)  # Speed of sound in lattice units
        
        # Calculate scaling parameters
        self.calculate_scaling()
        
    def calculate_scaling(self):
        """
        Calculate lattice parameters from physical parameters and targets.
        
        The key equations are:
        1. Re = u*L/ν = u_lattice * N / ν_lattice
        2. ν_lattice = (tau - 0.5) / 3
        3. Ma = u_lattice / c_s
        4. u_lattice = Ma * c_s
        
        From these we can solve for N and tau given Re and Ma targets.
        """
        # Lattice velocity from Mach number target
        self.u_lattice = self.Ma_target * self.c_s
        
        # Lattice viscosity from tau target
        self.nu_lattice = (self.tau_target - 0.5) / 3.0
        
        # Domain size from Reynolds number
        # Re = u_lattice * N / nu_lattice
        # N = Re * nu_lattice / u_lattice
        self.N = int(np.ceil(self.Re_target * self.nu_lattice / self.u_lattice))
        
        # Ensure minimum size
        if self.N < self.N_min:
            self.N = self.N_min
            warnings.warn(
                f"Calculated N={self.N} is below minimum. "
                f"Using N={self.N_min}. Reynolds number may not match target."
            )
        
        # Calculate actual Reynolds number in lattice
        self.Re_lattice = self.u_lattice * self.N / self.nu_lattice
        
        # Calculate scaling factors
        # Length: L_ref corresponds to N lattice units
        self.dx = self.L_ref / self.N
        
        # Velocity: u_ref corresponds to u_lattice
        self.velocity_scale = self.u_ref / self.u_lattice
        
        # Time: from velocity and length scales
        # u = dx/dt -> dt = dx/u
        self.dt = self.dx / self.velocity_scale
        
        # Alternatively: from viscosity scaling
        # ν = dx²/dt -> dt = dx²/ν_scale
        # where ν_scale = ν_ref / ν_lattice
        self.viscosity_scale = self.nu_ref / self.nu_lattice
        dt_from_visc = (self.dx ** 2) / self.viscosity_scale
        
        # Verify scaling consistency
        if not np.isclose(self.dt, dt_from_visc, rtol=0.01):
            warnings.warn(
                f"Time step from velocity ({self.dt:.6e}) and viscosity "
                f"({dt_from_visc:.6e}) scaling don't match. Using velocity-based dt."
            )
        
        # Verify tau from calculated dt and dx
        self.tau_actual = 0.5 + 3.0 * self.nu_ref * self.dt / (self.dx ** 2)
        
        if not np.isclose(self.tau_actual, self.tau_target, rtol=0.01):
            warnings.warn(
                f"Actual tau ({self.tau_actual:.3f}) differs from target ({self.tau_target:.3f})"
            )
        
        # Store scaling info
        self._print_summary()
    
    def _print_summary(self):
        """Print summary of scaling parameters."""
        print("\n" + "="*60)
        print("DIMENSIONLESS SCALING SUMMARY")
        print("="*60)
        print(f"\nPHYSICAL PARAMETERS:")
        print(f"  Reference length:     L = {self.L_ref:.6f} m")
        print(f"  Reference velocity:   u = {self.u_ref:.6f} m/s")
        print(f"  Kinematic viscosity:  ν = {self.nu_ref:.6e} m²/s")
        print(f"  Target Reynolds:     Re = {self.Re_target:.0f}")
        
        print(f"\nLATTICE PARAMETERS:")
        print(f"  Domain size:          N = {self.N} lattice units")
        print(f"  Lattice velocity:     u = {self.u_lattice:.6f} (Ma = {self.Ma_target:.3f})")
        print(f"  Lattice viscosity:    ν = {self.nu_lattice:.6f}")
        print(f"  Relaxation time:    tau = {self.tau_actual:.3f}")
        print(f"  Actual Reynolds:     Re = {self.Re_lattice:.1f}")
        
        print(f"\nSCALING FACTORS:")
        print(f"  Grid spacing:        dx = {self.dx:.6e} m")
        print(f"  Time step:           dt = {self.dx:.6e} s")
        print(f"  Velocity scale:      u* = {self.velocity_scale:.6e}")
        print(f"  Viscosity scale:     ν* = {self.viscosity_scale:.6e}")
        
        print(f"\nSTABILITY CHECKS:")
        ma_check = "✓" if self.Ma_target < 0.3 else "✗"
        print(f"  Mach number < 0.3:     {ma_check} (Ma = {self.Ma_target:.3f})")
        tau_check = "✓" if self.tau_actual > 0.6 else "⚠" if self.tau_actual > 0.55 else "✗"
        print(f"  Tau > 0.6:             {tau_check} (tau = {self.tau_actual:.3f})")
        re_match = "✓" if np.isclose(self.Re_lattice, self.Re_target, rtol=0.01) else "⚠"
        print(f"  Re matches target:     {re_match} (target={self.Re_target:.0f}, actual={self.Re_lattice:.1f})")
        print("="*60 + "\n")
    
    def physical_to_lattice_length(self, L_phys):
        """Convert physical length to lattice units."""
        return L_phys / self.dx
    
    def lattice_to_physical_length(self, L_latt):
        """Convert lattice length to physical units."""
        return L_latt * self.dx
    
    def physical_to_lattice_velocity(self, u_phys):
        """Convert physical velocity to lattice units."""
        return u_phys / self.velocity_scale
    
    def lattice_to_physical_velocity(self, u_latt):
        """Convert lattice velocity to physical units."""
        return u_latt * self.velocity_scale
    
    def physical_to_lattice_time(self, t_phys):
        """Convert physical time to lattice steps."""
        return t_phys / self.dt
    
    def lattice_to_physical_time(self, t_latt):
        """Convert lattice steps to physical time."""
        return t_latt * self.dt
    
    def physical_to_lattice_viscosity(self, nu_phys):
        """Convert physical viscosity to lattice units."""
        return nu_phys / self.viscosity_scale
    
    def lattice_to_physical_viscosity(self, nu_latt):
        """Convert lattice viscosity to physical units."""
        return nu_latt * self.viscosity_scale
    
    def get_recommended_grid_size(self, aspect_ratios=(1, 1, 1)):
        """
        Get recommended grid dimensions.
        
        Args:
            aspect_ratios: Tuple of (Lx/L, Ly/L, Lz/L) ratios
        
        Returns:
            Tuple of (nx, ny, nz) grid dimensions
        """
        # Normalize aspect ratios
        total = sum(aspect_ratios)
        ratios_normalized = tuple(r/total for r in aspect_ratios)
        
        # Distribute N according to ratios
        nx = int(np.ceil(self.N * ratios_normalized[0]))
        ny = int(np.ceil(self.N * ratios_normalized[1]))
        nz = int(np.ceil(self.N * ratios_normalized[2]))
        
        # Ensure minimum size
        nx = max(nx, self.N_min)
        ny = max(ny, self.N_min)
        nz = max(nz, self.N_min)
        
        return nx, ny, nz
    
    def calculate_physical_Re(self):
        """Calculate physical Reynolds number from reference parameters."""
        return self.u_ref * self.L_ref / self.nu_ref
    
    def calculate_lattice_Re(self):
        """Calculate lattice Reynolds number."""
        return self.u_lattice * self.N / self.nu_lattice
    
    def calculate_Ma(self):
        """Calculate Mach number."""
        return self.u_lattice / self.c_s
    
    def calculate_Pr(self, alpha_ref):
        """
        Calculate Prandtl number.
        
        Args:
            alpha_ref: Thermal diffusivity in physical units (m²/s)
        
        Returns:
            Prandtl number Pr = ν/α
        """
        return self.nu_ref / alpha_ref


def create_scaling_for_high_Re(Re_target, L_ref, u_ref, nu_ref, 
                                Ma_max=0.2, tau_min=0.65):
    """
    Create scaling specifically for high Reynolds number simulations.
    
    This function automatically adjusts parameters to achieve high Re
    while keeping Mach number and tau in safe ranges.
    
    Args:
        Re_target: Target Reynolds number
        L_ref: Reference length (m)
        u_ref: Reference velocity (m/s)
        nu_ref: Kinematic viscosity (m²/s)
        Ma_max: Maximum allowed Mach number (default: 0.2)
        tau_min: Minimum relaxation time (default: 0.65)
    
    Returns:
        DimensionlessScaling object
    """
    # Start with low Mach number
    Ma_target = min(Ma_max, 0.15)
    
    # Use safe tau
    tau_target = max(tau_min, 0.7)
    
    # Create scaling
    scaling = DimensionlessScaling(
        Re_target=Re_target,
        L_ref=L_ref,
        u_ref=u_ref,
        nu_ref=nu_ref,
        Ma_target=Ma_target,
        tau_target=tau_target
    )
    
    # Check if we need to adjust
    if scaling.N > 10000:
        warnings.warn(
            f"Required domain size N={scaling.N} is very large. "
            f"Consider increasing Ma_target or decreasing tau_target."
        )
    
    return scaling


def example_water_pipe():
    """
    Example: High Reynolds number flow in a pipe.
    
    Physical parameters:
    - Velocity: 6 m/s
    - Diameter: 0.01 m (10 mm)
    - Fluid: Water at 20°C
    - Target Re = 60,000
    """
    print("\nExample: High Reynolds number water flow in pipe")
    print("-" * 60)
    
    # Physical parameters
    u_phys = 6.0  # m/s
    D_phys = 0.01  # m
    nu_water = 1.0e-6  # m²/s (water at 20°C)
    
    # Calculate physical Reynolds number
    Re_phys = u_phys * D_phys / nu_water
    print(f"Physical Reynolds number: Re = {Re_phys:.0f}")
    
    # Create scaling
    scaling = DimensionlessScaling(
        Re_target=Re_phys,
        L_ref=D_phys,
        u_ref=u_phys,
        nu_ref=nu_water,
        Ma_target=0.1,  # Keep Ma low
        tau_target=0.7   # Safe tau value
    )
    
    # Print usage instructions
    print("\nUSAGE INSTRUCTIONS:")
    print(f"1. Create pipe geometry with diameter = {scaling.N} lattice units")
    print(f"2. Set dx = {scaling.dx:.6e} m")
    print(f"3. Set dt = {scaling.dt:.6e} s")
    print(f"4. Set inlet velocity = {scaling.u_lattice:.6f} (lattice units)")
    print(f"5. Domain should be ~{scaling.N*10} x {scaling.N} x {scaling.N} for pipe flow")
    
    return scaling


if __name__ == "__main__":
    # Run example
    scaling = example_water_pipe()
