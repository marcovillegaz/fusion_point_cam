"""
Image processing pipeline class
"""

import os
import cv2
from collections import OrderedDict

from ..utils.io import save_images
from ..utils.io import get_image_paths
from ..utils.io import save_metric

from ..utils.executor import execute_pipeline_steps
from ..utils.metric_batch import compute_metric_batch


class ImagePipeline:
    def __init__(
        self,
        steps,
        prefilter_fn=None,
        postprocess_fn=None,
        save_intermediate=True,
        valid_exts=(".jpg", ".jpeg", ".png", ".bmp"),
        experiment_name=None,
    ):

        # defining attributes
        self.experiment_name = experiment_name
        self.steps = OrderedDict(steps)
        self.prefilter_fn = prefilter_fn
        self.postprocess_fn = postprocess_fn
        self.save_intermediate = save_intermediate
        self.valid_exts = valid_exts
        self.metrics = []

    # --- METHODS ---

    # RUN THE PIPELINE TO BATCH OF IMAGES
    def run(self, input_folder, output_folder, results_folder=None):
        """
        Run the image processing pipeline on a batch of images from input_folder
        and save the processed images to output_folder.

        Args:
            input_folder: Path to raw images
            output_folder: Path to save processed images
            results_folder: Optional separate path to save metrics (defaults to output_folder)
        """
        # Reset metrics for this run
        self.metrics = []

        # Create output folders
        os.makedirs(output_folder, exist_ok=True)

        # Use separate results folder if specified
        if results_folder is None:
            results_folder = output_folder
        else:
            os.makedirs(results_folder, exist_ok=True)

        # Get images path
        image_paths = get_image_paths(input_folder, self.valid_exts)
        total_images = len(image_paths)

        # apply pipeline for each image in path
        for idx, path in enumerate(image_paths, 1):
            # Get base name
            base_name = os.path.splitext(os.path.basename(path))[0]
            print(f"[IMG_PIPE] [{idx}/{total_images}] Processing {base_name}")

            # open image
            img = cv2.imread(path)  # pylint: disable=no-member
            if img is None:
                print(
                    f"[IMG_PIPE] [{idx}/{total_images}] Warning: could not load image {path}"
                )
                continue

            # Apply prefilter pipeline
            if self.prefilter_fn:
                img = self.prefilter_fn(img)
                if img is None:
                    print(
                        f"[IMG_PIPE] [{idx}/{total_images}] X Image filtered out. Skipping."
                    )
                    continue

            # Apply image processing pipeline
            results = execute_pipeline_steps(img, self.steps)
            if not results:
                continue

            # Save image processign results
            self.save(output_folder, base_name, results)

            # Create list of tuples for postprocessing pipeline
            if self.postprocess_fn:
                final_image = list(results.values())[-1]
                self.metrics.append((final_image, base_name))

        # Apply post processing to get metric from all the batch (all at once)
        if self.postprocess_fn:
            # postprocess_fn is list of metric functions
            if isinstance(self.postprocess_fn, list):
                for metric_fn in self.postprocess_fn:
                    # apply metric_fn on full batch (self.metrics)
                    df = compute_metric_batch(self.metrics, metric_fn)
                    # save each metric CSV file with metric function's __name__ or a custom name
                    save_metric(df, results_folder, metric_fn.__name__)
            else:
                # postprocess_fn is a single function as before
                return self.postprocess_fn(self.metrics, results_folder)

    # save image processing results. (put in io.py)
    def save(self, output_folder, base_name, results):
        if self.save_intermediate:
            save_images(output_folder, base_name, results)
        else:
            first_key, first_val = next(iter(results.items()))
            last_key, last_val = next(reversed(results.items()))
            save_images(
                output_folder, base_name, {first_key: first_val, last_key: last_val}
            )
