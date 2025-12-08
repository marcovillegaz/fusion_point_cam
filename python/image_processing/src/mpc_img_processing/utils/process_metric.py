"""Module for processing and analyzing image metrics over time and temperature."""

import numpy as np
from scipy.signal import find_peaks


def calculate_derivative(x, y):
    """
    Calculate first derivative using numpy gradient.

    Args:
        x: Independent variable (e.g., time)
        y: Dependent variable (e.g., metric values)

    Returns:
        derivative: dy/dx
    """
    return np.gradient(y, x)


def find_transition_points(
    time, metric_values, temperature, prominence=None, height=None, distance=None
):
    """
    Find peaks in the first derivative to identify drastic changes.

    Args:
        time: Time array in ms
        metric_values: Metric values array
        temperature: Temperature array
        prominence: Minimum prominence for peak detection
        height: Minimum height for peak detection
        distance: Minimum distance between peaks

    Returns:
        peaks_info: Dictionary containing peak indices, temperatures, and derivative values
    """
    # Calculate first derivative
    derivative = calculate_derivative(time, metric_values)

    # Calculate absolute derivative to catch both positive and negative changes
    abs_derivative = np.abs(derivative)

    # Find peaks in absolute derivative
    peaks, properties = find_peaks(
        abs_derivative, prominence=prominence, height=height, distance=distance
    )

    peaks_info = {
        "indices": peaks,
        "temperatures": temperature[peaks] if len(peaks) > 0 else np.array([]),
        "derivative_values": derivative[peaks] if len(peaks) > 0 else np.array([]),
        "abs_derivative_values": (
            abs_derivative[peaks] if len(peaks) > 0 else np.array([])
        ),
        "time": time[peaks] if len(peaks) > 0 else np.array([]),
        "metric_values": metric_values[peaks] if len(peaks) > 0 else np.array([]),
        "properties": properties,
    }

    return derivative, abs_derivative, peaks_info
