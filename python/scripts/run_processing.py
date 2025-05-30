import os
import argparse
from src.steps import to_grayscale, apply_blur, threshold_image
from src.executor import run_pipeline
from src.utils import load_images_from_folder, save_images

experiment = r"test2"
input_folder = os.path.join("data", "images", experiment)

image_paths = load_images_from_folder(input_folder)
print(image_paths)

""" # Define your pipeline steps here
steps = {
    "gray": to_grayscale,
    "blurred": apply_blur,
    "thresholded": threshold_image,
}

for img_path in image_paths:
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    img = cv2.imread(img_path)
    if img is None:
        print(f"Warning: could not load image {img_path}")
        continue
    results = run_pipeline(img, steps)
    save_images(args.output_folder, base_name, results)
    print(f"Processed {base_name}") """
