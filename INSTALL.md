# Installation Guide

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.7 or higher
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 500MB for code + space for output data

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/RGoharimehr/lbm-test-cht.git
cd lbm-test-cht
```

### 2. Create Virtual Environment (Recommended)

Using venv:
```bash
python -m venv lbm_env
source lbm_env/bin/activate  # On Windows: lbm_env\Scripts\activate
```

Using conda:
```bash
conda create -n lbm_env python=3.9
conda activate lbm_env
```

### 3. Install Dependencies

Basic installation:
```bash
pip install -r requirements.txt
```

Development installation:
```bash
pip install -e ".[dev]"
```

With all optional features:
```bash
pip install -e ".[dev,viz,performance]"
```

### 4. Verify Installation

Run tests:
```bash
python tests/run_tests.py
```

Or using pytest:
```bash
pytest tests/
```

Run a simple example:
```bash
python examples/channel_flow.py
```

## Troubleshooting

### Issue: NumPy/SciPy Installation Fails

**Solution**: Install using conda instead:
```bash
conda install numpy scipy matplotlib
pip install pyyaml h5py
```

### Issue: VTK Import Error

VTK is optional. If you don't need VTK export:
- Comment out VTK imports in `src/utils.py`
- Or install VTK separately: `pip install vtk`

### Issue: Memory Error on Large Domains

**Solution**: 
- Reduce domain size (nx, ny, nz)
- Use smaller time steps
- Enable memory optimization in config

### Issue: Slow Performance

**Solutions**:
1. Install Numba: `pip install numba`
2. Reduce domain size for testing
3. Use fewer output intervals
4. Consider running on HPC cluster

## Platform-Specific Notes

### Linux
Works out of the box with pip installation.

### macOS
May need to install Xcode command line tools:
```bash
xcode-select --install
```

### Windows
- Use Anaconda for easier installation
- Or install Visual C++ Build Tools if using pip

## Optional Dependencies

### For Visualization
```bash
pip install vtk pyvista
```

### For Performance
```bash
pip install numba
```

### For Jupyter Notebooks
```bash
pip install jupyter
```

## Verifying Your Installation

Run this Python script to check all components:

```python
import sys
import importlib

required = ['numpy', 'scipy', 'matplotlib', 'yaml', 'h5py']
optional = ['numba', 'vtk', 'pytest']

print("Checking required packages:")
for pkg in required:
    try:
        importlib.import_module(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} - MISSING!")

print("\nChecking optional packages:")
for pkg in optional:
    try:
        importlib.import_module(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ○ {pkg} - not installed (optional)")

print("\nChecking LBM-CHT modules:")
sys.path.insert(0, 'src')
lbm_modules = ['lattice', 'mrt', 'flow_solver', 'geometry']
for mod in lbm_modules:
    try:
        importlib.import_module(mod)
        print(f"  ✓ {mod}")
    except ImportError as e:
        print(f"  ✗ {mod} - ERROR: {e}")
```

## Next Steps

After successful installation:

1. Read the [Quick Start](README.md#quick-start) guide
2. Run validation examples in `examples/`
3. Explore the configuration options in `config/simulation_config.yaml`
4. Try modifying parameters for your specific case

## Getting Help

- Check the [README](README.md) for documentation
- Open an issue on GitHub for bugs
- Consult the examples for usage patterns
