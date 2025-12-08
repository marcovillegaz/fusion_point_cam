# Code Improvement Recommendations

## Document Overview

This document provides technical recommendations for improving the deep eutectic solvent (DES) monitoring firmware. These suggestions focus on code quality, maintainability, robustness, and scientific data quality. The current firmware is functional but can be enhanced in several key areas.

**Target Audience**: Developer (Marco)  
**Date**: December 8, 2025  
**Current Status**: Functional firmware, ready for enhancement

---

## Priority Legend
- 🔴 **HIGH**: Critical for reliability or data quality
- 🟡 **MEDIUM**: Important for maintainability and features
- 🟢 **LOW**: Nice-to-have improvements

---

## 1. GPIO Resource Management 🔴 HIGH PRIORITY

### Current Issue
GPIO4 is shared between the DS18B20 temperature sensor and the camera's flash LED. The current implementation uses manual `init()`/`deinit()` cycles, which is error-prone and could lead to conflicts.

### Problems
- Manual resource management scattered across `main.cpp`
- Easy to forget `deinit()` calls
- No automatic cleanup on errors
- Code is tightly coupled to GPIO4 sharing logic

### Recommended Solutions

#### Option A: Resource Guard Pattern (Preferred)
```cpp
class GPIO4Guard {
private:
    enum class Owner { NONE, CAMERA, TEMPERATURE };
    static Owner current_owner;
    
public:
    static bool acquireForCamera();
    static bool acquireForTemperature();
    static void release();
    static bool isAvailable();
};
```

**Benefits**:
- Centralized resource management
- Compile-time safety
- Clear ownership model
- Easy to debug conflicts

#### Option B: RAII (Resource Acquisition Is Initialization)
```cpp
class ScopedCamera {
    CameraManager& cam;
public:
    ScopedCamera(CameraManager& c) : cam(c) { cam.init(); }
    ~ScopedCamera() { cam.deinit(); }
};

// Usage:
{
    ScopedCamera sc(camera);  // Auto-init
    camera.capturePhoto();
}  // Auto-deinit when scope exits
```

**Benefits**:
- Automatic cleanup
- Exception-safe (if exceptions enabled)
- Reduces human error

### Implementation Priority
Implement this before long-term experiments to prevent data loss from GPIO conflicts.

---

## 2. Error Handling and Recovery 🔴 HIGH PRIORITY

### Current Issue
System halts completely on sensor failures (`while(1) delay(100)`). This is problematic for long-duration experiments.

### Problems in Current Code

#### main.cpp Lines 54-59
```cpp
if (!camera.init())
{
    Serial.println("Camera initialization failed!");
    while (1)  // PROBLEM: Infinite loop
        delay(100);
}
```

#### main.cpp Lines 63-69
```cpp
if (!tempSensor.init())
{
    Serial.println("Temperature sensor initialization failed!");
    while (1)  // PROBLEM: Infinite loop
        delay(100);
}
```

### Recommended Solutions

#### 1. Retry Mechanism
```cpp
const int MAX_INIT_RETRIES = 3;
const int RETRY_DELAY_MS = 1000;

bool initializeCamera() {
    for (int attempt = 0; attempt < MAX_INIT_RETRIES; attempt++) {
        if (camera.init()) {
            Serial.println("[OK] Camera initialized");
            return true;
        }
        Serial.printf("[RETRY] Camera init failed, attempt %d/%d\n", 
                      attempt + 1, MAX_INIT_RETRIES);
        delay(RETRY_DELAY_MS);
    }
    return false;
}
```

#### 2. Graceful Degradation
Allow system to continue with reduced functionality:
```cpp
bool cameraAvailable = initializeCamera();
if (!cameraAvailable) {
    Serial.println("[WARNING] Running without camera");
    // Continue with temperature logging only
}
```

#### 3. Runtime Error Recovery
```cpp
// In loop():
if (readCount % PICTURE_INTERVAL == 0 && cameraAvailable) {
    camera_fb_t* fb = camera.capturePhoto();
    if (!fb) {
        Serial.println("[ERROR] Camera capture failed, retrying...");
        camera.deinit();
        delay(500);
        if (!camera.init()) {
            Serial.println("[ERROR] Camera recovery failed");
            cameraAvailable = false;  // Disable camera for this experiment
        }
    }
}
```

### Implementation Priority
Critical for experiments that run overnight or over multiple days.

