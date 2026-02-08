# Resolution and Smooth Boundary Guidelines

## Overview

This document provides guidelines for choosing appropriate grid resolution and using smooth boundaries in LBM CHT simulations. Proper resolution and boundary representation are critical for accurate results.

## Why Resolution Matters

### 1. Accuracy
- Low resolution creates jagged, stair-step boundaries
- Features smaller than ~4-6 grid cells cannot be accurately represented
- Curved surfaces need adequate resolution to avoid faceting

### 2. LBM Stability
- LBM requires smooth velocity and temperature gradients
- Jagged boundaries create artificial flow disturbances
- Smooth boundaries reduce numerical artifacts

### 3. Physical Fidelity
- Real-world geometries have smooth surfaces
- Surface roughness from low resolution is unphysical
- Heat transfer and pressure drop depend on surface smoothness

## Smooth Boundary Technology

### What is Smooth Boundary Representation?

Instead of binary solid/fluid masks, smooth boundaries use a **solid fraction field** (0-1) that represents the fraction of each voxel occupied by solid material.

**Traditional (Binary):**
```
Voxel state: [0, 0, 0, 1, 1, 1, 1, ...]
            (fluid)  (solid)
```

**Smooth Boundary:**
```
Solid fraction: [0.0, 0.2, 0.7, 0.95, 1.0, 1.0, ...]
                (mostly fluid → mixed → mostly solid)
```

### How It Works

For curved surfaces (cylinders, spheres):
1. Sample multiple points within each voxel (5×5×5 grid = 125 samples)
2. Calculate distance from each sample point to the surface
3. Determine what fraction of sample points are inside the solid
4. Store this fraction (0.0 to 1.0) for each voxel

### Benefits

✅ **Smoother boundaries** - Eliminates stair-step artifacts
✅ **Better accuracy** - Sub-voxel surface representation
✅ **Improved convergence** - Reduces numerical noise
✅ **More accurate surface area** - Uses fractional boundary areas
✅ **Better flow physics** - Smoother velocity gradients near walls

## Resolution Guidelines by Geometry Type

### Pin Fins

**Minimum Requirements:**
- **Pin diameter:** ≥ 6 lattice cells
- **Pin spacing:** ≥ 4 lattice cells
- **Base plate thickness:** ≥ 2 lattice cells

**Recommended:**
- **Pin diameter:** 8-12 lattice cells for smooth cylinders
- **Pin spacing:** ≥ 6 lattice cells to resolve inter-pin flow
- **Overall grid:** ≥ 40×30×30 for simple configurations

**Example:**
```python
# Insufficient resolution (warning issued)
geom_bad = PinFinsGeometry(nx=30, ny=20, nz=20, pin_diameter=3)
# Warning: Pin diameter (3 cells) may have insufficient resolution

# Good resolution
geom_good = PinFinsGeometry(nx=60, ny=40, nz=40, pin_diameter=8)
```

**Resolution Impact:**

| Diameter (cells) | Quality | Description |
|-----------------|---------|-------------|
| 2-3 | Poor | Barely recognizable as circle |
| 4-5 | Fair | Octagonal appearance |
| 6-7 | Good | Smooth with minor faceting |
| 8-12 | Excellent | Very smooth circular |
| 13+ | Overkill | Diminishing returns |

### Kelvin Cells

**Minimum Requirements:**
- **Strut thickness:** ≥ 4 lattice cells
- **Cell size:** ≥ 10 lattice cells
- **Overall grid:** ≥ 40×40×40

**Recommended:**
- **Strut thickness:** 4-6 lattice cells
- **Cell size:** 12-20 lattice cells
- **Overall grid:** 60×60×60 or larger

**Example:**
```python
# Minimum acceptable
geom_min = KelvinCellsGeometry(nx=40, ny=40, nz=40, 
                               cell_size=10, strut_thickness=4)

# Recommended
geom_good = KelvinCellsGeometry(nx=60, ny=60, nz=60,
                               cell_size=15, strut_thickness=5,
                               use_smooth_boundary=True)
```

