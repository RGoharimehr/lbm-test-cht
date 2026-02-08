"""
Duct geometry - rectangular or square duct
"""
import numpy as np
from .base_geometry import BaseGeometry


class DuctGeometry(BaseGeometry):
    """
    Rectangular duct geometry with walls.
    
    Creates a duct with specified wall thickness.
    """
    
    def __init__(self, nx, ny, nz, wall_thickness=2, dx=1.0):
        """
        Initialize duct geometry.
        
        Args:
            nx, ny, nz: Grid dimensions
            wall_thickness: Thickness of duct walls in lattice units
            dx: Lattice spacing
        """
        self.wall_thickness = wall_thickness
        super().__init__(nx, ny, nz, dx)
    
    def _build_geometry(self):
        """Build the duct geometry."""
        wt = self.wall_thickness
        
        # Set everything as fluid initially
        self.solid_mask[:, :, :] = False
        self.fluid_mask[:, :, :] = True
        
        # Create walls (solid regions)
        # Bottom wall
        self.solid_mask[:, :wt, :] = True
        self.fluid_mask[:, :wt, :] = False
        
        # Top wall
        self.solid_mask[:, -wt:, :] = True
        self.fluid_mask[:, -wt:, :] = False
        
        # Left wall
        self.solid_mask[:, :, :wt] = True
        self.fluid_mask[:, :, :wt] = False
        
        # Right wall
        self.solid_mask[:, :, -wt:] = True
        self.fluid_mask[:, :, -wt:] = False
