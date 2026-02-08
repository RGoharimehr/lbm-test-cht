"""
Example 1: Channel Flow with Boundary Layer Development

Demonstrates:
- Simple channel geometry with heated walls
- Velocity boundary layer development
- Thermal boundary layer development
- Comprehensive visualization:
  * Velocity contours
  * Temperature contours
  * Velocity profiles at multiple positions
  * Temperature profiles at multiple positions

This is a fundamental case in fluid mechanics and heat transfer.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from lbm_cht import ChannelGeometry, Material, LBMSolver
from lbm_cht.lbm.unit_converter import DimensionlessScaling

# ============================================================================
# SETUP PARAMETERS
# ============================================================================

# Physical parameters
u_inlet_phys = 0.05      # m/s - inlet velocity
L_phys = 0.05            # m - channel length
H_phys = 0.01            # m - channel height
T_inlet = 300.0          # K - inlet temperature
T_wall = 350.0           # K - wall temperature
Re_target = 500          # Reynolds number

print("=" * 70)
print("EXAMPLE 1: CHANNEL FLOW WITH BOUNDARY LAYER DEVELOPMENT")
print("=" * 70)
print(f"\nPhysical Parameters:")
print(f"  Inlet velocity: {u_inlet_phys} m/s")
print(f"  Channel length: {L_phys*1000} mm")
print(f"  Channel height: {H_phys*1000} mm")
print(f"  Target Reynolds: {Re_target}")
print(f"  Inlet temperature: {T_inlet} K")
print(f"  Wall temperature: {T_wall} K")

# ============================================================================
# DIMENSIONLESS SCALING
# ============================================================================

# Material properties for water at 300K
nu_water = 1e-6          # m^2/s - kinematic viscosity
rho_water = 1000.0       # kg/m^3
k_water = 0.6            # W/(m·K)
cp_water = 4186.0        # J/(kg·K)

# Calculate scaling
scaling = DimensionlessScaling(
    Re_target=Re_target,
    L_ref=H_phys,           # Use height as reference length
    u_ref=u_inlet_phys,
    nu_ref=nu_water,
    Ma_target=0.1,
    tau_target=0.7
)

print(f"\nLattice Parameters:")
print(f"  Domain height: {scaling.N} lattice units")
print(f"  dx: {scaling.dx*1000:.4f} mm")
print(f"  dt: {scaling.dt:.6f} s")
print(f"  Lattice velocity: {scaling.u_lattice:.4f}")

# ============================================================================
# CREATE GEOMETRY
# ============================================================================

# Calculate domain size
ny = int(scaling.N)                    # Height
nx = int(ny * L_phys / H_phys)         # Length (maintain aspect ratio)
nz = max(10, ny // 3)                  # Depth (for 3D, smaller)

print(f"\nDomain Size:")
print(f"  nx (length): {nx}")
print(f"  ny (height): {ny}")
print(f"  nz (depth): {nz}")

geometry = ChannelGeometry(
    nx=nx, ny=ny, nz=nz,
    height_ratio=0.8,      # 80% fluid, 10% wall each side
    dx=scaling.dx
)

print(f"\nGeometry created successfully")
print(f"  Porosity: {geometry.porosity:.4f}")

# ============================================================================
# CREATE MATERIALS
# ============================================================================

fluid = Material(
    name="Water",
    density=rho_water,
    viscosity=nu_water * rho_water,
    specific_heat=cp_water,
    thermal_conductivity=k_water
)

solid = Material(
    name="Aluminum",
    density=2700.0,
    specific_heat=900.0,
    thermal_conductivity=200.0
)

# ============================================================================
# CREATE SOLVER AND SET BOUNDARY CONDITIONS
# ============================================================================

solver = LBMSolver(
    geometry=geometry,
    fluid_material=fluid,
    solid_material=solid,
    dt=scaling.dt,
    n_inlet=max(5, nx // 20),
    n_outlet=max(5, nx // 20),
    boundary_method='simple'
)

# Set boundary conditions
solver.set_inlet_velocity(scaling.u_lattice)
solver.set_inlet_temperature(T_inlet)
solver.set_outlet_temperature(T_inlet)

# Initialize distributions
solver.initialize_distributions()

print(f"\nBoundary Conditions:")
solver.print_boundary_info()

# ============================================================================
# RUN SIMULATION
# ============================================================================

num_steps = 2000
print_interval = 400

print(f"\nRunning simulation for {num_steps} steps...")
solver.run(num_steps=num_steps, print_interval=print_interval)
print("Simulation complete!")

# ============================================================================
# EXTRACT RESULTS
# ============================================================================

# Get fields
u_mag = np.sqrt(solver.u[0]**2 + solver.u[1]**2 + solver.u[2]**2)
T = solver.T

# Convert to physical units
u_mag_phys = scaling.lattice_to_physical_velocity(u_mag)
x_phys = np.arange(nx) * scaling.dx * 1000  # mm
y_phys = np.arange(ny) * scaling.dx * 1000  # mm

# Mid-depth slice for visualization
z_mid = nz // 2

# ============================================================================
# VISUALIZATION
# ============================================================================

fig = plt.figure(figsize=(16, 10))

# -------------------------
# 1. Velocity Contours
# -------------------------
ax1 = plt.subplot(2, 3, 1)
X, Y = np.meshgrid(x_phys, y_phys)
contour = ax1.contourf(X, Y, u_mag_phys[:, :, z_mid].T, levels=20, cmap='jet')
ax1.set_xlabel('x (mm)')
ax1.set_ylabel('y (mm)')
ax1.set_title('Velocity Magnitude Contours')
plt.colorbar(contour, ax=ax1, label='Velocity (m/s)')
ax1.set_aspect('equal')

# -------------------------
# 2. Temperature Contours
# -------------------------
ax2 = plt.subplot(2, 3, 2)
contour = ax2.contourf(X, Y, T[:, :, z_mid].T, levels=20, cmap='hot')
ax2.set_xlabel('x (mm)')
ax2.set_ylabel('y (mm)')
ax2.set_title('Temperature Contours')
plt.colorbar(contour, ax=ax2, label='Temperature (K)')
ax2.set_aspect('equal')

# -------------------------
# 3. Streamlines with Velocity
# -------------------------
ax3 = plt.subplot(2, 3, 3)
# Subsample for streamlines
skip = max(1, nx // 40)
X_sub = X[::skip, ::skip]
Y_sub = Y[::skip, ::skip]
U_sub = solver.u[0, ::skip, ::skip, z_mid].T
V_sub = solver.u[1, ::skip, ::skip, z_mid].T
U_sub_phys = scaling.lattice_to_physical_velocity(U_sub)
V_sub_phys = scaling.lattice_to_physical_velocity(V_sub)

contour = ax3.contourf(X, Y, u_mag_phys[:, :, z_mid].T, levels=20, cmap='jet', alpha=0.7)
ax3.streamplot(X_sub, Y_sub, U_sub_phys, V_sub_phys, color='white', linewidth=0.5, density=1.5)
ax3.set_xlabel('x (mm)')
ax3.set_ylabel('y (mm)')
ax3.set_title('Velocity Field with Streamlines')
plt.colorbar(contour, ax=ax3, label='Velocity (m/s)')
ax3.set_aspect('equal')

# -------------------------
# 4. Velocity Profiles at Multiple x Positions
# -------------------------
ax4 = plt.subplot(2, 3, 4)
x_positions = [nx//10, nx//4, nx//2, 3*nx//4, 9*nx//10]
colors = ['blue', 'green', 'orange', 'red', 'purple']

for i, x_pos in enumerate(x_positions):
    y_profile = y_phys
    u_profile = u_mag_phys[x_pos, :, z_mid]
    ax4.plot(u_profile * 1000, y_profile, label=f'x={x_phys[x_pos]:.1f}mm', 
             color=colors[i], linewidth=2)

ax4.set_xlabel('Velocity (mm/s)')
ax4.set_ylabel('y (mm)')
ax4.set_title('Velocity Profiles at Multiple x Positions')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# -------------------------
# 5. Temperature Profiles at Multiple x Positions
# -------------------------
ax5 = plt.subplot(2, 3, 5)

for i, x_pos in enumerate(x_positions):
    y_profile = y_phys
    T_profile = T[x_pos, :, z_mid]
    ax5.plot(T_profile, y_profile, label=f'x={x_phys[x_pos]:.1f}mm',
             color=colors[i], linewidth=2)

ax5.set_xlabel('Temperature (K)')
ax5.set_ylabel('y (mm)')
ax5.set_title('Temperature Profiles at Multiple x Positions')
ax5.legend(fontsize=8)
ax5.grid(True, alpha=0.3)

# -------------------------
# 6. Centerline Development
# -------------------------
ax6 = plt.subplot(2, 3, 6)
y_center = ny // 2

# Velocity along centerline
u_centerline = u_mag_phys[:, y_center, z_mid]
ax6_twin = ax6.twinx()

line1 = ax6.plot(x_phys, u_centerline * 1000, 'b-', linewidth=2, label='Velocity')
ax6.set_xlabel('x (mm)')
ax6.set_ylabel('Centerline Velocity (mm/s)', color='b')
ax6.tick_params(axis='y', labelcolor='b')

# Temperature along centerline
T_centerline = T[:, y_center, z_mid]
line2 = ax6_twin.plot(x_phys, T_centerline, 'r-', linewidth=2, label='Temperature')
ax6_twin.set_ylabel('Centerline Temperature (K)', color='r')
ax6_twin.tick_params(axis='y', labelcolor='r')

# Combine legends
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax6.legend(lines, labels, loc='best')
ax6.set_title('Centerline Development Along Channel')
ax6.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('example1_channel_flow.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'example1_channel_flow.png'")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)

# Velocity statistics
u_max = np.max(u_mag_phys)
u_avg = np.mean(u_mag_phys[geometry.fluid_mask])
print(f"\nVelocity:")
print(f"  Maximum: {u_max*1000:.3f} mm/s")
print(f"  Average (fluid): {u_avg*1000:.3f} mm/s")
print(f"  Max/Avg ratio: {u_max/u_avg:.3f}")

# Temperature statistics
T_max = np.max(T[geometry.fluid_mask])
T_min = np.min(T[geometry.fluid_mask])
T_avg = np.mean(T[geometry.fluid_mask])
print(f"\nTemperature:")
print(f"  Maximum: {T_max:.2f} K")
print(f"  Minimum: {T_min:.2f} K")
print(f"  Average (fluid): {T_avg:.2f} K")
print(f"  Temperature rise: {T_avg - T_inlet:.2f} K")

# Boundary layer analysis
print(f"\nBoundary Layer Development:")
# At outlet, find where velocity reaches 99% of max
x_outlet = -5
y_profile_outlet = u_mag_phys[x_outlet, :, z_mid]
u_max_outlet = np.max(y_profile_outlet)
# Find BL thickness (both sides)
y_center = ny // 2
y_vals = np.arange(ny)
# Bottom wall
for y in range(y_center):
    if y_profile_outlet[y] >= 0.99 * u_max_outlet:
        bl_bottom = y * scaling.dx * 1000
        break
# Top wall
for y in range(ny-1, y_center, -1):
    if y_profile_outlet[y] >= 0.99 * u_max_outlet:
        bl_top = (ny - y) * scaling.dx * 1000
        break
        
print(f"  Velocity BL thickness (bottom): ~{bl_bottom:.3f} mm")
print(f"  Velocity BL thickness (top): ~{bl_top:.3f} mm")

print("\n" + "=" * 70)
print("Example 1 complete!")
print("=" * 70)
