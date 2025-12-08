/**
 * @file WebServerManager.h
 * @brief HTTP web server for remote camera control and configuration
 *
 * This module provides a web-based interface for controlling the ESP32-CAM and adjusting
 * camera settings during experiments. Allows remote monitoring and configuration without
 * requiring physical access to the device.
 *
 * Features:
 * - Live camera preview via JPEG streaming
 * - Real-time camera settings adjustment
 * - Web-based configuration interface
 * - JSON-based settings persistence
 *
 * Network Configuration:
 * - Protocol: HTTP (port 80)
 * - Connection: WiFi (configured via wifi_setup.h)
 * - MIME Types: HTML, JPEG, JSON
 * - CORS: No cross-origin restrictions
 *
 * Scientific Application:
 * - Remote experiment monitoring
 * - Camera orientation adjustment without disturbing setup
 * - Image quality optimization for documentation
 * - Network-accessible live feed for supervision
 *
 * @note Web server functionality is currently disabled in main.cpp
 * @note Can be enabled for setup and testing phases of experiments
 */

#pragma once

#include <WebServer.h>
#include <WiFi.h>
#include <LittleFS.h>
#include <ArduinoJson.h>

#include "CameraManager.h"
#include "TemperatureSensor.h"

#include "html_pages.h"

/**
 * @class WebServerManager
 * @brief Manages HTTP web server for camera control and configuration
 *
 * This class encapsulates a web server that provides browser-based access to the
 * ESP32-CAM. Serves HTML pages, handles camera control requests, and manages
 * configuration persistence.
 *
 * Key Features:
 * - RESTful API endpoints for camera control
 * - HTML page serving from LittleFS
 * - JSON configuration management
 * - Live JPEG image streaming
 * - Dynamic settings updates without restart
 *
 * Endpoint Structure:
 * - GET /          : Main control page (HTML)
 * - GET /cam.jpg   : Current camera image (JPEG)
 * - GET /settings  : Camera settings page (HTML)
 * - POST /set-config : Update camera configuration (JSON)
 *
 * Usage Pattern:
 * 1. Construct WebServerManager with port number
 * 2. Call init() with CameraManager pointer
 * 3. In main loop, call handleRequests() repeatedly
 * 4. Access via browser at http://[ESP32_IP]/
 *
 * @note Currently disabled in production firmware
 * @note Useful for initial setup and testing
 */
class WebServerManager
{
public:
    /**
     * @brief Constructor - create web server on specified port
     *
     * Initializes web server instance without starting it.
     * Default port 80 provides standard HTTP access.
     *
     * @param port TCP port for HTTP server (default: 80)
     * @note Server is not started until init() is called
     */
    WebServerManager(uint16_t port = 80);

    /**
     * @brief Initialize web server and register route handlers
     *
     * Mounts LittleFS for HTML page access, registers all HTTP endpoints,
     * and starts the web server listening on configured port.
     *
     * Registered Routes:
     * - /          : Serves main.html from LittleFS
     * - /cam.jpg   : Returns current camera frame as JPEG
     * - /settings  : Serves camera settings HTML page
     * - /set-config: Accepts JSON POST to update camera parameters
     * - 404 handler: Custom not-found response
     *
     * LittleFS Structure:
     * - /main.html      : Main control interface
     * - /cam_config.json: Persistent camera settings
     *
     * @param myCam Pointer to CameraManager instance for image capture
     * @note Requires WiFi connection to be established first
     * @note LittleFS must contain required HTML files
     */
    void init(CameraManager *myCam);

    /**
     * @brief Process incoming HTTP requests
     *
     * Must be called repeatedly in main loop to handle web client requests.
     * Non-blocking - returns quickly if no requests pending.
     *
     * @note Call frequency affects web interface responsiveness
     * @note Should be called at least every 100ms for good user experience
     */
    void handleRequests();

private:
    /**
     * @brief ESP8266WebServer instance handling HTTP protocol
     */
    WebServer server;

    /**
     * @brief Pointer to camera manager for image capture operations
     */
    CameraManager *myCam;

    /**
     * @brief Handler for root endpoint - serves main HTML page
     *
     * Loads and streams main.html from LittleFS to the client.
     * Provides primary user interface for camera control.
     *
     * Route: GET /
     * Content-Type: text/html
     *
     * @note Returns 500 error if LittleFS not mounted or file missing
     */
    void handleMainPage();

    /**
     * @brief Handler for image capture endpoint
     *
     * Captures current camera frame and returns as JPEG image.
     * Used for live preview and image capture from web interface.
     *
     * Route: GET /cam.jpg
     * Content-Type: image/jpeg
     *
     * Headers:
     * - Cache-Control: Prevents browser caching for live updates
     * - Pragma: no-cache
     * - Expires: -1
     *
     * @note Frame buffer automatically returned after transmission
     * @note Returns 500 error if camera capture fails
     */
    void handleImageCapture();

    /**
     * @brief Save current camera settings to persistent storage
     *
     * Writes camera sensor configuration to JSON file in LittleFS.
     * Preserves settings across power cycles.
     *
     * Saved Parameters:
     * - vflip: Vertical flip setting
     * - hmirror: Horizontal mirror setting
     * - brightness: Image brightness value
     * - contrast: Image contrast value
     * - saturation: Color saturation value
     * - framesize: Resolution setting
     * - quality: JPEG quality value
     *
     * @param path Path to JSON config file (default: "/cam_settings.json")
     * @return true if settings saved successfully, false if write failed
     * @note Called internally when settings are modified
     */
    bool saveCameraSettings(const char *path = "/cam_settings.json");

    /**
     * @brief Handler for camera settings page
     *
     * Serves HTML page with camera configuration controls.
     * Allows adjustment of image parameters via web interface.
     *
     * Route: GET /settings
     * Content-Type: text/html
     *
     * @note HTML content defined in html_pages.h
     */
    void handleSettingsPage();

    /**
     * @brief Handler for camera configuration update requests
     *
     * Receives JSON-formatted camera settings via POST, validates,
     * saves to LittleFS, and applies to camera sensor.
     *
     * Route: POST /set-config
     * Content-Type: application/json
     *
     * Expected JSON Format:
     * {
     *   "vflip": 0,
     *   "hmirror": 1,
     *   "brightness": 1,
     *   "contrast": 2,
     *   "saturation": -1,
     *   "framesize": 6,
     *   "quality": 10
     * }
     *
     * Response:
     * - 200 OK: Settings updated successfully
     * - 400 Bad Request: JSON parse error or missing body
     * - 500 Internal Server Error: Failed to save or apply settings
     *
     * @note Changes take effect immediately
     * @note Settings persisted to /cam_config.json
     */
    void handleCameraSettingUpdate();

    /**
     * @brief Handler for undefined routes
     *
     * Provides detailed error message for debugging.
     * Includes requested URI, method, and arguments.
     *
     * Route: * (catch-all)
     * Status: 404 Not Found
     * Content-Type: text/plain
     *
     * @note Useful for debugging client requests
     */
    void handleNotFound();
};
