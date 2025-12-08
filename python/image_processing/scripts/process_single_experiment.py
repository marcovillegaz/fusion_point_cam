"""
Reprocess a single experiment using the image pipeline.
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
)

# ============================================================
# --- USER SETTINGS ------------------------------------------
# ============================================================

# Main working directory
working_path = r"D:\Users\marco\Desktop\Fotos del paper\Thymol-Ac. Laurico"

# Set the experiment you want to reprocess
experiment = "Ty-lau 0.8"  # <--- change this

# ============================================================
# --- IMAGE PROCESSING CONFIG --------------------------------
# ============================================================

prefilter = lambda img: filter_bright_image(img, brightness_threshold=30)

steps = [
    ("cropped", lambda img: crop_image(img, x=200, y=300, width=310, height=300)),
    ("greyscale", to_grayscale),
    ("normalize", normalize_clahe),
    ("blurred", apply_blur),
]

postprocess = [brightness_stats]

pipeline = ImagePipeline(
    steps=steps,
    prefilter_fn=prefilter,
    postprocess_fn=postprocess,
    save_intermediate=True,
)

# ============================================================
# --- PATHS FOR THIS EXPERIMENT ------------------------------
# ============================================================

input_folder = os.path.join(working_path, "raw", experiment)
processed_folder = os.path.join(working_path, "processed", experiment)
metrics_folder = os.path.join(working_path, "metrics", experiment)
results_folder = os.path.join(working_path, "results", experiment)

print("=" * 60)
print(f"Reprocessing SINGLE experiment: {experiment}")
print("=" * 60)

# ============================================================
# --- RUN PIPELINE -------------------------------------------
# ============================================================

pipeline.experiment_name = experiment
pipeline.run(input_folder, processed_folder, metrics_folder)

# ============================================================
# --- FIND TEMP LOG ------------------------------------------
# ============================================================

txt_files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]
if not txt_files:
    raise FileNotFoundError(f"No .txt temperature log found in {input_folder}")

temp_log_file = os.path.join(input_folder, txt_files[0])

# ============================================================
# --- MERGE RESULTS ------------------------------------------
# ============================================================

merge_results(temp_log_file, metrics_folder, results_folder)

print("\n✅ Finished reprocessing")
print(f"   Processed images: {processed_folder}")
print(f"   Metrics:          {metrics_folder}")
print(f"   Results CSV:      {results_folder}")
print("=" * 60)
