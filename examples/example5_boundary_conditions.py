"""
Example 5: Boundary Conditions - Wall Thickness and Inlet/Outlet Configuration
Demonstrates how to specify and configure boundary conditions in LBM CHT.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import ChannelGeometry, DuctGeometry, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials


def example_wall_thickness():
    """Demonstrate different wall thickness configurations."""
    print("="*70)
    print("Part 1: Wall Thickness Configuration")
    print("="*70)
    
    # Test different wall thicknesses
    wall_thicknesses = [2, 4, 6]
    
    print("\nCreating ducts with different wall thicknesses:")
    print("-" * 70)
    
    for wt in wall_thicknesses:
        geom = DuctGeometry(
            nx=60, ny=40, nz=40,
            wall_thickness=wt,
            dx=0.001  # 1mm lattice spacing
        )
        
        print(f"\nWall thickness: {wt} lattice units")
        print(f"  Physical thickness: {wt * 0.001 * 1000:.2f} mm")
        print(f"  Porosity: {geom.get_porosity():.4f}")
        print(f"  Solid volume: {geom.get_solid_volume():.6f} m³")
        print(f"  Surface area: {geom.get_surface_area():.4f} m²")


def example_inlet_outlet_nodes():
    """Demonstrate inlet/outlet node configuration."""
    print("\n\n" + "="*70)
    print("Part 2: Inlet/Outlet Node Configuration")
    print("="*70)
    
    # Domain setup
    nx, ny, nz = 100, 40, 40
    dx = 0.001  # 1mm spacing
    
    print(f"\nDomain: {nx}×{ny}×{nz} lattice units")
    print(f"Physical size: {nx*dx*1000:.1f}×{ny*dx*1000:.1f}×{nz*dx*1000:.1f} mm")
    
    # Create geometry
    geometry = ChannelGeometry(
        nx=nx, ny=ny, nz=nz,
        channel_height_ratio=0.6,
        channel_width_ratio=0.6,
        dx=dx
    )
    
    # Materials
    fluid = CommonMaterials.water(temperature=300)
    solid = CommonMaterials.aluminum()
    
    # Test different inlet/outlet sizes
    bc_configs = [
        {"name": "Auto (default)", "n_inlet": None, "n_outlet": None},
        {"name": "Small (5 nodes)", "n_inlet": 5, "n_outlet": 5},
        {"name": "Medium (8 nodes)", "n_inlet": 8, "n_outlet": 8},
        {"name": "Large (12 nodes)", "n_inlet": 12, "n_outlet": 12},
    ]
    
    print("\n" + "-" * 70)
    print("Testing different inlet/outlet configurations:")
    print("-" * 70)
    
    for config in bc_configs:
        print(f"\n{config['name']}:")
        
        # Create solver
        solver = LBMSolver(
            geometry, fluid, solid,
            dx=dx, dt=1e-5,
            n_inlet=config['n_inlet'],
            n_outlet=config['n_outlet']
        )
        
        print(f"  Inlet: {solver.n_inlet} nodes ({solver.n_inlet/nx*100:.1f}% of domain)")
        print(f"  Outlet: {solver.n_outlet} nodes ({solver.n_outlet/nx*100:.1f}% of domain)")
        print(f"  Main domain: {nx - solver.n_inlet - solver.n_outlet} nodes")
        
        # Calculate physical dimensions
        inlet_length = solver.n_inlet * dx * 1000
        outlet_length = solver.n_outlet * dx * 1000
        main_length = (nx - solver.n_inlet - solver.n_outlet) * dx * 1000
        
        print(f"  Physical lengths:")
        print(f"    Inlet: {inlet_length:.2f} mm")
        print(f"    Outlet: {outlet_length:.2f} mm")
        print(f"    Main: {main_length:.2f} mm")


def example_complete_setup():
    """Demonstrate complete boundary condition setup."""
    print("\n\n" + "="*70)
    print("Part 3: Complete Boundary Condition Setup")
    print("="*70)
    
    # Domain configuration
    nx, ny, nz = 80, 40, 40
    dx = 0.001  # 1mm
    
    # Create geometry
    geometry = ChannelGeometry(
        nx=nx, ny=ny, nz=nz,
        channel_height_ratio=0.6,
        channel_width_ratio=0.6,
        dx=dx
    )
    
    # Materials
    fluid = CommonMaterials.water(temperature=300)
    solid = CommonMaterials.aluminum()
    
    # Create solver with explicit inlet/outlet configuration
    print("\nCreating solver with inlet/outlet configuration...")
    solver = LBMSolver(
        geometry, fluid, solid,
        dx=dx, dt=1e-5,
        T_initial=300.0,
        n_inlet=8,   # 8 nodes for inlet
        n_outlet=8   # 8 nodes for outlet
    )
    
    # Print boundary information
    solver.print_boundary_info()
    
    # Set boundary conditions using helper methods
    print("Setting boundary conditions...")
    T_inlet = 350.0  # Hot inlet
    T_outlet = 300.0  # Ambient outlet
    
    solver.set_inlet_temperature(T_inlet)
    solver.set_outlet_temperature(T_outlet)
    
    # Reinitialize distributions after setting BC
    print("\nReinitializing distribution functions...")
    solver.initialize_distributions()
    
    # Run simulation
    print("\nRunning simulation (500 steps)...")
    solver.run(num_steps=500)
    print("Simulation complete!")
    
    # Analyze results
    print("\nTemperature field analysis:")
    T = solver.get_temperature()
    
    # Check inlet region
    T_inlet_avg = np.mean(T[:solver.n_inlet, :, :])
    print(f"  Average inlet temperature: {T_inlet_avg:.2f}K (set: {T_inlet}K)")
    
    # Check outlet region
    T_outlet_avg = np.mean(T[-solver.n_outlet:, :, :])
    print(f"  Average outlet temperature: {T_outlet_avg:.2f}K (set: {T_outlet}K)")
    
    # Check main domain
    T_main_avg = np.mean(T[solver.n_inlet:-solver.n_outlet, :, :])
    print(f"  Average main domain temperature: {T_main_avg:.2f}K")
    
    # Create visualizations
    print("\nCreating visualizations...")
    visualizer = Visualizer(geometry, solver)
    
    # Temperature slice
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    
    # Get temperature slice
    z_mid = nz // 2
    T_slice = T[:, :, z_mid]
    
    # Plot temperature
    im = ax1.imshow(T_slice.T, origin='lower', cmap='hot', 
                    interpolation='bilinear', aspect='auto',
                    extent=[0, nx, 0, ny])
    ax1.set_xlabel('X (lattice units)')
    ax1.set_ylabel('Y (lattice units)')
    ax1.set_title('Temperature Distribution with Inlet/Outlet Regions')
    
    # Mark inlet and outlet regions
    ax1.axvline(x=solver.n_inlet, color='cyan', linestyle='--', linewidth=2, 
                label=f'Inlet region (x<{solver.n_inlet})')
    ax1.axvline(x=nx - solver.n_outlet, color='blue', linestyle='--', linewidth=2,
                label=f'Outlet region (x>{nx - solver.n_outlet})')
    
    ax1.legend(loc='upper right')
    plt.colorbar(im, ax=ax1, label='Temperature (K)')
    
    plt.tight_layout()
    plt.savefig('example5_boundary_conditions.png', dpi=150, bbox_inches='tight')
    print("  Saved: example5_boundary_conditions.png")
    
    # Profile along centerline
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    y_center = ny // 2
    T_profile = T[:, y_center, z_mid]
    x_coords = np.arange(nx) * dx * 1000  # Convert to mm
    
    ax2.plot(x_coords, T_profile, 'b-', linewidth=2, label='Temperature')
    ax2.axvline(x=solver.n_inlet * dx * 1000, color='cyan', 
                linestyle='--', label='Inlet boundary')
    ax2.axvline(x=(nx - solver.n_outlet) * dx * 1000, color='blue',
                linestyle='--', label='Outlet boundary')
    
    # Shade inlet/outlet regions
    ax2.axvspan(0, solver.n_inlet * dx * 1000, alpha=0.2, color='cyan', 
                label='Inlet region')
    ax2.axvspan((nx - solver.n_outlet) * dx * 1000, nx * dx * 1000, 
                alpha=0.2, color='blue', label='Outlet region')
    
    ax2.set_xlabel('X position (mm)')
    ax2.set_ylabel('Temperature (K)')
    ax2.set_title('Temperature Profile Along Centerline')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig('example5_temperature_profile.png', dpi=150, bbox_inches='tight')
    print("  Saved: example5_temperature_profile.png")
    
    plt.close('all')


def main():
    print("\n" + "="*70)
    print("Example 5: Boundary Conditions Configuration")
    print("="*70)
    
    # Run all examples
    example_wall_thickness()
    example_inlet_outlet_nodes()
    example_complete_setup()
    
    print("\n" + "="*70)
    print("Example completed successfully!")
    print("\nKey Takeaways:")
    print("  1. Wall thickness specified in lattice units at geometry creation")
    print("  2. Inlet/outlet nodes auto-calculated (8% of nx) or manually set")
    print("  3. Use solver.set_inlet_temperature() and set_outlet_temperature()")
    print("  4. Use solver.print_boundary_info() to see configuration")
    print("  5. Recommended: 5-10 nodes for inlet/outlet, 3-5 for wall thickness")
    print("\nSee BOUNDARY_CONDITIONS.md for detailed guidelines.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
