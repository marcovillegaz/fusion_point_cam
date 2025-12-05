"""
Example: Calculate and Plot Binary SLE Phase Diagram
File: examples/plot_phase_diagram.py

This example calculates the solid-liquid equilibrium phase diagram
for a Choline Chloride - Urea deep eutectic solvent system.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# Import from your package
from des_sle.data.component import Component
from des_sle.models.nrtl import NRTL
from obsolete.sle_solver import SLESolver


# Configure matplotlib for better-looking plots
rcParams["font.size"] = 11
rcParams["font.family"] = "sans-serif"
rcParams["axes.linewidth"] = 1.5
rcParams["lines.linewidth"] = 2


def create_chcl_urea_system():
    """
    Create Choline Chloride - Urea DES system.

    Returns:
        Tuple of (components, nrtl_model, parameters)
    """
    # Define components with their properties
    chcl = Component(
        name="Choline Chloride",
        Tm=575.15,  # K (302°C)
        dHfus=4100,  # J/mol
        MW=139.62,  # g/mol
        formula="C5H14ClNO",
    )

    urea = Component(
        name="Urea",
        Tm=405.65,  # K (132.5°C)
        dHfus=14600,  # J/mol
        MW=60.06,  # g/mol
        formula="CH4N2O",
    )

    # Create NRTL model
    nrtl = NRTL()

    # NRTL parameters (example values - adjust based on literature or fitting)
    # Positive tau values typically indicate positive deviation from ideality
    params = {
        "tau12": 1.5,  # ChCl-Urea interaction
        "tau21": -0.8,  # Urea-ChCl interaction
        "alpha12": 0.3,  # Non-randomness parameter
    }

    return [chcl, urea], nrtl, params


def plot_phase_diagram(
    x1_array,
    T_comp1,
    T_comp2,
    components,
    x_eutectic=None,
    T_eutectic=None,
    show_individual_curves=True,
):
    """
    Create a professional phase diagram plot.

    Args:
        x1_array: Composition array (mole fraction of component 1)
        T_comp1: Liquidus temperatures for component 1 precipitation
        T_comp2: Liquidus temperatures for component 2 precipitation
        components: List of Component objects
        x_eutectic: Eutectic composition (optional)
        T_eutectic: Eutectic temperature (optional)
        show_individual_curves: Show both liquidus curves separately
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Get actual liquidus (minimum of both curves)
    T_liquidus = np.minimum(T_comp1, T_comp2)

    # Convert to Celsius for plotting
    T_comp1_C = T_comp1 - 273.15
    T_comp2_C = T_comp2 - 273.15
    T_liquidus_C = T_liquidus - 273.15

    if show_individual_curves:
        # Plot individual liquidus curves (dashed)
        ax.plot(
            x1_array,
            T_comp1_C,
            "--",
            color="#1f77b4",
            alpha=0.5,
            label=f"{components[0].name} liquidus",
            linewidth=1.5,
        )
        ax.plot(
            x1_array,
            T_comp2_C,
            "--",
            color="#ff7f0e",
            alpha=0.5,
            label=f"{components[1].name} liquidus",
            linewidth=1.5,
        )

    # Plot actual liquidus curve (solid, thick)
    ax.plot(
        x1_array, T_liquidus_C, "-", color="#2ca02c", linewidth=3, label="Liquidus curve", zorder=5
    )

    # Mark eutectic point if provided
    if x_eutectic is not None and T_eutectic is not None:
        T_eutectic_C = T_eutectic - 273.15
        ax.plot(
            x_eutectic,
            T_eutectic_C,
            "r*",
            markersize=20,
            label=f"Eutectic: x={x_eutectic:.3f}, T={T_eutectic_C:.1f}°C",
            zorder=10,
        )

        # Add horizontal and vertical lines to eutectic
        ax.axhline(T_eutectic_C, color="red", linestyle=":", alpha=0.3, linewidth=1)
        ax.axvline(x_eutectic, color="red", linestyle=":", alpha=0.3, linewidth=1)

    # Mark pure component melting points
    ax.plot(0, components[1].Tm - 273.15, "o", color="#ff7f0e", markersize=10, zorder=5)
    ax.plot(1, components[0].Tm - 273.15, "o", color="#1f77b4", markersize=10, zorder=5)

    # Labels and formatting
    ax.set_xlabel(f"Mole Fraction of {components[0].name}", fontsize=13, fontweight="bold")
    ax.set_ylabel("Temperature (°C)", fontsize=13, fontweight="bold")
    ax.set_title("Solid-Liquid Equilibrium Phase Diagram", fontsize=14, fontweight="bold", pad=20)

    # Set axis limits
    ax.set_xlim(0, 1)
    y_min = np.nanmin(T_liquidus_C) - 20
    y_max = max(components[0].Tm, components[1].Tm) - 273.15 + 20
    ax.set_ylim(y_min, y_max)

    # Grid
    ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

    # Legend
    ax.legend(loc="best", framealpha=0.95, fontsize=10)

    # Add annotations for phases
    mid_x = 0.5
    mid_y_top = y_max - 15
    ax.text(
        mid_x,
        mid_y_top,
        "Liquid",
        ha="center",
        va="top",
        fontsize=12,
        bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.7),
    )

    # Tight layout
    plt.tight_layout()

    return fig, ax


