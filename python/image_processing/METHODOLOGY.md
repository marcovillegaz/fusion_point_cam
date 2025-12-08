# Methodology: Image Processing and Metric Analysis for Melting Point Detection in Eutectic Mixtures

## Overview

This document describes the computational methodology developed for automated melting point detection in eutectic mixtures using thermal imaging analysis. The approach combines digital image processing with derivative-based transition detection to identify phase change temperatures from time-series thermal camera data.

---

## 1. Image Processing Pipeline

### 1.1 Data Acquisition

Raw thermal images were captured during controlled heating/cooling experiments of eutectic mixtures at different mass ratios. The experimental setup recorded:
- **Temporal resolution**: Images captured at regular intervals
- **Temperature data**: Synchronized temperature measurements logged in parallel
- **Storage format**: Images stored in sequential folders with corresponding temperature logs

### 1.2 Image Processing Steps

A modular image processing pipeline was implemented using the `mpc_img_processing` package. The pipeline consists of the following sequential operations:

#### 1.2.1 Grayscale Conversion
```python
grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
```
- Converts RGB thermal images to single-channel grayscale
- Reduces computational complexity while preserving intensity information
- Output: 8-bit grayscale image (0-255 intensity range)

#### 1.2.2 Brightness Correction (Optional)
Applied to images with insufficient illumination:
```python
if avg_brightness < threshold:
    HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    V_channel = V_channel + brightness_boost
    corrected_image = cv2.cvtColor(HSV, cv2.COLOR_HSV2BGR)
```
- Threshold-based brightness adjustment in HSV color space
- Default threshold: 100 (0-255 scale)
- Ensures consistent image quality across experiments

#### 1.2.3 Image Preprocessing (When Required)
Additional operations applied as needed:
- **Gaussian blur**: Noise reduction using `cv2.GaussianBlur()`
- **Cropping**: Region of interest (ROI) extraction
- **Histogram equalization**: CLAHE (Contrast Limited Adaptive Histogram Equalization)
- **Thresholding**: Binary segmentation for specific applications

### 1.3 Image Quality Control

A brightness-based filtering algorithm was implemented to classify and optionally exclude images:
```python
def filter_bright_image(image, threshold=80):
    avg_brightness = np.mean(image)
    return avg_brightness >= threshold
```
This pre-filter ensures that only images meeting minimum quality criteria are included in subsequent analysis.

---

## 2. Brightness Metric Extraction

The brightness metric was selected as the primary quantitative indicator for detecting phase transitions in eutectic mixtures. This choice was based on preliminary studies showing that brightness variations provide the most reliable signal for melting point determination.

### 2.1 Brightness Calculation

**Mean Brightness**:
$$\text{Brightness} = \frac{1}{N} \sum_{i=1}^{N} I_i$$

where $I_i$ represents pixel intensity values and $N$ is the total number of pixels in the grayscale image.

**Implementation**:
```python
brightness_mean = image.mean()
```

### 2.2 Physical Interpretation

Brightness changes directly correlate with material opacity variations during phase transitions:

1. **Solid Phase**: Crystalline structures exhibit characteristic light scattering patterns, resulting in baseline brightness levels
2. **Transition Zone**: As melting begins, the solid-liquid interface produces rapid brightness fluctuations due to changing optical properties
3. **Liquid Phase**: Homogeneous liquid state typically shows stabilized brightness values distinct from the solid phase

The derivative of brightness with respect to time captures these transition dynamics, with peaks indicating the onset and completion of melting events.

### 2.3 Advantages of Brightness as Primary Metric

- **Sensitivity**: Highly responsive to phase changes in organic compounds
- **Computational efficiency**: Simple mean calculation enables real-time processing
- **Robustness**: Less susceptible to minor image artifacts compared to edge-based metrics
- **Physical relevance**: Direct relationship with material optical properties during phase transitions

---

## 3. Time-Series Analysis and Transition Detection

### 3.1 Data Structure

For each experiment, brightness values were synchronized with temperature measurements to create time-series datasets:

| Time (ms) | Temperature (°C) | Brightness |
| --------- | ---------------- | ---------- |
| t₁        | T₁               | B₁         |
| t₂        | T₂               | B₂         |
| ...       | ...              | ...        |

