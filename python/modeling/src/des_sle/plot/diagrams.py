"""
Module for plotting solid-liquid equilibrium diagrams.
"""

import matplotlib.pyplot as plt


def plot_sle_diagram(
    x_values,
    T_eq_1,
    T_eq_2,
    components,
    x_solidus=None,
    T_solidus=None,
    x_liquidus=None,
    T_liquidus=None,
):
    """Plot solid-liquid equilibrium diagram with model predictions and experimental data.

    Args:
        x_values: Mole fraction values for model predictions
        T_eq_1: Equilibrium temperatures for component 1
        T_eq_2: Equilibrium temperatures for component 2
        components: List of Component objects
        x_solidus: Experimental solidus mole fractions (optional)
        T_solidus: Experimental solidus temperatures (optional)
        x_liquidus: Experimental liquidus mole fractions (optional)
        T_liquidus: Experimental liquidus temperatures (optional)
    """
    plt.figure(figsize=(7, 5))

    # Model predictions
    plt.plot(x_values, T_eq_1, label=f"Model {components[0].name}")
    plt.plot(x_values, T_eq_2, label=f"Model {components[1].name}")

    # Experimental data (if provided)
    if x_solidus is not None and T_solidus is not None:
        plt.scatter(x_solidus, T_solidus, color="red", marker=".", label="Solidus (exp.)")
    if x_liquidus is not None and T_liquidus is not None:
        plt.scatter(x_liquidus, T_liquidus, color="blue", marker=".", label="Liquidus (exp.)")

    # Axes and formatting
    # plt.ylim(340, 400)
    plt.xlim(0, 1)
    plt.xlabel(f"Mole fraction of {components[0].name}")
    plt.ylabel("Equilibrium temperature (K)")
    plt.title("Solid–Liquid Equilibrium (NRTL model vs. experimental)")
    plt.legend()
    plt.grid(True)
    plt.show()
