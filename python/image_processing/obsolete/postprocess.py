import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from io import BytesIO
from PIL import Image


# Compute mean and median brightness of images.
def mean_median_brightness(images, output_folder):
    """
    Compute mean and median brightness for each image.

    Args:
        images (list of tuples): Each tuple contains (image: np.ndarray, filename: str)
        output_folder (str): output folder where the metric will be saved.

    Returns:
        pd.DataFrame: Columns = ["index", "mean_brightness", "median_brightness"]
    """
    data = []

    for img, filename in images:
        if len(img.shape) != 2:
            raise ValueError("Image must be grayscale for brightness computation")

        index = int(filename.split("_")[0])  # Extract index from filename

        mean_brightness = np.mean(img)
        median_brightness = np.median(img)
        data.append((index, mean_brightness, median_brightness))

        # for debug only
        print(f"{filename}: Average brightness = {mean_brightness:.2f}")

    # generate DataFrame (add column of time, which is contained in basename)
    df = pd.DataFrame(data, columns=["index", "mean_brightness", "median_brightness"])
    df.sort_values("index", inplace=True)
    df.reset_index(drop=True)

    # Save to CSV
    save_path = os.path.join(output_folder, "brightness_metrics.csv")
    df.to_csv(save_path, index=False)
    print(f"Saved brightness metrics to {save_path}")


def compute_edge_density(images, output_folder):
    """
    Compute mean and median brightness for each image.

    Args:
        images (list of tuples): Each tuple contains (image: np.ndarray, filename: str)
        output_folder (str): output folder where the metric will be saved.

    Returns:
        pd.DataFrame: Columns = ["index", "mean_brightness", "median_brightness"]
    """
    rows = []
    for img, filename in images:
        if len(img.shape) != 2:
            raise ValueError("Image must be grayscale for brightness computation")

        # Extract index from filename
        index = int(filename.split("_")[0])

        edges = cv2.Canny(img, 100, 200)
        density = edges.sum() / edges.size
        rows.append({"name": filename, "edge_density": density})

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(output_folder, "edge_density.csv"), index=False)
    return df


def extract_white_histogram(image_path, white_threshold=200):
    """
    Extract histogram of white pixels from a single image.
    Returns histogram array from pixel values 200–255.
    Args:
        image_path (str): Path to the input image
        white_threshold (int): Minimum pixel intensity to consider as "white" (default: 200)

    Returns:
        numpy.ndarray: Histogram of pixel intensities from 200 to 255

    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(
        img, cv2.COLOR_BGR2GRAY
    )  # remove this because the image is in grey

    # Mask to extract only white-ish pixels
    mask = (gray >= white_threshold).astype(np.uint8)

    # Calculate histogram for white pixels only
    hist = cv2.calcHist([gray], [0], mask, [256], [0, 256])
    return hist[white_threshold:]  # Only intensities 200–255


# Plot histogram and save it as a PNG file
def plot_and_save_histogram(hist, filename, output_folder, white_threshold=200):
    """
    Plot the histogram and save it as a PNG file.
    """
    plt.figure()
    plt.plot(range(white_threshold, 256), hist)
    plt.title("Histogram of White Pixels")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.tight_layout()

    plot_path = os.path.join(output_folder, filename)
    plt.savefig(plot_path)
    plt.close()
