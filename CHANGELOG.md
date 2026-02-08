# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-02-08

### Added

#### Core Features
- D3Q19 lattice implementation with velocity set, weights, and streaming
- Multiple Relaxation Time (MRT) collision operator
- Modified Shan-Chen forcing with EDM (Exact Difference Method)
- Guo forcing scheme implementation
- Double distribution function for conjugate heat transfer
- Fluid flow solver with MRT collision
- Thermal solver with separate temperature distribution
- Conjugate heat transfer coupling module

#### Geometry Generation
- Gyroid structure generation with implicit surface
- Automatic threshold adjustment for target porosity
- Diamond and Primitive surface types
- Simple geometries (channel, sphere, box)
- Geometry combination and smoothing utilities

#### Boundary Conditions
- Periodic boundary conditions (implicit in streaming)
- Bounce-back for no-slip walls
- Moving wall boundary condition
- Zou-He velocity and pressure boundaries
- Thermal boundary conditions (Dirichlet, Neumann, adiabatic)
- Conjugate interface handling

#### Analysis and Utilities
- Reynolds number calculation
- Prandtl number calculation
- Peclet number calculation
- Nusselt number calculation
- Permeability calculation for porous media
- Convergence checking utilities
- Vorticity and heat flux calculations

#### Visualization
- 2D velocity slice plotting
- 2D temperature slice plotting
- Velocity vector field plotting
- 3D geometry visualization
- Convergence history plotting
- VTK export for ParaView
- HDF5 data export

#### Examples
- Lid-driven cavity flow (validation)
- Poiseuille channel flow (validation)
- Heated channel flow (validation)
- Flow through gyroid structure
- Conjugate heat transfer in gyroid

#### Testing
- Unit tests for lattice module
- Unit tests for MRT collision
- Unit tests for Shan-Chen forcing
- Unit tests for geometry generation
- Test runner script

#### Documentation
- Comprehensive README with theory and usage
- Installation guide (INSTALL.md)
- Contributing guidelines (CONTRIBUTING.md)
- Configuration file with all parameters
- Docstrings for all modules and functions

#### Build and Distribution
- setup.py for package installation
- requirements.txt with all dependencies
- YAML configuration file support
- Package structure following best practices

### Features for High Reynolds/Nusselt Numbers
- MRT collision for stability at high Re (>1000)
- Enhanced forcing schemes (Guo and EDM)
- Thermal MRT for high Nu (>100)
- Different relaxation times for different moments

### Validation
- Poiseuille flow: analytical comparison
- Cavity flow: benchmark solutions
- Mass conservation: numerically verified
- Thermal profiles: analytical validation

## [Future Releases]

### Planned for v1.1.0
- [ ] Numba JIT compilation for performance
- [ ] Multi-threading support
- [ ] Additional validation cases
- [ ] Jupyter notebook tutorials
- [ ] Improved error handling

### Planned for v1.2.0
- [ ] GPU acceleration (CUDA)
- [ ] MPI parallelization
- [ ] Advanced turbulence models (LES)
- [ ] Particle tracking
- [ ] Porous media extensions

### Under Consideration
- [ ] Adaptive mesh refinement
- [ ] Non-Newtonian fluids
- [ ] Multi-phase flows
- [ ] Chemical reactions
- [ ] Fluid-structure interaction

---

[1.0.0]: https://github.com/RGoharimehr/lbm-test-cht/releases/tag/v1.0.0
