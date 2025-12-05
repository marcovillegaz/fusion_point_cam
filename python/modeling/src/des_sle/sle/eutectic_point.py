"""Functions to find the eutectic point of a binary mixture using 2×2
nonlinear system solving.
"""

import numpy as np
from scipy.optimize import fsolve

from des_sle.sle.sle_equation import SLEEquation


def sle_system(vars, sle: SLEEquation):
    """
    vars = [T, x1]
    Returns:
        [f1(T, [x1, 1-x1]), f2(T, [x1, 1-x1])]
    where f1 and f2 are scalar SLE residuals.
    """
    T = float(vars[0])
    x1 = vars[1]

    # avoid nonphysical compositions (helps solver behavior)
    if not (0.0 < x1 < 1.0):
        return [1e6, 1e6]

    x = np.array([x1, 1.0 - x1])

    # The SLEEquation class must provide a "residual" or "eval" method per component
    f1 = sle.residual(T, x, component_index=0)
    f2 = sle.residual(T, x, component_index=1)

    return [f1, f2]


def find_eutectic_point(sle_equation, T_guess=300.0, x_guess=0.5):
    """
    Solve the 2 unknowns:
        T_e = eutectic temperature
        x_e = eutectic composition

    by solving simultaneously:
        f1(T, x) = 0   (SLE equation for component 1)
        f2(T, x) = 0   (SLE equation for component 2)
    """

    sol, infodict, ier, mesg = fsolve(
        func=sle_system, x0=[T_guess, x_guess], args=(sle_equation,), full_output=True
    )

    if ier != 1:
        raise RuntimeError(f"Eutectic solver failed: {mesg}")

    T_e, x_e = sol[0], sol[1]
    return x_e, T_e
