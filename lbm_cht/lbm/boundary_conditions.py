"""
Advanced Boundary Condition Methods for LBM

Implements various boundary condition treatments for curved and planar boundaries,
adapted from methods by Bouzidi, Yu, Mei, and Filippova.

Reference: https://github.com/siramirsaman/LBM
Based on methods described in literature for accurate curved boundary treatment.
"""

import numpy as np


class BoundaryConditionMethod:
    """Base class for boundary condition methods."""
    
    def __init__(self, name):
        self.name = name
    
    def apply(self, f, solid_mask, solid_fraction, rho, u, lattice_vectors, weights, opp_indices):
        """
        Apply boundary condition.
        
        Args:
            f: Distribution functions [nx, ny, nz, 19]
            solid_mask: Boolean mask of solid nodes
            solid_fraction: Solid fraction field (0=fluid, 1=solid)
            rho: Density field
            u: Velocity field [nx, ny, nz, 3]
            lattice_vectors: D3Q19 lattice vectors [19, 3]
            weights: D3Q19 weights [19]
            opp_indices: Opposite direction indices [19]
        """
        raise NotImplementedError


class SimpleBounceBack(BoundaryConditionMethod):
    """
    Simple bounce-back boundary condition.
    
    Reflects distribution functions at solid boundaries.
    This is the standard method, simple but creates stair-stepping on curved boundaries.
    """
    
    def __init__(self):
        super().__init__("Simple Bounce-Back")
    
    def apply(self, f, solid_mask, solid_fraction, rho, u, lattice_vectors, weights, opp_indices):
        """Apply simple bounce-back."""
        # Swap distribution functions with opposite directions at solid nodes
        for i in range(19):
            opp = opp_indices[i]
            temp = f[solid_mask, i].copy()
            f[solid_mask, i] = f[solid_mask, opp]
            f[solid_mask, opp] = temp


class BouzidiInterpolatedBC(BoundaryConditionMethod):
    """
    Bouzidi interpolated bounce-back for curved boundaries.
    
    Reference: Bouzidi et al. (2001) "Momentum transfer of a Boltzmann-lattice fluid
    with boundaries"
    
    Uses fractional distance to boundary (delta) for sub-grid accuracy.
    - delta < 0.5: Boundary is far, use second neighbor
    - delta >= 0.5: Boundary is close, use first neighbor
    
    This provides smooth, accurate treatment of curved boundaries.
    """
    
    def __init__(self):
        super().__init__("Bouzidi Interpolated")
    
    def apply(self, f, solid_mask, solid_fraction, rho, u, lattice_vectors, weights, opp_indices):
        """Apply Bouzidi interpolated bounce-back."""
        nx, ny, nz, nq = f.shape
        
        # Create output array
        f_new = f.copy()
        
        # Process each solid node
        solid_indices = np.argwhere(solid_mask)
        
        for idx in solid_indices:
            i, j, k = idx
            
            # Check each lattice direction
            for q in range(nq):
                ex, ey, ez = int(lattice_vectors[q, 0]), int(lattice_vectors[q, 1]), int(lattice_vectors[q, 2])
                opp = opp_indices[q]
                
                # Neighbor in opposite direction (fluid side)
                ni, nj, nk = i - ex, j - ey, k - ez
                
                # Check if neighbor is in bounds and is fluid
                if (0 <= ni < nx and 0 <= nj < ny and 0 <= nk < nz and
                    not solid_mask[ni, nj, nk]):
                    
                    # Fractional distance to boundary
                    # Use solid_fraction: 0=fluid, 1=fully solid
                    # delta represents distance from fluid to boundary
                    delta = 1.0 - solid_fraction[i, j, k]
                    
                    # Clamp delta to avoid division by zero
                    delta = np.clip(delta, 0.01, 0.99)
                    
                    # Second neighbor for long-distance interpolation
                    ni2, nj2, nk2 = i - 2*ex, j - 2*ey, k - 2*ez
                    
                    if delta >= 0.5:
                        # Boundary is close to first neighbor
                        # Use interpolation between first neighbor's incoming and outgoing
                        f_new[i, j, k, opp] = (1.0 / (2.0 * delta)) * f[ni, nj, nk, q] + \
                                              ((2.0 * delta - 1.0) / (2.0 * delta)) * f[ni, nj, nk, opp]
                    else:
                        # Boundary is far from first neighbor
                        # Use second neighbor if available
                        if (0 <= ni2 < nx and 0 <= nj2 < ny and 0 <= nk2 < nz):
                            f_new[i, j, k, opp] = 2.0 * delta * f[ni, nj, nk, q] + \
                                                  (1.0 - 2.0 * delta) * f[ni2, nj2, nk2, opp]
                        else:
                            # Fallback to simple bounce-back if second neighbor unavailable
                            f_new[i, j, k, opp] = f[ni, nj, nk, q]
        
        # Copy back the modified distribution functions
        f[solid_mask] = f_new[solid_mask]


