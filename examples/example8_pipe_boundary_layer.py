"""
Example 8: Simple Pipe Thermal Boundary Layer Demo

A simplified version demonstrating thermal boundary layer development in a pipe.
Uses a smaller grid for faster execution suitable for demonstration.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import PipeGeometry, Material, LBMSolver
from lbm_cht.materials import CommonMaterials


def main():
    print("="*70)
    print("Example 8: Pipe Thermal Boundary Layer (Simple Demo)")
    print("="*70)
    
    # ========== 1. Geometry Setup ==========
    print("\n1. Creating circular pipe geometry...")
    nx, ny, nz = 60, 20, 20  # Smaller grid for faster demo
    
    geometry = PipeGeometry(
        nx=nx, ny=ny, nz=nz,
        inner_diameter_ratio=0.7,
        wall_thickness=2,
        dx=0.001,  # 1mm spacing
        use_smooth_boundary=True
    )
    
    D = geometry.get_inner_diameter()
    L = nx * geometry.dx
    
    print(f"   Grid: {nx} × {ny} × {nz}")
    print(f"   Inner diameter: {D*1000:.2f} mm ({D/geometry.dx:.1f} cells)")
    print(f"   Pipe length: {L*1000:.1f} mm")
    print(f"   Porosity: {geometry.get_porosity():.3f}")
    
    # ========== 2. Materials ==========
    print("\n2. Defining materials...")
    fluid = CommonMaterials.water(temperature=300)
    solid = CommonMaterials.aluminum()
    
    nu = fluid.get_kinematic_viscosity()
    alpha = fluid.get_thermal_diffusivity()
    Pr = nu / alpha
    
    print(f"   Fluid: {fluid.name} (Pr={Pr:.2f})")
    print(f"   Solid: {solid.name}")
    
    # ========== 3. Flow Conditions ==========
    print("\n3. Setting flow conditions...")
    u_inlet = 0.002  # 2 mm/s - lower velocity for stability
    Re = u_inlet * D / nu
    
    print(f"   Inlet velocity: {u_inlet*1000:.1f} mm/s")
    print(f"   Reynolds number: {Re:.1f}")
    
    # ========== 4. Solver Setup ==========
    print("\n4. Creating LBM solver...")
    solver = LBMSolver(
        geometry=geometry,
        fluid_material=fluid,
        solid_material=solid,
        dx=geometry.dx,
        dt=None,  # Auto-calculate
        n_inlet=6,
        n_outlet=6,
        boundary_method='bouzidi'
    )
    
    print(f"   Time step: {solver.dt:.4e} s")
    
    # ========== 5. Boundary Conditions ==========
    print("\n5. Setting boundary conditions...")
    T_inlet = 300.0
    T_wall = 350.0
    
    solver.set_inlet_temperature(T_inlet)
    solver.set_outlet_temperature(T_inlet)
    solver.set_inlet_velocity(u_inlet)
    
    # Set wall temperature
    solver.T[geometry.solid_mask] = T_wall
    
    print(f"   Inlet: {T_inlet}K, {u_inlet*1000:.1f} mm/s")
    print(f"   Wall: {T_wall}K")
    
    solver.initialize_distributions()
    
    # ========== 6. Run Simulation ==========
    print("\n6. Running simulation...")
    num_steps = 200
    print(f"   Simulating {num_steps} steps...")
    
    solver.run(num_steps=num_steps, print_interval=100)
    print("   ✓ Complete!")
    
    # ========== 7. Analysis ==========
    print("\n7. Analyzing results...")
    
    T = solver.T
    cy, cz = ny / 2.0, nz / 2.0
    
    # Temperature profiles at different positions
    x_D_positions = [2, 10, 20, 40]
    
    # ========== 8. Visualization ==========
    print("\n8. Creating visualizations...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Plot 1: Temperature field (slice)
    ax = axes[0, 0]
    T_slice = T[:, int(cy), :]
    im = ax.imshow(T_slice.T, aspect='auto', origin='lower', cmap='hot',
                   extent=[0, L*1000, 0, nz*geometry.dx*1000])
    ax.set_xlabel('Axial Position (mm)')
    ax.set_ylabel('Radial Position (mm)')
    ax.set_title('Temperature Field (Centerline Slice)')
    plt.colorbar(im, ax=ax, label='T (K)')
    
    # Plot 2: Temperature profiles
    ax = axes[0, 1]
    colors = plt.cm.viridis(np.linspace(0, 1, len(x_D_positions)))
    
    for idx, x_D in enumerate(x_D_positions):
        i = min(int(x_D * D / geometry.dx), nx-1)
        T_profile = T[i, int(cy), :]
        r_pos = (np.arange(nz) - cz) * geometry.dx * 1000
        ax.plot(r_pos, T_profile, marker='o', markersize=4,
                label=f'x/D = {x_D}', color=colors[idx])
    
    ax.set_xlabel('Radial Position (mm)')
    ax.set_ylabel('Temperature (K)')
    ax.set_title('Radial Temperature Profiles')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Centerline temperature
    ax = axes[0, 2]
    T_centerline = T[:, int(cy), int(cz)]
    x_pos = np.arange(nx) * geometry.dx * 1000
    ax.plot(x_pos, T_centerline, 'b-', linewidth=2)
    ax.set_xlabel('Axial Position (mm)')
    ax.set_ylabel('Centerline Temperature (K)')
    ax.set_title('Centerline Temperature Development')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=T_inlet, color='cyan', linestyle='--', label='Inlet T')
    ax.axhline(y=T_wall, color='red', linestyle='--', label='Wall T')
    ax.legend()
    
    # Plot 4: Cross-section at mid-length
    ax = axes[1, 0]
    i_mid = nx // 2
    T_cross = T[i_mid, :, :]
    im = ax.imshow(T_cross, cmap='hot', origin='lower',
                   extent=[0, nz*geometry.dx*1000, 0, ny*geometry.dx*1000])
    ax.set_xlabel('Z (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_title(f'Cross-Section at x={i_mid*geometry.dx*1000:.1f}mm')
    ax.set_aspect('equal')
    plt.colorbar(im, ax=ax, label='T (K)')
    
    # Plot 5: Temperature contours
    ax = axes[1, 1]
    levels = np.linspace(T.min(), T.max(), 12)
    contour = ax.contourf(T_cross, levels=levels, cmap='hot',
                          extent=[0, nz*geometry.dx*1000, 0, ny*geometry.dx*1000])
    ax.contour(T_cross, levels=levels, colors='black', linewidths=0.5, alpha=0.3,
               extent=[0, nz*geometry.dx*1000, 0, ny*geometry.dx*1000])
    ax.set_xlabel('Z (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_title('Temperature Contours')
    ax.set_aspect('equal')
    plt.colorbar(contour, ax=ax, label='T (K)')
    
    # Plot 6: Thermal boundary layer growth
    ax = axes[1, 2]
    
    # Estimate BL thickness
    T_threshold = T_inlet + 0.95 * (T_wall - T_inlet)
    bl_thickness = []
    x_bl_pos = []
    
    for i in range(solver.n_inlet, nx - solver.n_outlet, 3):
        T_radial = T[i, int(cy), int(cz):]
        above = T_radial > T_threshold
        if np.any(above):
            bl_idx = np.where(above)[0][0]
            bl_thickness.append(bl_idx * geometry.dx * 1000)
            x_bl_pos.append(i * geometry.dx * 1000)
    
    if bl_thickness:
        ax.plot(x_bl_pos, bl_thickness, 'ro-', linewidth=2, markersize=6)
        ax.axhline(y=D*1000/2, color='blue', linestyle='--',
                   label=f'Pipe radius ({D*1000/2:.2f}mm)')
        ax.set_xlabel('Axial Position (mm)')
        ax.set_ylabel('Thermal BL Thickness (mm)')
        ax.set_title('Thermal Boundary Layer Growth')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    plt.tight_layout()
    plt.savefig('example8_pipe_boundary_layer.png', dpi=150, bbox_inches='tight')
    print("   ✓ Saved: example8_pipe_boundary_layer.png")
    
    # ========== 9. Summary ==========
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Geometry: D={D*1000:.2f}mm, L={L*1000:.1f}mm")
    print(f"Flow: Re={Re:.1f}, Pr={Pr:.2f}, u={u_inlet*1000:.1f}mm/s")
    print(f"Temperature: Inlet={T_inlet}K, Wall={T_wall}K")
    print(f"Range: {T.min():.2f}K - {T.max():.2f}K")
    print(f"Centerline (exit): {T[-solver.n_outlet-1, int(cy), int(cz)]:.2f}K")
    
    # Calculate thermal entry length
    L_t = 0.05 * Re * Pr * D
    print(f"\nTheoretical thermal entry length: {L_t*1000:.1f}mm ({L_t/D:.1f}D)")
    if L > L_t:
        print("✓ Flow approaches fully developed")
    else:
        print("⚠ Flow is still developing")
    
    print("\n" + "="*70)
    print("Example 8 completed!")
    print("="*70)


if __name__ == "__main__":
    main()
