import os
import pandas as pd


def load_data(experiment, metric_file, save=None):
    """This function load the temperature log and the metrics a given
    experiment, and merge it into a unified dataframe. The data frame
    could saved (optional)"""

    temp_log_path = os.path.join("data/raw/temp_log", f"{experiment}.txt")
    metrics_path = os.path.join(f"data/processed/{experiment}", metric_file)

    print(f"Loading data from: {temp_log_path}")

    # Load temperature log
    temp_df = pd.read_csv(temp_log_path, sep=",")
    # Load metrics
    metrics_df = pd.read_csv(metrics_path)
    # Merge on the common index
    merged_df = pd.merge(temp_df, metrics_df, on="index")

    # Save to CSV (optional)
    if save:
        output_path = os.path.join("data/merged", experiment)
        merged_df.to_csv(output_path, index=False)
        print(f"✅ Merged file saved to: {output_path}")

    return merged_df
