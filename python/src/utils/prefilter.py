"""Here are function that are applied as filter befor processing
image using the pipeline"""

import numpy as np


def filter_bright_image(image, brightness_threshold=100):
    """
    Return the image only if its average brightness is above the threshold.

    Args:
        image (numpy.ndarray): Input RGB image
        brightness_threshold (int): Minimum brightness required (0-255)

    Returns:
        numpy.ndarray or None: The image if it meets the brightness requirement; otherwise None
    """
    avg_brightness = np.mean(image)
    print(f"\tAverage brightness: {avg_brightness:.1f}")

    if avg_brightness >= brightness_threshold:
        print("\t✔ Image is bright enough. Keeping it.")
        return image
    else:
        print("\t✘ Image is too dark. Skipping it.")
        return None
