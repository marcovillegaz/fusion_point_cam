import os
from src.classes.imagePipeline import ImagePipeline

from src.utils.steps import *
from src.utils.postprocess import *
from src.utils.prefilter import filter_bright_image

# --- INPUTS ---
experiment = "test4"
input_folder = os.path.join("data/raw/images", experiment)
output_folder = os.path.join("data/processed", experiment)

# Define your filter for images
prefilter = lambda img: filter_bright_image(img, brightness_threshold=70)

# Define your image processing pipeline
steps = [
    ("cropped", lambda img: crop_image(img, x=200, y=0, width=400, height=600)),
    ("greyscale", to_grayscale),
    ("normalize", normalize_clahe),
    ("blurred", apply_blur),
]

# Define your postprocessing pipeline
postprocess = lambda results, out_folder: mean_median_brightness(results, out_folder)


# optional post process (extract data from the final image)
def save_metrics(metrics):
    return mean_median_brightness(
        metrics, save_path=os.path.join(output_folder, "metrics", "mean_median.csv")
    )


# Instantiate and run pipeline
pipeline = ImagePipeline(
    experiment_name=experiment,
    steps=steps,
    prefilter_fn=prefilter,
    postprocess_fn=postprocess,
    save_intermediate=True,
)

pipeline.run(input_folder, output_folder)
