"""
Deep Eutectic Solvent Solid-Liquid Equilibria Modeling
"""

__version__ = "0.1.0"

from des_sle.data.component import Component
from des_sle.thermo.activity_model import ActivityModel
from des_sle.thermo.nrtl import NRTL
from des_sle.sle.sle_equation import SLEEquation
from des_sle.sle.sle_solver import SLESolver
from des_sle.sle.eutectic_point import find_eutectic_point

# defines which symbols are exported when someone imports *
__all__ = [
    "Component",
    "ActivityModel",
    "NRTL",
    "SLEEquation",
    "SLESolver",
    "find_eutectic_point",
]
