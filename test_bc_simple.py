"""
Simple test of boundary condition methods
"""

import numpy as np
from lbm_cht.geometries import ChannelGeometry
from lbm_cht.materials import Material
from lbm_cht.lbm import LBMSolver

# Create a simple channel
print("Creating channel geometry...")
geometry = ChannelGeometry(nx=40, ny=20, nz=10, dx=0.001)

# Materials
fluid = Material(
    name="Water",
    density=1000,
    specific_heat=4186.0,
    thermal_conductivity=0.6,
    viscosity=0.001
)

solid = Material(
    name="Steel",
    density=7800,
    specific_heat=500.0,
    thermal_conductivity=50.0,
    is_solid=True
)

# Test simple method
print("\n" + "="*60)
print("Testing Simple Bounce-Back")
print("="*60)

solver = LBMSolver(
    geometry, fluid, solid,
    dx=0.001, dt=None,
    boundary_method='simple'
)

solver.set_inlet_temperature(330.0)
solver.set_outlet_temperature(300.0)
solver.set_inlet_velocity(0.01)

print("\nRunning 100 steps...")
solver.run(num_steps=100, print_interval=50)
print(f"Final max velocity: {np.max(np.sqrt(solver.u[0]**2 + solver.u[1]**2 + solver.u[2]**2)):.6f} m/s")
print(f"Final mean temperature: {np.mean(solver.T[solver.fluid_mask]):.2f} K")

# Test Bouzidi method
print("\n" + "="*60)
print("Testing Bouzidi Interpolated")
print("="*60)

solver2 = LBMSolver(
    geometry, fluid, solid,
    dx=0.001, dt=None,
    boundary_method='bouzidi'
)

solver2.set_inlet_temperature(330.0)
solver2.set_outlet_temperature(300.0)
solver2.set_inlet_velocity(0.01)

print("\nRunning 100 steps...")
solver2.run(num_steps=100, print_interval=50)
print(f"Final max velocity: {np.max(np.sqrt(solver2.u[0]**2 + solver2.u[1]**2 + solver2.u[2]**2)):.6f} m/s")
print(f"Final mean temperature: {np.mean(solver2.T[solver2.fluid_mask]):.2f} K")

print("\n" + "="*60)
print("Both methods completed successfully!")
print("="*60)
