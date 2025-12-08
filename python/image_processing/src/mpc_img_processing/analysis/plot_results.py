"""
Module for plotting analysis results of image processing metrics
"""

import matplotlib.pyplot as plt
import numpy as np
from ..utils.io import load_data
from .compute_stats import smooth_data


def plot_temperature_vs_metric(df, metric_col):
    """
    Plot temperature against a specified metric.
    """
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(df["temperature"], df[metric_col], marker=".")
    ax1.set_xlabel("Temperature °C")
    ax1.set_ylabel(metric_col)
    plt.title(f"Temperature vs {metric_col.capitalize()}")
    plt.grid(True)
    plt.show()


def plot_time_series(df, metric_col):
    """
    Plot time series of temperature and a specified metric.
    """
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.set_xlabel("Time [sec]")

    # Plot temperature on left y-axis
    color1 = "tab:red"
    ax1.set_ylabel("Temperature (°C)", color=color1)
    ax1.plot(df["time"] / 1000, df["temperature"], color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)

    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()

    # Plot metric on right y-axis
    color2 = "tab:green"
    ax2.set_ylabel(metric_col.capitalize(), color=color2)
    ax2.plot(df["time"] / 1000, df[metric_col], color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)

    plt.title(f"Time series of temperature and {metric_col}")
    plt.grid(True)
    plt.show()


