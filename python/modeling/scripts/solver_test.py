"""Test of solving the SLE equation"""

import numpy as np

from des_sle.io.csv_loader import load_phase_diagram_csv
from des_sle.io.yaml_loader import load_mixture

from des_sle.thermo.nrtl import NRTL

from des_sle.sle.sle_solver import SLESolver
from des_sle.sle.sle_equation import SLEEquation

from des_sle.plot.diagrams import plot_sle_diagram

# Load experimental data
x_solidus, T_solidus = load_phase_diagram_csv("examples/solidus.csv")
x_liquidus, T_liquidus = load_phase_diagram_csv("examples/liquidus.csv")

# Load mixture definition (e.g. Pe4NBr + Erythritol)
components, params = load_mixture("examples/data/mixtures.yaml", "Pe4NBr_PimelicAcid")

# thermodynamic model isntance
model = NRTL(params)

# Intance of SLEEquation
sle_eq = SLEEquation(components, model)

# SLE Solver instance
solver = SLESolver(sle_eq, initial_guess=300)

# --- Compute model predictions ---
x_values = np.linspace(0.01, 0.99, 50)
T1, T2 = solver.compute_curve(x_values)

# --- Plot ---
plot_sle_diagram(x_values, T1, T2, components, x_solidus, T_solidus, x_liquidus, T_liquidus)
