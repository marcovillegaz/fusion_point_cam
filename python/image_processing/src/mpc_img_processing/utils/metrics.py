"""This script contains function that extracts brightness metrics from images.
This function is used in ImagePipeline Instances"""

import numpy as np

# Metrics return a dict with the metric name as key


def brightness_stats(img):
    """
    Calculate brightness statistics from a grayscale image.

    Args:
        img: Grayscale image array

    Returns:
        dict: Dictionary with 'brightness' (mean) and 'brightness_median' values
    """
    return {
        "brightness": img.mean(),
        "brightness_median": np.median(img),
    }
