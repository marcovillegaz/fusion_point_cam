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
