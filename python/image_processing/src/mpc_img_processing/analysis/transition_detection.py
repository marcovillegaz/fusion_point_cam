"""
Module for detecting temperature transition points in brightness metric data.
Uses first derivative peak detection to identify where brightness changes drastically.
"""

import numpy as np
import pandas as pd
from .compute_stats import calculate_derivative, detect_peaks


def auto_detect_peaks(time, metric_values, temperature, sensitivity="medium"):
    """
    Automatically detect peaks with adaptive parameters.

    Args:
        time: Time array in ms
        metric_values: Metric values array
        temperature: Temperature array
        sensitivity: 'low', 'medium', or 'high' - controls detection threshold

    Returns:
        derivative: First derivative array
        abs_derivative: Absolute derivative array
        peaks_info: Dictionary containing peak information
    """
    # Calculate smoothed derivative
    derivative = calculate_derivative(time, metric_values, smooth=True)
    abs_derivative = np.abs(derivative)

    # Set adaptive thresholds based on sensitivity
    sensitivity_map = {
        "low": 99,  # Only top 1% peaks
        "medium": 95,  # Top 5% peaks
        "high": 90,  # Top 10% peaks
    }

    percentile_threshold = sensitivity_map.get(sensitivity, 95)
    height_threshold = np.percentile(abs_derivative, percentile_threshold)

    # Calculate prominence threshold (relative to data range)
    prominence_threshold = 0.5 * height_threshold

    # Minimum distance: ~10% of data length or at least 10 points
    min_distance = max(10, len(time) // 10)

    print(f"  Auto-detection parameters (sensitivity='{sensitivity}'):")
    print(f"    Height threshold: {height_threshold:.6e}")
    print(f"    Prominence threshold: {prominence_threshold:.6e}")
    print(f"    Min distance: {min_distance} points")

    # Find peaks
    peaks, properties = detect_peaks(
        abs_derivative,
        prominence=prominence_threshold,
        height=height_threshold,
        distance=min_distance,
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


def analyze_metric_transitions(df, metric_name, sensitivity="medium"):
    """
    Analyze transitions for a single metric.

    Args:
        df: DataFrame with 'time (ms)', 'temperature (°C)', and metric columns
        metric_name: Name of the metric column to analyze
        sensitivity: Detection sensitivity ('low', 'medium', 'high')

    Returns:
        results: Dictionary with derivative, abs_derivative, and peaks_info
    """
    time = df["time (ms)"].values
    temp = df["temperature (°C)"].values
    metric = df[metric_name].values

    # Auto-detect transition points
    derivative, abs_derivative, peaks_info = auto_detect_peaks(
        time, metric, temp, sensitivity=sensitivity
    )

    results = {
        "derivative": derivative,
        "abs_derivative": abs_derivative,
        "peaks_info": peaks_info,
        "time": time,
        "temperature": temp,
        "metric_values": metric,
    }

    return results


def print_transition_summary(
    metric_name, derivative, abs_derivative, peaks_info, metric_values
):
    """
    Print summary statistics and detected transitions for a metric.

    Args:
        metric_name: Name of the metric
        derivative: First derivative array
        abs_derivative: Absolute derivative array
        peaks_info: Dictionary with peak information
        metric_values: Original metric values
    """
    # Print derivative statistics
    print(f"\n  Derivative statistics:")
    print(f"    Mean |derivative|: {np.mean(abs_derivative):.6e}")
    print(f"    Std |derivative|: {np.std(abs_derivative):.6e}")
    print(f"    Max |derivative|: {np.max(abs_derivative):.6e}")

    # Print findings
    if len(peaks_info["indices"]) > 0:
        print(f"\n  ✓ Found {len(peaks_info['indices'])} transition point(s):")
        for i, (idx, temp_val, time_val, deriv_val) in enumerate(
            zip(
                peaks_info["indices"],
                peaks_info["temperatures"],
                peaks_info["time"],
                peaks_info["derivative_values"],
            ),
            1,
        ):
            print(f"\n    Transition #{i}:")
            print(f"      Temperature: {temp_val:.2f}°C")
            print(f"      Time: {time_val/1000:.2f}s")
            print(f"      Derivative: {deriv_val:.6e}")
            print(f"      Metric value: {metric_values[idx]:.4f}")
    else:
        print(f"\n  ✗ No transition points detected.")


def create_summary_dataframe(results_dict):
    """
    Create a summary DataFrame of all detected transitions.

    Args:
        results_dict: Dictionary mapping metric names to their analysis results

    Returns:
        summary_df: DataFrame with all transitions
    """
    summary = []

    for metric_name, result in results_dict.items():
        peaks_info = result["peaks_info"]
        metric_values = result["metric_values"]

        if len(peaks_info["indices"]) > 0:
            for i, (idx, temp_val, time_val, deriv_val) in enumerate(
                zip(
                    peaks_info["indices"],
                    peaks_info["temperatures"],
                    peaks_info["time"],
                    peaks_info["derivative_values"],
                ),
                1,
            ):
                summary.append(
                    {
                        "metric": metric_name,
                        "transition_num": i,
                        "temperature": temp_val,
                        "time_s": time_val / 1000,
                        "derivative": deriv_val,
                        "metric_value": metric_values[idx],
                    }
                )

    if summary:
        return pd.DataFrame(summary)
    else:
        return pd.DataFrame()


def analyze_all_metrics(df, sensitivity="medium"):
    """
    Analyze brightness metric in the DataFrame for transition points.

    Note: This function is maintained for backward compatibility but now only
    analyzes the brightness metric. Use analyze_metric_transitions() directly
    for single metric analysis.

    Args:
        df: DataFrame with time, temperature, and brightness columns
        sensitivity: Detection sensitivity ('low', 'medium', 'high')

    Returns:
        results_dict: Dictionary mapping 'brightness' to analysis results
        summary_df: DataFrame with summary of brightness transitions
    """
    # Focus only on brightness metric
    metric_name = "brightness"

    if metric_name not in df.columns:
        print(f"Error: '{metric_name}' column not found in DataFrame")
        return {}, pd.DataFrame()

    print(f"\n{'='*70}")
    print(f"BRIGHTNESS TRANSITION ANALYSIS - Sensitivity: {sensitivity.upper()}")
    print(f"{'='*70}\n")

    print(f"\n{'='*70}")
    print(f"Analyzing: {metric_name}")
    print(f"{'='*70}")

    # Analyze transitions
    results = analyze_metric_transitions(df, metric_name, sensitivity)
    results_dict = {metric_name: results}

    # Print summary
    print_transition_summary(
        metric_name,
        results["derivative"],
        results["abs_derivative"],
        results["peaks_info"],
        results["metric_values"],
    )

    # Create summary DataFrame
    summary_df = create_summary_dataframe(results_dict)

    return results_dict, summary_df
