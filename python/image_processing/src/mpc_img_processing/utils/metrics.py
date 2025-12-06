"""This scripts contains function that extract metrics from images.
This functions are used in ImagePipeline Instances"""

import numpy as np
import cv2

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


def contrast_rms(img):
    return {"contrast_rms": float(np.std(img))}


def sharpness_laplacian(img):
    laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
    return {"sharpness": float(laplacian_var)}
