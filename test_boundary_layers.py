"""
Detailed test for boundary layer development in LBM solver.
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
print("Testing Boundary Layer Development")
print("="*60)

# Create channel geometry - longer for better boundary layer development
print("\n1. Creating geometry...")
geometry = ChannelGeometry(
    nx=80, ny=30, nz=20,
    dx=0.001,  # 1mm spacing
    channel_height_ratio=0.6,
    channel_width_ratio=0.8
)

# Simple fluid material (water-like, but with higher viscosity for visible BL)
print("2. Setting up materials...")
fluid = Material(
    name="Test Fluid",
    density=1000.0,
    viscosity=0.005,  # Higher viscosity to see boundary layer better
    thermal_conductivity=0.6,
    specific_heat=4200.0
)

# Solid material
solid = Material(
    name="Test Solid",
    density=2700.0,
    viscosity=0.001,
    thermal_conductivity=50.0,  # Lower than before to see thermal BL
    specific_heat=900.0
)

# Create solver
print("3. Creating solver...")
solver = LBMSolver(
    geometry, fluid, solid,
    dx=0.001,
    dt=0.0001,
    T_initial=300.0,
    n_inlet=6,
    n_outlet=6
)

# Set boundary conditions
print("\n4. Setting boundary conditions...")
solver.set_inlet_temperature(330.0)  # Hot inlet
solver.set_outlet_temperature(300.0)  # Cool outlet
solver.set_inlet_velocity(0.005)  # 5 mm/s for visible flow

solver.print_boundary_info()

# Reinitialize
print("\n5. Initializing distributions...")
solver.initialize_distributions()

# Run longer simulation for boundary layer to develop
print("\n6. Running simulation...")
solver.run(num_steps=500, print_interval=100)

# Get results
T = solver.get_temperature()
u = solver.get_velocity()
u_mag = np.sqrt(np.sum(u**2, axis=0))

print("\n7. Analyzing boundary layers...")
print(f"  Temperature range: {np.min(T):.2f}K to {np.max(T):.2f}K")
print(f"  Velocity range: {np.min(u_mag):.6f} to {np.max(u_mag):.6f} m/s")

# Check for boundary layer development
mid_x = geometry.nx // 2
mid_z = geometry.nz // 2

# Velocity profile across channel height
fluid_mask = geometry.get_fluid_mask()
y_indices = np.arange(geometry.ny)
u_profile = u[0, mid_x, :, mid_z]

# Find channel boundaries
fluid_y = fluid_mask[mid_x, :, mid_z]
channel_y_min = np.argmax(fluid_y)
channel_y_max = len(fluid_y) - np.argmax(fluid_y[::-1]) - 1

# Check if velocity is higher in center than at walls
u_center = u[0, mid_x, (channel_y_min + channel_y_max)//2, mid_z]
u_wall = u[0, mid_x, channel_y_min+1, mid_z]

print(f"\n  Velocity boundary layer check:")
print(f"    Center velocity: {u_center:.6f} m/s")
print(f"    Near-wall velocity: {u_wall:.6f} m/s")
print(f"    Ratio: {u_center/u_wall:.2f}" if u_wall > 1e-10 else "    Ratio: ∞")

if u_center > u_wall * 1.5:
    print("    ✓ Velocity boundary layer is developing!")
else:
    print("    ✗ Weak or no velocity boundary layer")

# Temperature profile
T_profile = T[mid_x, :, mid_z]
T_center = T[mid_x, (channel_y_min + channel_y_max)//2, mid_z]
T_wall = T[mid_x, channel_y_min+1, mid_z]

print(f"\n  Thermal boundary layer check:")
print(f"    Center temperature: {T_center:.2f}K")
print(f"    Near-wall temperature: {T_wall:.2f}K")
print(f"    Difference: {abs(T_center - T_wall):.2f}K")

if abs(T_center - T_wall) > 1.0:
    print("    ✓ Thermal boundary layer is developing!")
else:
    print("    ✗ Weak or no thermal boundary layer")

# Create detailed visualization
print("\n8. Creating detailed visualization...")
fig = plt.figure(figsize=(16, 12))

# Middle z-slice
mid_z = geometry.nz // 2

# 1. Temperature field
ax1 = plt.subplot(3, 3, 1)
im1 = ax1.imshow(T[:, :, mid_z].T, origin='lower', cmap='hot', aspect='auto',
                  vmin=300, vmax=330)
ax1.set_title('Temperature Field (K)', fontsize=12, fontweight='bold')
ax1.set_xlabel('x (lattice units)')
ax1.set_ylabel('y (lattice units)')
plt.colorbar(im1, ax=ax1, label='Temperature (K)')

# 2. Velocity magnitude field
ax2 = plt.subplot(3, 3, 2)
im2 = ax2.imshow(u_mag[:, :, mid_z].T, origin='lower', cmap='viridis', aspect='auto')
ax2.set_title('Velocity Magnitude (m/s)', fontsize=12, fontweight='bold')
ax2.set_xlabel('x (lattice units)')
ax2.set_ylabel('y (lattice units)')
plt.colorbar(im2, ax=ax2, label='|u| (m/s)')

# 3. Velocity vectors
ax3 = plt.subplot(3, 3, 3)
skip = 3  # Skip points for clarity
X, Y = np.meshgrid(np.arange(0, geometry.nx, skip), np.arange(0, geometry.ny, skip))
U = u[0, ::skip, ::skip, mid_z].T
V = u[1, ::skip, ::skip, mid_z].T
ax3.quiver(X, Y, U, V, scale=0.05)
ax3.set_title('Velocity Vectors', fontsize=12, fontweight='bold')
ax3.set_xlabel('x (lattice units)')
ax3.set_ylabel('y (lattice units)')
ax3.set_aspect('equal')

# 4. Velocity profile at mid-x (shows boundary layer!)
ax4 = plt.subplot(3, 3, 4)
ax4.plot(u[0, mid_x, :, mid_z] * 1000, y_indices, 'b-', linewidth=2, label='u_x')
ax4.axhline(channel_y_min, color='r', linestyle='--', alpha=0.5, label='Wall')
ax4.axhline(channel_y_max, color='r', linestyle='--', alpha=0.5)
ax4.set_xlabel('Velocity (mm/s)')
ax4.set_ylabel('y position (lattice units)')
ax4.set_title(f'Velocity Profile at x={mid_x}', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()

# 5. Temperature profile at mid-x (shows thermal boundary layer!)
ax5 = plt.subplot(3, 3, 5)
ax5.plot(T[mid_x, :, mid_z], y_indices, 'r-', linewidth=2, label='Temperature')
ax5.axhline(channel_y_min, color='b', linestyle='--', alpha=0.5, label='Wall')
ax5.axhline(channel_y_max, color='b', linestyle='--', alpha=0.5)
ax5.set_xlabel('Temperature (K)')
ax5.set_ylabel('y position (lattice units)')
ax5.set_title(f'Temperature Profile at x={mid_x}', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)
ax5.legend()

# 6. Temperature along centerline
ax6 = plt.subplot(3, 3, 6)
center_y = (channel_y_min + channel_y_max) // 2
ax6.plot(T[:, center_y, mid_z], 'r-', linewidth=2)
ax6.axvline(solver.n_inlet, color='cyan', linestyle='--', alpha=0.5, label='Inlet end')
ax6.axvline(geometry.nx - solver.n_outlet, color='blue', linestyle='--', alpha=0.5, label='Outlet start')
ax6.set_xlabel('x position (lattice units)')
ax6.set_ylabel('Temperature (K)')
ax6.set_title('Temperature Along Centerline', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3)
ax6.legend()

# 7. Velocity development along channel
ax7 = plt.subplot(3, 3, 7)
ax7.plot(u[0, :, center_y, mid_z] * 1000, 'b-', linewidth=2)
ax7.axvline(solver.n_inlet, color='cyan', linestyle='--', alpha=0.5, label='Inlet end')
ax7.axvline(geometry.nx - solver.n_outlet, color='blue', linestyle='--', alpha=0.5, label='Outlet start')
ax7.set_xlabel('x position (lattice units)')
ax7.set_ylabel('Velocity (mm/s)')
ax7.set_title('Velocity Along Centerline', fontsize=12, fontweight='bold')
ax7.grid(True, alpha=0.3)
ax7.legend()

# 8. Velocity profile evolution
ax8 = plt.subplot(3, 3, 8)
x_positions = [15, 30, 45, 60]
colors = ['blue', 'green', 'orange', 'red']
for x_pos, color in zip(x_positions, colors):
    ax8.plot(u[0, x_pos, :, mid_z] * 1000, y_indices, color=color, 
             linewidth=2, label=f'x={x_pos}', alpha=0.7)
ax8.axhline(channel_y_min, color='k', linestyle='--', alpha=0.3)
ax8.axhline(channel_y_max, color='k', linestyle='--', alpha=0.3)
ax8.set_xlabel('Velocity (mm/s)')
ax8.set_ylabel('y position')
ax8.set_title('Velocity Profile Evolution', fontsize=12, fontweight='bold')
ax8.grid(True, alpha=0.3)
ax8.legend()

# 9. Temperature contours
ax9 = plt.subplot(3, 3, 9)
contour = ax9.contourf(T[:, :, mid_z].T, levels=20, cmap='hot', origin='lower')
ax9.contour(T[:, :, mid_z].T, levels=10, colors='black', alpha=0.3, 
            linewidths=0.5, origin='lower')
ax9.set_title('Temperature Contours (Smoothness Check)', fontsize=12, fontweight='bold')
ax9.set_xlabel('x (lattice units)')
ax9.set_ylabel('y (lattice units)')
plt.colorbar(contour, ax=ax9, label='Temperature (K)')

plt.suptitle('LBM Boundary Layer Development Analysis', fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig('boundary_layer_analysis.png', dpi=150, bbox_inches='tight')
print("  Saved: boundary_layer_analysis.png")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
