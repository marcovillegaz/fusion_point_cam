"""
SLE Solver Class
"""

import numpy as np
from scipy.optimize import fsolve


class SLESolver:
    def __init__(self, sle_equation, initial_guess=300.0):
        self.eq = sle_equation
        self.initial_guess = initial_guess

    def solve_T(self, x, index):
        """
        Solve SLE for a single composition and solid component.
        """
        try:
            T = fsolve(self.eq, self.initial_guess, args=(x, index))[0]
            return T
        except Exception:
            return np.nan

    def compute_curve(self, x_values):
        """
        Compute equilibrium temperatures for both solids.
        """
        T_eq_1 = []
        T_eq_2 = []

        for x1 in x_values:
            x = [x1, 1 - x1]

            T1 = self.solve_T(x, index=0)
            T2 = self.solve_T(x, index=1)

            T_eq_1.append(T1)
            T_eq_2.append(T2)

        return np.array(T_eq_1), np.array(T_eq_2)
