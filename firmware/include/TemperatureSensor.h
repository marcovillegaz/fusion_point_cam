/**
 * @file TemperatureSensor.h
 * @brief DS18B20 temperature sensor interface for deep eutectic solvent thermal monitoring
 *
 * This module provides high-precision temperature measurement using the DS18B20 digital sensor.
 * It implements statistical analysis for steady-state detection, critical for determining
 * thermal equilibrium in deep eutectic solvent experiments.
 *
 * Hardware Configuration:
 * - Sensor: DS18B20 digital temperature sensor
 * - Interface: 1-Wire protocol on GPIO4
 * - Resolution: 12-bit (0.0625°C precision)
 * - Range: -55°C to +125°C
 * - GPIO Conflict: Shares GPIO4 with ESP32-CAM, requiring careful resource management
 *
 * Scientific Application:
 * - Monitors temperature during DES phase transitions
 * - Detects thermal equilibrium for steady-state measurements
 * - Provides high-frequency temperature sampling (configurable intervals)
 * - Statistical analysis for data quality assessment
 *
 * Steady-State Detection:
 * The system uses a rolling buffer to calculate variance and determine when the system
 * has reached thermal equilibrium. This is essential for:
 * - Identifying when measurements are stable
 * - Reducing noise in phase transition detection
 * - Ensuring data quality in scientific publications
 */

#pragma once
#include <OneWire.h>
#include <DallasTemperature.h>

/**
 * @def BUFFER_SIZE
 * @brief Number of temperature samples stored for statistical analysis
 *
 * The rolling buffer stores the most recent 10 temperature readings.
 * This size provides:
 * - Sufficient data for meaningful variance calculation
 * - Balance between responsiveness and noise filtering
 * - ~20 seconds of data at 2-second sampling intervals
 */
#define BUFFER_SIZE 10

/**
 * @def VARIANCE_THRESHOLD
 * @brief Threshold for steady-state detection (°C²)
 *
 * Temperature variance below this threshold indicates thermal equilibrium.
 * Value of 0.01°C² corresponds to ~0.1°C standard deviation.
 *
 * Scientific Rationale:
 * - Suitable for detecting phase transitions in DES
 * - Accounts for DS18B20 sensor noise (~±0.5°C)
 * - Can be adjusted based on experimental requirements
 */
#define VARIANCE_THRESHOLD 0.01

/**
 * @class TemperatureSensor
 * @brief Manages DS18B20 temperature sensor with statistical analysis capabilities
 *
 * This class encapsulates all temperature sensing operations including hardware initialization,
 * data acquisition, buffering, and statistical analysis for steady-state detection.
 *
 * Key Features:
 * - High-resolution 12-bit temperature readings
 * - Rolling buffer for temporal analysis
 * - Variance-based steady-state detection
 * - Linear regression for trend analysis
 * - Min/max tracking for quality control
 *
 * Statistical Methods:
 * The class maintains a circular buffer of recent temperature readings and provides:
 * - Mean and variance calculation
 * - Linear regression slope (temperature change rate)
 * - Min/max values for range assessment
 * - Automatic steady-state detection
 *
 * Usage Pattern:
 * 1. Construct with GPIO pin number
 * 2. Call init() to configure sensor
 * 3. Periodically call readTemperature() for measurements
 * 4. Check isSteadyState() to detect thermal equilibrium
 * 5. Call deinit() before using camera to release GPIO4
 */
class TemperatureSensor
{
public:
    /**
     * @brief Constructor - initialize temperature sensor on specified pin
     *
     * Sets up the OneWire communication interface and initializes the internal
     * circular buffer for statistical analysis.
     *
     * @param pin GPIO pin number for DS18B20 data line (typically GPIO4 on ESP32-CAM)
     * @note Constructor does not configure hardware - call init() after construction
     */
    TemperatureSensor(uint8_t pin);

    /**
     * @brief Initialize DS18B20 sensor hardware
     *
     * Configures the GPIO pin, starts the OneWire interface, and sets sensor parameters.
     * Verifies sensor presence on the bus.
     *
     * Configuration:
     * - Pin mode: INPUT (OneWire requires pull-up resistor)
     * - Resolution: 12-bit (0.0625°C precision, ~750ms conversion time)
     * - Mode: Non-blocking reads for better system responsiveness
     *
     * @return true if initialization successful and sensor detected, false if no sensor found
     * @note Includes 100ms stabilization delay after pin configuration
     * @warning Will fail if GPIO4 is in use by camera - ensure camera.deinit() called first
     */
    bool init();

