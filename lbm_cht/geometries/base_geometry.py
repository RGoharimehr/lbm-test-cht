"""
Base geometry class for all geometries
"""
import numpy as np
from abc import ABC, abstractmethod


class BaseGeometry(ABC):
    """
    Abstract base class for all geometries in LBM CHT simulations.
    
    Attributes:
        nx, ny, nz: Grid dimensions
        dx: Lattice spacing
        solid_mask: Boolean array indicating solid nodes
        fluid_mask: Boolean array indicating fluid nodes
    """
    
    def __init__(self, nx, ny, nz, dx=1.0):
        """
        Initialize base geometry.
        
        Args:
            nx, ny, nz: Number of lattice nodes in x, y, z directions
            dx: Lattice spacing (default: 1.0)
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.dx = dx
        
        # Initialize masks
        self.solid_mask = np.zeros((nx, ny, nz), dtype=bool)
        self.fluid_mask = np.ones((nx, ny, nz), dtype=bool)
        
        # Build the geometry
        self._build_geometry()
    
    @abstractmethod
    def _build_geometry(self):
        """
        Build the geometry by setting solid and fluid masks.
        Must be implemented by derived classes.
        """
        pass
    
    def get_solid_mask(self):
        """Return the solid mask."""
        return self.solid_mask
    
    def get_fluid_mask(self):
        """Return the fluid mask."""
        return self.fluid_mask
    
    def get_dimensions(self):
        """Return grid dimensions."""
        return self.nx, self.ny, self.nz
    
    def get_volume(self):
        """Calculate the total volume."""
        return self.nx * self.ny * self.nz * (self.dx ** 3)
    
    def get_solid_volume(self):
        """Calculate the solid volume."""
        return np.sum(self.solid_mask) * (self.dx ** 3)
    
    def get_fluid_volume(self):
        """Calculate the fluid volume."""
        return np.sum(self.fluid_mask) * (self.dx ** 3)
    
    def get_porosity(self):
        """Calculate the porosity (fluid volume fraction)."""
        return self.get_fluid_volume() / self.get_volume()
    
    def get_surface_area(self):
        """
        Estimate the solid-fluid interface surface area.
        Uses a simple neighbor counting approach.
        """
        # Count fluid-solid interfaces
        interface_count = 0
        
        for i in range(1, self.nx - 1):
            for j in range(1, self.ny - 1):
                for k in range(1, self.nz - 1):
                    if self.solid_mask[i, j, k]:
                        # Check neighbors
                        if not self.solid_mask[i-1, j, k]:
                            interface_count += 1
                        if not self.solid_mask[i+1, j, k]:
                            interface_count += 1
                        if not self.solid_mask[i, j-1, k]:
                            interface_count += 1
                        if not self.solid_mask[i, j+1, k]:
                            interface_count += 1
                        if not self.solid_mask[i, j, k-1]:
                            interface_count += 1
                        if not self.solid_mask[i, j, k+1]:
                            interface_count += 1
        
        return interface_count * (self.dx ** 2)