### Channels and Ducts

**Minimum Requirements:**
- **Channel height:** ≥ 10 lattice cells
- **Channel width:** ≥ 10 lattice cells
- **Wall thickness:** ≥ 2 lattice cells

**Recommended:**
- **Channel height:** 20-40 lattice cells
- **Channel width:** 20-40 lattice cells
- **Smooth boundaries:** Not necessary (already rectangular)

### Skived Fins

**Minimum Requirements:**
- **Fin thickness:** ≥ 2 lattice cells
- **Fin spacing:** ≥ 4 lattice cells
- **Fin height:** ≥ 10 lattice cells

**Recommended:**
- **Fin thickness:** 2-4 lattice cells (thin is realistic)
- **Fin spacing:** 6-10 lattice cells
- **Smooth boundaries:** Not necessary (already planar)

## How to Use Smooth Boundaries

### Enabling Smooth Boundaries

```python
from lbm_cht import PinFinsGeometry

# Enable smooth boundaries (default for pin fins)
geom_smooth = PinFinsGeometry(
    nx=60, ny=40, nz=40,
    num_pins_y=4, num_pins_z=4,
    pin_diameter=8,
    use_smooth_boundary=True  # This is the default
)

# Disable if you want traditional binary representation
geom_binary = PinFinsGeometry(
    nx=60, ny=40, nz=40,
    num_pins_y=4, num_pins_z=4,
    pin_diameter=8,
    use_smooth_boundary=False
)
```

### Which Geometries Support Smooth Boundaries?

| Geometry | Smooth Support | Default | Notes |
|----------|---------------|---------|-------|
| **Pin Fins** | ✅ Yes | Enabled | Cylindrical pins benefit most |
| **Kelvin Cells** | ✅ Yes | Enabled | Smooth cylindrical struts |
| **Channel** | ⚠️ Limited | Disabled | Already rectangular |
| **Duct** | ⚠️ Limited | Disabled | Already rectangular |
| **Skived Fins** | ⚠️ Limited | Disabled | Already planar |

### Accessing Smooth Boundary Data

```python
# Get the solid fraction field
solid_fraction = geom.get_solid_fraction()  # 3D array, values 0.0-1.0

# Check if geometry uses smooth boundaries
has_smooth = geom.has_smooth_boundary()  # True/False

# Get quality metrics
metrics = geom.compute_geometry_quality_metrics()
print(f"Has smooth boundary: {metrics['has_smooth_boundary']}")
print(f"Resolution ratio: {metrics['resolution_ratio']:.1f}")
```

## Computational Cost

### Memory Usage

Smooth boundaries add a `solid_fraction` field:
- **Binary mask:** 1 byte per voxel (boolean)
- **Solid fraction:** 8 bytes per voxel (float64)
- **Total increase:** ~8× for geometry data (small compared to LBM fields)

**Example:**
- Grid: 100×100×100 = 1 million voxels
- Binary mask: 1 MB
- With solid fraction: 9 MB
- LBM distribution functions: ~600 MB
- **Geometry overhead: < 2%**

### Computation Time

Smooth boundary generation is more expensive:
- Multi-point sampling: 25-125 samples per boundary voxel
- Only affects geometry creation (one-time cost)
- LBM simulation speed is nearly identical

**Typical generation times:**

| Grid Size | Binary | Smooth | Ratio |
|-----------|--------|--------|-------|
| 40×40×40 | 0.1s | 0.5s | 5× |
| 60×60×60 | 0.3s | 2s | 7× |
| 100×100×100 | 1s | 10s | 10× |

**Recommendation:** The one-time cost is negligible compared to simulation time.

## Resolution Validation

The package automatically validates resolution and issues warnings:

```python
# This will issue a warning
geom = PinFinsGeometry(nx=30, ny=20, nz=20, pin_diameter=3)
# UserWarning: Pin diameter (3 cells) may have insufficient resolution.
# Recommended: at least 6 cells per diameter for smooth pins.
```

You can check warnings programmatically:

