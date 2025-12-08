"""
NRTL Parameter Fitting by Separate Liquidus Curves

This script uses pre-split experimental data for left and right liquidus curves.
Each curve is fitted independently because:
- Left of eutectic: Component 2 crystallizes (controlled by component 2)
- Right of eutectic: Component 1 crystallizes (controlled by component 1)

Input files (in data/experimental_split/):
- liquidus_left.csv: Left curve (component 2 crystallizes)
- liquidus_right.csv: Right curve (component 1 crystallizes)

Usage:
    python fit_nrtl_by_curves.py
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from des_sle.data.component import Component
from des_sle.thermo.nrtl import NRTL
from des_sle.sle.sle_equation import SLEEquation
from des_sle.sle.sle_solver import SLESolver
from des_sle.sle.eutectic_point import find_eutectic_point
from des_sle.plot.diagrams import plot_sle_diagram
from des_sle.io.csv_loader import (
    load_liquidus_curve_csv,
    find_eutectic_from_data,
    load_eutectic_info,
)
from des_sle.io.yaml_loader import save_fitted_parameters
from des_sle.fitting.optimizer import (
    fit_curve,
    weighted_average_parameters,
    optimize_combined_parameters,
)


def main():
    """Main function."""
    print("=" * 70)
    print("NRTL FITTING BY SEPARATE LIQUIDUS CURVES")
    print("=" * 70)

    # Define components
    comp1 = Component(name="Component1", Tm=373.2, dHfus=41450)
    comp2 = Component(name="Component2", Tm=392.2, dHfus=39400)
    alpha12 = 0.3

    print(f"\nComponents:")
    print(f"  {comp1}")
    print(f"  {comp2}")
    print(f"  Alpha12: {alpha12}")

    # Load pre-split experimental data
    print("Loading pre-split experimental data...")
    base_path = Path(__file__).parent.parent / "data" / "experimental_split"

    # Load curves using package function
    left_curve = load_liquidus_curve_csv(base_path / "liquidus_left.csv")
    right_curve = load_liquidus_curve_csv(base_path / "liquidus_right.csv")

    # Determine eutectic point
    eutectic_info = load_eutectic_info(base_path / "eutectic_info.txt")
    if eutectic_info is not None:
        x_eutectic, T_eutectic = eutectic_info
        print(f"\nEutectic info loaded from file.")
    else:
        x_eutectic, T_eutectic = find_eutectic_from_data(left_curve, right_curve)
        print(f"\nEutectic point determined from data.")

    print(f"\n{'='*70}")
    print(f"EUTECTIC POINT")
    print(f"{'='*70}")
    print(f"  x_eutectic = {x_eutectic:.4f}")
    print(f"  T_eutectic = {T_eutectic:.2f} K ({T_eutectic-273.15:.2f} °C)")
    print(f"\nCurves loaded:")
    print(f"  Left curve (comp 2 crystallizes): {len(left_curve)} points")
    print(f"  Right curve (comp 1 crystallizes): {len(right_curve)} points")

    # Fit each curve independently
    print(f"\n{'='*70}")
    print(f"FITTING INDIVIDUAL CURVES")
    print(f"{'='*70}")

    bounds = [(-15000, 15000), (-15000, 15000)]

    # Left curve: component 2 crystallizes
    left_result = fit_curve(
        comp1,
        comp2,
        alpha12,
        left_curve,
        component_index=1,
        method="differential_evolution",
        bounds=bounds,
    )

    # Right curve: component 1 crystallizes
    right_result = fit_curve(
        comp1,
        comp2,
        alpha12,
        right_curve,
        component_index=0,
        method="differential_evolution",
        bounds=bounds,
    )

    # Combine parameters
    print(f"\n{'='*70}")
    print(f"COMBINING PARAMETERS")
    print(f"{'='*70}")

    # Method 1: Weighted average
    weighted_params = weighted_average_parameters(
        left_result, right_result, left_curve, right_curve
    )
    print(f"\nWeighted Average:")
    print(f"  g12 = {weighted_params['g12']:.2f} J/mol")
    print(f"  g21 = {weighted_params['g21']:.2f} J/mol")
    print(
        f"  Weights: left={weighted_params['left_weight']:.2f}, right={weighted_params['right_weight']:.2f}"
    )

    # Method 2: Optimize combined
    initial_guess = [weighted_params["g12"], weighted_params["g21"]]
    combined_params = optimize_combined_parameters(
        comp1, comp2, alpha12, left_curve, right_curve, initial_guess, bounds
    )

    # Compare all methods
    print(f"\n{'='*70}")
    print(f"SUMMARY OF ALL METHODS")
    print(f"{'='*70}")

    results_summary = {
        "Left Curve Only": {
            "g12": left_result["g12"],
            "g21": left_result["g21"],
            "rmse": left_result["rmse"],
        },
        "Right Curve Only": {
            "g12": right_result["g12"],
            "g21": right_result["g21"],
            "rmse": right_result["rmse"],
        },
        "Weighted Average": {
            "g12": weighted_params["g12"],
            "g21": weighted_params["g21"],
            "rmse": None,
        },
        "Combined Optimization": combined_params,
    }

    for method, params in results_summary.items():
        print(f"\n{method}:")
        print(f"  g12  = {params['g12']:.2f} J/mol")
        print(f"  g21  = {params['g21']:.2f} J/mol")
        if params.get("rmse"):
            print(f"  RMSE = {params['rmse']:.2f} K")

    # Plot results using modular plot_sle_diagram
    print(f"\nGenerating comparison plots...")

    for method_name, params in results_summary.items():
        print(f"  Plotting {method_name}...")

        # Create NRTL model with current parameters
        nrtl_params = {"g12": params["g12"], "g21": params["g21"], "alpha12": alpha12}
        model = NRTL(nrtl_params)
        components = [comp1, comp2]
        sle_eq = SLEEquation(components, model)
        solver = SLESolver(sle_eq.residual, initial_guess=300.0)

        # Generate prediction curves
        x_range = np.linspace(0.001, 0.999, 100)
        T1, T2 = solver.compute_curve(x_range)

        # Find eutectic point
        x_e, T_e = find_eutectic_point(sle_eq)
        print(f"    Eutectic point: x={x_e:.4f}, T={T_e:.2f} K")

        # Combine experimental data
        x_liquidus = np.concatenate([left_curve["x"].values, right_curve["x"].values])
        T_liquidus = np.concatenate([left_curve["T"].values, right_curve["T"].values])

        # Crop curves at eutectic point
        T1 = np.where(x_range >= x_e, T1, np.nan)
        T2 = np.where(x_range <= x_e, T2, np.nan)

        # Use modular plot_sle_diagram function
        plot_sle_diagram(
            x_values=x_range,
            T_eq_1=T1,
            T_eq_2=T2,
            components=components,
            x_liquidus=x_liquidus,
            T_liquidus=T_liquidus,
        )

        """ # Add title with method and parameters
        rmse_text = f" - RMSE = {params['rmse']:.2f} K" if params.get("rmse") else ""
        plt.gcf().suptitle(
            f"{method_name}{rmse_text}\n"
            f"g₁₂={params['g12']:.1f} J/mol, g₂₁={params['g21']:.1f} J/mol, α₁₂={alpha12:.3f}",
            fontsize=11,
            y=0.98,
        )
        plt.tight_layout()
        plt.show() """

    # Save best parameters
    best_params = combined_params
    output_path = (
        Path(__file__).parent.parent / "data" / "fitting" / "fitted_parameters_by_curves.yaml"
    )

    fitting_info = {
        "method": "separate_curves_then_combined",
        "rmse_K": float(best_params["rmse"]),
        "eutectic_point": {"x": float(x_eutectic), "T_K": float(T_eutectic)},
        "left_curve_points": len(left_curve),
        "right_curve_points": len(right_curve),
    }

    nrtl_params = {
        "g12": best_params["g12"],
        "g21": best_params["g21"],
        "alpha12": alpha12,
    }

    save_fitted_parameters(
        filepath=output_path,
        mixture_name="Fitted_By_Curves",
        components=[comp1, comp2],
        nrtl_params=nrtl_params,
        fitting_info=fitting_info,
    )

    print(f"\nParameters saved to: {output_path}")

    print(f"\n{'='*70}")
    print(f"FITTING COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
