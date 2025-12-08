/**
 * @file SDManager.h
 * @brief SD card interface for persistent data storage in DES experiments
 *
 * This module manages all SD card operations including initialization, file creation,
 * and data writing for both temperature logs and camera images. Uses SD_MMC interface
 * in 1-bit mode for compatibility with ESP32-CAM's limited GPIO availability.
 *
 * Hardware Configuration:
 * - Interface: SD_MMC (1-bit mode)
 * - Pins: Default SD_MMC pins on ESP32-CAM
 * - Card Type: SD/SDHC cards (FAT32 recommended)
 * - LED Indicator: GPIO pin for visual feedback during operations
 *
 * Design Philosophy:
 * - Initialize-use-deinitialize pattern to conserve power
 * - Short SD access windows to minimize conflicts
 * - Automatic directory listing for verification
 * - Error handling with boolean return values
 *
 * Scientific Application:
 * - Persistent storage of temperature time-series data
 * - Image archival for visual documentation
 * - Long-term experiment data retention
 * - Offline data analysis and publication preparation
 *
 * File Organization:
 * - Temperature logs: "/experiment_name.txt" (CSV format)
 * - Images: "/readCount_experiment_name.jpg" (JPEG format)
 * - Configuration: Stored in LittleFS (not SD card)
 */

#pragma once

#include <Arduino.h>
#include "SD_MMC.h"

/**
 * @class SDManager
 * @brief Manages SD card operations for experimental data persistence
 *
 * This class provides a high-level interface for SD card operations with automatic
 * initialization and deinitialization to optimize power consumption and minimize
 * resource conflicts with other peripherals.
 *
 * Key Features:
 * - Automatic init/deinit for each operation
 * - Support for text log files and binary image data
 * - File append mode for continuous logging
 * - Directory listing for debugging
 * - LED feedback for SD activity
 *
 * Reliability Features:
 * - Immediate file closing after writes
 * - Return value checking for all operations
 * - Explicit error handling
 * - Minimized SD card access time
 *
 * Usage Pattern:
 * 1. Construct SDManager with LED pin
 * 2. Call createLogFile() once during setup
 * 3. Periodically call saveLog() with accumulated data
 * 4. Call saveImage() after each camera capture
 * 5. Optional: listFiles() for debugging
 *
 * @note Each method handles init/deinit internally - no manual SD management needed
 */
class SDManager
{
public:
    /**
     * @brief Constructor - initialize SD manager with status LED
     *
     * Sets up SDManager with specified GPIO pin for LED indicator.
     * LED provides visual feedback during SD card operations.
     *
     * @param LED_PIN GPIO pin number for status LED
     * @note LED pin is configured as OUTPUT in constructor
     * @note LED control is managed internally during SD operations
     */
    SDManager(uint8_t LED_PIN);

    /**
     * @brief Initialize SD card hardware
     *
     * Configures SD_MMC interface in 1-bit mode and prepares card for operations.
     * Called automatically by other methods - rarely needs manual invocation.
     *
     * Hardware Configuration:
     * - Uses default ESP32-CAM SD_MMC pins
     * - 1-bit mode for GPIO conservation
     * - Releases GPIO4 before initialization to avoid conflicts
     * - 100ms stabilization delay
     *
     * @return true if SD card initialized successfully, false if card not present or init failed
     * @note Includes GPIO4 release sequence to prevent DS18B20 interference
     */
    bool init();

    /**
     * @brief Deinitialize SD card and release resources
     *
     * Closes SD card interface and releases GPIO pins for use by other peripherals.
     * Called automatically by all SD operation methods after completing their task.
     *
     * @note Essential for preventing resource conflicts in this multi-peripheral system
     */
    void deinit();

    /**
     * @brief List all files and directories on SD card
     *
     * Debugging utility that prints directory contents to Serial monitor.
     * Useful for verifying file creation and monitoring storage usage.
     *
     * Output Format (via Serial):
     * - Directories: "\tDIR : directory_name"
     * - Files: "\tFILE: filename  SIZE: bytes"
     *
     * @note Automatically handles init/deinit
     * @note Output sent to Serial at configured baud rate
     */
    void listFiles();

    /**
     * @brief Create new temperature log file with CSV header
     *
     * Creates (or overwrites) a log file and writes the CSV header row.
     * Called once during experiment setup to initialize the data file.
     *
     * File Content:
     * - Header: "n, time (ms), temperature (°C)\n"
     * - Subsequent data appended via saveLog()
     *
     * Scientific Application:
     * - Initializes experiment data file
     * - Establishes CSV structure for analysis software
     * - Named after experiment for organization
     *
     * @param filename Path to log file (e.g., "/experiment_001.txt")
     * @return true if file created and header written successfully, false if SD init or write failed
     * @note Overwrites existing files with same name
     * @note Automatically handles SD init/deinit
     */
    bool createLogFile(const String &filename);

    /**
     * @brief Append temperature log data to existing file
     *
     * Writes accumulated temperature readings to SD card in append mode.
     * Used periodically to persist in-memory log buffer to permanent storage.
     *
     * Operation:
     * 1. Initialize SD card
     * 2. Open file in append mode (preserves existing data)
     * 3. Write log text (typically multiple CSV rows)
     * 4. Close file immediately
     * 5. Deinitialize SD card
     *
     * Scientific Application:
     * - Periodic persistence of temperature time-series
     * - Batch writing reduces SD wear
     * - Maintains chronological data order
     * - Enables long-duration experiments without memory overflow
     *
     * @param logText CSV-formatted temperature data from TemperatureLogger
     * @param filename Path to log file (default: "/temps.txt")
     * @return true if data written successfully, false if SD init or write failed
     * @note File must already exist (create with createLogFile() first)
     * @note Automatically handles SD init/deinit
     */
    bool saveLog(const String &logText, const String &filename = "/temps.txt");

    /**
     * @brief Save JPEG image to SD card
     *
     * Writes camera frame buffer to SD card as JPEG file.
     * Used to store periodic images for visual documentation of experiments.
     *
     * Operation:
     * 1. Initialize SD card
     * 2. Create/overwrite file
     * 3. Write binary JPEG data
     * 4. Close file
     * 5. Deinitialize SD card
     *
     * Scientific Application:
     * - Visual documentation of phase transitions
     * - Correlation with temperature data via filename timestamps
     * - Evidence for publications and presentations
     * - Post-experiment image analysis
     *
     * File Naming Convention:
     * Typically: "/readCount_experimentName.jpg"
     * Example: "/42_DES_ChCl_Urea.jpg" (42nd reading of ChCl-Urea experiment)
     *
     * @param data Pointer to JPEG image buffer (from camera_fb_t->buf)
     * @param length Size of image data in bytes (from camera_fb_t->len)
     * @param filename Path for image file including .jpg extension
     * @return true if image saved successfully, false if SD init or write failed
     * @note Images typically 10-100 KB depending on resolution and quality settings
     * @note Automatically handles SD init/deinit
     */
    bool saveImage(const uint8_t *data, size_t length, const String &filename);

private:
    /**
     * @brief GPIO pin number for status LED
     *
     * Used to provide visual feedback during SD card operations.
     * Configured as OUTPUT in constructor.
     */
    uint8_t LED_PIN;
};
