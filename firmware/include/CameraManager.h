/**
 * @file CameraManager.h
 * @brief Camera management system for ESP32-CAM module in deep eutectic solvent experiments
 *
 * This module provides a comprehensive interface for controlling the ESP32-CAM OV2640 camera sensor.
 * It handles camera initialization, configuration persistence, image capture, and resource management.
 * The camera is used to document visual changes in deep eutectic solvents during thermal experiments.
 *
 * Hardware Configuration:
 * - Camera Module: ESP32-CAM with OV2640 sensor
 * - Resolution: Configurable (QVGA to SVGA depending on PSRAM availability)
 * - GPIO Conflict: Shares GPIO4 with DS18B20 temperature sensor, requiring careful init/deinit cycles
 *
 * Scientific Application:
 * - Captures periodic images of the experimental setup
 * - Documents phase transitions and visual changes in the solvent
 * - Provides visual correlation with temperature data
 * - Images saved with timestamp correlation to temperature logs
 */

#pragma once

#include <esp_camera.h>
#include <WebServer.h>

/**
 * @class CameraManager
 * @brief Manages ESP32-CAM operations for scientific imaging in DES experiments
 *
 * This class encapsulates all camera operations including hardware initialization,
 * sensor configuration, image capture, and settings persistence. It manages the
 * OV2640 camera sensor through the ESP32 camera driver API.
 *
 * Key Features:
 * - Dynamic resolution selection based on PSRAM availability
 * - Persistent settings storage using JSON configuration files
 * - Grayscale imaging optimized for thermal experiments
 * - Resource management to prevent GPIO conflicts
 *
 * Usage Pattern:
 * 1. Instantiate CameraManager
 * 2. Call init() to configure hardware
 * 3. Optionally loadSettings() for custom configuration
 * 4. Use capturePhoto() to acquire images
 * 5. Call deinit() to release GPIO resources before temperature readings
 */
class CameraManager
{
public:
    /**
     * @brief Default constructor
     * Initializes internal pointers to nullptr
     */
    CameraManager();

    /**
     * @brief Initialize camera hardware and sensor
     *
     * Configures the ESP32-CAM hardware pins, initializes the OV2640 sensor,
     * and sets up image capture parameters. Resolution and quality are automatically
     * adjusted based on PSRAM availability.
     *
     * Configuration:
     * - With PSRAM: SVGA (800x600), JPEG quality 10, suitable for detailed documentation
     * - Without PSRAM: QVGA (320x240), JPEG quality 12, reduced memory footprint
     * - Grayscale mode: Optimized for thermal and phase transition observation
     * - GPIO4 handling: Configured LOW to prevent interference with DS18B20
     *
     * @return true if initialization successful, false if camera init failed or sensor unavailable
     * @note Must be called before any image capture operations
     * @note Will conflict with DS18B20 on GPIO4 if not properly deinitialized between uses
     */
    bool init();

    /**
     * @brief Load camera settings from JSON configuration file
     *
     * Reads and applies camera parameters from a LittleFS-stored JSON file.
     * Allows for persistent configuration across power cycles and experiment-specific settings.
     *
     * Configurable Parameters:
     * - vflip: Vertical flip (0 or 1)
     * - hmirror: Horizontal mirror (0 or 1)
     * - brightness: Image brightness (-2 to +2)
     * - contrast: Image contrast (-2 to +2)
     * - saturation: Color saturation (-2 to +2)
     * - framesize: Resolution setting (FRAMESIZE_* enum)
     * - quality: JPEG compression quality (0-63, lower = higher quality)
     *
     * @param path Path to JSON configuration file in LittleFS (default: "/cam_config.json")
     * @return true if settings loaded and applied successfully, false if file not found or JSON parse error
     * @note File must be present in LittleFS before calling this function
     */
    bool loadSettings(const char *path = "/cam_config.json");

    /**
     * @brief Capture a single image frame
     *
     * Acquires one frame from the camera sensor and returns the frame buffer.
     * The captured image is stored in JPEG format in PSRAM or regular RAM.
     *
     * Scientific Use:
     * - Called periodically during experiments to document visual changes
     * - Images timestamped and correlated with temperature readings
     * - Captures phase transitions, color changes, or crystal formation
     *
     * @return Pointer to camera_fb_t structure containing image data and metadata,
     *         nullptr if capture failed or camera not initialized
     * @note Caller is responsible for returning frame buffer using esp_camera_fb_return()
     *       or calling deinit() which handles cleanup automatically
     * @note Automatically initializes camera if not already done
     */
    camera_fb_t *capturePhoto();

    /**
     * @brief Deinitialize camera and release resources
     *
     * Shuts down the camera driver, releases GPIO pins, and frees frame buffers.
     * Critical for allowing GPIO4 to be used by the DS18B20 temperature sensor.
     *
     * Resource Cleanup:
     * - Returns any held frame buffers to the system
     * - Calls esp_camera_deinit() to release driver resources
     * - Resets sensor pointer
     * - Includes 200ms delay for stable GPIO state transition
     *
     * @note Must be called before initializing temperature sensor to avoid GPIO conflicts
     * @note After calling deinit(), init() must be called again before capturing new images
     */
    void deinit();

    /**
     * @brief Pointer to camera sensor structure for direct parameter access
     *
     * Provides access to the OV2640 sensor_t structure for advanced configuration.
     * Allows direct manipulation of sensor registers and settings not exposed through
     * standard API.
     */
    sensor_t *sensor;

    /**
     * @brief Pointer to the most recently captured frame buffer
     *
     * Stores reference to the last acquired image frame. Used internally for
     * resource management and cleanup operations.
     */
    camera_fb_t *lastFrameBuffer;
};
