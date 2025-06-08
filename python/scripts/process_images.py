import os
from src.classes.imagePipeline import ImagePipeline

from src.utils.steps import *
from obsolete.postprocess import *
from src.utils.prefilter import filter_bright_image

from src.utils.metrics import *


# --- INPUTS ---
experiment = "test4"
input_folder = os.path.join("data", "raw", "images", experiment)
output_folder = os.path.join("data", "processed", experiment)

# Define your filter for images (enhence for more filters)
prefilter = lambda img: filter_bright_image(img, brightness_threshold=70)

# Define your image processing pipeline (OrderedDtct)
steps = [
    ("cropped", lambda img: crop_image(img, x=200, y=0, width=400, height=600)),
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

# Instantiate and run pipeline
pipeline = ImagePipeline(
    experiment_name=experiment,
    steps=steps,
    prefilter_fn=prefilter,
    postprocess_fn=postprocess,
    save_intermediate=True,
)

pipeline.run(input_folder, output_folder)
