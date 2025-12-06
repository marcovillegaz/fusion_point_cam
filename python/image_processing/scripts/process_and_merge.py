"""
This script processes multiple experiments in a mixture folder and merges results.

Folder Structure Expected:
mixture_folder/
├── raw/
│   ├── experiment1/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── temp_log.csv (or .txt)
│   └── experiment2/
│       └── ...
├── processed/ (created by script)
│   ├── experiment1/
│   └── experiment2/
└── results/ (created by script)
    ├── experiment1/
    │   ├── brightness_stats.csv
    │   ├── edge_density.csv
    │   └── master_results.csv (merged)
    └── experiment2/
"""

import os
from mpc_img_processing import ImagePipeline
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
from mpc_img_processing.analysis import merge_results


# --- INPUTS ---
working_path = r"C:\Users\marco\OneDrive - usach.cl\Archivos de Alejandro Araya - Eutectic point - Karim\Fotos del paper\Thymol-Ac. Laurico"


# --- IMAGE PROCESSING SETTINGS ---
# Define your filter for images
prefilter = lambda img: filter_bright_image(img, brightness_threshold=70)

# Define your image processing pipeline
steps = [
    ("cropped", lambda img: crop_image(img, x=200, y=0, width=400, height=600)),
    ("greyscale", to_grayscale),
    ("normalize", normalize_clahe),
    ("blurred", apply_blur),
]

# Define your postprocessing metrics
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
raw_folder = os.path.join(working_path, "raw")
experiments = [
    f for f in os.listdir(raw_folder) if os.path.isdir(os.path.join(raw_folder, f))
]

print(f"Found {len(experiments)} experiments to process\n")

# Process each experiment folder
for i, experiment in enumerate(experiments, 1):
    print(f"{'='*70}")
    print(f"[{i}/{len(experiments)}] Processing experiment: {experiment}")
    print(f"{'='*70}")

    # Set up paths
    input_folder = os.path.join(working_path, "raw", experiment)
    processed_folder = os.path.join(working_path, "processed", experiment)
    results_folder = os.path.join(working_path, "results", experiment)

    # Run pipeline with separate results folder
    pipeline.experiment_name = experiment
    pipeline.run(input_folder, processed_folder, results_folder)

    print(f"\n✅ Finished processing experiment: {experiment}")
    print(f"   Processed images → {processed_folder}")
    print(f"   Metrics → {results_folder}")

    # Merge results with temperature log
    print(f"\nMerging results with temperature log...")

    # Look for temperature log file in raw folder
    temp_log_file = None
    for file in os.listdir(input_folder):
        if file.endswith((".txt", ".csv")) and "temp" in file.lower():
            temp_log_file = os.path.join(input_folder, file)
            break

    if temp_log_file and os.path.exists(temp_log_file):
        try:
            merged_df = merge_results(temp_log_file, results_folder, save=True)
            print(f"Results merged successfully!\n")
        except Exception as e:
            print(f"Warning: Could not merge results: {e}\n")
    else:
        print(f"Warning: No temperature log found in {input_folder}\n")

print(f"\n{'='*70}")
print("All experiments processed and merged successfully!")
print(f"{'='*70}")
print(f"\nOutput folders:")
print(f"  Processed images: {os.path.join(working_path, 'processed')}")
print(f"  Results & metrics: {os.path.join(working_path, 'results')}")