---

## 3. Data Integrity and Loss Prevention 🔴 HIGH PRIORITY

### Current Issues

#### Issue 1: No Verification of SD Writes
Currently, SD writes return `true/false` but failures are not handled in `main.cpp`.

```cpp
// Current code (main.cpp line 111):
sdManager.saveLog(buffer, "/" + experimentName + ".txt");
// If this fails, data is silently lost!
```

#### Issue 2: Temperature Buffer Loss Risk
If SD write fails, the `tempLogger` buffer is cleared anyway (line 112), losing data permanently.

### Recommended Solutions

#### 1. Verified Writes with Retry
```cpp
bool saveLogWithRetry(const String& logText, const String& filename, int maxRetries = 3) {
    for (int attempt = 0; attempt < maxRetries; attempt++) {
        if (sdManager.saveLog(logText, filename)) {
            return true;  // Success
        }
        Serial.printf("[RETRY] SD write failed, attempt %d/%d\n", attempt + 1, maxRetries);
        delay(500);
    }
    return false;  // All retries failed
}

// Usage:
String buffer = tempLogger.getLog();
if (saveLogWithRetry(buffer, "/" + experimentName + ".txt")) {
    tempLogger.clear();  // Only clear on successful write
    Serial.println("[OK] Temperature log saved");
} else {
    Serial.println("[ERROR] Failed to save temperature log - data retained in buffer");
    // Buffer remains intact for next attempt
}
```

#### 2. Persistent Backup Buffer
```cpp
class PersistentLogger : public TemperatureLogger {
private:
    String backupBuffer;  // Holds failed writes
public:
    void markWriteFailed() {
        backupBuffer += logBuffer;  // Append to backup
    }
    String getWithBackup() {
        return backupBuffer + logBuffer;  // Include old data
    }
    void clearAll() {
        backupBuffer = "";
        clear();
    }
};
```

#### 3. Data Checksums
Add data integrity checking:
```cpp
// In TemperatureLogger::addReading():
void addReading(float temperature, int readCount) {
    String line = String(readCount) + "," + String(millis()) + "," + 
                  String(temperature, 2) + "\n";
    logBuffer += line;
    
    // Calculate simple checksum
    uint32_t checksum = calculateChecksum(line);
    logBuffer += "CHKSUM:" + String(checksum) + "\n";
}
```

### Implementation Priority
Implement verified writes immediately. Checksums can be added later for long-term studies.

---

## 4. Code Organization and Structure 🟡 MEDIUM PRIORITY

### Current Issues

#### Issue 1: Magic Numbers Scattered Throughout Code
Examples:
- `delay(100)` appears 8+ times with unclear purpose
- `delay(200)` in CameraManager.cpp line 128
- `delay(300)` in main.cpp line 127
- Temperature buffer size hardcoded as `#define` in header

#### Issue 2: Configuration Scattered Across Files
- Timing constants in `main.cpp`
- Sensor constants in `TemperatureSensor.h`
- GPIO pins hardcoded in multiple places

### Recommended Solutions

#### 1. Create Configuration Header
```cpp
// config.h
#ifndef CONFIG_H
#define CONFIG_H

// ============================================================================
// HARDWARE CONFIGURATION
// ============================================================================
namespace Hardware {
    constexpr uint8_t GPIO_TEMP_SENSOR = 4;
    constexpr uint8_t GPIO_STATUS_LED = 4;  // Shared with temp sensor
}

// ============================================================================
// TIMING CONFIGURATION
// ============================================================================
namespace Timing {
    constexpr unsigned long TEMP_READ_INTERVAL_MS = 2000;
    constexpr unsigned long CAMERA_STABILIZE_DELAY_MS = 100;
    constexpr unsigned long SD_INIT_DELAY_MS = 100;
    constexpr unsigned long RESOURCE_SWITCH_DELAY_MS = 300;
}

// ============================================================================
// DATA ACQUISITION CONFIGURATION
// ============================================================================
namespace Acquisition {
    constexpr int TEMP_BUFFER_SIZE = 10;
    constexpr int PICTURE_INTERVAL = 4;  // Pictures every N temperature readings
    constexpr float VARIANCE_THRESHOLD = 0.01f;  // Steady-state detection
}

// ============================================================================
// SD CARD CONFIGURATION
// ============================================================================
namespace Storage {
    constexpr const char* LOG_FILE_EXTENSION = ".txt";
    constexpr const char* IMAGE_FILE_EXTENSION = ".jpg";
    constexpr const char* CSV_HEADER = "n, time (ms), temperature (°C)";
}

// ============================================================================
// CAMERA CONFIGURATION
// ============================================================================
namespace Camera {
    constexpr int JPEG_QUALITY_PSRAM = 10;      // With PSRAM (lower = better)
    constexpr int JPEG_QUALITY_NO_PSRAM = 12;   // Without PSRAM
    constexpr int XCLK_FREQ_HZ = 20000000;      // 20 MHz
}

#endif // CONFIG_H
```