    /**
     * @brief Deinitialize sensor and release GPIO pin
     *
     * Releases control of GPIO4 to allow camera usage. Sets pin as INPUT
     * to minimize interference with other peripherals.
     *
     * @note Buffer state is preserved - only hardware resources are released
     * @note Must be called before camera initialization to avoid GPIO conflicts
     */
    void deinit();

    /**
     * @brief Read current temperature and update statistical buffer
     *
     * Requests a temperature conversion from DS18B20, waits for completion,
     * reads the result, and stores it in the circular buffer for analysis.
     *
     * Measurement Process:
     * 1. Request temperature conversion from sensor
     * 2. Wait 100ms for 12-bit conversion to complete
     * 3. Read temperature value via OneWire protocol
     * 4. Store in circular buffer (overwrites oldest value when full)
     * 5. Update buffer fill status
     *
     * @return Temperature in degrees Celsius (float)
     * @note Each call advances the buffer index, maintaining most recent 10 readings
     * @note Returns sensor value directly; check for -127°C which indicates sensor error
     */
    float readTemperature();

    /**
     * @brief Check if system has reached thermal steady-state
     *
     * Determines if temperature variance is below threshold, indicating thermal equilibrium.
     * Used to identify when the deep eutectic solvent system is stable for measurements.
     *
     * Scientific Significance:
     * - Ensures measurements are taken at equilibrium
     * - Helps identify completion of phase transitions
     * - Improves reproducibility of experimental data
     * - Critical for accurate thermodynamic property determination
     *
     * Algorithm:
     * 1. Requires full buffer (10 samples minimum)
     * 2. Calculates temperature variance across buffer
     * 3. Compares variance to VARIANCE_THRESHOLD
     * 4. Returns true if variance < threshold
     *
     * @return true if steady-state detected (variance < VARIANCE_THRESHOLD), false otherwise
     * @note Returns false if buffer not yet filled (< 10 samples)
     */
    bool isSteadyState();

    /**
     * @brief Calculate temperature variance for quality assessment
     *
     * Computes statistical variance of buffered temperature readings.
     * Provides quantitative measure of temperature stability.
     *
     * Calculation: variance = E[T²] - (E[T])²
     * Where E represents mean of buffered values
     *
     * Applications:
     * - Assess data quality for scientific reporting
     * - Tune VARIANCE_THRESHOLD for specific experiments
     * - Identify periods of instability or disturbances
     * - Generate uncertainty estimates for publications
     *
     * @return Temperature variance in °C², or -1.0 if buffer not filled
     * @note Requires at least BUFFER_SIZE samples for valid calculation
     */
    float getVariance();

private:
    uint8_t sensorPin;         ///< GPIO pin number for DS18B20 data line
    OneWire oneWire;           ///< OneWire protocol handler
    DallasTemperature sensors; ///< Dallas Temperature library interface

    float tempBuffer[BUFFER_SIZE]; ///< Circular buffer storing recent temperature readings
    int bufferIndex;               ///< Current write position in circular buffer
    bool bufferFilled;             ///< Flag indicating buffer has been filled at least once

    /**
     * @brief Calculate mean and variance of buffered temperatures
     *
     * Internal statistical analysis function used by steady-state detection.
     *
     * @return std::pair<float, float> containing (mean, variance)
     * @note Private helper function for isSteadyState()
     */
    std::pair<float, float> getMeanAndVariance();

    /**
     * @brief Calculate temperature change rate via linear regression
     *
     * Performs least-squares linear regression on buffered data to determine
     * the slope (temperature change rate).
     *
     * Scientific Application:
     * - Detect heating/cooling trends
     * - Identify approaching phase transitions
     * - Assess system response characteristics
     *
     * @return Slope in °C per sample interval, or 0.0 if insufficient data
     * @note Not currently used in steady-state detection but available for future analysis
     */
    float getSlope();

    /**
     * @brief Find minimum and maximum temperatures in buffer
     *
     * Identifies temperature range over the buffered period.
     * Useful for quality control and outlier detection.
     *
     * @return std::pair<float, float> containing (min, max) temperatures in °C
     * @return Returns (999.0, -999.0) if buffer not filled (error indicator)
     * @note Used for data validation and range checking
     */
    std::pair<float, float> getMinMax();
};