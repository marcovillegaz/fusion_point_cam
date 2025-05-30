import os
import cv2


def load_images_from_folder(folder):
    """
    Loads all images from a specified folder and returns their paths.
    Args:
        folder (str): Folder from which images will be loaded
    """

    image_paths = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                image_paths.append(os.path.join(root, file))
    return image_paths


def save_images(output_folder, base_name, images_dict):
    """
    Saves images from a dictionary to a specified output folder.
    Args:
        output_folder (str): Folder where images will be saved
        base_name (str): Base name for the images
        images_dict (dict): Dictionary containing images with names as keys
    """

    # create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through the dictionary and save each image
    for name, img in images_dict.items():
        # save grayscale as PNG, color as JPG
        ext = ".png" if len(img.shape) < 3 else ".jpg"
        # Construct the output path with base name and name
        output_path = os.path.join(output_folder, f"{base_name}_{name}{ext}")
        # Write the image to the output path
        cv2.imwrite(output_path, img)