class YuInterpolatedBC(BoundaryConditionMethod):
    """
    Yu interpolated boundary condition with wall velocity support.
    
    Reference: Yu et al. (2003) "Viscous flow computations with the method of
    lattice Boltzmann equation"
    
    Similar to Bouzidi but with better handling of wall velocity and improved
    interpolation formula.
    """
    
    def __init__(self, wall_velocity=None):
        super().__init__("Yu Interpolated")
        self.wall_velocity = wall_velocity if wall_velocity is not None else np.zeros(3)
    
    def apply(self, f, solid_mask, solid_fraction, rho, u, lattice_vectors, weights, opp_indices):
        """Apply Yu interpolated BC with wall velocity."""
        nx, ny, nz, nq = f.shape
        f_new = f.copy()
        
        solid_indices = np.argwhere(solid_mask)
        
        for idx in solid_indices:
            i, j, k = idx
            
            for q in range(nq):
                ex, ey, ez = int(lattice_vectors[q, 0]), int(lattice_vectors[q, 1]), int(lattice_vectors[q, 2])
                opp = opp_indices[q]
                
                ni, nj, nk = i - ex, j - ey, k - ez
                
                if (0 <= ni < nx and 0 <= nj < ny and 0 <= nk < nz and
                    not solid_mask[ni, nj, nk]):
                    
                    delta = 1.0 - solid_fraction[i, j, k]
                    delta = np.clip(delta, 0.01, 0.99)
                    
                    ni2, nj2, nk2 = i - 2*ex, j - 2*ey, k - 2*ez
                    
                    # Wall velocity contribution
                    u_wall_dot_e = (self.wall_velocity[0] * lattice_vectors[opp, 0] +
                                   self.wall_velocity[1] * lattice_vectors[opp, 1] +
                                   self.wall_velocity[2] * lattice_vectors[opp, 2])
                    
                    wall_term = 2.0 * weights[q] * rho[ni, nj, nk] * 3.0 * u_wall_dot_e
                    
                    # Interpolate equilibrium at boundary
                    if (0 <= ni2 < nx and 0 <= nj2 < ny and 0 <= nk2 < nz):
                        f_wall = f[ni2, nj2, nk2, q] + delta * (f[ni, nj, nk, q] - f[ni2, nj2, nk2, q])
                    else:
                        f_wall = f[ni, nj, nk, q]
                    
                    # Yu formula
                    f_new[i, j, k, opp] = f_wall + (delta / (1.0 + delta)) * \
                                          (f[ni, nj, nk, opp] - f_wall) + wall_term
        
        f[solid_mask] = f_new[solid_mask]


