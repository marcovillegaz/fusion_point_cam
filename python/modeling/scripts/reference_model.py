"""Test of solving the SLE equation"""

import numpy as np

# import io functions to work with experimental data
from des_sle.io.csv_loader import load_phase_diagram_csv
from des_sle.io.yaml_loader import load_mixture

# import thermodynamic model
from des_sle.thermo.nrtl import NRTL

# import sle equations and solver
from des_sle.sle.sle_solver import SLESolver
from des_sle.sle.sle_equation import SLEEquation

# import eutectic point finder
from des_sle.sle.eutectic_point import find_eutectic_point

# import plotting functions
from des_sle.plot.diagrams import plot_sle_diagram


# Load experimental data
x_solidus, T_solidus = load_phase_diagram_csv("data/reference_examples/solidus.csv")
x_liquidus, T_liquidus = load_phase_diagram_csv("data/reference_examples/liquidus.csv")

# Load mixture definition (e.g. Pe4NBr + Erythritol)
components, params = load_mixture("data/reference_examples/mixtures.yaml", "Pe4NBr_Erythritol")
# thermodynamic model isntance
model = NRTL(params)

# Intance of SLEEquation
sle_eq = SLEEquation(components, model)

# SLE Solver instance
solver = SLESolver(sle_eq, initial_guess=300)

# --- Compute model predictions ---
x_values = np.linspace(0.01, 0.99, 100)
T1, T2 = solver.compute_curve(x_values)
# --- Find eutectic point ---
x_e, T_e = find_eutectic_point(sle_eq)
print("Eutectic point:", x_e, T_e)

# crop curves at eutectic point
T1 = np.where(x_values >= x_e, T1, np.nan)
T2 = np.where(x_values <= x_e, T2, np.nan)

# --- Plot --- (make this a pipeline to add different elements to the plot)
# experimetnal data, model predictions, eutectic point

plot_sle_diagram(x_values, T1, T2, components, x_solidus, T_solidus, x_liquidus, T_liquidus)
