"""
Visualization tools for LBM CHT simulations
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False


class Visualizer:
    """
    Visualization class for LBM CHT results.
    
    Provides methods for 2D slices, 3D views, and animations.
    """
    
    def __init__(self, geometry, solver=None):
        """
        Initialize visualizer.
        
        Args:
            geometry: Geometry object
            solver: Optional LBM solver object
        """
        self.geometry = geometry
        self.solver = solver
    
    def plot_geometry_slice(self, axis='z', position=None, figsize=(10, 8)):
        """
        Plot a 2D slice of the geometry.
        
        Args:
            axis: Slice axis ('x', 'y', or 'z')
            position: Slice position (default: middle)
            figsize: Figure size
        """
        nx, ny, nz = self.geometry.get_dimensions()
        solid_mask = self.geometry.get_solid_mask()
        
        # Determine slice position
        if position is None:
            position = {'x': nx // 2, 'y': ny // 2, 'z': nz // 2}[axis]
        
        # Extract slice
        if axis == 'x':
            slice_data = solid_mask[position, :, :]
            xlabel, ylabel = 'Y', 'Z'
        elif axis == 'y':
            slice_data = solid_mask[:, position, :]
            xlabel, ylabel = 'X', 'Z'
        else:  # z
            slice_data = solid_mask[:, :, position]
            xlabel, ylabel = 'X', 'Y'
        
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        im = ax.imshow(slice_data.T, origin='lower', cmap='gray', 
                      interpolation='nearest')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f'Geometry Slice ({axis}={position})')
        plt.colorbar(im, ax=ax, label='Solid (1) / Fluid (0)')
        plt.tight_layout()
        return fig
    
    def plot_temperature_slice(self, axis='z', position=None, figsize=(10, 8), 
                               vmin=None, vmax=None):
        """
        Plot a 2D slice of temperature field.
        
        Args:
            axis: Slice axis ('x', 'y', or 'z')
            position: Slice position (default: middle)
            figsize: Figure size
            vmin, vmax: Temperature range for colormap
        """
        if self.solver is None:
            raise ValueError("Solver not provided to visualizer")
        
        nx, ny, nz = self.geometry.get_dimensions()
        T = self.solver.get_temperature()
        
        # Determine slice position
        if position is None:
            position = {'x': nx // 2, 'y': ny // 2, 'z': nz // 2}[axis]
        
        # Extract slice
        if axis == 'x':
            slice_data = T[position, :, :]
            xlabel, ylabel = 'Y', 'Z'
        elif axis == 'y':
            slice_data = T[:, position, :]
            xlabel, ylabel = 'X', 'Z'
        else:  # z
            slice_data = T[:, :, position]
            xlabel, ylabel = 'X', 'Y'
        
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        im = ax.imshow(slice_data.T, origin='lower', cmap='hot', 
                      interpolation='bilinear', vmin=vmin, vmax=vmax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f'Temperature Field ({axis}={position})')
        plt.colorbar(im, ax=ax, label='Temperature (K)')
        plt.tight_layout()
        return fig
    
    def plot_velocity_slice(self, axis='z', position=None, figsize=(10, 8),
                           scale=1.0, skip=2):
        """
        Plot a 2D slice of velocity field with arrows.
        
        Args:
            axis: Slice axis ('x', 'y', or 'z')
            position: Slice position (default: middle)
            figsize: Figure size
            scale: Arrow scale
            skip: Skip every N points for clarity
        """
        if self.solver is None:
            raise ValueError("Solver not provided to visualizer")
        
        nx, ny, nz = self.geometry.get_dimensions()
        u = self.solver.get_velocity()
        
        # Determine slice position
        if position is None:
            position = {'x': nx // 2, 'y': ny // 2, 'z': nz // 2}[axis]
        
        # Extract slice and velocity components
        if axis == 'x':
            u1 = u[1, position, ::skip, ::skip]
            u2 = u[2, position, ::skip, ::skip]
            magnitude = np.sqrt(u[1, position, :, :] ** 2 + u[2, position, :, :] ** 2)
            xlabel, ylabel = 'Y', 'Z'
        elif axis == 'y':
            u1 = u[0, ::skip, position, ::skip]
            u2 = u[2, ::skip, position, ::skip]
            magnitude = np.sqrt(u[0, :, position, :] ** 2 + u[2, :, position, :] ** 2)
            xlabel, ylabel = 'X', 'Z'
        else:  # z
            u1 = u[0, ::skip, ::skip, position]
            u2 = u[1, ::skip, ::skip, position]
            magnitude = np.sqrt(u[0, :, :, position] ** 2 + u[1, :, :, position] ** 2)
            xlabel, ylabel = 'X', 'Y'
        
        # Create meshgrid for arrows
        Y, Z = np.meshgrid(range(0, magnitude.shape[0], skip),
                          range(0, magnitude.shape[1], skip), indexing='ij')
        
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        im = ax.imshow(magnitude.T, origin='lower', cmap='viridis', 
                      interpolation='bilinear')
        ax.quiver(Z, Y, u2.T, u1.T, scale=scale, color='white', alpha=0.6)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f'Velocity Field ({axis}={position})')
        plt.colorbar(im, ax=ax, label='Velocity Magnitude')
        plt.tight_layout()
        return fig
    
    def plot_3d_geometry(self, figsize=(12, 10), opacity=0.3):
        """
        Plot 3D geometry using matplotlib.
        
        Args:
            figsize: Figure size
            opacity: Opacity of solid regions
        """
        solid_mask = self.geometry.get_solid_mask()
        
        # Create figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Get solid voxel positions
        x, y, z = np.where(solid_mask)
        
        # Plot as scatter
        ax.scatter(x, y, z, c='gray', marker='s', s=1, alpha=opacity)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('3D Geometry')
        plt.tight_layout()
        return fig
    
    def plot_3d_temperature(self, threshold_percentile=90, figsize=(12, 10)):
        """
        Plot 3D temperature field (only high temperature regions).
        
        Args:
            threshold_percentile: Only show temperatures above this percentile
            figsize: Figure size
        """
        if self.solver is None:
            raise ValueError("Solver not provided to visualizer")
        
        T = self.solver.get_temperature()
        threshold = np.percentile(T, threshold_percentile)
        
        # Create figure
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
        
        # Get hot voxel positions
        x, y, z = np.where(T > threshold)
        colors = T[x, y, z]
        
        # Plot as scatter with color
        scatter = ax.scatter(x, y, z, c=colors, marker='o', s=2, 
                           cmap='hot', alpha=0.6)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'3D Temperature (>{threshold_percentile}th percentile)')
        plt.colorbar(scatter, ax=ax, label='Temperature (K)')
        plt.tight_layout()
        return fig
    
    def create_pyvista_mesh(self):
        """
        Create PyVista mesh for advanced 3D visualization.
        
        Returns:
            PyVista UniformGrid object
        """
        if not PYVISTA_AVAILABLE:
            raise ImportError("PyVista not available. Install with: pip install pyvista")
        
        nx, ny, nz = self.geometry.get_dimensions()
        
        # Create uniform grid
        grid = pv.UniformGrid()
        grid.dimensions = (nx, ny, nz)
        grid.spacing = (1, 1, 1)
        
        # Add geometry data
        grid.cell_data['solid'] = self.geometry.get_solid_mask().flatten(order='F')
        
        # Add solver data if available
        if self.solver is not None:
            # Use Fortran order for PyVista compatibility (column-major layout)
            grid.cell_data['temperature'] = self.solver.get_temperature().flatten(order='F')
            u = self.solver.get_velocity()
            velocity_mag = np.sqrt(u[0]**2 + u[1]**2 + u[2]**2)
            grid.cell_data['velocity_magnitude'] = velocity_mag.flatten(order='F')
        
        return grid
    
    def save_vtk(self, filename):
        """
        Save data to VTK file for visualization in ParaView.
        
        Args:
            filename: Output filename (should end with .vts)
        """
        grid = self.create_pyvista_mesh()
        grid.save(filename)
        print(f"Saved VTK file: {filename}")
