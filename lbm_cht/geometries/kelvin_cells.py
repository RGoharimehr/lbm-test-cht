"""
Kelvin cell geometry - periodic cellular structure
"""
import numpy as np
from .base_geometry import BaseGeometry


class KelvinCellsGeometry(BaseGeometry):
    """
    Kelvin cells (tetrakaidecahedron) geometry.
    
    Creates a periodic cellular structure based on Kelvin's minimal surface.
    This is a simplified approximation using struts.
    """
    
    def __init__(self, nx, ny, nz, cell_size=10, strut_thickness=2, dx=1.0):
        """
        Initialize Kelvin cells geometry.
        
        Args:
            nx, ny, nz: Grid dimensions
            cell_size: Size of each unit cell in lattice units
            strut_thickness: Thickness of struts in lattice units
            dx: Lattice spacing
        """
        self.cell_size = cell_size
        self.strut_thickness = strut_thickness
        super().__init__(nx, ny, nz, dx)
    
    def _build_geometry(self):
        """Build the Kelvin cells geometry."""
        # Set everything as fluid initially
        self.solid_mask[:, :, :] = False
        self.fluid_mask[:, :, :] = True
        
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
                        self._add_strut(cx, cy, cz, cx, cy + cs, cz)
                    
                    # Horizontal struts in x direction
                    if cx + cs <= self.nx:
                        self._add_strut(cx, cy, cz, cx + cs, cy, cz)
                    
                    # Horizontal struts in z direction
                    if cz + cs <= self.nz:
                        self._add_strut(cx, cy, cz, cx, cy, cz + cs)
                    
                    # Add diagonal struts for tetrakaidecahedron approximation
                    if i < nx_cells and j < ny_cells and k < nz_cells:
                        # Face diagonals
                        if cx + cs <= self.nx and cy + cs <= self.ny:
                            self._add_strut(cx, cy, cz, cx + cs, cy + cs, cz)
    
    def _add_strut(self, x1, y1, z1, x2, y2, z2):
        """Add a strut between two points."""
        # Simple line drawing algorithm
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        
        length = max(abs(dx), abs(dy), abs(dz))
        if length == 0:
            return
        
        t = self.strut_thickness // 2
        
        for i in range(int(length) + 1):
            alpha = i / length if length > 0 else 0
            x = int(x1 + alpha * dx)
            y = int(y1 + alpha * dy)
            z = int(z1 + alpha * dz)
            
            # Add thickness around the line
            for ti in range(-t, t + 1):
                for tj in range(-t, t + 1):
                    for tk in range(-t, t + 1):
                        xi = x + ti
                        yi = y + tj
                        zi = z + tk
                        
                        if 0 <= xi < self.nx and 0 <= yi < self.ny and 0 <= zi < self.nz:
                            self.solid_mask[xi, yi, zi] = True
                            self.fluid_mask[xi, yi, zi] = False
