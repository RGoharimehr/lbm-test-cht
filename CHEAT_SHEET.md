# LBM-CHT Command Cheat Sheet

## Installation & Setup

```bash
# Install dependencies
pip install numpy scipy matplotlib pyyaml

# Verify installation
python verify_install.py

# Run tests
python tests/run_tests.py
```

## Quick Start

```bash
# Your first simulation (1 minute)
python quick_start.py

# Simple channel flow (1-2 minutes)  
python examples/channel_flow.py

# Heated channel (2-3 minutes)
python examples/heated_channel.py

# Full gyroid CHT (5-10 minutes)
python examples/gyroid_cht.py
```

## Common Code Snippets

### Basic Flow Simulation

```python
from src.flow_solver import FlowSolver
import numpy as np

# Create solver
solver = FlowSolver(32, 32, 32, viscosity=0.01)

# Add driving force
force = np.zeros((32, 32, 32, 3))
force[:, :, :, 0] = 0.0001
solver.set_external_force(force)

# Run
solver.initialize()
solver.run(n_steps=1000)
```

### Generate Gyroid

```python
from src.geometry import GyroidGenerator

geom = GyroidGenerator(64, 64, 64)
gyroid = geom.generate_gyroid(threshold=0.0, scale=2.0)
porosity = geom.calculate_porosity(gyroid)
```

### Conjugate Heat Transfer

```python
from src.conjugate_ht import ConjugateHTSolver

solver = ConjugateHTSolver(64, 64, 64,
                           viscosity=0.01,
                           alpha_fluid=0.01,
                           alpha_solid=0.001,
                           k_ratio=10.0)
                           
solver.set_geometry(solid_mask)
solver.initialize()
solver.run(n_steps=5000)
```

### Calculate Dimensionless Numbers

```python
from src.utils import (calculate_reynolds_number,
                      calculate_nusselt_number)

Re = calculate_reynolds_number(U, L, viscosity)
Nu = calculate_nusselt_number(q, dT, L, k)
```

### Visualize Results

```python
from src.visualization import (plot_velocity_slice,
                               plot_temperature_slice)

plot_velocity_slice(velocity, z_slice=32,
                   filename='velocity.png')
                   
plot_temperature_slice(temperature, z_slice=32,
                      filename='temperature.png')
```

## Typical Parameters

```python
# Small domain (fast, for testing)
nx, ny, nz = 32, 32, 32
n_steps = 1000

# Medium domain (good balance)
nx, ny, nz = 64, 64, 64
n_steps = 5000

# Large domain (detailed, slow)
nx, ny, nz = 128, 128, 128
n_steps = 10000

# Viscosity (higher = more stable)
viscosity = 0.01  # Standard
viscosity = 0.001  # Low (high Re)
viscosity = 0.1   # High (low Re)

# Reynolds number
Re = U * L / viscosity
# Typical: Re = 10-100 (laminar)
#          Re = 100-1000 (transitional)
#          Re > 1000 (turbulent-like, needs MRT)
```

## File Locations

```
Quick Reference:     HOW_TO_USE.txt, GETTING_STARTED.md
Examples:            examples/*.py
Core Code:           src/*.py
Tests:               tests/*.py
Configuration:       config/simulation_config.yaml
Documentation:       README.md, USER_GUIDE.md, INSTALL.md
```

## Troubleshooting Quick Fixes

```bash
# Missing modules
pip install numpy scipy matplotlib pyyaml

# Simulation diverges - reduce parameters
# In your code, try:
viscosity *= 2      # Double viscosity
force *= 0.1        # Reduce force
n_steps = 1000      # Shorter run first

# Memory issues - reduce domain
nx = ny = nz = 32   # Start small
```

## Output Locations

```
Results:             output/
Plots:               output/*/*.png
Data files:          output/*/*.h5, output/*/*.vti
```

## Documentation Quick Access

```bash
cat HOW_TO_USE.txt           # Quick commands
cat GETTING_STARTED.md       # 5-min tutorial
less USER_GUIDE.md           # Detailed guide
less README.md               # Full docs
```

## Key Modules

```python
# Import commonly used modules
from src.lattice import lattice_d3q19
from src.flow_solver import FlowSolver
from src.thermal_solver import ThermalSolver
from src.conjugate_ht import ConjugateHTSolver
from src.geometry import GyroidGenerator, generate_gyroid
from src.utils import (calculate_reynolds_number,
                      create_output_directory)
from src.visualization import plot_velocity_slice
```

## Getting Help

1. Check GETTING_STARTED.md
2. Read error message carefully
3. Try smaller domain first
4. Look at examples/
5. Read USER_GUIDE.md
6. Open GitHub issue

## Quick Tests

```bash
# One-liner test
python -c "from src.lattice import lattice_d3q19; print('Works!')"

# Full verification
python verify_install.py

# Unit tests
python tests/run_tests.py
```