#### 2. Extract Constants from Code
Replace:
```cpp
delay(100);  // What does this delay do?
```

With:
```cpp
delay(Timing::CAMERA_STABILIZE_DELAY_MS);  // Clear purpose
```

### Benefits
- Single location for all configuration
- Easy to tune for different experiments
- Self-documenting code
- No need to search through multiple files

---

## 5. Temperature Sensor Enhancements 🟡 MEDIUM PRIORITY

### Current Issues

#### Issue 1: Unused Statistical Methods
The `TemperatureSensor` class has `getSlope()`, `getMinMax()`, and `getMeanAndVariance()` methods that are never used in the main loop.

#### Issue 2: Incomplete Steady-State Detection
The `isSteadyState()` function exists but is commented out in the main loop.

#### Issue 3: Missing getMeanAndVariance() Implementation
The function is declared and used but never implemented, causing compilation warnings.

### Recommended Solutions

#### 1. Complete Statistical Analysis Implementation
```cpp
// In TemperatureSensor.cpp - add the missing function:
std::pair<float, float> TemperatureSensor::getMeanAndVariance() {
    if (!bufferFilled) {
        return {0.0f, -1.0f};  // Indicate insufficient data
    }
    
    float sum = 0.0f;
    float sumSq = 0.0f;
    
    for (int i = 0; i < BUFFER_SIZE; ++i) {
        sum += tempBuffer[i];
        sumSq += tempBuffer[i] * tempBuffer[i];
    }
    
    float mean = sum / BUFFER_SIZE;
    float variance = (sumSq / BUFFER_SIZE) - (mean * mean);
    
    return {mean, variance};
}
```

#### 2. Utilize Steady-State Detection in Main Loop
```cpp
// In main.cpp loop():
if (tempSensor.isSteadyState()) {
    Serial.println("[INFO] System reached thermal steady-state");
    
    // Optional: Mark this event in the log
    // Optional: Trigger special image capture
    // Optional: Notify user via LED pattern
}
```

#### 3. Enhanced Data Logging
```cpp
class EnhancedTemperatureLogger : public TemperatureLogger {
public:
    void addReadingWithStats(float temp, int count, float variance, bool steadyState) {
        String line = String(count) + "," + 
                      String(millis()) + "," + 
                      String(temp, 2) + "," +
                      String(variance, 4) + "," +
                      String(steadyState ? "SS" : "TR") + "\n";  // SS=Steady State, TR=Transient
        logBuffer += line;
    }
};
```

### Benefits
- Richer scientific data
- Automatic phase transition detection
- Better data quality assessment
- Useful for publication-quality results

---

## 6. Camera Configuration Improvements 🟡 MEDIUM PRIORITY

### Current Issues

#### Issue 1: Hardcoded Camera Settings
Camera parameters are hardcoded in `CameraManager::init()` (lines 84-107).

#### Issue 2: Commented-Out Alternative Settings
Lines 76-82 contain alternative camera settings that might be useful but are commented out.

#### Issue 3: Confusing Comment
Line 63: `// SOMEHTING HERE` - unclear purpose

### Recommended Solutions