### 3.2 Signal Smoothing

To reduce measurement noise, Savitzky-Golay filtering was applied:

$$\tilde{y}_i = \sum_{j=-m}^{m} c_j y_{i+j}$$

where $c_j$ are pre-computed coefficients, $m$ is the half-window size, and the filter fits a polynomial of specified order.

**Implementation**:
```python
from scipy.signal import savgol_filter
smoothed_metric = savgol_filter(metric, window_length=11, polyorder=2)
```

**Parameters**:
- Window length: 11 data points
- Polynomial order: 2 (quadratic fit)
- Preserves peak positions while reducing high-frequency noise

### 3.3 First Derivative Calculation

The rate of change of brightness with respect to time was computed using numerical differentiation:

$$\frac{dB}{dt} \approx \frac{B(t_{i+1}) - B(t_{i-1})}{t_{i+1} - t_{i-1}}$$

where $B$ represents the brightness value at time $t$.

**Implementation**:
```python
derivative = np.gradient(smoothed_brightness, time)
abs_derivative = np.abs(derivative)
```

The absolute derivative captures both increasing and decreasing brightness transitions, corresponding to different stages of the melting process.

### 3.4 Peak Detection Algorithm

Transition temperatures were identified by detecting peaks in $\left|\frac{dB}{dt}\right|$ using `scipy.signal.find_peaks` with adaptive thresholds:

$$\text{Peak} \Leftrightarrow \begin{cases}
\left|\frac{dB}{dt}\right|_i > h \\
\text{prominence}_i > p \\
|i - j| > d \text{ for all other peaks } j
\end{cases}$$

**Adaptive thresholds**:
- **Height** ($h$): 95th percentile of $\left|\frac{dB}{dt}\right|$ (medium sensitivity)
- **Prominence** ($p$): $0.5 \times h$ (ensures peaks stand out from baseline)
- **Distance** ($d$): $\max(10, 0.1N)$ where $N$ is data length (prevents false positives)

**Sensitivity levels**:
- **Low**: 99th percentile (only most significant transitions)
- **Medium**: 95th percentile (balanced detection)
- **High**: 90th percentile (sensitive to subtle changes)

**Implementation**:
```python
from scipy.signal import find_peaks

percentile_threshold = 95  # Medium sensitivity
height_threshold = np.percentile(abs_derivative, percentile_threshold)
prominence_threshold = 0.5 * height_threshold
min_distance = max(10, len(time) // 10)

peaks, properties = find_peaks(
    abs_derivative,
    height=height_threshold,
    prominence=prominence_threshold,
    distance=min_distance
)
```

### 3.5 Temperature Assignment

For each detected peak at time $t_{\text{peak}}$, the corresponding transition temperature was extracted:

$$T_{\text{transition}} = T(t_{\text{peak}})$$

This associates derivative maxima with specific temperatures, identifying the thermal conditions where phase changes occur.

---

## 4. Experimental Validation

### 4.1 Eutectic Systems Studied

The methodology was applied to three binary eutectic mixtures:

1. **Thymol - Lauric Acid**
   - Mass ratios tested: 0.2, 0.4, 0.6, 0.8
   
2. **Thymol - 10-Undecenoic Acid**
   - Mass ratios tested: 0.2, 0.4, 0.6, 0.8
   
3. **Thymol - Decanoic Acid**
   - Mass ratios tested: 0.1, 0.2, 0.3, 0.4, 0.6, 0.8

### 4.2 Batch Processing Workflow

1. **Data Organization**: 
   - Raw experimental data from multiple trials organized by mixture and ratio
   - CSV files containing synchronized temperature and metric time-series

2. **Automated Analysis**:
   - Batch processing script (`analyze_brightness_batch.py`) applied to all experiments
   - Brightness metric selected as primary indicator based on its sensitivity to phase transitions

3. **Output Generation**:
   - Individual transition plots for each experiment
   - Comparison plots grouping experiments by mixture type
   - Master summary CSV with all detected transitions

**Total Experiments Processed**: 14  
**Total Transitions Detected**: 29

---

## 5. Statistical Summary

### 5.1 Results Overview

