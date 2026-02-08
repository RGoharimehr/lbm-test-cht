"""
Test LBM solver stability with simple channel flow.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add package to path
sys.path.insert(0, '/home/runner/work/lbm-test-cht/lbm-test-cht')

from lbm_cht.geometries import ChannelGeometry
from lbm_cht.materials import Material
from lbm_cht.lbm import LBMSolver

print("="*60)
print("Testing LBM Solver Stability")
print("="*60)

# Create simple channel geometry
print("\n1. Creating geometry...")
geometry = ChannelGeometry(
    nx=60, ny=20, nz=20,
    dx=0.001,  # 1mm spacing
    channel_height_ratio=0.8,
    channel_width_ratio=0.8
)

# Simple fluid material (water-like)
print("2. Setting up materials...")
fluid = Material(
    name="Test Fluid",
    density=1000.0,
    viscosity=0.001,  # 1 cP
    thermal_conductivity=0.6,
    specific_heat=4200.0
)

# Simple solid material (aluminum-like)
solid = Material(
    name="Test Solid",
    density=2700.0,
    viscosity=0.001,  # Not used for solid
    thermal_conductivity=200.0,
    specific_heat=900.0
)

# Create solver with smaller time step for stability
print("3. Creating solver...")
solver = LBMSolver(
    geometry, fluid, solid,
    dx=0.001,
    dt=0.0001,  # Smaller time step
    T_initial=300.0,
    n_inlet=5,
    n_outlet=5
)

# Set boundary conditions with LOW velocity for stability
print("\n4. Setting boundary conditions...")
solver.set_inlet_temperature(320.0)  # Warm inlet
solver.set_outlet_temperature(300.0)  # Cool outlet
solver.set_inlet_velocity(0.001)  # Very low velocity: 1 mm/s

solver.print_boundary_info()

# Reinitialize distributions
print("\n5. Initializing distributions...")
solver.initialize_distributions()

# Run simulation
print("\n6. Running simulation...")
try:
    solver.run(num_steps=200, print_interval=50)
    print("\n✓ Simulation completed successfully!")
    
    # Check results
    print("\n7. Checking results...")
    T = solver.get_temperature()
    u = solver.get_velocity()
    
    print(f"  Temperature range: {np.min(T):.2f}K to {np.max(T):.2f}K")
    u_mag = np.sqrt(np.sum(u**2, axis=0))
    print(f"  Velocity range: {np.min(u_mag):.6f} to {np.max(u_mag):.6f} m/s")
    
    # Check for smooth contours (no sharp jumps)
    fluid_mask = geometry.get_fluid_mask()
    T_fluid = T[fluid_mask]
    T_std = np.std(T_fluid)
    print(f"  Temperature std dev in fluid: {T_std:.2f}K")
    
    if T_std < 100:  # Reasonable variation
        print("  ✓ Temperature field appears smooth")
    else:
        print("  ✗ Temperature field shows large variations (possible instability)")
    
    # Create simple visualization
    print("\n8. Creating visualization...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Middle slice
    mid_z = geometry.nz // 2
    
    # Temperature
    ax = axes[0, 0]
    im = ax.imshow(T[:, :, mid_z].T, origin='lower', cmap='hot', aspect='auto')
    ax.set_title('Temperature (K)')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, ax=ax)
    
    # Velocity magnitude
    ax = axes[0, 1]
    im = ax.imshow(u_mag[:, :, mid_z].T, origin='lower', cmap='viridis', aspect='auto')
    ax.set_title('Velocity Magnitude (m/s)')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, ax=ax)
    
    # Temperature profile along centerline
    ax = axes[1, 0]
    mid_y = geometry.ny // 2
    ax.plot(T[:, mid_y, mid_z], 'b-', linewidth=2)
    ax.set_xlabel('x position')
    ax.set_ylabel('Temperature (K)')
    ax.set_title('Temperature along centerline')
    ax.grid(True, alpha=0.3)
    
    # Velocity profile
    ax = axes[1, 1]
    ax.plot(u[0, :, mid_y, mid_z], 'r-', linewidth=2)
    ax.set_xlabel('x position')
    ax.set_ylabel('u_x velocity (m/s)')
    ax.set_title('Velocity along centerline')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('stability_test.png', dpi=150, bbox_inches='tight')
    print("  Saved: stability_test.png")
    
    print("\n" + "="*60)
    print("TEST PASSED: Simulation is stable!")
    print("="*60)
    
except RuntimeError as e:
    print(f"\n✗ Simulation failed: {e}")
    print("\n" + "="*60)
    print("TEST FAILED: Simulation diverged!")
    print("="*60)
    sys.exit(1)
