"""
Channel geometry - simple rectangular channel
"""
import numpy as np
from .base_geometry import BaseGeometry


class ChannelGeometry(BaseGeometry):
    """
    Simple rectangular channel geometry.
    
    Creates a straight channel with specified height and width.
    """
    
    def __init__(self, nx, ny, nz, channel_height_ratio=0.5, channel_width_ratio=0.5, dx=1.0,
                 use_smooth_boundary=False):
        """
        Initialize channel geometry.
        
        Args:
            nx, ny, nz: Grid dimensions
            channel_height_ratio: Ratio of channel height to ny (0-1)
            channel_width_ratio: Ratio of channel width to nz (0-1)
            dx: Lattice spacing
            use_smooth_boundary: Use smooth boundaries (not applicable for rectangular channels)
        """
        self.channel_height_ratio = channel_height_ratio
        self.channel_width_ratio = channel_width_ratio
        super().__init__(nx, ny, nz, dx, use_smooth_boundary)
    
    def _build_geometry(self):
        """Build the channel geometry."""
        # Calculate channel dimensions
        channel_height = int(self.ny * self.channel_height_ratio)
        channel_width = int(self.nz * self.channel_width_ratio)
        
        # Calculate offsets to center the channel
        y_offset = (self.ny - channel_height) // 2
        z_offset = (self.nz - channel_width) // 2
        
        # Set everything as solid initially
        self.solid_mask[:, :, :] = True
        self.fluid_mask[:, :, :] = False
        self.solid_fraction[:, :, :] = 1.0
        
        # Create channel (fluid region)
        self.solid_mask[:,
                       y_offset:y_offset + channel_height,
                       z_offset:z_offset + channel_width] = False
        self.fluid_mask[:,
                       y_offset:y_offset + channel_height,
                       z_offset:z_offset + channel_width] = True
        self.solid_fraction[:,
                           y_offset:y_offset + channel_height,
                           z_offset:z_offset + channel_width] = 0.0