| Mixture                   | Experiments | Transitions Detected |
| ------------------------- | ----------- | -------------------- |
| Thymol-Lauric Acid        | 4           | 7                    |
| Thymol-10-Undecenoic Acid | 4           | 7                    |
| Thymol-Decanoic Acid      | 6           | 15                   |

### 5.2 Typical Transition Characteristics

For the brightness metric:
- **Derivative magnitude range**: 10⁻⁶ to 10⁻⁴ (brightness units/ms)
- **Temperature range**: 6.8°C to 33.8°C (depending on composition)
- **Detection sensitivity**: Peaks with prominence ≥ 50% of 95th percentile derivative

---

## 6. Software Implementation

### 6.1 Package Structure

The analysis pipeline was implemented as a Python package (`mpc_img_processing`) with modular architecture:

```
mpc_img_processing/
├── analysis/
│   ├── compute_stats.py         # Derivative and smoothing functions
│   ├── transition_detection.py  # Peak detection algorithms
│   └── plot_results.py          # Visualization routines
├── utils/
│   ├── steps.py                 # Image processing operations
│   ├── metrics.py               # Metric extraction functions
│   └── io.py                    # Data loading utilities
└── classes/
    └── imagePipeline.py         # Pipeline orchestration
```

### 6.2 Key Dependencies

- **OpenCV (cv2)**: Image processing operations
- **NumPy**: Numerical computations and array operations
- **SciPy**: Signal processing (filtering, peak detection)
- **Pandas**: Time-series data management
- **Matplotlib**: Visualization and plotting

### 6.3 Reproducibility

All analysis scripts are version-controlled and include:
- Fixed random seeds where applicable
- Documented parameter settings
- Automated logging of processing steps
- CSV outputs for external validation

---

## 7. Advantages of the Methodology

1. **Objectivity**: Eliminates subjective visual interpretation of melting points
2. **Automation**: Processes multiple experiments without manual intervention
3. **Sensitivity**: Detects subtle phase transitions via derivative analysis of brightness changes
4. **Reproducibility**: Standardized pipeline ensures consistent results across experiments
5. **Computational efficiency**: Single-metric focus enables rapid processing of large datasets
6. **Scalability**: Batch processing accommodates extensive experimental campaigns
7. **Physical relevance**: Brightness directly reflects optical property changes during phase transitions

---

## 8. Limitations and Future Work

### 8.1 Current Limitations

- **Sampling rate dependency**: Temporal resolution limited by image acquisition frequency
- **Noise sensitivity**: High-frequency noise may require parameter tuning for optimal peak detection
- **Manual parameter selection**: Sensitivity thresholds require initial calibration per experimental setup
- **Illumination variability**: Requires consistent lighting conditions across experiments

### 8.2 Proposed Improvements

1. **Machine learning integration**: Supervised learning to classify transition types and improve detection accuracy
2. **Adaptive filtering**: Dynamic adjustment of smoothing parameters based on signal-to-noise characteristics
3. **Uncertainty quantification**: Confidence intervals for detected transition temperatures using statistical resampling
4. **Real-time processing**: Online analysis during experiments for immediate feedback and adaptive parameter adjustment
5. **Complementary metrics**: Integration of additional optical properties (e.g., texture, color channels) for enhanced robustness

---

## 9. Conclusions

This methodology provides a rigorous, automated approach to melting point determination from thermal imaging data. By combining classical image processing techniques with modern signal analysis, the system achieves reliable phase transition detection across diverse eutectic compositions. The open-source implementation facilitates reproducibility and extension by other researchers investigating thermal properties of phase change materials.

---

## References

**Image Processing**:
- Bradski, G. (2000). The OpenCV Library. *Dr. Dobb's Journal of Software Tools*.

**Signal Processing**:
- Savitzky, A., & Golay, M. J. E. (1964). Smoothing and differentiation of data by simplified least squares procedures. *Analytical Chemistry*, 36(8), 1627-1639.

**Peak Detection**:
- Virtanen, P., et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, 261-272.

**Eutectic Systems**:
- [Domain-specific references to be added based on your research context]

---

*Document prepared by: Marco Villegas*  
*Date: December 7, 2025*  
*Software Version: mpc_img_processing v1.0*
