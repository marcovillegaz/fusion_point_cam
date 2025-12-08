# ESP32-CAM Deep Eutectic Solvent Monitoring System

## Overview

This firmware transforms an ESP32-CAM into an automated monitoring system for deep eutectic solvent (DES) experiments. It synchronizes temperature logging with periodic image capture, enabling researchers to correlate thermal data with visual observations during phase transitions and thermal studies.

## What This Firmware Does

The system performs three core functions:
1. **Temperature Monitoring**: Reads temperature from a DS18B20 sensor every 2 seconds with 0.0625°C precision
2. **Visual Documentation**: Captures grayscale images at regular intervals to document visual changes
3. **Data Persistence**: Saves both temperature logs (CSV format) and images (JPEG) to an SD card

### Key Features

- **Automated Data Collection**: Runs autonomously once started, no manual intervention needed
- **Synchronized Logging**: Temperature readings and images are timestamped and correlated
- **Steady-State Detection**: Built-in algorithm identifies when the system reaches thermal equilibrium
- **Resource Management**: Intelligently shares GPIO4 between temperature sensor and camera
- **Flexible Configuration**: Adjustable sampling rates and image capture intervals
- **Scientific Data Format**: CSV output compatible with Excel, Python, MATLAB, etc.

## System Architecture

### Hardware Components

```
┌─────────────────────────────────────────┐
│           ESP32-CAM Module              │
│                                         │
│  ┌──────────┐         ┌─────────────┐  │
│  │ OV2640   │────────▶│   PSRAM     │  │
│  │ Camera   │ Images  │   4 MB      │  │
│  └──────────┘         └─────────────┘  │
│                                         │
│  ┌──────────┐         ┌─────────────┐  │
│  │ DS18B20  │────────▶│  SD Card    │  │
│  │ Sensor   │  Data   │  Storage    │  │
│  │ (GPIO4)  │         └─────────────┘  │
│  └──────────┘                          │
└─────────────────────────────────────────┘
```

### Software Architecture

The firmware is organized into six modular classes:

1. **CameraManager**: Controls the OV2640 camera sensor
   - Initialization and configuration
   - Image capture
   - Settings persistence

2. **TemperatureSensor**: Interfaces with DS18B20 sensor
   - Temperature readings (12-bit precision)
   - Statistical analysis (mean, variance, slope)
   - Steady-state detection

3. **TemperatureLogger**: In-memory data buffering
   - CSV-formatted data accumulation
   - Batch writing to minimize SD card operations

4. **SDManager**: Persistent storage operations
   - File creation and management
   - Temperature log writing
   - Image storage

5. **WebServerManager**: Remote access (optional, currently disabled)
   - Live camera preview
   - Settings adjustment
   - Remote monitoring

6. **WiFiSetup**: Network connectivity (optional)
   - WiFi connection management
   - Static or DHCP IP configuration

## How It Works: The Main Loop Logic

### Initialization (Setup Phase)

```
1. Start Serial Communication (115200 baud)
   ↓
2. User enters experiment name via Serial Monitor
   ↓
3. Create log file on SD card with CSV header
   ↓
4. Test camera initialization → deinitialize
   ↓
5. Initialize temperature sensor
   ↓
6. Begin main monitoring loop
```

### Main Monitoring Loop

The system operates on a time-based cycle that handles GPIO resource conflicts:

```
Every 2 seconds:
┌─────────────────────────────────────────────┐
│ 1. READ TEMPERATURE                         │
│    • Initialize DS18B20 sensor (GPIO4)      │
│    • Read temperature value                 │
│    • Store in circular buffer (10 samples)  │
│    • Add to in-memory log                   │
│    • Deinitialize sensor (release GPIO4)    │
│    • Print reading to Serial Monitor        │
└─────────────────────────────────────────────┘
              ↓
         Every 4 readings (8 seconds):
┌─────────────────────────────────────────────┐
│ 2. SAVE TEMPERATURE LOG                     │
│    • Retrieve buffered temperature data     │
│    • Write to SD card (CSV append)          │
│    • Clear memory buffer                    │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ 3. CAPTURE AND SAVE IMAGE                   │
│    • Initialize camera (GPIO4 available)    │
│    • Capture JPEG image (800×600)           │
│    • Save to SD card with reading number    │
│    • Deinitialize camera (release GPIO4)    │
└─────────────────────────────────────────────┘
              ↓
         Loop continues...
```

## The GPIO4 Resource Challenge

