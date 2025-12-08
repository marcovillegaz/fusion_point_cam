# NRTL Parameter Fitting Scripts

This directory contains scripts for fitting and verifying NRTL parameters using a **curve-by-curve methodology** for eutectic systems.

## Overview

The refactored package now provides modular fitting tools through the `des_sle.fitting` module, with scripts that demonstrate best practices for parameter estimation in binary eutectic systems.

## Key Concept: Curve-by-Curve Fitting

**Why it matters:** In eutectic systems, the liquidus curve consists of two distinct branches where different components crystallize. Traditional full-curve fitting treats this as a single dataset, which is thermodynamically incorrect.

**Solution:** Split the liquidus at the eutectic point and fit each branch with the correct crystallizing component index:
- **Left branch** (x < x_eutectic): Component 2 crystallizes (index=1)
- **Right branch** (x > x_eutectic): Component 1 crystallizes (index=0)

## Scripts

### 1. `split_liquidus_data.py`

Splits experimental liquidus data into left and right curves at the eutectic point.

**Purpose:**
- Identifies eutectic point (minimum temperature)
- Splits data into two CSV files for independent fitting
- Creates metadata file with eutectic information

**Usage:**
```bash
python scripts/split_liquidus_data.py
```

**Input:**
- `data/reference_examples/liquidus.csv` - Full liquidus curve

**Output:**
- `data/experimental_split/liquidus_left.csv` - Left branch (comp 2 crystallizes)
- `data/experimental_split/liquidus_right.csv` - Right branch (comp 1 crystallizes)
- `data/experimental_split/eutectic_info.txt` - Eutectic coordinates

**Uses package functions:**
```python
from des_sle.io.csv_loader import split_liquidus_curves
```

---

### 2. `fit_nrtl_by_curves.py` ⭐ **Main Fitting Script**

Fits NRTL parameters using the curve-by-curve methodology with multiple optimization strategies.

**Features:**
- Loads pre-split experimental curves
- Fits left curve (component 2 crystallizes) independently
- Fits right curve (component 1 crystallizes) independently  
- Combines parameters using:
  - Weighted average (based on data points)
  - Joint optimization (both curves simultaneously)
- Generates comparison plots for all methods
- Saves best parameters to YAML

**Usage:**
```bash
python scripts/fit_nrtl_by_curves.py
```

**Input:**
- `data/experimental_split/liquidus_left.csv`
- `data/experimental_split/liquidus_right.csv`
- `data/experimental_split/eutectic_info.txt` (optional)

**Output:**
- Console: Detailed fitting results for each method
- Plots: Phase diagrams comparing all parameter sets
- File: `data/fitted_parameters_by_curves.yaml`

**Uses package modules:**
```python
from des_sle.io.csv_loader import (
    load_liquidus_curve_csv,
    find_eutectic_from_data,
    load_eutectic_info
)
from des_sle.io.yaml_loader import save_fitted_parameters
from des_sle.fitting.optimizer import (
    fit_curve,
    weighted_average_parameters,
    optimize_combined_parameters
)
```

**Customization:**

Edit component properties in the script:
```python
comp1 = Component(name="Pe4NBr", Tm=373.2, dHfus=41450)
comp2 = Component(name="Component2", Tm=392.2, dHfus=39400)
alpha12 = 0.3  # NRTL non-randomness parameter
```

Adjust optimization bounds:
```python
bounds = [(-15000, 15000), (-15000, 15000)]  # [g12, g21] in J/mol
```

**Output Example:**
```
NRTL FITTING BY SEPARATE LIQUIDUS CURVES
======================================================================

EUTECTIC POINT
======================================================================
  x_eutectic = 0.5940
  T_eutectic = 342.00 K (68.85 °C)

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

Optimizing combined parameters...
  Results: g12=-1089.34 J/mol, g21=7234.56 J/mol, RMSE=2.33 K

Parameters saved to: data/fitted_parameters_by_curves.yaml
```

---

### 3. `verify_nrtl_params.py`

Verifies fitted NRTL parameters against experimental data with comprehensive error analysis.

**Features:**
- Loads parameters from YAML
- Compares model predictions with experimental data
- Calculates error statistics (RMSE, MAE, mean error, max error)
- Generates diagnostic plots

**Usage:**
```bash
python scripts/verify_nrtl_params.py
```

**Input:**
- YAML file with fitted parameters
- Experimental data for validation

**Output:**
- Console: Comprehensive error statistics
- Plots: Two-panel diagnostic (phase diagram + residuals)

---

## Package Module Usage

The refactored package provides reusable modules that these scripts leverage:

### Fitting Module (`des_sle.fitting`)

```python
from des_sle.fitting.optimizer import fit_curve

# Fit a single curve
result = fit_curve(
    comp1, comp2, alpha12,
    curve_data,
    component_index=1,  # Which component crystallizes
    method="differential_evolution",
    bounds=[(-15000, 15000), (-15000, 15000)]
)

print(f"g12 = {result['g12']:.2f} J/mol")
print(f"g21 = {result['g21']:.2f} J/mol")
print(f"RMSE = {result['rmse']:.2f} K")
```

### IO Module (`des_sle.io`)

