"""
Example: Resolution and Smooth Boundary Comparison for Pin Fins
Demonstrates the importance of resolution and smooth boundary representation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
from lbm_cht import PinFinsGeometry, Visualizer

def main():
    print("="*70)
    print("Resolution and Smooth Boundary Analysis for Pin Fins")
    print("="*70)
    
    # Test different resolutions and smoothing options
    configs = [
        {"name": "Low Res, No Smooth", "nx": 40, "ny": 30, "nz": 30, 
         "diameter": 4, "smooth": False},
        {"name": "Low Res, With Smooth", "nx": 40, "ny": 30, "nz": 30, 
         "diameter": 4, "smooth": True},
        {"name": "High Res, No Smooth", "nx": 80, "ny": 60, "nz": 60, 
         "diameter": 8, "smooth": False},
        {"name": "High Res, With Smooth", "nx": 80, "ny": 60, "nz": 60, 
         "diameter": 8, "smooth": True},
    ]
    
    geometries = []
    print("\n1. Creating geometries with different resolutions:")
    print("-" * 70)
    
    for config in configs:
        print(f"\n  {config['name']}:")
        print(f"    Grid: {config['nx']}x{config['ny']}x{config['nz']}")
        print(f"    Diameter: {config['diameter']} cells")
        print(f"    Smooth boundaries: {config['smooth']}")
        
        geom = PinFinsGeometry(
            nx=config['nx'], ny=config['ny'], nz=config['nz'],
            num_pins_y=2, num_pins_z=2,
            pin_diameter=config['diameter'],
            use_smooth_boundary=config['smooth']
        )
        
        metrics = geom.compute_geometry_quality_metrics()
        print(f"    Porosity: {metrics['porosity']:.4f}")
        print(f"    Surface area: {metrics['surface_area']:.2f}")
        print(f"    Has smooth boundary: {metrics['has_smooth_boundary']}")
        print(f"    Resolution ratio: {metrics['resolution_ratio']:.1f}")
        
        geometries.append((config['name'], geom))
    
    # Create comparison visualization
    print("\n2. Creating comparison visualization...")
    print("-" * 70)
    
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    
    for idx, (name, geom) in enumerate(geometries):
        row = idx // 2
        col = (idx % 2) * 2
        
        # Get cross-section
        x_slice = geom.nx // 2
        
        # Plot binary mask
        axes[row, col].imshow(
            geom.solid_mask[x_slice, :, :].T,
            origin='lower', cmap='gray', interpolation='nearest'
        )
        axes[row, col].set_title(f'{name}\nBinary Mask')
        axes[row, col].set_xlabel('Y')
        axes[row, col].set_ylabel('Z')
        
        # Plot solid fraction
        im = axes[row, col+1].imshow(
            geom.solid_fraction[x_slice, :, :].T,
            origin='lower', cmap='viridis', interpolation='nearest',
            vmin=0, vmax=1
        )
        axes[row, col+1].set_title(f'{name}\nSolid Fraction')
        axes[row, col+1].set_xlabel('Y')
        axes[row, col+1].set_ylabel('Z')
        plt.colorbar(im, ax=axes[row, col+1], fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    plt.savefig('example_resolution_comparison.png', dpi=150, bbox_inches='tight')
    print("  Saved: example_resolution_comparison.png")
    
    # Create zoomed detail comparison
    fig2, axes2 = plt.subplots(1, 4, figsize=(20, 5))
    
    for idx, (name, geom) in enumerate(geometries):
        x_slice = geom.nx // 2
        
        # Find pin center
        base = 2
        y_center = int(base + (geom.ny - base) / 3)
        z_center = int(geom.nz / 3)
        
        # Zoom region (adjust size based on resolution)
        zoom = max(10, geom.pin_diameter + 4)
        y_min = max(0, y_center - zoom)
        y_max = min(geom.ny, y_center + zoom)
        z_min = max(0, z_center - zoom)
        z_max = min(geom.nz, z_center + zoom)
        
        # Plot zoomed solid fraction
        im = axes2[idx].imshow(
            geom.solid_fraction[x_slice, y_min:y_max, z_min:z_max].T,
            origin='lower', cmap='viridis', interpolation='nearest',
            vmin=0, vmax=1
        )
        axes2[idx].set_title(f'{name}\n(Zoomed Detail)')
        axes2[idx].set_xlabel('Y')
        axes2[idx].set_ylabel('Z')
        plt.colorbar(im, ax=axes2[idx], fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    plt.savefig('example_boundary_detail.png', dpi=150, bbox_inches='tight')
    print("  Saved: example_boundary_detail.png")
    
    # Quantitative comparison
    print("\n3. Quantitative Boundary Smoothness Analysis:")
    print("-" * 70)
    
    for name, geom in geometries:
        # Count boundary voxels (partial solid fraction)
        boundary_voxels = np.sum(
            (geom.solid_fraction > 0) & (geom.solid_fraction < 1)
        )
        total_voxels = geom.nx * geom.ny * geom.nz
        boundary_fraction = boundary_voxels / total_voxels
        
        # Calculate smoothness metric (variance in boundary solid fractions)
        boundary_fractions = geom.solid_fraction[
            (geom.solid_fraction > 0) & (geom.solid_fraction < 1)
        ]
        
        if len(boundary_fractions) > 0:
            smoothness = 1 - np.std(boundary_fractions)
        else:
            smoothness = 0
        
        print(f"\n  {name}:")
        print(f"    Boundary voxels: {boundary_voxels} ({boundary_fraction*100:.2f}%)")
        print(f"    Smoothness metric: {smoothness:.4f}")
        if geom.has_smooth_boundary():
            print(f"    Avg boundary solid fraction: {np.mean(boundary_fractions):.3f}")
    
    print("\n" + "="*70)
    print("Example completed successfully!")
    print("\nKey Observations:")
    print("  - Smooth boundaries significantly increase boundary voxels")
    print("  - Higher resolution provides better accuracy even without smoothing")
    print("  - Smooth boundaries + high resolution = best accuracy")
    print("  - Low resolution without smoothing creates jagged stair-step patterns")
    print("="*70)


if __name__ == "__main__":
    main()