class FilippovaInterpolatedBC(BoundaryConditionMethod):
    """
    Filippova-Hanel interpolated boundary condition.
    
    Reference: Filippova & Hanel (1998) "Grid refinement for lattice-BGK models"
    
    Alternative interpolation scheme with different treatment for delta < 0.5 vs >= 0.5.
    """
    
    def __init__(self, wall_velocity=None):
        super().__init__("Filippova Interpolated")
        self.wall_velocity = wall_velocity if wall_velocity is not None else np.zeros(3)
    
    def apply(self, f, solid_mask, solid_fraction, rho, u, lattice_vectors, weights, opp_indices):
        """Apply Filippova interpolated BC."""
        nx, ny, nz, nq = f.shape
        f_new = f.copy()
        
        solid_indices = np.argwhere(solid_mask)
        
        for idx in solid_indices:
            i, j, k = idx
            
            for q in range(nq):
                ex, ey, ez = int(lattice_vectors[q, 0]), int(lattice_vectors[q, 1]), int(lattice_vectors[q, 2])
                opp = opp_indices[q]
                
                ni, nj, nk = i - ex, j - ey, k - ez
                
                if (0 <= ni < nx and 0 <= nj < ny and 0 <= nk < nz and
                    not solid_mask[ni, nj, nk]):
                    
                    delta = 1.0 - solid_fraction[i, j, k]
                    delta = np.clip(delta, 0.01, 0.99)
                    
                    # Wall velocity contribution
                    u_wall_dot_e = (self.wall_velocity[0] * lattice_vectors[opp, 0] +
                                   self.wall_velocity[1] * lattice_vectors[opp, 1] +
                                   self.wall_velocity[2] * lattice_vectors[opp, 2])
                    
                    wall_term = 2.0 * weights[q] * rho[ni, nj, nk] * 3.0 * u_wall_dot_e
                    
                    if delta >= 0.5:
                        # Close boundary: use fluid node velocity
                        u_bf = ((delta - 1.0) / delta) * u[ni, nj, nk] + \
                               (1.0 / delta) * self.wall_velocity
                    else:
                        # Far boundary: use fluid node directly
                        u_bf = u[ni, nj, nk]
                    
                    # Calculate equilibrium at boundary with interpolated velocity
                    u_bf_dot_e = (u_bf[0] * lattice_vectors[q, 0] +
                                 u_bf[1] * lattice_vectors[q, 1] +
                                 u_bf[2] * lattice_vectors[q, 2])
                    
                    u_bf_mag_sq = u_bf[0]**2 + u_bf[1]**2 + u_bf[2]**2
                    
                    f_star = weights[q] * (1.0 + 3.0 * u_bf_dot_e +
                                          4.5 * u_bf_dot_e**2 - 1.5 * u_bf_mag_sq)
                    
                    # Filippova formula (depends on tau - to be provided)
                    # For now, use simplified version
                    f_new[i, j, k, opp] = f[ni, nj, nk, q] + wall_term
        
        f[solid_mask] = f_new[solid_mask]


# Factory function to get boundary condition method
def get_boundary_method(method_name, **kwargs):
    """
    Get boundary condition method by name.
    
    Args:
        method_name: One of 'simple', 'bouzidi', 'yu', 'filippova'
        **kwargs: Additional arguments (e.g., wall_velocity for Yu/Filippova)
    
    Returns:
        BoundaryConditionMethod instance
    """
    methods = {
        'simple': SimpleBounceBack,
        'bounce-back': SimpleBounceBack,
        'bouzidi': BouzidiInterpolatedBC,
        'interpolated': BouzidiInterpolatedBC,
        'yu': lambda: YuInterpolatedBC(**kwargs),
        'filippova': lambda: FilippovaInterpolatedBC(**kwargs),
    }
    
    method_name = method_name.lower()
    if method_name not in methods:
        raise ValueError(f"Unknown boundary method: {method_name}. "
                        f"Available: {list(methods.keys())}")
    
    method_class = methods[method_name]
    if callable(method_class) and not isinstance(method_class, type):
        return method_class()
    else:
        return method_class()
