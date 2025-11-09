"""NRTL model"""

from typing import Dict, List
import numpy as np
from des_sle.models.activity_model import ActivityModel


class NRTL(ActivityModel):
    """
    Non-Random Two-Liquid (NRTL) activity coefficient model.

    For binary systems, parameters are:
        - tau12, tau21: Binary interaction parameters (dimensionless)
        - alpha12: Non-randomness parameter (typically 0.2-0.47)

    NRTL equation:
        ln(gamma_i) = [Σj(xj·τji·Gji) / Σk(xk·Gki)] +
                 Σj[xj·Gij/Σk(xk·Gkj) · (τij - Σm(xm·τmj·Gmj)/Σk(xk·Gkj))]

    where: Gij = exp(-alpha_ij·τij)
    """

    def __init__(self):
        self.name = "NRTL"

    def activity_coefficient(self, x: np.ndarray, T: float, params: Dict) -> np.ndarray:
        """
        Calculate NRTL activity coefficients.

        Args:
            x: Mole fraction array [x1, x2, ..., xn]
            T: Temperature [K] (not used in basic NRTL, but kept for consistency)
            params: Dictionary with keys like 'tau12', 'tau21', 'alpha12', etc.

        Returns:
            Array of activity coefficients [alpha_1, alpha_2, ..., alpha_n]
        """

        self.validate_composition(x)

        x = np.asarray(x)
        n = len(x)

        if n == 2:
            return self._binary_nrtl(x, params)
        elif n > 2:
            return self._multicomponent_nrtl(x, params)
        else:
            print("component are less than one, error.")  # Improve this message

    def _binary_nrtl(self, x: np.ndarray, params: Dict) -> np.ndarray:
        """
        Calculate NRTL activity coefficients for binary system.
        Optimized implementation for 2-component systems.
        """
        # Extract parameters
        tau12 = params["tau12"]
        tau21 = params["tau21"]
        alpha12 = params.get("alpha12", 0.3)  # Default alpha = 0.3

        # Mole fractions
        x1, x2 = x[0], x[1]

        # Calculate G parameters
        G12 = np.exp(-alpha12 * tau12)
        G21 = np.exp(-alpha12 * tau21)

        # Activity coefficient for component 1
        term1_1 = tau21 * G21 / (x1 + x2 * G21)
        term2_1 = tau12 * G12 / (x2 + x1 * G12)
        ln_gamma1 = x2**2 * (term1_1 + term2_1**2)

        # Activity coefficient for component 2
        term1_2 = tau12 * G12 / (x2 + x1 * G12)
        term2_2 = tau21 * G21 / (x1 + x2 * G21)
        ln_gamma2 = x1**2 * (term1_2 + term2_2**2)

        gamma1 = np.exp(ln_gamma1)
        gamma2 = np.exp(ln_gamma2)

        return np.array([gamma1, gamma2])

    def _multicomponent_nrtl(self, x: np.ndarray, params: Dict) -> np.ndarray:
        """
        Calculate NRTL activity coefficients for multicomponent system.
        General implementation following the full NRTL equation.
        """
        n = len(x)

        # Build tau and alpha matrices
        tau = np.zeros((n, n))
        alpha = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                if i != j:
                    tau[i, j] = params.get(f"tau{i+1}{j+1}", 0.0)
                    alpha[i, j] = params.get(f"alpha{i+1}{j+1}", 0.3)

        # Calculate G matrix
        G = np.exp(-alpha * tau)
        np.fill_diagonal(G, 1.0)  # Gii = 1

        # Calculate activity coefficients
        ln_gamma = np.zeros(n)

        for i in range(n):
            # First term: Σj(xj·τji·Gji) / Σk(xk·Gki)
            sum_xG_i = np.sum(x * G[:, i])
            term1 = np.sum(x * tau[:, i] * G[:, i]) / sum_xG_i

            # Second term: Σj[xj·Gij/Σk(xk·Gkj) · (τij - Σm(xm·τmj·Gmj)/Σk(xk·Gkj))]
            term2 = 0.0
            for j in range(n):
                sum_xG_j = np.sum(x * G[:, j])
                inner_sum = np.sum(x * tau[:, j] * G[:, j]) / sum_xG_j
                term2 += x[j] * G[i, j] / sum_xG_j * (tau[i, j] - inner_sum)

            ln_gamma[i] = term1 + term2

        return np.exp(ln_gamma)

    def get_parameter_names(self, n_components: int) -> List[str]:
        """
        Get required parameter names for NRTL model.

        For binary: ['tau12', 'tau21', 'alpha12']
        For multicomponent: ['tau12', 'tau21', ..., 'alpha12', 'alpha21', ...]
        """
        params = []
        for i in range(1, n_components + 1):
            for j in range(1, n_components + 1):
                if i != j:
                    params.append(f"tau{i}{j}")

        for i in range(1, n_components + 1):
            for j in range(1, n_components + 1):
                if i != j:
                    params.append(f"alpha{i}{j}")

        return params
