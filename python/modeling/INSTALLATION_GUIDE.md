# Installation and Usage Guide

## For Colleagues and Collaborators

This guide will help you install the DES-SLE package and use it for your research on solid-liquid equilibria modeling.

## Quick Start (5 minutes)

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/marcovillegaz/fusion_point_cam.git
cd fusion_point_cam/python/modeling

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install the package
pip install -e .
```

### 2. Verify Installation

```bash
python -c "from des_sle import Component, NRTL; print('✓ Installation successful!')"
```

## Complete Workflow Example

### Step 1: Prepare Your Data

Create a CSV file with your experimental liquidus data:

**Format:** `liquidus.csv`
```csv
x;T
0.0;119.05
0.1;95.2
0.2;80.3
0.3;68.85
0.4;65.12
0.5;68.92
0.6;75.8
0.7;85.3
0.8;95.0
0.9;105.2
1.0;120.0
```

**Important:**
- Delimiter: `;` (semicolon)
- Decimal: `,` (comma) - European format
- Column names: `x` (mole fraction), `T` (temperature in °C)
- Place file in: `data/reference_examples/liquidus.csv`

### Step 2: Split Data at Eutectic Point

```bash
cd fusion_point_cam/python/modeling
python scripts/split_liquidus_data.py
```

**Output:**
```
Reading data from: data/reference_examples/liquidus.csv
Total data points: 47

Eutectic point identified:
  x_eutectic = 0.5940
  T_eutectic = 68.85 °C

Data split:
  Left curve (component 2 crystallizes): 31 points
  Right curve (component 1 crystallizes): 16 points

Files created:
  data/experimental_split/liquidus_left.csv
  data/experimental_split/liquidus_right.csv
  data/experimental_split/eutectic_info.txt

✓ Data split complete!
```

### Step 3: Define Your System

Edit `scripts/fit_nrtl_by_curves.py` to define your components:

```python
# Around line 55, modify these lines:
comp1 = Component(
    name="YourComponent1",  # Change this
    Tm=373.2,               # Melting temperature in K
    dHfus=41450            # Enthalpy of fusion in J/mol
)
comp2 = Component(
    name="YourComponent2",  # Change this
    Tm=392.2,               # Melting temperature in K
    dHfus=39400            # Enthalpy of fusion in J/mol
)
alpha12 = 0.3  # NRTL non-randomness parameter (typically 0.2-0.47)
```

**Where to find these values:**
- Literature databases (NIST, CRC Handbook)
- Differential Scanning Calorimetry (DSC) measurements
- Published papers on your compounds

### Step 4: Fit NRTL Parameters

```bash
python scripts/fit_nrtl_by_curves.py
```

**What happens:**
1. Loads your split experimental curves
2. Fits left curve (component 2 crystallizes) using global optimization
3. Fits right curve (component 1 crystallizes) using global optimization
4. Combines parameters using weighted average
5. Refines parameters with joint optimization
6. Shows comparison plots
7. Saves best parameters to YAML

**Expected output:**
```
NRTL FITTING BY SEPARATE LIQUIDUS CURVES
======================================================================

EUTECTIC POINT
  x_eutectic = 0.5940
  T_eutectic = 342.00 K (68.85 °C)

FITTING INDIVIDUAL CURVES
======================================================================

Fitting curve for Component2 crystallization...
  Data points: 31
  Results: g12=-1234.56 J/mol, g21=7890.12 J/mol, RMSE=1.85 K

Fitting curve for Component1 crystallization...
  Data points: 16
  Results: g12=-987.65 J/mol, g21=6543.21 J/mol, RMSE=2.12 K

COMBINING PARAMETERS
======================================================================

Weighted Average:
  g12 = -1150.23 J/mol
  g21 = 7456.89 J/mol

Optimizing combined parameters...
  Results: g12=-1089.34 J/mol, g21=7234.56 J/mol, RMSE=2.33 K

Parameters saved to: data/fitting/fitted_parameters_by_curves.yaml

FITTING COMPLETE
======================================================================
```

**Interpretation:**
- **RMSE < 5 K**: Excellent fit
- **RMSE 5-15 K**: Good fit  
- **RMSE > 15 K**: Check data quality or component properties

### Step 5: Verify and Validate

```bash
python scripts/verify_nrtl_params.py
```

This generates diagnostic plots and error statistics to validate your fit.

## Using the Package Programmatically

### Import the Package

```python
from des_sle import Component, NRTL, SLEEquation, SLESolver, find_eutectic_point
from des_sle.io import load_mixture, save_fitted_parameters
from des_sle.fitting import fit_curve, optimize_combined_parameters
from des_sle.plot.diagrams import plot_sle_diagram
import numpy as np
```

### Calculate Phase Diagram

```python
# Load fitted parameters
components, nrtl_params = load_mixture(
    "data/fitting/fitted_parameters_by_curves.yaml",
    "Fitted_By_Curves"
)

# Create model
model = NRTL(nrtl_params)
sle_eq = SLEEquation(components, model)
solver = SLESolver(sle_eq.residual, initial_guess=300.0)

# Generate phase diagram
x_range = np.linspace(0.001, 0.999, 100)
T_eq_1, T_eq_2 = solver.compute_curve(x_range)

