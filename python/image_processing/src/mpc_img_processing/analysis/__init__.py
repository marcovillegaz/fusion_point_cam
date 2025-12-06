"""Analysis modules for metrics and visualization"""

from .plot_results import plot_temperature_vs_metric, plot_time_series
from .compute_stats import smooth_series, compute_slope, detect_peaks
from .merge_results import merge_results

__all__ = [
    "plot_temperature_vs_metric",
    "plot_time_series",
    "smooth_series",
    "compute_slope",
    "detect_peaks",
    "merge_results",
]