### The Problem
The ESP32-CAM has limited GPIO pins, and **GPIO4 is shared between**:
- **DS18B20 temperature sensor** (1-Wire data line)
- **Camera flash LED** (which must be disabled)

Both peripherals cannot use GPIO4 simultaneously.

### The Solution
The firmware implements a **sequential resource management strategy**:

```
| Time            | GPIO4 User          | Action                 |
| --------------- | ------------------- | ---------------------- |
| 0s              | Temperature         | Read temperature       |
| ↓ Release GPIO4 | Deinitialize sensor |
| 2s              | Temperature         | Read temperature again |
| ↓ Release GPIO4 | Deinitialize sensor |
| 4s              | Temperature         | Read temperature       |
| ↓ Release GPIO4 | Deinitialize sensor |
| 6s              | Temperature         | Read temperature       |
| ↓ Release GPIO4 | Deinitialize sensor |
| 8s              | Camera              | Initialize camera      |
| Camera          | Capture image       |
| ↓ Release GPIO4 | Deinitialize camera |
```

This ensures:
- Temperature sensor has exclusive access during readings
- Camera has exclusive access during captures
- No conflicts or interference
- Both functions work reliably

## Data Output Format

### Temperature Log File
**Filename**: `/experimentName.txt`

**Format**: CSV (Comma-Separated Values)

```csv
n, time (ms), temperature (°C)
1, 2000, 25.34
2, 4000, 25.56
3, 6000, 25.62
4, 8000, 25.68
5, 10000, 25.71
...
```

Where:
- `n`: Sequential reading number (1, 2, 3, ...)
- `time (ms)`: Milliseconds since system start
- `temperature (°C)`: DS18B20 reading with 2 decimal places

### Image Files
**Filename Pattern**: `/N_experimentName.jpg`

