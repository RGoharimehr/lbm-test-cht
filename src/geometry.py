"""
Gyroid and Complex Geometry Generation

This module generates 3D gyroid structures and other complex geometries
for LBM simulations.
"""

import numpy as np


class GyroidGenerator:
    """
    Generate 3D gyroid structures using implicit surface equations.
    
    Gyroids are triply periodic minimal surfaces useful for studying
    heat transfer and fluid flow in porous media.
    """
    
    def __init__(self, nx, ny, nz):
        """
        Initialize gyroid generator.
        
        Parameters:
        -----------
        nx, ny, nz : int
            Domain dimensions
        """
        self.nx = nx
        self.ny = ny
        self.nz = nz
        
    def generate_gyroid(self, threshold=0.0, scale=1.0, surface_type='G'):
        """
        Generate gyroid structure.
        
        Parameters:
        -----------
        threshold : float
            Level set threshold (controls porosity)
            Typical range: -1.0 to 1.0
        scale : float
            Spatial scale (number of unit cells)
            Smaller values = more unit cells
        surface_type : str
            Type of minimal surface:
            - 'G': Gyroid surface
            - 'D': Diamond surface
            - 'P': Primitive surface
            
        Returns:
        --------
        solid_mask : ndarray
            Boolean mask (True = solid, False = fluid)
        """
        # Create coordinate grids
        x = np.linspace(0, 2*np.pi*scale, self.nx)
        y = np.linspace(0, 2*np.pi*scale, self.ny)
        z = np.linspace(0, 2*np.pi*scale, self.nz)
        
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        if surface_type == 'G':
            # Gyroid: sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = threshold
            surface = (np.sin(X) * np.cos(Y) + 
                      np.sin(Y) * np.cos(Z) + 
                      np.sin(Z) * np.cos(X))
        
        elif surface_type == 'D':
            # Diamond: sin(x)sin(y)sin(z) + sin(x)cos(y)cos(z) + 
            #          cos(x)sin(y)cos(z) + cos(x)cos(y)sin(z) = threshold
            surface = (np.sin(X) * np.sin(Y) * np.sin(Z) + 
                      np.sin(X) * np.cos(Y) * np.cos(Z) +
                      np.cos(X) * np.sin(Y) * np.cos(Z) + 
                      np.cos(X) * np.cos(Y) * np.sin(Z))
        
        elif surface_type == 'P':
            # Primitive (Schwarz P): cos(x) + cos(y) + cos(z) = threshold
            surface = np.cos(X) + np.cos(Y) + np.cos(Z)
        
        else:
            raise ValueError(f"Unknown surface type: {surface_type}")
        
        # Create solid mask: solid where surface > threshold
        solid_mask = surface > threshold
        
        return solid_mask
    
    def calculate_porosity(self, solid_mask):
        """
        Calculate porosity of the structure.
        
        Parameters:
        -----------
        solid_mask : ndarray
            Boolean mask (True = solid, False = fluid)
            
        Returns:
        --------
        porosity : float
            Volume fraction of fluid (0 to 1)
        """
        porosity = np.sum(~solid_mask) / solid_mask.size
        return porosity
    
    def adjust_threshold_for_porosity(self, target_porosity, scale=1.0, 
                                     surface_type='G', tolerance=0.01, 
                                     max_iterations=50):
        """
        Find threshold value that gives target porosity.
        
        Parameters:
        -----------
        target_porosity : float
            Desired porosity (0 to 1)
        scale : float
            Spatial scale
        surface_type : str
            Type of surface
        tolerance : float
            Convergence tolerance
        max_iterations : int
            Maximum bisection iterations
            
        Returns:
        --------
        threshold : float
            Optimal threshold value
        solid_mask : ndarray
            Resulting solid mask
        """
        # Bisection method to find threshold
        threshold_low = -2.0
        threshold_high = 2.0
        
        for iteration in range(max_iterations):
            threshold = (threshold_low + threshold_high) / 2.0
            
            solid_mask = self.generate_gyroid(threshold, scale, surface_type)
            porosity = self.calculate_porosity(solid_mask)
            
            error = porosity - target_porosity
            
            if abs(error) < tolerance:
                print(f"Converged in {iteration+1} iterations: "
                      f"porosity={porosity:.4f}, threshold={threshold:.4f}")
                return threshold, solid_mask
            
            if error > 0:
                # Too much fluid, need higher threshold (more solid)
                threshold_low = threshold
            else:
                # Too much solid, need lower threshold (more fluid)
                threshold_high = threshold
        
        print(f"Warning: Did not converge to target porosity. "
              f"Final porosity={porosity:.4f}")
        
        return threshold, solid_mask
    
    def generate_simple_box(self, wall_thickness=2):
        """
        Generate a simple box geometry with walls.
        
        Parameters:
        -----------
        wall_thickness : int
            Thickness of walls in lattice units
            
        Returns:
        --------
        solid_mask : ndarray
            Boolean mask (True = solid walls, False = fluid)
        """
        solid_mask = np.zeros((self.nx, self.ny, self.nz), dtype=bool)
        
        # Add walls on all boundaries
        solid_mask[:wall_thickness, :, :] = True   # -x wall
        solid_mask[-wall_thickness:, :, :] = True  # +x wall
        solid_mask[:, :wall_thickness, :] = True   # -y wall
        solid_mask[:, -wall_thickness:, :] = True  # +y wall
        solid_mask[:, :, :wall_thickness] = True   # -z wall
        solid_mask[:, :, -wall_thickness:] = True  # +z wall
        
        return solid_mask
    
    def generate_channel(self, channel_height=None):
        """
        Generate a channel geometry (flow between parallel plates).
        
        Parameters:
        -----------
        channel_height : int, optional
            Height of the channel (default: nz - 4)
            
        Returns:
        --------
        solid_mask : ndarray
            Boolean mask with solid walls at top and bottom
        """
        if channel_height is None:
            channel_height = self.nz - 4
        
        solid_mask = np.zeros((self.nx, self.ny, self.nz), dtype=bool)
        
        # Bottom wall
        wall_bottom = (self.nz - channel_height) // 2
        solid_mask[:, :, :wall_bottom] = True
        
        # Top wall
        wall_top = wall_bottom + channel_height
        solid_mask[:, :, wall_top:] = True
        
        return solid_mask
    
    def generate_sphere(self, center=None, radius=None):
        """
        Generate a sphere.
        
        Parameters:
        -----------
        center : tuple, optional
            Center coordinates (cx, cy, cz)
        radius : float, optional
            Sphere radius
            
        Returns:
        --------
        solid_mask : ndarray
            Boolean mask (True = solid sphere, False = fluid)
        """
        if center is None:
            center = (self.nx//2, self.ny//2, self.nz//2)
        if radius is None:
            radius = min(self.nx, self.ny, self.nz) / 4.0
        
        # Create coordinate grids
        x = np.arange(self.nx)
        y = np.arange(self.ny)
        z = np.arange(self.nz)
        
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Distance from center
        dist = np.sqrt((X - center[0])**2 + 
                      (Y - center[1])**2 + 
                      (Z - center[2])**2)
        
        solid_mask = dist <= radius
        
        return solid_mask
    
    def combine_geometries(self, *masks, operation='union'):
        """
        Combine multiple geometry masks.
        
        Parameters:
        -----------
        *masks : ndarrays
            Multiple boolean masks
        operation : str
            'union' (OR), 'intersection' (AND), 'difference' (XOR)
            
        Returns:
        --------
        combined_mask : ndarray
            Combined boolean mask
        """
        if len(masks) == 0:
            return np.zeros((self.nx, self.ny, self.nz), dtype=bool)
        
        combined = masks[0].copy()
        
        for mask in masks[1:]:
            if operation == 'union':
                combined |= mask
            elif operation == 'intersection':
                combined &= mask
            elif operation == 'difference':
                combined ^= mask
            else:
                raise ValueError(f"Unknown operation: {operation}")
        
        return combined
    
    def smooth_geometry(self, solid_mask, iterations=1):
        """
        Smooth geometry using morphological operations.
        
        Parameters:
        -----------
        solid_mask : ndarray
            Boolean mask
        iterations : int
            Number of smoothing iterations
            
        Returns:
        --------
        smoothed_mask : ndarray
            Smoothed boolean mask
        """
        from scipy.ndimage import binary_opening, binary_closing
        
        smoothed = solid_mask.copy()
        
        for _ in range(iterations):
            # Opening followed by closing
            smoothed = binary_opening(smoothed)
            smoothed = binary_closing(smoothed)
        
        return smoothed


def generate_gyroid(nx, ny, nz, threshold=0.0, scale=1.0, surface_type='G'):
    """
    Convenience function to generate gyroid structure.
    
    Parameters:
    -----------
    nx, ny, nz : int
        Domain dimensions
    threshold : float
        Level set threshold
    scale : float
        Spatial scale
    surface_type : str
        Type of minimal surface ('G', 'D', or 'P')
        
    Returns:
    --------
    solid_mask : ndarray
        Boolean mask (True = solid, False = fluid)
    """
    generator = GyroidGenerator(nx, ny, nz)
    return generator.generate_gyroid(threshold, scale, surface_type)
