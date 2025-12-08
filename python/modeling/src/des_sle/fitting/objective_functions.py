"""
Objective functions for parameter fitting.
"""

import numpy as np
import warnings
from des_sle.thermo.nrtl import NRTL
from des_sle.sle.sle_equation import SLEEquation
from des_sle.sle.sle_solver import SLESolver


def objective_function_single_curve(params, comp1, comp2, alpha12, curve_data, component_index):
    """
    Objective function for fitting a single liquidus curve.

    Args:
        params: [g12, g21]
        comp1, comp2: Component objects
        alpha12: Fixed alpha parameter
        curve_data: DataFrame with 'x' and 'T' columns for this curve
        component_index: 0 for component 1, 1 for component 2 (which one is crystallizing)

    Returns:
        RMSE for this curve
    """
    g12, g21 = params

    nrtl_params = {"g12": g12, "g21": g21, "alpha12": alpha12}
    model = NRTL(nrtl_params)
    components = [comp1, comp2]
    sle_eq = SLEEquation(components, model)
    solver = SLESolver(sle_eq.residual, initial_guess=300.0)

    total_error = 0.0
    n_points = 0

    for _, row in curve_data.iterrows():
        x1_exp = row["x"]
        T_exp = row["T"]

        # Skip endpoints
        if x1_exp < 0.001 or x1_exp > 0.999:
            continue

        x = np.array([x1_exp, 1 - x1_exp])

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Predict temperature for the crystallizing component
                T_pred = solver.solve_T(x, index=component_index)

                if np.isnan(T_pred) or T_pred < 0:
                    total_error += 1e5
                else:
                    error = (T_exp - T_pred) ** 2
                    total_error += error
                    n_points += 1
        except:
            total_error += 1e5

    if n_points > 0:
        return total_error / n_points
    else:
        return 1e10


def objective_function_combined_curves(params, comp1, comp2, alpha12, left_curve, right_curve):
    """
    Objective function for fitting both liquidus curves simultaneously.

    Args:
        params: [g12, g21]
        comp1, comp2: Component objects
        alpha12: Fixed alpha parameter
        left_curve: DataFrame with left curve data (component 2 crystallizes)
        right_curve: DataFrame with right curve data (component 1 crystallizes)

    Returns:
        RMSE for both curves combined
    """
    g12, g21 = params

    nrtl_params = {"g12": g12, "g21": g21, "alpha12": alpha12}
    model = NRTL(nrtl_params)
    components = [comp1, comp2]
    sle_eq = SLEEquation(components, model)
    solver = SLESolver(sle_eq.residual, initial_guess=300.0)

    total_error = 0.0
    n_points = 0

    # Left curve: component 2 crystallizes (index=1)
    for _, row in left_curve.iterrows():
        x1_exp = row["x"]
        T_exp = row["T"]

        if x1_exp < 0.001 or x1_exp > 0.999:
            continue

        x = np.array([x1_exp, 1 - x1_exp])

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                T_pred = solver.solve_T(x, index=1)  # Component 2 crystallizes

                if not np.isnan(T_pred) and T_pred > 0:
                    error = (T_exp - T_pred) ** 2
                    total_error += error
                    n_points += 1
                else:
                    total_error += 1e5
        except:
            total_error += 1e5

    # Right curve: component 1 crystallizes (index=0)
    for _, row in right_curve.iterrows():
        x1_exp = row["x"]
        T_exp = row["T"]

        if x1_exp < 0.001 or x1_exp > 0.999:
            continue

        x = np.array([x1_exp, 1 - x1_exp])

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                T_pred = solver.solve_T(x, index=0)  # Component 1 crystallizes

                if not np.isnan(T_pred) and T_pred > 0:
                    error = (T_exp - T_pred) ** 2
                    total_error += error
                    n_points += 1
                else:
                    total_error += 1e5
        except:
            total_error += 1e5

    if n_points > 0:
        return total_error / n_points
    else:
        return 1e10
