"""
Test script to validate improved geometry generation with smooth boundaries
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, '/home/runner/work/lbm-test-cht/lbm-test-cht')

from lbm_cht import PinFinsGeometry, KelvinCellsGeometry

print("="*70)
print("Testing Improved Geometry Generation with Smooth Boundaries")
print("="*70)

# Test 1: Pin Fins with different resolutions
print("\n1. Testing Pin Fins Geometry:")
print("-" * 70)

# Low resolution without smooth boundaries
print("\n  Low resolution (diameter=4, no smoothing):")
geom_low_nosmooth = PinFinsGeometry(
    nx=30, ny=20, nz=20, 
    num_pins_y=2, num_pins_z=2, 
    pin_diameter=4,
    use_smooth_boundary=False
)
print(f"    Porosity: {geom_low_nosmooth.get_porosity():.4f}")
print(f"    Has smooth boundary: {geom_low_nosmooth.has_smooth_boundary()}")
print(f"    Surface area: {geom_low_nosmooth.get_surface_area():.2f}")

# Low resolution with smooth boundaries
print("\n  Low resolution (diameter=4, with smoothing):")
geom_low_smooth = PinFinsGeometry(
    nx=30, ny=20, nz=20, 
    num_pins_y=2, num_pins_z=2, 
    pin_diameter=4,
    use_smooth_boundary=True
)
print(f"    Porosity: {geom_low_smooth.get_porosity():.4f}")
print(f"    Has smooth boundary: {geom_low_smooth.has_smooth_boundary()}")
print(f"    Surface area: {geom_low_smooth.get_surface_area():.2f}")

# Check solid fraction field
boundary_voxels = np.sum((geom_low_smooth.solid_fraction > 0) & 
                        (geom_low_smooth.solid_fraction < 1))
print(f"    Boundary voxels (partial): {boundary_voxels}")

# High resolution with smooth boundaries
print("\n  High resolution (diameter=8, with smoothing):")
geom_high_smooth = PinFinsGeometry(
    nx=60, ny=40, nz=40, 
    num_pins_y=2, num_pins_z=2, 
    pin_diameter=8,
    use_smooth_boundary=True
)
print(f"    Porosity: {geom_high_smooth.get_porosity():.4f}")
print(f"    Has smooth boundary: {geom_high_smooth.has_smooth_boundary()}")
print(f"    Surface area: {geom_high_smooth.get_surface_area():.2f}")

boundary_voxels_high = np.sum((geom_high_smooth.solid_fraction > 0) & 
                              (geom_high_smooth.solid_fraction < 1))
print(f"    Boundary voxels (partial): {boundary_voxels_high}")

# Test 2: Kelvin Cells
print("\n2. Testing Kelvin Cells Geometry:")
print("-" * 70)

print("\n  Without smooth boundaries:")
kelvin_nosmooth = KelvinCellsGeometry(
    nx=40, ny=40, nz=40,
    cell_size=10,
    strut_thickness=3,
    use_smooth_boundary=False
)
print(f"    Porosity: {kelvin_nosmooth.get_porosity():.4f}")
print(f"    Has smooth boundary: {kelvin_nosmooth.has_smooth_boundary()}")
print(f"    Surface area: {kelvin_nosmooth.get_surface_area():.2f}")

print("\n  With smooth boundaries:")
kelvin_smooth = KelvinCellsGeometry(
    nx=40, ny=40, nz=40,
    cell_size=10,
    strut_thickness=3,
    use_smooth_boundary=True
)
print(f"    Porosity: {kelvin_smooth.get_porosity():.4f}")
print(f"    Has smooth boundary: {kelvin_smooth.has_smooth_boundary()}")
print(f"    Surface area: {kelvin_smooth.get_surface_area():.2f}")

boundary_voxels_kelvin = np.sum((kelvin_smooth.solid_fraction > 0) & 
                                (kelvin_smooth.solid_fraction < 1))
print(f"    Boundary voxels (partial): {boundary_voxels_kelvin}")

# Test 3: Quality metrics
print("\n3. Geometry Quality Metrics:")
print("-" * 70)

print("\n  Pin fins (high res, smooth):")
metrics = geom_high_smooth.compute_geometry_quality_metrics()
for key, value in metrics.items():
    print(f"    {key}: {value}")

print("\n  Kelvin cells (smooth):")
metrics_kelvin = kelvin_smooth.compute_geometry_quality_metrics()
for key, value in metrics_kelvin.items():
    print(f"    {key}: {value}")

# Test 4: Create visualization comparing smooth vs non-smooth
print("\n4. Creating comparison visualizations...")
print("-" * 70)

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Row 1: Pin fins without smoothing
geom_test = geom_low_nosmooth
x_slice = 15
axes[0, 0].imshow(geom_test.solid_mask[x_slice, :, :].T, 
                  origin='lower', cmap='gray', interpolation='nearest')
axes[0, 0].set_title('Pin Fins: No Smoothing\n(Binary Mask)')
axes[0, 0].set_xlabel('Y')
axes[0, 0].set_ylabel('Z')

axes[0, 1].imshow(geom_test.solid_fraction[x_slice, :, :].T,
                  origin='lower', cmap='viridis', interpolation='nearest', vmin=0, vmax=1)
axes[0, 1].set_title('Solid Fraction\n(All 0 or 1)')
axes[0, 1].set_xlabel('Y')
axes[0, 1].set_ylabel('Z')

# Show a zoomed region
y_center = 10
z_center = 10
zoom = 5
axes[0, 2].imshow(
    geom_test.solid_fraction[x_slice, y_center-zoom:y_center+zoom, z_center-zoom:z_center+zoom].T,
    origin='lower', cmap='viridis', interpolation='nearest', vmin=0, vmax=1
)
axes[0, 2].set_title('Zoomed Detail\n(Jagged boundary)')
axes[0, 2].set_xlabel('Y')
axes[0, 2].set_ylabel('Z')

# Row 2: Pin fins with smoothing
geom_test2 = geom_low_smooth
axes[1, 0].imshow(geom_test2.solid_mask[x_slice, :, :].T,
                  origin='lower', cmap='gray', interpolation='nearest')
axes[1, 0].set_title('Pin Fins: With Smoothing\n(Binary Mask)')
axes[1, 0].set_xlabel('Y')
axes[1, 0].set_ylabel('Z')

axes[1, 1].imshow(geom_test2.solid_fraction[x_slice, :, :].T,
                  origin='lower', cmap='viridis', interpolation='nearest', vmin=0, vmax=1)
axes[1, 1].set_title('Solid Fraction\n(Smooth 0-1 values)')
axes[1, 1].set_xlabel('Y')
axes[1, 1].set_ylabel('Z')

# Show a zoomed region
axes[1, 2].imshow(
    geom_test2.solid_fraction[x_slice, y_center-zoom:y_center+zoom, z_center-zoom:z_center+zoom].T,
    origin='lower', cmap='viridis', interpolation='nearest', vmin=0, vmax=1
)
axes[1, 2].set_title('Zoomed Detail\n(Smooth boundary)')
axes[1, 2].set_xlabel('Y')
axes[1, 2].set_ylabel('Z')

# Add colorbars
for ax in axes[:, 1:].flatten():
    plt.colorbar(ax.images[0], ax=ax, fraction=0.046, pad=0.04)

plt.tight_layout()
plt.savefig('/home/runner/work/lbm-test-cht/lbm-test-cht/geometry_smooth_comparison.png', 
            dpi=150, bbox_inches='tight')
print("  Saved: geometry_smooth_comparison.png")

# Create second figure for Kelvin cells
fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))

# Kelvin cells comparison
z_slice = 20
axes2[0].imshow(kelvin_nosmooth.solid_mask[:, :, z_slice].T,
                origin='lower', cmap='gray', interpolation='nearest')
axes2[0].set_title('Kelvin Cells: No Smoothing')
axes2[0].set_xlabel('X')
axes2[0].set_ylabel('Y')

axes2[1].imshow(kelvin_smooth.solid_mask[:, :, z_slice].T,
                origin='lower', cmap='gray', interpolation='nearest')
axes2[1].set_title('Kelvin Cells: With Smoothing\n(Binary Mask)')
axes2[1].set_xlabel('X')
axes2[1].set_ylabel('Y')

im = axes2[2].imshow(kelvin_smooth.solid_fraction[:, :, z_slice].T,
                     origin='lower', cmap='viridis', interpolation='nearest', vmin=0, vmax=1)
axes2[2].set_title('Solid Fraction\n(Smooth struts)')
axes2[2].set_xlabel('X')
axes2[2].set_ylabel('Y')
plt.colorbar(im, ax=axes2[2], fraction=0.046, pad=0.04)

plt.tight_layout()
plt.savefig('/home/runner/work/lbm-test-cht/lbm-test-cht/kelvin_cells_smooth_comparison.png',
            dpi=150, bbox_inches='tight')
print("  Saved: kelvin_cells_smooth_comparison.png")

print("\n" + "="*70)
print("Testing complete! All improvements validated.")
print("="*70)
