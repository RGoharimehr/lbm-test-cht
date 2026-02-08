"""
Example 1: Channel Geometry with Water Flow
Demonstrates simple channel geometry with water as the working fluid.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import ChannelGeometry, Material, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials


def main():
    print("="*60)
    print("Example 1: Channel Geometry with Water Flow")
    print("="*60)
    
    # Create geometry
    print("\n1. Creating channel geometry...")
    nx, ny, nz = 50, 30, 30
    geometry = ChannelGeometry(
        nx=nx, ny=ny, nz=nz,
        channel_height_ratio=0.6,
        channel_width_ratio=0.6,
        dx=0.001  # 1mm spacing
    )
    
    print(f"   Grid dimensions: {nx} x {ny} x {nz}")
    print(f"   Porosity: {geometry.get_porosity():.3f}")
    print(f"   Surface area: {geometry.get_surface_area():.6f} m²")
    
    # Define materials
    print("\n2. Defining materials...")
    fluid = CommonMaterials.water(temperature=300)
    solid = CommonMaterials.aluminum()
    
    print(f"   Fluid: {fluid.name}")
    print(f"     - Density: {fluid.density:.2f} kg/m³")
    print(f"     - Thermal conductivity: {fluid.thermal_conductivity:.3f} W/m·K")
    print(f"     - Viscosity: {fluid.viscosity:.6e} Pa·s")
    
    print(f"   Solid: {solid.name}")
    print(f"     - Density: {solid.density:.2f} kg/m³")
    print(f"     - Thermal conductivity: {solid.thermal_conductivity:.1f} W/m·K")
    
    # Create solver
    print("\n3. Creating LBM solver...")
    solver = LBMSolver(
        geometry=geometry,
        fluid_material=fluid,
        solid_material=solid,
        dx=0.001,
        dt=1e-5,
        n_inlet=5,   # 5 nodes for inlet
        n_outlet=5   # 5 nodes for outlet
    )
    
    print(f"   Relaxation time (fluid): {solver.tau_f:.4f}")
    print(f"   Relaxation time (thermal, fluid): {solver.tau_g_fluid:.4f}")
    print(f"   Relaxation time (thermal, solid): {solver.tau_g_solid:.4f}")
    
    # Print boundary configuration
    solver.print_boundary_info()
    
    # Set boundary conditions using helper methods
    print("\n4. Setting boundary conditions...")
    # Hot inlet (left side)
    solver.set_inlet_temperature(350.0)  # 350K
    # Cold outlet (right side)
    solver.set_outlet_temperature(300.0)  # 300K
    # Inlet velocity for forced convection
    u_inlet = 0.01  # 0.01 m/s in x-direction
    solver.set_inlet_velocity(u_inlet)
    
    # Reinitialize distributions after setting BC
    print("\n5. Reinitializing distributions...")
    solver.initialize_distributions()
    
    # Create visualizer
    print("\n6. Creating visualizations...")
    visualizer = Visualizer(geometry, solver)
    
    # Plot initial geometry
    fig1 = visualizer.plot_geometry_slice(axis='z', position=nz//2)
    plt.savefig('example1_geometry.png', dpi=150, bbox_inches='tight')
    print("   Saved: example1_geometry.png")
    plt.close(fig1)
    
    # Plot initial temperature
    fig2 = visualizer.plot_temperature_slice(axis='z', position=nz//2)
    plt.savefig('example1_temperature_initial.png', dpi=150, bbox_inches='tight')
    print("   Saved: example1_temperature_initial.png")
    plt.close(fig2)
    
    # Run simulation
    print("\n7. Running simulation with forced convection...")
    num_steps = 100
    print(f"   Number of steps: {num_steps}")
    print(f"   Inlet velocity: {u_inlet} m/s")
    
    for step in range(num_steps):
        solver.step()
        if (step + 1) % 20 == 0:
            print(f"   Step {step + 1}/{num_steps} completed")
    
    # Plot final temperature
    fig3 = visualizer.plot_temperature_slice(axis='z', position=nz//2)
    plt.savefig('example1_temperature_final.png', dpi=150, bbox_inches='tight')
    print("   Saved: example1_temperature_final.png")
    plt.close(fig3)
    
    # Plot final velocity
    fig4 = visualizer.plot_velocity_slice(axis='z', position=nz//2, skip=3)
    plt.savefig('example1_velocity.png', dpi=150, bbox_inches='tight')
    print("   Saved: example1_velocity.png")
    plt.close(fig4)
    
    print("\n" + "="*60)
    print("Example 1 completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
