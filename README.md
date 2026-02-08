# LBM Conjugate Heat Transfer - 3D Lattice Boltzmann Method for Various Geometries

A Python package for simulating conjugate heat transfer (CHT) using the Lattice Boltzmann Method (LBM) in various geometries including channels, ducts, skived fins, Kelvin cells, and pin fins.

## ⚠️ Latest Updates ✅

### Advanced Boundary Condition Methods (NEW!)

**Curved boundary treatment methods adapted from https://github.com/siramirsaman/LBM:**

- ✅ **Bouzidi Interpolated BC** - Sub-grid accuracy for curved boundaries
- ✅ **Yu Interpolated BC** - For moving/rotating walls
- ✅ **Filippova Interpolated BC** - Alternative interpolation scheme
- ✅ **Smooth cylinder surfaces** - No stair-stepping on pin fins
- ✅ **Method selection** - Choose best BC for your geometry

**See [BOUNDARY_METHODS.md](BOUNDARY_METHODS.md) for complete guide!**

```python
# Use advanced boundary method for curved geometries
solver = LBMSolver(
    geometry, fluid, solid,
    boundary_method='bouzidi'  # 'simple', 'bouzidi', 'yu', 'filippova'
)
```

### Critical Stability Fixes

**The LBM solver has been significantly improved with critical stability fixes:**

- ✅ **Boundary layers now clearly visible!** (velocity & temperature)
- ✅ **Numerical stability ensured** - no more divergence
- ✅ **Smooth contours** - no jagged edges  
- ✅ **Auto time step calculation** for optimal stability
- ✅ **Runtime monitoring** - detects NaN/Inf automatically

**See [STABILITY_FIX_SUMMARY.md](STABILITY_FIX_SUMMARY.md) for complete details!**

### Quick Example with Stable Solver:

```python
from lbm_cht import ChannelGeometry, Material, LBMSolver

# Create geometry
geometry = ChannelGeometry(nx=80, ny=30, nz=20, dx=0.001)

# Create materials  
fluid = Material("Water", density=1000, viscosity=0.001, 
                 thermal_conductivity=0.6, specific_heat=4200)
solid = Material("Aluminum", density=2700, viscosity=0.001,
                 thermal_conductivity=200, specific_heat=900)

# Create solver with AUTO time step (recommended!)
solver = LBMSolver(geometry, fluid, solid, dt=None)  # dt=None → auto-calculate!

# Set boundary conditions (enforced every timestep)
solver.set_inlet_temperature(330.0)
solver.set_outlet_temperature(300.0)
solver.set_inlet_velocity(0.01)  # 10 mm/s

# Run simulation
solver.run(num_steps=1000, print_interval=200)

# Results show clear boundary layers!
T = solver.get_temperature()
u = solver.get_velocity()
```

**Results:** Clear boundary layer development with 2.6× velocity ratio (center/wall) and 14.4K thermal gradient!

## Features

- **Multiple Geometries Support:**
  - Simple rectangular channels
  - Ducts with walls
  - Circular pipes (for thermal entry length studies) ⭐ **NEW!**
  - Skived fins (parallel plate fins)
  - Kelvin cells (periodic cellular structures)
  - Pin fins (cylindrical pins)

- **Smooth Boundary Representation:** ⭐
  - Sub-voxel accuracy for curved surfaces
  - Eliminates jagged stair-step boundaries
  - Multi-point sampling for accurate solid fraction calculation
  - Improved surface area and boundary representation

- **Resolution Validation:** ⭐
  - Automatic warnings for insufficient resolution
  - Geometry-specific resolution requirements
  - Quality metrics (porosity, surface area, resolution ratio)

- **Numerical Stability:** ⭐ **NEW!**
  - Auto time step calculation (dt=None recommended)
  - Relaxation parameter validation (τ > 0.6 for stability)
  - Runtime NaN/Inf detection
  - Mach number monitoring
  - Progress tracking with velocity/temperature diagnostics

- **Boundary Conditions Management:** ⭐
  - Configurable wall thickness in lattice units
  - Explicit inlet/outlet region specification
  - BCs enforced every timestep (not just initialization)
  - Helper methods for setting boundary conditions
  - Automatic validation and warnings
  - See [BOUNDARY_CONDITIONS.md](BOUNDARY_CONDITIONS.md) for details

- **Material Properties:**
  - Built-in common materials (Water, Air, Copper, Aluminum, Steel)
  - CoolProp integration for extensive fluid property database
  - Custom material definitions

