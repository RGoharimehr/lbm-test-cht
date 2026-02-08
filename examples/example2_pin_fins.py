"""
Example 2: Pin Fins Heat Exchanger

Demonstrates:
- Pin fins array geometry for heat transfer enhancement
- Complex flow patterns around cylinders
- Enhanced heat transfer with forced convection
- Comprehensive visualization:
  * Velocity contours showing flow around pins
  * Temperature contours showing cooling effect
  * Velocity profiles before/after pins
  * Temperature profiles showing thermal development
  * Heat transfer performance metrics

This represents a practical engineering application.
"""

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import PinFinsGeometry, Material, LBMSolver
from lbm_cht.lbm.unit_converter import DimensionlessScaling

# ============================================================================
# SETUP PARAMETERS
# ============================================================================

print("=" * 70)
print("EXAMPLE 2: PIN FINS HEAT EXCHANGER")
print("=" * 70)

# Physical parameters
u_inlet_phys = 0.1       # m/s - higher velocity for forced convection
L_phys = 0.06            # m - domain length
H_phys = 0.02            # m - domain height
pin_diameter = 0.003     # m - 3mm pins
T_inlet = 300.0          # K - cool inlet air
T_pins = 350.0           # K - hot pins
Re_target = 300          # Based on pin diameter

print(f"\nPhysical Parameters:")
print(f"  Inlet velocity: {u_inlet_phys} m/s")
print(f"  Domain: {L_phys*1000}mm × {H_phys*1000}mm")
print(f"  Pin diameter: {pin_diameter*1000} mm")
print(f"  Target Reynolds: {Re_target}")
print(f"  Inlet temperature: {T_inlet} K")
print(f"  Pin temperature: {T_pins} K")

# ============================================================================
# DIMENSIONLESS SCALING
# ============================================================================

# Air properties at 300K
nu_air = 1.5e-5          # m^2/s
rho_air = 1.2            # kg/m^3
k_air = 0.026            # W/(m·K)
cp_air = 1005.0          # J/(kg·K)

scaling = DimensionlessScaling(
    Re_target=Re_target,
    L_ref=pin_diameter,     # Use pin diameter as reference
    u_ref=u_inlet_phys,
    nu_ref=nu_air,
    Ma_target=0.1,
    tau_target=0.7
)

print(f"\nLattice Parameters:")
print(f"  Pin diameter: {scaling.N} lattice units")
print(f"  dx: {scaling.dx*1000:.4f} mm")
print(f"  dt: {scaling.dt:.6f} s")

# ============================================================================
# CREATE GEOMETRY
# ============================================================================

# Calculate domain size
pin_cells = int(scaling.N)
ny = int(H_phys / pin_diameter * pin_cells)  # Height
nx = int(L_phys / pin_diameter * pin_cells)  # Length
nz = max(10, pin_cells)                      # Depth

print(f"\nDomain Size:")
print(f"  nx (length): {nx}")
print(f"  ny (height): {ny}")
print(f"  nz (depth): {nz}")

geometry = PinFinsGeometry(
    nx=nx, ny=ny, nz=nz,
    pin_diameter_ratio=pin_diameter/H_phys,
    pin_spacing_x=0.012,
    pin_spacing_y=0.01,
    dx=scaling.dx,
    use_smooth_boundary=True
)

print(f"\nGeometry created successfully")
print(f"  Porosity: {geometry.porosity:.4f}")
print(f"  Number of pins: ~{np.sum(geometry.solid_mask) / (np.pi * (pin_cells/2)**2 * nz):.0f}")

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
    name="Copper",
    density=8900.0,
    specific_heat=385.0,
    thermal_conductivity=400.0
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
    boundary_method='bouzidi'  # Better for curved pins
)

# Set boundary conditions
solver.set_inlet_velocity(scaling.u_lattice)
solver.set_inlet_temperature(T_inlet)
solver.set_outlet_temperature(T_inlet)

# Initialize hot pins
solver.T[geometry.solid_mask] = T_pins

solver.initialize_distributions()

print(f"\nBoundary Conditions:")
solver.print_boundary_info()

# ============================================================================
# RUN SIMULATION
# ============================================================================

num_steps = 1500
print_interval = 300

print(f"\nRunning simulation for {num_steps} steps...")
solver.run(num_steps=num_steps, print_interval=print_interval)
print("Simulation complete!")

# ============================================================================
# EXTRACT RESULTS
# ============================================================================

u_mag = np.sqrt(solver.u[0]**2 + solver.u[1]**2 + solver.u[2]**2)
T = solver.T

# Convert to physical units
u_mag_phys = scaling.lattice_to_physical_velocity(u_mag)
x_phys = np.arange(nx) * scaling.dx * 1000
y_phys = np.arange(ny) * scaling.dx * 1000

