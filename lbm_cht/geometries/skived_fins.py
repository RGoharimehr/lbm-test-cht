"""
Skived fins geometry - parallel plate fins
"""
import numpy as np
from .base_geometry import BaseGeometry


class SkivedFinsGeometry(BaseGeometry):
    """
    Skived fins geometry with parallel plate fins.
    
    Creates an array of thin parallel fins for enhanced heat transfer.
    """
    
    def __init__(self, nx, ny, nz, num_fins=10, fin_thickness=2, dx=1.0):
        """
        Initialize skived fins geometry.
        
        Args:
            nx, ny, nz: Grid dimensions
            num_fins: Number of fins
            fin_thickness: Thickness of each fin in lattice units
            dx: Lattice spacing
        """
        self.num_fins = num_fins
        self.fin_thickness = fin_thickness
        super().__init__(nx, ny, nz, dx)
    
    def _build_geometry(self):
        """Build the skived fins geometry."""
        # Set everything as fluid initially
        self.solid_mask[:, :, :] = False
        self.fluid_mask[:, :, :] = True
        
        # Calculate spacing between fins
        available_space = self.nz - (self.num_fins * self.fin_thickness)
        if available_space < 0:
            raise ValueError("Too many fins or fins too thick for the given domain size")
        
        spacing = available_space // (self.num_fins + 1) if self.num_fins > 0 else 0
        
        # Create fins along z-direction (parallel plates in y-z plane)
        z_pos = spacing
        for i in range(self.num_fins):
            if z_pos + self.fin_thickness <= self.nz:
                self.solid_mask[:, :, z_pos:z_pos + self.fin_thickness] = True
                self.fluid_mask[:, :, z_pos:z_pos + self.fin_thickness] = False
                z_pos += self.fin_thickness + spacing
        
        # Add base plate at bottom
        base_thickness = 2
        self.solid_mask[:, :base_thickness, :] = True
        self.fluid_mask[:, :base_thickness, :] = False
