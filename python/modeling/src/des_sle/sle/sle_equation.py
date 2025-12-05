"""
SLEEquation: computes solid–liquid equilibrium residuals for a binary mixture.

This version is designed to be extensible and compatible with the eutectic
solver find_eutectic_point() based on a 2×2 equation system.
"""

import numpy as np


class SLEEquation:
    """
    General SLE equation:

        ln(x_i * γ_i) + (ΔH_fus,i / R) * (1/T – 1/Tm_i) = 0

    - components: list of Component objects with attributes dHfus (J/mol) and Tm (K)
    - model: thermodynamic model with method activity_coefficient(x, T)

    Extensible: you can override `residual()` to implement alternative SLE formulas.
    """

    R = 8.31446  # J/mol·K

    def __init__(self, components, model):
        self.components = components
        self.model = model

    # ------------------------------
    # Main interface used by solver
    # ------------------------------
    def residual(self, T, x, component_index):
        """
        Compute a scalar SLE residual for the component at `component_index`.

        T : float (temperature in K)
        x : array-like of mole fractions
        component_index : int (0 or 1 in a binary mixture)

        Returns: float
        """
        T = float(T)
        x = np.asarray(x, float)

        # 1) Activity coefficients
        gamma = np.asarray(self.model.activity_coefficient(x, T), float)

        # 2) Select component
        comp = self.components[component_index]

        # 3) SLE equation (scalar)
        lhs = np.log(x[component_index] * gamma[component_index])
        rhs = (comp.dHfus / self.R) * (1.0 / T - 1.0 / comp.Tm)

        return lhs + rhs  # scalar float

    # ----------------------------------------------------
    # Backward compatibility — allows eq(T,x,i) calls
    # ----------------------------------------------------
    def __call__(self, T, x, index=0):
        """
        Legacy wrapper so old code using sle(T, x, index) still works.
        """
        return np.array([self.residual(T, x, index)], float)


"""
If you want to add a new SLE equation model (for example Schroeder–van Laar or 
solid-solution SLE), you only need to create a subclass:

class SLEEquation_SolidSolution(SLEEquation):
    def residual(self, T, x, component_index):
        # implement new formula here
        return new_residual


"""
