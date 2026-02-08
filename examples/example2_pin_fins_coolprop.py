"""
Example 2: Pin Fins with CoolProp Material
Demonstrates pin fins geometry with material properties from CoolProp.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import PinFinsGeometry, Visualizer
from lbm_cht.materials import CommonMaterials, CoolPropMaterial

# Check if CoolProp is available
try:
    from lbm_cht.materials.coolprop_material import COOLPROP_AVAILABLE
except ImportError:
    COOLPROP_AVAILABLE = False


def main():
    print("="*60)
    print("Example 2: Pin Fins with CoolProp Material")
    print("="*60)
    
    # Create geometry
    print("\n1. Creating pin fins geometry...")
    nx, ny, nz = 60, 40, 40
    geometry = PinFinsGeometry(
        nx=nx, ny=ny, nz=nz,
        num_pins_y=4,
        num_pins_z=4,
        pin_diameter=6,
        dx=0.001  # 1mm spacing
    )
    
    print(f"   Grid dimensions: {nx} x {ny} x {nz}")
    print(f"   Porosity: {geometry.get_porosity():.3f}")
    print(f"   Surface area: {geometry.get_surface_area():.6f} m²")
    
    # Define materials
    print("\n2. Defining materials...")
    
    if COOLPROP_AVAILABLE:
        print("   Using CoolProp for fluid properties...")
        try:
            # Use R134a refrigerant at 300K
            fluid = CoolPropMaterial('R134a', temperature=300, pressure=101325)
            print(f"   Fluid: {fluid.name}")
            print(f"     - Density: {fluid.density:.2f} kg/m³")
            print(f"     - Thermal conductivity: {fluid.thermal_conductivity:.4f} W/m·K")
            print(f"     - Viscosity: {fluid.viscosity:.6e} Pa·s")
            print(f"     - Prandtl number: {fluid.get_prandtl_number():.4f}")
        except Exception as e:
            print(f"   CoolProp error: {e}")
            print("   Falling back to Air...")
            fluid = CommonMaterials.air(temperature=300)
    else:
        print("   CoolProp not available, using Air...")
        fluid = CommonMaterials.air(temperature=300)
        print(f"   Fluid: {fluid.name}")
        print(f"     - Density: {fluid.density:.2f} kg/m³")
        print(f"     - Thermal conductivity: {fluid.thermal_conductivity:.4f} W/m·K")
    
    solid = CommonMaterials.copper()
    print(f"   Solid: {solid.name}")
    print(f"     - Density: {solid.density:.2f} kg/m³")
    print(f"     - Thermal conductivity: {solid.thermal_conductivity:.1f} W/m·K")
    
    # Create visualizer (without solver for geometry visualization)
    print("\n3. Creating visualizations...")
    visualizer = Visualizer(geometry)
    
    # Plot geometry from different angles
    fig1 = visualizer.plot_geometry_slice(axis='x', position=nx//2)
    plt.savefig('example2_geometry_x.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_geometry_x.png")
    plt.close(fig1)
    
    fig2 = visualizer.plot_geometry_slice(axis='y', position=ny//2)
    plt.savefig('example2_geometry_y.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_geometry_y.png")
    plt.close(fig2)
    
    fig3 = visualizer.plot_geometry_slice(axis='z', position=nz//2)
    plt.savefig('example2_geometry_z.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_geometry_z.png")
    plt.close(fig3)
    
    # Plot 3D view
    print("\n4. Creating 3D visualization...")
    fig4 = visualizer.plot_3d_geometry(opacity=0.2)
    plt.savefig('example2_geometry_3d.png', dpi=150, bbox_inches='tight')
    print("   Saved: example2_geometry_3d.png")
    plt.close(fig4)
    
    print("\n" + "="*60)
    print("Example 2 completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
