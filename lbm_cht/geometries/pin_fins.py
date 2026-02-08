"""
Pin fins geometry - cylindrical pins with smooth boundaries
"""
import numpy as np
from .base_geometry import BaseGeometry
import warnings


class PinFinsGeometry(BaseGeometry):
    """
    Pin fins geometry with cylindrical pins arranged in a grid.
    
    Creates an array of cylindrical pin fins for enhanced heat transfer.
    Uses signed distance functions for smooth boundary representation.
    """
    
    def __init__(self, nx, ny, nz, num_pins_y=5, num_pins_z=5, pin_diameter=4, dx=1.0, 
                 use_smooth_boundary=True):
        """
        Initialize pin fins geometry.
        
        Args:
            nx, ny, nz: Grid dimensions
            num_pins_y: Number of pins in y direction
            num_pins_z: Number of pins in z direction
            pin_diameter: Diameter of each pin in lattice units
            dx: Lattice spacing
            use_smooth_boundary: Use sub-voxel accuracy for smooth boundaries
        """
        self.num_pins_y = num_pins_y
        self.num_pins_z = num_pins_z
        self.pin_diameter = pin_diameter
        super().__init__(nx, ny, nz, dx, use_smooth_boundary)
    
    def _validate_resolution(self):
        """Validate that pin diameter has sufficient resolution."""
        min_cells_per_diameter = 6  # Minimum for reasonable circle representation
        cells_per_diameter = self.pin_diameter
        
        if cells_per_diameter < min_cells_per_diameter:
            warnings.warn(
                f"Pin diameter ({self.pin_diameter} cells) may have insufficient resolution. "
                f"Recommended: at least {min_cells_per_diameter} cells per diameter for smooth pins. "
                f"Consider increasing grid resolution or pin diameter.",
                UserWarning
            )
        
        # Also check overall grid resolution
        super()._validate_resolution()
    
    def _build_geometry(self):
        """Build the pin fins geometry with smooth boundaries."""
        # Set everything as fluid initially
        self.solid_mask[:, :, :] = False
        self.fluid_mask[:, :, :] = True
        self.solid_fraction[:, :, :] = 0.0
        
        # Add base plate
        base_thickness = 2
        self.solid_mask[:, :base_thickness, :] = True
        self.fluid_mask[:, :base_thickness, :] = False
        self.solid_fraction[:, :base_thickness, :] = 1.0
        
        # Calculate pin spacing
        radius = self.pin_diameter / 2.0
        
        # Calculate available space for pins
        y_space = self.ny - base_thickness
        z_space = self.nz
        
        y_spacing = y_space / (self.num_pins_y + 1)
        z_spacing = z_space / (self.num_pins_z + 1)
        
        # Create pins with smooth boundaries
        for i in range(self.num_pins_y):
            for j in range(self.num_pins_z):
                # Pin center position
                y_center = base_thickness + (i + 1) * y_spacing
                z_center = (j + 1) * z_spacing
                
                # Create cylindrical pin along x-axis
                self._add_smooth_cylinder(y_center, z_center, radius)
    
    def _add_smooth_cylinder(self, y_center, z_center, radius):
        """
        Add a cylindrical pin along the x-axis with smooth boundaries.
        Uses signed distance function for sub-voxel accuracy.
        """
        # Extended search region to ensure we capture all boundary voxels
        y_min = max(0, int(y_center - radius - 2))
        y_max = min(self.ny, int(y_center + radius + 3))
        z_min = max(0, int(z_center - radius - 2))
        z_max = min(self.nz, int(z_center + radius + 3))
        
        for x in range(self.nx):
            for y in range(y_min, y_max):
                for z in range(z_min, z_max):
                    if self.use_smooth_boundary:
                        # Calculate solid fraction using sub-voxel sampling
                        solid_frac = self._compute_cylinder_solid_fraction(
                            y, z, y_center, z_center, radius
                        )
                        
                        self.solid_fraction[x, y, z] = max(
                            self.solid_fraction[x, y, z], solid_frac
                        )
                        
                        # Update masks based on solid fraction threshold
                        if solid_frac > 0.5:
                            self.solid_mask[x, y, z] = True
                            self.fluid_mask[x, y, z] = False
                    else:
                        # Simple binary check
                        dist_sq = (y - y_center) ** 2 + (z - z_center) ** 2
                        if dist_sq <= radius ** 2:
                            self.solid_mask[x, y, z] = True
                            self.fluid_mask[x, y, z] = False
                            self.solid_fraction[x, y, z] = 1.0
    
    def _compute_cylinder_solid_fraction(self, y, z, y_center, z_center, radius):
        """
        Compute solid fraction for a voxel intersecting a cylinder.
        Uses multi-point sampling within the voxel for accuracy.
        
        Args:
            y, z: Voxel indices
            y_center, z_center: Cylinder center coordinates
            radius: Cylinder radius
            
        Returns:
            float: Solid fraction (0.0 to 1.0)
        """
        # Sample points within the voxel (5x5 grid)
        n_samples = 5
        sample_points = np.linspace(-0.4, 0.4, n_samples)
        
        inside_count = 0
        total_count = 0
        
        for dy in sample_points:
            for dz in sample_points:
                # Sample point coordinates
                y_sample = y + dy
                z_sample = z + dz
                
                # Distance from cylinder axis
                dist = np.sqrt((y_sample - y_center)**2 + (z_sample - z_center)**2)
                
                # Check if inside cylinder
                if dist <= radius:
                    inside_count += 1
                total_count += 1
        
        return inside_count / total_count
    
    def _estimate_min_feature_size(self):
        """Estimate minimum feature size (pin diameter)."""
        return self.pin_diameter * self.dx
