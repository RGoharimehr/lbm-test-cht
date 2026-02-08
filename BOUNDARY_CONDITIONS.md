# Boundary Conditions Guide - Wall Thickness and Inlet/Outlet Specification

## Overview

This guide explains how boundary conditions, wall thickness, and inlet/outlet regions are specified in the LBM CHT package. Understanding these parameters is crucial for accurate simulations.

## Table of Contents

1. [Wall Thickness Specification](#wall-thickness-specification)
2. [Inlet and Outlet Regions](#inlet-and-outlet-regions)
3. [Number of Lattice Nodes](#number-of-lattice-nodes)
4. [Boundary Condition Types](#boundary-condition-types)
5. [Best Practices](#best-practices)
6. [Examples](#examples)

## Wall Thickness Specification

### How Wall Thickness is Defined

Wall thickness is specified in **lattice units** (number of grid cells) when creating geometry objects.

### Geometry-Specific Wall Thickness

#### 1. Duct Geometry

```python
from lbm_cht import DuctGeometry

# Create duct with 2 lattice units wall thickness (default)
geom = DuctGeometry(
    nx=50, ny=30, nz=30,
    wall_thickness=2,  # Wall thickness in lattice units
    dx=0.001  # Physical lattice spacing (1mm)
)

# Physical wall thickness = wall_thickness × dx = 2 × 0.001m = 2mm
```

**Duct geometry walls:**
- Bottom wall: `y ∈ [0, wall_thickness)`
- Top wall: `y ∈ [ny - wall_thickness, ny)`
- Left wall: `z ∈ [0, wall_thickness)`
- Right wall: `z ∈ [nz - wall_thickness, nz)`

**Recommended wall thickness:**
- Minimum: 2 lattice units (captures basic solid region)
- Recommended: 3-5 lattice units for accurate heat conduction
- Maximum: Should not exceed 20% of channel dimension

#### 2. Pin Fins / Skived Fins Geometry

```python
from lbm_cht import PinFinsGeometry, SkivedFinsGeometry

# Pin fins have a base plate
pin_fins = PinFinsGeometry(
    nx=60, ny=40, nz=40,
    num_pins_y=4, num_pins_z=4,
    pin_diameter=8  # Pin diameter in lattice units
)
# Base plate thickness is hardcoded to 2 lattice units at y ∈ [0, 2)

# Skived fins also have a base plate
skived_fins = SkivedFinsGeometry(
    nx=50, ny=30, nz=30,
    num_fins=10,
    fin_thickness=2  # Fin thickness in lattice units
)
# Base plate thickness is hardcoded to 2 lattice units at y ∈ [0, 2)
```

#### 3. Channel Geometry

```python
from lbm_cht import ChannelGeometry

# Channel has solid walls surrounding the fluid region
channel = ChannelGeometry(
    nx=50, ny=30, nz=30,
    channel_height_ratio=0.5,  # Channel is 50% of ny
    channel_width_ratio=0.5    # Channel is 50% of nz
)

# Wall thickness is implicitly defined by the ratio
# Wall thickness = (ny - channel_height) / 2 on top and bottom
# Wall thickness = (nz - channel_width) / 2 on left and right
```

**Example calculation:**
```python
ny = 30
channel_height_ratio = 0.5
channel_height = int(30 × 0.5) = 15
wall_thickness_y = (30 - 15) / 2 = 7.5 ≈ 7 lattice units (top and bottom)
```

### Wall Thickness Guidelines

| Geometry Type | Parameter | Typical Range | Recommendation |
|--------------|-----------|---------------|----------------|
| Duct | `wall_thickness` | 2-10 | 3-5 for heat transfer |
| Pin Fins | base plate | Fixed at 2 | Adequate for most cases |
| Skived Fins | `fin_thickness` | 2-4 | 2-3 for thin fins |
| Channel | implicit | 5-15 | Adjust via ratios |

## Inlet and Outlet Regions

### Current Implementation

The LBM solver uses **periodic boundary conditions** by default (due to `np.roll` in streaming step). Inlet and outlet conditions must be explicitly set.

### Defining Inlet and Outlet Regions

Inlet and outlet regions are typically defined at the **x-boundaries** of the domain:

```python
# Standard convention:
# - Inlet: x = 0 (left side, x ∈ [0, n_inlet))
# - Outlet: x = nx-1 (right side, x ∈ [nx - n_outlet, nx))
# - Main domain: x ∈ [n_inlet, nx - n_outlet)
```

### Number of Lattice Nodes for Inlet/Outlet

#### Recommended Node Counts

| Domain Size | Inlet Nodes | Outlet Nodes | Reasoning |
|------------|-------------|--------------|-----------|
| Small (nx < 50) | 3-5 | 3-5 | Minimum for stability |
| Medium (50 ≤ nx < 100) | 5-8 | 5-8 | Good balance |
| Large (nx ≥ 100) | 8-12 | 8-12 | Better accuracy |

**Rule of thumb:** Use 5-10% of nx for inlet/outlet regions, but not less than 5 nodes each.

#### Example Configuration

```python
from lbm_cht import ChannelGeometry, LBMSolver
from lbm_cht.materials import CommonMaterials

# Create geometry
nx, ny, nz = 80, 40, 40
geometry = ChannelGeometry(nx, ny, nz)

# Define inlet/outlet regions
n_inlet = 8   # 8 lattice nodes for inlet (10% of nx)
n_outlet = 8  # 8 lattice nodes for outlet (10% of nx)

# Create solver
fluid = CommonMaterials.water(temperature=300)
solid = CommonMaterials.aluminum()
solver = LBMSolver(geometry, fluid, solid)

# Set inlet boundary condition (hot inlet)
T_inlet = 350.0  # K
solver.T[:n_inlet, :, :] = T_inlet

# Set outlet boundary condition (cold outlet)
T_outlet = 300.0  # K
solver.T[-n_outlet:, :, :] = T_outlet

# Reinitialize distribution functions
solver.initialize_distributions()
```

## Number of Lattice Nodes

### Why Node Count Matters

1. **Boundary Layer Resolution:**
   - Thermal boundary layer needs adequate resolution
   - Velocity boundary layer needs adequate resolution
   - Too few nodes → inaccurate gradients
   - Too many nodes → wasted computation

2. **Numerical Stability:**
   - Boundary conditions affect stability
   - Sharp gradients at boundaries need smoothing
   - Inlet/outlet nodes provide transition region

3. **Physical Accuracy:**
   - Inlet: Develops flow profile
   - Outlet: Allows flow to exit smoothly
   - Walls: Captures heat conduction

### Minimum Requirements

**Inlet/Outlet:**
- **Absolute minimum:** 3 nodes (barely functional)
- **Recommended minimum:** 5 nodes (basic accuracy)
- **Good practice:** 8-12 nodes (reliable results)

**Wall Thickness:**
- **Absolute minimum:** 2 nodes (captures solid region)
- **Recommended minimum:** 3 nodes (basic heat conduction)
- **Good practice:** 4-6 nodes (accurate temperature gradients)

### Resolution vs Domain Size

```python
# Example scaling with domain size

# Small domain
nx_small = 40
n_inlet_small = max(5, int(0.1 * nx_small))  # 5 nodes (12.5%)
n_wall_small = 3  # 3 nodes

# Medium domain  
nx_medium = 80
n_inlet_medium = int(0.1 * nx_medium)  # 8 nodes (10%)
n_wall_medium = 4  # 4 nodes

# Large domain
nx_large = 200
n_inlet_large = int(0.05 * nx_large)  # 10 nodes (5%)
n_wall_large = 6  # 6 nodes
```

## Boundary Condition Types

### 1. Temperature Boundary Conditions

#### Fixed Temperature (Dirichlet)

```python
# Hot inlet
T_inlet = 350.0
solver.T[:n_inlet, :, :] = T_inlet

# Cold outlet
T_outlet = 300.0
solver.T[-n_outlet:, :, :] = T_outlet

# Re-initialize after setting temperatures
solver.initialize_distributions()
```

#### Fixed Heat Flux (Neumann)

Currently not directly implemented. Can be approximated:

```python
# Set temperature gradient at boundary
q_wall = 1000.0  # W/m²
k = solid_material.thermal_conductivity
dx = solver.dx

# Approximate heat flux boundary
dT = q_wall * dx / k
for i in range(wall_thickness):
    solver.T[:, i, :] = T_base + i * dT
```

### 2. Velocity Boundary Conditions

#### No-Slip at Walls (Default)

Implemented via bounce-back in `boundary_conditions()`:

```python
# Bounce-back at solid walls (no-slip condition)
for i in range(1, 19):
    opp = solver.get_opposite_direction(i)
    solver.f[i][solver.solid_mask] = solver.f[opp][solver.solid_mask]
```

This automatically enforces zero velocity at solid walls.

#### Inlet Velocity (Future Enhancement)

For forced convection, inlet velocity should be specified:

```python
# Desired inlet velocity (m/s)
u_inlet = 0.01  # 1 cm/s

# Set inlet velocity (current workaround)
solver.u[0, :n_inlet, :, :] = u_inlet  # x-direction velocity
```

## Best Practices

### 1. Wall Thickness Selection

✅ **Do:**
- Use 3-5 lattice units for walls with heat conduction
- Ensure wall thickness ≥ 2 for solid regions
- Scale with overall grid resolution
- Document physical dimensions (lattice units × dx)

❌ **Don't:**
- Use 1 lattice unit for walls (too thin)
- Make walls > 20% of channel dimension (wasteful)
- Mix very thin walls with coarse grids

### 2. Inlet/Outlet Configuration

✅ **Do:**
- Use 5-10% of nx for inlet/outlet, minimum 5 nodes
- Apply boundary conditions before initialize_distributions()
- Re-initialize distributions after changing BC
- Check that inlet/outlet don't overlap with walls

❌ **Don't:**
- Use < 3 nodes for inlet/outlet (unstable)
- Set conflicting temperature values
- Forget to reinitialize distributions
- Apply BC in solid regions

### 3. Resolution Considerations

✅ **Do:**
- Increase inlet/outlet nodes with larger domains
- Increase wall thickness for better heat transfer accuracy
- Validate results with resolution studies
- Document all boundary settings

❌ **Don't:**
- Use fixed node counts regardless of domain size
- Neglect boundary layer resolution
- Assume results are grid-independent
- Ignore validation warnings

## Examples

### Example 1: Configurable Inlet/Outlet

```python
from lbm_cht import ChannelGeometry, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials
import numpy as np

# Domain setup
nx, ny, nz = 100, 40, 40
dx = 0.001  # 1mm lattice spacing

# Boundary region sizes
n_inlet = int(0.08 * nx)   # 8 nodes (8%)
n_outlet = int(0.08 * nx)  # 8 nodes (8%)
wall_thickness = 4         # 4 nodes

print(f"Domain: {nx}×{ny}×{nz}")
print(f"Inlet nodes: {n_inlet} ({n_inlet/nx*100:.1f}%)")
print(f"Outlet nodes: {n_outlet} ({n_outlet/nx*100:.1f}%)")
print(f"Wall thickness: {wall_thickness} ({wall_thickness*dx*1000:.1f}mm)")

# Create geometry with specified wall thickness
geometry = ChannelGeometry(
    nx=nx, ny=ny, nz=nz,
    channel_height_ratio=0.7,
    channel_width_ratio=0.7
)

# Materials
fluid = CommonMaterials.water(temperature=300)
solid = CommonMaterials.aluminum()

# Create solver
solver = LBMSolver(geometry, fluid, solid, dx=dx, dt=1e-5)

# Set inlet condition (hot)
T_inlet = 350.0
solver.T[:n_inlet, :, :] = T_inlet
print(f"Inlet temperature: {T_inlet}K")

# Set outlet condition (ambient)
T_outlet = 300.0
solver.T[-n_outlet:, :, :] = T_outlet
print(f"Outlet temperature: {T_outlet}K")

# Reinitialize
solver.initialize_distributions()

# Run simulation
print("\nRunning simulation...")
solver.run(num_steps=1000)

# Visualize
visualizer = Visualizer(geometry, solver)
fig = visualizer.plot_temperature_slice(axis='z', position=nz//2)
```

### Example 2: Multiple Wall Thicknesses

```python
from lbm_cht import DuctGeometry
import matplotlib.pyplot as plt

# Compare different wall thicknesses
wall_thicknesses = [2, 4, 6, 8]
geometries = []

for wt in wall_thicknesses:
    geom = DuctGeometry(
        nx=60, ny=40, nz=40,
        wall_thickness=wt,
        dx=0.001
    )
    geometries.append((wt, geom))
    
    porosity = geom.get_porosity()
    print(f"Wall thickness: {wt} nodes ({wt*0.001*1000:.1f}mm)")
    print(f"  Porosity: {porosity:.3f}")
    print(f"  Solid volume: {geom.get_solid_volume():.6f} m³")

# Visualize
fig, axes = plt.subplots(2, 2, figsize=(12, 12))
axes = axes.flatten()

for idx, (wt, geom) in enumerate(geometries):
    slice_data = geom.solid_mask[:, :, 20]
    axes[idx].imshow(slice_data.T, origin='lower', cmap='gray')
    axes[idx].set_title(f'Wall Thickness: {wt} nodes')
    axes[idx].set_xlabel('X')
    axes[idx].set_ylabel('Y')

plt.tight_layout()
plt.savefig('wall_thickness_comparison.png', dpi=150)
```

### Example 3: Inlet/Outlet Node Count Study

```python
from lbm_cht import ChannelGeometry, LBMSolver
from lbm_cht.materials import CommonMaterials
import numpy as np

# Fixed domain
nx, ny, nz = 80, 30, 30

# Test different inlet/outlet node counts
node_counts = [3, 5, 8, 12]
results = []

for n_bc in node_counts:
    geometry = ChannelGeometry(nx, ny, nz)
    fluid = CommonMaterials.water()
    solid = CommonMaterials.aluminum()
    solver = LBMSolver(geometry, fluid, solid)
    
    # Set BC
    solver.T[:n_bc, :, :] = 350.0  # Inlet
    solver.T[-n_bc:, :, :] = 300.0  # Outlet
    solver.initialize_distributions()
    
    # Run short simulation
    solver.run(num_steps=100)
    
    # Check temperature gradient at boundaries
    grad_inlet = np.mean(np.abs(solver.T[n_bc, :, :] - solver.T[n_bc-1, :, :]))
    grad_outlet = np.mean(np.abs(solver.T[-n_bc, :, :] - solver.T[-n_bc-1, :, :]))
    
    results.append({
        'n_nodes': n_bc,
        'percentage': n_bc/nx*100,
        'grad_inlet': grad_inlet,
        'grad_outlet': grad_outlet
    })
    
    print(f"BC nodes: {n_bc} ({n_bc/nx*100:.1f}%)")
    print(f"  Inlet gradient: {grad_inlet:.3f} K")
    print(f"  Outlet gradient: {grad_outlet:.3f} K")
```

## Troubleshooting

### Problem: Simulation Unstable at Boundaries

**Cause:** Too few inlet/outlet nodes or too sharp temperature gradients

**Solution:**
- Increase inlet/outlet nodes to at least 8
- Use gradual temperature transitions
- Reduce temperature difference

### Problem: Inaccurate Heat Transfer at Walls

**Cause:** Wall thickness too small

**Solution:**
- Increase wall thickness to 4-6 lattice units
- Refine grid resolution near walls
- Check that dx is appropriate for physical wall thickness

### Problem: Flow Not Developing Properly

**Cause:** Insufficient inlet region

**Solution:**
- Increase inlet nodes to allow flow development
- Check that inlet velocity is not too high
- Ensure inlet region is in fluid, not solid

## Summary

**Key Parameters:**

| Parameter | Typical Value | Units | Set Where |
|-----------|---------------|-------|-----------|
| Wall thickness | 3-5 | lattice units | Geometry constructor |
| Inlet nodes | 5-10% of nx | lattice units | Manual BC setup |
| Outlet nodes | 5-10% of nx | lattice units | Manual BC setup |
| Min wall thickness | 2 | lattice units | Geometry constructor |
| Min inlet/outlet | 5 | lattice units | Manual BC setup |

**Setup Checklist:**

✅ Define wall thickness in geometry (3-5 nodes recommended)
✅ Calculate inlet/outlet node count (5-10% of nx, min 5 nodes)
✅ Set inlet temperature: `solver.T[:n_inlet, :, :] = T_inlet`
✅ Set outlet temperature: `solver.T[-n_outlet:, :, :] = T_outlet`
✅ Reinitialize: `solver.initialize_distributions()`
✅ Document physical dimensions: nodes × dx

## References

1. **LBM Theory:** Succi, S. "The Lattice Boltzmann Equation for Fluid Dynamics and Beyond"
2. **Boundary Conditions:** Zou, Q. & He, X. "On pressure and velocity boundary conditions for the lattice Boltzmann BGK model"
3. **Conjugate Heat Transfer:** Karani, H. & Huber, C. "Lattice Boltzmann formulation for conjugate heat transfer"
