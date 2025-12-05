"""
Docstring for des_sle.solver.sle_equation
"""

import numpy as np


class SLEEquation:
    """
    Scalar SLE equation used by fsolve.
    """

    def __init__(self, components, model):
        """
        components: list of component objects with dHfus, Tm, etc.
        model: a thermodynamic model with .activity_coefficient(x, T)
        """
        self.gas_constant = 8.31446  # J/mol·K

        self.components = components
        self.model = model

    def __call__(self, T, x, index=0):
        """
        Scalar SLE equation used by fsolve.
        - T: scalar temperature (array allowed but only first element used)
        - x: mole fractions
        - index: which component is solid
        """
        T = np.atleast_1d(T).item()

        # 1) Activity coefficients
        gamma = np.asarray(self.model.activity_coefficient(x, T), float)

        # 2) Select solid component
        comp = self.components[index]

        # 3) SLE equation value
        val = np.log(x[index] * gamma[index]) + (comp.dHfus / self.gas_constant) * (
            1.0 / T - 1.0 / comp.Tm
        )

        return np.array([val], float)  # fsolve expects 1D array
