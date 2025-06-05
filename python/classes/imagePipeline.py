import os
import cv2
from collections import OrderedDict


class ImagePipeline:
    def __init__(
        self,
        steps,
        prefilter_fn=None,
        postprocess_fn=None,
        save_intermediate=True,
        valid_exts=(".jpg", ".jpeg", ".png", ".bmp"),
    ):
        self.steps = OrderedDict(steps)
        self.prefilter_fn = prefilter_fn
        self.postprocess_fn = postprocess_fn
        self.save_intermediate = save_intermediate
        self.valid_exts = valid_exts
        self.metrics = []

    def load_images(self, folder):
        return [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(self.valid_exts)
        ]

    def run(self, input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        image_paths = self.load_images(input_folder)

        for path in image_paths:
            base_name = os.path.splitext(os.path.basename(path))[0]
            print(f"Processing {base_name}")

            img = cv2.imread(path)
            if img is None:
                print(f"Warning: could not load image {path}")
                continue

            if self.prefilter_fn:
                img = self.prefilter_fn(img)
                if img is None:
                    print("X Image filtered out. Skipping.")
                    continue

            results = self.apply_steps(img)
            if not results:
                continue

            self.save(output_folder, base_name, results)

            if self.postprocess_fn:
                final_image = list(results.values())[-1]
                self.metrics.append((final_image, base_name))

        if self.postprocess_fn:
            return self.postprocess_fn(self.metrics)

    def apply_steps(self, img):
        results = OrderedDict()
        current = img
        for name, fn in self.steps.items():
            current = fn(current)
            if current is None:
                return None  # abort this image
            results[name] = current
        return results

    def save(self, output_folder, base_name, results):
        if self.save_intermediate:
            save_images(output_folder, base_name, results)
        else:
            first_key, first_val = next(iter(results.items()))
            last_key, last_val = next(reversed(results.items()))
            save_images(
                output_folder, base_name, {first_key: first_val, last_key: last_val}
            )
