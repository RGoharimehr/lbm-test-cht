#!/usr/bin/env python
"""
LBM-CHT Installation Verification Script

Run this script to verify that LBM-CHT is properly installed and ready to use.
"""

import sys
import os

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_header("Checking Dependencies")
    
    required = {
        'numpy': 'NumPy',
        'scipy': 'SciPy', 
        'matplotlib': 'Matplotlib',
        'yaml': 'PyYAML'
    }
    
    optional = {
        'h5py': 'HDF5 support',
        'numba': 'Performance (JIT)',
        'vtk': 'VTK export'
    }
    
    all_ok = True
    
    print("\nRequired packages:")
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name:20s} - installed")
        except ImportError:
            print(f"  ✗ {name:20s} - MISSING!")
            all_ok = False
    
    print("\nOptional packages:")
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"  ✓ {name:20s} - installed")
        except ImportError:
            print(f"  ○ {name:20s} - not installed (optional)")
    
    return all_ok

def check_modules():
    """Check if LBM-CHT modules load correctly"""
    print_header("Checking LBM-CHT Modules")
    
    # Add src to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    modules = [
        ('src.lattice', 'D3Q19 Lattice'),
        ('src.mrt', 'MRT Collision'),
        ('src.shan_chen', 'Shan-Chen Forcing'),
        ('src.flow_solver', 'Flow Solver'),
        ('src.thermal_solver', 'Thermal Solver'),
        ('src.conjugate_ht', 'Conjugate HT Solver'),
        ('src.geometry', 'Geometry Generation'),
        ('src.boundary_conditions', 'Boundary Conditions'),
        ('src.utils', 'Utilities'),
        ('src.visualization', 'Visualization')
    ]
    
    all_ok = True
    
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {description:25s} ({module_name})")
        except Exception as e:
            print(f"  ✗ {description:25s} - ERROR: {e}")
            all_ok = False
    
    return all_ok

def run_basic_test():
    """Run a basic functionality test"""
    print_header("Running Basic Functionality Test")
    
    try:
        from src.lattice import lattice_d3q19
        from src.geometry import GyroidGenerator
        from src.flow_solver import FlowSolver
        import numpy as np
        
        print("\n  Testing lattice operations...")
        # Test lattice
        assert lattice_d3q19.Q == 19, "Lattice should have 19 velocities"
        assert np.abs(np.sum(lattice_d3q19.w) - 1.0) < 1e-10, "Weights should sum to 1"
        print("    ✓ Lattice OK")
        
        print("\n  Testing geometry generation...")
        # Test geometry
        geom = GyroidGenerator(16, 16, 16)
        solid_mask = geom.generate_channel(channel_height=12)
        assert solid_mask.shape == (16, 16, 16), "Geometry shape mismatch"
        porosity = geom.calculate_porosity(solid_mask)
        assert 0 < porosity < 1, "Porosity should be between 0 and 1"
        print(f"    ✓ Generated channel with porosity: {porosity:.2%}")
        
        print("\n  Testing flow solver...")
        # Test flow solver
        solver = FlowSolver(16, 16, 16, viscosity=0.01)
        solver.initialize()
        assert solver.f is not None, "Distribution function should be initialized"
        print(f"    ✓ Flow solver initialized")
        
        print("\n  Running mini simulation (100 steps)...")
        solver.run(n_steps=100)
        u_mag = solver.get_velocity_magnitude()
        print(f"    ✓ Simulation completed, max velocity: {u_mag.max():.6f}")
        
        return True
        
    except Exception as e:
        print(f"\n  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(deps_ok, modules_ok, test_ok):
    """Print final summary"""
    print_header("Verification Summary")
    
    print(f"\n  Dependencies:  {'✓ PASS' if deps_ok else '✗ FAIL'}")
    print(f"  Modules:       {'✓ PASS' if modules_ok else '✗ FAIL'}")
    print(f"  Functionality: {'✓ PASS' if test_ok else '✗ FAIL'}")
    
    print("\n" + "-"*70)
    
    if deps_ok and modules_ok and test_ok:
        print("""
  🎉 SUCCESS! LBM-CHT is properly installed and working!
  
  You can now:
  1. Run quick_start.py:           python quick_start.py
  2. Try examples:                 python examples/channel_flow.py
  3. Read getting started guide:   cat GETTING_STARTED.md
  4. Create your own simulations!
        """)
        return 0
    else:
        print("""
  ⚠️  ISSUES DETECTED
  
  Please fix the issues above and try again.
  
  Common solutions:
  - Install missing dependencies: pip install numpy scipy matplotlib pyyaml
  - Check you're in the correct directory
  - See INSTALL.md for detailed instructions
        """)
        return 1

def main():
    """Main verification function"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              LBM-CHT Installation Verification                        ║
║                                                                       ║
║  This script checks if LBM-CHT is properly installed and ready       ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n⚠️  Cannot continue - missing required dependencies")
        print("Install them with: pip install numpy scipy matplotlib pyyaml")
        return 1
    
    # Check modules
    modules_ok = check_modules()
    
    if not modules_ok:
        print("\n⚠️  Some modules failed to load")
        print_summary(deps_ok, modules_ok, False)
        return 1
    
    # Run basic test
    test_ok = run_basic_test()
    
    # Print summary
    return print_summary(deps_ok, modules_ok, test_ok)

if __name__ == "__main__":
    sys.exit(main())