- **Advanced Visualization:**
  - 2D slice visualizations (geometry, temperature, velocity)
  - 3D visualizations with matplotlib
  - PyVista support for advanced 3D rendering
  - VTK export for ParaView visualization

- **LBM Solver:**
  - D3Q19 lattice for 3D simulations
  - Conjugate heat transfer coupling
  - BGK collision operator
  - Bounce-back boundary conditions
  - Zou-He velocity boundary conditions

## Installation

```bash
# Clone the repository
git clone https://github.com/RGoharimehr/lbm-test-cht.git
cd lbm-test-cht

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

### Example 1: Pin Fins with Smooth Boundaries

```python
from lbm_cht import PinFinsGeometry, Visualizer
from lbm_cht.materials import CommonMaterials

# Create pin fins geometry with smooth boundaries (default)
geometry = PinFinsGeometry(
    nx=60, ny=40, nz=40,
    num_pins_y=4, num_pins_z=4,
    pin_diameter=8,  # 8 cells per diameter for smooth representation
    use_smooth_boundary=True  # Enable sub-voxel accuracy
)

# Check geometry quality
metrics = geometry.compute_geometry_quality_metrics()
print(f"Porosity: {metrics['porosity']:.3f}")
print(f"Has smooth boundary: {metrics['has_smooth_boundary']}")
print(f"Resolution ratio: {metrics['resolution_ratio']:.1f}")

# Visualize the smooth solid fraction field
visualizer = Visualizer(geometry)
fig = visualizer.plot_geometry_slice()
```

### Example 2: Channel with Water Flow

```python
from lbm_cht import ChannelGeometry, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials

# Create geometry
geometry = ChannelGeometry(nx=50, ny=30, nz=30, 
                          channel_height_ratio=0.6)

# Define materials
fluid = CommonMaterials.water(temperature=300)
solid = CommonMaterials.aluminum()

# Create solver
solver = LBMSolver(geometry, fluid, solid)

# Run simulation
solver.run(num_steps=1000)

# Visualize results
visualizer = Visualizer(geometry, solver)
fig = visualizer.plot_temperature_slice()
```

### Example 3: Kelvin Cells with CoolProp

```python
from lbm_cht import KelvinCellsGeometry, Visualizer
from lbm_cht.materials import CoolPropMaterial, CommonMaterials

# Create Kelvin cells with smooth struts
geometry = KelvinCellsGeometry(
    nx=60, ny=60, nz=60,
    cell_size=15,
    strut_thickness=5,
    use_smooth_boundary=True  # Smooth cylindrical struts
)

# Use CoolProp for fluid properties
fluid = CoolPropMaterial('R134a', temperature=300)
solid = CommonMaterials.copper()

# Visualize geometry
visualizer = Visualizer(geometry)
fig = visualizer.plot_3d_geometry()
```

## Resolution Guidelines ⭐ NEW!

Proper resolution is critical for accurate LBM simulations. The package now includes:

- **Automatic validation** with warnings for insufficient resolution
- **Smooth boundary support** for sub-voxel accuracy on curved surfaces
- **Quality metrics** to assess geometry adequacy

### Recommended Resolutions

| Geometry | Feature | Minimum | Recommended |
|----------|---------|---------|-------------|
| **Pin Fins** | Diameter | 6 cells | 8-12 cells |
| **Kelvin Cells** | Strut thickness | 4 cells | 5-6 cells |
| **Channels** | Height/Width | 10 cells | 20-40 cells |

See [RESOLUTION_GUIDE.md](RESOLUTION_GUIDE.md) for comprehensive guidelines.

## Smooth Boundaries ⭐ NEW!

Smooth boundaries eliminate jagged stair-step artifacts on curved surfaces:

```python
# Traditional binary representation (jagged)
geom_binary = PinFinsGeometry(nx=40, ny=30, nz=30, pin_diameter=6,
                              use_smooth_boundary=False)

# Smooth sub-voxel representation (recommended)
geom_smooth = PinFinsGeometry(nx=40, ny=30, nz=30, pin_diameter=6,
                              use_smooth_boundary=True)

# Check if geometry uses smooth boundaries
print(f"Has smooth boundaries: {geom_smooth.has_smooth_boundary()}")

# Access solid fraction field (0-1 continuous values)
solid_fraction = geom_smooth.get_solid_fraction()
```

**Benefits:**
- ✅ Eliminates jagged boundaries
- ✅ Improves surface area accuracy
- ✅ Better flow physics near walls
- ✅ Smoother convergence

## Examples

Run the included examples to see the package in action:

```bash
# Example 1: Channel geometry with forced convection
python examples/example1_channel.py

