import os

from src.steps import *
from src.utils import process_image_batch
from src.postprocess import *

experiment = r"test4"
input_folder = os.path.join("data", "raw", experiment)
output_folder = os.path.join("data", "processed", experiment)

# process batch of images
process_image_batch(
    input_folder,
    output_folder,
    steps={
        "cropped": lambda img: crop_image(img, x=200, y=0, width=400, height=600),
        "greyscale": to_grayscale,
        "normalize": lambda img: normalize_clahe(img),
        "blurred": apply_blur,
        "histogram": lambda img: extract_white_histogram(img, white_threshold=0),
        # "thresholded": lambda img: threshold_image(img, thresh=150),
    },
    prefilter_fn=lambda img: filter_bright_image(img, brightness_threshold=70),
    postprocess_fn=lambda img: mean_median_brightness(
        img, save_path=os.path.join(output_folder, "metrics", "mean_median.csv")
    ),
    save_intermediate=False,
)

# extract white pixels as number

# create dataframe using log

# create plot of results T,W vs time
