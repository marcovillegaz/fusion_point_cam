"""
This class is for componet
"""

from dataclasses import dataclass


@dataclass
class Component:
    """
    Stores pure component thermodynamic properties for SLE calculations.

    Attributes:
        name: Component name
        Tm: Melting temperature [K]
        dHfus: Enthalpy of fusion [J/mol]
        MW: Molecular weight [g/mol] (optional)
        formula: Chemical formula (optional)
    """

    name: str
    Tm: float  # Melting temperature [K]
    dHfus: float  # Enthalpy of fusion [J/mol]
    MW: float = None  # Molecular weight [g/mol]
    formula: str = None

    def __post_init__(self):
        """Validate input parameters for testing"""
        if self.Tm <= 0:
            raise ValueError(f"Melting temperature must be positive, got {self.Tm}")
        if self.dHfus <= 0:
            raise ValueError(f"Enthalpy of fusion must be positive, got {self.dHfus}")

    def __repr__(self):
        return f"Component('{self.name}', Tm={self.Tm:.2f} K, ΔHfus={self.dHfus:.0f} J/mol)"