#### 1. Create Camera Profile System
```cpp
struct CameraProfile {
    const char* name;
    int brightness;
    int contrast;
    int saturation;
    int specialEffect;
    bool whiteBalance;
    bool awbGain;
    bool hmirror;
    bool vflip;
};

// Predefined profiles for different experiments
const CameraProfile PROFILE_GRAYSCALE_HIGH_CONTRAST = {
    .name = "Grayscale High Contrast",
    .brightness = 1,
    .contrast = 2,
    .saturation = -1,
    .specialEffect = 2,  // Grayscale
    .whiteBalance = true,
    .awbGain = true,
    .hmirror = true,
    .vflip = false
};

const CameraProfile PROFILE_COLOR_BALANCED = {
    .name = "Color Balanced",
    .brightness = 0,
    .contrast = 0,
    .saturation = 0,
    .specialEffect = 0,  // No effect
    .whiteBalance = true,
    .awbGain = true,
    .hmirror = true,
    .vflip = false
};

// In CameraManager:
bool CameraManager::applyProfile(const CameraProfile& profile) {
    sensor->set_brightness(sensor, profile.brightness);
    sensor->set_contrast(sensor, profile.contrast);
    // ... apply all settings
    Serial.printf("[CAMERA] Applied profile: %s\n", profile.name);
    return true;
}
```

#### 2. Fix and Document GPIO4 Handling
Replace line 63 comment:
```cpp
// Configure GPIO4 to prevent flash LED interference with DS18B20 temperature sensor
// The flash LED and temperature sensor share GPIO4, so we must explicitly
// disable the flash by setting GPIO4 LOW during camera operation
pinMode(4, OUTPUT);
digitalWrite(4, LOW);
```

### Benefits
- Easy to switch between experiment types
- Clear documentation of camera settings
- Reproducible results
- Better suited for scientific publications

---

## 7. Code Comments and Typos 🟡 MEDIUM PRIORITY

### Issues Found

#### Typos in Comments
1. **CameraManager.cpp line 11**: "Unit camera, alway first" → "Initialize camera, always first"
2. **CameraManager.cpp line 172**: "This fucntion alwys return" → "This function always returns"
3. **main.cpp line 28**: "Temeprature log" → "Temperature log"
4. **TemperatureSensor.cpp line 76**: "This is reapted above" → "This is repeated above"
5. **TemperatureSensor.cpp line 110**: "lienar regression" → "linear regression"

#### Inconsistent Comment Styles
- Some files use `//` comments
- Some use `/* */` multi-line
- Some have no comments at all
- Mix of comment positions (above vs. inline)

### Recommended Solutions

#### 1. Standardize Comment Style
Use Doxygen-style comments consistently:
```cpp
/**
 * @brief Brief one-line description
 * 
 * Detailed multi-line description if needed.
 * Can span multiple lines.
 * 
 * @param paramName Parameter description
 * @return Return value description
 * @note Any special notes
 * @warning Any warnings
 */
```

#### 2. Fix All Typos
Run spell check on all comments and fix identified typos.

#### 3. Add Implementation Comments
```cpp
// Good comment - explains WHY, not WHAT
sensor->set_special_effect(sensor, 2); // Grayscale mode for better contrast in DES experiments

// Bad comment - just repeats code
sensor->set_special_effect(sensor, 2); // Set special effect to 2
```

---

## 8. Memory Management 🟡 MEDIUM PRIORITY

### Current Issues

#### Issue 1: Unbounded String Growth
`TemperatureLogger::logBuffer` is an Arduino String that grows without limits. Could cause memory exhaustion in very long experiments.

#### Issue 2: No Memory Monitoring
No visibility into ESP32 heap usage during runtime.

### Recommended Solutions

#### 1. Add Memory Monitoring
```cpp
void printMemoryStatus() {
    Serial.printf("[MEM] Free heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("[MEM] Largest free block: %d bytes\n", ESP.getMaxAllocHeap());
    if (psramFound()) {
        Serial.printf("[MEM] Free PSRAM: %d bytes\n", ESP.getFreePsram());
    }
}

// Call periodically:
if (readCount % 50 == 0) {  // Every 50 readings
    printMemoryStatus();
}
```

#### 2. Limit Temperature Logger Buffer Size
```cpp
class TemperatureLogger {
private:
    String logBuffer;
    static constexpr size_t MAX_BUFFER_SIZE = 4096;  // 4 KB limit
    
public:
    void addReading(float temperature, int readCount) {
        String entry = String(readCount) + "," + String(millis()) + "," + 
                      String(temperature, 2) + "\n";
        
        if (logBuffer.length() + entry.length() > MAX_BUFFER_SIZE) {
            Serial.println("[WARNING] Temperature log buffer full - forcing SD write");
            // Trigger immediate SD write in main loop
            bufferFullFlag = true;
        }
        
        logBuffer += entry;
    }
    
    bool isBufferFull() const { return bufferFullFlag; }
};
```