def plot_slope_and_peaks(time, slope, peaks):
    """
    Plot the slope of a smoothed metric and highlight detected peaks.
    """
    plt.figure(figsize=(8, 4))
    plt.plot(time[1:], slope, label="Slope")
    plt.scatter(time[1:][peaks], slope[peaks], color="red", label="Peaks")
    plt.xlabel("Time")
    plt.ylabel("Slope")
    plt.title("Slope of Smoothed Metric with Detected Peaks")
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_transition_analysis(df, metric_name, results, save_path=None):
    """
    Create comprehensive plots for transition analysis.

    Args:
        df: DataFrame with data
        metric_name: Name of the metric being analyzed
        results: Dictionary with analysis results (from analyze_metric_transitions)
        save_path: Optional path to save the figure

    Returns:
        fig: Matplotlib figure object
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(f"Transition Analysis: {metric_name}", fontsize=16, fontweight="bold")

    time = results["time"]
    temp = results["temperature"]
    metric = results["metric_values"]
    derivative = results["derivative"]
    abs_derivative = results["abs_derivative"]
    peaks_info = results["peaks_info"]

    # Apply smoothing for visualization
    metric_smooth = smooth_data(metric)

    # Plot 1: Metric vs Time
    ax1 = axes[0, 0]
    ax1.plot(time / 1000, metric, "b-", linewidth=0.8, alpha=0.5, label="Original")
    ax1.plot(time / 1000, metric_smooth, "b-", linewidth=2, label="Smoothed")
    if len(peaks_info["indices"]) > 0:
        ax1.plot(
            peaks_info["time"] / 1000,
            peaks_info["metric_values"],
            "ro",
            markersize=12,
            markeredgewidth=2,
            markeredgecolor="darkred",
            label=f'{len(peaks_info["indices"])} transition(s)',
            zorder=5,
        )
        # Add annotations
        for i, (t, v) in enumerate(
            zip(peaks_info["time"] / 1000, peaks_info["metric_values"])
        ):
            ax1.annotate(
                f"{i+1}",
                xy=(t, v),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=9,
                fontweight="bold",
            )
    ax1.set_xlabel("Time (s)", fontsize=12, fontweight="bold")
    ax1.set_ylabel(metric_name, fontsize=12, fontweight="bold")
    ax1.set_title("Metric vs Time", fontsize=13, fontweight="bold")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    # Plot 2: Metric vs Temperature
    ax2 = axes[0, 1]
    # Color by time to show progression
    scatter = ax2.scatter(
        temp,
        metric,
        c=time / 1000,
        cmap="viridis",
        s=20,
        alpha=0.6,
        label="Data points",
    )
    plt.colorbar(scatter, ax=ax2, label="Time (s)")
    ax2.plot(temp, metric_smooth, "b-", linewidth=2, alpha=0.8, label="Smoothed")

    if len(peaks_info["indices"]) > 0:
        ax2.plot(
            peaks_info["temperatures"],
            peaks_info["metric_values"],
            "ro",
            markersize=14,
            markeredgewidth=2,
            markeredgecolor="darkred",
            label="Transitions",
            zorder=5,
        )
        # Add temperature labels
        for i, (t_val, m_val, temp_val) in enumerate(
            zip(
                peaks_info["time"] / 1000,
                peaks_info["metric_values"],
                peaks_info["temperatures"],
            )
        ):
            ax2.annotate(
                f"{i+1}: {temp_val:.1f}°C",
                xy=(temp_val, m_val),
                xytext=(10, -10),
                textcoords="offset points",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )

    ax2.set_xlabel("Temperature (°C)", fontsize=12, fontweight="bold")
    ax2.set_ylabel(metric_name, fontsize=12, fontweight="bold")
    ax2.set_title("Metric vs Temperature", fontsize=13, fontweight="bold")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=9)

    # Plot 3: First Derivative Analysis
    ax3 = axes[1, 0]
    ax3.plot(
        time / 1000,
        derivative,
        "purple",
        linewidth=1.5,
        alpha=0.6,
        label="d(Metric)/dt",
    )
    ax3.plot(
        time / 1000,
        abs_derivative,
        "orange",
        linewidth=2,
        alpha=0.8,
        label="|d(Metric)/dt|",
    )

    if len(peaks_info["indices"]) > 0:
        ax3.plot(
            peaks_info["time"] / 1000,
            peaks_info["abs_derivative_values"],
            "ro",
            markersize=12,
            markeredgewidth=2,
            markeredgecolor="darkred",
            label="Detected peaks",
            zorder=5,
        )
        # Add vertical lines and shaded regions
        for i, (t, temp_val) in enumerate(
            zip(peaks_info["time"] / 1000, peaks_info["temperatures"])
        ):
            ax3.axvline(x=t, color="red", linestyle="--", alpha=0.5, linewidth=2)
            ax3.axvspan(t - 2, t + 2, alpha=0.2, color="red")
            # Add temperature label on x-axis
            ax3.text(
                t,
                ax3.get_ylim()[0],
                f"{temp_val:.1f}°C",
                rotation=45,
                ha="right",
                fontsize=8,
                color="red",
            )

    ax3.set_xlabel("Time (s)", fontsize=12, fontweight="bold")
    ax3.set_ylabel("Rate of Change", fontsize=12, fontweight="bold")
    ax3.set_title(
        "Derivative Analysis - Peak Detection", fontsize=13, fontweight="bold"
    )
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    ax3.axhline(y=0, color="k", linestyle="-", linewidth=0.5)

    # Plot 4: Temperature Derivative (shows rate of temperature change)
    ax4 = axes[1, 1]
    temp_derivative = np.gradient(temp, time / 1000)  # °C/s
    ax4.plot(time / 1000, temp_derivative, "green", linewidth=2, label="dT/dt (°C/s)")
    ax4.axhline(y=0, color="k", linestyle="-", linewidth=0.5)

    if len(peaks_info["indices"]) > 0:
        # Mark the transitions on temperature derivative plot
        for i, t in enumerate(peaks_info["time"] / 1000):
            ax4.axvline(x=t, color="red", linestyle="--", alpha=0.5, linewidth=2)

    ax4.set_xlabel("Time (s)", fontsize=12, fontweight="bold")
    ax4.set_ylabel("Temperature Rate (°C/s)", fontsize=12, fontweight="bold")
    ax4.set_title("Temperature Change Rate", fontsize=13, fontweight="bold")
    ax4.grid(True, alpha=0.3)
    ax4.legend(fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Saved plot to {save_path}")

    return fig
