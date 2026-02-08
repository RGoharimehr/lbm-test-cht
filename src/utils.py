"""
Utility Functions for LBM Simulations

This module provides helper functions for unit conversions, dimensionless
numbers, convergence checking, and data export.
"""

import numpy as np
import os


def calculate_reynolds_number(velocity, length, viscosity):
    """
    Calculate Reynolds number.
    
    Re = U*L/ν
    
    Parameters:
    -----------
    velocity : float
        Characteristic velocity
    length : float
        Characteristic length
    viscosity : float
        Kinematic viscosity
        
    Returns:
    --------
    Re : float
        Reynolds number
    """
    return velocity * length / viscosity


def calculate_prandtl_number(viscosity, thermal_diffusivity):
    """
    Calculate Prandtl number.
    
    Pr = ν/α
    
    Parameters:
    -----------
    viscosity : float
        Kinematic viscosity
    thermal_diffusivity : float
        Thermal diffusivity
        
    Returns:
    --------
    Pr : float
        Prandtl number
    """
    return viscosity / thermal_diffusivity


def calculate_peclet_number(velocity, length, thermal_diffusivity):
    """
    Calculate Peclet number.
    
    Pe = U*L/α = Re*Pr
    
    Parameters:
    -----------
    velocity : float
        Characteristic velocity
    length : float
        Characteristic length
    thermal_diffusivity : float
        Thermal diffusivity
        
    Returns:
    --------
    Pe : float
        Peclet number
    """
    return velocity * length / thermal_diffusivity


def calculate_rayleigh_number(g_beta_dT, length, viscosity, thermal_diffusivity):
    """
    Calculate Rayleigh number for natural convection.
    
    Ra = g*β*ΔT*L³/(ν*α)
    
    Parameters:
    -----------
    g_beta_dT : float
        Product of g*β*ΔT (buoyancy parameter)
    length : float
        Characteristic length
    viscosity : float
        Kinematic viscosity
    thermal_diffusivity : float
        Thermal diffusivity
        
    Returns:
    --------
    Ra : float
        Rayleigh number
    """
    return g_beta_dT * length**3 / (viscosity * thermal_diffusivity)


def calculate_nusselt_number(heat_flux, dT, length, conductivity):
    """
    Calculate Nusselt number.
    
    Nu = q*L/(k*ΔT) = h*L/k
    
    Parameters:
    -----------
    heat_flux : float
        Heat flux or heat transfer coefficient
    dT : float
        Temperature difference
    length : float
        Characteristic length
    conductivity : float
        Thermal conductivity
        
    Returns:
    --------
    Nu : float
        Nusselt number
    """
    if dT < 1e-10:
        return 0.0
    return heat_flux * length / (conductivity * dT)


def lattice_to_physical_velocity(u_lattice, dx, dt):
    """
    Convert lattice velocity to physical velocity.
    
    Parameters:
    -----------
    u_lattice : float or ndarray
        Velocity in lattice units
    dx : float
        Lattice spacing in physical units
    dt : float
        Time step in physical units
        
    Returns:
    --------
    u_physical : float or ndarray
        Velocity in physical units
    """
    return u_lattice * dx / dt


def physical_to_lattice_velocity(u_physical, dx, dt):
    """
    Convert physical velocity to lattice velocity.
    
    Parameters:
    -----------
    u_physical : float or ndarray
        Velocity in physical units
    dx : float
        Lattice spacing in physical units
    dt : float
        Time step in physical units
        
    Returns:
    --------
    u_lattice : float or ndarray
        Velocity in lattice units
    """
    return u_physical * dt / dx


def get_relaxation_time(viscosity, cs2=1.0/3.0):
    """
    Calculate relaxation time from viscosity.
    
    ν = cs²(τ - 0.5)
    τ = ν/cs² + 0.5
    
    Parameters:
    -----------
    viscosity : float
        Kinematic viscosity
    cs2 : float
        Speed of sound squared (default: 1/3)
        
    Returns:
    --------
    tau : float
        Relaxation time
    """
    return viscosity / cs2 + 0.5


def get_viscosity_from_tau(tau, cs2=1.0/3.0):
    """
    Calculate viscosity from relaxation time.
    
    Parameters:
    -----------
    tau : float
        Relaxation time
    cs2 : float
        Speed of sound squared (default: 1/3)
        
    Returns:
    --------
    viscosity : float
        Kinematic viscosity
    """
    return cs2 * (tau - 0.5)


def check_convergence(field_new, field_old, tolerance=1e-6, norm='L2'):
    """
    Check convergence between two fields.
    
    Parameters:
    -----------
    field_new : ndarray
        New field values
    field_old : ndarray
        Old field values
    tolerance : float
        Convergence tolerance
    norm : str
        Norm type ('L2', 'Linf', 'L1')
        
    Returns:
    --------
    converged : bool
        True if converged
    error : float
        Convergence error
    """
    diff = field_new - field_old
    
    if norm == 'L2':
        error = np.linalg.norm(diff) / (np.linalg.norm(field_new) + 1e-10)
    elif norm == 'Linf':
        error = np.max(np.abs(diff)) / (np.max(np.abs(field_new)) + 1e-10)
    elif norm == 'L1':
        error = np.sum(np.abs(diff)) / (np.sum(np.abs(field_new)) + 1e-10)
    else:
        raise ValueError(f"Unknown norm type: {norm}")
    
    converged = error < tolerance
    
    return converged, error


