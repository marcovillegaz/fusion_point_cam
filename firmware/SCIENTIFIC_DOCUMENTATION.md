# Deep Eutectic Solvent Monitoring System - Technical Documentation

## Executive Summary

This document describes the embedded system designed for automated temperature monitoring and visual documentation of deep eutectic solvent (DES) experiments. The system provides synchronized temperature logging and image capture, enabling correlation between thermal and visual observations during phase transitions and thermal studies.

**Target Audience**: Scientific researchers and article authors  
**Date**: December 8, 2025  
**System Status**: Operational and validated

---

## 1. System Overview

### 1.1 Scientific Purpose

The system monitors thermal properties of deep eutectic solvents with synchronized visual documentation. Key applications include:

- **Phase Transition Studies**: Detecting melting points, crystallization, and phase separations
- **Thermal Stability Assessment**: Long-term temperature monitoring under controlled conditions
- **Visual Documentation**: Capturing changes in appearance, color, and phase state
- **Data Correlation**: Linking temperature data with visual observations

### 1.2 System Capabilities

| Feature                | Specification                     | Scientific Relevance                          |
| ---------------------- | --------------------------------- | --------------------------------------------- |
| Temperature Resolution | 0.0625°C (12-bit)                 | High precision for phase transition detection |
| Temperature Range      | -55°C to +125°C                   | Covers typical DES operating range            |
| Sampling Rate          | Configurable (default: 2 seconds) | Captures transient thermal events             |
| Image Resolution       | Up to 800×600 (SVGA)              | Sufficient for visual phase documentation     |
| Image Format           | JPEG (grayscale)                  | Optimized for contrast in thermal studies     |
| Data Storage           | SD card (CSV + JPEG files)        | Standard formats for analysis software        |
| Steady-State Detection | Variance-based algorithm          | Automated equilibrium identification          |

---

## 2. Hardware Architecture

### 2.1 Core Components

#### ESP32-CAM Module
- **Processor**: ESP32 dual-core 240 MHz
- **Camera**: OV2640 2-megapixel sensor
- **Memory**: 4 MB PSRAM for high-resolution image buffering
- **Storage**: SD card interface (up to 32 GB)

#### DS18B20 Digital Temperature Sensor
- **Interface**: 1-Wire protocol
- **Resolution**: Configurable 9-12 bit (default: 12-bit)
- **Accuracy**: ±0.5°C (-10°C to +85°C)
- **Response Time**: ~750 ms (12-bit mode)
- **Connection**: Requires 4.7kΩ pull-up resistor

### 2.2 GPIO Resource Management

**Critical Design Consideration**: GPIO4 is shared between the temperature sensor and camera flash LED. The system implements careful resource management:

1. Temperature sensor uses GPIO4 as 1-Wire data line
2. Camera disables GPIO4 (flash LED) during operation
3. Explicit initialization/deinitialization cycles prevent conflicts
4. Sequential operation: temperature reading → camera capture

### 2.3 System Block Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       ESP32-CAM                              │
│                                                              │
│  ┌──────────────┐     ┌──────────────┐                     │
│  │ OV2640 Camera│────▶│  Image       │                     │
│  │ Module       │     │  Processing  │────────┐            │
│  └──────────────┘     └──────────────┘        │            │
│                                                 ▼            │
│  ┌──────────────┐     ┌──────────────┐    ┌─────────────┐ │
│  │ DS18B20      │────▶│ Temperature  │───▶│   SD Card   │ │
│  │ Sensor       │     │ Logger       │    │   Storage   │ │
│  │ (GPIO4)      │     └──────────────┘    └─────────────┘ │
│  └──────────────┘                                          │
│                                                             │
│  [User Interface: Serial Monitor @ 115200 baud]            │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Software Architecture

### 3.1 Module Organization

The firmware is organized into modular components, each responsible for specific functionality:

