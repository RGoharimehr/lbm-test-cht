"""
Example 2: Pin Fins with CoolProp Material and Forced Convection
Demonstrates pin fins geometry with material properties from CoolProp
and forced convection cooling simulation.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import PinFinsGeometry, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials, CoolPropMaterial

# Check if CoolProp is available
try:
    from lbm_cht.materials.coolprop_material import COOLPROP_AVAILABLE
except ImportError:
    COOLPROP_AVAILABLE = False


def main():
    print("="*70)
    print("Example 2: Pin Fins with CoolProp Material and Forced Convection")
    print("="*70)
    
    # Create geometry
    print("\n1. Creating pin fins geometry...")
    nx, ny, nz = 60, 40, 40
    geometry = PinFinsGeometry(
        nx=nx, ny=ny, nz=nz,
        num_pins_y=4,
        num_pins_z=4,
        pin_diameter=6,
        dx=0.001,  # 1mm spacing
        use_smooth_boundary=True  # Use smooth boundaries for better accuracy
    )
    
    print(f"   Grid dimensions: {nx} x {ny} x {nz}")
    print(f"   Porosity: {geometry.get_porosity():.3f}")
    print(f"   Surface area: {geometry.get_surface_area():.6f} m²")
    
    # Define materials
    print("\n2. Defining materials...")
    
    if COOLPROP_AVAILABLE:
        print("   Using CoolProp for fluid properties...")
        try:
            # Use R134a refrigerant at 300K
            fluid = CoolPropMaterial('R134a', temperature=300, pressure=101325)
            print(f"   Fluid: {fluid.name}")
            print(f"     - Density: {fluid.density:.2f} kg/m³")
            print(f"     - Thermal conductivity: {fluid.thermal_conductivity:.4f} W/m·K")
            print(f"     - Viscosity: {fluid.viscosity:.6e} Pa·s")
            print(f"     - Prandtl number: {fluid.get_prandtl_number():.4f}")
        except Exception as e:
            print(f"   CoolProp error: {e}")
            print("   Falling back to Air...")
            fluid = CommonMaterials.air(temperature=300)
    else:
        print("   CoolProp not available, using Air...")
        fluid = CommonMaterials.air(temperature=300)
        print(f"   Fluid: {fluid.name}")
        print(f"     - Density: {fluid.density:.2f} kg/m³")
        print(f"     - Thermal conductivity: {fluid.thermal_conductivity:.4f} W/m·K")
    
    solid = CommonMaterials.copper()
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
        T_initial=300.0,
        n_inlet=5,
        n_outlet=5
    )
    
    # Print boundary configuration
    solver.print_boundary_info()
    
    # Set boundary conditions
    print("\n4. Setting boundary conditions for forced convection...")
    T_hot = 350.0  # Hot pins (heated from base)
    T_inlet = 300.0  # Cool inlet air
    u_inlet = 0.02  # 0.02 m/s inlet velocity (forced convection)
    
    solver.set_inlet_temperature(T_inlet)
    solver.set_outlet_temperature(T_inlet)
    solver.set_inlet_velocity(u_inlet)
    
    # Initialize hot pins (set solid temperature high)
    solver.T[:, :, :][geometry.get_solid_mask()] = T_hot
    
    # Reinitialize distributions
    print("\n5. Reinitializing distributions...")
    solver.initialize_distributions()
    
    # Create visualizer
    print("\n6. Creating initial geometry visualizations...")
    visualizer = Visualizer(geometry, solver)
    
    # Plot geometry from different angles
    fig1 = visualizer.plot_geometry_slice(axis='x', position=nx//2)
    plt.savefig('example2_geometry_x.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_geometry_x.png")
    plt.close(fig1)
    
    fig2 = visualizer.plot_geometry_slice(axis='z', position=nz//2)
    plt.savefig('example2_geometry_z.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_geometry_z.png")
    plt.close(fig2)
    
    # Plot initial temperature
    fig3 = visualizer.plot_temperature_slice(axis='z', position=nz//2)
    plt.savefig('example2_temperature_initial.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_temperature_initial.png")
    plt.close(fig3)
    
    # Run simulation
    print("\n7. Running forced convection simulation...")
    num_steps = 150
    print(f"   Number of steps: {num_steps}")
    print(f"   Inlet velocity: {u_inlet} m/s")
    print(f"   Pin temperature: {T_hot} K")
    print(f"   Inlet temperature: {T_inlet} K")
    
    for step in range(num_steps):
        solver.step()
        if (step + 1) % 30 == 0:
            print(f"   Step {step + 1}/{num_steps} completed")
    
    # Plot final temperature
    print("\n8. Creating final visualizations...")
    fig4 = visualizer.plot_temperature_slice(axis='z', position=nz//2)
    plt.savefig('example2_temperature_final.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_temperature_final.png")
    plt.close(fig4)
    
    # Plot temperature at different x positions
    fig5, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    for idx, x_pos in enumerate([10, 30, 50]):
        T_slice = solver.T[x_pos, :, :]
        im = axes[idx].imshow(T_slice.T, origin='lower', cmap='hot', 
                              vmin=T_inlet, vmax=T_hot)
        axes[idx].set_title(f'Temperature at x={x_pos} ({x_pos*0.001*1000:.0f}mm)')
        axes[idx].set_xlabel('Y')
        axes[idx].set_ylabel('Z')
        plt.colorbar(im, ax=axes[idx], label='Temperature (K)')
    
    plt.tight_layout()
    plt.savefig('example2_temperature_evolution.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_temperature_evolution.png")
    plt.close(fig5)
    
    # Plot velocity field
    fig6 = visualizer.plot_velocity_slice(axis='z', position=nz//2, skip=2)
    plt.savefig('example2_velocity.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_velocity.png")
    plt.close(fig6)
    
    print("\n" + "="*70)
    print("Example 2 completed successfully!")
    print("\nKey Results:")
    T_avg_inlet = np.mean(solver.T[:5, :, :])
    T_avg_outlet = np.mean(solver.T[-5:, :, :])
    T_max = np.max(solver.T)
    print(f"  Average inlet temperature: {T_avg_inlet:.2f} K")
    print(f"  Average outlet temperature: {T_avg_outlet:.2f} K")
    print(f"  Maximum temperature: {T_max:.2f} K")
    print(f"  Temperature rise: {T_avg_outlet - T_avg_inlet:.2f} K")
    print("="*70)


if __name__ == "__main__":
    main()
