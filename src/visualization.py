"""
Visualization Module for LBM Simulations

This module provides functions for plotting velocity fields, temperature
fields, streamlines, and exporting to VTK format for ParaView.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D


def plot_velocity_slice(u, z_slice=None, title='Velocity Field', 
                        cmap='viridis', filename=None, show=True):
    """
    Plot velocity magnitude on a 2D slice.
    
    Parameters:
    -----------
    u : ndarray
        Velocity field (nx, ny, nz, 3)
    z_slice : int, optional
        Z-slice index (default: middle)
    title : str
        Plot title
    cmap : str
        Colormap name
    filename : str, optional
        Save figure to file
    show : bool
        Show plot
    """
    if z_slice is None:
        z_slice = u.shape[2] // 2
    
    # Calculate velocity magnitude
    u_mag = np.sqrt(u[:, :, z_slice, 0]**2 + 
                   u[:, :, z_slice, 1]**2 + 
                   u[:, :, z_slice, 2]**2)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(u_mag.T, origin='lower', cmap=cmap, aspect='equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Velocity Magnitude')
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_temperature_slice(T, z_slice=None, title='Temperature Field',
                           cmap='hot', filename=None, show=True):
    """
    Plot temperature on a 2D slice.
    
    Parameters:
    -----------
    T : ndarray
        Temperature field (nx, ny, nz)
    z_slice : int, optional
        Z-slice index (default: middle)
    title : str
        Plot title
    cmap : str
        Colormap name
    filename : str, optional
        Save figure to file
    show : bool
        Show plot
    """
    if z_slice is None:
        z_slice = T.shape[2] // 2
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(T[:, :, z_slice].T, origin='lower', cmap=cmap, aspect='equal')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Temperature')
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_velocity_vectors(u, z_slice=None, subsample=4, title='Velocity Vectors',
                         filename=None, show=True):
    """
    Plot velocity vectors on a 2D slice.
    
    Parameters:
    -----------
    u : ndarray
        Velocity field (nx, ny, nz, 3)
    z_slice : int, optional
        Z-slice index (default: middle)
    subsample : int
        Subsampling factor for vectors
    title : str
        Plot title
    filename : str, optional
        Save figure to file
    show : bool
        Show plot
    """
    if z_slice is None:
        z_slice = u.shape[2] // 2
    
    # Extract slice
    u_slice = u[:, :, z_slice, :]
    
    # Velocity magnitude for background
    u_mag = np.sqrt(u_slice[:, :, 0]**2 + u_slice[:, :, 1]**2)
    
    # Subsample for quiver plot
    u_sub = u_slice[::subsample, ::subsample, :]
    
    # Create meshgrid
    nx, ny = u_sub.shape[:2]
    x = np.arange(0, u.shape[0], subsample)
    y = np.arange(0, u.shape[1], subsample)
    X, Y = np.meshgrid(x, y, indexing='ij')
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Background: velocity magnitude
    im = ax.imshow(u_mag.T, origin='lower', cmap='viridis', alpha=0.5, aspect='equal')
    
    # Vectors
    ax.quiver(X, Y, u_sub[:, :, 0], u_sub[:, :, 1], 
             color='white', scale=None, width=0.003)
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Velocity Magnitude')
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_3d_geometry(solid_mask, title='3D Geometry', 
                     filename=None, show=True, alpha=0.3):
    """
    Plot 3D geometry using voxel representation.
    
    Parameters:
    -----------
    solid_mask : ndarray
        Boolean mask (True = solid)
    title : str
        Plot title
    filename : str, optional
        Save figure to file
    show : bool
        Show plot
    alpha : float
        Transparency
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Subsample for visualization
    subsample = max(1, solid_mask.shape[0] // 50)
    solid_sub = solid_mask[::subsample, ::subsample, ::subsample]
    
    # Plot solid voxels
    ax.voxels(solid_sub, facecolors='gray', alpha=alpha, edgecolor='k')
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title(title)
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_convergence_history(history, title='Convergence History',
                             filename=None, show=True):
    """
    Plot convergence history.
    
    Parameters:
    -----------
    history : list or dict
        Convergence history (list or dict with 'flow' and 'thermal' keys)
    title : str
        Plot title
    filename : str, optional
        Save figure to file
    show : bool
        Show plot
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if isinstance(history, dict):
        if 'flow_convergence' in history:
            ax.semilogy(history['flow_convergence'], 'b-', label='Flow')
        if 'thermal_convergence' in history:
            ax.semilogy(history['thermal_convergence'], 'r-', label='Thermal')
        ax.legend()
    else:
        ax.semilogy(history, 'b-')
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Relative Error')
    ax.set_title(title)
    ax.grid(True)
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close()


def plot_velocity_profile(y, u, u_analytical=None, title='Velocity Profile',
                         filename=None, show=True):
    """
    Plot velocity profile comparison with analytical solution.
    
    Parameters:
    -----------
    y : ndarray
        Y-coordinates
    u : ndarray
        Numerical velocity profile
    u_analytical : ndarray, optional
        Analytical velocity profile
    title : str
        Plot title
    filename : str, optional
        Save figure to file
    show : bool
        Show plot
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.plot(u, y, 'bo-', label='LBM', markersize=4)
    
    if u_analytical is not None:
        ax.plot(u_analytical, y, 'r-', label='Analytical', linewidth=2)
        
        # Calculate error
        error = np.abs(u - u_analytical).max()
        ax.text(0.05, 0.95, f'Max Error: {error:.2e}',
               transform=ax.transAxes, verticalalignment='top')
    
    ax.set_xlabel('Velocity')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close()


def export_to_vtk(filename, velocity=None, temperature=None, 
                 pressure=None, solid_mask=None):
    """
    Export fields to VTK format for ParaView visualization.
    
    Parameters:
    -----------
    filename : str
        Output filename (without extension)
    velocity : ndarray, optional
        Velocity field (nx, ny, nz, 3)
    temperature : ndarray, optional
        Temperature field (nx, ny, nz)
    pressure : ndarray, optional
        Pressure field (nx, ny, nz)
    solid_mask : ndarray, optional
        Solid mask (nx, ny, nz)
    """
    from .utils import save_field_vtk
    
    if velocity is not None:
        save_field_vtk(f"{filename}_velocity", velocity, 
                      field_name='velocity')
    
    if temperature is not None:
        save_field_vtk(f"{filename}_temperature", temperature, 
                      field_name='temperature')
    
    if pressure is not None:
        save_field_vtk(f"{filename}_pressure", pressure, 
                      field_name='pressure')
    
    if solid_mask is not None:
        save_field_vtk(f"{filename}_solid", solid_mask.astype(float), 
                      field_name='solid')
    
    print(f"Exported fields to VTK: {filename}_*.vti")


def create_animation_frames(solver, n_frames, output_dir='frames',
                           field_type='velocity', z_slice=None):
    """
    Create animation frames during simulation.
    
    Parameters:
    -----------
    solver : FlowSolver or ConjugateHTSolver
        LBM solver object
    n_frames : int
        Number of frames to generate
    output_dir : str
        Output directory for frames
    field_type : str
        Type of field to plot ('velocity' or 'temperature')
    z_slice : int, optional
        Z-slice index
    """
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # This would be called as a callback during simulation
    # Implementation depends on specific solver interface
    pass


def plot_dimensionless_numbers(Re, Pr, Nu, Ra=None, title='Dimensionless Numbers',
                               filename=None, show=True):
    """
    Plot dimensionless numbers as a summary.
    
    Parameters:
    -----------
    Re : float
        Reynolds number
    Pr : float
        Prandtl number
    Nu : float
        Nusselt number
    Ra : float, optional
        Rayleigh number
    title : str
        Plot title
    filename : str, optional
        Save figure to file
    show : bool
        Show plot
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    numbers = ['Re', 'Pr', 'Nu']
    values = [Re, Pr, Nu]
    
    if Ra is not None:
        numbers.append('Ra')
        values.append(Ra)
    
    ax.bar(numbers, values, color=['blue', 'green', 'red', 'orange'][:len(numbers)])
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.set_yscale('log')
    
    for i, (n, v) in enumerate(zip(numbers, values)):
        ax.text(i, v, f'{v:.2e}', ha='center', va='bottom')
    
    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
    
    if show:
        plt.show()
    else:
        plt.close()