# Find eutectic point
x_e, T_e = find_eutectic_point(sle_eq)
print(f"Eutectic: x={x_e:.4f}, T={T_e:.2f} K")

# Crop curves at eutectic
T_eq_1 = np.where(x_range >= x_e, T_eq_1, np.nan)
T_eq_2 = np.where(x_range <= x_e, T_eq_2, np.nan)

# Plot
plot_sle_diagram(x_range, T_eq_1, T_eq_2, components)
```

### Fit Custom Parameters

```python
from des_sle.io.csv_loader import load_liquidus_curve_csv
from des_sle.fitting.optimizer import fit_curve
from des_sle.data.component import Component

# Define your system
comp1 = Component(name="CompA", Tm=373.2, dHfus=41450)
comp2 = Component(name="CompB", Tm=392.2, dHfus=39400)

# Load data
curve_data = load_liquidus_curve_csv("your_data.csv")

# Fit with custom settings
result = fit_curve(
    comp1, comp2,
    alpha12=0.3,
    curve_data=curve_data,
    component_index=1,  # Which component crystallizes
    method="differential_evolution",
    bounds=[(-20000, 20000), (-20000, 20000)]
)

print(f"Fitted: g12={result['g12']:.2f}, g21={result['g21']:.2f}")
print(f"RMSE: {result['rmse']:.2f} K")
```

## Troubleshooting

### High RMSE (>10 K)

**Possible causes:**
1. Incorrect component properties (Tm, ΔHfus)
2. Data not properly split at eutectic
3. Wrong crystallizing component indices

**Solutions:**
```python
# 1. Verify component properties
print(f"Comp1: Tm={comp1.Tm} K, ΔHfus={comp1.dHfus} J/mol")
print(f"Comp2: Tm={comp2.Tm} K, ΔHfus={comp2.dHfus} J/mol")

# 2. Check eutectic point in eutectic_info.txt
with open("data/experimental_split/eutectic_info.txt") as f:
    print(f.read())

# 3. Expand parameter bounds
bounds = [(-20000, 20000), (-20000, 20000)]
```

### Import Errors

```bash
# Ensure package is installed
pip list | grep des-sle

# If not found, reinstall
pip install -e .

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Optimization Doesn't Converge

```python
# Try different optimization method
result = fit_curve(..., method="multi_start")  # Instead of "differential_evolution"

# Or increase iterations
# Edit optimizer.py, line ~56:
# maxiter=2000  →  maxiter=5000
```

## File Locations

**Input files:**
- Raw data: `data/reference_examples/liquidus.csv`
- Split data: `data/experimental_split/liquidus_left.csv`, `liquidus_right.csv`

**Output files:**
- Fitted parameters: `data/fitting/fitted_parameters_by_curves.yaml`
- Plots: Displayed in matplotlib windows (can be saved manually)

**Scripts:**
- Data splitting: `scripts/split_liquidus_data.py`
- Parameter fitting: `scripts/fit_nrtl_by_curves.py`
- Verification: `scripts/verify_nrtl_params.py`

**Package modules:**
- Components: `src/des_sle/data/component.py`
- NRTL model: `src/des_sle/thermo/nrtl.py`
- Fitting: `src/des_sle/fitting/optimizer.py`
- IO: `src/des_sle/io/csv_loader.py`, `yaml_loader.py`

## For Article Writing

### Key Points to Emphasize

1. **Curve-by-Curve Methodology**: Unlike traditional methods, we split the liquidus at the eutectic point and fit each branch with the correct crystallizing component

2. **Thermodynamic Consistency**: Each branch is fitted with the appropriate component index (left=1, right=0), ensuring correct phase equilibrium calculations

3. **Multiple Optimization Strategies**: 
   - Individual curve fitting
   - Weighted parameter averaging
   - Joint curve optimization

4. **Validation**: Comprehensive error analysis (RMSE, MAE, residuals)

### Citation-Ready Results

```python
# Generate publication-quality figures
plot_sle_diagram(x_range, T_eq_1, T_eq_2, components,
                 x_liquidus=x_exp, T_liquidus=T_exp)

# Extract key metrics
print(f"Fitted NRTL parameters:")
print(f"  g₁₂ = {params['g12']:.1f} ± {std_g12:.1f} J/mol")
print(f"  g₂₁ = {params['g21']:.1f} ± {std_g21:.1f} J/mol")
print(f"  α₁₂ = {params['alpha12']:.3f} (fixed)")
print(f"Model performance: RMSE = {rmse:.2f} K")
```

## Getting Help

1. **Documentation**: 
   - `README_PUBLICATION.md` - Comprehensive theory and API
   - `scripts/README_NRTL_FITTING.md` - Detailed script documentation
   - `REFACTORING_SUMMARY.md` - Package structure details

2. **Code Examples**:
   - `scripts/fit_nrtl_by_curves.py` - Complete workflow
   - `scripts/reference_model.py` - Basic usage

3. **Contact**: Open an issue on GitHub or contact the repository maintainer

## Next Steps

After successful fitting:
1. Save your results to version control
2. Document parameter sources (literature vs fitted)
3. Perform sensitivity analysis (vary α₁₂)
4. Compare with literature values if available
5. Generate publication figures
6. Write methods section citing NRTL model reference

Good luck with your research! 🚀
