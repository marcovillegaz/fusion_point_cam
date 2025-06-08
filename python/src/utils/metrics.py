"""This scripts contains function that extract metrics from images.
This functions are used in ImagePipeline Instances"""

import os
import numpy as np
import pandas as pd
import cv2
from src.utils.io import save_metric

# Metrics return a dict with the metric name as key


def brightness_stats(img):
    return {
        "brightness": img.mean(),
        "brightness_median": np.median(img),
    }


def edge_density(img):
    edges = cv2.Canny(img, 100, 200)
    density = edges.sum() / edges.size
    return {"edge_density": density}