z_mid = nz // 2

# ============================================================================
# VISUALIZATION
# ============================================================================

fig = plt.figure(figsize=(18, 12))

# -------------------------
# 1. Velocity Contours with Pin Geometry
# -------------------------
ax1 = plt.subplot(3, 3, 1)
X, Y = np.meshgrid(x_phys, y_phys)
u_slice = u_mag_phys[:, :, z_mid].T
# Mask solid regions
u_masked = np.ma.masked_where(geometry.solid_mask[:, :, z_mid].T, u_slice)
contour = ax1.contourf(X, Y, u_masked, levels=20, cmap='jet')
ax1.contour(X, Y, geometry.solid_mask[:, :, z_mid].T, levels=[0.5], colors='black', linewidths=2)
ax1.set_xlabel('x (mm)')
ax1.set_ylabel('y (mm)')
ax1.set_title('Velocity Magnitude Around Pins')
plt.colorbar(contour, ax=ax1, label='Velocity (m/s)')
ax1.set_aspect('equal')

# -------------------------
# 2. Temperature Contours with Pin Geometry
# -------------------------
ax2 = plt.subplot(3, 3, 2)
T_slice = T[:, :, z_mid].T
contour = ax2.contourf(X, Y, T_slice, levels=20, cmap='hot')
ax2.contour(X, Y, geometry.solid_mask[:, :, z_mid].T, levels=[0.5], colors='white', linewidths=1.5)
ax2.set_xlabel('x (mm)')
ax2.set_ylabel('y (mm)')
ax2.set_title('Temperature Distribution (Pins Outlined)')
plt.colorbar(contour, ax=ax2, label='Temperature (K)')
ax2.set_aspect('equal')

