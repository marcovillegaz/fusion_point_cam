# Installation and Setup

## Package Installation

This project is now a proper Python package! Follow these steps to install and use it:

### 1. Install in Development Mode (Recommended)

From the project root directory, run:

```powershell
pip install -e .
```

The `-e` flag installs the package in "editable" mode, meaning changes to the source code will immediately be reflected without reinstalling.

### 2. Install Normally

If you prefer a standard installation:

```powershell
pip install .
```

### 3. Verify Installation

Test that the package is installed correctly:

```powershell
python -c "import mpc_img_processing; print(mpc_img_processing.__version__)"
```

## Usage

### Running the Image Processing Script

```powershell
python scripts/process_images.py
```

### Running the Analysis Script

```powershell
python merge_and_analyze.py
```

### Using the Package in Your Own Scripts

```python
from mpc_img_processing import ImagePipeline
from mpc_img_processing.utils import (
    crop_image,
    to_grayscale,
    normalize_clahe,
    filter_bright_image,
    brightness_stats,
)

# Create and run your pipeline
pipeline = ImagePipeline(
    experiment_name="my_experiment",
    steps=[
        ("cropped", lambda img: crop_image(img, x=200, y=0, width=400, height=600)),
        ("greyscale", to_grayscale),
        ("normalize", normalize_clahe),
    ],
    prefilter_fn=lambda img: filter_bright_image(img, brightness_threshold=70),
    postprocess_fn=[brightness_stats],
    save_intermediate=True,
)

pipeline.run("input_folder", "output_folder")
```

## Development

### Installing Development Dependencies

```powershell
pip install -e ".[dev]"
```

This installs additional tools like pytest, black, and flake8 for development.

## Package Structure

```
mpc_img_processing/
├── __init__.py          # Main package entry point
├── analysis/            # Analysis and visualization modules
│   ├── compute_stats.py
│   ├── io.py
│   └── plot_results.py
├── classes/             # Core pipeline classes
│   └── imagePipeline.py
└── utils/               # Utility functions
    ├── executor.py
    ├── io.py
    ├── metric_batch.py
    ├── metrics.py
    ├── prefilter.py
    └── steps.py
```

## Migrating from Old Import Syntax

**Old:**
```python
from src.classes.imagePipeline import ImagePipeline
from src.utils.steps import *
```

**New:**
```python
from mpc_img_processing import ImagePipeline
from mpc_img_processing.utils import crop_image, to_grayscale, ...
```
