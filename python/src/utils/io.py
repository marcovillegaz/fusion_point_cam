import os
import cv2


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


def create_gif_from_folder(input_folder, output_path, duration=0.3):
    """
    Create a GIF from all images in the specified folder.

    Args:
        input_folder (str): Folder containing image frames.
        output_path (str): Path to save the output GIF.
        duration (float): Duration per frame in seconds.
    """
    """ valid_exts = (".jpg", ".jpeg", ".png", ".bmp")
    image_files = sorted(
        [
            os.path.join(input_folder, f)
            for f in os.listdir(input_folder)
            if f.lower().endswith(valid_exts)
        ]
    )

    if not image_files:
        print("No valid images found.")
        return

    print(f"Creating GIF with {len(image_files)} frames...")
    images = [imageio.imread(img) for img in image_files]
    imageio.mimsave(output_path, images, duration=duration)
    print(f"GIF saved to {output_path}")
 """
