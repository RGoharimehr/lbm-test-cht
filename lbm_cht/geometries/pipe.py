"""
Circular pipe geometry - for studying thermal boundary layer development
"""
import numpy as np
from .base_geometry import BaseGeometry


class PipeGeometry(BaseGeometry):
    """
    Circular pipe geometry with walls.
    
    Creates a circular pipe with specified inner diameter and wall thickness.
    Ideal for studying thermal entry length and boundary layer development.
    """
    
    def __init__(self, nx, ny, nz, inner_diameter_ratio=0.7, wall_thickness=3, 
                 dx=1.0, use_smooth_boundary=True):
        """
        Initialize circular pipe geometry.
        
        Args:
            nx, ny, nz: Grid dimensions (nx is length, ny and nz define cross-section)
            inner_diameter_ratio: Inner diameter as fraction of cross-section size (0-1)
            wall_thickness: Wall thickness in lattice units
            dx: Lattice spacing in meters
            use_smooth_boundary: Use smooth boundaries with solid fraction field
        """
        self.inner_diameter_ratio = inner_diameter_ratio
        self.wall_thickness = wall_thickness
        
        # Calculate inner radius in lattice units
        # Use smaller of ny, nz for circular constraint
        cross_section_size = min(ny, nz)
        self.inner_radius = (cross_section_size / 2.0) * inner_diameter_ratio
        self.outer_radius = self.inner_radius + wall_thickness
        
        super().__init__(nx, ny, nz, dx, use_smooth_boundary)
    
    def _build_geometry(self):
        """Build the circular pipe geometry."""
        # Calculate center of cross-section
        cy = self.ny / 2.0
        cz = self.nz / 2.0
        
        if self.use_smooth_boundary:
            self._build_smooth_pipe(cy, cz)
        else:
            self._build_simple_pipe(cy, cz)
    
    def _build_simple_pipe(self, cy, cz):
        """Build pipe with simple binary mask (no sub-voxel accuracy)."""
        # Initialize all as solid
        self.solid_mask[:, :, :] = True
        self.fluid_mask[:, :, :] = False
        self.solid_fraction[:, :, :] = 1.0
        
        # Create circular fluid region
        for j in range(self.ny):
            for k in range(self.nz):
                # Calculate distance from center
                dy = j - cy
                dz = k - cz
                r = np.sqrt(dy**2 + dz**2)
                
                # Check if inside inner radius (fluid region)
                if r <= self.inner_radius:
                    self.solid_mask[:, j, k] = False
                    self.fluid_mask[:, j, k] = True
                    self.solid_fraction[:, j, k] = 0.0
    
    def _build_smooth_pipe(self, cy, cz):
        """Build pipe with smooth boundaries using solid fraction field."""
        # Initialize all as solid
        self.solid_mask[:, :, :] = True
        self.fluid_mask[:, :, :] = False
        self.solid_fraction[:, :, :] = 1.0
        
        # Use multi-point sampling for smooth boundaries
        n_samples = 5  # 5x5 sub-grid sampling
        
        for j in range(self.ny):
            for k in range(self.nz):
                # Calculate distance from center to cell center
                dy = j - cy
                dz = k - cz
                r_center = np.sqrt(dy**2 + dz**2)
                
                # Quick check: clearly inside or outside
                if r_center < self.inner_radius - 0.7:
                    # Clearly fluid
                    self.solid_mask[:, j, k] = False
                    self.fluid_mask[:, j, k] = True
                    self.solid_fraction[:, j, k] = 0.0
                elif r_center > self.outer_radius + 0.7:
                    # Clearly solid (outside pipe)
                    self.solid_mask[:, j, k] = True
                    self.fluid_mask[:, j, k] = False
                    self.solid_fraction[:, j, k] = 1.0
                else:
                    # Near boundary - use sub-voxel sampling
                    solid_count = 0
                    total_samples = n_samples * n_samples
                    
                    for sj in range(n_samples):
                        for sk in range(n_samples):
                            # Sample point within voxel
                            sample_y = j + (sj + 0.5) / n_samples - 0.5
                            sample_z = k + (sk + 0.5) / n_samples - 0.5
                            
                            # Distance from pipe center
                            dy_sample = sample_y - cy
                            dz_sample = sample_z - cz
                            r_sample = np.sqrt(dy_sample**2 + dz_sample**2)
                            
                            # Check if sample point is in solid
                            # Solid if: r < inner_radius (wall) or r > outer_radius (outside)
                            if r_sample < self.inner_radius or r_sample > self.outer_radius:
                                solid_count += 1
                    
                    # Calculate solid fraction
                    solid_frac = solid_count / total_samples
                    self.solid_fraction[:, j, k] = solid_frac
                    
                    # Set masks based on majority
                    if solid_frac > 0.5:
                        self.solid_mask[:, j, k] = True
                        self.fluid_mask[:, j, k] = False
                    else:
                        self.solid_mask[:, j, k] = False
                        self.fluid_mask[:, j, k] = True
        
        # Validate minimum resolution
        diameter_cells = 2 * self.inner_radius
        if diameter_cells < 10:
            import warnings
            warnings.warn(
                f"Pipe inner diameter has only {diameter_cells:.1f} cells. "
                f"Recommend at least 10-20 cells for accurate boundary layers. "
                f"Consider increasing grid resolution or inner_diameter_ratio."
            )
    
    def get_inner_diameter(self):
        """Get inner diameter in physical units."""
        return 2 * self.inner_radius * self.dx
    
    def get_outer_diameter(self):
        """Get outer diameter in physical units."""
        return 2 * self.outer_radius * self.dx
    
    def get_wall_thickness_physical(self):
        """Get wall thickness in physical units."""
        return self.wall_thickness * self.dx
    
    def get_cross_sectional_area(self):
        """Get fluid cross-sectional area in physical units."""
        return np.pi * (self.inner_radius * self.dx) ** 2
    
    def get_hydraulic_diameter(self):
        """Get hydraulic diameter (equals inner diameter for circular pipe)."""
        return self.get_inner_diameter()
    
    def __repr__(self):
        return (f"PipeGeometry(nx={self.nx}, ny={self.ny}, nz={self.nz}, "
                f"inner_diameter={self.get_inner_diameter():.6f}m, "
                f"wall_thickness={self.get_wall_thickness_physical():.6f}m)")
