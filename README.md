# LBM Conjugate Heat Transfer - 3D Lattice Boltzmann Method for Various Geometries

A Python package for simulating conjugate heat transfer (CHT) using the Lattice Boltzmann Method (LBM) in various geometries including channels, ducts, skived fins, Kelvin cells, and pin fins.

## Features

- **Multiple Geometries Support:**
  - Simple rectangular channels
  - Ducts with walls
  - Skived fins (parallel plate fins)
  - Kelvin cells (periodic cellular structures)
  - Pin fins (cylindrical pins)

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

### Example 1: Channel with Water Flow

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

### Example 2: Pin Fins with CoolProp

```python
from lbm_cht import PinFinsGeometry, Visualizer
from lbm_cht.materials import CoolPropMaterial, CommonMaterials

# Create pin fins geometry
geometry = PinFinsGeometry(nx=60, ny=40, nz=40,
                          num_pins_y=4, num_pins_z=4,
                          pin_diameter=6)

# Use CoolProp for fluid properties
fluid = CoolPropMaterial('R134a', temperature=300)
solid = CommonMaterials.copper()

# Visualize geometry
visualizer = Visualizer(geometry)
fig = visualizer.plot_3d_geometry()
```

## Examples

Run the included examples to see the package in action:

```bash
# Example 1: Channel geometry with water flow
python examples/example1_channel.py

# Example 2: Pin fins with CoolProp material
python examples/example2_pin_fins_coolprop.py

# Example 3: Compare all geometries
python examples/example3_geometry_comparison.py
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

### 3. Skived Fins
Parallel plate fins for enhanced heat transfer.

```python
SkivedFinsGeometry(nx=50, ny=30, nz=30,
                  num_fins=10, fin_thickness=2)
```

### 4. Kelvin Cells
Periodic cellular structure based on tetrakaidecahedron.

```python
KelvinCellsGeometry(nx=50, ny=30, nz=30,
                   cell_size=10, strut_thickness=2)
```

### 5. Pin Fins
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