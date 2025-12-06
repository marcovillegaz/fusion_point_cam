"""
Here are function that merge temperature log and metrics into a single dataframe
and save it to a CSV file for further analisis
"""

import os
import pandas as pd


def merge_results(temp_log_path, metrics_path, save_path):
    """This function loads the temperature log and all metric CSVs from a given
    experiment, and merges them into a unified dataframe.

    Args:
        temp_log_path: Path to the temperature log CSV file
        metrics_path: Path to the folder containing metric CSV files
        save_path: Path to save the merged results CSV file

    Returns:
        DataFrame with merged temperature and metric data
    """

    print(f"Loading temp log data from: {temp_log_path}")

    os.makedirs(save_path, exist_ok=True)

    # Load temperature log
    temp_df = pd.read_csv(temp_log_path, sep=",", index_col=0)
    temp_df.index.name = "index"  # rename index to match metrics
    print(f"  Temperature log has {len(temp_df)} rows")

    # Get all CSV files from metrics folder
    metric_files = [f for f in os.listdir(metrics_path) if f.endswith(".csv")]
    print(f"Found {len(metric_files)} metric files to merge")

    metric_dfs = []
    all_metric_indexes = set()

    # Merge each metric file
    for metric_file in metric_files:
        path = os.path.join(metrics_path, metric_file)
        print(f"  Loading {metric_file}...")

        df = pd.read_csv(path, index_col=0)
        df.index = df.index.astype(int)
        df.index.name = "index"

        metric_dfs.append(df)
        all_metric_indexes.update(df.index)

        print(metric_dfs)

    all_metric_indexes = sorted(all_metric_indexes)
    print(f"Unique metric indexes: {len(all_metric_indexes)}")

    # Keep ONLY temp_log rows that match metric indexes
    filtered_temp_df = temp_df.loc[temp_df.index.isin(all_metric_indexes)]

    print(f"Filtered temp rows kept: {len(filtered_temp_df)}")

    # Merge EVERYTHING by index
    merged = pd.concat([filtered_temp_df] + metric_dfs, axis=1, join="inner")

    print(f"Final merged dataframe has {len(merged)} rows")

    # Save to CSV
    print(merged.head())
    output_path = os.path.join(save_path, "master_results.csv")
    merged.to_csv(output_path, index=False)
    print(f"✅ Merged file saved to: {output_path}")

    return merged
