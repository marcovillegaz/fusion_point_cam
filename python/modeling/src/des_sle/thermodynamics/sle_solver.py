"""
Solid-Liquid Equilibrium Solver
File: src/des_sle/thermodynamics/sle_solver.py

Solves the SLE equation:
    ln(xi * γi) = - ΔHfus,i/R * (1/T - 1/Tm,i)

for each component i to find the liquidus temperature.
"""

import numpy as np
from scipy.optimize import fsolve, root_scalar
from typing import List, Dict, Tuple, Optional
import warnings


class SLESolver:
    """
    Solid-Liquid Equilibrium solver for binary and multicomponent systems.

    Attributes:
        components: List of Component objects
        activity_model: Activity coefficient model (NRTL, Wilson, etc.)
        params: Dictionary of activity model parameters
        R: Universal gas constant [J/(mol·K)]
    """

    # Universal gas constant [J/(mol·K)]
    R = 8.314

    def __init__(self, components: List, activity_model, params: Dict):
        """
        Initialize SLE solver.

        Args:
            components: List of Component objects with Tm and dHfus
            activity_model: Instance of ActivityModel (e.g., NRTL)
            params: Dictionary of model parameters
        """
        self.components = components
        self.activity_model = activity_model
        self.params = params
        self.n_components = len(components)

        # Validate
        if self.n_components < 2:
            raise ValueError("Need at least 2 components for SLE calculation")

    def activity_term(self, x: np.ndarray, T: float, component_index: int) -> float:
        """
        Calculate the activity term for SLE equation.

        Term = xi * γi * exp[ΔHfus,i/R * (1/T - 1/Tm,i)]

        Args:
            x: Mole fraction array
            T: Temperature [K]
            component_index: Index of component (0, 1, ...)

        Returns:
            Activity term value (should equal 1 at equilibrium)
        """
        comp = self.components[component_index]

        # Get activity coefficient
        gamma = self.activity_model.activity_coefficient(x, T, self.params)

        # Calculate exponential term
        exp_term = np.exp((comp.dHfus / self.R) * (1 / comp.Tm - 1 / T))

        # Activity term
        activity = x[component_index] * gamma[component_index] * exp_term

        return activity

    def sle_residual(self, T: float, x: np.ndarray, component_index: int) -> float:
        """
        Residual function for SLE equation.

        Residual = xi * γi * exp[ΔHfus,i/R * (1/Tm,i - 1/T)] - 1

        At equilibrium, residual = 0.

        Args:
            T: Temperature [K]
            x: Mole fraction array
            component_index: Index of component

        Returns:
            Residual value
        """
        return self.activity_term(x, T, component_index) - 1.0

    def calculate_liquidus_temperature(  # REVISAR
        self, x: np.ndarray, component_index: int = 0, T_guess: Optional[float] = None
    ) -> float:
        """
        Calculate liquidus temperature for given composition.

        Solves: xi * γi * exp[ΔHfus,i/R * (1/Tm,i - 1/T)] = 1

        Args:
            x: Mole fraction array [x1, x2, ...]
            component_index: Which component is precipitating (default: 0)
            T_guess: Initial guess for temperature [K] (optional)

        Returns:
            Liquidus temperature [K]
        """
        x = np.asarray(x)

        # Validate composition
        if not np.isclose(np.sum(x), 1.0, atol=1e-6):
            raise ValueError(f"Mole fractions must sum to 1.0, got {np.sum(x)}")

        # Initial guess: weighted average of melting points
        if T_guess is None:
            T_guess = np.sum([x[i] * self.components[i].Tm for i in range(self.n_components)])

        # Get bounds for solver
        T_min = min(comp.Tm for comp in self.components) * 0.5  # Lower bound
        T_max = max(comp.Tm for comp in self.components) * 1.2  # Upper bound

        try:
            # Use root_scalar for robust solving
            result = root_scalar(
                self.sle_residual,
                args=(x, component_index),
                x0=T_guess,
                bracket=[T_min, T_max],
                method="brentq",
            )

            if result.converged:
                return result.root
            else:
                warnings.warn(f"Solver did not converge for x={x}")
                return result.root

        except ValueError as e:
            # If bracket method fails, try fsolve
            warnings.warn(f"Bracket method failed, trying fsolve: {e}")
            result = fsolve(self.sle_residual, T_guess, args=(x, component_index), full_output=True)

            T_solution = result[0][0]
            info = result[1]

            if info["fvec"][0] ** 2 < 1e-6:  # Check if residual is small
                return T_solution
            else:
                raise RuntimeError(f"Failed to converge for composition x={x}")

    def calculate_phase_diagram_binary(
        self, n_points: int = 50, x_range: Tuple[float, float] = (0.01, 0.99)
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate complete binary phase diagram.

        For binary systems, calculates liquidus curves for both components.

        Args:
            n_points: Number of composition points
            x_range: Range of x1 to calculate (min, max)

        Returns:
            Tuple of (x1_array, T_liquidus_comp1, T_liquidus_comp2)
        """
        if self.n_components != 2:
            raise ValueError("This method is only for binary systems")

        x1_array = np.linspace(x_range[0], x_range[1], n_points)
        T_comp1 = np.zeros(n_points)  # Liquidus when component 1 precipitates
        T_comp2 = np.zeros(n_points)  # Liquidus when component 2 precipitates

        for i, x1 in enumerate(x1_array):
            x = np.array([x1, 1 - x1])

            # Calculate liquidus for component 1 precipitation
            try:
                T_comp1[i] = self.calculate_liquidus_temperature(x, component_index=0)
            except:
                T_comp1[i] = np.nan

            # Calculate liquidus for component 2 precipitation
            try:
                T_comp2[i] = self.calculate_liquidus_temperature(x, component_index=1)
            except:
                T_comp2[i] = np.nan

        return x1_array, T_comp1, T_comp2

    def find_eutectic_point_binary(
        self, x_guess: float = 0.5, T_guess: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Find eutectic point for binary system.

        At eutectic: both components satisfy SLE equation simultaneously.

        Args:
            x_guess: Initial guess for eutectic composition
            T_guess: Initial guess for eutectic temperature

        Returns:
            Tuple of (x_eutectic, T_eutectic)
        """
        if self.n_components != 2:
            raise ValueError("This method is only for binary systems")

        if T_guess is None:
            T_guess = min(comp.Tm for comp in self.components) * 0.9

        def eutectic_residuals(vars):
            """Both SLE equations must be satisfied"""
            x1, T = vars
            x = np.array([x1, 1 - x1])

            res1 = self.sle_residual(T, x, component_index=0)
            res2 = self.sle_residual(T, x, component_index=1)

            return [res1, res2]

        # Solve system of equations
        result = fsolve(eutectic_residuals, [x_guess, T_guess], full_output=True)

        x_eut, T_eut = result[0]
        info = result[1]

        # Check convergence
        if np.sum(info["fvec"] ** 2) < 1e-6:
            return x_eut, T_eut
        else:
            warnings.warn("Eutectic point calculation may not have converged")
            return x_eut, T_eut

    def get_actual_liquidus(
        self, x1_array: np.ndarray, T_comp1: np.ndarray, T_comp2: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the actual liquidus curve (minimum of both component curves).

        The actual liquidus is the lower temperature at each composition,
        since that's where first solid appears on cooling.

        Args:
            x1_array: Composition array
            T_comp1: Liquidus temperatures when component 1 precipitates
            T_comp2: Liquidus temperatures when component 2 precipitates

        Returns:
            Tuple of (x_liquidus, T_liquidus) - the actual liquidus curve
        """
        # Take minimum temperature at each composition
        T_liquidus = np.minimum(T_comp1, T_comp2)

        # Remove NaN values
        mask = ~np.isnan(T_liquidus)

        return x1_array[mask], T_liquidus[mask]

    def __repr__(self):
        comp_names = ", ".join([c.name for c in self.components])
        return f"SLESolver({comp_names}, {self.activity_model.name})"