def main():
    """Main execution function"""

    print("=" * 70)
    print("Solid-Liquid Equilibrium Phase Diagram Calculation")
    print("=" * 70)

    # Step 1: Create the system
    print("\n1. Creating Choline Chloride - Urea system...")
    components, nrtl, params = create_chcl_urea_system()

    print(f"   Component 1: {components[0]}")
    print(f"   Component 2: {components[1]}")
    print(
        f"   NRTL Parameters: τ12={params['tau12']}, τ21={params['tau21']}, α12={params['alpha12']}"
    )

    # Step 2: Create SLE solver
    print("\n2. Initializing SLE solver...")
    solver = SLESolver(components, nrtl, params)
    print(f"   {solver}")

    # Step 3: Calculate phase diagram
    print("\n3. Calculating phase diagram...")
    print("   Computing liquidus temperatures across composition range...")

    x1_array, T_comp1, T_comp2 = solver.calculate_phase_diagram_binary(
        n_points=100, x_range=(0.01, 0.99)
    )

    print(f"   ✓ Calculated {len(x1_array)} points")

    # Step 4: Find eutectic point
    print("\n4. Finding eutectic point...")
    try:
        x_eutectic, T_eutectic = solver.find_eutectic_point_binary(
            x_guess=0.33, T_guess=250 + 273.15  # ChCl:Urea ≈ 1:2 molar ratio
        )

        print(f"   ✓ Eutectic composition: x_ChCl = {x_eutectic:.4f}")
        print(f"   ✓ Eutectic temperature: T = {T_eutectic:.2f} K ({T_eutectic-273.15:.2f}°C)")
        print(f"   ✓ Molar ratio ChCl:Urea ≈ 1:{(1-x_eutectic)/x_eutectic:.2f}")

    except Exception as e:
        print(f"   ⚠ Warning: Could not find eutectic point: {e}")
        x_eutectic, T_eutectic = None, None

    # Step 5: Create plot
    print("\n5. Creating phase diagram plot...")

    fig, ax = plot_phase_diagram(
        x1_array,
        T_comp1,
        T_comp2,
        components,
        x_eutectic=x_eutectic,
        T_eutectic=T_eutectic,
        show_individual_curves=True,
    )

    # Save plot
    output_file = "phase_diagram_ChCl_Urea.png"
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    print(f"   ✓ Plot saved as: {output_file}")

    # Show plot
    print("\n6. Displaying plot...")
    plt.show()

    # Step 6: Print summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    T_liquidus = np.minimum(T_comp1, T_comp2)
    T_min = np.nanmin(T_liquidus)
    T_max = np.nanmax(T_liquidus)

    print(f"Temperature range: {T_min-273.15:.2f}°C to {T_max-273.15:.2f}°C")
    print(
        f"Depression below pure components: {min(components[0].Tm, components[1].Tm) - T_min:.2f} K"
    )

    if x_eutectic is not None:
        depression = min(components[0].Tm, components[1].Tm) - T_eutectic
        print(f"Eutectic depression: {depression:.2f} K")

    print("\n✅ Phase diagram calculation complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
