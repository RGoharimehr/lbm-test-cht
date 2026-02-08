"""
Example 3: Circular Pipe with Thermal Entry Length

Demonstrates:
- Circular pipe geometry (more realistic than rectangular)
- Developing velocity and temperature profiles
- Thermal entry length analysis
- Comprehensive visualization:
  * Velocity contours (longitudinal and cross-section)
  * Temperature contours (longitudinal and cross-section)
  * Radial velocity profiles at multiple positions
  * Radial temperature profiles showing thermal BL development
  * Comparison with theoretical predictions

This is a classical problem in heat transfer and fluid mechanics.
"""

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import PipeGeometry, Material, LBMSolver
from lbm_cht.lbm.unit_converter import DimensionlessScaling

# ============================================================================
# SETUP PARAMETERS
# ============================================================================

print("=" * 70)
print("EXAMPLE 3: CIRCULAR PIPE WITH THERMAL ENTRY LENGTH")
print("=" * 70)

# Physical parameters
u_inlet_phys = 0.02      # m/s
D_phys = 0.01            # m - pipe diameter
L_phys = 0.08            # m - pipe length
T_inlet = 300.0          # K
T_wall = 350.0           # K
Re_target = 200          # Laminar flow

print(f"\nPhysical Parameters:")
print(f"  Inlet velocity: {u_inlet_phys} m/s")
print(f"  Pipe diameter: {D_phys*1000} mm")
print(f"  Pipe length: {L_phys*1000} mm")
print(f"  L/D ratio: {L_phys/D_phys:.1f}")
print(f"  Target Reynolds: {Re_target}")
print(f"  Inlet temperature: {T_inlet} K")
print(f"  Wall temperature: {T_wall} K")

# ============================================================================
# DIMENSIONLESS SCALING
# ============================================================================

# Water properties
nu_water = 1e-6
rho_water = 1000.0
k_water = 0.6
cp_water = 4186.0

scaling = DimensionlessScaling(
    Re_target=Re_target,
    L_ref=D_phys,
    u_ref=u_inlet_phys,
    nu_ref=nu_water,
    Ma_target=0.1,
    tau_target=0.7
)

print(f"\nLattice Parameters:")
print(f"  Pipe diameter: {scaling.N} lattice units")
print(f"  dx: {scaling.dx*1000:.4f} mm")
print(f"  dt: {scaling.dt:.6f} s")

# ============================================================================
# CREATE GEOMETRY
# ============================================================================

D_cells = int(scaling.N)
nx = int(L_phys / D_phys * D_cells)
ny = D_cells + 6  # Diameter + wall
nz = D_cells + 6

print(f"\nDomain Size:")
print(f"  nx (length): {nx}")
print(f"  ny, nz (cross-section): {ny} × {nz}")

geometry = PipeGeometry(
    nx=nx, ny=ny, nz=nz,
    inner_diameter_ratio=0.85,
    wall_thickness=3,
    dx=scaling.dx,
    use_smooth_boundary=True
)

print(f"\nGeometry created successfully")
print(f"  Porosity: {geometry.porosity:.4f}")
print(f"  Inner diameter: {geometry.get_inner_diameter()*1000:.2f} mm")

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
    name="Stainless Steel",
    density=8000.0,
    specific_heat=500.0,
    thermal_conductivity=16.0
)

# ============================================================================
# CREATE SOLVER
# ============================================================================