```python
from des_sle.io.csv_loader import load_liquidus_curve_csv, split_liquidus_curves
from des_sle.io.yaml_loader import save_fitted_parameters

# Load and split data
data = load_liquidus_curve_csv("liquidus.csv")
left, right = split_liquidus_curves(data, x_eutectic=0.5)

# Save parameters
save_fitted_parameters(
    filepath="output.yaml",
    mixture_name="MySystem",
    components=[comp1, comp2],
    nrtl_params={"g12": g12, "g21": g21, "alpha12": alpha12},
    fitting_info={"rmse": 2.5, "method": "curve_by_curve"}
)
```

---

## Data Format

### YAML Format (mixtures.yaml)

```yaml
mixtures:
  Pe4NBr_SuccinicAcid:
    components:
      - name: Pe4NBr
        Tm: 373.2      # Melting temperature [K]
        dHfus: 41450   # Enthalpy of fusion [J/mol]
      - name: Succinic acid
        Tm: 461.0      # K
        dHfus: 39400   # J/mol
    nrtl_params:
      g12: -2578.1     # Energy parameter [J/mol]
      g21: -9225.3     # Energy parameter [J/mol]
      alpha12: 0.3     # Non-randomness parameter (0.2-0.47)
```

### CSV Format (liquidus.csv, solidus.csv)

- **Delimiter:** `;` (semicolon)
- **Decimal:** `,` (comma) - European format
- **Columns:** `x` (mole fraction), `T` (temperature)

Example:
```csv
x;T
0,077;120,7
0,092;120,13
0,11;119,8
```

---

## Workflow Example

### 1. Fit Parameters to New Experimental Data

```bash
# 1. Prepare your data files
# - examples/liquidus.csv (required)
# - examples/solidus.csv (optional)

# 2. Edit component properties in nrtl_parameter_fitting.py
# - Update Tm and dHfus for your components

# 3. Run optimization
python scripts/nrtl_parameter_fitting.py

# 4. Check output
# - Optimized parameters printed to console
# - Phase diagram plot displayed
# - Parameters saved to examples/data/fitted_parameters.yaml
```

### 2. Verify Existing Parameters

```bash
# 1. Ensure YAML file exists with parameters
# - examples/data/mixtures.yaml

# 2. Run verification
python scripts/verify_nrtl_params.py

# 3. Check results
# - Error statistics in console
# - Diagnostic plots displayed
```

---

## Understanding Results

### Error Metrics

- **RMSE (Root Mean Square Error):** Overall fit quality. Lower is better.
  - Excellent: < 5 K
  - Good: 5-15 K
  - Fair: 15-30 K
  - Poor: > 30 K

- **MAE (Mean Absolute Error):** Average magnitude of errors.

- **Mean Error:** Indicates systematic bias (should be near 0).

- **Max |Error|:** Largest single prediction error.

### NRTL Parameters

- **g12, g21:** Energy parameters [J/mol]
  - Usually negative (attractive interactions)
  - Typical range: -15000 to 5000 J/mol
  - These are optimized to fit experimental data

- **alpha12:** Non-randomness parameter
  - **Fixed at 0.3** (standard NRTL practice)
  - Can be changed if needed (typical range: 0.2-0.47)
  - 0.3 is the most commonly used value
  - Lower values = more random mixing

### Troubleshooting

**Problem:** High RMSE (> 50 K)

**Solutions:**
1. Check component properties (Tm, dHfus) - ensure they're correct
2. Verify temperature units (Celsius vs Kelvin)
3. Check experimental data quality
4. Try different optimization method
5. Adjust parameter bounds in code

**Problem:** Optimization fails or doesn't converge

**Solutions:**
1. Use `differential_evolution` instead of `minimize`
2. Check for data outliers
3. Ensure composition range doesn't include pure components (x=0 or x=1)
4. Increase `maxiter` in optimization settings

**Problem:** RuntimeWarnings during optimization

**Solutions:**
1. Normal for optimization process (trying invalid parameter regions)
2. If excessive, check parameter bounds
3. Ensure experimental data is reasonable

---

## Advanced Usage

### Custom Optimization Bounds

Edit bounds in `nrtl_parameter_fitting.py`:

```python
bounds = [
    (-15000, 5000),   # g12 bounds [J/mol]
    (-15000, 5000),   # g21 bounds [J/mol]
]
# Note: alpha12 is fixed and not optimized
```

### Custom Alpha12 Value

If you need to use a different alpha12 value:

```python
# In the main() function, modify the fitter initialization:
fitter = NRTLParameterFitter(
    comp1, 
    comp2, 
    liquidus_data, 
    solidus_data,
    alpha12=0.25  # Change from default 0.3
)
```

### Multiple Mixture Fitting

To fit multiple systems, create a loop:

```python
systems = [
    ('System1', comp1_a, comp2_a, 'data1.csv'),
    ('System2', comp1_b, comp2_b, 'data2.csv'),
]

for name, c1, c2, datafile in systems:
    liquidus_data = load_csv_data(datafile)
    fitter = NRTLParameterFitter(c1, c2, liquidus_data)
    params = fitter.fit()
    fitter.save_to_yaml(f"{name}_params.yaml", name)
```

---

## References

- NRTL Model: Renon, H., & Prausnitz, J. M. (1968). AIChE Journal, 14(1), 135-144.
- SLE Theory: Prausnitz, J. M., et al. (1999). Molecular Thermodynamics of Fluid-Phase Equilibria.

---

## Dependencies

```
numpy
pandas
matplotlib
scipy
pyyaml
```

Install with:
```bash
pip install numpy pandas matplotlib scipy pyyaml
```
