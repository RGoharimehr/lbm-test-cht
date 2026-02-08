#!/usr/bin/env python
"""
Quick Start Script for LBM-CHT

This script demonstrates basic usage of the LBM-CHT package with a
simple channel flow example.
"""

import numpy as np
import sys
import os

# Add src to path if running from repository
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.flow_solver import FlowSolver
from src.geometry import GyroidGenerator
from src.utils import (calculate_reynolds_number, 
                       create_output_directory,
                       print_simulation_parameters)


def quick_start_example():
    """
    Run a simple channel flow simulation as a quick start demo.
    """
    print("\n" + "="*70)
    print("LBM-CHT QUICK START EXAMPLE")
    print("="*70 + "\n")
    
    # Parameters
    nx, ny, nz = 64, 32, 32  # Small domain for quick demo
    H = 24  # Channel height
    Re = 10  # Low Reynolds number for stability
    U_avg = 0.05  # Average velocity
    
    # Calculate viscosity from Re
    viscosity = U_avg * H / Re
    
    # Print simulation parameters
    params = {
        'Domain size': f'{nx} x {ny} x {nz}',
        'Channel height': H,
        'Reynolds number': Re,
        'Average velocity': U_avg,
        'Viscosity': viscosity,
    }
    print_simulation_parameters(params)
    
    # Create flow solver
    print("Creating flow solver...")
    solver = FlowSolver(nx, ny, nz, viscosity=viscosity)
    
    # Create channel geometry
    print("Generating channel geometry...")
    geom = GyroidGenerator(nx, ny, nz)
    solid_mask = geom.generate_channel(channel_height=H)
    solver.set_solid_mask(solid_mask)
    
    # Apply body force
    force_magnitude = 8.0 * viscosity * U_avg / (H**2)
    external_force = np.zeros((nx, ny, nz, 3))
    external_force[:, :, :, 0] = force_magnitude
    solver.set_external_force(external_force)
    
    # Initialize
    print("Initializing simulation...")
    solver.initialize()
    
    # Run simulation
    n_steps = 5000  # Quick demo
    print(f"\nRunning simulation for {n_steps} steps...")
    print("(This may take 30-60 seconds...)\n")
    
    def callback(solver, step):
        if step % 1000 == 0:
            u_mag = solver.get_velocity_magnitude()
            u_max = u_mag.max()
            print(f"  Step {step:5d}: max |u| = {u_max:.6f}")
    
    history = solver.run(n_steps, output_interval=100, callback=callback)
    
    # Results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    u_mag = solver.get_velocity_magnitude()
    u_avg_final = np.mean(u_mag[~solid_mask])
    u_max_final = u_mag.max()
    
    print(f"\nFinal velocity statistics:")
    print(f"  Maximum velocity: {u_max_final:.6e}")
    print(f"  Average velocity (fluid region): {u_avg_final:.6e}")
    print(f"  Final convergence error: {history[-1]:.2e}")
    
    # Calculate actual Re
    Re_actual = calculate_reynolds_number(u_avg_final, H, viscosity)
    print(f"\nDimensionless numbers:")
    print(f"  Target Re: {Re:.2f}")
    print(f"  Actual Re: {Re_actual:.2f}")
    
    print("\n" + "="*70)
    print("QUICK START COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Try other examples in examples/ directory")
    print("2. Modify parameters in this script")
    print("3. Explore the full documentation in README.md")
    print("4. Run validation cases to see analytical comparisons")
    print("\n")
    
    return solver


if __name__ == "__main__":
    solver = quick_start_example()