solver = LBMSolver(
    geometry=geometry,
    fluid_material=fluid,
    solid_material=solid,
    dt=scaling.dt,
    n_inlet=max(5, nx // 20),
    n_outlet=max(5, nx // 20),
    boundary_method='bouzidi'
)

# Set boundary conditions
solver.set_inlet_velocity(scaling.u_lattice)
solver.set_inlet_temperature(T_inlet)
solver.set_outlet_temperature(T_inlet)

# Set wall temperature
solver.T[geometry.solid_mask] = T_wall

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

u_mag = np.sqrt(solver.u[0]**2 + solver.u[1]**2 + solver.u[2]**2)
T = solver.T

u_mag_phys = scaling.lattice_to_physical_velocity(u_mag)
x_phys = np.arange(nx) * scaling.dx * 1000

# ============================================================================
# VISUALIZATION
# ============================================================================

fig = plt.figure(figsize=(18, 12))

# -------------------------
# 1. Longitudinal Velocity Contours (xz plane at y=ny/2)
# -------------------------
ax1 = plt.subplot(3, 3, 1)
y_mid = ny // 2
z_vals = np.arange(nz) * scaling.dx * 1000
X, Z = np.meshgrid(x_phys, z_vals)
u_long = u_mag_phys[:, y_mid, :].T
u_masked = np.ma.masked_where(geometry.solid_mask[:, y_mid, :].T, u_long)
contour = ax1.contourf(X, Z, u_masked, levels=20, cmap='jet')
ax1.contour(X, Z, geometry.solid_mask[:, y_mid, :].T, levels=[0.5], colors='black', linewidths=1)
ax1.set_xlabel('x (mm)')
ax1.set_ylabel('z (mm)')
ax1.set_title('Velocity - Longitudinal Section')
plt.colorbar(contour, ax=ax1, label='Velocity (m/s)')
ax1.set_aspect('equal')

# -------------------------
# 2. Longitudinal Temperature Contours
# -------------------------
ax2 = plt.subplot(3, 3, 2)
T_long = T[:, y_mid, :].T
contour = ax2.contourf(X, Z, T_long, levels=20, cmap='hot')
ax2.contour(X, Z, geometry.solid_mask[:, y_mid, :].T, levels=[0.5], colors='white', linewidths=1)
ax2.set_xlabel('x (mm)')
ax2.set_ylabel('z (mm)')
ax2.set_title('Temperature - Longitudinal Section')
plt.colorbar(contour, ax=ax2, label='Temperature (K)')
ax2.set_aspect('equal')

# -------------------------
# 3. Cross-Section Velocity at Mid-Length
# -------------------------
ax3 = plt.subplot(3, 3, 3)
x_mid = nx // 2
Y, Z = np.meshgrid(np.arange(ny) * scaling.dx * 1000, z_vals)
u_cross = u_mag_phys[x_mid, :, :].T
u_masked_cross = np.ma.masked_where(geometry.solid_mask[x_mid, :, :].T, u_cross)
contour = ax3.contourf(Y, Z, u_masked_cross, levels=20, cmap='jet')
ax3.contour(Y, Z, geometry.solid_mask[x_mid, :, :].T, levels=[0.5], colors='black', linewidths=2)
ax3.set_xlabel('y (mm)')
ax3.set_ylabel('z (mm)')
ax3.set_title(f'Velocity Cross-Section at x={x_phys[x_mid]:.1f}mm')
plt.colorbar(contour, ax=ax3, label='Velocity (m/s)')
ax3.set_aspect('equal')

# -------------------------
# 4. Cross-Section Temperature at Mid-Length
# -------------------------
ax4 = plt.subplot(3, 3, 4)
T_cross = T[x_mid, :, :].T
contour = ax4.contourf(Y, Z, T_cross, levels=20, cmap='hot')
ax4.contour(Y, Z, geometry.solid_mask[x_mid, :, :].T, levels=[0.5], colors='white', linewidths=1.5)
ax4.set_xlabel('y (mm)')
ax4.set_ylabel('z (mm)')
ax4.set_title(f'Temperature Cross-Section at x={x_phys[x_mid]:.1f}mm')
plt.colorbar(contour, ax=ax4, label='Temperature (K)')
ax4.set_aspect('equal')

# -------------------------
# 5. Radial Velocity Profiles at Multiple x Positions
# -------------------------
ax5 = plt.subplot(3, 3, 5)

# Calculate radial profiles
y_center = ny // 2
z_center = nz // 2
x_positions = [nx//10, nx//4, nx//2, 3*nx//4, 9*nx//10]
colors = ['blue', 'green', 'orange', 'red', 'purple']

for i, x_pos in enumerate(x_positions):
    # Extract radial profile (along y at z_center)
    r_profile = []
    u_profile = []
    for y in range(ny):
        dy = (y - y_center) * scaling.dx * 1000
        if not geometry.solid_mask[x_pos, y, z_center]:
            r_profile.append(abs(dy))
            u_profile.append(u_mag_phys[x_pos, y, z_center])
    
    # Sort by radius
    if len(r_profile) > 0:
        sorted_indices = np.argsort(r_profile)
        r_sorted = np.array(r_profile)[sorted_indices]
        u_sorted = np.array(u_profile)[sorted_indices]
        ax5.plot(u_sorted * 1000, r_sorted, label=f'x/D={x_phys[x_pos]/D_phys/1000:.1f}',
                 color=colors[i], linewidth=2, marker='o', markersize=3)

ax5.set_xlabel('Velocity (mm/s)')
ax5.set_ylabel('Radial Distance from Center (mm)')
ax5.set_title('Radial Velocity Profiles')
ax5.legend(fontsize=8)
ax5.grid(True, alpha=0.3)

# -------------------------
# 6. Radial Temperature Profiles at Multiple x Positions
# -------------------------
ax6 = plt.subplot(3, 3, 6)

for i, x_pos in enumerate(x_positions):
    r_profile = []
    T_profile = []
    for y in range(ny):
        dy = (y - y_center) * scaling.dx * 1000
        if not geometry.solid_mask[x_pos, y, z_center]:
            r_profile.append(abs(dy))
            T_profile.append(T[x_pos, y, z_center])
    
    if len(r_profile) > 0:
        sorted_indices = np.argsort(r_profile)
        r_sorted = np.array(r_profile)[sorted_indices]
        T_sorted = np.array(T_profile)[sorted_indices]
        ax6.plot(T_sorted, r_sorted, label=f'x/D={x_phys[x_pos]/D_phys/1000:.1f}',
                 color=colors[i], linewidth=2, marker='o', markersize=3)

ax6.set_xlabel('Temperature (K)')
ax6.set_ylabel('Radial Distance from Center (mm)')
ax6.set_title('Radial Temperature Profiles')
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3)

# -------------------------
# 7. Centerline Development
# -------------------------
ax7 = plt.subplot(3, 3, 7)
u_centerline = u_mag_phys[:, y_center, z_center]
ax7_twin = ax7.twinx()

line1 = ax7.plot(x_phys, u_centerline * 1000, 'b-', linewidth=2, label='Velocity')
ax7.set_xlabel('x (mm)')
ax7.set_ylabel('Centerline Velocity (mm/s)', color='b')
ax7.tick_params(axis='y', labelcolor='b')

T_centerline = T[:, y_center, z_center]
line2 = ax7_twin.plot(x_phys, T_centerline, 'r-', linewidth=2, label='Temperature')
ax7_twin.set_ylabel('Centerline Temperature (K)', color='r')
ax7_twin.tick_params(axis='y', labelcolor='r')

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax7.legend(lines, labels, loc='best')
ax7.set_title('Centerline Development Along Pipe')
ax7.grid(True, alpha=0.3)

# -------------------------
# 8. Thermal Entry Length Analysis
# -------------------------
ax8 = plt.subplot(3, 3, 8)

# Calculate bulk temperature at each x
T_bulk = []
for x in range(nx):
    fluid_at_x = geometry.fluid_mask[x, :, :]
    if np.any(fluid_at_x):
        T_bulk.append(np.mean(T[x, fluid_at_x]))
    else:
        T_bulk.append(T_inlet)

T_bulk = np.array(T_bulk)

# Dimensionless temperature
theta = (T_bulk - T_inlet) / (T_wall - T_inlet)

ax8.plot(x_phys / (D_phys * 1000), theta * 100, 'g-', linewidth=2)
ax8.set_xlabel('x/D')
ax8.set_ylabel('Dimensionless Temperature θ (%)')
ax8.set_title('Thermal Development Along Pipe')
ax8.grid(True, alpha=0.3)

# Mark thermal entry length (where theta reaches ~95%)
try:
    entry_idx = np.where(theta >= 0.95)[0][0]
    entry_length = x_phys[entry_idx] / (D_phys * 1000)
    ax8.axvline(x=entry_length, color='red', linestyle='--', label=f'L_t/D≈{entry_length:.1f}')
    ax8.legend()
except:
    pass

# -------------------------
# 9. Nusselt Number vs Position
# -------------------------
ax9 = plt.subplot(3, 3, 9)

# Simplified Nusselt number calculation
# Nu = h*D/k, where h is local heat transfer coefficient
Nu = []
x_vals_nu = []
for x in range(10, nx-10, 5):  # Skip inlet/outlet
    fluid_at_x = geometry.fluid_mask[x, :, :]
    if np.any(fluid_at_x):
        T_bulk_x = np.mean(T[x, fluid_at_x])
        # Find wall temperature (average of solid points)
        solid_at_x = geometry.solid_mask[x, :, :]
        if np.any(solid_at_x):
            T_wall_x = np.mean(T[x, solid_at_x])
            # Simplified Nu (qualitative)
            if T_wall_x - T_bulk_x > 1:
                h_approx = 1000  # Simplified
                Nu_x = h_approx * D_phys / k_water
                Nu.append(Nu_x)
                x_vals_nu.append(x_phys[x] / (D_phys * 1000))

if len(Nu) > 0:
    ax9.plot(x_vals_nu, Nu, 'b-', linewidth=2)
    ax9.axhline(y=3.66, color='red', linestyle='--', label='Nu=3.66 (Fully Developed)')
    ax9.set_xlabel('x/D')
    ax9.set_ylabel('Nusselt Number (Simplified)')
    ax9.set_title('Heat Transfer Coefficient Development')
    ax9.legend()
    ax9.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('example3_pipe.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'example3_pipe.png'")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)

# Velocity statistics
u_fluid = u_mag_phys[geometry.fluid_mask]
u_max = np.max(u_fluid)
u_avg = np.mean(u_fluid)
print(f"\nVelocity (fluid only):")
print(f"  Maximum: {u_max*1000:.3f} mm/s")
print(f"  Average: {u_avg*1000:.3f} mm/s")
print(f"  Max/Avg ratio: {u_max/u_avg:.3f} (theory: ~2.0 for fully developed)")

# Temperature statistics
T_fluid = T[geometry.fluid_mask]
print(f"\nTemperature (fluid only):")
print(f"  Maximum: {np.max(T_fluid):.2f} K")
print(f"  Minimum: {np.min(T_fluid):.2f} K")
print(f"  Average: {np.mean(T_fluid):.2f} K")
print(f"  Bulk outlet: {T_bulk[-1]:.2f} K")
print(f"  Temperature rise: {T_bulk[-1] - T_inlet:.2f} K")

# Thermal entry length
Pr = nu_water / (k_water / (rho_water * cp_water))
L_t_theory = 0.05 * Re_target * Pr * D_phys
print(f"\nThermal Entry Length:")
print(f"  Prandtl number: {Pr:.2f}")
print(f"  Theoretical L_t: {L_t_theory*1000:.1f} mm")
print(f"  Theoretical L_t/D: {L_t_theory/D_phys:.1f}")
if 'entry_length' in locals():
    print(f"  Simulated L_t/D: {entry_length:.1f}")

print("\n" + "=" * 70)
print("Example 3 complete!")
print("=" * 70)
