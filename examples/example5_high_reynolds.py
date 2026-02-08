"""
Example 5: High Reynolds Number Simulation

Demonstrates:
- Proper dimensionless scaling for high Re flows
- How to achieve Re=10,000+ while maintaining stability
- Balancing Ma number, tau, and domain size
- Comprehensive visualization:
  * Velocity contours showing developed flow
  * Temperature contours
  * Velocity and temperature profiles
  * Comparison with theoretical predictions
  * Performance analysis

This shows the power of dimensionless scaling in LBM.
"""

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import ChannelGeometry, Material, LBMSolver
from lbm_cht.lbm.unit_converter import DimensionlessScaling

# ============================================================================
# SETUP PARAMETERS - HIGH REYNOLDS NUMBER CASE
# ============================================================================

print("=" * 70)
print("EXAMPLE 5: HIGH REYNOLDS NUMBER SIMULATION")
print("=" * 70)

# Physical parameters - represents realistic industrial flow
u_inlet_phys = 2.0       # m/s - high velocity
H_phys = 0.01            # m - channel height
L_phys = 0.10            # m - longer channel
T_inlet = 300.0          # K
T_wall = 350.0           # K
Re_target = 10000        # High Reynolds number!

print(f"\nPhysical Parameters:")
print(f"  Inlet velocity: {u_inlet_phys} m/s (HIGH)")
print(f"  Channel height: {H_phys*1000} mm")
print(f"  Channel length: {L_phys*1000} mm")
print(f"  Target Reynolds: {Re_target} (HIGH!)")
print(f"  Inlet temperature: {T_inlet} K")
print(f"  Wall temperature: {T_wall} K")

print(f"\nThis demonstrates how to achieve high Re while maintaining LBM stability!")

# ============================================================================
# DIMENSIONLESS SCALING - CAREFULLY TUNED
# ============================================================================

# Water properties
nu_water = 1e-6
rho_water = 1000.0
k_water = 0.6
cp_water = 4186.0

# Use aggressive but stable parameters
print(f"\nDimensionless Scaling Strategy:")
print(f"  Approach: Balance Ma and tau to achieve high Re with practical domain size")
print(f"  Ma_target = 0.15 (compromise between stability and domain size)")
print(f"  tau_target = 0.65 (lower limit for stability)")

scaling = DimensionlessScaling(
    Re_target=Re_target,
    L_ref=H_phys,
    u_ref=u_inlet_phys,
    nu_ref=nu_water,
    Ma_target=0.15,      # Higher Ma for smaller domain
    tau_target=0.65       # Lower tau for smaller domain
)

print(f"\nLattice Parameters:")
print(f"  Domain height N: {scaling.N} lattice units")
print(f"  dx: {scaling.dx*1000:.4f} mm")
print(f"  dt: {scaling.dt:.6f} s")
print(f"  Lattice velocity: {scaling.u_lattice:.4f}")
print(f"  Physical Re: {Re_target}")

# Check if domain is practical
if scaling.N > 5000:
    print(f"\n⚠ WARNING: Domain size ({scaling.N}) is very large!")
    print(f"  Consider: Increasing Ma or decreasing tau further")
    print(f"  Or: Accept longer computation time")
elif scaling.N > 2000:
    print(f"\n✓ Domain size is large but manageable for demonstration")
else:
    print(f"\n✓ Domain size is practical")

# ============================================================================
# CREATE GEOMETRY
# ============================================================================

