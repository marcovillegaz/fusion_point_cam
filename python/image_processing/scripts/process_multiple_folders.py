"""
This script processes a batch of images using a defined image processing pipeline.
It applies prefiltering, a series of processing steps, and postprocessing metrics,
then saves the results.
"""

import os
from mpc_img_processing.analysis import merge_results
from mpc_img_processing.classes import ImagePipeline

from mpc_img_processing.utils import (
    crop_image,
    to_grayscale,
    normalize_clahe,
    apply_blur,
    filter_bright_image,
    brightness_stats,
    edge_density,
    sharpness_laplacian,
    contrast_rms,
)


# --- INPUTS ---
working_path = r"D:\Users\marco\Desktop\Fotos del paper\Topo-Ac. Decanoico"

# --- IMAGE PROCESSING SETTING ---
# Define your filter for images (enhence for more filters)
prefilter = lambda img: filter_bright_image(img, brightness_threshold=30)

# Define your image processing pipeline (OrderedDtct)
steps = [
    ("cropped", lambda img: crop_image(img, x=200, y=0, width=310, height=540)),
    ("greyscale", to_grayscale),
    ("normalize", normalize_clahe),
    ("blurred", apply_blur),
]

# Define your postprocessing pipeline (list)
postprocess = [
    brightness_stats,
    edge_density,
    sharpness_laplacian,
    contrast_rms,
]

# Instantiate pipeline
pipeline = ImagePipeline(
    steps=steps,
    prefilter_fn=prefilter,
    postprocess_fn=postprocess,
    save_intermediate=True,
)

# Extract experiments list from raw folder
experiments = [
    f
    for f in os.listdir(os.path.join(working_path, "raw"))
    if os.path.isdir(os.path.join(working_path, "raw", f))
]

print(f"Found {len(experiments)} experiments to process\n")

# Process each experiment folder
for experiment in experiments:
    print(f"{'='*60}")
    print(f"Processing experiment: {experiment}")
    print(f"{'='*60}")

    # Set up paths
    input_folder = os.path.join(working_path, "raw", experiment)
    processed_folder = os.path.join(working_path, "processed", experiment)
    metrics_folder = os.path.join(working_path, "metrics", experiment)
    results_folder = os.path.join(working_path, "results", experiment)

    # Run pipeline with separate results folder
    pipeline.experiment_name = experiment
    pipeline.run(input_folder, processed_folder, metrics_folder)

    # Find the temperature log file (unique .txt file in the folder)
    txt_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
    temp_log_file = os.path.join(input_folder, txt_files[0])

    merge_results(temp_log_file, metrics_folder, results_folder)

    print(f"\n✅ Finished processing experiment: {experiment}")
    print(f"   Processed images saved to: {processed_folder}")
    print(f"   Metrics saved to: {metrics_folder}\n")
    print(f" master results.csv created in: {results_folder}")

print(f"\n{'='*60}")
print("All experiments processed successfully!")
print(f"{'='*60}")
