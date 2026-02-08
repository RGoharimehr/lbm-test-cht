"""
Base material class for defining thermal properties
"""


class Material:
    """
    Base class for material properties.
    
    Defines thermal and fluid properties for LBM simulations.
    """
    
    def __init__(self, name, density, thermal_conductivity, specific_heat,
                 viscosity=None, is_solid=False):
        """
        Initialize material with properties.
        
        Args:
            name: Material name
            density: Density (kg/m^3)
            thermal_conductivity: Thermal conductivity (W/m·K)
            specific_heat: Specific heat capacity (J/kg·K)
            viscosity: Dynamic viscosity (Pa·s) - required for fluids
            is_solid: Whether this is a solid material
        """
        self.name = name
        self.density = density
        self.thermal_conductivity = thermal_conductivity
        self.specific_heat = specific_heat
        self.viscosity = viscosity
        self.is_solid = is_solid
        
        if not is_solid and viscosity is None:
            raise ValueError("Viscosity must be specified for fluid materials")
    
    def get_thermal_diffusivity(self):
        """Calculate thermal diffusivity (m^2/s)."""
        return self.thermal_conductivity / (self.density * self.specific_heat)
    
    def get_kinematic_viscosity(self):
        """Calculate kinematic viscosity (m^2/s)."""
        if self.is_solid:
            raise ValueError("Kinematic viscosity not defined for solids")
        return self.viscosity / self.density
    
    def get_prandtl_number(self):
        """Calculate Prandtl number."""
        if self.is_solid:
            raise ValueError("Prandtl number not defined for solids")
        return self.viscosity * self.specific_heat / self.thermal_conductivity
    
    def __repr__(self):
        return (f"Material(name='{self.name}', density={self.density}, "
                f"k={self.thermal_conductivity}, cp={self.specific_heat}, "
                f"mu={self.viscosity}, solid={self.is_solid})")


# Predefined common materials
class CommonMaterials:
    """Common materials with predefined properties."""
    
    @staticmethod
    def water(temperature=300):
        """Water at specified temperature (default: 300K = 27°C)."""
        # Properties at 300K
        return Material(
            name="Water",
            density=997.0,
            thermal_conductivity=0.613,
            specific_heat=4182.0,
            viscosity=8.54e-4,
            is_solid=False
        )
    
    @staticmethod
    def air(temperature=300):
        """Air at specified temperature (default: 300K = 27°C)."""
        # Properties at 300K, 1 atm
        return Material(
            name="Air",
            density=1.177,
            thermal_conductivity=0.0267,
            specific_heat=1007.0,
            viscosity=1.85e-5,
            is_solid=False
        )
    
    @staticmethod
    def copper():
        """Copper solid."""
        return Material(
            name="Copper",
            density=8960.0,
            thermal_conductivity=401.0,
            specific_heat=385.0,
            viscosity=None,
            is_solid=True
        )
    
    @staticmethod
    def aluminum():
        """Aluminum solid."""
        return Material(
            name="Aluminum",
            density=2700.0,
            thermal_conductivity=237.0,
            specific_heat=897.0,
            viscosity=None,
            is_solid=True
        )
    
    @staticmethod
    def steel():
        """Stainless steel solid."""
        return Material(
            name="Steel",
            density=8000.0,
            thermal_conductivity=16.0,
            specific_heat=500.0,
            viscosity=None,
            is_solid=True
        )
