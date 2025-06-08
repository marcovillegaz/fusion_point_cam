import pandas as pd


def compute_metric_batch(images, metric_fn):
    """
    Apply a per-image metric_fn to a full batch of images and return a sorted DataFrame.

    Args:
        images (list): List of (img, filename) tuples
        metric_fn (function): Function(img, filename) → dict of metric values

    Returns:
        pd.DataFrame: Sorted DataFrame with columns: index, filename, <metric values...>
    """
    print(f"[POST PROCESS] Computing {metric_fn.__name__} for the image batch")

    rows = []
    for img, filename in images:

        index = int(filename.split("_")[0])

        row = {"index": index}
        row.update(metric_fn(img))  # metric_fn returns dict with column name as key
        rows.append(row)

    df = pd.DataFrame(rows)
    df.sort_values("index", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df
