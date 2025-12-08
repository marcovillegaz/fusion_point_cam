# Installation and Usage Guide

## Overview

This package (`mpc_img_processing`) automates the detection of melting point transitions in eutectic mixtures using thermal imaging analysis. It processes raw thermal images, extracts brightness metrics, and identifies temperature transition points through derivative-based peak detection.

### What This Package Does

1. **Image Processing**: Converts raw thermal camera images to grayscale, applies filtering, and extracts brightness values
2. **Data Synchronization**: Combines image metrics with temperature measurements to create time-series datasets
3. **Transition Detection**: Identifies melting point temperatures by detecting peaks in brightness derivative
4. **Batch Analysis**: Processes multiple experiments across different eutectic mixture compositions
5. **Visualization**: Generates plots showing brightness vs. time/temperature and detected transition points

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Step 1: Create and Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install the Package

From the project root directory:

```powershell
# Install in editable/development mode (recommended)
pip install -e .
```

The `-e` flag allows you to modify source code without reinstalling.

### Step 3: Verify Installation

```powershell
python -c "import mpc_img_processing; print('Package installed successfully!')"
```

---

## Data Preparation

### Expected Folder Structure

Before running scripts, organize your data as follows:

```
project_root/
├── data/
    ├── images/
        ├── eutectic_mixture/    # e.g., "Thymol-Ac. Laurico" 
            └── experiment_name/    # e.g., "Ty-lau 0.2"
                └── raw
                    ├── image_001.jpg
                    ├── image_002.jpg
                    ├── ...
                    └── temp_log.txt

```

### Temperature Log Format

Temperature logs should be `.txt` files with two columns (tab or space-separated):
```
Time(ms)    Temperature(°C)
0           25.3
100         25.4
200         25.6
...
```

---

## Workflow: Step-by-Step Execution

### **STEP 1: Process Raw Images** (Optional - if you need to extract metrics from images)

If you have raw thermal images and need to extract brightness metrics:

#### For Single Experiment:

```powershell
python scripts/process_single_experiment.py
```

**What to configure:**
- Open `process_single_experiment.py`
- Set `working_path` to your data directory
- Set `experiment` to the folder name you want to process
- Adjust `crop_image()` parameters if needed (x, y, width, height)

#### For Multiple Experiments:

```powershell
python scripts/process_multiple_experiments.py
```

**What to configure:**
- Open `process_multiple_experiments.py`
- Set `working_path` to your data directory (containing multiple experiment folders)
- Adjust processing parameters as needed

**Output:**
- Processed images in `data/processed/{experiment_name}/`
- `master_results.csv` with columns: `time (ms)`, `temperature (°C)`, `brightness`, `brightness_median`

---

### **STEP 2: Organize Experiments** (Required for batch analysis)

This script organizes `master_results.csv` files from multiple experiments into a structured format:

```powershell
python scripts/organize_experiments.py
```

**What to configure:**
- Open `organize_experiments.py`
- Update the `mixtures` dictionary with your experiment paths:

```python
mixtures = {
    "Thymol-Lauric_Acid": r"D:\path\to\Thymol-Ac. Laurico",
    "Your_Mixture_Name": r"D:\path\to\your\mixture\folder",
}
```

**What it does:**
- Searches for `master_results.csv` in each experiment folder
- Copies files to `data/organized_experiments/{mixture_name}/`
- Renames files to `{mixture}_{ratio}.csv` (e.g., `Thymol-Lauric_Acid_0_2.csv`)

**Output:**
```
data/organized_experiments/
├── Thymol-Lauric_Acid/
│   ├── Thymol-Lauric_Acid_0_2.csv
│   ├── Thymol-Lauric_Acid_0_4.csv
│   └── ...
└── Thymol-10_Undecenoic_Acid/
    └── ...
```

---

### **STEP 3: Analyze Brightness Transitions** (Main Analysis)

This is the core analysis that detects melting point transitions:

```powershell
python scripts/analyze_brightness_batch.py
```

**What to configure:**
- Open `analyze_brightness_batch.py`
- Verify paths in the `main()` function:
  - `experiments_root`: Should point to `data/organized_experiments`
  - `output_root`: Where results will be saved (default: `data/brightness_analysis`)
- Adjust `sensitivity` parameter if needed:
  - `"low"`: Only most significant transitions
  - `"medium"`: Balanced detection (default)
  - `"high"`: More sensitive, may detect noise

**What it does:**
1. Loads each organized experiment CSV
2. Calculates brightness derivative with respect to time
3. Applies Savitzky-Golay smoothing to reduce noise
4. Detects peaks in derivative using adaptive thresholds
5. Extracts transition temperatures at peak locations
6. Generates individual plots for each experiment
7. Creates comparison plots grouped by mixture
8. Saves master summary CSV with all detected transitions

