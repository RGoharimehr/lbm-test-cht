"""
3D Poiseuille (Channel) Flow Validation

This example validates the LBM implementation against the analytical solution
for pressure-driven flow between parallel plates.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.flow_solver import FlowSolver
from src.geometry import GyroidGenerator
from src.utils import (calculate_reynolds_number, analytical_poiseuille_velocity,
                       create_output_directory)
from src.visualization import plot_velocity_slice, plot_velocity_profile


def run_channel_flow(nx=128, ny=32, nz=32, Re=10, n_steps=10000):
    """
    Run 3D Poiseuille flow simulation.
    
    Parameters:
    -----------
    nx, ny, nz : int
        Domain dimensions (x: flow direction, z: channel height)
    Re : float
        Reynolds number
    n_steps : int
        Number of time steps
    """
    print(f"\n{'='*60}")
    print(f"3D Poiseuille Channel Flow - Re = {Re}")
    print(f"Domain: {nx} x {ny} x {nz}")
    print(f"{'='*60}\n")
    
    # Physical parameters
    H = nz - 4  # Channel height (excluding walls)
    U_max = 0.1  # Maximum velocity (lattice units)
    
    # Calculate viscosity from Reynolds number
    # Re = U_avg * H / nu, where U_avg = 2/3 * U_max for Poiseuille
    U_avg = 2.0/3.0 * U_max
    viscosity = U_avg * H / Re
    
    print(f"Channel height: {H}")
    print(f"Max velocity: {U_max}")
    print(f"Avg velocity: {U_avg}")
    print(f"Viscosity: {viscosity}\n")
    
    # Create solver
    solver = FlowSolver(nx, ny, nz, viscosity=viscosity)
    
    # Create channel geometry
    geom = GyroidGenerator(nx, ny, nz)
    solid_mask = geom.generate_channel(channel_height=H)
    solver.set_solid_mask(solid_mask)
    
    # Apply body force to drive the flow
    # F = dp/dx (pressure gradient)
    force_magnitude = 8.0 * viscosity * U_max / (H**2)
    external_force = np.zeros((nx, ny, nz, 3))
    external_force[:, :, :, 0] = force_magnitude  # Force in x-direction
    solver.set_external_force(external_force)
    
    # Initialize with zero velocity
    solver.initialize()
    
    # Create output directory
    output_dir = create_output_directory(f'output/channel_Re{Re}')
    
    # Callback for monitoring
    def callback(solver, step):
        if step % 1000 == 0:
            u_mag = solver.get_velocity_magnitude()
            print(f"Step {step}: max |u| = {u_mag.max():.6f}")
    
    # Run simulation
    print("Running simulation...")
    history = solver.run(n_steps, output_interval=100, callback=callback)
    
    # Extract velocity profile at channel center
    mid_x = nx // 2
    mid_y = ny // 2
    z_coords = np.arange(nz)
    u_profile = solver.u[mid_x, mid_y, :, 0]  # u-velocity
    
    # Analytical solution (parabolic profile)
    z_fluid = z_coords[~solid_mask[mid_x, mid_y, :]]
    z_rel = z_fluid - z_fluid.min()
    u_analytical = U_max * 4.0 * z_rel * (H - z_rel) / (H**2)
    u_numerical = u_profile[~solid_mask[mid_x, mid_y, :]]
    
    # Calculate error
    error = np.abs(u_numerical - u_analytical).max()
    error_percent = 100.0 * error / U_max
    
    print(f"\nValidation Results:")
    print(f"Max velocity (numerical): {u_numerical.max():.6f}")
    print(f"Max velocity (analytical): {u_analytical.max():.6f}")
    print(f"Max absolute error: {error:.6e}")
    print(f"Max relative error: {error_percent:.2f}%")
    
    # Plot results
    plot_velocity_slice(solver.u, z_slice=nz//2,
                       title=f'Channel Flow Re={Re}',
                       filename=f'{output_dir}/velocity_slice.png')
    
    plot_velocity_profile(z_rel, u_numerical, u_analytical,
                         title=f'Velocity Profile Comparison - Re={Re}',
                         filename=f'{output_dir}/profile_comparison.png')
    
    print(f"\nSimulation complete! Results saved to {output_dir}/")
    
    return solver, error


if __name__ == "__main__":
    # Run channel flow at different Reynolds numbers
    Re_values = [10, 50, 100]
    
    for Re in Re_values:
        solver, error = run_channel_flow(nx=128, ny=32, nz=32, 
                                        Re=Re, n_steps=10000)
        print(f"\nCompleted Re = {Re}, Error = {error:.2e}\n")