```python
import warnings

with warnings.catch_warnings(record=True) as w:
    geom = PinFinsGeometry(nx=30, ny=20, nz=20, pin_diameter=3)
    if w:
        print(f"Geometry warning: {w[0].message}")
```

## Best Practices

### 1. Start with Recommended Resolutions

Use the resolution guidelines above as starting points.

### 2. Enable Smooth Boundaries for Curved Surfaces

Always use `use_smooth_boundary=True` for:
- Pin fins (cylindrical)
- Kelvin cells (cylindrical struts)
- Any custom geometry with curves

### 3. Verify Geometry Quality

```python
metrics = geom.compute_geometry_quality_metrics()
print(f"Porosity: {metrics['porosity']:.3f}")
print(f"Surface area: {metrics['surface_area']:.2f}")
print(f"Has smooth boundary: {metrics['has_smooth_boundary']}")
print(f"Resolution ratio: {metrics['resolution_ratio']:.1f}")
```

### 4. Visualize Before Simulating

```python
from lbm_cht import Visualizer

vis = Visualizer(geom)

# Check geometry slices
fig1 = vis.plot_geometry_slice(axis='z', position=nz//2)

# For smooth boundaries, also check solid fraction
import matplotlib.pyplot as plt
plt.imshow(geom.solid_fraction[:, :, nz//2].T, cmap='viridis', vmin=0, vmax=1)
plt.colorbar(label='Solid Fraction')
plt.title('Solid Fraction Field')
plt.show()
```

### 5. Balance Resolution with Computational Cost

Higher resolution is better, but:
- Memory scales as nx × ny × nz
- Computation time scales as nx × ny × nz × num_timesteps
- For 2× finer resolution: 8× memory, 16× computation time

**Strategy:**
1. Start with minimum recommended resolution
2. Run short simulation (100 steps)
3. Check if results are reasonable
4. If needed, increase resolution by 1.5× and retest

### 6. Document Your Resolution Choice

Always document the resolution used:

```python
# Good practice - explain resolution choice
config = {
    'nx': 80, 'ny': 60, 'nz': 60,  # Grid resolution
    'pin_diameter': 10,              # 10 cells per diameter
    'dx': 0.001,                     # 1mm physical spacing
    'rationale': 'Pin diameter = 10mm physical = 10 cells ensures smooth representation'
}

geom = PinFinsGeometry(**config)
```

## Troubleshooting

### Problem: Jagged boundaries even with smooth boundaries enabled

**Solution:** Increase resolution. Smooth boundaries help, but can't fix extremely low resolution.

### Problem: Too slow to generate geometry

**Solution:** 
- Reduce grid size or disable smooth boundaries for testing
- Use smooth boundaries only for production runs

### Problem: Warnings about insufficient resolution

**Solution:**
- Increase grid dimensions (nx, ny, nz)
- Or increase feature sizes (pin_diameter, strut_thickness, etc.)
- Or accept the warning if you're just testing

### Problem: Simulation unstable despite smooth boundaries

**Solution:**
- Check LBM time step (dt) - may need to reduce
- Verify boundary conditions are properly applied
- Check for unrealistic geometry (e.g., pins too close together)

## Examples

See the `examples/` directory:
- `example4_resolution_comparison.py` - Compare different resolutions
- `test_smooth_geometry.py` - Comprehensive testing of smooth boundaries

## References

1. **Bouzidi et al. (2001)** - Momentum transfer of a Boltzmann-lattice fluid with boundaries
2. **Filippova & Hänel (1998)** - Grid refinement for lattice-BGK models
3. **Guo et al. (2002)** - Discrete lattice effects on forcing term
4. **Mei et al. (2002)** - Force evaluation in LBM

## Summary

✅ **Use smooth boundaries** for curved geometries (pin fins, Kelvin cells)
✅ **Follow resolution guidelines** (≥6 cells per diameter for pins)
✅ **Validate your geometry** using quality metrics
✅ **Visualize before simulating** to check geometry quality
✅ **Balance accuracy with cost** - start with recommended resolutions
