# DES-SLE: Deep Eutectic Solvent Solid-Liquid Equilibria Modeling

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python package for modeling solid-liquid equilibria (SLE) in binary systems, with emphasis on deep eutectic solvents (DES) and eutectic mixtures. This tool enables thermodynamic modeling, NRTL parameter fitting from experimental data, and phase diagram generation for scientific research and engineering applications.

---

## Table of Contents

1. [Overview](#overview)
2. [Theoretical Background](#theoretical-background)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Usage](#usage)
   - [Quick Start](#quick-start)
   - [Parameter Fitting Workflow](#parameter-fitting-workflow)
   - [Verification and Validation](#verification-and-validation)
6. [Methodology](#methodology)
7. [Examples](#examples)
8. [API Reference](#api-reference)
9. [Citation](#citation)
10. [Contributing](#contributing)
11. [License](#license)

---

## Overview

**DES-SLE** is a modular Python framework designed for:

- **Thermodynamic modeling** of solid-liquid equilibria using activity coefficient models (NRTL)
- **NRTL parameter fitting** from experimental liquidus data using advanced optimization algorithms
- **Phase diagram generation** including eutectic point identification
- **Model validation** against experimental data with comprehensive error analysis
- **Curve-by-curve fitting** methodology for improved accuracy in eutectic systems

This package was developed to support research on deep eutectic solvents and is suitable for publication-quality results in scientific journals.

### Key Features

- ✅ **NRTL activity coefficient model** implementation
- ✅ **Multiple optimization methods**: Differential evolution, basin hopping, multi-start local optimization
- ✅ **Eutectic-aware fitting**: Separate curve fitting for left and right branches
- ✅ **Modular architecture**: Easy to extend with additional activity models (Wilson, UNIQUAC)
- ✅ **Comprehensive validation tools**: RMSE, MAE, error statistics, and diagnostic plots
- ✅ **YAML-based data management**: Reproducible parameter storage
- ✅ **Publication-ready visualizations**: Using standardized plotting functions

---

## Theoretical Background

### Solid-Liquid Equilibrium Fundamentals

In solid-liquid equilibrium modeling, the fugacity of component *i* in both phases must be equal:

$$
f_i^S = f_i^L
$$

The fugacity of the component in the liquid phase is expressed using the concept of activity:

$$
f_i^L = a_i^L f_i^{L,o} = x_i \gamma_i f_i^{L,o}
$$

where:
- $x_i$ is the mole fraction of component *i*
- $\gamma_i$ is the activity coefficient (accounts for non-ideal mixing)
- $f_i^{L,o}$ is the fugacity of pure liquid component *i*

For a pure solid precipitating from solution, the equilibrium condition becomes:

$$
x_i \gamma_i = \frac{f_i^S}{f_i^{L,o}} = a_i^{\text{fusion}}
$$

The ideal solubility factor $a_i^{\text{fusion}}$ depends only on temperature and pure component properties:

$$
\ln(x_i \gamma_i) = -\frac{\Delta H_{\text{fus},i}}{R} \left( \frac{1}{T} - \frac{1}{T_{m,i}} \right) + \frac{\Delta C_{p,i}}{R} \left( \frac{T_{m,i}}{T} - 1 - \ln\left(\frac{T_{m,i}}{T}\right) \right)
$$

where:
- $\Delta H_{\text{fus},i}$ = enthalpy of fusion (J/mol)
- $T_{m,i}$ = melting temperature (K)
- $\Delta C_{p,i}$ = heat capacity difference between liquid and solid
- $R$ = universal gas constant (8.314 J/mol·K)

**Note**: In most practical applications, $\Delta C_{p,i}$ is neglected or set to zero.

### NRTL Activity Coefficient Model

The Non-Random Two-Liquid (NRTL) model calculates activity coefficients for non-ideal liquid mixtures. For a binary system:

$$
\ln \gamma_1 = x_2^2 \left[ \tau_{21} \left( \frac{G_{21}}{x_1 + x_2 G_{21}} \right)^2 + \frac{\tau_{12} G_{12}}{(x_2 + x_1 G_{12})^2} \right]
$$

$$
\ln \gamma_2 = x_1^2 \left[ \tau_{12} \left( \frac{G_{12}}{x_2 + x_1 G_{12}} \right)^2 + \frac{\tau_{21} G_{21}}{(x_1 + x_2 G_{21})^2} \right]
$$

where:
- $\tau_{ij} = \frac{g_{ij}}{RT}$ (energy parameters)
- $G_{ij} = \exp(-\alpha_{ij} \tau_{ij})$
- $g_{ij}$ = binary interaction energy parameters (J/mol)
- $\alpha_{ij}$ = non-randomness parameter (typically 0.2–0.47, often fixed at 0.3)

### Phase Behavior in Eutectic Systems

In binary eutectic systems, the liquidus curve consists of two distinct branches:

1. **Left branch** ($x < x_{\text{eutectic}}$): Component 2 crystallizes (solid phase = pure component 2)
2. **Right branch** ($x > x_{\text{eutectic}}$): Component 1 crystallizes (solid phase = pure component 1)

At the **eutectic point** ($x_{\text{eutectic}}, T_{\text{eutectic}}$), both components crystallize simultaneously.

**Critical Insight**: Each branch must be fitted with the appropriate component index to correctly predict which solid phase is in equilibrium with the liquid.

---

## Installation

### Requirements

- Python ≥ 3.8
- NumPy ≥ 1.21.0
- SciPy ≥ 1.7.0
- pandas ≥ 1.3.0
- matplotlib ≥ 3.4.0
- PyYAML

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/marcovillegaz/fusion_point_cam.git
   cd fusion_point_cam/python/modeling
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies (optional):**
   ```bash
   pip install -e ".[dev]"
   ```

---

## Project Structure

```
des-sle/
├── src/
│   └── des_sle/
│       ├── __init__.py
│       ├── data/
│       │   ├── __init__.py
│       │   └── component.py         # Component class with pure properties
│       ├── thermo/
│       │   ├── __init__.py
│       │   ├── activity_model.py    # Base class for activity models
│       │   ├── nrtl.py              # NRTL model implementation
│       │   └── README.md            # Thermodynamic models documentation
│       ├── sle/
│       │   ├── __init__.py
│       │   ├── sle_equation.py      # SLE equilibrium equations
│       │   ├── sle_solver.py        # Numerical solver for T or x
│       │   └── eutectic_point.py    # Eutectic point detection
│       ├── fitting/                 # Parameter optimization module
│       │   ├── __init__.py
│       │   ├── objective_functions.py # Objective functions for fitting
│       │   └── optimizer.py         # Optimization algorithms
│       ├── io/                      # Data loading/saving module
│       │   ├── __init__.py
│       │   ├── yaml_loader.py       # YAML data loading & saving
│       │   └── csv_loader.py        # CSV data loading & processing
│       └── plot/
│           ├── __init__.py
│           └── diagrams.py          # Phase diagram plotting
├── scripts/
│   ├── split_liquidus_data.py       # Split experimental data at eutectic
│   ├── fit_nrtl_by_curves.py        # Main fitting script (curve-by-curve)
│   ├── verify_nrtl_params.py        # Validation script
│   └── README_NRTL_FITTING.md       # Detailed usage documentation
├── data/
│   ├── reference_examples/
│   │   ├── liquidus.csv             # Experimental liquidus data
│   │   └── solidus.csv              # Experimental solidus data (optional)
│   ├── experimental_split/
│   │   ├── liquidus_left.csv        # Left branch (comp 2 crystallizes)
│   │   ├── liquidus_right.csv       # Right branch (comp 1 crystallizes)
│   │   └── eutectic_info.txt        # Eutectic point coordinates
│   └── fitting/
│       └── fitted_parameters_by_curves.yaml  # Output from fitting
├── tests/
│   ├── test_component.py
│   ├── test_nrtl.py
│   ├── test_sle_solver.py
│   └── integration/
│       └── test_full_workflow.py
├── REFACTORING_SUMMARY.md          # Details of package refactoring
├── pyproject.toml
├── requirements.txt
├── README.md                        # Quick start guide
└── README_PUBLICATION.md            # This file (comprehensive documentation)
```

---

## Usage

### Quick Start

#### 1. Define Components and Create Phase Diagram

```python
from des_sle.data.component import Component
from des_sle.thermo.nrtl import NRTL
from des_sle.sle.sle_equation import SLEEquation
from des_sle.sle.sle_solver import SLESolver
from des_sle.plot.diagrams import plot_sle_diagram
import numpy as np

# Define binary components
comp1 = Component(name="Pe4NBr", Tm=373.2, dHfus=41450)
comp2 = Component(name="LauricAcid", Tm=392.2, dHfus=39400)

# NRTL parameters (from fitting or literature)
nrtl_params = {"g12": 5234.5, "g21": -8765.3, "alpha12": 0.3}
model = NRTL(nrtl_params)

# Create SLE equation and solver
components = [comp1, comp2]
sle_eq = SLEEquation(components, model)
solver = SLESolver(sle_eq.residual, initial_guess=300.0)

# Generate phase diagram
x_range = np.linspace(0.001, 0.999, 100)
T_eq_1, T_eq_2 = [], []

for x1 in x_range:
    x = np.array([x1, 1 - x1])
    T_eq_1.append(solver.solve_T(x, index=0))
    T_eq_2.append(solver.solve_T(x, index=1))

# Plot
plot_sle_diagram(x_range, T_eq_1, T_eq_2, components)
```

### Parameter Fitting Workflow

#### Step 1: Prepare Experimental Data

Create CSV files with semicolon delimiter and comma as decimal separator (European format):

**liquidus.csv:**
```csv
x;T
0.0;119.05
0.1;95.2
0.2;80.3
...
```

Place in `data/reference_examples/`

#### Step 2: Split Data at Eutectic Point

```bash
python scripts/split_liquidus_data.py
```

This creates:
- `data/experimental_split/liquidus_left.csv`
- `data/experimental_split/liquidus_right.csv`
- `data/experimental_split/eutectic_info.txt`

#### Step 3: Fit NRTL Parameters

```bash
python scripts/fit_nrtl_by_curves.py
```

This script:
1. Loads pre-split experimental curves
2. Fits left curve (component 2 crystallizes) independently
3. Fits right curve (component 1 crystallizes) independently
4. Combines parameters using weighted average and joint optimization
5. Generates comparison plots for all methods
6. Saves best parameters to YAML

**Output:**
```
NRTL FITTING BY SEPARATE LIQUIDUS CURVES
======================================================================

Components:
  Component(name='Pe4NBr', Tm=373.2 K, dHfus=41450 J/mol)
  Component(name='Component2', Tm=392.2 K, dHfus=39400 J/mol)
  Alpha12: 0.3

Loading pre-split experimental data...

EUTECTIC POINT
======================================================================
  x_eutectic = 0.5940
  T_eutectic = 342.00 K (68.85 °C)

Curves loaded:
  Left curve (comp 2 crystallizes): 31 points
  Right curve (comp 1 crystallizes): 16 points

FITTING INDIVIDUAL CURVES
======================================================================

Fitting curve for Component2 crystallization...
  Data points: 31
  Results: g12=-1234.56 J/mol, g21=7890.12 J/mol, RMSE=1.85 K

Fitting curve for Pe4NBr crystallization...
  Data points: 16
  Results: g12=-987.65 J/mol, g21=6543.21 J/mol, RMSE=2.12 K

COMBINING PARAMETERS
======================================================================

Weighted Average:
  g12 = -1150.23 J/mol
  g21 = 7456.89 J/mol
  Weights: left=0.66, right=0.34

Optimizing combined parameters with curve-specific predictions...
  Results: g12=-1089.34 J/mol, g21=7234.56 J/mol, RMSE=2.33 K

SUMMARY OF ALL METHODS
======================================================================

Left Curve Only:
  g12  = -1234.56 J/mol
  g21  = 7890.12 J/mol
  RMSE = 1.85 K

Right Curve Only:
  g12  = -987.65 J/mol
  g21  = 6543.21 J/mol
  RMSE = 2.12 K

Weighted Average:
  g12  = -1150.23 J/mol
  g21  = 7456.89 J/mol

Combined Optimization:
  g12  = -1089.34 J/mol
  g21  = 7234.56 J/mol
  RMSE = 2.33 K

Parameters saved to: data/fitted_parameters_by_curves.yaml

FITTING COMPLETE
======================================================================
```

### Verification and Validation

Verify fitted parameters against experimental data:

```bash
python scripts/verify_nrtl_params.py
```

This generates:
- Error statistics (RMSE, MAE, mean error, max error)
- Two-panel diagnostic plots comparing model vs. experiment

---

## Methodology

### Curve-by-Curve Fitting Approach

**Problem**: Traditional full-curve fitting treats the entire liquidus as a single dataset, but this is thermodynamically incorrect for eutectic systems.

**Solution**: Split liquidus at eutectic point and fit each branch separately with the correct crystallizing component index.

#### Algorithm:

1. **Identify eutectic point**: Find minimum temperature in liquidus data
2. **Split curves**:
   - Left: $x \leq x_{\text{eutectic}}$ → Component 2 crystallizes (index=1)
   - Right: $x \geq x_{\text{eutectic}}$ → Component 1 crystallizes (index=0)
3. **Fit independently**: Use differential evolution for each curve
4. **Combine parameters**:
   - Weighted average based on number of data points
   - Joint optimization using both curves simultaneously

#### Objective Function:

For each curve:

$$
\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (T_{\text{exp},i} - T_{\text{pred},i})^2}
$$

where $T_{\text{pred},i}$ is calculated using the appropriate component index for that curve.

### Optimization Methods

1. **Differential Evolution** (default, recommended)
   - Global optimization algorithm
   - Population-based evolutionary strategy
   - Best for non-convex parameter spaces
   - Settings: `maxiter=2000`, `popsize=20`, `strategy='best1bin'`

2. **Multi-Start Local Optimization**
   - Multiple L-BFGS-B runs from random initial points
   - Good for smooth objective functions
   - 15 trials by default

3. **Basin Hopping**
   - Global optimization with local refinement
   - Good balance between exploration and exploitation

4. **Dual Annealing**
   - Simulated annealing variant
   - Effective for rugged landscapes

5. **SHGO (Simplicial Homology Global Optimization)**
   - Deterministic global optimization
   - Guarantees finding global minimum (with sufficient resources)

---

## Examples

### Example 1: Fit and Validate

```python
# 1. Split your experimental data
# Place liquidus.csv in data/reference_examples/
# Run: python scripts/split_liquidus_data.py

# 2. Fit NRTL parameters
# Run: python scripts/fit_nrtl_by_curves.py

# 3. Verify results
# Run: python scripts/verify_nrtl_params.py
```

### 2. Fit NRTL Parameters from Data

The package provides a modular fitting workflow through the `des_sle.fitting` module:

```python
from des_sle.io.csv_loader import load_liquidus_curve_csv
from des_sle.fitting.optimizer import fit_curve
from des_sle.data.component import Component

# Define components
comp1 = Component(name="Pe4NBr", Tm=373.2, dHfus=41450)
comp2 = Component(name="Component2", Tm=392.2, dHfus=39400)

# Load curve data
left_curve = load_liquidus_curve_csv("data/experimental_split/liquidus_left.csv")

# Fit parameters for left curve (component 2 crystallizes)
result = fit_curve(
    comp1, comp2, 
    alpha12=0.3,
    curve_data=left_curve,
    component_index=1,  # Component 2 crystallizes
    method="differential_evolution",
    bounds=[(-15000, 15000), (-15000, 15000)]
)

print(f"Fitted parameters: g12={result['g12']:.2f}, g21={result['g21']:.2f}")
print(f"RMSE: {result['rmse']:.2f} K")
```

### 3. Use Fitted Parameters

```python
from des_sle.io.yaml_loader import load_mixture

# Load fitted parameters
components, nrtl_params = load_mixture(
    "data/fitting/fitted_parameters_by_curves.yaml",
    "Fitted_By_Curves"
)

comp1, comp2 = components
print(f"NRTL Parameters:")
print(f"  g12 = {nrtl_params['g12']:.2f} J/mol")
print(f"  g21 = {nrtl_params['g21']:.2f} J/mol")
print(f"  α12 = {nrtl_params['alpha12']:.3f}")
```

---

## API Reference

### Core Classes

#### `Component`
```python
Component(name: str, Tm: float, dHfus: float, dCp: float = 0.0)
```
- `name`: Component identifier
- `Tm`: Melting temperature (K)
- `dHfus`: Enthalpy of fusion (J/mol)
- `dCp`: Heat capacity difference (J/mol·K), default 0

#### `NRTL`
```python
NRTL(params: dict)
```
- `params`: Dictionary with keys `g12`, `g21`, `alpha12`
- Methods:
  - `activity_coefficient(x, T)`: Calculate γ₁ and γ₂

**Example:**
```python
from des_sle.thermo.nrtl import NRTL

params = {"g12": -1089.34, "g21": 7234.56, "alpha12": 0.3}
model = NRTL(params)

gamma1, gamma2 = model.activity_coefficient([0.5, 0.5], T=350.0)
```

#### `fit_curve` (from `des_sle.fitting.optimizer`)
```python
fit_curve(
    comp1, comp2, alpha12, curve_data, component_index,
    method="differential_evolution", bounds=None
)
```
Fit NRTL parameters for a single liquidus curve.

**Parameters:**
- `comp1`, `comp2`: Component objects
- `alpha12`: Fixed NRTL non-randomness parameter
- `curve_data`: DataFrame with 'x' and 'T' columns
- `component_index`: Which component crystallizes (0 or 1)
- `method`: Optimization method ('differential_evolution', 'multi_start', etc.)
- `bounds`: Parameter bounds for [g12, g21]

**Returns:**
- Dictionary: `{'g12': float, 'g21': float, 'rmse': float, 'success': bool}`

#### `save_fitted_parameters` (from `des_sle.io.yaml_loader`)
```python
save_fitted_parameters(
    filepath, mixture_name, components, nrtl_params, fitting_info=None
)
```
Save fitted parameters to YAML file.

**Parameters:**
- `filepath`: Output YAML file path
- `mixture_name`: Name for this mixture
- `components`: List of Component objects
- `nrtl_params`: Dict with 'g12', 'g21', 'alpha12'
- `fitting_info`: Optional dict with fitting metadata

#### `split_liquidus_curves` (from `des_sle.io.csv_loader`)
```python
split_liquidus_curves(liquidus_data, x_eutectic)
```
Split liquidus DataFrame into left and right curves.

**Returns:**
- Tuple: `(left_curve, right_curve)` DataFrames

#### `SLEEquation`
```python
SLEEquation(components: list, activity_model)
```
- Creates SLE residual function
- Methods:
  - `residual(T, x, index)`: Calculate equilibrium residual

#### `SLESolver`
```python
SLESolver(residual_func, initial_guess: float = 300.0)
```
- Methods:
  - `solve_T(x, index)`: Solve for temperature at given composition
  - `solve_x(T, index)`: Solve for composition at given temperature

### Plotting Functions

#### `plot_sle_diagram`
```python
plot_sle_diagram(
    x_values, T_eq_1, T_eq_2, components,
    x_solidus=None, T_solidus=None,
    x_liquidus=None, T_liquidus=None
)
```
Generates publication-quality phase diagram with model predictions and experimental data.

---

## Citation

If you use this software in your research, please cite:

```bibtex
@article{yourname2025dessle,
  title={Thermodynamic Modeling of Deep Eutectic Solvent Phase Behavior Using NRTL-Based Solid-Liquid Equilibrium},
  author={Your Name and Collaborators},
  journal={Journal Name},
  year={2025},
  volume={XX},
  pages={XXX--XXX},
  doi={10.XXXX/xxxxx}
}
```

**Software Citation:**
```bibtex
@software{dessle2025,
  author = {Your Name},
  title = {DES-SLE: Deep Eutectic Solvent Solid-Liquid Equilibria Modeling},
  year = {2025},
  version = {0.1.0},
  url = {https://github.com/marcovillegaz/fusion_point_cam}
}
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code Style

- Follow PEP 8
- Use Black for formatting: `black src/ scripts/`
- Use docstrings (NumPy style)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- NRTL model formulation based on Renon & Prausnitz (1968)
- SLE theory from Prausnitz et al., *Molecular Thermodynamics of Fluid-Phase Equilibria* (1999)
- Optimization algorithms from SciPy library

---

## Contact

For questions, issues, or collaboration opportunities:
- **GitHub Issues**: [https://github.com/marcovillegaz/fusion_point_cam/issues](https://github.com/marcovillegaz/fusion_point_cam/issues)

---

## Troubleshooting

### Common Issues

**1. High RMSE (>10 K)**
- Check that data is correctly split at eutectic point
- Verify component crystallization indices (left=1, right=0)
- Try expanding parameter bounds: `[(-20000, 20000), (-20000, 20000)]`

**2. Convergence Failures**
- Increase `maxiter` in optimization settings
- Try different optimization methods
- Check data quality (outliers, measurement errors)

**3. Import Errors**
- Ensure package is installed: `pip install -e .`
- Check Python version ≥ 3.8
- Verify all dependencies are installed

**4. Eutectic Detection Issues**
- Manually verify eutectic point in `eutectic_info.txt`
- Check that left curve ends at same x as right curve begins
- Ensure temperature is minimum at eutectic

---

## Changelog

### Version 0.1.0 (2025-12-07)
- Initial release
- NRTL activity coefficient model
- Curve-by-curve fitting methodology
- Differential evolution optimization
- Modular phase diagram plotting
- Comprehensive validation tools