### Benefits
- Prevents out-of-memory crashes
- Visibility into resource usage
- Early warning of potential issues

---

## 9. Testing and Validation 🟡 MEDIUM PRIORITY

### Current Issues
- No unit tests
- No integration tests
- Manual testing only
- Difficult to verify correctness

### Recommended Solutions

#### 1. Add Test Mode
```cpp
// config.h
#define TEST_MODE 0  // Set to 1 for testing

#if TEST_MODE
    #define READ_INTERVAL_MS 500      // Faster for testing
    #define PICTURE_INTERVAL 2        // More frequent images
#else
    #define READ_INTERVAL_MS 2000     // Production timing
    #define PICTURE_INTERVAL 4
#endif
```

#### 2. Add Self-Test Function
```cpp
bool runSystemSelfTest() {
    Serial.println("\n========== SYSTEM SELF-TEST ==========");
    
    bool allPassed = true;
    
    // Test 1: Temperature sensor
    Serial.print("[TEST] Temperature sensor... ");
    float testTemp = tempSensor.readTemperature();
    if (testTemp > -50 && testTemp < 100) {
        Serial.println("PASS");
    } else {
        Serial.printf("FAIL (reading: %.2f°C)\n", testTemp);
        allPassed = false;
    }
    
    // Test 2: SD card
    Serial.print("[TEST] SD card... ");
    if (sdManager.init()) {
        Serial.println("PASS");
        sdManager.deinit();
    } else {
        Serial.println("FAIL");
        allPassed = false;
    }
    
    // Test 3: Camera
    Serial.print("[TEST] Camera... ");
    if (camera.init()) {
        Serial.println("PASS");
        camera.deinit();
    } else {
        Serial.println("FAIL");
        allPassed = false;
    }
    
    Serial.println("=====================================\n");
    return allPassed;
}

// Call in setup():
if (!runSystemSelfTest()) {
    Serial.println("[ERROR] Self-test failed - review issues above");
    delay(5000);  // Give user time to read
}
```

#### 3. Add Data Validation
```cpp
bool isValidTemperature(float temp) {
    // DS18B20 returns -127°C on error
    if (temp <= -100) return false;
    
    // Sanity check for DES experiments
    if (temp < -50 || temp > 150) {
        Serial.printf("[WARNING] Temperature out of expected range: %.2f°C\n", temp);
        return false;
    }
    
    return true;
}

// Use in main loop:
float temp = tempSensor.readTemperature();
if (isValidTemperature(temp)) {
    tempLogger.addReading(temp, readCount);
} else {
    Serial.println("[ERROR] Invalid temperature reading - skipped");
}
```

### Benefits
- Catch issues early
- Verify system health
- Improve reliability
- Easier debugging

---

## 10. User Experience Improvements 🟢 LOW PRIORITY

### Current Issues
- No visual feedback (except Serial)
- No experiment status indication
- Difficult to know if system is working without Serial monitor

### Recommended Solutions

#### 1. LED Status Indicators
```cpp
namespace LED {
    enum class Pattern {
        IDLE,           // Slow blink
        READING_TEMP,   // Fast blink
        WRITING_SD,     // Solid on
        CAPTURING_IMG,  // Double blink
        ERROR           // Rapid blink
    };
    
    void show(Pattern pattern) {
        // Implement LED patterns
    }
}

// Use throughout code:
LED::show(LED::Pattern::READING_TEMP);
float temp = tempSensor.readTemperature();
LED::show(LED::Pattern::IDLE);
```

#### 2. Progress Indicators
```cpp
void printExperimentProgress() {
    unsigned long elapsedSeconds = millis() / 1000;
    unsigned long hours = elapsedSeconds / 3600;
    unsigned long minutes = (elapsedSeconds % 3600) / 60;
    unsigned long seconds = elapsedSeconds % 60;
    
    Serial.printf("\n--- Experiment Status ---\n");
    Serial.printf("Elapsed time: %02lu:%02lu:%02lu\n", hours, minutes, seconds);
    Serial.printf("Readings: %d\n", readCount);
    Serial.printf("Images: %d\n", readCount / PICTURE_INTERVAL);
    Serial.printf("Current temp: %.2f°C\n", lastTemperature);
    Serial.printf("-------------------------\n\n");
}

// Call periodically:
if (readCount % 25 == 0) {  // Every 25 readings (~50 seconds)
    printExperimentProgress();
}
```

