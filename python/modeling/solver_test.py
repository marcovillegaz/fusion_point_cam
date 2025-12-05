"""Test of solving the SLE equation"""

import numpy as np
import pandas as pd
from scipy.optimize import fsolve
import matplotlib.pyplot as plt


from des_sle.models.nrtl import NRTL
from des_sle.data.component import Component


# --- Load experimental data ---
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

R = 8.31446  # J/mol·K

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


# --- SLE equation ---
def sle_equation(T, x, components, model, index=0):
    # Ensure scalar T
    T = np.atleast_1d(T).item()

    # Compute activity coefficients (array)
    gamma = np.asarray(model.activity_coefficient(x, T), dtype=float)

    comp = components[index]

    # Compute equilibrium function value (scalar)
    val = np.log(x[index] * gamma[index]) + (comp.dHfus / R) * (1 / T - 1 / comp.Tm)

    # Return as a 1D NumPy array of floats
    return np.array([val], dtype=float)


# --- Compute SLE curve ---
x_values = np.linspace(0.01, 0.99, 50)
T_eq_1 = []
T_eq_2 = []

for x1 in x_values:
    x = [x1, 1 - x1]
    T_guess = 300

    try:
        # Component 1 solid in equilibrium
        T1 = fsolve(sle_equation, T_guess, args=(x, components, model, 0))[0]
        # Component 2 solid in equilibrium
        T2 = fsolve(sle_equation, T_guess, args=(x, components, model, 1))[0]
    except Exception:
        T1, T2 = np.nan, np.nan  # store NaN if solver fails

    T_eq_1.append(T1)
    T_eq_2.append(T2)

# --- Plot ---
plt.figure(figsize=(7, 5))

# Model predictions
plt.plot(x_values, T_eq_1, label=f"Model {components[0].name}")
plt.plot(x_values, T_eq_2, label=f"Model {components[1].name}")

# Experimental data
plt.scatter(x_solidus, T_solidus, color="red", marker=".", label="Solidus (exp.)")
plt.scatter(x_liquidus, T_liquidus, color="blue", marker=".", label="Liquidus (exp.)")

# Axes and formatting
plt.ylim(340, 400)
plt.xlim(0, 1)
plt.xlabel(f"Mole fraction of {components[0].name}")
plt.ylabel("Equilibrium temperature (K)")
plt.title("Solid–Liquid Equilibrium (NRTL model vs. experimental)")
plt.legend()
plt.grid(True)
plt.show()
