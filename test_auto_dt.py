"""
Test with auto-calculated time step for stability.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/runner/work/lbm-test-cht/lbm-test-cht')

from lbm_cht.geometries import ChannelGeometry
from lbm_cht.materials import Material
from lbm_cht.lbm import LBMSolver

print("="*70)
print("Testing LBM with Auto-Calculated Time Step for Stability")
print("="*70)

# Create channel geometry
print("\n1. Creating geometry...")
geometry = ChannelGeometry(
    nx=80, ny=30, nz=20,
    dx=0.001,  # 1mm spacing
    channel_height_ratio=0.6,
    channel_width_ratio=0.8
)

# Fluid material (water-like)
print("2. Setting up materials...")
fluid = Material(
    name="Water-like Fluid",
    density=1000.0,
    viscosity=0.001,  # 1 cP = 0.001 Pa·s
    thermal_conductivity=0.6,
    specific_heat=4200.0
)

# Solid material (aluminum-like)
solid = Material(
    name="Aluminum-like Solid",
    density=2700.0,
    viscosity=0.001,
    thermal_conductivity=200.0,
    specific_heat=900.0
)

# Create solver with AUTO time step
print("3. Creating solver with auto time step...")
solver = LBMSolver(
    geometry, fluid, solid,
    dx=0.001,
    dt=None,  # AUTO-CALCULATE for stability!
    T_initial=300.0,
    n_inlet=6,
    n_outlet=6
)

# Set boundary conditions
print("\n4. Setting boundary conditions...")
solver.set_inlet_temperature(330.0)
solver.set_outlet_temperature(300.0)
solver.set_inlet_velocity(0.01)  # 10 mm/s

solver.print_boundary_info()

# Initialize
print("\n5. Initializing distributions...")
solver.initialize_distributions()

# Run simulation
print("\n6. Running simulation...")
solver.run(num_steps=1000, print_interval=200)

# Analyze results
print("\n7. Analyzing results...")
T = solver.get_temperature()
u = solver.get_velocity()
u_mag = np.sqrt(np.sum(u**2, axis=0))

print(f"  Temperature range: {np.min(T):.2f}K to {np.max(T):.2f}K")
print(f"  Velocity range: {np.min(u_mag):.6f} to {np.max(u_mag):.6f} m/s")

# Check for smooth fields
fluid_mask = geometry.get_fluid_mask()
T_fluid = T[fluid_mask]
T_std = np.std(T_fluid)
print(f"  Temperature std dev: {T_std:.2f}K")

# Check boundary layers
mid_x = geometry.nx // 2
mid_z = geometry.nz // 2

# Find channel boundaries
fluid_y = fluid_mask[mid_x, :, mid_z]
channel_y_min = np.argmax(fluid_y)
channel_y_max = len(fluid_y) - np.argmax(fluid_y[::-1]) - 1
center_y = (channel_y_min + channel_y_max) // 2

# Velocity boundary layer
u_center = u[0, mid_x, center_y, mid_z]
u_wall = u[0, mid_x, channel_y_min+1, mid_z]

print(f"\n  Velocity boundary layer:")
print(f"    Center velocity: {u_center*1000:.3f} mm/s")
print(f"    Near-wall velocity: {u_wall*1000:.3f} mm/s")

if u_wall > 1e-10:
    ratio = u_center / u_wall
    print(f"    Ratio (center/wall): {ratio:.2f}")
    if ratio > 1.2:
        print("    ✓ Velocity boundary layer visible!")
    else:
        print("    ⚠ Weak velocity boundary layer")
else:
    print("    ⚠ Near-wall velocity too low to assess")

# Temperature boundary layer
T_center = T[mid_x, center_y, mid_z]
T_wall = T[mid_x, channel_y_min+1, mid_z]
T_diff = abs(T_center - T_wall)

print(f"\n  Thermal boundary layer:")
print(f"    Center temperature: {T_center:.2f}K")
print(f"    Near-wall temperature: {T_wall:.2f}K")
print(f"    Difference: {T_diff:.2f}K")

if T_diff > 1.0:
    print("    ✓ Thermal boundary layer visible!")
else:
    print("    ⚠ Weak thermal boundary layer")

# Create visualization
print("\n8. Creating visualization...")
fig = plt.figure(figsize=(16, 10))

# Temperature field
ax1 = plt.subplot(2, 3, 1)
im1 = ax1.imshow(T[:, :, mid_z].T, origin='lower', cmap='hot', aspect='auto')
ax1.set_title('Temperature Field', fontsize=12, fontweight='bold')
ax1.set_xlabel('x')
ax1.set_ylabel('y')
plt.colorbar(im1, ax=ax1, label='T (K)')

# Velocity field
ax2 = plt.subplot(2, 3, 2)
im2 = ax2.imshow(u_mag[:, :, mid_z].T, origin='lower', cmap='viridis', aspect='auto')
ax2.set_title('Velocity Magnitude', fontsize=12, fontweight='bold')
ax2.set_xlabel('x')
ax2.set_ylabel('y')
plt.colorbar(im2, ax=ax2, label='|u| (m/s)')

# Velocity profile
ax3 = plt.subplot(2, 3, 3)
y_indices = np.arange(geometry.ny)
ax3.plot(u[0, mid_x, :, mid_z] * 1000, y_indices, 'b-', linewidth=2)
ax3.axhline(channel_y_min, color='r', linestyle='--', alpha=0.5, label='Wall')
ax3.axhline(channel_y_max, color='r', linestyle='--', alpha=0.5)
ax3.set_xlabel('u_x (mm/s)')
ax3.set_ylabel('y')
ax3.set_title(f'Velocity Profile at x={mid_x}', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend()

# Temperature profile
ax4 = plt.subplot(2, 3, 4)
ax4.plot(T[mid_x, :, mid_z], y_indices, 'r-', linewidth=2)
ax4.axhline(channel_y_min, color='b', linestyle='--', alpha=0.5, label='Wall')
ax4.axhline(channel_y_max, color='b', linestyle='--', alpha=0.5)
ax4.set_xlabel('Temperature (K)')
ax4.set_ylabel('y')
ax4.set_title(f'Temperature Profile at x={mid_x}', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()

# Temperature contours
ax5 = plt.subplot(2, 3, 5)
contour = ax5.contourf(T[:, :, mid_z].T, levels=20, cmap='hot', origin='lower')
ax5.contour(T[:, :, mid_z].T, levels=10, colors='black', alpha=0.3,
            linewidths=0.5, origin='lower')
ax5.set_title('Temperature Contours', fontsize=12, fontweight='bold')
ax5.set_xlabel('x')
ax5.set_ylabel('y')
plt.colorbar(contour, ax=ax5)

# Velocity evolution
ax6 = plt.subplot(2, 3, 6)
ax6.plot(u[0, :, center_y, mid_z] * 1000, 'b-', linewidth=2)
ax6.axvline(solver.n_inlet, color='cyan', linestyle='--', alpha=0.5, label='Inlet end')
ax6.axvline(geometry.nx - solver.n_outlet, color='blue', linestyle='--', alpha=0.5, label='Outlet start')
ax6.set_xlabel('x position')
ax6.set_ylabel('u_x (mm/s)')
ax6.set_title('Velocity Along Centerline', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3)
ax6.legend()

plt.suptitle(f'LBM Simulation Results (dt={solver.dt:.6f}s, stable tau)', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('stable_simulation.png', dpi=150, bbox_inches='tight')
print("  Saved: stable_simulation.png")

# Summary
print("\n" + "="*70)
print("SIMULATION SUMMARY")
print("="*70)
print(f"Time step (dt): {solver.dt:.6f} s (auto-calculated for stability)")
print(f"Relaxation times: tau_f={solver.tau_f:.3f}, tau_g={solver.tau_g_fluid:.3f}")
print(f"Stability: {'✓ STABLE' if T_std < 50 and np.max(u_mag) < 0.1 else '✗ UNSTABLE'}")
print(f"Boundary layers: {'✓ VISIBLE' if T_diff > 1.0 and ratio > 1.2 else '⚠ WEAK'}")
print(f"Smooth contours: {'✓ YES' if T_std < 20 else '✗ NO'}")
print("="*70)
