import os
from src.steps import *
from src.postprocess import *
from classes.imagePipeline import *

experiment = "test4"

input_folder = os.path.join("data/raw/images", experiment)
output_folder = os.path.join("data/processed", experiment)


# Define your pipeline steps THis is only image processing
steps = [
    ("cropped", lambda img: crop_image(img, x=200, y=0, width=400, height=600)),
    ("greyscale", to_grayscale),
    ("normalize", normalize_clahe),
    ("blurred", apply_blur),
    # ("histogram", lambda img: extract_white_histogram(img, white_threshold=0)),
]

# Optional prefilter
prefilter = lambda img: filter_bright_image(img, brightness_threshold=70)

# optional post process (extract data from the final image)


""" # Optional postprocess
def save_metrics(metrics):
    return mean_median_brightness(
        metrics, save_path=os.path.join(output_folder, "metrics", "mean_median.csv")
    ) """


# Instantiate and run pipeline
pipeline = ImagePipeline(
    experiment_name=experiment,
    steps=steps,
    prefilter_fn=prefilter,
    save_intermediate=True,
)

pipeline.run(input_folder, output_folder)