def save_field_vtk(filename, field, field_name='scalar', origin=(0, 0, 0), spacing=(1, 1, 1)):
    """
    Save 3D field to VTK file for visualization in ParaView.
    
    Parameters:
    -----------
    filename : str
        Output filename (without extension)
    field : ndarray
        3D scalar or vector field
    field_name : str
        Name of the field
    origin : tuple
        Origin coordinates
    spacing : tuple
        Grid spacing
    """
    try:
        import vtk
        from vtk.util import numpy_support
    except ImportError:
        print("Warning: VTK not available. Skipping VTK export.")
        return
    
    # Determine if scalar or vector field
    if field.ndim == 3:
        # Scalar field
        nx, ny, nz = field.shape
        is_vector = False
    elif field.ndim == 4:
        # Vector field
        nx, ny, nz, _ = field.shape
        is_vector = True
    else:
        raise ValueError("Field must be 3D or 4D array")
    
    # Create image data
    image_data = vtk.vtkImageData()
    image_data.SetDimensions(nx, ny, nz)
    image_data.SetOrigin(origin)
    image_data.SetSpacing(spacing)
    
    # Convert numpy array to VTK array
    if is_vector:
        # Flatten and reshape for VTK
        vtk_array = numpy_support.numpy_to_vtk(
            field.reshape(-1, 3), deep=True, array_type=vtk.VTK_FLOAT)
    else:
        vtk_array = numpy_support.numpy_to_vtk(
            field.flatten(), deep=True, array_type=vtk.VTK_FLOAT)
    
    vtk_array.SetName(field_name)
    
    if is_vector:
        vtk_array.SetNumberOfComponents(3)
        image_data.GetPointData().SetVectors(vtk_array)
    else:
        image_data.GetPointData().SetScalars(vtk_array)
    
    # Write to file
    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(f"{filename}.vti")
    writer.SetInputData(image_data)
    writer.Write()
    
    print(f"Saved VTK file: {filename}.vti")


def save_field_hdf5(filename, **fields):
    """
    Save multiple fields to HDF5 file.
    
    Parameters:
    -----------
    filename : str
        Output filename
    **fields : ndarrays
        Named fields to save
    """
    try:
        import h5py
    except ImportError:
        print("Warning: h5py not available. Skipping HDF5 export.")
        return
    
    with h5py.File(filename, 'w') as f:
        for name, field in fields.items():
            f.create_dataset(name, data=field, compression='gzip')
    
    print(f"Saved HDF5 file: {filename}")


def load_field_hdf5(filename):
    """
    Load fields from HDF5 file.
    
    Parameters:
    -----------
    filename : str
        Input filename
        
    Returns:
    --------
    fields : dict
        Dictionary of loaded fields
    """
    try:
        import h5py
    except ImportError:
        print("Error: h5py not available.")
        return None
    
    fields = {}
    with h5py.File(filename, 'r') as f:
        for name in f.keys():
            fields[name] = f[name][:]
    
    return fields


def create_output_directory(base_dir='output'):
    """
    Create output directory if it doesn't exist.
    
    Parameters:
    -----------
    base_dir : str
        Base directory name
        
    Returns:
    --------
    output_dir : str
        Created output directory path
    """
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    return base_dir


def print_simulation_parameters(params):
    """
    Print simulation parameters in a formatted way.
    
    Parameters:
    -----------
    params : dict
        Dictionary of simulation parameters
    """
    print("\n" + "="*60)
    print("SIMULATION PARAMETERS")
    print("="*60)
    
    for key, value in params.items():
        if isinstance(value, float):
            print(f"{key:30s}: {value:.6e}")
        else:
            print(f"{key:30s}: {value}")
    
    print("="*60 + "\n")


def analytical_poiseuille_velocity(y, H, dp_dx, viscosity):
    """
    Analytical solution for 2D Poiseuille flow velocity profile.
    
    u(y) = -(dp/dx) * y * (H - y) / (2*μ)
    
    Parameters:
    -----------
    y : ndarray
        y-coordinates
    H : float
        Channel height
    dp_dx : float
        Pressure gradient
    viscosity : float
        Dynamic viscosity
        
    Returns:
    --------
    u : ndarray
        Velocity profile
    """
    return -dp_dx * y * (H - y) / (2.0 * viscosity)


def analytical_couette_velocity(y, H, U_wall):
    """
    Analytical solution for Couette flow velocity profile.
    
    u(y) = U_wall * y / H
    
    Parameters:
    -----------
    y : ndarray
        y-coordinates
    H : float
        Channel height
    U_wall : float
        Moving wall velocity
        
    Returns:
    --------
    u : ndarray
        Velocity profile
    """
    return U_wall * y / H


def calculate_permeability(velocity, viscosity, length, pressure_drop):
    """
    Calculate permeability of porous medium (Darcy's law).
    
    K = μ*u*L / ΔP
    
    Parameters:
    -----------
    velocity : float
        Average velocity through medium
    viscosity : float
        Dynamic viscosity
    length : float
        Medium length
    pressure_drop : float
        Pressure drop across medium
        
    Returns:
    --------
    K : float
        Permeability
    """
    if pressure_drop < 1e-10:
        return 0.0
    return viscosity * velocity * length / pressure_drop
