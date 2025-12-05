"""
Abstract model
"""

from abc import ABC, abstractmethod
from typing import Dict, List

import numpy as np


class ActivityModel(ABC):
    """
    Abstract base class for activity coefficient models.
    All specific models (NRTL, Wilson, UNIQUAC) inherit from this class.
    """

    @abstractmethod
    def activity_coefficient(self, x: np.ndarray, T: float) -> np.ndarray:
        """
        Calculate activity coefficients for all components.

        Args:
            x: Mole fraction array [x1, x2, ..., xn]
            T: Temperature [K]
            params: Dictionary of model parameters

        Returns:
            Array of activity coefficients [gamma1, gamma2, ..., gamman]
        """
        pass

    @abstractmethod
    def get_parameter_names(self, n_components: int) -> List[str]:
        """
        Return list of required parameter names for given number of components.

        Args:
            n_components: Number of components in the system

        Returns:
            List of parameter names
        """
        pass

    def validate_composition(self, x: np.ndarray) -> None:
        """Validate mole fraction array"""
        x = np.asarray(x)
        if not np.isclose(np.sum(x), 1.0, atol=1e-6):
            raise ValueError(f"Mole fractions must sum to 1.0, got sum={np.sum(x)}")
        if np.any(x < 0) or np.any(x > 1):
            raise ValueError(f"Mole fractions must be between 0 and 1, got {x}")
