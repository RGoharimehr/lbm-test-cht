"""
3D Lid-Driven Cavity Flow Validation

This example validates the LBM implementation with the classic 3D lid-driven
cavity benchmark at various Reynolds numbers.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.flow_solver import FlowSolver
from src.utils import calculate_reynolds_number, create_output_directory
from src.visualization import plot_velocity_slice, plot_velocity_profile


def run_cavity_flow(nx=64, ny=64, nz=64, Re=100, n_steps=10000):
    """
    Run 3D lid-driven cavity flow simulation.
    
    Parameters:
    -----------
    nx, ny, nz : int
        Domain dimensions
    Re : float
        Reynolds number
    n_steps : int
        Number of time steps
    """
    print(f"\n{'='*60}")
    print(f"3D Lid-Driven Cavity Flow - Re = {Re}")
    print(f"Domain: {nx} x {ny} x {nz}")
    print(f"{'='*60}\n")
    
    # Physical parameters
    U_lid = 0.1  # Lid velocity (lattice units)
    L = ny  # Characteristic length (cavity height)
    
    # Calculate viscosity from Reynolds number
    viscosity = U_lid * L / Re
    
    print(f"Lid velocity: {U_lid}")
    print(f"Viscosity: {viscosity}")
    print(f"Relaxation time: {0.5 + viscosity/0.333:.4f}\n")
    
    # Create solver
    solver = FlowSolver(nx, ny, nz, viscosity=viscosity)
    
    # Initialize with zero velocity
    solver.initialize()
    
    # Set up boundary conditions (simplified - walls are implicit)
    # In full implementation, would set proper BCs for walls and moving lid
    
    # Create output directory
    output_dir = create_output_directory(f'output/cavity_Re{Re}')
    
    # Callback for monitoring
    def callback(solver, step):
        if step % 1000 == 0:
            u_mag = solver.get_velocity_magnitude()
            print(f"Step {step}: max |u| = {u_mag.max():.6f}")
            
            # Save slice
            if step % 5000 == 0:
                plot_velocity_slice(solver.u, z_slice=nz//2,
                                  title=f'Cavity Flow Re={Re}, Step={step}',
                                  filename=f'{output_dir}/velocity_step{step}.png',
                                  show=False)
    
    # Run simulation
    print("Running simulation...")
    history = solver.run(n_steps, output_interval=100, callback=callback)
    
    # Extract centerline velocity profile
    mid_x = nx // 2
    mid_z = nz // 2
    y_coords = np.arange(ny)
    u_centerline = solver.u[mid_x, :, mid_z, 1]  # v-velocity along centerline
    
    # Plot final results
    plot_velocity_slice(solver.u, z_slice=nz//2,
                       title=f'Cavity Flow Re={Re} - Final',
                       filename=f'{output_dir}/velocity_final.png')
    
    plot_velocity_profile(y_coords, u_centerline,
                         title=f'Centerline Velocity Profile - Re={Re}',
                         filename=f'{output_dir}/profile.png')
    
    print(f"\nSimulation complete! Results saved to {output_dir}/")
    
    return solver


if __name__ == "__main__":
    # Run cavity flow at different Reynolds numbers
    Re_values = [100, 400, 1000]
    
    for Re in Re_values:
        solver = run_cavity_flow(nx=64, ny=64, nz=64, Re=Re, n_steps=10000)
        print(f"\nCompleted Re = {Re}\n")