# -------------------------
# 3. Velocity Vectors Around Pins
# -------------------------
ax3 = plt.subplot(3, 3, 3)
skip = max(1, nx // 30)
X_sub = X[::skip, ::skip]
Y_sub = Y[::skip, ::skip]
U_sub = solver.u[0, ::skip, ::skip, z_mid].T
V_sub = solver.u[1, ::skip, ::skip, z_mid].T
U_sub_phys = scaling.lattice_to_physical_velocity(U_sub)
V_sub_phys = scaling.lattice_to_physical_velocity(V_sub)

# Plot velocity magnitude as background
contour = ax3.contourf(X, Y, u_masked, levels=20, cmap='jet', alpha=0.5)
# Plot velocity vectors
ax3.quiver(X_sub, Y_sub, U_sub_phys, V_sub_phys, scale=3, width=0.002)
ax3.contour(X, Y, geometry.solid_mask[:, :, z_mid].T, levels=[0.5], colors='black', linewidths=2)
ax3.set_xlabel('x (mm)')
ax3.set_ylabel('y (mm)')
ax3.set_title('Velocity Vectors Around Pins')
ax3.set_aspect('equal')

# -------------------------
# 4. Velocity Profile - Before Pins
# -------------------------
ax4 = plt.subplot(3, 3, 4)
x_before = nx // 8  # Before first row of pins
u_profile_before = u_mag_phys[x_before, :, z_mid]
ax4.plot(u_profile_before * 1000, y_phys, 'b-', linewidth=2, label='Before Pins')
ax4.set_xlabel('Velocity (mm/s)')
ax4.set_ylabel('y (mm)')
ax4.set_title(f'Velocity Profile at x={x_phys[x_before]:.1f}mm')
ax4.grid(True, alpha=0.3)
ax4.legend()

# -------------------------
# 5. Velocity Profile - After Pins
# -------------------------
ax5 = plt.subplot(3, 3, 5)
x_after = 7 * nx // 8  # After last row of pins
u_profile_after = u_mag_phys[x_after, :, z_mid]
ax5.plot(u_profile_after * 1000, y_phys, 'r-', linewidth=2, label='After Pins')
ax5.set_xlabel('Velocity (mm/s)')
ax5.set_ylabel('y (mm)')
ax5.set_title(f'Velocity Profile at x={x_phys[x_after]:.1f}mm')
ax5.grid(True, alpha=0.3)
ax5.legend()

# -------------------------
# 6. Comparison of Profiles
# -------------------------
ax6 = plt.subplot(3, 3, 6)
ax6.plot(u_profile_before * 1000, y_phys, 'b-', linewidth=2, label='Before Pins')
ax6.plot(u_profile_after * 1000, y_phys, 'r-', linewidth=2, label='After Pins')
ax6.set_xlabel('Velocity (mm/s)')
ax6.set_ylabel('y (mm)')
ax6.set_title('Velocity Profile Comparison')
ax6.grid(True, alpha=0.3)
ax6.legend()

# -------------------------
# 7. Temperature Profile Evolution
# -------------------------
ax7 = plt.subplot(3, 3, 7)
x_positions = [nx//6, nx//3, nx//2, 2*nx//3, 5*nx//6]
colors = ['blue', 'green', 'orange', 'red', 'purple']

for i, x_pos in enumerate(x_positions):
    T_profile = T[x_pos, :, z_mid]
    ax7.plot(T_profile, y_phys, label=f'x={x_phys[x_pos]:.1f}mm',
             color=colors[i], linewidth=2)

ax7.set_xlabel('Temperature (K)')
ax7.set_ylabel('y (mm)')
ax7.set_title('Temperature Profiles Through Pin Array')
ax7.legend(fontsize=8)
ax7.grid(True, alpha=0.3)

# -------------------------
# 8. Centerline Temperature Development
# -------------------------
ax8 = plt.subplot(3, 3, 8)
y_center = ny // 2
T_centerline = T[:, y_center, z_mid]
ax8.plot(x_phys, T_centerline, 'r-', linewidth=2)
ax8.axhline(y=T_inlet, color='blue', linestyle='--', label='Inlet T')
ax8.axhline(y=T_pins, color='red', linestyle='--', label='Pin T')
ax8.set_xlabel('x (mm)')
ax8.set_ylabel('Temperature (K)')
ax8.set_title('Centerline Temperature Development')
ax8.grid(True, alpha=0.3)
ax8.legend()

# -------------------------
# 9. Heat Transfer Performance
# -------------------------
ax9 = plt.subplot(3, 3, 9)

# Calculate average temperature at different x positions
T_avg_x = []
for x in range(nx):
    fluid_at_x = geometry.fluid_mask[x, :, z_mid]
    if np.any(fluid_at_x):
        T_avg_x.append(np.mean(T[x, fluid_at_x, z_mid]))
    else:
        T_avg_x.append(T_inlet)

T_avg_x = np.array(T_avg_x)
heating_effectiveness = (T_avg_x - T_inlet) / (T_pins - T_inlet) * 100

ax9.plot(x_phys, heating_effectiveness, 'g-', linewidth=2)
ax9.set_xlabel('x (mm)')
ax9.set_ylabel('Heating Effectiveness (%)')
ax9.set_title('Heat Transfer Performance')
ax9.grid(True, alpha=0.3)
ax9.set_ylim([0, 100])

plt.tight_layout()
plt.savefig('example2_pin_fins.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'example2_pin_fins.png'")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)

# Velocity statistics
u_max = np.max(u_mag_phys[geometry.fluid_mask])
u_avg = np.mean(u_mag_phys[geometry.fluid_mask])
print(f"\nVelocity (fluid region only):")
print(f"  Maximum: {u_max*1000:.3f} mm/s")
print(f"  Average: {u_avg*1000:.3f} mm/s")
print(f"  Max/Avg ratio: {u_max/u_avg:.3f}")

# Temperature statistics
T_fluid = T[geometry.fluid_mask]
T_max_fluid = np.max(T_fluid)
T_min_fluid = np.min(T_fluid)
T_avg_fluid = np.mean(T_fluid)
print(f"\nTemperature (fluid region only):")
print(f"  Maximum: {T_max_fluid:.2f} K")
print(f"  Minimum: {T_min_fluid:.2f} K")
print(f"  Average: {T_avg_fluid:.2f} K")
print(f"  Temperature rise: {T_avg_fluid - T_inlet:.2f} K")

# Heat transfer effectiveness
outlet_avg_T = np.mean(T[-5:, geometry.fluid_mask[-5:, :, z_mid], z_mid])
effectiveness = (outlet_avg_T - T_inlet) / (T_pins - T_inlet) * 100
print(f"\nHeat Transfer Performance:")
print(f"  Outlet average temperature: {outlet_avg_T:.2f} K")
print(f"  Heating effectiveness: {effectiveness:.1f}%")

# Pressure drop estimate (simplified)
inlet_u_avg = np.mean(u_mag_phys[:5, geometry.fluid_mask[:5, :, z_mid], z_mid])
outlet_u_avg = np.mean(u_mag_phys[-5:, geometry.fluid_mask[-5:, :, z_mid], z_mid])
print(f"\nFlow Characteristics:")
print(f"  Inlet average velocity: {inlet_u_avg*1000:.2f} mm/s")
print(f"  Outlet average velocity: {outlet_u_avg*1000:.2f} mm/s")
print(f"  Velocity increase (due to blockage): {(outlet_u_avg/inlet_u_avg - 1)*100:.1f}%")

print("\n" + "=" * 70)
print("Example 2 complete!")
print("=" * 70)