# Example 2: Pin fins with forced convection cooling
python examples/example2_pin_fins_coolprop.py

# Example 3: Compare all geometries
python examples/example3_geometry_comparison.py

# Example 4: Resolution comparison
python examples/example4_resolution_comparison.py

# Example 5: Boundary conditions configuration
python examples/example5_boundary_conditions.py

# Example 6: Velocity comparison (forced convection effects)
python examples/example6_velocity_comparison.py

# Example 7: Thermal entry length in circular pipe ⭐ NEW!
python examples/example7_pipe_thermal_entry.py

# Example 8: Pipe thermal boundary layer (simplified demo) ⭐ NEW!
python examples/example8_pipe_boundary_layer.py
```

## Available Geometries

### 1. Channel Geometry
Simple rectangular channel for basic flow studies.

```python
ChannelGeometry(nx=50, ny=30, nz=30, 
               channel_height_ratio=0.5,
               channel_width_ratio=0.5)
```

### 2. Duct Geometry
Rectangular duct with solid walls.

```python
DuctGeometry(nx=50, ny=30, nz=30, wall_thickness=2)
```

### 3. Circular Pipe ⭐ **NEW!**
Circular pipe for thermal entry length and boundary layer studies.

```python
PipeGeometry(nx=100, ny=30, nz=30,
            inner_diameter_ratio=0.7,  # 70% of cross-section
            wall_thickness=3,
            use_smooth_boundary=True)  # Smooth circular walls
```

**Key features:**
- Smooth circular boundaries with sub-voxel accuracy
- Variable diameter and wall thickness
- Hydraulic diameter and cross-sectional area calculations
- Ideal for studying thermal boundary layer development
- Resolution validation (recommends 10-20 cells across diameter)

### 4. Skived Fins
Parallel plate fins for enhanced heat transfer.

```python
SkivedFinsGeometry(nx=50, ny=30, nz=30,
                  num_fins=10, fin_thickness=2)
```

### 5. Kelvin Cells
Periodic cellular structure based on tetrakaidecahedron.

```python
KelvinCellsGeometry(nx=50, ny=30, nz=30,
                   cell_size=10, strut_thickness=2)
```

### 6. Pin Fins
Array of cylindrical pins for heat transfer enhancement.

```python
PinFinsGeometry(nx=60, ny=40, nz=40,
               num_pins_y=5, num_pins_z=5,
               pin_diameter=4)
```

## Material Properties

### Built-in Materials

```python
from lbm_cht.materials import CommonMaterials

water = CommonMaterials.water(temperature=300)
air = CommonMaterials.air(temperature=300)
copper = CommonMaterials.copper()
aluminum = CommonMaterials.aluminum()
steel = CommonMaterials.steel()
```

### CoolProp Integration

```python
from lbm_cht.materials import CoolPropMaterial

# Access hundreds of fluids from CoolProp database
fluid = CoolPropMaterial('Water', temperature=300, pressure=101325)
refrigerant = CoolPropMaterial('R134a', temperature=280)
co2 = CoolPropMaterial('CO2', temperature=300)

# List available fluids
fluids = CoolPropMaterial.list_available_fluids()
```

### Custom Materials

```python
from lbm_cht import Material

custom_fluid = Material(
    name="Custom Fluid",
    density=1000,
    thermal_conductivity=0.6,
    specific_heat=4200,
    viscosity=0.001,
    is_solid=False
)
```

## Visualization Options

### 2D Slices

```python
visualizer = Visualizer(geometry, solver)

# Geometry slices
visualizer.plot_geometry_slice(axis='z', position=15)

# Temperature field
visualizer.plot_temperature_slice(axis='z', position=15)

# Velocity field with arrows
visualizer.plot_velocity_slice(axis='z', position=15)
```

### 3D Visualization

```python
# 3D geometry
visualizer.plot_3d_geometry(opacity=0.3)

# 3D temperature field
visualizer.plot_3d_temperature(threshold_percentile=90)
```

### VTK Export

```python
# Export to VTK for ParaView
visualizer.save_vtk('simulation_output.vts')
```

## Dependencies

- numpy >= 1.21.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0
- CoolProp >= 6.4.1
- pyvista >= 0.36.0 (optional, for advanced 3D visualization)
- numba >= 0.54.0 (optional, for performance)

## License

This project is open source and available under the MIT License.

## Author

Reza Goharimehr

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.