"""Test of solving the SLE equation"""

import numpy as np
import pandas as pd

from des_sle.models.nrtl import NRTL
from des_sle.data.component import Component
from des_sle.plot.diagrams import plot_sle_diagram

from des_sle.solver.sle_solver import SLESolver
from des_sle.solver.sle_equation import SLEEquation

# Load experimental data
solidus_data = pd.read_csv("examples/solidus.csv", sep=";", decimal=",")
liquidus_data = pd.read_csv("examples/liquidus.csv", sep=";", decimal=",")

# Convert temperatures from °C to K
solidus_data["T"] = solidus_data["T"] + 273.15
liquidus_data["T"] = liquidus_data["T"] + 273.15

print(liquidus_data)
print(solidus_data)

# Each CSV must have two columns: "x" and "T"
x_solidus = solidus_data["x"].values
T_solidus = solidus_data["T"].values

x_liquidus = liquidus_data["x"].values
T_liquidus = liquidus_data["T"].values


# Define components with their properties
Pe4NBr = Component(
    name="Pe4NBr",
    Tm=373.2,  # K
    dHfus=41.45 * 1000,  # J/mol
    MW=378.47,  # g/mol
    formula="[CH3(CH2)4]4N(Br)",
)

erythritol = Component(
    name="Erythritol",
    Tm=392.2,  # K
    dHfus=39.40 * 1000,  # J/mol
    MW=122.12,  # g/mol
    formula="C4H10O4",
)

# Pe4NBr with erythritol (ET)
params = {
    "g12": -1567.0,
    "g21": -4735.4,
    "alpha12": 0.3,  # Non-randomness parameter
}

# thermodynamic model isntance
model = NRTL(params)
components = [Pe4NBr, erythritol]

# Intance of SLEEquation
sle_eq = SLEEquation(components, model)

# SLE Solver instance
solver = SLESolver(sle_eq, initial_guess=300)

# --- Compute model predictions ---
x_values = np.linspace(0.01, 0.99, 50)
T1, T2 = solver.compute_curve(x_values)

# --- Plot ---
plot_sle_diagram(x_values, T1, T2, components, x_solidus, T_solidus, x_liquidus, T_liquidus)
