"""
Batch analysis script for brightness metric across all organized experiments.
Analyzes brightness transitions for all eutectic mixture experiments.
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from mpc_img_processing.utils.io import load_data
from mpc_img_processing.analysis.transition_detection import analyze_metric_transitions
from mpc_img_processing.analysis.plot_results import plot_transition_analysis


def analyze_brightness_batch(experiments_root, output_root, sensitivity="medium"):
    """
    Analyze brightness metric for all experiments in organized_experiments folder.

    Args:
        experiments_root: Root directory containing organized experiment folders
        output_root: Directory to save analysis results
        sensitivity: Detection sensitivity ('low', 'medium', 'high')

    Returns:
        all_results: Dictionary with results for each experiment
        master_summary: DataFrame with all transitions from all experiments
    """
    experiments_path = Path(experiments_root)
    output_path = Path(output_root)

    if not experiments_path.exists():
        print(f"Error: Experiments directory not found: {experiments_path}")
        return {}, pd.DataFrame()

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print("BATCH BRIGHTNESS ANALYSIS")
    print(f"{'='*70}")
    print(f"Experiments root: {experiments_path}")
    print(f"Output directory: {output_path}")
    print(f"Sensitivity: {sensitivity.upper()}")
    print(f"{'='*70}\n")

    all_results = {}
    all_transitions = []

    # Iterate through each eutectic mixture directory
    for mixture_dir in sorted(experiments_path.iterdir()):
        if not mixture_dir.is_dir():
            continue

        mixture_name = mixture_dir.name
        print(f"\n{'='*70}")
        print(f"MIXTURE: {mixture_name}")
        print(f"{'='*70}")

        # Create output subdirectory for this mixture
        output_mixture_dir = output_path / mixture_name
        output_mixture_dir.mkdir(parents=True, exist_ok=True)

        # Find all CSV files in this mixture directory
        csv_files = sorted(mixture_dir.glob("*.csv"))

        if not csv_files:
            print(f"  Warning: No CSV files found in {mixture_dir}")
            continue

        print(f"Found {len(csv_files)} experiment(s)\n")

        # Analyze each experiment
        for csv_file in csv_files:
            experiment_name = csv_file.stem  # Filename without extension

            print(f"Analyzing: {experiment_name}")

            try:
                # Load data
                df = load_data(csv_file)

                # Check if brightness column exists
                if "brightness" not in df.columns:
                    print(
                        f"  Warning: 'brightness' column not found in {csv_file.name}"
                    )
                    continue

                # Analyze brightness transitions
                results = analyze_metric_transitions(df, "brightness", sensitivity)

                # Store results
                all_results[experiment_name] = {
                    "mixture": mixture_name,
                    "file": csv_file,
                    "results": results,
                }

                # Print summary
                peaks_info = results["peaks_info"]
                if len(peaks_info["indices"]) > 0:
                    print(f"  ✓ Found {len(peaks_info['indices'])} transition(s):")
                    for i, (temp_val, time_val) in enumerate(
                        zip(peaks_info["temperatures"], peaks_info["time"] / 1000), 1
                    ):
                        print(
                            f"    {i}. Temperature: {temp_val:.2f}°C, Time: {time_val:.2f}s"
                        )

                        # Collect for master summary
                        all_transitions.append(
                            {
                                "mixture": mixture_name,
                                "experiment": experiment_name,
                                "transition_num": i,
                                "temperature": temp_val,
                                "time_s": time_val,
                                "derivative": peaks_info["derivative_values"][i - 1],
                                "brightness": peaks_info["metric_values"][i - 1],
                            }
                        )
                else:
                    print(f"  ✗ No transitions detected")

                # Create and save plot
                save_path = (
                    output_mixture_dir / f"{experiment_name}_brightness_analysis.png"
                )
                plot_transition_analysis(df, "brightness", results, save_path)

            except Exception as e:
                print(f"  Error processing {csv_file.name}: {e}")
                continue

    # Create master summary DataFrame
    if all_transitions:
        master_summary = pd.DataFrame(all_transitions)
    else:
        master_summary = pd.DataFrame()

    return all_results, master_summary


def create_comparison_plots(all_results, output_path):
    """
    Create comparison plots across all experiments for each mixture.

    Args:
        all_results: Dictionary with results from all experiments
        output_path: Directory to save comparison plots
    """
    print(f"\n{'='*70}")
    print("CREATING COMPARISON PLOTS")
    print(f"{'='*70}")

    # Group experiments by mixture
    by_mixture = {}
    for exp_name, exp_data in all_results.items():
        mixture = exp_data["mixture"]
        if mixture not in by_mixture:
            by_mixture[mixture] = []
        by_mixture[mixture].append((exp_name, exp_data))

    # Create comparison plot for each mixture
    for mixture_name, experiments in by_mixture.items():
        if len(experiments) < 2:
            continue

        print(f"\nCreating comparison for: {mixture_name}")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(
            f"Brightness Comparison - {mixture_name}", fontsize=16, fontweight="bold"
        )

        cmap = plt.get_cmap("tab10")
        colors = [cmap(i) for i in range(len(experiments))]

        for idx, (exp_name, exp_data) in enumerate(sorted(experiments)):
            results = exp_data["results"]
            time = results["time"]
            temp = results["temperature"]
            brightness = results["metric_values"]
            peaks_info = results["peaks_info"]

            # Extract ratio from experiment name
            label = exp_name.split("_")[-1] if "_" in exp_name else exp_name
            color = colors[idx]

            # Plot 1: Brightness vs Time
            ax1.plot(
                time / 1000,
                brightness,
                "-",
                linewidth=2,
                label=f"Ratio {label}",
                color=color,
                alpha=0.7,
            )

            if len(peaks_info["indices"]) > 0:
                ax1.plot(
                    peaks_info["time"] / 1000,
                    peaks_info["metric_values"],
                    "o",
                    markersize=8,
                    color=color,
                    markeredgecolor="black",
                    markeredgewidth=1.5,
                )

            # Plot 2: Brightness vs Temperature
            ax2.plot(
                temp,
                brightness,
                "-",
                linewidth=2,
                label=f"Ratio {label}",
                color=color,
                alpha=0.7,
            )

            if len(peaks_info["indices"]) > 0:
                ax2.plot(
                    peaks_info["temperatures"],
                    peaks_info["metric_values"],
                    "o",
                    markersize=8,
                    color=color,
                    markeredgecolor="black",
                    markeredgewidth=1.5,
                )

        # Configure axes
        ax1.set_xlabel("Time (s)", fontsize=12, fontweight="bold")
        ax1.set_ylabel("Brightness", fontsize=12, fontweight="bold")
        ax1.set_title("Brightness vs Time", fontsize=13, fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.legend(fontsize=9)

        ax2.set_xlabel("Temperature (°C)", fontsize=12, fontweight="bold")
        ax2.set_ylabel("Brightness", fontsize=12, fontweight="bold")
        ax2.set_title("Brightness vs Temperature", fontsize=13, fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=9)

        plt.tight_layout()

        # Save comparison plot
        save_path = output_path / f"{mixture_name}_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"  Saved: {save_path.name}")
        plt.close()


def main():
    """Main function."""
    # Define paths
    experiments_root = (
        Path(__file__).parent.parent / "data" / "organized_experiments_metrics"
    )
    output_root = Path(__file__).parent.parent / "data" / "brightness_analysis"

    # Run batch analysis
    all_results, master_summary = analyze_brightness_batch(
        experiments_root=experiments_root,
        output_root=output_root,
        sensitivity="medium",  # Options: 'low', 'medium', 'high'
    )

    # Save master summary
    if not master_summary.empty:
        print(f"\n{'='*70}")
        print("MASTER SUMMARY - ALL TRANSITIONS")
        print(f"{'='*70}\n")
        print(master_summary.to_string(index=False))

        summary_path = output_root / "master_brightness_summary.csv"
        master_summary.to_csv(summary_path, index=False)
        print(f"\nMaster summary saved to: {summary_path}")
    else:
        print("\nNo transitions detected in any experiment.")

    # Create comparison plots
    if all_results:
        create_comparison_plots(all_results, output_root)

    print(f"\n{'='*70}")
    print("BATCH ANALYSIS COMPLETE!")
    print(f"{'='*70}")
    print(f"Total experiments analyzed: {len(all_results)}")
    print(f"Total transitions found: {len(master_summary)}")
    print(f"Results saved to: {output_root}")
    print(f"{'='*70}\n")

    plt.show()


if __name__ == "__main__":
    main()
