import numpy as np
from scipy.signal import savgol_filter, find_peaks


def smooth_series(series, window=51, polyorder=3):
    """Apply Savitzky-Golay filter smoothing"""
    if len(series) < window:
        window = len(series) if len(series) % 2 == 1 else len(series) - 1
    return savgol_filter(series, window_length=window, polyorder=polyorder)


def smooth_data(data, window_length=11, polyorder=2):
    """
    Apply Savitzky-Golay filter to smooth the data.

    Args:
        data: Input data array
        window_length: Length of the filter window (must be odd)
        polyorder: Order of the polynomial used to fit the samples

    Returns:
        smoothed_data: Smoothed data array
    """
    if len(data) < window_length:
        window_length = len(data) if len(data) % 2 == 1 else len(data) - 1
    return savgol_filter(data, window_length, polyorder)


def compute_slope(time, series):
    """
    Compute slope using numpy diff.

    Args:
        time: Time array
        series: Data series array

    Returns:
        slope: dy/dt array (length = len(series) - 1)
    """
    dt = np.diff(time)
    dy = np.diff(series)
    slope = dy / dt
    return slope


def calculate_derivative(x, y, smooth=True, window_length=11, polyorder=2):
    """
    Calculate first derivative using numpy gradient with optional smoothing.

    Args:
        x: Independent variable (e.g., time)
        y: Dependent variable (e.g., metric values)
        smooth: Whether to smooth the data before differentiation
        window_length: Window length for smoothing
        polyorder: Polynomial order for smoothing

    Returns:
        derivative: dy/dx (same length as input)
    """
    if smooth:
        y_smooth = smooth_data(y, window_length=window_length, polyorder=polyorder)
        return np.gradient(y_smooth, x)
    else:
        return np.gradient(y, x)


def detect_peaks(data, height=None, distance=None, prominence=None):
    """
    Detect peaks in data using scipy.signal.find_peaks.

    Args:
        data: Input data array
        height: Minimum height of peaks
        distance: Minimum distance between peaks
        prominence: Minimum prominence of peaks

    Returns:
        peaks: Array of peak indices
        properties: Dictionary of peak properties
    """
    peaks, properties = find_peaks(
        data, height=height, distance=distance, prominence=prominence
    )
    return peaks, properties
