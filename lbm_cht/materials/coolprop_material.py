"""
CoolProp integration for material properties
"""
from .material import Material

try:
    import CoolProp.CoolProp as CP
    COOLPROP_AVAILABLE = True
except ImportError:
    COOLPROP_AVAILABLE = False


class CoolPropMaterial(Material):
    """
    Material properties using CoolProp database.
    
    Provides access to thermophysical properties of fluids from CoolProp.
    """
    
    def __init__(self, fluid_name, temperature, pressure=101325):
        """
        Initialize material from CoolProp database.
        
        Args:
            fluid_name: Name of fluid in CoolProp (e.g., 'Water', 'Air', 'R134a')
            temperature: Temperature in Kelvin
            pressure: Pressure in Pascal (default: 101325 Pa = 1 atm)
        """
        if not COOLPROP_AVAILABLE:
            raise ImportError(
                "CoolProp is not installed. Install it with: pip install CoolProp"
            )
        
        self.fluid_name = fluid_name
        self.temperature = temperature
        self.pressure = pressure
        
        # Get properties from CoolProp
        try:
            density = CP.PropsSI('D', 'T', temperature, 'P', pressure, fluid_name)
            thermal_conductivity = CP.PropsSI('L', 'T', temperature, 'P', pressure, fluid_name)
            specific_heat = CP.PropsSI('C', 'T', temperature, 'P', pressure, fluid_name)
            viscosity = CP.PropsSI('V', 'T', temperature, 'P', pressure, fluid_name)
            
            # Initialize parent Material class
            super().__init__(
                name=f"{fluid_name} ({temperature}K, {pressure/1000:.1f}kPa)",
                density=density,
                thermal_conductivity=thermal_conductivity,
                specific_heat=specific_heat,
                viscosity=viscosity,
                is_solid=False
            )
        except Exception as e:
            raise ValueError(f"Failed to get properties for {fluid_name}: {e}")
    
    def update_temperature(self, temperature):
        """
        Update properties for a new temperature.
        
        Args:
            temperature: New temperature in Kelvin
        """
        self.temperature = temperature
        
        try:
            self.density = CP.PropsSI('D', 'T', temperature, 'P', self.pressure, self.fluid_name)
            self.thermal_conductivity = CP.PropsSI('L', 'T', temperature, 'P', self.pressure, self.fluid_name)
            self.specific_heat = CP.PropsSI('C', 'T', temperature, 'P', self.pressure, self.fluid_name)
            self.viscosity = CP.PropsSI('V', 'T', temperature, 'P', self.pressure, self.fluid_name)
            self.name = f"{self.fluid_name} ({temperature}K, {self.pressure/1000:.1f}kPa)"
        except Exception as e:
            raise ValueError(f"Failed to update properties for {self.fluid_name}: {e}")
    
    def update_pressure(self, pressure):
        """
        Update properties for a new pressure.
        
        Args:
            pressure: New pressure in Pascal
        """
        self.pressure = pressure
        
        try:
            self.density = CP.PropsSI('D', 'T', self.temperature, 'P', pressure, self.fluid_name)
            self.thermal_conductivity = CP.PropsSI('L', 'T', self.temperature, 'P', pressure, self.fluid_name)
            self.specific_heat = CP.PropsSI('C', 'T', self.temperature, 'P', pressure, self.fluid_name)
            self.viscosity = CP.PropsSI('V', 'T', self.temperature, 'P', pressure, self.fluid_name)
            self.name = f"{self.fluid_name} ({self.temperature}K, {pressure/1000:.1f}kPa)"
        except Exception as e:
            raise ValueError(f"Failed to update properties for {self.fluid_name}: {e}")
    
    @staticmethod
    def list_available_fluids():
        """List all available fluids in CoolProp."""
        if not COOLPROP_AVAILABLE:
            raise ImportError("CoolProp is not installed.")
        
        # Get list of fluids
        fluids = CP.get_global_param_string("FluidsList").split(',')
        return sorted(fluids)
    
    def __repr__(self):
        return (f"CoolPropMaterial(fluid='{self.fluid_name}', T={self.temperature}K, "
                f"P={self.pressure/1000:.1f}kPa, rho={self.density:.2f}, "
                f"k={self.thermal_conductivity:.4f}, cp={self.specific_heat:.2f}, "
                f"mu={self.viscosity:.6e})")