#### 3. Web Interface (Future Enhancement)
The code has WebServerManager but it's disabled. Consider enabling it for:
- Real-time experiment monitoring
- Remote camera preview
- Live temperature graphs
- Experiment control (pause/resume)

---

## 11. Documentation Improvements 🟢 LOW PRIORITY

### Current Issues
- No `README.md` with setup instructions
- No hardware connection diagram
- No experiment procedure documentation
- Limited comments in code

### Recommended Solutions

#### 1. Create Comprehensive README.md
Should include:
- Hardware requirements and connections
- Software dependencies
- Installation instructions
- Usage guide
- Troubleshooting section
- Example experiments

#### 2. Add Hardware Documentation
Create `HARDWARE.md` with:
- Wiring diagrams
- GPIO pin mappings
- Power requirements
- Recommended components
- Assembly instructions

#### 3. Create Experiment Guide
Create `EXPERIMENT_GUIDE.md` with:
- Preparation checklist
- Step-by-step procedures
- Data analysis workflow
- Common issues and solutions
- Best practices for DES experiments

---

## 12. Future Feature Ideas 🟢 LOW PRIORITY

These are ideas for future enhancement, not critical for current operation:

### 1. Real-Time Data Upload
Upload temperature data to cloud service for:
- Remote monitoring
- Automatic backup
- Collaborative research
- Real-time alerting

### 2. Adaptive Sampling
Adjust sampling rate based on temperature change rate:
```cpp
if (abs(temperatureSlope) > 0.5) {
    // Rapid change detected - increase sampling
    readInterval = 1000;  // 1 second
} else {
    // Stable temperature - reduce sampling
    readInterval = 5000;  // 5 seconds
}
```

### 3. Multi-Sensor Support
Support multiple DS18B20 sensors for:
- Temperature gradients
- Spatial temperature distribution
- Reference temperature tracking

### 4. Time-Lapse Video Generation
Combine captured images into time-lapse videos automatically:
- FFmpeg integration
- Configurable frame rate
- Overlay temperature data on video

### 5. Machine Learning Integration
Use TensorFlow Lite for:
- Automatic phase transition detection
- Anomaly detection
- Predictive modeling

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1)
1. Implement GPIO resource guard
2. Add error handling with retry logic
3. Add SD write verification
4. Fix typos and add missing function implementations

### Phase 2: Code Organization (Week 2)
1. Create `config.h` file
2. Extract all magic numbers
3. Standardize comment style
4. Add memory monitoring

### Phase 3: Enhanced Features (Week 3)
1. Implement steady-state detection
2. Add statistical logging
3. Create camera profiles
4. Add self-test function

### Phase 4: Documentation (Week 4)
1. Write comprehensive README
2. Create hardware documentation
3. Write experiment guide
4. Generate API documentation with Doxygen

---

## Testing Recommendations

### Before Long Experiments
1. Run self-test to verify all hardware
2. Test SD card write/read cycles
3. Verify camera captures successfully
4. Check temperature sensor readings
5. Ensure sufficient SD card space
6. Check battery/power supply

### During Experiments
1. Monitor Serial output periodically
2. Check SD card file sizes
3. Verify temperature readings are reasonable
4. Confirm images are being captured
5. Monitor free memory if possible

### After Experiments
1. Verify data integrity
2. Check for missing data points
3. Validate CSV format
4. Review image timestamps
5. Document any anomalies

---

## Conclusion

This firmware is functional and suitable for scientific experiments. However, implementing these improvements will significantly enhance:

- **Reliability**: Fewer failures, better error recovery
- **Maintainability**: Easier to modify and extend
- **Data Quality**: Better verification, less data loss
- **Usability**: Better feedback, easier troubleshooting
- **Scientific Value**: Richer data, better documentation

Focus on Phase 1 (critical fixes) before running important experiments. Phases 2-4 can be implemented gradually.

---

## Questions for Consideration

1. How long do your typical DES experiments run? (This affects buffer sizing)
2. What temperature range do you typically observe? (For validation limits)
3. Do you need real-time monitoring, or is post-experiment analysis sufficient?
4. What's your SD card size? (Affects how many images you can store)
5. Do you have multiple experiments running simultaneously? (Affects file naming)

---

**Document Version**: 1.0  
**Last Updated**: December 8, 2025  
**Author**: GitHub Copilot  
**Next Review**: After implementing Phase 1 improvements
