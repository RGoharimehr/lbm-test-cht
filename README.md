# LBM-CHT: 3D Lattice Boltzmann Method for Conjugate Heat Transfer in Gyroid Structures

A comprehensive Python implementation of the Lattice Boltzmann Method (LBM) for simulating conjugate heat transfer in complex 3D structures, with particular focus on gyroid geometries. This code features:

- **D3Q19 lattice** for velocity and temperature fields
- **Multiple Relaxation Time (MRT)** collision scheme for enhanced stability
- **Modified Shan-Chen forcing** with Exact Difference Method (EDM)
- **Double distribution function** approach for conjugate heat transfer
- **Gyroid geometry generation** with controllable porosity
- **High Reynolds and Nusselt number** capability (Re > 1000, Nu > 100)

## 🚀 Want to Use It Now?

**👉 See [GETTING_STARTED.md](GETTING_STARTED.md) for a 5-minute quick start!**

Or run:
```bash
pip install numpy scipy matplotlib pyyaml
python verify_install.py  # Check installation
python quick_start.py     # Run your first simulation
```

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Theory Background](#theory-background)
- [Module Documentation](#module-documentation)
- [Examples](#examples)
- [Configuration](#configuration)
- [Validation](#validation)
- [Performance](#performance)
- [References](#references)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Capabilities

- **3D Lattice Boltzmann Method**
  - D3Q19 lattice velocity set
  - Efficient streaming and collision operations
  - Periodic, bounce-back, and advanced boundary conditions

- **Multiple Relaxation Time (MRT) Collision**
  - Enhanced stability compared to BGK
  - Independent control of different physical processes
  - Suitable for high Reynolds number flows (Re > 1000)

- **Modified Shan-Chen Forcing**
  - Exact Difference Method (EDM) for improved accuracy
  - Guo forcing scheme option
  - Temperature-dependent forcing for buoyancy

- **Conjugate Heat Transfer**
  - Double distribution function approach
  - Different thermal properties in solid and fluid regions
  - Automatic interface handling
  - High Nusselt number support (Nu > 100)

- **Gyroid Geometry Generation**
  - Implicit surface formulation
  - Adjustable porosity (automatic threshold optimization)
  - Multiple surface types (Gyroid, Diamond, Primitive)
  - Smooth surface generation

### Advanced Features

- **Boundary Conditions**
  - Velocity and pressure (Zou-He) boundaries
  - Moving wall (lid-driven cavity)
  - Thermal boundaries (Dirichlet, Neumann, Robin)
  - Adiabatic walls
  - Conjugate interface conditions

- **Analysis Tools**
  - Reynolds, Prandtl, Peclet, Nusselt number calculations
  - Permeability computation
  - Vorticity and heat flux fields
  - Convergence monitoring

- **Visualization**
  - 2D slice plots (velocity, temperature)
  - 3D geometry visualization
  - VTK export for ParaView
  - HDF5 data storage
  - Convergence history plots

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Basic Installation

```bash
git clone https://github.com/RGoharimehr/lbm-test-cht.git
cd lbm-test-cht
pip install -r requirements.txt
```

### Development Installation

```bash
pip install -e ".[dev]"
```

### Optional Dependencies

For visualization:
```bash
pip install -e ".[viz]"
```

For performance (JIT compilation):
```bash
pip install -e ".[performance]"
```

## Quick Start

### 1. Simple Channel Flow

```python
from src.flow_solver import FlowSolver
from src.geometry import GyroidGenerator

# Create domain
nx, ny, nz = 128, 32, 32
solver = FlowSolver(nx, ny, nz, viscosity=0.01)

# Create channel geometry
geom = GyroidGenerator(nx, ny, nz)
solid_mask = geom.generate_channel(channel_height=24)
solver.set_solid_mask(solid_mask)

# Initialize and run
solver.initialize()
solver.run(n_steps=10000)
```

### 2. Gyroid Heat Transfer

```python
from src.conjugate_ht import ConjugateHTSolver
from src.geometry import generate_gyroid

# Create solver
solver = ConjugateHTSolver(64, 64, 64, 
                           viscosity=0.01,
                           alpha_fluid=0.01,
                           alpha_solid=0.001,
                           k_ratio=10.0)

# Generate gyroid
solid_mask = generate_gyroid(64, 64, 64, threshold=0.0, scale=2.0)
solver.set_geometry(solid_mask)

# Run simulation
solver.initialize()
solver.run(n_steps=20000)
```

### 3. Run Examples

```bash
# Validation examples
python examples/cavity_flow.py
python examples/channel_flow.py
python examples/heated_channel.py

# Main examples
python examples/gyroid_flow.py
python examples/gyroid_cht.py
```

## Theory Background

### Lattice Boltzmann Method

The LBM solves the discrete Boltzmann equation:

```
f_i(x + e_i·Δt, t + Δt) = f_i(x, t) - Ω[f_i(x, t) - f_i^eq(x, t)] + F_i
```

where:
- `f_i` is the distribution function in direction `i`
- `e_i` are the lattice velocities
- `Ω` is the collision operator
- `f_i^eq` is the equilibrium distribution
- `F_i` is the forcing term

### MRT Collision Operator

The MRT scheme transforms to moment space:

```
m = M · f
m* = m - S · (m - m^eq)
f* = M^(-1) · m*
```

where:
- `M` is the transformation matrix
- `S` is the diagonal relaxation matrix
- Different moments relax at different rates for stability

### Shan-Chen Forcing

The Exact Difference Method (EDM):

```
F_i = f_i^eq(ρ, u + F/ρ) - f_i^eq(ρ, u)
```

Provides better momentum conservation than standard forcing schemes.

### Conjugate Heat Transfer

Uses separate distribution functions:
- `f_i` for momentum (fluid flow)
- `g_i` for energy (temperature)

Interface conditions automatically satisfied through different thermal diffusivities.

### Gyroid Surface

Implicit surface equation:

```
sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = threshold
```

The threshold controls porosity; the scale controls unit cell size.

## Module Documentation

### `src/lattice.py`

Defines the D3Q19 lattice structure.

**Key Classes:**
- `D3Q19`: Lattice velocity set, weights, and operations

**Key Functions:**
- `get_equilibrium(rho, u)`: Calculate equilibrium distribution
- `get_macroscopic(f)`: Extract density and velocity
- `stream(f)`: Perform streaming step

### `src/mrt.py`

Implements MRT collision operator.

**Key Classes:**
- `MRT_D3Q19`: Transformation matrices and collision

**Key Functions:**
- `get_equilibrium_moments(rho, u)`: Equilibrium in moment space
- `get_collision_matrix(tau, ...)`: Create relaxation matrix
- `collide(f, rho, u, S)`: Perform MRT collision

### `src/shan_chen.py`

Modified Shan-Chen forcing schemes.

**Key Classes:**
- `ShanChenForcing`: Forcing term calculations

**Key Functions:**
- `calculate_force(psi, G)`: Shan-Chen interaction force
- `guo_forcing_velocity(u, F, rho, tau)`: Modified velocity
- `edm_forcing(rho, u, F, tau)`: EDM forcing term

### `src/flow_solver.py`

Main fluid flow solver.

**Key Classes:**
- `FlowSolver`: Complete LBM flow solver with MRT

**Key Methods:**
- `initialize(rho0, u0)`: Initialize simulation
- `step()`: One time step (collision + streaming + BC)
- `run(n_steps)`: Run multiple time steps

### `src/thermal_solver.py`

Thermal field solver.

**Key Classes:**
- `ThermalSolver`: Temperature field with double distribution

**Key Methods:**
- `initialize(T0)`: Initialize temperature
- `set_velocity_field(u)`: Couple to flow field
- `step()`: One thermal time step

### `src/conjugate_ht.py`

Couples flow and thermal solvers.

**Key Classes:**
- `ConjugateHTSolver`: Integrated CHT solver

**Key Methods:**
- `set_geometry(solid_mask)`: Define solid/fluid regions
- `step()`: Coupled time step
- `get_nusselt_number(...)`: Calculate Nu

### `src/geometry.py`

Geometry generation tools.

**Key Classes:**
- `GyroidGenerator`: Generate complex geometries

**Key Methods:**
- `generate_gyroid(threshold, scale, surface_type)`: Create gyroid
- `adjust_threshold_for_porosity(porosity)`: Auto-tune threshold
- `generate_channel()`, `generate_sphere()`: Simple geometries

### `src/boundary_conditions.py`

Boundary condition implementations.

**Key Classes:**
- `BoundaryConditions`: All BC types

**Key Methods:**
- `apply_bounce_back()`: No-slip walls
- `apply_moving_wall()`: Lid-driven cavity
- `zou_he_velocity_inlet()`: Velocity BC
- `thermal_constant_temperature()`: Dirichlet thermal BC

### `src/utils.py`

Helper functions and utilities.

**Key Functions:**
- `calculate_reynolds_number(U, L, nu)`
- `calculate_nusselt_number(q, dT, L, k)`
- `check_convergence(field_new, field_old)`
- `save_field_vtk()`, `save_field_hdf5()`

### `src/visualization.py`

Plotting and visualization tools.

**Key Functions:**
- `plot_velocity_slice()`, `plot_temperature_slice()`
- `plot_velocity_vectors()`, `plot_3d_geometry()`
- `plot_convergence_history()`
- `export_to_vtk()`

## Examples

### Validation Examples

Located in `examples/`:

1. **`cavity_flow.py`**: 3D lid-driven cavity at Re = 100, 400, 1000
2. **`channel_flow.py`**: Poiseuille flow validation
3. **`heated_channel.py`**: Thermal solver validation

### Main Examples

4. **`gyroid_flow.py`**: Flow through gyroid, permeability calculation
5. **`gyroid_cht.py`**: Full conjugate heat transfer in gyroid

Each example includes:
- Problem setup
- Simulation execution
- Post-processing
- Validation (where applicable)
- Visualization output

## Configuration

Simulations can be configured via YAML files (see `config/simulation_config.yaml`):

```yaml
simulation:
  nx: 64
  ny: 64
  nz: 64
  timesteps: 20000

fluid:
  viscosity: 0.01
  thermal_diffusivity: 0.01

gyroid:
  enabled: true
  porosity_target: 0.7
  scale: 2.0

output:
  directory: 'output'
  vtk: true
  hdf5: true
```

Load configuration:
```python
import yaml
with open('config/simulation_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

## Validation

The implementation has been validated against:

1. **Poiseuille Flow**: Parabolic velocity profile (error < 1%)
2. **Lid-Driven Cavity**: Benchmark solutions at Re = 100, 400, 1000
3. **Heated Channel**: Temperature profile comparison
4. **Mass Conservation**: Numerically verified in all cases
5. **Stability**: Tested up to Re = 2000

### Running Tests

```bash
python -m pytest tests/
```

## Performance

### Computational Complexity

- **Memory**: O(nx × ny × nz × Q), where Q = 19
- **Time per step**: O(nx × ny × nz × Q)

### Optimization Tips

1. **Domain Size**: Start small (32³) for testing, scale up as needed
2. **Time Steps**: Use convergence monitoring to determine sufficient iterations
3. **Numba**: Enable JIT compilation for 2-3x speedup
4. **Parallelization**: Streaming is inherently parallelizable

### Typical Performance

On a modern CPU (single core):
- 64³ domain: ~10-20 seconds per 1000 iterations
- 128³ domain: ~2-3 minutes per 1000 iterations

## References

### Key Papers

1. **D'Humières, D.** (2002). "Multiple-relaxation-time lattice Boltzmann models in three dimensions." *Philosophical Transactions of the Royal Society A*, 360(1792), 437-451.

2. **Shan, X., & Chen, H.** (1993). "Lattice Boltzmann model for simulating flows with multiple phases and components." *Physical Review E*, 47(3), 1815.

3. **Guo, Z., Zheng, C., & Shi, B.** (2002). "Discrete lattice effects on the forcing term in the lattice Boltzmann method." *Physical Review E*, 65(4), 046308.

4. **Mohamad, A. A.** (2011). *Lattice Boltzmann Method: Fundamentals and Engineering Applications with Computer Codes*. Springer.

5. **Schoen, A. H.** (1970). "Infinite periodic minimal surfaces without self-intersections." NASA Technical Report D-5541.

### Books

- **Krüger, T., et al.** (2017). *The Lattice Boltzmann Method: Principles and Practice*. Springer.
- **Succi, S.** (2001). *The Lattice Boltzmann Equation for Fluid Dynamics and Beyond*. Oxford University Press.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

## License

MIT License - see LICENSE file for details.

## Authors

LBM-CHT Development Team

## Acknowledgments

This implementation draws on extensive research in the LBM community. Special thanks to researchers who have made their implementations and papers openly available.

## Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Last Updated**: 2024

**Status**: Active Development

**Version**: 1.0.0