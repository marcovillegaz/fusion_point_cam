import os
import cv2
import pandas as pd


def get_image_paths(folder, valid_exts=(".jpg", ".jpeg", ".png", ".bmp")):
    """
    Returns a list of valid image file paths in a folder.
    """
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(valid_exts)
    ]


def save_images(output_folder, base_name, images_dict):
    """
    Saves images from a dictionary to a specified output folder.
    Args:
        output_folder (str): Folder where images will be saved
        base_name (str): Base name for the images
        images_dict (dict): Dictionary containing images with names as keys
                         Format: {'subfolder': image_data}
    """

    # create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through the dictionary and save each image
    for name, img in images_dict.items():
        # Create subfolder if it doesn't exist
        subfolder_path = os.path.join(output_folder, name)
        os.makedirs(subfolder_path, exist_ok=True)
        # save grayscale as PNG, color as JPG
        ext = ".png" if len(img.shape) < 3 else ".jpg"
        # Construct the output path with base name and name
        output_path = os.path.join(subfolder_path, f"{base_name}_{name}{ext}")
        # Write the image to the output path
        cv2.imwrite(output_path, img)


def save_metric(df: pd.DataFrame, output_folder: str, metric_name: str):
    """Save a metric DataFrame to CSV."""
    os.makedirs(output_folder, exist_ok=True)
    save_path = os.path.join(output_folder, f"{metric_name}.csv")
    df.to_csv(save_path, index=False)
    print(f"[POST PROCESS] Saved {metric_name} to {save_path}")


def load_data(csv_path):
    """Load the CSV file with metrics data."""
    df = pd.read_csv(csv_path)
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    return df
