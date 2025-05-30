"""
This module contains functions for image processing steps that can
be incorpored into a larger image processing pipeline.
"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


# Apply grey scale conversion to an image.
def to_grayscale(image):
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
def apply_blur(image, ksize=(5, 5)):
    # return cv2.bilateralFilter(image, 5, 25, 75)
    return cv2.GaussianBlur(image, ksize, 0)


# Crop the image to the specified rectangle.
def crop_image(image, x, y, width, height):
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

    _, binary = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)
    return binary