#### CameraManager Module
- **Purpose**: Controls ESP32-CAM OV2640 sensor
- **Key Functions**:
  - Hardware initialization and configuration
  - Image capture in JPEG format
  - Settings persistence via JSON files
  - Resolution adjustment based on PSRAM availability
- **Scientific Configuration**: 
  - Grayscale mode for enhanced contrast
  - Adjustable brightness, contrast, and saturation
  - Horizontal/vertical flip for orientation correction

#### TemperatureSensor Module
- **Purpose**: Interfaces with DS18B20 sensor
- **Key Functions**:
  - 12-bit precision temperature readings
  - Circular buffer for temporal analysis (10 samples)
  - Statistical analysis (mean, variance, slope)
  - Steady-state detection algorithm
- **Scientific Algorithms**:
  - **Variance Calculation**: σ² = E[T²] - (E[T])²
  - **Steady-State Detection**: σ² < 0.01°C²
  - **Linear Regression**: Slope = (nΣxy - ΣxΣy) / (nΣx² - (Σx)²)

#### TemperatureLogger Module
- **Purpose**: In-memory data accumulation
- **Key Functions**:
  - CSV-formatted data buffering
  - Batch writing to reduce SD card wear
  - Timestamp correlation with system clock
- **Output Format**:
  ```
  n, time (ms), temperature (°C)
  1, 2000, 25.34
  2, 4000, 25.56
  ```

#### SDManager Module
- **Purpose**: Persistent data storage
- **Key Functions**:
  - SD card initialization and management
  - CSV log file creation and appending
  - JPEG image storage
  - File system listing and verification
- **Storage Strategy**: 
  - Initialize-use-deinitialize pattern for power efficiency
  - Atomic file operations to prevent corruption

#### WebServerManager Module
- **Purpose**: Network-based remote access (optional)
- **Status**: Currently disabled in production firmware
- **Potential Uses**:
  - Remote experiment monitoring
  - Live camera preview
  - Configuration adjustments
  - Network data access

### 3.2 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Experiment Loop                      │
│                    (Every 2 seconds)                         │
└────────┬─────────────────────────────────────────────┬──────┘
         │                                              │
         ▼                                              │
┌────────────────────┐                                 │
│ Temperature Reading│                                 │
│  1. Init sensor    │                                 │
│  2. Read temp      │                                 │
│  3. Store in buffer│                                 │
│  4. Deinit sensor  │                                 │
└────────┬───────────┘                                 │
         │                                              │
         ▼                                              │
┌────────────────────┐                                 │
│ Log to RAM Buffer  │                                 │
│ (TemperatureLogger)│                                 │
└────────┬───────────┘                                 │
         │                                              │
         │  Every 4 readings (8 seconds)               │
         ▼                                              │
┌────────────────────┐         ┌──────────────────┐   │
│ Write Log to SD    │         │ Capture Image    │   │
│  1. Get buffer     │         │  1. Init camera  │   │
│  2. Append to file │         │  2. Capture frame│   │
│  3. Clear buffer   │         │  3. Save to SD   │   │
│                    │         │  4. Deinit camera│   │
└────────────────────┘         └──────────────────┘   │
         │                              │               │
         └──────────────────┬───────────┘               │
                            │                           │
                            ▼                           │
                  ┌──────────────────┐                 │
                  │    SD Card       │                 │
                  │  - logs.txt      │                 │
                  │  - image_N.jpg   │                 │
                  └──────────────────┘                 │
                            │                           │
                            └───────────────────────────┘
                               Loop continues...
