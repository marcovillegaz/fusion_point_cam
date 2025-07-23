import numpy as np
from scipy.signal import savgol_filter, find_peaks


def smooth_series(series, window=51, polyorder=3):
    """Apply Savitzky-Golay filter smoothing"""
    return savgol_filter(series, window_length=window, polyorder=polyorder)


def compute_slope(time, series):
    dt = np.diff(time)
    dy = np.diff(series)
    slope = dy / dt
    return slope


def detect_peaks(data, height=None, distance=None):
    peaks, properties = find_peaks(data, height=height, distance=distance)
    return peaks, properties
