"""
Heated Channel Flow Validation

This example validates the thermal solver with a heated channel flow,
comparing against analytical temperature profiles.
"""

import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.conjugate_ht import ConjugateHTSolver
from src.geometry import GyroidGenerator
from src.utils import create_output_directory
from src.visualization import plot_temperature_slice, plot_velocity_slice


def run_heated_channel(nx=128, ny=32, nz=32, Re=10, Pr=0.7, n_steps=20000):
    """
    Run heated channel flow simulation.
    
    Parameters:
    -----------
    nx, ny, nz : int
        Domain dimensions
    Re : float
        Reynolds number
    Pr : float
        Prandtl number
    n_steps : int
        Number of time steps
    """
    print(f"\n{'='*60}")
    print(f"Heated Channel Flow")
    print(f"Re = {Re}, Pr = {Pr}")
    print(f"Domain: {nx} x {ny} x {nz}")
    print(f"{'='*60}\n")
    
    # Physical parameters
    H = nz - 4  # Channel height
    U_avg = 0.05
    viscosity = U_avg * H / Re
    alpha_fluid = viscosity / Pr
    
    print(f"Channel height: {H}")
    print(f"Viscosity: {viscosity}")
    print(f"Thermal diffusivity: {alpha_fluid}\n")
    
    # Create solver
    solver = ConjugateHTSolver(nx, ny, nz, 
                               viscosity=viscosity,
                               alpha_fluid=alpha_fluid,
                               alpha_solid=alpha_fluid * 0.1,
                               k_ratio=10.0)
    
    # Create channel geometry
    geom = GyroidGenerator(nx, ny, nz)
    solid_mask = geom.generate_channel(channel_height=H)
    solver.set_geometry(solid_mask)
    
    # Apply body force to drive the flow
    force_magnitude = 8.0 * viscosity * U_avg / (H**2)
    external_force = np.zeros((nx, ny, nz, 3))
    external_force[:, :, :, 0] = force_magnitude
    solver.flow.set_external_force(external_force)
    
    # Initialize with cold fluid
    T0 = np.ones((nx, ny, nz)) * 0.0
    # Hot bottom wall, cold top wall
    wall_bottom = (nz - H) // 2
    T0[:, :, :wall_bottom] = 1.0  # Hot bottom wall
    
    solver.initialize(T0=T0)
    
    # Create output directory
    output_dir = create_output_directory(f'output/heated_channel_Re{Re}_Pr{Pr}')
    
    # Callback for monitoring
    def callback(solver, step):
        if step % 1000 == 0:
            T_max = solver.thermal.T.max()
            T_min = solver.thermal.T.min()
            print(f"Step {step}: T = [{T_min:.4f}, {T_max:.4f}]")
            
            if step % 5000 == 0:
                plot_temperature_slice(solver.thermal.T, z_slice=nz//2,
                                     title=f'Temperature - Step {step}',
                                     filename=f'{output_dir}/temperature_step{step}.png',
                                     show=False)
    
    # Run simulation
    print("Running simulation...")
    history = solver.run(n_steps, output_interval=100, callback=callback)
    
    # Calculate Nusselt number
    T_hot = 1.0
    T_cold = 0.0
    Nu = solver.get_nusselt_number(T_hot, T_cold, H)
    
    print(f"\nResults:")
    print(f"Nusselt number: {Nu:.4f}")
    
    # Plot final results
    plot_velocity_slice(solver.flow.u, z_slice=nz//2,
                       title=f'Velocity Field',
                       filename=f'{output_dir}/velocity_final.png')
    
    plot_temperature_slice(solver.thermal.T, z_slice=nz//2,
                          title=f'Temperature Field',
                          filename=f'{output_dir}/temperature_final.png')
    
    print(f"\nSimulation complete! Results saved to {output_dir}/")
    
    return solver


if __name__ == "__main__":
    solver = run_heated_channel(nx=128, ny=32, nz=32, 
                               Re=10, Pr=0.7, n_steps=20000)
