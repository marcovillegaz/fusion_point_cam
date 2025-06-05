from src.steps import *
from src.postprocess import *
from classes.imagePipeline import *


# Define your pipeline steps
steps = [
    ("cropped", lambda img: crop_image(img, x=200, y=0, width=400, height=600)),
    ("greyscale", to_grayscale),
    ("normalize", normalize_clahe),
    ("blurred", apply_blur),
    ("histogram", lambda img: extract_white_histogram(img, white_threshold=0)),
]

# Optional prefilter
prefilter = lambda img: filter_bright_image(img, brightness_threshold=70)


# Optional postprocess
def save_metrics(metrics):
    return mean_median_brightness(
        metrics, save_path=os.path.join(output_folder, "metrics", "mean_median.csv")
    )


# Instantiate and run pipeline
pipeline = ImagePipeline(
    steps=steps,
    prefilter_fn=prefilter,
    postprocess_fn=save_metrics,
    save_intermediate=False,
)

pipeline.run(input_folder, output_folder)
