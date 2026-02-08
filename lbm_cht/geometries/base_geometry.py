"""
Base geometry class for all geometries
"""
import numpy as np
from abc import ABC, abstractmethod
import warnings


class BaseGeometry(ABC):
    """
    Abstract base class for all geometries in LBM CHT simulations.
    
    Attributes:
        nx, ny, nz: Grid dimensions
        dx: Lattice spacing
        solid_mask: Boolean array indicating solid nodes
        fluid_mask: Boolean array indicating fluid nodes
        solid_fraction: Float array (0-1) indicating partial solid coverage for smooth boundaries
    """
    
    def __init__(self, nx, ny, nz, dx=1.0, use_smooth_boundary=True):
        """
        Initialize base geometry.
        
        Args:
            nx, ny, nz: Number of lattice nodes in x, y, z directions
            dx: Lattice spacing (default: 1.0)
            use_smooth_boundary: Use sub-voxel accuracy for smooth boundaries (default: True)
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        self.dx = dx
        self.use_smooth_boundary = use_smooth_boundary
        
        # Initialize masks
        self.solid_mask = np.zeros((nx, ny, nz), dtype=bool)
        self.fluid_mask = np.ones((nx, ny, nz), dtype=bool)
        
        # Initialize solid fraction field for smooth boundaries (0=fluid, 1=solid)
        self.solid_fraction = np.zeros((nx, ny, nz), dtype=float)
        
        # Build the geometry
        self._build_geometry()
        
        # Validate geometry resolution
        self._validate_resolution()
    
    @abstractmethod
    def _build_geometry(self):
        """
        Build the geometry by setting solid and fluid masks.
        Must be implemented by derived classes.
        """
        pass
    
    def _validate_resolution(self):
        """
        Validate that the geometry has adequate resolution.
        Should be overridden by derived classes with specific requirements.
        """
        # Default: warn if grid is too coarse
        min_cells = 10
        if min(self.nx, self.ny, self.nz) < min_cells:
            warnings.warn(
                f"Grid resolution may be too coarse: {self.nx}x{self.ny}x{self.nz}. "
                f"Consider using at least {min_cells} cells in each direction.",
                UserWarning
            )
    
    def get_solid_mask(self):
        """Return the solid mask."""
        return self.solid_mask
    
    def get_fluid_mask(self):
        """Return the fluid mask."""
        return self.fluid_mask
    
    def get_solid_fraction(self):
        """Return the solid fraction field for smooth boundaries."""
        return self.solid_fraction
    
    def has_smooth_boundary(self):
        """Check if geometry uses smooth boundary representation."""
        return self.use_smooth_boundary and np.any((self.solid_fraction > 0) & (self.solid_fraction < 1))
    
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
        Uses neighbor counting with solid fraction for improved accuracy.
        """
        if self.has_smooth_boundary():
            # Use solid fraction for more accurate surface area
            surface_area = 0.0
            
            for i in range(1, self.nx - 1):
                for j in range(1, self.ny - 1):
                    for k in range(1, self.nz - 1):
                        sf = self.solid_fraction[i, j, k]
                        if sf > 0:
                            # Check neighbors and weight by solid fraction difference
                            for di, dj, dk in [(-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1)]:
                                ni, nj, nk = i+di, j+dj, k+dk
                                neighbor_sf = self.solid_fraction[ni, nj, nk]
                                # Add interface area proportional to solid fraction difference
                                surface_area += abs(sf - neighbor_sf) * 0.5
            
            return surface_area * (self.dx ** 2)
        else:
            # Use simple face counting for non-smooth boundaries
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
    
    def compute_geometry_quality_metrics(self):
        """
        Compute quality metrics for the geometry.
        
        Returns:
            dict: Dictionary containing quality metrics
        """
        metrics = {
            'porosity': self.get_porosity(),
            'surface_area': self.get_surface_area(),
            'has_smooth_boundary': self.has_smooth_boundary(),
            'min_feature_size': self._estimate_min_feature_size(),
            'resolution_ratio': self._compute_resolution_ratio(),
        }
        
        return metrics
    
    def _estimate_min_feature_size(self):
        """Estimate minimum feature size in lattice units."""
        # Simple estimate: find smallest connected solid region
        # For now, return dx as a placeholder
        return self.dx
    
    def _compute_resolution_ratio(self):
        """
        Compute resolution ratio (grid cells per minimum feature).
        Higher is better for accuracy.
        """
        min_feature = self._estimate_min_feature_size()
        if min_feature > 0:
            return min_feature / self.dx
        return 0.0
