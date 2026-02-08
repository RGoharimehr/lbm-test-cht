"""
Example 4: Kelvin Cell Heat Exchanger

Demonstrates:
- Complex 3D Kelvin cell geometry (periodic cellular structure)
- Advanced flow patterns through porous structure
- Enhanced heat transfer in periodic structures
- Comprehensive 3D visualization:
  * Velocity contours through structure
  * Temperature contours showing heat distribution
  * Velocity profiles at multiple positions
  * Temperature profiles showing thermal development
  * Comparison with pin fins performance

This represents an advanced heat exchanger design.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from lbm_cht import KelvinCellsGeometry, Material, LBMSolver
from lbm_cht.lbm.unit_converter import DimensionlessScaling

# ============================================================================
# SETUP PARAMETERS
# ============================================================================

print("=" * 70)
print("EXAMPLE 4: KELVIN CELL HEAT EXCHANGER")
print("=" * 70)

# Physical parameters
u_inlet_phys = 0.08      # m/s
L_phys = 0.05            # m
cell_size = 0.01         # m - Kelvin cell size
T_inlet = 300.0          # K
T_structure = 350.0      # K
Re_target = 400

print(f"\nPhysical Parameters:")
print(f"  Inlet velocity: {u_inlet_phys} m/s")
print(f"  Domain length: {L_phys*1000} mm")
print(f"  Cell size: {cell_size*1000} mm")
print(f"  Target Reynolds: {Re_target}")
print(f"  Inlet temperature: {T_inlet} K")
print(f"  Structure temperature: {T_structure} K")

# ============================================================================
# DIMENSIONLESS SCALING
# ============================================================================

# Air properties
nu_air = 1.5e-5
rho_air = 1.2
k_air = 0.026
cp_air = 1005.0

scaling = DimensionlessScaling(
    Re_target=Re_target,
    L_ref=cell_size,
    u_ref=u_inlet_phys,
    nu_ref=nu_air,
    Ma_target=0.15,  # Slightly higher for practical domain size
    tau_target=0.65
)

print(f"\nLattice Parameters:")
print(f"  Cell size: {scaling.N} lattice units")
print(f"  dx: {scaling.dx*1000:.4f} mm")
print(f"  dt: {scaling.dt:.6f} s")

# ============================================================================
# CREATE GEOMETRY
# ============================================================================

cell_cells = int(scaling.N)
nx = int(L_phys / cell_size * cell_cells)
ny = int(cell_cells * 1.5)
nz = int(cell_cells * 1.5)

print(f"\nDomain Size:")
print(f"  nx (length): {nx}")
print(f"  ny, nz: {ny} × {nz}")

geometry = KelvinCellsGeometry(
    nx=nx, ny=ny, nz=nz,
    cell_size_ratio=cell_size/(ny*scaling.dx),
    strut_thickness=0.002,
    dx=scaling.dx,
    use_smooth_boundary=True
)

print(f"\nGeometry created successfully")
print(f"  Porosity: {geometry.porosity:.4f}")
print(f"  Surface area: {geometry.surface_area:.2e} m²")

# ============================================================================
# CREATE MATERIALS
# ============================================================================

fluid = Material(
    name="Air",
    density=rho_air,
    viscosity=nu_air * rho_air,
    specific_heat=cp_air,
    thermal_conductivity=k_air
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
    n_inlet=max(5, nx // 15),
    n_outlet=max(5, nx // 15),
    boundary_method='bouzidi'
)

solver.set_inlet_velocity(scaling.u_lattice)
solver.set_inlet_temperature(T_inlet)
solver.set_outlet_temperature(T_inlet)
solver.T[geometry.solid_mask] = T_structure

solver.initialize_distributions()

print(f"\nBoundary Conditions:")
solver.print_boundary_info()

# ============================================================================
# RUN SIMULATION
# ============================================================================

num_steps = 1200
print_interval = 300

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
y_phys = np.arange(ny) * scaling.dx * 1000
z_phys = np.arange(nz) * scaling.dx * 1000

y_mid = ny // 2
z_mid = nz // 2

# ============================================================================
# VISUALIZATION
# ============================================================================

fig = plt.figure(figsize=(18, 12))

# -------------------------
# 1. Velocity Contours (xy plane at z_mid)
# -------------------------
ax1 = plt.subplot(3, 3, 1)
X, Y = np.meshgrid(x_phys, y_phys)
u_slice = u_mag_phys[:, :, z_mid].T
u_masked = np.ma.masked_where(geometry.solid_mask[:, :, z_mid].T, u_slice)
contour = ax1.contourf(X, Y, u_masked, levels=20, cmap='jet')
ax1.set_xlabel('x (mm)')
ax1.set_ylabel('y (mm)')
ax1.set_title('Velocity Magnitude (z=mid)')
plt.colorbar(contour, ax=ax1, label='Velocity (m/s)')
ax1.set_aspect('equal')

# -------------------------
# 2. Temperature Contours (xy plane at z_mid)
# -------------------------
ax2 = plt.subplot(3, 3, 2)
T_slice = T[:, :, z_mid].T
contour = ax2.contourf(X, Y, T_slice, levels=20, cmap='hot')
ax2.set_xlabel('x (mm)')
ax2.set_ylabel('y (mm)')
ax2.set_title('Temperature Distribution (z=mid)')
plt.colorbar(contour, ax=ax2, label='Temperature (K)')
ax2.set_aspect('equal')

# -------------------------
# 3. Velocity Contours (xz plane at y_mid)
# -------------------------
ax3 = plt.subplot(3, 3, 3)
X, Z = np.meshgrid(x_phys, z_phys)
u_slice_xz = u_mag_phys[:, y_mid, :].T
u_masked_xz = np.ma.masked_where(geometry.solid_mask[:, y_mid, :].T, u_slice_xz)
contour = ax3.contourf(X, Z, u_masked_xz, levels=20, cmap='jet')
ax3.set_xlabel('x (mm)')
ax3.set_ylabel('z (mm)')
ax3.set_title('Velocity Magnitude (y=mid)')
plt.colorbar(contour, ax=ax3, label='Velocity (m/s)')
ax3.set_aspect('equal')

# -------------------------
# 4. Temperature Contours (xz plane at y_mid)
# -------------------------
ax4 = plt.subplot(3, 3, 4)
T_slice_xz = T[:, y_mid, :].T
contour = ax4.contourf(X, Z, T_slice_xz, levels=20, cmap='hot')
ax4.set_xlabel('x (mm)')
ax4.set_ylabel('z (mm)')
ax4.set_title('Temperature Distribution (y=mid)')
plt.colorbar(contour, ax=ax4, label='Temperature (K)')
ax4.set_aspect('equal')

# -------------------------
# 5. Velocity Profiles at Multiple x Positions
# -------------------------
ax5 = plt.subplot(3, 3, 5)
x_positions = [nx//10, nx//4, nx//2, 3*nx//4, 9*nx//10]
colors = ['blue', 'green', 'orange', 'red', 'purple']

for i, x_pos in enumerate(x_positions):
    u_profile = u_mag_phys[x_pos, :, z_mid]
    ax5.plot(u_profile * 1000, y_phys, label=f'x={x_phys[x_pos]:.1f}mm',
             color=colors[i], linewidth=2)

ax5.set_xlabel('Velocity (mm/s)')
ax5.set_ylabel('y (mm)')
ax5.set_title('Velocity Profiles Through Structure')
ax5.legend(fontsize=8)
ax5.grid(True, alpha=0.3)

# -------------------------
# 6. Temperature Profiles at Multiple x Positions
# -------------------------
ax6 = plt.subplot(3, 3, 6)

for i, x_pos in enumerate(x_positions):
    T_profile = T[x_pos, :, z_mid]
    ax6.plot(T_profile, y_phys, label=f'x={x_phys[x_pos]:.1f}mm',
             color=colors[i], linewidth=2)

ax6.set_xlabel('Temperature (K)')
ax6.set_ylabel('y (mm)')
ax6.set_title('Temperature Profiles Through Structure')
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3)

# -------------------------
# 7. Centerline Development
# -------------------------
ax7 = plt.subplot(3, 3, 7)
u_centerline = u_mag_phys[:, y_mid, z_mid]
ax7_twin = ax7.twinx()

line1 = ax7.plot(x_phys, u_centerline * 1000, 'b-', linewidth=2, label='Velocity')
ax7.set_xlabel('x (mm)')
ax7.set_ylabel('Centerline Velocity (mm/s)', color='b')
ax7.tick_params(axis='y', labelcolor='b')

T_centerline = T[:, y_mid, z_mid]
line2 = ax7_twin.plot(x_phys, T_centerline, 'r-', linewidth=2, label='Temperature')
ax7_twin.set_ylabel('Centerline Temperature (K)', color='r')
ax7_twin.tick_params(axis='y', labelcolor='r')

lines = line1 + line2
labels = [l.get_label() for l in lines]
ax7.legend(lines, labels, loc='best')
ax7.set_title('Centerline Development')
ax7.grid(True, alpha=0.3)

# -------------------------
# 8. Average Temperature Development
# -------------------------
ax8 = plt.subplot(3, 3, 8)

T_avg_x = []
for x in range(nx):
    fluid_at_x = geometry.fluid_mask[x, :, :]
    if np.any(fluid_at_x):
        T_avg_x.append(np.mean(T[x, fluid_at_x]))
    else:
        T_avg_x.append(T_inlet)

T_avg_x = np.array(T_avg_x)
ax8.plot(x_phys, T_avg_x, 'g-', linewidth=2)
ax8.axhline(y=T_inlet, color='blue', linestyle='--', label='Inlet T')
ax8.axhline(y=T_structure, color='red', linestyle='--', label='Structure T')
ax8.set_xlabel('x (mm)')
ax8.set_ylabel('Average Temperature (K)')
ax8.set_title('Bulk Temperature Development')
ax8.legend()
ax8.grid(True, alpha=0.3)

# -------------------------
# 9. Heat Transfer Effectiveness
# -------------------------
ax9 = plt.subplot(3, 3, 9)

effectiveness = (T_avg_x - T_inlet) / (T_structure - T_inlet) * 100
ax9.plot(x_phys, effectiveness, 'purple', linewidth=2)
ax9.set_xlabel('x (mm)')
ax9.set_ylabel('Heating Effectiveness (%)')
ax9.set_title('Heat Transfer Performance')
ax9.grid(True, alpha=0.3)
ax9.set_ylim([0, 100])

plt.tight_layout()
plt.savefig('example4_kelvin_cells.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'example4_kelvin_cells.png'")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)

# Velocity statistics
u_fluid = u_mag_phys[geometry.fluid_mask]
print(f"\nVelocity (fluid only):")
print(f"  Maximum: {np.max(u_fluid)*1000:.3f} mm/s")
print(f"  Average: {np.mean(u_fluid)*1000:.3f} mm/s")
print(f"  Std deviation: {np.std(u_fluid)*1000:.3f} mm/s")

# Temperature statistics
T_fluid = T[geometry.fluid_mask]
print(f"\nTemperature (fluid only):")
print(f"  Maximum: {np.max(T_fluid):.2f} K")
print(f"  Minimum: {np.min(T_fluid):.2f} K")
print(f"  Average: {np.mean(T_fluid):.2f} K")
print(f"  Temperature rise: {np.mean(T_fluid) - T_inlet:.2f} K")

# Heat transfer performance
outlet_T = np.mean(T[-5:, geometry.fluid_mask[-5:, :, :]])
effectiveness_final = (outlet_T - T_inlet) / (T_structure - T_inlet) * 100
print(f"\nHeat Transfer Performance:")
print(f"  Outlet average temperature: {outlet_T:.2f} K")
print(f"  Heating effectiveness: {effectiveness_final:.1f}%")
print(f"  Porosity: {geometry.porosity:.3f}")

print("\n" + "=" * 70)
print("Example 4 complete!")
print("=" * 70)
