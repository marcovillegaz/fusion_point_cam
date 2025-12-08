# Thermodynamic Models Module

This module contains activity coefficient models for calculating non-ideal liquid phase behavior.

## NRTL Model

The Non-Random Two-Liquid (NRTL) model calculates activity coefficients for binary mixtures.

### Binary System Equations

For a binary system (components 1 and 2):

$$
\ln \gamma_1 = x_2^2 \left[ \tau_{21} \left( \frac{G_{21}}{x_1 + x_2 G_{21}} \right)^2 + \frac{\tau_{12} G_{12}}{(x_2 + x_1 G_{12})^2} \right]
$$

$$
\ln \gamma_2 = x_1^2 \left[ \tau_{12} \left( \frac{G_{12}}{x_2 + x_1 G_{12}} \right)^2 + \frac{\tau_{21} G_{21}}{(x_1 + x_2 G_{21})^2} \right]
$$

where:
- $\tau_{ij} = \frac{g_{ij}}{RT}$ (dimensionless energy parameters)
- $G_{ij} = \exp(-\alpha_{ij} \tau_{ij})$
- $g_{ij}$ = binary interaction energy parameters [J/mol]
- $\alpha_{ij}$ = non-randomness parameter (typically 0.2–0.47, often fixed at 0.3)
- $R$ = gas constant (8.314 J/mol·K)
- $T$ = temperature [K]

### Parameters

**Required parameters:**
- `g12`: Energy parameter for 1-2 interaction [J/mol]
- `g21`: Energy parameter for 2-1 interaction [J/mol]
- `alpha12`: Non-randomness parameter (dimensionless)

### Usage

```python
from des_sle.thermo.nrtl import NRTL
import numpy as np

# Define parameters
params = {
    "g12": -1089.34,  # J/mol
    "g21": 7234.56,   # J/mol
    "alpha12": 0.3    # dimensionless
}

# Create model
model = NRTL(params)

# Calculate activity coefficients
x = np.array([0.5, 0.5])  # Mole fractions
T = 350.0  # Temperature [K]

gamma1, gamma2 = model.activity_coefficient(x, T)
print(f"γ₁ = {gamma1:.4f}, γ₂ = {gamma2:.4f}")
```

## ActivityModel Base Class

Abstract base class for all activity coefficient models. Defines the interface:

```python
class ActivityModel(ABC):
    @abstractmethod
    def activity_coefficient(self, x, T):
        """Calculate activity coefficients.
        
        Args:
            x: Mole fraction array
            T: Temperature [K]
            
        Returns:
            Activity coefficients for each component
        """
        pass
```

## Future Models

The modular design allows easy addition of other activity coefficient models:
- Wilson
- UNIQUAC
- UNIFAC
- Margules

To add a new model, create a class inheriting from `ActivityModel` and implement the `activity_coefficient` method.

## Reference

Renon, H., & Prausnitz, J. M. (1968). Local compositions in thermodynamic excess functions for liquid mixtures. *AIChE Journal*, 14(1), 135-144.
