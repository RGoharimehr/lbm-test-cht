"""
Materials module for LBM CHT
Defines material properties using CoolProp and custom definitions
"""

from .material import Material
from .coolprop_material import CoolPropMaterial

__all__ = ["Material", "CoolPropMaterial"]
