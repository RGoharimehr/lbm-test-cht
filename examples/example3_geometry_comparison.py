"""
Example 3: Comparison of All Geometries
Demonstrates all available geometries side by side.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import (
    ChannelGeometry, DuctGeometry, SkivedFinsGeometry,
    KelvinCellsGeometry, PinFinsGeometry, Visualizer
)


def main():
    print("="*60)
    print("Example 3: Comparison of All Geometries")
    print("="*60)
    
    # Common dimensions
    nx, ny, nz = 50, 30, 30
    
    # Create all geometries
    print("\n1. Creating geometries...")
    
    geometries = {
        'Channel': ChannelGeometry(nx, ny, nz, channel_height_ratio=0.6, channel_width_ratio=0.6),
        'Duct': DuctGeometry(nx, ny, nz, wall_thickness=2),
        'Skived Fins': SkivedFinsGeometry(nx, ny, nz, num_fins=8, fin_thickness=2),
        'Kelvin Cells': KelvinCellsGeometry(nx, ny, nz, cell_size=8, strut_thickness=2),
        'Pin Fins': PinFinsGeometry(nx, ny, nz, num_pins_y=5, num_pins_z=5, pin_diameter=4),
    }
    
    # Print properties
    print("\n2. Geometry Properties:")
    print(f"   {'Geometry':<15} {'Porosity':<12} {'Surface Area (m²)':<20}")
    print("   " + "-"*47)
    for name, geom in geometries.items():
        porosity = geom.get_porosity()
        surface_area = geom.get_surface_area()
        print(f"   {name:<15} {porosity:<12.3f} {surface_area:<20.6f}")
    
    # Create comparison visualization
    print("\n3. Creating comparison visualization...")
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, (name, geom) in enumerate(geometries.items()):
        visualizer = Visualizer(geom)
        ax = axes[idx]
        
        # Get slice data
        solid_mask = geom.get_solid_mask()
        slice_data = solid_mask[:, :, nz//2]
        
        # Plot
        im = ax.imshow(slice_data.T, origin='lower', cmap='gray', 
                      interpolation='nearest')
        ax.set_title(f'{name}\nPorosity: {geom.get_porosity():.3f}')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
    
    # Hide the extra subplot
    axes[-1].axis('off')
    
    plt.tight_layout()
    plt.savefig('example3_geometry_comparison.png', dpi=150, bbox_inches='tight')
    print("   Saved: example3_geometry_comparison.png")
    plt.close(fig)
    
    # Create individual detailed views
    print("\n4. Creating individual geometry views...")
    for name, geom in geometries.items():
        visualizer = Visualizer(geom)
        
        # Create multi-view figure
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        # X slice
        solid_mask = geom.get_solid_mask()
        axes[0].imshow(solid_mask[nx//2, :, :].T, origin='lower', cmap='gray')
        axes[0].set_title(f'{name} - X slice')
        axes[0].set_xlabel('Y')
        axes[0].set_ylabel('Z')
        
        # Y slice
        axes[1].imshow(solid_mask[:, ny//2, :].T, origin='lower', cmap='gray')
        axes[1].set_title(f'{name} - Y slice')
        axes[1].set_xlabel('X')
        axes[1].set_ylabel('Z')
        
        # Z slice
        axes[2].imshow(solid_mask[:, :, nz//2].T, origin='lower', cmap='gray')
        axes[2].set_title(f'{name} - Z slice')
        axes[2].set_xlabel('X')
        axes[2].set_ylabel('Y')
        
        plt.tight_layout()
        filename = f'example3_{name.lower().replace(" ", "_")}_views.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"   Saved: {filename}")
        plt.close(fig)
    
    print("\n" + "="*60)
    print("Example 3 completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
