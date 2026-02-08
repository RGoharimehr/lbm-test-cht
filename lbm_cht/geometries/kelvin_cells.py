"""
Kelvin cell geometry - periodic cellular structure with smooth struts
"""
import numpy as np
from .base_geometry import BaseGeometry
import warnings


class KelvinCellsGeometry(BaseGeometry):
    """
    Kelvin cells (tetrakaidecahedron) geometry.
    
    Creates a periodic cellular structure based on Kelvin's minimal surface.
    Uses improved strut generation with smooth boundaries.
    """
    
    def __init__(self, nx, ny, nz, cell_size=10, strut_thickness=2, dx=1.0, 
                 use_smooth_boundary=True):
        """
        Initialize Kelvin cells geometry.
        
        Args:
            nx, ny, nz: Grid dimensions
            cell_size: Size of each unit cell in lattice units
            strut_thickness: Thickness of struts in lattice units
            dx: Lattice spacing
            use_smooth_boundary: Use smooth boundaries for struts
        """
        self.cell_size = cell_size
        self.strut_thickness = strut_thickness
        super().__init__(nx, ny, nz, dx, use_smooth_boundary)
    
    def _validate_resolution(self):
        """Validate that struts have sufficient resolution."""
        min_cells_per_strut = 4
        if self.strut_thickness < min_cells_per_strut:
            warnings.warn(
                f"Strut thickness ({self.strut_thickness} cells) may have insufficient resolution. "
                f"Recommended: at least {min_cells_per_strut} cells for smooth struts.",
                UserWarning
            )
        
        super()._validate_resolution()
    
    def _build_geometry(self):
        """Build the Kelvin cells geometry with smooth struts."""
        # Set everything as fluid initially
        self.solid_mask[:, :, :] = False
        self.fluid_mask[:, :, :] = True
        self.solid_fraction[:, :, :] = 0.0
        
        # Create simplified Kelvin cell structure using cubic framework with diagonal struts
        cs = self.cell_size
        st = self.strut_thickness
        
        # Number of cells in each direction
        nx_cells = self.nx // cs
        ny_cells = self.ny // cs
        nz_cells = self.nz // cs
        
        for i in range(nx_cells + 1):
            for j in range(ny_cells + 1):
                for k in range(nz_cells + 1):
                    # Cell center
                    cx = min(i * cs, self.nx - 1)
                    cy = min(j * cs, self.ny - 1)
                    cz = min(k * cs, self.nz - 1)
                    
                    # Create struts along edges of cubic cells
                    # Vertical struts
                    if cy + cs <= self.ny:
                        self._add_smooth_strut(cx, cy, cz, cx, cy + cs, cz)
                    
                    # Horizontal struts in x direction
                    if cx + cs <= self.nx:
                        self._add_smooth_strut(cx, cy, cz, cx + cs, cy, cz)
                    
                    # Horizontal struts in z direction
                    if cz + cs <= self.nz:
                        self._add_smooth_strut(cx, cy, cz, cx, cy, cz + cs)
                    
                    # Add diagonal struts for tetrakaidecahedron approximation
                    if i < nx_cells and j < ny_cells and k < nz_cells:
                        # Face diagonals
                        if cx + cs <= self.nx and cy + cs <= self.ny:
                            self._add_smooth_strut(cx, cy, cz, cx + cs, cy + cs, cz)
    
    def _add_smooth_strut(self, x1, y1, z1, x2, y2, z2):
        """
        Add a strut between two points with smooth boundaries.
        Uses cylindrical distance field for better accuracy.
        """
        # Direction vector
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        
        length = np.sqrt(dx**2 + dy**2 + dz**2)
        if length < 1e-6:
            return
        
        # Normalized direction
        ux, uy, uz = dx/length, dy/length, dz/length
        
        # Strut radius
        radius = self.strut_thickness / 2.0
        
        # Bounding box for strut
        x_min = max(0, int(min(x1, x2) - radius - 2))
        x_max = min(self.nx, int(max(x1, x2) + radius + 3))
        y_min = max(0, int(min(y1, y2) - radius - 2))
        y_max = min(self.ny, int(max(y1, y2) + radius + 3))
        z_min = max(0, int(min(z1, z2) - radius - 2))
        z_max = min(self.nz, int(max(z1, z2) + radius + 3))
        
        for x in range(x_min, x_max):
            for y in range(y_min, y_max):
                for z in range(z_min, z_max):
                    if self.use_smooth_boundary:
                        # Calculate solid fraction for smooth strut
                        solid_frac = self._compute_strut_solid_fraction(
                            x, y, z, x1, y1, z1, ux, uy, uz, length, radius
                        )
                        
                        self.solid_fraction[x, y, z] = max(
                            self.solid_fraction[x, y, z], solid_frac
                        )
                        
                        if solid_frac > 0.5:
                            self.solid_mask[x, y, z] = True
                            self.fluid_mask[x, y, z] = False
                    else:
                        # Simple binary check
                        dist_to_line = self._distance_point_to_line_segment(
                            x, y, z, x1, y1, z1, x2, y2, z2
                        )
                        
                        if dist_to_line <= radius:
                            self.solid_mask[x, y, z] = True
                            self.fluid_mask[x, y, z] = False
                            self.solid_fraction[x, y, z] = 1.0
    
    def _compute_strut_solid_fraction(self, x, y, z, x1, y1, z1, ux, uy, uz, length, radius):
        """
        Compute solid fraction for a voxel intersecting a cylindrical strut.
        Uses multi-point sampling.
        """
        # Sample points within the voxel
        n_samples = 5
        sample_points = np.linspace(-0.4, 0.4, n_samples)
        
        inside_count = 0
        total_count = 0
        
        for dx_sample in sample_points:
            for dy_sample in sample_points:
                for dz_sample in sample_points:
                    # Sample point coordinates
                    x_sample = x + dx_sample
                    y_sample = y + dy_sample
                    z_sample = z + dz_sample
                    
                    # Distance from strut axis
                    dist = self._distance_point_to_line_segment_extended(
                        x_sample, y_sample, z_sample, 
                        x1, y1, z1, ux, uy, uz, length
                    )
                    
                    if dist <= radius:
                        inside_count += 1
                    total_count += 1
        
        return inside_count / total_count
    
    def _distance_point_to_line_segment(self, px, py, pz, x1, y1, z1, x2, y2, z2):
        """Calculate minimum distance from point to line segment."""
        # Vector from start to end
        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
        length_sq = dx**2 + dy**2 + dz**2
        
        if length_sq < 1e-6:
            # Degenerate case: point segment
            return np.sqrt((px - x1)**2 + (py - y1)**2 + (pz - z1)**2)
        
        # Parameter t along line segment (0 to 1)
        t = max(0, min(1, ((px - x1)*dx + (py - y1)*dy + (pz - z1)*dz) / length_sq))
        
        # Closest point on segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        closest_z = z1 + t * dz
        
        # Distance to closest point
        return np.sqrt((px - closest_x)**2 + (py - closest_y)**2 + (pz - closest_z)**2)
    
    def _distance_point_to_line_segment_extended(self, px, py, pz, x1, y1, z1, ux, uy, uz, length):
        """Calculate distance from point to line segment using parametric form."""
        # Vector from start to point
        vx, vy, vz = px - x1, py - y1, pz - z1
        
        # Project onto line direction
        t = vx*ux + vy*uy + vz*uz
        
        # Clamp to segment
        t = max(0, min(length, t))
        
        # Closest point on segment
        closest_x = x1 + t * ux
        closest_y = y1 + t * uy
        closest_z = z1 + t * uz
        
        # Distance to closest point
        return np.sqrt((px - closest_x)**2 + (py - closest_y)**2 + (pz - closest_z)**2)
