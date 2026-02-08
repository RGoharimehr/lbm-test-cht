"""
Example 6: Forced Convection - Velocity Comparison
Demonstrates the effect of different inlet velocities on heat transfer.
Compares natural convection (low velocity) vs forced convection (high velocity).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import DuctGeometry, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials


def run_simulation(u_inlet, case_name):
    """Run a simulation with specified inlet velocity."""
    print(f"\n{'='*70}")
    print(f"Case: {case_name} (u_inlet = {u_inlet} m/s)")
    print('='*70)
    
    # Create geometry
    nx, ny, nz = 80, 40, 40
    geometry = DuctGeometry(
        nx=nx, ny=ny, nz=nz,
        wall_thickness=4,
        dx=0.001
    )
    
    # Materials
    fluid = CommonMaterials.air(temperature=300)
    solid = CommonMaterials.aluminum()
    
    # Create solver
    solver = LBMSolver(
        geometry=geometry,
        fluid_material=fluid,
        solid_material=solid,
        dx=0.001,
        dt=1e-5,
        T_initial=300.0,
        n_inlet=8,
        n_outlet=8
    )
    
    # Set boundary conditions
    T_hot = 350.0
    T_cold = 300.0
    solver.set_inlet_temperature(T_cold)
    solver.set_outlet_temperature(T_cold)
    solver.set_inlet_velocity(u_inlet)
    
    # Hot walls (set wall temperature)
    solver.T[:, :4, :] = T_hot  # Bottom wall
    solver.T[:, -4:, :] = T_hot  # Top wall
    
    solver.initialize_distributions()
    
    # Run simulation
    print(f"Running simulation...")
    num_steps = 200
    for step in range(num_steps):
        solver.step()
        if (step + 1) % 50 == 0:
            print(f"  Step {step + 1}/{num_steps}")
    
    # Calculate results
    T_inlet_avg = np.mean(solver.T[:8, :, :])
    T_outlet_avg = np.mean(solver.T[-8:, :, :])
    T_rise = T_outlet_avg - T_inlet_avg
    
    print(f"\nResults:")
    print(f"  Inlet temperature: {T_inlet_avg:.2f} K")
    print(f"  Outlet temperature: {T_outlet_avg:.2f} K")
    print(f"  Temperature rise: {T_rise:.2f} K")
    
    return solver, geometry, T_rise


def main():
    print("="*70)
    print("Example 6: Forced Convection - Velocity Comparison")
    print("="*70)
    print("\nThis example demonstrates how inlet velocity affects heat transfer.")
    print("Higher velocities lead to better heat transfer (forced convection).\n")
    
    # Test different velocities
    velocities = [0.005, 0.02, 0.05]  # m/s
    case_names = ["Low Velocity (Natural)", "Medium Velocity", "High Velocity (Forced)"]
    
    results = []
    for u_inlet, case_name in zip(velocities, case_names):
        solver, geometry, T_rise = run_simulation(u_inlet, case_name)
        results.append({
            'velocity': u_inlet,
            'name': case_name,
            'solver': solver,
            'geometry': geometry,
            'T_rise': T_rise
        })
    
    # Create comparison visualizations
    print("\n" + "="*70)
    print("Creating comparison visualizations...")
    print("="*70)
    
    # 1. Temperature comparison at centerline
    fig1, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, result in enumerate(results):
        solver = result['solver']
        geometry = result['geometry']
        
        # Get temperature slice
        nz = geometry.nz
        T_slice = solver.T[:, :, nz//2]
        
        im = axes[idx].imshow(T_slice.T, origin='lower', cmap='hot',
                              vmin=300, vmax=350, aspect='auto')
        axes[idx].set_title(f"{result['name']}\nu = {result['velocity']} m/s, ΔT = {result['T_rise']:.2f}K")
        axes[idx].set_xlabel('X (lattice units)')
        axes[idx].set_ylabel('Y (lattice units)')
        plt.colorbar(im, ax=axes[idx], label='Temperature (K)')
    
    plt.tight_layout()
    plt.savefig('example6_temperature_comparison.png', dpi=150, bbox_inches='tight')
    print("  Saved: example6_temperature_comparison.png")
    plt.close(fig1)
    
    # 2. Velocity field comparison
    fig2, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, result in enumerate(results):
        solver = result['solver']
        geometry = result['geometry']
        visualizer = Visualizer(geometry, solver)
        
        # Get velocity magnitude
        nz = geometry.nz
        u_mag = np.sqrt(solver.u[0, :, :, nz//2]**2 + 
                       solver.u[1, :, :, nz//2]**2)
        
        im = axes[idx].imshow(u_mag.T, origin='lower', cmap='viridis', aspect='auto')
        axes[idx].set_title(f"{result['name']}\nu_inlet = {result['velocity']} m/s")
        axes[idx].set_xlabel('X (lattice units)')
        axes[idx].set_ylabel('Y (lattice units)')
        plt.colorbar(im, ax=axes[idx], label='Velocity Magnitude (m/s)')
    
    plt.tight_layout()
    plt.savefig('example6_velocity_comparison.png', dpi=150, bbox_inches='tight')
    print("  Saved: example6_velocity_comparison.png")
    plt.close(fig2)
    
    # 3. Temperature profile along centerline
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    for result in results:
        solver = result['solver']
        geometry = result['geometry']
        
        # Get centerline temperature
        ny, nz = geometry.ny, geometry.nz
        T_centerline = solver.T[:, ny//2, nz//2]
        x_coords = np.arange(len(T_centerline)) * 0.001 * 1000  # Convert to mm
        
        ax.plot(x_coords, T_centerline, 'o-', linewidth=2, markersize=4,
                label=f"{result['name']}: {result['velocity']} m/s (ΔT={result['T_rise']:.2f}K)")
    
    ax.set_xlabel('X position (mm)')
    ax.set_ylabel('Temperature (K)')
    ax.set_title('Temperature Profile Along Centerline')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('example6_temperature_profile.png', dpi=150, bbox_inches='tight')
    print("  Saved: example6_temperature_profile.png")
    plt.close(fig3)
    
    # 4. Summary plot
    fig4, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    velocities_plot = [r['velocity'] for r in results]
    T_rises = [r['T_rise'] for r in results]
    names = [r['name'] for r in results]
    
    # Temperature rise vs velocity
    ax1.bar(range(len(velocities_plot)), T_rises, color=['blue', 'green', 'red'])
    ax1.set_xticks(range(len(velocities_plot)))
    ax1.set_xticklabels([f"{v} m/s" for v in velocities_plot])
    ax1.set_ylabel('Temperature Rise (K)')
    ax1.set_xlabel('Inlet Velocity')
    ax1.set_title('Temperature Rise vs Inlet Velocity')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Heat transfer enhancement
    T_rise_base = T_rises[0]
    enhancement = [T / T_rise_base for T in T_rises]
    
    ax2.bar(range(len(velocities_plot)), enhancement, color=['blue', 'green', 'red'])
    ax2.set_xticks(range(len(velocities_plot)))
    ax2.set_xticklabels([f"{v} m/s" for v in velocities_plot])
    ax2.set_ylabel('Heat Transfer Enhancement Factor')
    ax2.set_xlabel('Inlet Velocity')
    ax2.set_title('Heat Transfer Enhancement (Relative to Base Case)')
    ax2.axhline(y=1.0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('example6_summary.png', dpi=150, bbox_inches='tight')
    print("  Saved: example6_summary.png")
    plt.close(fig4)
    
    # Print summary
    print("\n" + "="*70)
    print("Example 6 completed successfully!")
    print("="*70)
    print("\nSummary:")
    print(f"{'Velocity (m/s)':<20} {'Temperature Rise (K)':<25} {'Enhancement Factor':<20}")
    print("-"*70)
    for result, enh in zip(results, enhancement):
        print(f"{result['velocity']:<20.3f} {result['T_rise']:<25.2f} {enh:<20.2f}x")
    
    print("\nKey Findings:")
    print(f"  • Natural convection (low velocity): ΔT = {results[0]['T_rise']:.2f}K")
    print(f"  • Forced convection (high velocity): ΔT = {results[-1]['T_rise']:.2f}K")
    print(f"  • Enhancement factor: {enhancement[-1]:.2f}x")
    print("\n  Higher inlet velocities increase heat transfer by enhancing")
    print("  convective mixing and reducing thermal boundary layer thickness.")
    print("="*70)


if __name__ == "__main__":
    main()