Example: `/4_DES_ChCl_Urea.jpg` (captured at reading #4)

**Specifications**:
- Format: JPEG
- Color: Grayscale (optimized for contrast)
- Resolution: 800×600 (with PSRAM) or 320×240 (without)
- Frequency: Every 8 seconds (configurable via `PICTURE_INTERVAL`)

### File Correlation
Images and temperature readings are correlated by number:
- Image `/4_experiment.jpg` → Temperature reading #4 at time = 8000 ms
- Image `/8_experiment.jpg` → Temperature reading #8 at time = 16000 ms

## Configuration Options

### Adjustable Parameters (in main.cpp)

```cpp
// Sampling rate
const unsigned long READ_INTERVAL_MS = 2000;  // Temperature reading interval (ms)

// Image capture frequency
const int PICTURE_INTERVAL = 4;  // Take picture every N readings

// GPIO assignment
#define TEMP_SENSOR_PIN 4  // DS18B20 data pin
```

### Temperature Sensor Settings (TemperatureSensor.h)

```cpp
#define BUFFER_SIZE 10          // Samples for statistical analysis
#define VARIANCE_THRESHOLD 0.01 // Steady-state detection threshold (°C²)
```

## Steady-State Detection Algorithm

The system implements a variance-based algorithm to detect when the temperature has stabilized:

### How It Works

1. **Circular Buffer**: Maintains last 10 temperature readings
2. **Variance Calculation**: Computes σ² = E[T²] - (E[T])²
3. **Threshold Comparison**: If σ² < 0.01°C², steady-state detected
4. **Scientific Value**: Identifies when system has reached equilibrium

### Example Application

```
Time    Temp (°C)    Variance    State
--------------------------------
0s      25.1         0.15        Transient
10s     25.3         0.08        Transient
20s     25.4         0.02        Transient
30s     25.4         0.008       Steady-State ✓
```

## Usage Example

### 1. Hardware Setup
- Connect DS18B20 to GPIO4 with 4.7kΩ pull-up resistor
- Insert formatted SD card (FAT32)
- Connect ESP32-CAM to computer via USB

### 2. Start Experiment
- Open Serial Monitor at 115200 baud
- System prompts: `>>> Enter the experiment name:`
- Enter name: `DES_ChCl_Urea_25C`
- Press Enter

### 3. System Operation
```
========== SYSTEM LOG START ==========

>>> Enter the experiment name:
DES_ChCl_Urea_25C
[SETUP] Experiment name set to: DES_ChCl_Urea_25C
[SETUP] Creating log file: /DES_ChCl_Urea_25C.txt
>>> Listing directory contents:
    FILE: DES_ChCl_Urea_25C.txt  SIZE: 35
[CAMERA] Camera initialized successfully

#1, 2.00 s, 25.34°C
#2, 4.00 s, 25.56°C
#3, 6.00 s, 25.62°C
#4, 8.00 s, 25.68°C
[SD Manager] Temperature log saved to: /DES_ChCl_Urea_25C.txt
[SD Manager] Image saved to: /4_DES_ChCl_Urea_25C.jpg
...
```

### 4. Data Retrieval
Remove SD card and copy files:
- `/DES_ChCl_Urea_25C.txt` → Open in Excel, Python, MATLAB
- `/4_DES_ChCl_Urea_25C.jpg`, `/8_DES_ChCl_Urea_25C.jpg`, ... → View/analyze images

## Technical Specifications

| Parameter                  | Value                      |
| -------------------------- | -------------------------- |
| **Microcontroller**        | ESP32 dual-core @ 240 MHz  |
| **Temperature Sensor**     | DS18B20 digital (1-Wire)   |
| **Temperature Range**      | -55°C to +125°C            |
| **Temperature Resolution** | 0.0625°C (12-bit)          |
| **Temperature Accuracy**   | ±0.5°C                     |
| **Sampling Rate**          | 0.5 Hz (configurable)      |
| **Camera**                 | OV2640 2MP                 |
| **Image Resolution**       | 800×600 or 320×240         |
| **Storage**                | SD/SDHC card (up to 32 GB) |
| **Power**                  | 5V via USB                 |

## Dependencies

The firmware requires these libraries (automatically managed by PlatformIO):
- **Arduino Framework for ESP32**
- **ArduinoJson** (v7.4.1+) - JSON configuration files
- **OneWire** (v2.3.8+) - 1-Wire protocol for DS18B20
- **DallasTemperature** (v4.0.4+) - DS18B20 interface

## File Structure

```
firmware/
├── src/
│   ├── main.cpp                    # Main program logic
│   ├── CameraManager.cpp           # Camera control implementation
│   ├── TemperatureSensor.cpp       # Temperature sensor implementation
│   ├── TemperatureLogger.cpp       # Data logging implementation
│   ├── SDManager.cpp               # SD card management
│   ├── WebServerManager.cpp        # Web server (optional)
│   └── wifi_setup.cpp              # WiFi connectivity (optional)
├── include/
│   ├── CameraManager.h             # Camera interface
│   ├── TemperatureSensor.h         # Temperature sensor interface
│   ├── TemperatureLogger.h         # Logger interface
│   ├── SDManager.h                 # SD card interface
│   ├── WebServerManager.h          # Web server interface
│   ├── wifi_setup.h                # WiFi interface
│   └── secrets.h                   # WiFi credentials (not in repo)
├── platformio.ini                  # Build configuration
└── README.md                       # This file
```

## Common Questions

### Q: Why grayscale images instead of color?
**A**: Grayscale provides better contrast for observing phase transitions and uses less storage space.

### Q: Can I change the sampling rate?
**A**: Yes, modify `READ_INTERVAL_MS` in `main.cpp`. Faster sampling = more data = larger files.

### Q: How long can experiments run?
**A**: Limited by SD card size and power supply. A 16GB card can store months of data.

### Q: What if SD card gets full?
**A**: System will continue attempting writes (which fail). Monitor free space for long experiments.

### Q: Can I use this without images?
**A**: Yes, set `PICTURE_INTERVAL` to a very large number (e.g., 1000) to rarely capture images.

## Troubleshooting

| Problem                  | Likely Cause                    | Solution                          |
| ------------------------ | ------------------------------- | --------------------------------- |
| Camera init failed       | Loose ribbon cable              | Reconnect camera module           |
| Temperature reads -127°C | DS18B20 not connected           | Check wiring and pull-up resistor |
| SD card mount failed     | Card not formatted or corrupted | Format as FAT32                   |
| System resets randomly   | Insufficient power              | Use 5V 2A power supply            |

## Future Enhancements

Potential improvements documented in `CODE_IMPROVEMENTS.md`:
- Error recovery and retry mechanisms
- Real-time data upload to cloud
- Multiple temperature sensor support
- Adaptive sampling rates
- Enhanced statistical analysis

## License

[Add your license information here]

## Authors

[Research Team / Your Name]

## Acknowledgments

- ESP32 Arduino Core by Espressif Systems
- DallasTemperature library by Miles Burton
- ArduinoJson by Benoît Blanchon

---

**For detailed scientific documentation**, see `SCIENTIFIC_DOCUMENTATION.md`  
**For code improvement suggestions**, see `CODE_IMPROVEMENTS.md`

