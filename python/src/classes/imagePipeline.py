import os
import cv2
from collections import OrderedDict

from src.utils.io import save_images
from src.utils.io import get_image_paths

from src.utils.pipeline import execute_pipeline_steps


class ImagePipeline:
    def __init__(
        self,
        experiment_name,
        steps,
        prefilter_fn=None,
        postprocess_fn=None,
        save_intermediate=True,
        valid_exts=(".jpg", ".jpeg", ".png", ".bmp"),
    ):

        # defining attributes
        self.EXPERIMENT_NAME = experiment_name
        self.steps = OrderedDict(steps)
        self.prefilter_fn = prefilter_fn
        self.postprocess_fn = postprocess_fn
        self.save_intermediate = save_intermediate
        self.valid_exts = valid_exts
        self.metrics = []

    # --- METHODS ---

    # RUN THE PAIPLE TO BATCH OF IMAGES
    def run(self, input_folder, output_folder):

        # Create output folders
        os.makedirs(output_folder, exist_ok=True)

        # Get images path
        image_paths = get_image_paths(input_folder, self.valid_exts)

        # apply pipeline for each image in path
        for path in image_paths:
            # Get base name
            base_name = os.path.splitext(os.path.basename(path))[0]
            print(f"Processing {base_name}")

            # open image
            img = cv2.imread(path)
            if img is None:
                print(f"Warning: could not load image {path}")
                continue

            # Apply prefilter pipeline
            if self.prefilter_fn:
                img = self.prefilter_fn(img)
                if img is None:
                    print("X Image filtered out. Skipping.")
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
            return self.postprocess_fn(self.metrics, output_folder)

    # save image processing results.
    def save(self, output_folder, base_name, results):
        if self.save_intermediate:
            save_images(output_folder, base_name, results)
        else:
            first_key, first_val = next(iter(results.items()))
            last_key, last_val = next(reversed(results.items()))
            save_images(
                output_folder, base_name, {first_key: first_val, last_key: last_val}
            )
