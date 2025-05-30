import argparse
from src.steps import to_grayscale, apply_blur, threshold_image
from src.executor import run_pipeline
from src.utils import load_images_from_folder, save_images
import os

parser = argparse.ArgumentParser(description="Run image pipeline on folder")
parser.add_argument("input_folder", help="Input folder with images")
parser.add_argument("output_folder", help="Output folder to save results")
args = parser.parse_args()

image_paths = load_images_from_folder(args.input_folder)

# Define your pipeline steps here
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
    print(f"Processed {base_name}")
