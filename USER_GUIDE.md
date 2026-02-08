# User Guide

## Introduction

This guide will help you get started with the LBM-CHT package for simulating conjugate heat transfer in complex 3D structures using the Lattice Boltzmann Method.

## Table of Contents

1. [Basic Concepts](#basic-concepts)
2. [Your First Simulation](#your-first-simulation)
3. [Understanding Parameters](#understanding-parameters)
4. [Working with Geometries](#working-with-geometries)
5. [Setting Up Flow](#setting-up-flow)
6. [Adding Heat Transfer](#adding-heat-transfer)
7. [Boundary Conditions](#boundary-conditions)
8. [Post-Processing](#post-processing)
9. [Troubleshooting](#troubleshooting)

## Basic Concepts

### Lattice Boltzmann Method (LBM)

LBM is a computational fluid dynamics method that:
- Solves on a regular lattice (grid)
- Uses particle distribution functions
- Is naturally parallel and scales well
- Handles complex geometries easily

### Key Components

1. **Lattice**: D3Q19 (3D with 19 velocity directions)
2. **Collision**: MRT (Multiple Relaxation Time) for stability
3. **Forcing**: Shan-Chen with EDM for momentum sources
4. **Heat Transfer**: Double distribution function

## Your First Simulation

### Minimal Working Example

```python
from src.flow_solver import FlowSolver

# Create a small domain
solver = FlowSolver(nx=32, ny=32, nz=32, viscosity=0.01)

# Initialize
solver.initialize()

# Run for 1000 steps
solver.run(n_steps=1000)

# Get results
velocity = solver.u
density = solver.rho
```

### Simple Channel Flow

```python
from src.flow_solver import FlowSolver
from src.geometry import GyroidGenerator
import numpy as np

# Create domain and solver
nx, ny, nz = 64, 32, 32
solver = FlowSolver(nx, ny, nz, viscosity=0.01)

# Create channel geometry
geom = GyroidGenerator(nx, ny, nz)
solid_mask = geom.generate_channel(channel_height=24)
solver.set_solid_mask(solid_mask)

# Add driving force
force = np.zeros((nx, ny, nz, 3))
force[:, :, :, 0] = 0.0001  # Force in x-direction
solver.set_external_force(force)

# Run simulation
solver.initialize()
solver.run(n_steps=5000)
```

## Understanding Parameters

### Lattice Units

All quantities in LBM are in lattice units (dimensionless):

- **Length**: Measured in lattice nodes (1 = one grid spacing)
- **Time**: Measured in time steps (1 = one iteration)
- **Velocity**: Lattice nodes per time step

### Key Parameters

#### Viscosity

```python
viscosity = 0.01  # Lattice units
```

- Controls fluid thickness/resistance
- Lower = thinner fluid (higher Re)
- Typical range: 0.001 - 0.1
- Related to relaxation time: `τ = 0.5 + ν/cs²`

#### Reynolds Number

```python
Re = U * L / viscosity
```

- Characterizes flow regime
- Low Re (<100): Laminar, viscous-dominated
- High Re (>1000): Turbulent-like, inertia-dominated
- Our implementation stable up to Re ~ 2000

#### Thermal Parameters

```python
thermal_diffusivity = 0.01  # Fluid
alpha_solid = 0.001  # Solid (lower for higher conductivity ratio)
```

- Controls heat diffusion
- Prandtl number: `Pr = viscosity / thermal_diffusivity`

## Working with Geometries

### Built-in Geometries

#### Channel

```python
from src.geometry import GyroidGenerator

geom = GyroidGenerator(nx, ny, nz)
solid_mask = geom.generate_channel(channel_height=20)
```

#### Sphere

```python
solid_mask = geom.generate_sphere(
    center=(nx//2, ny//2, nz//2),
    radius=10
)
```

#### Box with Walls

```python
solid_mask = geom.generate_simple_box(wall_thickness=2)
```

### Gyroid Structures

#### Basic Gyroid

```python
solid_mask = geom.generate_gyroid(
    threshold=0.0,    # Controls porosity
    scale=2.0,        # Unit cell size
    surface_type='G'  # 'G', 'D', or 'P'
)

# Check porosity
porosity = geom.calculate_porosity(solid_mask)
print(f"Porosity: {porosity:.2f}")
```

#### Auto-adjust for Target Porosity

```python
threshold, solid_mask = geom.adjust_threshold_for_porosity(
    target_porosity=0.7,
    scale=2.0,
    tolerance=0.01
)
```

### Custom Geometries

```python
import numpy as np

# Create your own geometry
solid_mask = np.zeros((nx, ny, nz), dtype=bool)

# Add solid regions
solid_mask[10:20, :, :] = True  # Vertical wall

# Combine geometries
gyroid = geom.generate_gyroid(threshold=0.0, scale=2.0)
walls = geom.generate_simple_box(wall_thickness=2)
combined = gyroid | walls  # Union
```

## Setting Up Flow

### Pressure-Driven Flow

```python
# Apply body force (pressure gradient)
force = np.zeros((nx, ny, nz, 3))
force[:, :, :, 0] = force_magnitude  # x-direction

solver.set_external_force(force)
```

### Inlet/Outlet Flow

```python
# Use Zou-He boundary conditions
# (Implementation in boundary_conditions.py)
```

### Lid-Driven Cavity

```python
# Apply moving wall BC at top boundary
# (See examples/cavity_flow.py)
```

## Adding Heat Transfer

### Basic Thermal Simulation

```python
from src.thermal_solver import ThermalSolver

# Create thermal solver
thermal = ThermalSolver(nx, ny, nz, thermal_diffusivity=0.01)

# Set initial temperature
T0 = np.ones((nx, ny, nz))
T0[:nx//2, :, :] = 1.0  # Hot region
T0[nx//2:, :, :] = 0.0  # Cold region

thermal.initialize(T0)

# Run
thermal.run(n_steps=5000)
```

### Conjugate Heat Transfer

```python
from src.conjugate_ht import ConjugateHTSolver

# Create coupled solver
solver = ConjugateHTSolver(
    nx, ny, nz,
    viscosity=0.01,
    alpha_fluid=0.01,
    alpha_solid=0.001,
    k_ratio=10.0  # Conductivity ratio
)

# Set geometry
solver.set_geometry(solid_mask)

# Initialize
solver.initialize(T0=T0)

# Run coupled simulation
solver.run(n_steps=10000)
```

## Boundary Conditions

### No-Slip Walls (Bounce-Back)

```python
# Automatically applied to solid regions
solver.set_solid_mask(solid_mask)
```

### Periodic Boundaries

```python
# Automatically handled by streaming with np.roll
# No special code needed
```

### Thermal Boundaries

```python
# Constant temperature wall
from src.boundary_conditions import boundary_conditions as bc

g = bc.thermal_constant_temperature(g, T_wall=1.0, wall_mask=wall_mask)

# Adiabatic wall
g = bc.thermal_adiabatic(g, wall_mask=wall_mask)
```

## Post-Processing

### Extracting Results

```python
# Velocity field
velocity = solver.u  # Shape: (nx, ny, nz, 3)
u_magnitude = np.sqrt(np.sum(velocity**2, axis=3))

# Temperature
temperature = thermal.T  # Shape: (nx, ny, nz)

# Vorticity
vorticity = solver.get_vorticity()

# Heat flux
heat_flux = thermal.get_heat_flux()
```

### Visualization

```python
from src.visualization import (plot_velocity_slice, 
                               plot_temperature_slice,
                               plot_3d_geometry)

# 2D slices
plot_velocity_slice(velocity, z_slice=nz//2, 
                   filename='velocity.png')

plot_temperature_slice(temperature, z_slice=nz//2,
                      filename='temperature.png')

# 3D geometry
plot_3d_geometry(solid_mask, filename='geometry.png')
```

### Export to ParaView

```python
from src.visualization import export_to_vtk

export_to_vtk('results',
             velocity=velocity,
             temperature=temperature,
             pressure=density/3.0,
             solid_mask=solid_mask)

# Creates: results_velocity.vti, results_temperature.vti, etc.
# Open in ParaView for interactive 3D visualization
```

### Calculate Dimensionless Numbers

```python
from src.utils import (calculate_reynolds_number,
                      calculate_nusselt_number)

Re = calculate_reynolds_number(U_avg, L, viscosity)
Nu = calculate_nusselt_number(q_avg, dT, L, conductivity)

print(f"Reynolds number: {Re:.2f}")
print(f"Nusselt number: {Nu:.2f}")
```

## Troubleshooting

### Simulation Diverges

**Symptoms**: Velocity or temperature values become NaN or very large

**Solutions**:
1. Decrease velocity/force: `force *= 0.1`
2. Increase viscosity: `viscosity *= 2`
3. Use smaller domain initially
4. Check boundary conditions
5. Ensure MRT relaxation times are appropriate

### Simulation Too Slow

**Solutions**:
1. Reduce domain size for testing
2. Use fewer time steps initially
3. Increase output interval: `output_interval=1000`
4. Install Numba: `pip install numba`
5. Reduce number of fields to save

### Low Reynolds Number Not Achieved

**Causes**: Force too weak or domain too small

**Solutions**:
1. Increase driving force
2. Decrease viscosity (but watch stability!)
3. Use larger domain
4. Check force is applied correctly

### Temperature Not Changing

**Causes**: Thermal diffusivity too low or not enough time steps

**Solutions**:
1. Increase thermal diffusivity
2. Run more time steps
3. Check initial conditions
4. Verify thermal boundaries

### Memory Issues

**Solutions**:
1. Reduce domain size
2. Output less frequently
3. Don't store all time steps
4. Use HDF5 for large data: `save_field_hdf5()`

## Tips and Best Practices

### Starting a New Simulation

1. **Start small**: Use 32³ or 64³ domain for testing
2. **Validate**: Run simple cases with known solutions first
3. **Monitor**: Watch convergence and stability
4. **Scale up**: Gradually increase domain size and complexity

### Choosing Parameters

1. **Viscosity**: Start with 0.01, adjust for desired Re
2. **Time steps**: Run until convergence (check residuals)
3. **Force**: Start small, increase until desired velocity
4. **Resolution**: Ensure at least 10 nodes across features

### Performance Optimization

1. Use appropriate output intervals
2. Don't compute/save unnecessary fields
3. Profile your code to find bottlenecks
4. Consider Numba for critical loops
5. Use HDF5 for large datasets

## Next Steps

After mastering the basics:

1. Run all validation examples
2. Try different geometries
3. Experiment with parameters
4. Develop your own applications
5. Contribute improvements!

## Getting Help

- Check the [README](README.md) for comprehensive documentation
- Review [examples/](examples/) for working code
- Run tests to verify installation
- Open GitHub issue for bugs
- Check references for theory

---

**Happy simulating!**