**Output:**
```
data/brightness_analysis/
├── master_brightness_summary.csv         # All transitions from all experiments
├── Thymol-Lauric_Acid/
│   ├── Thymol-Lauric_Acid_0_2_analysis.png
│   ├── Thymol-Lauric_Acid_0_4_analysis.png
│   ├── ...
│   └── comparison_plot.png              # Overlay of all ratios
├── Thymol-10_Undecenoic_Acid/
│   └── ...
└── Thymol-Decanoic_Acid/
    └── ...
```

**Understanding the Output:**

`master_brightness_summary.csv` contains:
- `mixture`: Eutectic mixture name
- `experiment`: Specific ratio/experiment
- `transition_num`: Sequential transition number
- `temperature`: Detected transition temperature (°C)
- `time_s`: Time when transition occurred (seconds)
- `derivative`: Brightness derivative magnitude at transition
- `brightness`: Brightness value at transition

---

## Quick Start Example

Complete workflow for new users:

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. If you have organized CSV files already, skip to step 3
# Otherwise, configure and run:
python scripts/organize_experiments.py

# 3. Run brightness analysis (this is the main analysis)
python scripts/analyze_brightness_batch.py

# 4. Check results in data/brightness_analysis/
```

---

## Package Structure

```
mpc_img_processing/
├── __init__.py                      # Package entry point
├── analysis/                        # Analysis modules
│   ├── compute_stats.py            # Derivative calculation, peak detection
│   ├── transition_detection.py     # Core transition detection algorithm
│   ├── plot_results.py             # Visualization functions
│   └── merge_results.py            # Data merging utilities
├── classes/                         # Core classes
│   └── imagePipeline.py            # Image processing pipeline
└── utils/                           # Utility functions
    ├── metrics.py                  # Brightness extraction
    ├── steps.py                    # Image processing steps (grayscale, crop, etc.)
    ├── io.py                       # File I/O operations
    ├── prefilter.py                # Image quality filtering
    └── executor.py                 # Pipeline execution
```

---

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'mpc_img_processing'
```
**Solution:** Make sure you installed the package with `pip install -e .` and activated your virtual environment.

### No CSV Files Found
```
Warning: No CSV files found in {directory}
```
**Solution:** 
1. Check that `master_results.csv` exists in your experiment folders
2. Verify paths in `organize_experiments.py` are correct
3. Run image processing scripts first if you don't have CSV files

### No Transitions Detected
```
Warning: No transition points detected.
```
**Solution:**
1. Try changing sensitivity from `"medium"` to `"high"` in `analyze_brightness_batch.py`
2. Check that your CSV has valid `brightness` and `temperature (°C)` columns
3. Verify temperature actually changes during the experiment

### Column Name Errors
```
KeyError: 'brightness' or 'temperature (°C)'
```
**Solution:** Ensure your CSV has correct column names with proper spacing and capitalization.

---

## Advanced Usage

### Using the Package in Custom Scripts

```python
from mpc_img_processing.analysis.transition_detection import analyze_metric_transitions
from mpc_img_processing.utils.io import load_data
import pandas as pd

# Load your data
df = load_data("path/to/your/master_results.csv")

# Analyze brightness transitions
results = analyze_metric_transitions(df, "brightness", sensitivity="medium")

# Access results
peaks_info = results["peaks_info"]
transition_temperatures = peaks_info["temperatures"]
print(f"Detected {len(transition_temperatures)} transitions at: {transition_temperatures}°C")
```

### Customizing the Image Pipeline

```python
from mpc_img_processing import ImagePipeline
from mpc_img_processing.utils import to_grayscale, crop_image, brightness_stats

pipeline = ImagePipeline(
    steps=[
        ("cropped", lambda img: crop_image(img, x=100, y=50, width=300, height=400)),
        ("grayscale", to_grayscale),
    ],
    prefilter_fn=lambda img: img.mean() > 50,  # Custom brightness threshold
    postprocess_fn=[brightness_stats],
    save_intermediate=True,
)

pipeline.run("input/folder", "output/folder")
```

---

## Citation

If you use this package in your research, please cite:

```
Marco Villegas (2025). MPC Image Processing: Automated Melting Point Detection 
in Eutectic Mixtures. Version 1.0.
```

---

## Support

For questions or issues:
1. Check the `METHODOLOGY.md` file for detailed scientific methodology
2. Review example scripts in `scripts/` folder
3. Contact: [Your contact information]

---

