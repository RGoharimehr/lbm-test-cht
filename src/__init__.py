"""
LBM-CHT: 3D Lattice Boltzmann Method for Conjugate Heat Transfer in Gyroid Structures

This package provides a complete implementation of the Lattice Boltzmann Method (LBM)
with Multiple Relaxation Time (MRT) collision and modified Shan-Chen forcing for
simulating conjugate heat transfer in complex geometries.
"""

__version__ = "1.0.0"
__author__ = "LBM-CHT Team"

from . import lattice
from . import mrt
from . import shan_chen
from . import flow_solver
from . import thermal_solver
from . import conjugate_ht
from . import geometry
from . import boundary_conditions
from . import utils
from . import visualization

__all__ = [
    'lattice',
    'mrt',
    'shan_chen',
    'flow_solver',
    'thermal_solver',
    'conjugate_ht',
    'geometry',
    'boundary_conditions',
    'utils',
    'visualization'
]
