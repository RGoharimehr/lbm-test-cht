"""
Flow Through Gyroid Structure

This example demonstrates fluid flow through a 3D gyroid structure,
calculating permeability and pressure drop.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.flow_solver import FlowSolver
from src.geometry import GyroidGenerator
from src.utils import (calculate_reynolds_number, calculate_permeability,
                       create_output_directory)
from src.visualization import plot_velocity_slice, plot_3d_geometry


def run_gyroid_flow(nx=64, ny=64, nz=64, Re=100, porosity=0.7, 
                   scale=2.0, n_steps=20000):
    """
    Run flow through gyroid structure simulation.
    
    Parameters:
    -----------
    nx, ny, nz : int
        Domain dimensions
    Re : float
        Reynolds number
    porosity : float
        Target porosity
    scale : float
        Gyroid scale (number of unit cells)
    n_steps : int
        Number of time steps
    """
    print(f"\n{'='*60}")
    print(f"Flow Through Gyroid Structure")
    print(f"Re = {Re}, Target Porosity = {porosity}")
    print(f"Domain: {nx} x {ny} x {nz}")
    print(f"{'='*60}\n")
    
    # Generate gyroid geometry
    print("Generating gyroid geometry...")
    geom = GyroidGenerator(nx, ny, nz)
    threshold, solid_mask = geom.adjust_threshold_for_porosity(
        porosity, scale=scale, surface_type='G', tolerance=0.01
    )
    
    actual_porosity = geom.calculate_porosity(solid_mask)
    print(f"Actual porosity: {actual_porosity:.4f}")
    print(f"Threshold: {threshold:.4f}\n")
    
    # Physical parameters
    U_avg = 0.05
    L = nx
    viscosity = U_avg * L / Re
    
    print(f"Average velocity: {U_avg}")
    print(f"Viscosity: {viscosity}\n")
    
    # Create solver
    solver = FlowSolver(nx, ny, nz, viscosity=viscosity)
    solver.set_solid_mask(solid_mask)
    
    # Apply body force to drive the flow
    force_magnitude = viscosity * U_avg / (L**2) * 100.0
    external_force = np.zeros((nx, ny, nz, 3))
    external_force[:, :, :, 0] = force_magnitude
    solver.set_external_force(external_force)
    
    # Initialize
    solver.initialize()
    
    # Create output directory
    output_dir = create_output_directory(f'output/gyroid_flow_Re{Re}_por{porosity:.2f}')
    
    # Save geometry
    print("Saving geometry visualization...")
    plot_3d_geometry(solid_mask, 
                    title=f'Gyroid Structure (ε={actual_porosity:.2f})',
                    filename=f'{output_dir}/geometry.png',
                    show=False)
    
    # Callback for monitoring
    def callback(solver, step):
        if step % 1000 == 0:
            u_mag = solver.get_velocity_magnitude()
            u_avg_fluid = np.mean(u_mag[~solid_mask])
            print(f"Step {step}: avg |u| (fluid) = {u_avg_fluid:.6f}")
            
            if step % 5000 == 0:
                plot_velocity_slice(solver.u, z_slice=nz//2,
                                  title=f'Gyroid Flow - Step {step}',
                                  filename=f'{output_dir}/velocity_step{step}.png',
                                  show=False)
    
    # Run simulation
    print("Running simulation...")
    history = solver.run(n_steps, output_interval=100, callback=callback)
    
    # Calculate flow characteristics
    u_mag = solver.get_velocity_magnitude()
    u_avg_fluid = np.mean(u_mag[~solid_mask])
    u_max = u_mag.max()
    
    # Estimate pressure drop (from force and velocity)
    dp = force_magnitude * nx
    
    # Calculate permeability (Darcy's law: K = μ*u*L/ΔP)
    K = calculate_permeability(u_avg_fluid, viscosity, nx, dp)
    
    print(f"\nResults:")
    print(f"Average velocity (fluid): {u_avg_fluid:.6e}")
    print(f"Maximum velocity: {u_max:.6e}")
    print(f"Pressure drop: {dp:.6e}")
    print(f"Permeability: {K:.6e}")
    print(f"Re (actual): {calculate_reynolds_number(u_avg_fluid, L, viscosity):.2f}")
    
    # Plot final results
    plot_velocity_slice(solver.u, z_slice=nz//2,
                       title=f'Gyroid Flow Re={Re} - Final',
                       filename=f'{output_dir}/velocity_final.png')
    
    # Save velocity magnitude in all three planes
    for axis, name in [(0, 'yz'), (1, 'xz'), (2, 'xy')]:
        mid_slice = solver.u.shape[axis] // 2
        if axis == 0:
            u_slice = np.sqrt(np.sum(solver.u[mid_slice, :, :, :]**2, axis=2))
        elif axis == 1:
            u_slice = np.sqrt(np.sum(solver.u[:, mid_slice, :, :]**2, axis=2))
        else:
            u_slice = np.sqrt(np.sum(solver.u[:, :, mid_slice, :]**2, axis=2))
    
    print(f"\nSimulation complete! Results saved to {output_dir}/")
    
    return solver, K


if __name__ == "__main__":
    # Run gyroid flow at different conditions
    solver, K = run_gyroid_flow(nx=64, ny=64, nz=64, 
                               Re=100, porosity=0.7, 
                               scale=2.0, n_steps=20000)
    
    print(f"\nGyroid permeability: K = {K:.6e}")
