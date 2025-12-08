# Deep Eutectic Solvent SLE Modeling Package

A Python package for modeling solid-liquid equilibria in binary systems using the NRTL activity coefficient model.

## Package Structure

```
src/des_sle/
├── __init__.py
├── data/
│   ├── __init__.py
│   └── component.py           # Component class with pure properties
├── thermo/
│   ├── __init__.py
│   ├── activity_model.py      # Abstract base class for activity models
│   └── nrtl.py                # NRTL implementation
├── sle/
│   ├── __init__.py
│   ├── sle_equation.py        # SLE equilibrium equations
│   ├── sle_solver.py          # Numerical solver
│   └── eutectic_point.py      # Eutectic point detection
├── fitting/                   # NEW: Parameter optimization module
│   ├── __init__.py
│   ├── objective_functions.py # Objective functions for fitting
│   └── optimizer.py           # Optimization algorithms
├── io/                        # ENHANCED: Data loading/saving
│   ├── __init__.py
│   ├── csv_loader.py          # CSV data loading & processing
│   └── yaml_loader.py         # YAML parameter loading/saving
└── plot/
    ├── __init__.py
    └── diagrams.py            # Phase diagram plotting

scripts/
├── split_liquidus_data.py     # Split experimental data at eutectic
├── fit_nrtl_by_curves.py      # Curve-by-curve parameter fitting
└── verify_nrtl_params.py      # Parameter verification

data/
├── reference_examples/        # Original experimental data
├── experimental_split/        # Pre-split curves for fitting
└── fitting/                   # Fitted parameters output
```

## Installation

```bash
# Clone the repository
git clone https://github.com/marcovillegaz/fusion_point_cam.git
cd fusion_point_cam/python/modeling

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install package
pip install -e .
```

## Quick Start

### 1. Define Components and Model

```python
from des_sle import Component, NRTL, SLEEquation, SLESolver
import numpy as np

# Define binary components
comp1 = Component(name="Pe4NBr", Tm=373.2, dHfus=41450)
comp2 = Component(name="Component2", Tm=392.2, dHfus=39400)

# NRTL parameters
nrtl_params = {"g12": -1089.34, "g21": 7234.56, "alpha12": 0.3}
model = NRTL(nrtl_params)

# Create SLE solver
components = [comp1, comp2]
sle_eq = SLEEquation(components, model)
solver = SLESolver(sle_eq.residual, initial_guess=300.0)

# Calculate liquidus temperature at x=0.5
x = np.array([0.5, 0.5])
T = solver.solve_T(x, index=0)  # Component 1 crystallizes
print(f"Liquidus temperature: {T:.2f} K")
```

### 2. Fit NRTL Parameters from Data

```bash
# Step 1: Split your experimental data at eutectic point
python scripts/split_liquidus_data.py

# Step 2: Fit NRTL parameters using curve-by-curve method
python scripts/fit_nrtl_by_curves.py

# Step 3: Verify fitted parameters
python scripts/verify_nrtl_params.py
```

## Key Features

### Modular Design
- **data**: Component properties management
- **thermo**: Activity coefficient models (NRTL, extensible to Wilson, UNIQUAC)
- **sle**: SLE equation solving and eutectic point detection
- **fitting**: Parameter optimization with multiple algorithms
- **io**: Flexible data loading/saving (CSV, YAML)
- **plot**: Publication-quality phase diagrams

### Advanced Fitting Methodology
- **Curve-by-curve fitting**: Accounts for different crystallizing components
- **Multiple optimization methods**: Differential evolution, multi-start, basin hopping
- **Weighted parameter combination**: Based on data point distribution
- **Comprehensive validation**: RMSE, MAE, residual analysis

## Component Class
Stores pure component thermodynamic properties:
- `name`: Component identifier
- `Tm`: Melting temperature [K]
- `dHfus`: Enthalpy of fusion [J/mol]
- `dCp`: Heat capacity difference [J/mol·K] (optional, default 0)

## Activity Model Classes

### Base Class: `ActivityModel`
Abstract base class for all activity coefficient models

### NRTL Model
Non-Random Two-Liquid model for activity coefficients





# Theory 
In modelling solid liquid equilibrium the fugacity of the component in both phase must be equal: 

$$
f_{i}^{L} = a_{i}^{L} f_{i}^{L,o}
$$

For pure solid, eg. The component I precipitates as a pure solid, its fugacity is simple the fugacity of the pure solid. 

The fugacity of the component in the liquid phase is expressed using the concept of activity

$$
f_{i}^{L} = a_{i}^{L} f_{i}^{L,o}
$$

Where f_{i}^{L,o} is the fugacity of the pure liquid component I at the system T and P.
The activity of the liquid is related to the mole fraction x_{i} and the activity coefficient \alpha_{i}

$$
a_{i}^{L} = x_{i} \alpha_{i}
$$
Substituying this into the fugacity equilibrium equation and rearranging for the moalr fraction

$$
x_{i} \alpha_{i} = \frac{f_{i}^{S}}{f_{i}^{L,o}} = a_{i}^{fusion}
$$

the ratio a_{i}^{fusion} is the ideal solubility factor, which depends only on temperature and the pure component’s melting properties (melting point, heat of fusion and heat capacity difference). 

$$
\ln(x_i \, \gamma_i) = -\frac{\Delta H_{\text{fus},i}}{R} \left( \frac{1}{T} - \frac{1}{T_{m,i}} \right) 
+ \frac{\Delta C_{p,i}}{R} \left( \frac{T_{m,i}}{T} - 1 - \ln\!\left(\frac{T_{m,i}}{T}\right) \right)
$$


In the equation above, the activity coefficient can be estimated using activity models such a NRTL. This terms describes the interaction between the solid solute and the liquid solvent in the liquid phase. 

In most practical cases the phase is ideal. The precipitating solid is assumed to be pure (or forms and ideal solid solution), meaning its behavior is fixed by its own properties and is independent of the liquid mixture composition

The liquid phase is non ideal. The NRTL model is an excess Gibbs energy model, which is specifically designe to compute the activity coefficients that quantifies non-ideal mixing effects. 

Since the non ideality of the total SLE siytem is entirely contained within the \alpha_{i} term for the liquid phase, any reliable activity coefficient model, including those developes for LLE or VLE, can be use for SLE modelling. 




