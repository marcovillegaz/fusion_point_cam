"""
Parameter optimization functions for NRTL fitting.
"""

import numpy as np
import warnings
from scipy.optimize import minimize, differential_evolution

from .objective_functions import objective_function_single_curve, objective_function_combined_curves


def fit_curve(
    comp1, comp2, alpha12, curve_data, component_index, method="differential_evolution", bounds=None
):
    """
    Fit NRTL parameters for a single liquidus curve.

    Args:
        comp1, comp2: Component objects
        alpha12: Fixed alpha parameter
        curve_data: DataFrame with curve data (columns: 'x', 'T')
        component_index: Which component is crystallizing (0 or 1)
        method: Optimization method ('differential_evolution', 'multi_start', or other scipy method)
        bounds: Parameter bounds for [g12, g21]. Default: [(-15000, 15000), (-15000, 15000)]

    Returns:
        Dictionary with optimized parameters and RMSE:
        {
            'g12': float,
            'g21': float,
            'rmse': float,
            'success': bool
        }
    """
    if bounds is None:
        bounds = [(-15000, 15000), (-15000, 15000)]

    def obj(params):
        return objective_function_single_curve(
            params, comp1, comp2, alpha12, curve_data, component_index
        )

    component_name = comp1.name if component_index == 0 else comp2.name
    print(f"\nFitting curve for {component_name} crystallization...")
    print(f"  Data points: {len(curve_data)}")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if method == "differential_evolution":
            result = differential_evolution(
                obj,
                bounds,
                strategy="best1bin",
                maxiter=2000,
                popsize=20,
                tol=0.001,
                mutation=(0.5, 1.5),
                recombination=0.7,
                seed=42,
                polish=True,
                disp=False,
            )
        elif method == "multi_start":
            best_result = None
            best_fun = np.inf

            for trial in range(15):
                x0 = [np.random.uniform(*bounds[0]), np.random.uniform(*bounds[1])]
                result = minimize(
                    obj, x0, method="L-BFGS-B", bounds=bounds, options={"maxiter": 1000}
                )

                if result.fun < best_fun:
                    best_fun = result.fun
                    best_result = result

            result = best_result
        else:
            x0 = [0, 0]
            result = minimize(obj, x0, method="L-BFGS-B", bounds=bounds, options={"maxiter": 1000})

    g12, g21 = result.x
    rmse = np.sqrt(result.fun)

    print(f"  Results: g12={g12:.2f} J/mol, g21={g21:.2f} J/mol, RMSE={rmse:.2f} K")

    return {
        "g12": g12,
        "g21": g21,
        "rmse": rmse,
        "success": result.success if hasattr(result, "success") else True,
    }


def weighted_average_parameters(left_result, right_result, left_curve, right_curve):
    """
    Combine parameters from both curves using weighted average based on number of points.

    Args:
        left_result: Results dictionary from left curve fitting
        right_result: Results dictionary from right curve fitting
        left_curve: Left curve DataFrame
        right_curve: Right curve DataFrame

    Returns:
        Dictionary with combined parameters:
        {
            'g12': float,
            'g21': float,
            'method': 'weighted_average',
            'left_weight': float,
            'right_weight': float
        }
    """
    n_left = len(left_curve)
    n_right = len(right_curve)
    total = n_left + n_right

    w_left = n_left / total
    w_right = n_right / total

    g12_combined = w_left * left_result["g12"] + w_right * right_result["g12"]
    g21_combined = w_left * left_result["g21"] + w_right * right_result["g21"]

    return {
        "g12": g12_combined,
        "g21": g21_combined,
        "method": "weighted_average",
        "left_weight": w_left,
        "right_weight": w_right,
    }


def optimize_combined_parameters(
    comp1, comp2, alpha12, left_curve, right_curve, initial_params, bounds=None
):
    """
    Optimize parameters using both curves simultaneously but with curve-specific predictions.

    Args:
        comp1, comp2: Component objects
        alpha12: Fixed alpha parameter
        left_curve: Left curve DataFrame (component 2 crystallizes)
        right_curve: Right curve DataFrame (component 1 crystallizes)
        initial_params: Initial guess [g12, g21]
        bounds: Parameter bounds. Default: [(-15000, 15000), (-15000, 15000)]

    Returns:
        Dictionary with optimized parameters:
        {
            'g12': float,
            'g21': float,
            'rmse': float,
            'method': 'combined_optimization'
        }
    """
    if bounds is None:
        bounds = [(-15000, 15000), (-15000, 15000)]

    def obj(params):
        return objective_function_combined_curves(
            params, comp1, comp2, alpha12, left_curve, right_curve
        )

    print("\nOptimizing combined parameters with curve-specific predictions...")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        result = minimize(
            obj,
            initial_params,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 2000, "disp": False},
        )

    g12, g21 = result.x
    rmse = np.sqrt(result.fun)

    print(f"  Results: g12={g12:.2f} J/mol, g21={g21:.2f} J/mol, RMSE={rmse:.2f} K")

    return {"g12": g12, "g21": g21, "rmse": rmse, "method": "combined_optimization"}
