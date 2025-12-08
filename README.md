# Deep Eutectic Solvent Fusion Point Monitoring System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: ESP32](https://img.shields.io/badge/Platform-ESP32-blue.svg)](https://www.espressif.com/en/products/socs/esp32)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)

An automated embedded system for detecting melting points and phase transitions in deep eutectic solvents (DES) using synchronized thermal imaging and temperature monitoring.

---

## Overview

This project provides a complete solution for studying thermal properties of deep eutectic solvents and eutectic mixtures through automated data acquisition and analysis. The system consists of three integrated components:

1. **Embedded Hardware System** (ESP32-CAM firmware)
2. **Image Processing & Analysis Pipeline** (Python)
3. **Thermodynamic Modeling Tools** (Python)

The system enables researchers to:
- Automatically monitor temperature and capture synchronized images during thermal experiments
- Process thermal images to extract quantitative metrics (brightness, texture, edges)
- Detect phase transition temperatures through derivative-based analysis
- Model solid-liquid equilibria using NRTL activity coefficient models
- Correlate experimental observations with thermodynamic predictions

### Key Features

- **High-precision temperature logging**: 0.0625°C resolution (DS18B20 sensor, 12-bit)
- **Automated visual documentation**: Synchronized image capture at configurable intervals
- **Steady-state detection**: Automated thermal equilibrium identification
- **Derivative-based transition detection**: Peak detection in brightness derivatives to identify melting points
- **Batch processing capabilities**: Analyze multiple experiments across composition ranges
- **Thermodynamic modeling**: NRTL-based phase diagram generation and parameter fitting
- **Scientific data formats**: CSV outputs compatible with standard analysis software

---

## System Architecture

### Hardware Components

The embedded system is built around an ESP32-CAM module with the following configuration:

```
┌────────────────────────────────────────────────────┐
│              ESP32-CAM Module                      │
│  ┌──────────────┐         ┌──────────────┐       │
│  │   OV2640     │────────▶│   PSRAM      │       │
│  │   Camera     │ Images  │   4 MB       │       │
│  └──────────────┘         └──────────────┘       │
│                                                    │
│  ┌──────────────┐         ┌──────────────┐       │
│  │   DS18B20    │────────▶│   SD Card    │       │
│  │ Temperature  │  Data   │   Storage    │       │
│  │ (GPIO4)      │         └──────────────┘       │
│  └──────────────┘                                 │
└────────────────────────────────────────────────────┘
```

**Key Specifications:**
- **Processor**: ESP32 dual-core @ 240 MHz
- **Camera**: OV2640 2-megapixel sensor (up to 800×600 SVGA)
- **Temperature**: DS18B20 digital sensor (-55°C to +125°C, ±0.5°C accuracy)
- **Storage**: SD card interface (up to 32 GB)
- **Sampling Rate**: Configurable (default: 2 seconds for temperature)

### Software Pipeline

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   ESP32-CAM     │────▶│ Image Processing │────▶│  Thermodynamic  │
│   Firmware      │     │    & Analysis    │     │    Modeling     │
│                 │     │                  │     │                 │
│ • Temperature   │     │ • Brightness     │     │ • NRTL Model    │
│   logging       │     │   extraction     │     │ • SLE Solver    │
│ • Image capture │     │ • Transition     │     │ • Phase         │
│ • SD storage    │     │   detection      │     │   diagrams      │
│                 │     │ • Batch analysis │     │ • Parameter     │
│                 │     │                  │     │   fitting       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
     (Embedded C++)         (Python)                  (Python)
```

---

## Repository Structure

```
fusion_point_cam/
├── firmware/                    # ESP32-CAM embedded system
│   ├── src/                    # Main source files
│   ├── include/                # Header files
│   ├── data/                   # Configuration files (JSON, HTML)
│   ├── platformio.ini          # PlatformIO configuration
│   ├── README.md               # Detailed firmware documentation
│   └── SCIENTIFIC_DOCUMENTATION.md  # Technical/scientific details
│
├── python/
│   ├── image_processing/       # Image analysis package
│   │   ├── src/mpc_img_processing/  # Core processing modules
│   │   ├── scripts/            # Analysis scripts
│   │   ├── data/               # Processed experimental data
│   │   ├── README.md           # Installation and usage guide
│   │   └── METHODOLOGY.md      # Scientific methodology
│   │
│   └── modeling/               # Thermodynamic modeling package
│       ├── src/des_sle/        # SLE modeling modules
│       ├── scripts/            # Fitting and analysis scripts
│       ├── data/               # Experimental and fitted data
│       ├── tests/              # Unit and integration tests
│       └── README.md           # Installation and usage guide
│
└── README.md                   # This file (project overview)
```

---

## Getting Started

### Prerequisites

**Hardware:**
- ESP32-CAM module
- DS18B20 temperature sensor
- MicroSD card (≤32 GB, FAT32 formatted)
- 4.7kΩ pull-up resistor for DS18B20
- USB-to-TTL programmer (e.g., FTDI, CP2102)

**Software:**
- [PlatformIO IDE](https://platformio.org/) or Arduino IDE with ESP32 support
- Python 3.8 or higher
- Git (for cloning the repository)

### Quick Start

#### 1. Clone the Repository

```bash
git clone https://github.com/marcovillegaz/fusion_point_cam.git
cd fusion_point_cam
```

#### 2. Firmware Setup

See detailed instructions in [`firmware/README.md`](firmware/README.md):

```bash
cd firmware
# Configure WiFi credentials in include/secrets.h
# Upload firmware using PlatformIO
pio run --target upload
```

#### 3. Python Environment Setup

**Image Processing:**
```bash
cd python/image_processing
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -e .
```

**Thermodynamic Modeling:**
```bash
cd python/modeling
pip install -e .
```

#### 4. Run an Experiment

1. Power on the ESP32-CAM with SD card inserted
2. Start data acquisition via serial monitor or web interface
3. System automatically logs temperature and captures images
4. Data is saved to SD card in CSV and JPEG formats

#### 5. Process Results

```bash
# Process single experiment
python scripts/process_single_experiment.py --experiment_path data/my_experiment