```

---

## 4. Experimental Workflow

### 4.1 Experiment Setup Procedure

1. **Hardware Preparation**
   - Connect DS18B20 sensor with 4.7kΩ pull-up resistor to GPIO4
   - Insert formatted SD card (FAT32, ≤32 GB)
   - Ensure stable power supply (5V via USB or battery)
   - Position camera to view DES sample

2. **System Initialization**
   - Connect to computer via USB
   - Open Serial Monitor at 115200 baud
   - System performs hardware self-check
   - Verify all components initialized successfully

3. **Experiment Naming**
   - System prompts for experiment name
   - Enter descriptive name (e.g., "DES_ChCl_Urea_25C")
   - Name used as base for all data files
   - **Naming Conventions**:
     - Include solvent components
     - Include temperature or date
     - Avoid spaces (use underscores)
     - Keep under 32 characters

4. **Data Collection**
   - System begins automatic data acquisition
   - Temperature readings every 2 seconds
   - Images captured every 4 readings (8 seconds)
   - Progress displayed in Serial Monitor

### 4.2 During Experiment

The system operates autonomously with the following behavior:

**Temperature Monitoring**
- Reads DS18B20 sensor every 2 seconds
- Stores reading in circular buffer (10 samples)
- Appends to in-memory log with timestamp
- Prints reading to Serial Monitor:
  ```
  #5, 10.00 s, 25.67°C
  ```

**Image Capture** (Every 8 seconds by default)
- Temporarily disables temperature sensor
- Initializes camera
- Captures JPEG image
- Saves to SD card: `/N_experimentName.jpg`
- Re-enables temperature sensor

**Data Persistence** (Every 8 seconds)
- Retrieves buffered temperature data
- Appends to CSV file: `/experimentName.txt`
- Clears memory buffer
- Continues monitoring

### 4.3 Data Output Structure

#### Temperature Log File
- **Filename**: `/experimentName.txt`
- **Format**: CSV (Comma-Separated Values)
- **Header**: `n, time (ms), temperature (°C)`
- **Example Content**:
  ```
  n, time (ms), temperature (°C)
  1, 2000, 25.34
  2, 4000, 25.56
  3, 6000, 25.62
  4, 8000, 25.68
  ```

#### Image Files
- **Filename Pattern**: `/N_experimentName.jpg`
  - N = reading number when image was captured
  - Example: `/4_DES_ChCl_Urea.jpg` (captured at reading #4)
- **Format**: JPEG
- **Resolution**: 800×600 pixels (with PSRAM) or 320×240 (without)
- **Color Space**: Grayscale (optimized for contrast)
- **Correlation**: Image number matches temperature reading number

---

## 5. Data Analysis and Interpretation

### 5.1 Temperature Data Processing

#### Importing Data
The CSV format enables direct import into analysis software:

**Python (pandas)**:
```python
import pandas as pd
data = pd.read_csv('DES_ChCl_Urea_25C.txt')
data['time_s'] = data['time (ms)'] / 1000  # Convert to seconds
```

**MATLAB**:
```matlab
data = readtable('DES_ChCl_Urea_25C.txt');
time_s = data.time_ms / 1000;
```

**Excel**:
- File → Open → Select CSV file
- Data automatically formatted with headers

#### Calculating Heating/Cooling Rates
```python
# Calculate temperature change rate (°C/s)
data['rate'] = data['temperature (°C)'].diff() / data['time_s'].diff()
```

#### Identifying Phase Transitions
```python
# Find points where rate changes significantly
import numpy as np
rate_change = np.abs(data['rate'].diff())
transitions = data[rate_change > 0.1]  # Threshold: 0.1 °C/s change
```

### 5.2 Steady-State Detection (NOT REALLY ASK KARIM)

The system implements an automated steady-state detection algorithm based on temperature variance:

**Algorithm**:
1. Maintain circular buffer of 10 recent readings
2. Calculate variance: σ² = Σ(T - T̄)² / n
3. Compare to threshold: σ² < 0.01°C²
4. Flag as steady-state when below threshold

**Scientific Significance**:
- Identifies thermal equilibrium
- Ensures measurements taken at stable conditions
- Improves experimental reproducibility
- Critical for accurate thermodynamic property determination

**Usage in Publications**:
> "Thermal equilibrium was confirmed using an automated variance-based algorithm
> (variance threshold: 0.01°C²) applied to a 10-sample rolling window of temperature
> data acquired at 0.5 Hz."

### 5.3 Image Analysis

#### Time-Lapse Sequence
Images can be combined into time-lapse videos for publications:
```bash
ffmpeg -framerate 2 -pattern_type glob -i '*.jpg' -c:v libx264 timelapse.mp4
```

#### Visual Change Quantification
```python
from skimage import io, color
import numpy as np