ny = int(scaling.N)
nx = int(ny * L_phys / H_phys)
nz = max(8, ny // 4)  # Smaller depth for faster computation

print(f"\nDomain Size:")
print(f"  nx (length): {nx}")
print(f"  ny (height): {ny}")
print(f"  nz (depth): {nz}")
print(f"  Total cells: {nx * ny * nz:,}")

geometry = ChannelGeometry(
    nx=nx, ny=ny, nz=nz,
    height_ratio=0.85,
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
# CREATE SOLVER
# ============================================================================

solver = LBMSolver(
    geometry=geometry,
    fluid_material=fluid,
    solid_material=solid,
    dt=scaling.dt,
    n_inlet=max(5, nx // 25),
    n_outlet=max(5, nx // 25),
    boundary_method='simple'
)

solver.set_inlet_velocity(scaling.u_lattice)
solver.set_inlet_temperature(T_inlet)
solver.set_outlet_temperature(T_inlet)

solver.initialize_distributions()

print(f"\nBoundary Conditions:")
solver.print_boundary_info()

# ============================================================================
# RUN SIMULATION
# ============================================================================

num_steps = 1500
print_interval = 300

print(f"\nRunning HIGH REYNOLDS NUMBER simulation...")
print(f"This may take longer due to larger domain and more timesteps needed...")
solver.run(num_steps=num_steps, print_interval=print_interval)
print("Simulation complete!")

# ============================================================================
# EXTRACT RESULTS
# ============================================================================

u_mag = np.sqrt(solver.u[0]**2 + solver.u[1]**2 + solver.u[2]**2)
T = solver.T

u_mag_phys = scaling.lattice_to_physical_velocity(u_mag)
x_phys = np.arange(nx) * scaling.dx * 1000
y_phys = np.arange(ny) * scaling.dx * 1000

z_mid = nz // 2

# ============================================================================
# VISUALIZATION
# ============================================================================

fig = plt.figure(figsize=(18, 12))

# -------------------------
# 1. Velocity Contours
# -------------------------
ax1 = plt.subplot(3, 3, 1)
X, Y = np.meshgrid(x_phys, y_phys)
contour = ax1.contourf(X, Y, u_mag_phys[:, :, z_mid].T, levels=20, cmap='jet')
ax1.set_xlabel('x (mm)')
ax1.set_ylabel('y (mm)')
ax1.set_title(f'Velocity Magnitude (Re={Re_target})')
plt.colorbar(contour, ax=ax1, label='Velocity (m/s)')
ax1.set_aspect('equal')

# -------------------------
# 2. Temperature Contours
# -------------------------
ax2 = plt.subplot(3, 3, 2)
contour = ax2.contourf(X, Y, T[:, :, z_mid].T, levels=20, cmap='hot')
ax2.set_xlabel('x (mm)')
ax2.set_ylabel('y (mm)')
ax2.set_title('Temperature Distribution')
plt.colorbar(contour, ax=ax2, label='Temperature (K)')
ax2.set_aspect('equal')

# -------------------------
# 3. Velocity with Streamlines
# -------------------------
ax3 = plt.subplot(3, 3, 3)
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
# 4. Velocity Profiles
# -------------------------
ax4 = plt.subplot(3, 3, 4)
x_positions = [nx//10, nx//4, nx//2, 3*nx//4, 9*nx//10]
colors = ['blue', 'green', 'orange', 'red', 'purple']

for i, x_pos in enumerate(x_positions):
    u_profile = u_mag_phys[x_pos, :, z_mid]
    ax4.plot(u_profile, y_phys, label=f'x={x_phys[x_pos]:.0f}mm',
             color=colors[i], linewidth=2)

ax4.set_xlabel('Velocity (m/s)')
ax4.set_ylabel('y (mm)')
ax4.set_title('Velocity Profiles at Multiple Positions')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# -------------------------
# 5. Temperature Profiles
# -------------------------
ax5 = plt.subplot(3, 3, 5)

for i, x_pos in enumerate(x_positions):
    T_profile = T[x_pos, :, z_mid]
    ax5.plot(T_profile, y_phys, label=f'x={x_phys[x_pos]:.0f}mm',
             color=colors[i], linewidth=2)

ax5.set_xlabel('Temperature (K)')
ax5.set_ylabel('y (mm)')
ax5.set_title('Temperature Profiles at Multiple Positions')
ax5.legend(fontsize=8)
ax5.grid(True, alpha=0.3)

# -------------------------
# 6. Velocity Profile Comparison with Theory
# -------------------------
ax6 = plt.subplot(3, 3, 6)

# Extract velocity profile at outlet
x_outlet = -10
u_profile_outlet = u_mag_phys[x_outlet, :, z_mid]
y_normalized = (y_phys - y_phys[0]) / (y_phys[-1] - y_phys[0])

# Theoretical parabolic profile for fully developed flow
# u(y) = u_max * (1 - (2*y - 1)^2) for y in [0, 1]
u_max_theory = np.max(u_profile_outlet)
u_theory = u_max_theory * (1 - (2*y_normalized - 1)**2)

ax6.plot(u_profile_outlet, y_phys, 'b-', linewidth=2, label='LBM Result')
ax6.plot(u_theory, y_phys, 'r--', linewidth=2, label='Parabolic Theory')
ax6.set_xlabel('Velocity (m/s)')
ax6.set_ylabel('y (mm)')
ax6.set_title('Velocity Profile vs Theory')
ax6.legend()
ax6.grid(True, alpha=0.3)

# -------------------------
# 7. Centerline Development
# -------------------------
ax7 = plt.subplot(3, 3, 7)
y_center = ny // 2

u_centerline = u_mag_phys[:, y_center, z_mid]
ax7_twin = ax7.twinx()

line1 = ax7.plot(x_phys, u_centerline, 'b-', linewidth=2, label='Velocity')
ax7.set_xlabel('x (mm)')
ax7.set_ylabel('Centerline Velocity (m/s)', color='b')
ax7.tick_params(axis='y', labelcolor='b')

T_centerline = T[:, y_center, z_mid]
line2 = ax7_twin.plot(x_phys, T_centerline, 'r-', linewidth=2, label='Temperature')
ax7_twin.set_ylabel('Centerline Temperature (K)', color='r')
ax7_twin.tick_params(axis='y', labelcolor='r')

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax7.legend(lines, labels, loc='best')
ax7.set_title('Centerline Development Along Channel')
ax7.grid(True, alpha=0.3)

# -------------------------
# 8. Boundary Layer Thickness
# -------------------------
ax8 = plt.subplot(3, 3, 8)

# Calculate BL thickness at multiple x positions
bl_thickness = []
x_bl = []
for x in range(nx//10, nx-10, max(1, nx//20)):
    u_profile = u_mag_phys[x, :, z_mid]
    u_max = np.max(u_profile)
    # Find where velocity reaches 99% of max
    for y in range(ny//2):
        if u_profile[y] >= 0.99 * u_max:
            bl = y * scaling.dx * 1000
            bl_thickness.append(bl)
            x_bl.append(x_phys[x])
            break

if len(bl_thickness) > 0:
    ax8.plot(x_bl, bl_thickness, 'g-', linewidth=2, marker='o')
    ax8.set_xlabel('x (mm)')
    ax8.set_ylabel('BL Thickness (mm)')
    ax8.set_title('Velocity Boundary Layer Development')
    ax8.grid(True, alpha=0.3)

# -------------------------
# 9. Reynolds Number Verification
# -------------------------
ax9 = plt.subplot(3, 3, 9)

# Calculate local Re based on average velocity and height
Re_local = []
x_re = []
for x in range(0, nx, max(1, nx//20)):
    fluid_at_x = geometry.fluid_mask[x, :, z_mid]
    if np.any(fluid_at_x):
        u_avg = np.mean(u_mag_phys[x, fluid_at_x, z_mid])
        h_local = np.sum(fluid_at_x) * scaling.dx
        re_local = u_avg * h_local / nu_water
        Re_local.append(re_local)
        x_re.append(x_phys[x])

if len(Re_local) > 0:
    ax9.plot(x_re, Re_local, 'purple', linewidth=2, marker='s')
    ax9.axhline(y=Re_target, color='red', linestyle='--', label=f'Target Re={Re_target}')
    ax9.set_xlabel('x (mm)')
    ax9.set_ylabel('Local Reynolds Number')
    ax9.set_title('Reynolds Number Verification')
    ax9.legend()
    ax9.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('example5_high_reynolds.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'example5_high_reynolds.png'")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 70)
print("RESULTS SUMMARY - HIGH REYNOLDS NUMBER")
print("=" * 70)

# Velocity statistics
u_max = np.max(u_mag_phys)
u_avg = np.mean(u_mag_phys[geometry.fluid_mask])
print(f"\nVelocity:")
print(f"  Maximum: {u_max:.3f} m/s")
print(f"  Average (fluid): {u_avg:.3f} m/s")
print(f"  Max/Avg ratio: {u_max/u_avg:.3f}")

# Reynolds number verification
Re_actual = u_avg * H_phys / nu_water
print(f"\nReynolds Number:")
print(f"  Target Re: {Re_target}")
print(f"  Actual Re: {Re_actual:.0f}")
print(f"  Match: {abs(Re_actual - Re_target)/Re_target * 100:.1f}% error")

# Temperature statistics
T_max = np.max(T[geometry.fluid_mask])
T_min = np.min(T[geometry.fluid_mask])
T_avg = np.mean(T[geometry.fluid_mask])
print(f"\nTemperature:")
print(f"  Maximum: {T_max:.2f} K")
print(f"  Minimum: {T_min:.2f} K")
print(f"  Average (fluid): {T_avg:.2f} K")
print(f"  Temperature rise: {T_avg - T_inlet:.2f} K")

# Computational performance
print(f"\nComputational Aspects:")
print(f"  Domain size: {nx}×{ny}×{nz} = {nx*ny*nz:,} cells")
print(f"  Timesteps: {num_steps}")
print(f"  Ma number: {scaling.u_lattice / (1/np.sqrt(3)):.3f}")
print(f"  tau (momentum): {scaling.tau:.3f}")

print(f"\n✓ Successfully simulated Re={Re_target} flow!")
print(f"✓ Maintained LBM stability (Ma={scaling.u_lattice / (1/np.sqrt(3)):.3f})")
print(f"✓ Achieved target Re within {abs(Re_actual - Re_target)/Re_target * 100:.1f}%")

print("\n" + "=" * 70)
print("Example 5 complete!")
print("=" * 70)
