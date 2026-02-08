"""
Example 7: Thermal Entry Length in Circular Pipe

Demonstrates thermal boundary layer development in a circular pipe.
Shows how the temperature profile evolves from uniform at inlet to 
fully developed flow downstream. This is a classic problem in heat transfer.

Key concepts:
- Thermal entry length
- Developing vs fully developed flow
- Temperature profiles at different axial positions
- Nusselt number variation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import PipeGeometry, Material, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials


def calculate_thermal_entry_length(Re, Pr, D):
    """
    Calculate theoretical thermal entry length.
    
    For laminar flow: L_t ≈ 0.05 * Re * Pr * D
    
    Args:
        Re: Reynolds number
        Pr: Prandtl number
        D: Pipe diameter
    
    Returns:
        Thermal entry length
    """
    return 0.05 * Re * Pr * D


def calculate_reynolds_number(u, D, nu):
    """Calculate Reynolds number."""
    return u * D / nu


def calculate_prandtl_number(nu, alpha):
    """Calculate Prandtl number."""
    return nu / alpha


def extract_radial_profile(T, i, cy, cz):
    """
    Extract radial temperature profile at axial position i.
    
    Args:
        T: Temperature field
        i: Axial index
        cy, cz: Center coordinates
    
    Returns:
        r: Radial positions
        T_r: Temperatures at those positions
    """
    ny, nz = T.shape[1], T.shape[2]
    
    # Extract along horizontal line through center
    T_line = T[i, int(cy), :]
    z_positions = np.arange(nz) - cz
    
    return z_positions, T_line


def main():
    print("="*70)
    print("Example 7: Thermal Entry Length in Circular Pipe")
    print("="*70)
    print("\nThis example demonstrates thermal boundary layer development")
    print("in a circular pipe with heated walls.")
    print()
    
    # ========== 1. Geometry Setup ==========
    print("1. Creating circular pipe geometry...")
    nx, ny, nz = 100, 30, 30  # Long pipe for entry length study
    
    geometry = PipeGeometry(
        nx=nx, ny=ny, nz=nz,
        inner_diameter_ratio=0.7,  # 70% of cross-section
        wall_thickness=3,
        dx=0.0005,  # 0.5mm spacing for fine resolution
        use_smooth_boundary=True  # Smooth circular boundary
    )
    
    D = geometry.get_inner_diameter()
    A = geometry.get_cross_sectional_area()
    L = nx * geometry.dx
    
    print(f"   Grid: {nx} × {ny} × {nz}")
    print(f"   Inner diameter: {D*1000:.2f} mm ({D/geometry.dx:.1f} cells)")
    print(f"   Pipe length: {L*1000:.1f} mm")
    print(f"   Wall thickness: {geometry.get_wall_thickness_physical()*1000:.2f} mm")
    print(f"   Cross-sectional area: {A*1e6:.3f} mm²")
    print(f"   Porosity: {geometry.get_porosity():.3f}")
    
    # ========== 2. Materials ==========
    print("\n2. Defining materials...")
    # Use water for moderate Prandtl number
    T_ref = 300.0  # K
    fluid = CommonMaterials.water(temperature=T_ref)
    solid = CommonMaterials.aluminum()  # Pipe wall
    
    nu = fluid.get_kinematic_viscosity()
    alpha = fluid.get_thermal_diffusivity()
    Pr = calculate_prandtl_number(nu, alpha)
    
    print(f"   Fluid: {fluid.name}")
    print(f"     - Kinematic viscosity: {nu:.3e} m²/s")
    print(f"     - Thermal diffusivity: {alpha:.3e} m²/s")
    print(f"     - Prandtl number: {Pr:.2f}")
    print(f"   Solid: {solid.name}")
    
    # ========== 3. Flow Conditions ==========
    print("\n3. Setting flow conditions...")
    u_inlet = 0.005  # 5 mm/s - low velocity for laminar flow
    Re = calculate_reynolds_number(u_inlet, D, nu)
    
    # Calculate theoretical entry length
    L_t_theory = calculate_thermal_entry_length(Re, Pr, D)
    L_t_D = L_t_theory / D  # In terms of diameters
    
    print(f"   Inlet velocity: {u_inlet*1000:.1f} mm/s")
    print(f"   Reynolds number: {Re:.1f}")
    print(f"   Theoretical thermal entry length: {L_t_theory*1000:.2f} mm ({L_t_D:.1f} D)")
    
    if L_t_theory > L * 0.9:
        print(f"   ⚠ Warning: Pipe may be too short for full development")
        print(f"     (L_t = {L_t_theory*1000:.1f}mm, L = {L*1000:.1f}mm)")
    
    # ========== 4. Solver Setup ==========
    print("\n4. Creating LBM solver...")
    solver = LBMSolver(
        geometry=geometry,
        fluid_material=fluid,
        solid_material=solid,
        dx=geometry.dx,
        dt=None,  # Auto-calculate for stability
        n_inlet=8,
        n_outlet=8,
        boundary_method='bouzidi'  # Use interpolated BC for smooth pipe
    )
    
    print(f"   Time step: {solver.dt:.4e} s")
    print(f"   Relaxation parameters: τ_f={solver.tau_f:.3f}, τ_g={solver.tau_g_fluid:.3f}")
    
    # ========== 5. Boundary Conditions ==========
    print("\n5. Setting boundary conditions...")
    T_inlet = 300.0  # Cold inlet
    T_wall = 350.0   # Hot wall
    
    solver.set_inlet_temperature(T_inlet)
    solver.set_outlet_temperature(T_inlet)  # Zero gradient at outlet
    solver.set_inlet_velocity(u_inlet)
    
    # Set wall temperature (initialize solid regions as hot)
    solver.T[geometry.solid_mask] = T_wall
    
    print(f"   Inlet: {T_inlet}K, {u_inlet*1000:.1f} mm/s")
    print(f"   Wall: {T_wall}K (constant)")
    print(f"   Outlet: Zero gradient")
    
    solver.print_boundary_info()
    
    # Reinitialize distributions
    solver.initialize_distributions()
    
    # ========== 6. Run Simulation ==========
    print("\n6. Running simulation...")
    num_steps = 1000
    print_interval = 200
    
    print(f"   Simulating {num_steps} time steps...")
    solver.run(num_steps=num_steps, print_interval=print_interval)
    
    print("   ✓ Simulation complete!")
    
    # ========== 7. Analysis ==========
    print("\n7. Analyzing thermal boundary layer development...")
    
    # Extract temperature field
    T = solver.T
    cy, cz = ny / 2.0, nz / 2.0
    
    # Positions to analyze (in terms of x/D)
    x_over_D_positions = [0, 5, 10, 20, 40, 60]
    axial_positions = []
    
    for x_D in x_over_D_positions:
        x_physical = x_D * D
        i = int(x_physical / geometry.dx)
        if i < nx:
            axial_positions.append((x_D, i))
    
    print(f"   Analyzing temperature profiles at {len(axial_positions)} positions")
    
    # ========== 8. Visualization ==========
    print("\n8. Creating visualizations...")
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Subplot 1: Temperature field (centerline slice)
    ax1 = plt.subplot(3, 2, 1)
    T_slice = T[:, int(cy), :]
    im1 = ax1.imshow(T_slice.T, aspect='auto', origin='lower', cmap='hot')
    ax1.set_xlabel('Axial Position (x)')
    ax1.set_ylabel('Radial Position (z)')
    ax1.set_title('Temperature Field (y-centerline slice)')
    plt.colorbar(im1, ax=ax1, label='Temperature (K)')
    
    # Add entry length marker
    if L_t_theory < L:
        i_entry = int(L_t_theory / geometry.dx)
        ax1.axvline(x=i_entry, color='cyan', linestyle='--', linewidth=2, 
                    label=f'Theoretical L_t ({L_t_D:.1f}D)')
        ax1.legend()
    
    # Subplot 2: Temperature profiles at different positions
    ax2 = plt.subplot(3, 2, 2)
    colors = plt.cm.viridis(np.linspace(0, 1, len(axial_positions)))
    
    for idx, (x_D, i) in enumerate(axial_positions):
        r_pos, T_profile = extract_radial_profile(T, i, cy, cz)
        # Normalize radial position by inner radius
        r_norm = r_pos / (D / (2 * geometry.dx))
        ax2.plot(r_norm, T_profile, marker='o', markersize=4, 
                label=f'x/D = {x_D}', color=colors[idx])
    
    ax2.set_xlabel('Normalized Radial Position (r/R)')
    ax2.set_ylabel('Temperature (K)')
    ax2.set_title('Radial Temperature Profiles')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: Centerline temperature vs axial position
    ax3 = plt.subplot(3, 2, 3)
    T_centerline = T[:, int(cy), int(cz)]
    x_positions = np.arange(nx) * geometry.dx * 1000  # mm
    ax3.plot(x_positions, T_centerline, 'b-', linewidth=2)
    ax3.set_xlabel('Axial Position (mm)')
    ax3.set_ylabel('Centerline Temperature (K)')
    ax3.set_title('Temperature Development Along Pipe Centerline')
    ax3.grid(True, alpha=0.3)
    
    if L_t_theory < L:
        ax3.axvline(x=L_t_theory*1000, color='red', linestyle='--', 
                    label=f'Theoretical L_t = {L_t_theory*1000:.1f}mm')
        ax3.legend()
    
    # Subplot 4: 3D temperature visualization at mid-length
    ax4 = plt.subplot(3, 2, 4, projection='3d')
    i_mid = nx // 2
    Y, Z = np.meshgrid(np.arange(ny), np.arange(nz), indexing='ij')
    T_cross = T[i_mid, :, :]
    surf = ax4.plot_surface(Y, Z, T_cross, cmap='hot', alpha=0.9)
    ax4.set_xlabel('Y')
    ax4.set_ylabel('Z')
    ax4.set_zlabel('Temperature (K)')
    ax4.set_title(f'Cross-Section at x = {i_mid*geometry.dx*1000:.1f}mm')
    
    # Subplot 5: Temperature contours (cross-section)
    ax5 = plt.subplot(3, 2, 5)
    T_cross = T[i_mid, :, :]
    levels = np.linspace(T.min(), T.max(), 15)
    contour = ax5.contourf(T_cross, levels=levels, cmap='hot')
    ax5.contour(T_cross, levels=levels, colors='black', linewidths=0.5, alpha=0.3)
    plt.colorbar(contour, ax=ax5, label='Temperature (K)')
    ax5.set_xlabel('Y Direction')
    ax5.set_ylabel('Z Direction')
    ax5.set_title(f'Temperature Contours at x = {i_mid*geometry.dx*1000:.1f}mm')
    ax5.set_aspect('equal')
    
    # Subplot 6: Thermal boundary layer thickness vs position
    ax6 = plt.subplot(3, 2, 6)
    
    # Estimate thermal BL thickness (distance where T reaches 99% of T_wall)
    T_threshold = T_inlet + 0.99 * (T_wall - T_inlet)
    bl_thickness = []
    x_bl_positions = []
    
    for i in range(solver.n_inlet, nx - solver.n_outlet, 5):
        # Extract temperature along radius from center
        T_radial = T[i, int(cy), int(cz):]
        r_positions = np.arange(len(T_radial))
        
        # Find where temperature exceeds threshold
        above_threshold = T_radial > T_threshold
        if np.any(above_threshold):
            bl_idx = np.where(above_threshold)[0][0]
            bl_thickness.append(bl_idx * geometry.dx * 1000)  # mm
            x_bl_positions.append(i * geometry.dx * 1000)  # mm
    
    if bl_thickness:
        ax6.plot(x_bl_positions, bl_thickness, 'ro-', linewidth=2, markersize=6)
        ax6.set_xlabel('Axial Position (mm)')
        ax6.set_ylabel('Thermal BL Thickness (mm)')
        ax6.set_title('Thermal Boundary Layer Growth')
        ax6.grid(True, alpha=0.3)
        
        # Add horizontal line for pipe radius
        ax6.axhline(y=D*1000/2, color='blue', linestyle='--', 
                    label=f'Pipe radius = {D*1000/2:.2f}mm')
        ax6.legend()
    
    plt.tight_layout()
    plt.savefig('example7_pipe_thermal_entry.png', dpi=150, bbox_inches='tight')
    print("   ✓ Saved: example7_pipe_thermal_entry.png")
    
    # ========== 9. Summary ==========
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Geometry:")
    print(f"  Pipe diameter: {D*1000:.2f} mm")
    print(f"  Pipe length: {L*1000:.1f} mm")
    print(f"\nFlow Conditions:")
    print(f"  Reynolds number: {Re:.1f}")
    print(f"  Prandtl number: {Pr:.2f}")
    print(f"  Inlet velocity: {u_inlet*1000:.1f} mm/s")
    print(f"\nThermal Entry Length:")
    print(f"  Theoretical: {L_t_theory*1000:.2f} mm ({L_t_D:.1f} D)")
    print(f"  Available length: {L*1000:.1f} mm ({L/D:.1f} D)")
    
    if L > L_t_theory:
        print(f"  ✓ Sufficient length for full thermal development")
    else:
        print(f"  ⚠ Flow may not be fully developed")
    
    print(f"\nTemperature Range:")
    print(f"  Inlet: {T_inlet:.1f} K")
    print(f"  Wall: {T_wall:.1f} K")
    print(f"  Min: {T.min():.2f} K")
    print(f"  Max: {T.max():.2f} K")
    print(f"  Centerline (inlet): {T[solver.n_inlet, int(cy), int(cz)]:.2f} K")
    print(f"  Centerline (outlet): {T[-solver.n_outlet-1, int(cy), int(cz)]:.2f} K")
    
    print("\n" + "="*70)
    print("Example 7 completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
