import os
import cv2
import numpy as np
import matplotlib.pyplot as plt


# Correct brightness of an image if it's below a certain threshold.
def brightness_corrector(img, brightness_threshold=100, brightness_boost=50):
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

    # Convert to grayscale for brightness evaluation
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Calculate average brightness
    avg_brightness = np.mean(img_gray)

    print(f"\tAverage brightness: {avg_brightness:.1f}")

    if avg_brightness < brightness_threshold:
        print("\tImage is dark, applying brightness adjustment...")
        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
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
        return img


# Save processed images in organized subfolders based on a dictionary.
def save_images(output_folder, base_name, img_dict):
    """
    Save processed images in organized subfolders based in dictioanry.

    Args:
        output_folder (str): Root output directory
        base_name (str): Base filename without extension
        img_dict (dict): Dictionary of image types and their data
                        Format: {'subfolder': image_data}
    """
    for subfolder, image_data in img_dict.items():
        # Create subfolder if it doesn't exist
        subfolder_path = os.path.join(output_folder, subfolder)
        os.makedirs(subfolder_path, exist_ok=True)
        # Save the image
        output_path = os.path.join(subfolder_path, f"{base_name}.jpg")
        cv2.imwrite(output_path, image_data)


# Preprocess a single image: brightness correction, blur, crop, threshold.
def preprocess_image(
    image_path,
    crop_x1=110,
    crop_x2=290,
    brightness_threshold=100,
    brightness_boost=50,
):
    """
    Processes a single image: brightness correction, blur, crop, threshold.

    Args:
        image_path (str): Path to the image file
        crop_x1, crop_x2, brightness_threshold, brightness_boost: Parameters for processing

    Returns:
        dict: Dictionary with processed image versions
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Apply brightness adjustment using the dedicated function
    adjusted_img = brightness_corrector(img, brightness_threshold, brightness_boost)
    # Convert to grayscale
    gray = cv2.cvtColor(adjusted_img, cv2.COLOR_BGR2GRAY)
    # Apply bilateral filter to reduce noise while preserving edges
    blurred = cv2.bilateralFilter(gray, 5, 25, 75)
    # Crop image to new dimensions
    roi = blurred[:, crop_x1:crop_x2]
    # Threshold to binary image
    _, binary = cv2.threshold(roi, 100, 255, cv2.THRESH_TOZERO)

    return {
        "adjusted": adjusted_img,
        "blurred": blurred,
        "cropped": roi,
        "binary": binary,
    }


# Process all images in a folder and save results in subfolders.
def process_folder(
    input_folder,
    output_folder,
    crop_x1=110,
    crop_x2=290,
    brightness_threshold=100,
    brightness_boost=50,
):
    """
    Processes all images in a folder using process_single_image and saves results.

    Args:
        input_folder (str): Folder with input images
        output_folder (str): Folder where outputs are saved
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_files = [
        f
        for f in os.listdir(input_folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    for image_file in image_files:
        print(f"Processing {image_file}")

        try:
            image_path = os.path.join(input_folder, image_file)
            base_name = os.path.splitext(image_file)[0]

            img_dict = preprocess_image(
                image_path,
                crop_x1,
                crop_x2,
                brightness_threshold,
                brightness_boost,
            )

            save_images(output_folder, base_name, img_dict)

        except Exception as e:
            print(f"\tError processing {image_file}: {str(e)}")


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