# Batch analysis across compositions
python scripts/process_multiple_experiments.py --base_dir data/experiments
```

---

## Scientific Applications

This system is designed for research in:

- **Deep Eutectic Solvents (DES)**: Characterization of novel DES formulations
- **Phase Equilibria**: Experimental determination of liquidus and solidus curves
- **Eutectic Point Detection**: Automated identification of eutectic compositions and temperatures
- **Thermal Stability**: Long-term stability studies under controlled thermal conditions
- **Green Chemistry**: Sustainable solvent development and characterization

### Methodology Highlights

- **Derivative-based transition detection**: Identifies melting points by detecting peaks in brightness derivative curves
- **Multi-metric analysis**: Supports brightness, texture, and edge-based metrics for robust detection
- **NRTL activity model**: Industry-standard thermodynamic framework for binary systems
- **Automated parameter fitting**: Curve-by-curve optimization for accurate phase diagram prediction
- **Reproducibility**: Standardized data formats and processing workflows

---

## Documentation

Each component includes comprehensive documentation:

### Firmware
- **[`firmware/README.md`](firmware/README.md)**: Complete hardware setup, software architecture, and usage guide
- **[`firmware/SCIENTIFIC_DOCUMENTATION.md`](firmware/SCIENTIFIC_DOCUMENTATION.md)**: Technical specifications, validation, and scientific methodology

### Image Processing
- **[`python/image_processing/README.md`](python/image_processing/README.md)**: Installation, API reference, and usage examples
- **[`python/image_processing/METHODOLOGY.md`](python/image_processing/METHODOLOGY.md)**: Image processing pipeline and transition detection algorithms

### Thermodynamic Modeling
- **[`python/modeling/README.md`](python/modeling/README.md)**: Package structure, installation, and modeling workflows
- **[`python/modeling/README_PUBLICATION.md`](python/modeling/README_PUBLICATION.md)**: Publication-ready documentation

---

## Example Results

The system has been validated with multiple eutectic mixtures:

| System                    | Composition Range       | Detected Transitions | Phase Diagram |
| ------------------------- | ----------------------- | -------------------- | ------------- |
| Thymol-Lauric Acid        | 0.2 - 0.8 mass fraction | ✓                    | ✓             |
| Thymol-10-Undecenoic Acid | 0.2 - 0.8 mass fraction | ✓                    | ✓             |
| α-Terpineol-Decanoic Acid | 0.2 - 0.8 mass fraction | ✓                    | ✓             |

Sample output includes:
- Temperature-time profiles with steady-state detection
- Brightness-temperature curves with transition markers
- Derivative plots showing melting point peaks
- Experimental vs. modeled phase diagrams

---

## Citation

If you use this system in your research, please cite:

```bibtex
@software{villegas2025fusion,
  author = {Villegas, Marco},
  title = {Deep Eutectic Solvent Fusion Point Monitoring System},
  year = {2025},
  url = {https://github.com/marcovillegaz/fusion_point_cam},
  note = {Automated melting point detection using ESP32-CAM and image processing}
}
```

---

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Guidelines

1. Follow existing code style and documentation standards
2. Include unit tests for new functionality
3. Update relevant README files and documentation
4. Test firmware changes on actual hardware before submitting PRs

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- ESP32-CAM community for hardware support and examples
- OpenCV and NumPy communities for image processing tools
- SciPy developers for optimization and scientific computing libraries

---

## Contact

**Marco Villegas**  
Repository: [https://github.com/marcovillegaz/fusion_point_cam](https://github.com/marcovillegaz/fusion_point_cam)

For questions, issues, or collaboration opportunities, please open an issue on GitHub.

---

## Project Status

**Status**: Active Development  
**Last Updated**: December 2025  
**Version**: 1.0.0

The system is currently operational and has been validated with multiple eutectic systems. Ongoing development includes:
- Web-based real-time monitoring interface
- Additional image processing metrics
- Machine learning-based transition detection
- Extended thermodynamic model support 

To avoid conflict in temeprature reading we use the next approuch: 

Temperature sensor has priorty. When a certain condition is meet, for example steady state or a interval that do not conflict with reading interval, the camera and SD manager are initizalized to take a picture a save it into the SD. At the same time, the buffer of the temperature read at this moment, is append to a txt file wich contain the read temeprature. 