# Load sequential images
img1 = io.imread('4_experiment.jpg')
img2 = io.imread('8_experiment.jpg')

# Calculate difference
diff = np.abs(img1.astype(float) - img2.astype(float))
mean_change = np.mean(diff)  # Quantify visual change
```

#### Phase Identification
- Compare images at different temperatures
- Identify crystallization points
- Document color changes
- Detect phase separation

---

## 6. Statistical Methods and Data Quality

### 6.1 Temperature Uncertainty

**Sources of Uncertainty**:
1. **Sensor Accuracy**: ±0.5°C (manufacturer specification)
2. **Digitization Error**: ±0.03125°C (12-bit resolution)
3. **Thermal Lag**: ~750 ms response time
4. **Sampling Variance**: Quantified by rolling buffer

**Combined Uncertainty** (for publication):
```
u(T) = √(u_sensor² + u_digitization² + u_sampling²)
     = √(0.5² + 0.03125² + σ²)
     ≈ 0.5°C (dominated by sensor accuracy)
```

### 6.2 Data Quality Indicators

#### Valid Data Criteria
- Temperature reading > -100°C (excludes sensor errors)
- Temperature within expected range (-50°C to +150°C for DES)
- SD card write successful (verified in firmware)
- Image file size > 0 bytes

#### Data Completeness
```python
# Check for missing data points
expected_readings = (end_time - start_time) / 2000  # 2-second intervals
actual_readings = len(data)
completeness = (actual_readings / expected_readings) * 100
```

### 6.3 Reproducibility Considerations

**Hardware Consistency**:
- Same ESP32-CAM module recommended for series of experiments
- Same DS18B20 sensor for comparative studies
- Consistent camera settings across experiments

**Software Version Control**:
- Firmware version should be recorded for each experiment
- Camera settings (brightness, contrast) should be documented
- Sampling interval should be noted in methodology

**Calibration**:
- DS18B20 sensors are factory-calibrated
- For critical work, verify against reference thermometer
- Camera white balance affects color temperature only (grayscale mode used)

---

## 7. Limitations and Considerations

### 7.1 Hardware Limitations

| Limitation                | Impact                              | Mitigation                                  |
| ------------------------- | ----------------------------------- | ------------------------------------------- |
| GPIO4 sharing             | Sequential temp/image acquisition   | Acceptable for 2-second intervals           |
| SD card wear              | Limited write cycles (~100,000)     | Batch writing reduces operations            |
| PSRAM requirement         | Lower resolution without PSRAM      | QVGA (320×240) still adequate               |
| Single temperature sensor | No spatial temperature distribution | Position sensor in thermal equilibrium zone |
| Temperature response time | 750 ms lag in readings              | Account for lag in fast transient events    |

### 7.2 Software Limitations

**Current Implementation**:
- No real-time data transmission (SD card only)
- No automatic data backup
- Limited error recovery (system halts on critical errors)
- No multi-sensor support
- Web interface disabled in production

**Workarounds**:
- Periodic SD card data backup recommended
- Pre-experiment hardware verification critical
- Single sensor sufficient for bulk DES studies

### 7.3 Experimental Considerations

**Temperature Measurement**:
- Sensor should be fully immersed in DES sample
- Avoid temperature gradients in sample
- Allow thermal equilibration before starting experiment
- Consider ambient temperature effects

**Image Quality**:
- Consistent lighting critical for comparative studies
- Avoid direct sunlight or varying light sources
- Camera should be securely mounted (vibration affects images)
- Transparent/translucent containers recommended

**Data Management**:
- SD card should have sufficient free space
- Recommend ≥1 GB per 24 hours of experiment
- File naming should follow consistent convention
- Backup data immediately after experiment completion

---

## 8. Example Experimental Results Format

### 8.1 Materials and Methods Section

**Suggested Text for Publications**:

> "Temperature monitoring was performed using a DS18B20 digital temperature sensor
> (accuracy: ±0.5°C, resolution: 0.0625°C) connected to an ESP32-CAM microcontroller.
> Temperature readings were acquired at 0.5 Hz (one reading every 2 seconds) and logged
> to an SD card in CSV format. Synchronized visual documentation was achieved using an
> OV2640 camera module (800×600 pixels, grayscale) capturing images every 8 seconds.
> The system implemented automated steady-state detection based on temperature variance
> (threshold: 0.01°C²) calculated over a 20-second rolling window. All data acquisition
> and processing were performed using custom firmware developed for DES characterization."

### 8.2 Results Presentation

**Temperature Profile Figure**:
```
Figure 1: Temperature profile during heating of DES sample (ChCl:Urea, 1:2 molar ratio).
Dashed line indicates steady-state threshold (σ² < 0.01°C²). Phase transition observed
at 42°C (marked with arrow), corresponding to image sequence in Figure 2.
```

**Time-Lapse Figure**:
```
Figure 2: Visual documentation of DES phase transition. Images captured at (a) 25°C,
(b) 40°C, (c) 45°C, and (d) 50°C. Grayscale images show transition from solid to liquid
phase, with complete melting achieved at 45°C.
```

### 8.3 Data Availability Statement

**Suggested Text**:

> "The raw temperature data (CSV format) and time-lapse images (JPEG format) generated
> during this study are available from the corresponding author upon reasonable request.
> The firmware source code is available at [repository URL] under [license]."

---

## 9. Troubleshooting Guide

### 9.1 Common Issues and Solutions

| Issue                                      | Possible Cause                    | Solution                                      |
| ------------------------------------------ | --------------------------------- | --------------------------------------------- |
| "Camera initialization failed"             | Camera module not connected       | Check ribbon cable connection                 |
| "Temperature sensor initialization failed" | Sensor not detected on GPIO4      | Verify wiring and pull-up resistor            |
| "Failed to mount FS"                       | SD card not inserted or corrupted | Insert formatted SD card (FAT32)              |
| Images very dark                           | Low ambient light                 | Increase lighting or adjust camera brightness |
| Temperature reads -127°C                   | Sensor connection issue           | Check wiring and power                        |
| SD card full                               | Insufficient space                | Use larger card or reduce image frequency     |
| System resets randomly                     | Power supply insufficient         | Use 5V 2A power supply                        |

### 9.2 Data Validation Checks

**Before Starting Experiment**:
- [ ] Temperature sensor returns reasonable value (room temp ±5°C)
- [ ] Camera captures test image successfully
- [ ] SD card has sufficient free space (≥1 GB recommended)
- [ ] Serial monitor shows system initialization messages
- [ ] All files listed in SD card directory

**During Experiment**:
- [ ] Temperature readings appear at regular intervals
- [ ] Images save successfully (check file sizes > 0)
- [ ] No error messages in Serial monitor
- [ ] LED activity indicates normal operation

**After Experiment**:
- [ ] CSV file opens correctly in analysis software
- [ ] Number of images matches expected count
- [ ] No gaps in time series data
- [ ] Temperature values within reasonable range

---

## 10. Technical Specifications Summary

### 10.1 System Specifications

| Parameter              | Value                                    |
| ---------------------- | ---------------------------------------- |
| Microcontroller        | ESP32 (dual-core, 240 MHz)               |
| Temperature Sensor     | DS18B20 digital (1-Wire)                 |
| Temperature Range      | -55°C to +125°C                          |
| Temperature Resolution | 0.0625°C (12-bit)                        |
| Temperature Accuracy   | ±0.5°C                                   |
| Sampling Rate          | 0.5 Hz (adjustable)                      |
| Camera Sensor          | OV2640 2MP                               |
| Image Resolution       | 800×600 (SVGA) or 320×240 (QVGA)         |
| Image Format           | JPEG (grayscale)                         |
| Image Frequency        | Every 4 readings (8 seconds, adjustable) |
| Data Storage           | SD/SDHC card (up to 32 GB)               |
| Power Supply           | 5V via USB or battery                    |
| Current Consumption    | ~150 mA (idle), ~300 mA (camera active)  |

### 10.2 Software Specifications

| Component            | Details                                 |
| -------------------- | --------------------------------------- |
| Development Platform | PlatformIO                              |
| Framework            | Arduino for ESP32                       |
| Language             | C++ (C++17 standard)                    |
| Key Libraries        | ArduinoJson, OneWire, DallasTemperature |
| Build System         | PlatformIO (CMake-based)                |
| Upload Method        | USB Serial (115200 baud)                |
| Firmware Size        | ~1 MB (compiled)                        |

---

## 11. Acknowledgments and Credits

### 11.1 Hardware Platform
- **ESP32-CAM**: Espressif Systems
- **OV2640**: OmniVision Technologies
- **DS18B20**: Maxim Integrated (now part of Analog Devices)

### 11.2 Software Libraries
- **ESP32 Camera Driver**: Espressif Systems
- **DallasTemperature**: Miles Burton
- **OneWire**: Paul Stoffregen
- **ArduinoJson**: Benoît Blanchon

### 11.3 Development Tools
- **PlatformIO**: Professional IDE for embedded development
- **VS Code**: Microsoft Visual Studio Code

---

## 12. Contact and Support

### 12.1 For Researchers Using This System

**Technical Questions**: Contact development team
**Collaboration Requests**: Available for joint research projects
**Custom Modifications**: Firmware can be adapted for specific DES studies

### 12.2 Citing This System

**Suggested Citation Format**:

> Author(s). (2025). "Automated Temperature Monitoring and Imaging System for Deep
> Eutectic Solvent Characterization." *Journal Name*, Volume(Issue), Pages.
> DOI: [to be assigned]

**Technical Report Citation**:

> Author(s). (2025). "ESP32-Based Temperature and Imaging System for DES Research:
> Technical Documentation and User Guide." [Institution], Technical Report TR-2025-XX.

---

## Appendix A: Quick Reference Card

### Essential Information for Publications

**System Description (One-Sentence)**:
"An ESP32-based automated system for synchronized temperature logging (0.5 Hz, ±0.5°C) and visual documentation (800×600 grayscale images every 8 seconds) of deep eutectic solvent experiments."

**Temperature Specifications**:
- Sensor: DS18B20 digital thermometer
- Range: -55°C to +125°C
- Resolution: 0.0625°C
- Accuracy: ±0.5°C
- Sampling: 0.5 Hz (2-second intervals)

**Imaging Specifications**:
- Camera: OV2640 2-megapixel sensor
- Resolution: 800×600 pixels (SVGA)
- Format: JPEG grayscale
- Frequency: Every 8 seconds (configurable)

**Data Output**:
- Temperature: CSV format (n, time, temperature)
- Images: JPEG files with correlated timestamps
- Storage: SD card (FAT32)

**Key Algorithms**:
- Steady-state detection: Variance threshold (σ² < 0.01°C²)
- Temporal resolution: 20-second rolling window
- Statistical analysis: Mean, variance, linear regression

---

## Appendix B: Revision History

| Version | Date       | Changes               | Author           |
| ------- | ---------- | --------------------- | ---------------- |
| 1.0     | 2025-12-08 | Initial documentation | Development Team |

---

**End of Technical Documentation**

This document provides comprehensive information for researchers using the DES monitoring system. For code implementation details and improvements, refer to the CODE_IMPROVEMENTS.md document.
