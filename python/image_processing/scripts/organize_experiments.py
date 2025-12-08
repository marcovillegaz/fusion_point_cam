"""
Script to organize master_results.csv files from multiple eutectic mixture experiments.
Copies files from nested experiment folders and renames them based on mixture and ratio.
"""

import os
import shutil
from pathlib import Path


def sanitize_filename(name):
    """
    Sanitize a string to be used as a safe filename.

    Args:
        name: String to sanitize

    Returns:
        Sanitized string safe for filenames
    """
    # Replace problematic characters
    replacements = {
        " ": "_",
        ".": "_",
        ":": "",
        "/": "_",
        "\\": "_",
        "<": "",
        ">": "",
        '"': "",
        "|": "",
        "?": "",
        "*": "",
    }

    result = name
    for old, new in replacements.items():
        result = result.replace(old, new)

    return result


def extract_ratio_from_path(experiment_path):
    """
    Extract the ratio information from the experiment folder name.

    Args:
        experiment_path: Path object for the experiment folder

    Returns:
        Sanitized ratio string (e.g., "0_2", "0_4")
    """
    folder_name = experiment_path.name
    # Extract ratio from folder names like "Ty-lau 0.2" -> "0_2"
    parts = folder_name.split()
    if len(parts) > 1:
        ratio = parts[-1].replace(".", "_")
        return ratio
    return sanitize_filename(folder_name)


def organize_experiment_results(source_root, output_root):
    """
    Organize master_results.csv files from experiments.

    Args:
        source_root: Root directory containing eutectic mixture folders
        output_root: Destination directory for organized results

    Structure:
        source_root/
            Mixture1/
                results/
                    Experiment1/master_results.csv
                    Experiment2/master_results.csv
            Mixture2/
                ...

        Output:
        output_root/
            Mixture1/
                Mixture1_ratio1.csv
                Mixture1_ratio2.csv
            Mixture2/
                ...
    """
    source_path = Path(source_root)
    output_path = Path(output_root)

    if not source_path.exists():
        print(f"Error: Source directory does not exist: {source_path}")
        return

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Source directory: {source_path}")
    print(f"Output directory: {output_path}")
    print("=" * 70)

    # Track statistics
    total_files = 0
    copied_files = 0

    # Iterate through eutectic mixture directories
    for mixture_dir in source_path.iterdir():
        if not mixture_dir.is_dir():
            continue

        mixture_name = mixture_dir.name
        mixture_name_clean = sanitize_filename(mixture_name)

        print(f"\nProcessing mixture: {mixture_name}")

        # Look for results folder
        results_dir = mixture_dir / "results"

        if not results_dir.exists():
            print(f"  Warning: No 'results' folder found in {mixture_name}")
            continue

        # Create output subdirectory for this mixture
        output_mixture_dir = output_path / mixture_name_clean
        output_mixture_dir.mkdir(parents=True, exist_ok=True)

        # Find all master_results.csv files
        master_results_files = list(results_dir.glob("*/master_results.csv"))

        if not master_results_files:
            print(f"  Warning: No master_results.csv files found in {results_dir}")
            continue

        print(f"  Found {len(master_results_files)} experiment(s)")

        # Copy and rename each file
        for csv_file in master_results_files:
            total_files += 1

            # Get experiment folder name
            experiment_folder = csv_file.parent
            ratio = extract_ratio_from_path(experiment_folder)

            # Create new filename: Mixture_ratio.csv
            new_filename = f"{mixture_name_clean}_{ratio}.csv"
            output_file = output_mixture_dir / new_filename

            try:
                # Copy the file
                shutil.copy2(csv_file, output_file)
                copied_files += 1
                print(f"    ✓ Copied: {experiment_folder.name} -> {new_filename}")
            except Exception as e:
                print(f"    ✗ Error copying {csv_file}: {e}")

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files found: {total_files}")
    print(f"Successfully copied: {copied_files}")
    print(f"Output location: {output_path}")
    print("=" * 70)


def main():
    """Main function."""
    # Define paths
    source_root = r"D:\Users\marco\Desktop\Fotos del paper"
    output_root = (
        Path(__file__).parent.parent / "data" / "organized_experiments_metrics"
    )

    print("Eutectic Mixture Experiment Organizer")
    print("=" * 70)

    organize_experiment_results(source_root, output_root)

    print("\nDone!")


if __name__ == "__main__":
    main()
