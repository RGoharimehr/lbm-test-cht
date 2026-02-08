# Usage Guide - LBM CHT

This guide provides detailed instructions for using the LBM CHT package.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Geometry Types](#geometry-types)
4. [Material Properties](#material-properties)
5. [Running Simulations](#running-simulations)
6. [Visualization](#visualization)
7. [Advanced Topics](#advanced-topics)

## Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Step-by-step Installation

```bash
# Clone the repository
git clone https://github.com/RGoharimehr/lbm-test-cht.git
cd lbm-test-cht

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Basic Usage

### Creating a Simple Simulation

```python
from lbm_cht import ChannelGeometry, LBMSolver, Visualizer
from lbm_cht.materials import CommonMaterials

# 1. Create geometry
geometry = ChannelGeometry(nx=50, ny=30, nz=30)

# 2. Define materials
fluid = CommonMaterials.water(temperature=300)
solid = CommonMaterials.aluminum()

# 3. Create solver
solver = LBMSolver(geometry, fluid, solid, dx=0.001, dt=1e-5)

# 4. Set initial conditions
solver.T[:5, :, :] = 350.0  # Hot inlet

# 5. Run simulation
solver.run(num_steps=1000)

# 6. Visualize results
visualizer = Visualizer(geometry, solver)
fig = visualizer.plot_temperature_slice()
```

## Geometry Types

### 1. Channel Geometry

Simple rectangular channel for basic flow studies.

```python
from lbm_cht import ChannelGeometry

geometry = ChannelGeometry(
    nx=50,                      # Grid size in x
    ny=30,                      # Grid size in y
    nz=30,                      # Grid size in z
    channel_height_ratio=0.5,   # Channel height as fraction of ny
    channel_width_ratio=0.5,    # Channel width as fraction of nz
    dx=0.001                    # Lattice spacing in meters
)
```

**Applications:** Simple heat exchangers, parallel plate flow, basic conjugate heat transfer studies

### 2. Duct Geometry

Rectangular duct with solid walls.

```python
from lbm_cht import DuctGeometry

geometry = DuctGeometry(
    nx=50,
    ny=30,
    nz=30,
    wall_thickness=2,  # Wall thickness in lattice units
    dx=0.001
)
```

**Applications:** HVAC ducts, enclosed flow channels, pipe flow studies

### 3. Skived Fins

Parallel plate fins for enhanced heat transfer.

```python
from lbm_cht import SkivedFinsGeometry

geometry = SkivedFinsGeometry(
    nx=50,
    ny=30,
    nz=30,
    num_fins=10,         # Number of fins
    fin_thickness=2,     # Thickness of each fin in lattice units
    dx=0.001
)
```

**Applications:** Heat sinks, CPU coolers, compact heat exchangers

### 4. Kelvin Cells

Periodic cellular structure for lattice materials.

```python
from lbm_cht import KelvinCellsGeometry

geometry = KelvinCellsGeometry(
    nx=60,
    ny=60,
    nz=60,
    cell_size=10,        # Size of unit cell
    strut_thickness=2,   # Thickness of struts
    dx=0.001
)
```

**Applications:** Porous media, lattice structures, 3D printed heat exchangers, foam materials

### 5. Pin Fins

Array of cylindrical pins for heat transfer enhancement.

```python
from lbm_cht import PinFinsGeometry

geometry = PinFinsGeometry(
    nx=60,
    ny=40,
    nz=40,
    num_pins_y=5,      # Number of pins in y direction
    num_pins_z=5,      # Number of pins in z direction
    pin_diameter=4,    # Diameter of pins in lattice units
    dx=0.001
)
```

**Applications:** Heat sinks with pin fins, tube banks, compact heat exchangers

### Geometry Properties

All geometries provide the following properties:

```python
# Get porosity (fluid volume fraction)
porosity = geometry.get_porosity()

# Get surface area
surface_area = geometry.get_surface_area()

# Get volumes
total_volume = geometry.get_volume()
fluid_volume = geometry.get_fluid_volume()
solid_volume = geometry.get_solid_volume()

# Get masks
fluid_mask = geometry.get_fluid_mask()
solid_mask = geometry.get_solid_mask()
```

## Material Properties

### Built-in Materials

```python
from lbm_cht.materials import CommonMaterials

# Fluids
water = CommonMaterials.water(temperature=300)
air = CommonMaterials.air(temperature=300)

# Solids
copper = CommonMaterials.copper()
aluminum = CommonMaterials.aluminum()
steel = CommonMaterials.steel()
```

### CoolProp Materials

CoolProp provides access to hundreds of fluids with accurate thermophysical properties.

```python
from lbm_cht.materials import CoolPropMaterial

# Create material from CoolProp database
fluid = CoolPropMaterial(
    fluid_name='Water',
    temperature=300,    # Kelvin
    pressure=101325     # Pascal
)

# Update properties for new conditions
fluid.update_temperature(350)
fluid.update_pressure(200000)

# Get available fluids
fluids = CoolPropMaterial.list_available_fluids()
print(f"Available fluids: {len(fluids)}")
```

**Common CoolProp fluids:**
- Water, Air, Nitrogen, Oxygen, CO2
- Refrigerants: R134a, R410A, R32, R1234yf
- Hydrocarbons: Methane, Ethane, Propane, Butane
- And many more...

### Custom Materials

```python
from lbm_cht import Material

custom_fluid = Material(
    name="Glycol Mix",
    density=1050,                    # kg/m³
    thermal_conductivity=0.5,        # W/m·K
    specific_heat=3500,              # J/kg·K
    viscosity=0.002,                 # Pa·s
    is_solid=False
)

custom_solid = Material(
    name="Carbon Fiber",
    density=1600,
    thermal_conductivity=150,
    specific_heat=710,
    viscosity=None,
    is_solid=True
)
```

### Material Properties

```python
# Thermal diffusivity
alpha = material.get_thermal_diffusivity()  # m²/s

# For fluids only:
nu = material.get_kinematic_viscosity()     # m²/s
Pr = material.get_prandtl_number()          # Dimensionless
```

## Running Simulations

### Basic Simulation

```python
from lbm_cht import LBMSolver

solver = LBMSolver(
    geometry=geometry,
    fluid_material=fluid,
    solid_material=solid,
    dx=0.001,  # Lattice spacing (m)
    dt=1e-5    # Time step (s)
)

# Run for fixed number of steps
solver.run(num_steps=1000)
```

### Simulation with Callback

```python
def progress_callback(step, solver):
    """Called after each time step"""
    if step % 100 == 0:
        T = solver.get_temperature()
        T_max = T.max()
        T_min = T.min()
        print(f"Step {step}: T_max={T_max:.2f}K, T_min={T_min:.2f}K")

solver.run(num_steps=1000, callback=progress_callback)
```

### Setting Initial Conditions

```python
# Set temperature field
solver.T[:5, :, :] = 350.0      # Hot inlet
solver.T[-5:, :, :] = 300.0     # Cold outlet

# Set velocity field (if needed)
solver.u[0, :, :, :] = 0.01     # x-velocity

# Reinitialize distributions
solver.initialize_distributions()
```

### Extracting Results

```python
# Get fields
temperature = solver.get_temperature()
velocity = solver.get_velocity()
density = solver.get_density()

# Get specific values
T_center = temperature[nx//2, ny//2, nz//2]
u_max = np.max(np.sqrt(velocity[0]**2 + velocity[1]**2 + velocity[2]**2))
```

## Visualization

### 2D Slice Visualizations

```python
from lbm_cht import Visualizer

visualizer = Visualizer(geometry, solver)

# Geometry slice
fig1 = visualizer.plot_geometry_slice(axis='z', position=15)

# Temperature slice
fig2 = visualizer.plot_temperature_slice(
    axis='z',
    position=15,
    vmin=300,  # Minimum temperature
    vmax=350   # Maximum temperature
)

# Velocity slice with arrows
fig3 = visualizer.plot_velocity_slice(
    axis='z',
    position=15,
    scale=10,   # Arrow scale
    skip=2      # Show every 2nd arrow
)
```

### 3D Visualizations

```python
# 3D geometry
fig4 = visualizer.plot_3d_geometry(opacity=0.3)

# 3D temperature (hot regions only)
fig5 = visualizer.plot_3d_temperature(threshold_percentile=90)
```

### PyVista (Advanced 3D)

```python
# Create PyVista mesh
grid = visualizer.create_pyvista_mesh()

# Interactive visualization
grid.plot(scalars='temperature')

# Save to VTK
visualizer.save_vtk('output.vts')
```

You can then open the VTK file in ParaView for advanced visualization.

### Saving Figures

```python
import matplotlib.pyplot as plt

fig = visualizer.plot_temperature_slice()
plt.savefig('temperature.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Advanced Topics

### Choosing Time Step and Grid Size

For numerical stability, the LBM requires:

```python
# Mach number constraint: Ma < 0.1
u_physical = 1.0  # m/s (maximum velocity)
Ma = u_physical * dt / dx  # Should be < 0.1

# Adjust dt accordingly
dt = 0.1 * dx / u_physical

# Diffusive stability: dt < dx² / (2α)
alpha = material.get_thermal_diffusivity()
dt_max = dx**2 / (2 * alpha)
```

### Non-dimensional Numbers

```python
# Reynolds number
Re = u_physical * L / fluid.get_kinematic_viscosity()

# Prandtl number
Pr = fluid.get_prandtl_number()

# Peclet number
Pe = Re * Pr
```

### Convergence Monitoring

```python
def check_convergence(step, solver):
    if step % 100 == 0:
        T = solver.get_temperature()
        # Check temperature change
        if step > 0:
            dT = np.abs(T - T_prev).max()
            if dT < 1e-6:
                print(f"Converged at step {step}")
                return True
        T_prev = T.copy()
    return False
```

### Performance Optimization

```python
# Use smaller domains for testing
geometry = ChannelGeometry(nx=30, ny=20, nz=20)  # Smaller grid

# Use fewer time steps initially
solver.run(num_steps=100)  # Quick test

# Monitor performance
import time
start = time.time()
solver.run(num_steps=1000)
print(f"Time: {time.time() - start:.2f}s")
```

## Troubleshooting

### Common Issues

1. **ImportError: CoolProp not available**
   ```bash
   pip install CoolProp
   ```

2. **Memory error for large grids**
   - Reduce grid size: nx, ny, nz
   - Use float32 instead of float64 (modify source)

3. **Simulation unstable (NaN values)**
   - Reduce time step dt
   - Check Mach number constraint
   - Verify initial conditions

4. **Slow simulation**
   - Reduce grid size
   - Use fewer time steps
   - Consider GPU acceleration (future work)

## Examples

See the `examples/` directory for complete working examples:

- `example1_channel.py` - Channel with water flow
- `example2_pin_fins_coolprop.py` - Pin fins with CoolProp
- `example3_geometry_comparison.py` - Compare all geometries

## Further Reading

- Lattice Boltzmann Method theory
- Conjugate heat transfer
- Heat exchanger design
- Computational fluid dynamics

## Support

For questions and issues, please open an issue on GitHub:
https://github.com/RGoharimehr/lbm-test-cht/issues
