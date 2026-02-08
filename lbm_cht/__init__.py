"""
LBM CHT - Lattice Boltzmann Method for Conjugate Heat Transfer
A Python package for simulating heat transfer in various geometries
"""

__version__ = "0.1.0"

from .geometries import (
    BaseGeometry,
    ChannelGeometry,
    DuctGeometry,
    SkivedFinsGeometry,
    KelvinCellsGeometry,
    PinFinsGeometry,
    PipeGeometry,
)
from .materials import Material, CoolPropMaterial
from .lbm import LBMSolver
from .visualization import Visualizer

__all__ = [
    "BaseGeometry",
    "ChannelGeometry",
    "DuctGeometry",
    "SkivedFinsGeometry",
    "KelvinCellsGeometry",
    "PinFinsGeometry",
    "PipeGeometry",
    "Material",
    "CoolPropMaterial",
    "LBMSolver",
    "Visualizer",
]
