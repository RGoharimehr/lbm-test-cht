"""
Pin fins geometry - cylindrical pins
"""
import numpy as np
from .base_geometry import BaseGeometry


class PinFinsGeometry(BaseGeometry):
    """
    Pin fins geometry with cylindrical pins arranged in a grid.
    
    Creates an array of cylindrical pin fins for enhanced heat transfer.
    """
    
    def __init__(self, nx, ny, nz, num_pins_y=5, num_pins_z=5, pin_diameter=4, dx=1.0):
        """
        Initialize pin fins geometry.
        
        Args:
            nx, ny, nz: Grid dimensions
            num_pins_y: Number of pins in y direction
            num_pins_z: Number of pins in z direction
            pin_diameter: Diameter of each pin in lattice units
            dx: Lattice spacing
        """
        self.num_pins_y = num_pins_y
        self.num_pins_z = num_pins_z
        self.pin_diameter = pin_diameter
        super().__init__(nx, ny, nz, dx)
    
    def _build_geometry(self):
        """Build the pin fins geometry."""
        # Set everything as fluid initially
        self.solid_mask[:, :, :] = False
        self.fluid_mask[:, :, :] = True
        
        # Add base plate
        base_thickness = 2
        self.solid_mask[:, :base_thickness, :] = True
        self.fluid_mask[:, :base_thickness, :] = False
        
        # Calculate pin spacing
        radius = self.pin_diameter / 2.0
        
        # Calculate available space for pins
        y_space = self.ny - base_thickness
        z_space = self.nz
        
        y_spacing = y_space / (self.num_pins_y + 1)
        z_spacing = z_space / (self.num_pins_z + 1)
        
        # Create pins
        for i in range(self.num_pins_y):
            for j in range(self.num_pins_z):
                # Pin center position
                y_center = base_thickness + int((i + 1) * y_spacing)
                z_center = int((j + 1) * z_spacing)
                
                # Create cylindrical pin along x-axis
                self._add_cylinder(y_center, z_center, radius)
    
    def _add_cylinder(self, y_center, z_center, radius):
        """Add a cylindrical pin along the x-axis."""
        r_sq = radius ** 2
        
        for x in range(self.nx):
            for y in range(max(0, int(y_center - radius - 1)),
                          min(self.ny, int(y_center + radius + 2))):
                for z in range(max(0, int(z_center - radius - 1)),
                              min(self.nz, int(z_center + radius + 2))):
                    # Check if point is inside cylinder
                    dist_sq = (y - y_center) ** 2 + (z - z_center) ** 2
                    if dist_sq <= r_sq:
                        self.solid_mask[x, y, z] = True
                        self.fluid_mask[x, y, z] = False
