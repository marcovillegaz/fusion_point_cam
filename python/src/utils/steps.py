"""
This module contains functions for image processing steps that can
be incorpored into a larger image processing pipeline.
"""

import os
import cv2
import numpy as np


# Apply grey scale conversion to an image.
def to_grayscale(image):
    print("\tConverting image to grayscale...")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# Correct brightness of an image if it's below a certain threshold.
def brightness_corrector(image, brightness_threshold=100, brightness_boost=50):
    """
    Adjust brightness of an image if it's below the threshold.

    Args:
        img (numpy.ndarray): Input RGB image
        brightness_threshold (int): Threshold for brightness adjustment (0-255)
        brightness_boost (int): Amount to boost brightness (0-100)

    Returns:
        tuple: (adjusted_image, was_adjusted)
               adjusted_image may be the original or brightness-enhanced version
               was_adjusted is a boolean indicating if adjustment was applied
    """

    print("\tChecking image brightness...")
    # Calculate average brightness
    avg_brightness = np.mean(image)

    print(f"\tAverage brightness: {avg_brightness:.1f}")

    if avg_brightness < brightness_threshold:
        print("\tImage is dark, applying brightness adjustment...")
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # Apply brightness boost to the Value channel
        lim = 255 - brightness_boost
        v[v > lim] = 255
        v[v <= lim] += brightness_boost

        # Merge back and convert to BGR
        final_hsv = cv2.merge((h, s, v))
        adjusted_img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

        # calculate new average brightness
        new_avg_brightness = np.mean(cv2.cvtColor(adjusted_img, cv2.COLOR_BGR2GRAY))
        print(f"\tNew average brightness: {new_avg_brightness:.1f}")

        return adjusted_img
    else:
        print("\tImage brightness is sufficient, no adjustment needed.")
        return image


# Apply Gaussian blur to an image.
def apply_blur(image):
    return cv2.bilateralFilter(image, 5, 25, 75)
    # return cv2.GaussianBlur(image, ksize, 0)


# Crop the image to the specified rectangle.
def crop_image(image, x=0, y=0, width=0, height=0):
    """
    Crop the image to the specified rectangle.

    Args:
        image (numpy.ndarray): Input image
        x (int): X coordinate of the top-left corner
        y (int): Y coordinate of the top-left corner
        width (int): Width of the rectangle
        height (int): Height of the rectangle

    Returns:
        numpy.ndarray: Cropped image
    """
    # image size check
    print("Image shape:", image.shape)

    return image[y : y + height, x : x + width]


# Apply binary thresholding to the image.
def threshold_image(image, thresh=100):
    """
    Apply binary thresholding to the image.
    Args:
        image (numpy.ndarray): Input grayscale image
        thresh (int): Threshold value (0-255)
    Returns:
        numpy.ndarray: Binary image after thresholding
    """

    _, binary = cv2.threshold(image, thresh, 255, cv2.THRESH_TOZERO)
    return binary


# --- NORMALIZATION FUNCTIONS ---
def normalize_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).
    Input: grayscale image (uint8). Returns uint8.
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(image)


def normalize_hist_eq(image):
    """
    Apply global histogram equalization to a grayscale image.

    Args:
        image (numpy.ndarray): Grayscale input image (CV_8UC1)

    Returns:
        numpy.ndarray: Normalized image with enhanced contrast
    """
    if len(image.shape) != 2:
        raise ValueError("normalize_hist_eq expects a grayscale image")

    return cv2.equalizeHist(image)
