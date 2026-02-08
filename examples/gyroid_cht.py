"""
Conjugate Heat Transfer in Gyroid Structure

This is the main example demonstrating conjugate heat transfer simulation
in a 3D gyroid structure with fluid flow.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conjugate_ht import ConjugateHTSolver
from src.geometry import GyroidGenerator
from src.utils import create_output_directory
from src.visualization import (plot_velocity_slice, plot_temperature_slice,
                               plot_3d_geometry, plot_convergence_history)


def run_gyroid_cht(nx=64, ny=64, nz=64, Re=100, Pr=0.7, porosity=0.7,
                  scale=2.0, k_ratio=10.0, n_steps=30000):
    """
    Run conjugate heat transfer simulation in gyroid structure.
    
    Parameters:
    -----------
    nx, ny, nz : int
        Domain dimensions
    Re : float
        Reynolds number
    Pr : float
        Prandtl number
    porosity : float
        Target porosity
    scale : float
        Gyroid scale
    k_ratio : float
        Thermal conductivity ratio (solid/fluid)
    n_steps : int
        Number of time steps
    """
    print(f"\n{'='*60}")
    print(f"CONJUGATE HEAT TRANSFER IN GYROID STRUCTURE")
    print(f"{'='*60}")
    print(f"Reynolds number: {Re}")
    print(f"Prandtl number: {Pr}")
    print(f"Target porosity: {porosity}")
    print(f"Conductivity ratio: {k_ratio}")
    print(f"Domain: {nx} x {ny} x {nz}")
    print(f"{'='*60}\n")
    
    # Generate gyroid geometry
    print("Generating gyroid geometry...")
    geom = GyroidGenerator(nx, ny, nz)
    threshold, solid_mask = geom.adjust_threshold_for_porosity(
        porosity, scale=scale, surface_type='G', tolerance=0.01
    )
    
    actual_porosity = geom.calculate_porosity(solid_mask)
    print(f"Actual porosity: {actual_porosity:.4f}\n")
    
    # Physical parameters
    U_avg = 0.05
    L = nx
    viscosity = U_avg * L / Re
    alpha_fluid = viscosity / Pr
    alpha_solid = alpha_fluid / k_ratio  # Lower thermal diffusivity in solid
    
    print(f"Fluid Properties:")
    print(f"  Viscosity: {viscosity:.6e}")
    print(f"  Thermal diffusivity: {alpha_fluid:.6e}")
    print(f"Solid Properties:")
    print(f"  Thermal diffusivity: {alpha_solid:.6e}")
    print(f"  Conductivity ratio: {k_ratio}\n")
    
    # Create conjugate HT solver
    solver = ConjugateHTSolver(nx, ny, nz,
                               viscosity=viscosity,
                               alpha_fluid=alpha_fluid,
                               alpha_solid=alpha_solid,
                               k_ratio=k_ratio)
    
    # Set geometry
    solver.set_geometry(solid_mask)
    
    # Apply body force to drive the flow
    force_magnitude = viscosity * U_avg / (L**2) * 100.0
    external_force = np.zeros((nx, ny, nz, 3))
    external_force[:, :, :, 0] = force_magnitude
    solver.flow.set_external_force(external_force)
    
    # Initialize temperature field
    # Hot inlet (left), cold outlet (right)
    T0 = np.zeros((nx, ny, nz))
    T0[:nx//4, :, :] = 1.0  # Hot region on left
    T0[3*nx//4:, :, :] = 0.0  # Cold region on right
    
    # Gradient in between
    for i in range(nx//4, 3*nx//4):
        T0[i, :, :] = 1.0 - (i - nx//4) / (nx//2)
    
    solver.initialize(T0=T0)
    
    # Create output directory
    output_dir = create_output_directory(
        f'output/gyroid_cht_Re{Re}_Pr{Pr}_por{porosity:.2f}'
    )
    
    # Save geometry
    print("Saving geometry visualization...")
    plot_3d_geometry(solid_mask,
                    title=f'Gyroid Structure (ε={actual_porosity:.2f})',
                    filename=f'{output_dir}/geometry.png',
                    show=False)
    
    # Callback for monitoring
    def callback(solver, step):
        if step % 1000 == 0:
            u_mag = solver.flow.get_velocity_magnitude()
            u_avg_fluid = np.mean(u_mag[~solid_mask])
            T_avg = np.mean(solver.thermal.T)
            print(f"Step {step}: u_avg={u_avg_fluid:.6f}, T_avg={T_avg:.4f}")
            
            if step % 5000 == 0:
                # Save velocity slice
                plot_velocity_slice(solver.flow.u, z_slice=nz//2,
                                  title=f'Velocity - Step {step}',
                                  filename=f'{output_dir}/velocity_step{step}.png',
                                  show=False)
                
                # Save temperature slice
                plot_temperature_slice(solver.thermal.T, z_slice=nz//2,
                                     title=f'Temperature - Step {step}',
                                     filename=f'{output_dir}/temperature_step{step}.png',
                                     show=False)
    
    # Run simulation
    print("Running conjugate heat transfer simulation...")
    print("This may take several minutes...\n")
    
    history = solver.run(n_steps, output_interval=100, callback=callback)
    
    # Calculate dimensionless numbers
    u_mag = solver.flow.get_velocity_magnitude()
    u_avg_fluid = np.mean(u_mag[~solid_mask])
    
    Re_actual = solver.get_reynolds_number(u_avg_fluid, L)
    Pr_actual = solver.get_prandtl_number()
    Pe_actual = solver.get_peclet_number(u_avg_fluid, L)
    
    # Estimate Nusselt number
    T_hot = 1.0
    T_cold = 0.0
    Nu = solver.get_nusselt_number(T_hot, T_cold, L)
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Flow Characteristics:")
    print(f"  Average velocity (fluid): {u_avg_fluid:.6e}")
    print(f"  Maximum velocity: {u_mag.max():.6e}")
    print(f"  Reynolds number: {Re_actual:.2f}")
    print(f"\nThermal Characteristics:")
    print(f"  Prandtl number: {Pr_actual:.4f}")
    print(f"  Peclet number: {Pe_actual:.2f}")
    print(f"  Nusselt number: {Nu:.4f}")
    print(f"\nGeometry:")
    print(f"  Porosity: {actual_porosity:.4f}")
    print(f"  Solid volume fraction: {1-actual_porosity:.4f}")
    print(f"{'='*60}\n")
    
    # Plot final results
    plot_velocity_slice(solver.flow.u, z_slice=nz//2,
                       title=f'Final Velocity Field',
                       filename=f'{output_dir}/velocity_final.png')
    
    plot_temperature_slice(solver.thermal.T, z_slice=nz//2,
                          title=f'Final Temperature Field',
                          filename=f'{output_dir}/temperature_final.png')
    
    plot_convergence_history(history,
                            title='Convergence History',
                            filename=f'{output_dir}/convergence.png')
    
    # Save results summary
    with open(f'{output_dir}/results_summary.txt', 'w') as f:
        f.write(f"Gyroid CHT Simulation Results\n")
        f.write(f"="*50 + "\n\n")
        f.write(f"Input Parameters:\n")
        f.write(f"  Domain: {nx} x {ny} x {nz}\n")
        f.write(f"  Reynolds number: {Re}\n")
        f.write(f"  Prandtl number: {Pr}\n")
        f.write(f"  Porosity: {actual_porosity:.4f}\n")
        f.write(f"  Conductivity ratio: {k_ratio}\n\n")
        f.write(f"Results:\n")
        f.write(f"  Average velocity: {u_avg_fluid:.6e}\n")
        f.write(f"  Nusselt number: {Nu:.4f}\n")
        f.write(f"  Peclet number: {Pe_actual:.2f}\n")
    
    print(f"Simulation complete! Results saved to {output_dir}/")
    
    return solver


if __name__ == "__main__":
    # Run main gyroid CHT simulation
    solver = run_gyroid_cht(nx=64, ny=64, nz=64,
                           Re=100, Pr=0.7, porosity=0.7,
                           scale=2.0, k_ratio=10.0, n_steps=30000)
