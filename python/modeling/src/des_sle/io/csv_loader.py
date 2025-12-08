"""
CSV loader for experimental phase diagram data.
"""

import pandas as pd


def load_phase_diagram_csv(filepath):
    """
    Load a CSV file containing columns:
        x ; T   (T in °C)
    Converts T to Kelvin internally.
    """
    df = pd.read_csv(filepath, sep=";", decimal=",")
    df["T"] = df["T"] + 273.15  # convert to Kelvin
    return df["x"].values, df["T"].values


def load_liquidus_curve_csv(filepath):
    """
    Load a liquidus curve CSV file and return as DataFrame.

    Args:
        filepath: Path to CSV file with 'x' and 'T' columns (T in °C)

    Returns:
        DataFrame with 'x' and 'T' columns (T converted to Kelvin)
    """
    df = pd.read_csv(filepath, sep=";", decimal=",")
    df["T"] = df["T"] + 273.15  # convert to Kelvin
    return df


def split_liquidus_curves(liquidus_data, x_eutectic):
    """
    Split liquidus data into two curves based on eutectic composition.

    Args:
        liquidus_data: DataFrame with 'x' and 'T' columns
        x_eutectic: Eutectic composition

    Returns:
        Tuple of (left_curve, right_curve) DataFrames
        - left_curve: x <= x_eutectic (component 2 crystallizes)
        - right_curve: x >= x_eutectic (component 1 crystallizes)
    """
    # Left curve: component 2 crystallizes (lower x values)
    left_curve = liquidus_data[liquidus_data["x"] <= x_eutectic].copy()

    # Right curve: component 1 crystallizes (higher x values)
    right_curve = liquidus_data[liquidus_data["x"] >= x_eutectic].copy()

    return left_curve, right_curve


def find_eutectic_from_data(left_curve, right_curve):
    """
    Determine eutectic point from pre-split curve data.

    Args:
        left_curve: DataFrame with left liquidus curve
        right_curve: DataFrame with right liquidus curve

    Returns:
        Tuple of (x_eutectic, T_eutectic)
    """
    # The eutectic point is where the curves meet
    left_last_x = left_curve.iloc[-1]["x"]
    left_last_T = left_curve.iloc[-1]["T"]
    right_first_x = right_curve.iloc[0]["x"]
    right_first_T = right_curve.iloc[0]["T"]

    # Use the point with minimum temperature as eutectic
    if left_last_T <= right_first_T:
        return left_last_x, left_last_T
    else:
        return right_first_x, right_first_T


def load_eutectic_info(filepath):
    """
    Load eutectic point information from text file.

    Args:
        filepath: Path to eutectic_info.txt file

    Returns:
        Tuple of (x_eutectic, T_eutectic_K) or None if file cannot be read
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if "=" in line]
            x_eutectic = None
            T_eutectic = None

            for line in lines:
                if "x_eutectic" in line:
                    x_eutectic = float(line.split("=")[1].strip())
                elif "T_eutectic" in line and "K" in line:
                    T_eutectic = float(line.split("=")[1].strip().split()[0])

            if x_eutectic is not None and T_eutectic is not None:
                return x_eutectic, T_eutectic
    except Exception:
        pass

    return None
