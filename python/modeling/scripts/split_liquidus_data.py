"""
Script to split liquidus data into left and right curves based on eutectic point.
Creates separate CSV files for each curve.
"""

import pandas as pd
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from des_sle.io.csv_loader import split_liquidus_curves


def main():
    """Main function to split liquidus data."""
    # Paths
    base_path = Path(__file__).parent.parent
    input_file = base_path / "data" / "reference_examples" / "liquidus.csv"
    output_dir = base_path / "data" / "experimental_split"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read data
    print(f"Reading data from: {input_file}")
    df = pd.read_csv(input_file, delimiter=";", decimal=",")

    print(f"Total data points: {len(df)}")
    print(f"\nData preview:")
    print(df.head())

    # Find eutectic point (minimum temperature)
    min_idx = df["T"].idxmin()
    x_eutectic = df.loc[min_idx, "x"]
    T_eutectic = df.loc[min_idx, "T"]

    print(f"\nEutectic point identified:")
    print(f"  x_eutectic = {x_eutectic}")
    print(f"  T_eutectic = {T_eutectic} °C")

    # Split data using package function
    left_curve, right_curve = split_liquidus_curves(df, x_eutectic)

    print(f"\nData split:")
    print(f"  Left curve (component 2 crystallizes): {len(left_curve)} points")
    print(f"  Right curve (component 1 crystallizes): {len(right_curve)} points")

    # Save to files
    left_file = output_dir / "liquidus_left.csv"
    right_file = output_dir / "liquidus_right.csv"
    eutectic_file = output_dir / "eutectic_info.txt"

    # Save CSV files (preserve original format)
    left_curve.to_csv(left_file, sep=";", decimal=",", index=False)
    right_curve.to_csv(right_file, sep=";", decimal=",", index=False)

    print(f"\nFiles created:")
    print(f"  {left_file}")
    print(f"  {right_file}")

    # Save eutectic info
    with open(eutectic_file, "w") as f:
        f.write(f"Eutectic Point Information\n")
        f.write(f"==========================\n\n")
        f.write(f"x_eutectic = {x_eutectic}\n")
        f.write(f"T_eutectic = {T_eutectic} °C\n")
        f.write(f"T_eutectic = {T_eutectic + 273.15} K\n\n")
        f.write(f"Left curve points: {len(left_curve)}\n")
        f.write(f"Right curve points: {len(right_curve)}\n")

    print(f"  {eutectic_file}")

    print("\n✓ Data split complete!")


if __name__ == "__main__":
    main()
