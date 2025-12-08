/**
 * @file main.cpp
 * @brief Main firmware for deep eutectic solvent temperature monitoring and imaging system
 *
 * This firmware coordinates multiple subsystems to perform synchronized temperature logging
 * and image capture of deep eutectic solvent (DES) experiments. The system manages GPIO
 * resource conflicts between the DS18B20 temperature sensor and ESP32-CAM camera module,
 * both sharing GPIO4.
 *
 * System Architecture:
 * - Temperature monitoring: DS18B20 sensor via 1-Wire protocol
 * - Visual documentation: ESP32-CAM with OV2640 sensor
 * - Data persistence: SD card via SD_MMC interface
 * - User interface: Serial communication for experiment naming
 *
 * Experimental Workflow:
 * 1. User provides experiment name via Serial
 * 2. System creates log file with CSV header
 * 3. Temperature readings taken at regular intervals
 * 4. Readings buffered in RAM for batch writing
 * 5. Periodic image capture synchronized with temperature logging
 * 6. Data and images saved to SD card with consistent naming
 *
 * Scientific Application:
 * This system is designed for studying thermal properties of deep eutectic solvents,
 * including phase transitions, melting points, and thermal stability. The synchronized
 * temperature and image data enables correlation between thermal and visual observations.
 *
 * Hardware Requirements:
 * - ESP32-CAM board with OV2640 camera
 * - DS18B20 temperature sensor on GPIO4
 * - SD card (FAT32 recommended)
 * - 4.7kΩ pull-up resistor on DS18B20 data line
 *
 * Author: [Research Team]
 * Date: December 2025
 * Purpose: Deep Eutectic Solvent Research
 */

#include <Arduino.h>

#include "wifi_setup.h"
#include "CameraManager.h"
#include "TemperatureSensor.h"
#include "TemperatureLogger.h"
#include "SDManager.h"
#include "WebServerManager.h"

#include "secrets.h" // WiFi credentials (not version controlled)

// ============================================================================
// CONFIGURATION CONSTANTS
// ============================================================================

/**
 * @brief GPIO pin for DS18B20 temperature sensor
 *
 * WARNING: GPIO4 is shared between the DS18B20 sensor and the camera's flash LED.
 * Careful initialization and deinitialization sequences are required to prevent conflicts.
 *
 * Resource Management:
 * - Temperature reading: DS18B20 uses GPIO4 as 1-Wire data line
 * - Camera operation: GPIO4 configured LOW to disable flash LED
 * - Conflict resolution: Explicit init/deinit cycles in main loop
 */
#define TEMP_SENSOR_PIN 4

// IPAddress staticIP(192, 168, 1, 184); // Optional static IP
// IPAddress local_IP(0, 0, 0, 0); // forces DHCP instead of static

// --- Instances ---
TemperatureSensor tempSensor(TEMP_SENSOR_PIN);
SDManager sdManager(TEMP_SENSOR_PIN);
TemperatureLogger tempLogger;
CameraManager camera;
// WebServerManager webServer; // WebServerManager instance

// --- Constants ---
const unsigned long READ_INTERVAL_MS = 2000; // 2 seconds between readings
unsigned long lastReadTime = 0;

const int PICTURE_INTERVAL = 4; // Take picture every 10 readings

int readCount = 0;
String experimentName = ""; // This can be set by the user in the future

void setup()
{
    // Initialize serial communication
    Serial.begin(115200);

    // Temeprature log and camera initialization
    Serial.println("========== SYSTEM LOG START ==========\n");

    // --- Set Experiment name ---
    // Enter experiment name by user in serial monitor
    Serial.println(">>> Enter the experiment name:");

    // Wait until the user inputs something
    while (experimentName.length() == 0)
    {
        if (Serial.available() > 0)
        {
            experimentName = Serial.readStringUntil('\n'); // Read until newline
            experimentName.trim();                         // Remove any trailing newline or spaces
        }
    }
    Serial.printf("[SETUP] Experiment name set to: %s\n", experimentName.c_str());

    delay(1000);

    // Create log file on SD card
    Serial.print("[SETUP] ");
    sdManager.createLogFile("/" + experimentName + ".txt");
    // List files on SD card
    Serial.println(">>> Listing directory contents:");
    sdManager.listFiles();

    // Test camera initialization
    if (!camera.init())
    {
        Serial.println("Camera initialization failed!");
        while (1)
            delay(100);
    }
    camera.deinit();

    // Temperature sensor initialization
    if (!tempSensor.init())
    {
        Serial.println("Temperature sensor initialization failed!");
        while (1)
            delay(100);
    }

    /*// Load setting from json to camera
    // Initializing camera
    if (!camera.init())
    {
        Serial.println("Camera failed to initialize");
        return;
    }
    camera.loadSettings("/cam_config.json"); // Optional: load last settings

    /* // --- Camera Test in webserver ---
    // Connect to WiFi
    connectToWiFi(ssid, password); // Connect to WiFi
    // Initialize web server and pass reference to camera and tempSensor
    webServer.init(&camera); */
}

void loop()
{
    // --- Logic handling GPIO4 for multiples sensors ---
    unsigned long currentTime = millis();

    if (currentTime - lastReadTime >= READ_INTERVAL_MS)
    {
        lastReadTime = currentTime;

        // --- Temperature Reading Phase ---
        readCount++;                               // Increment read count
        float temp = tempSensor.readTemperature(); // Read temperature
        tempLogger.addReading(temp, readCount);    // Add reading to logger
        tempSensor.deinit();                       // Release GPIO4

        Serial.printf("#%d, %.2f s, %.2f°C\n",
                      readCount,
                      lastReadTime / 1000.0f, // Convert ms to seconds as float
                      temp);

        // --- Periodic SD Card and Camera Operations ---
        if (readCount % PICTURE_INTERVAL == 0)
        {
            // 1. Save temperature log
            String buffer = tempLogger.getLog();                      // Get log buffer
            sdManager.saveLog(buffer, "/" + experimentName + ".txt"); // Append to SD file
            tempLogger.clear();                                       // Clear log buffer

            // 2. Take and save photo
            // camera.init();                           // Initialize camera (may use other pins)
            camera_fb_t *fb = camera.capturePhoto(); // Capture photo
            if (fb)
            {
                // Filename of the capture
                String filename = "/" + String(readCount) + "_" + experimentName + ".jpg";
                // Save image to SD
                sdManager.saveImage(fb->buf, fb->len, filename);
                // Deinit camera and return frame buffer
            }
            camera.deinit(); //

            delay(300); // Small delay to ensure clean transition
        }
    }
    delay(READ_INTERVAL_MS);

    /* // Web server handling
    // Handle incoming web requests
    webServer.handleRequests(); */
}

// --- Old code ---
// Temperature readings
/* float temperature = tempSensor.readTemperature();
float variance = tempSensor.getVariance();

Serial.print("\nTemperature: ");
Serial.print(temperature, 4);
Serial.print(" °C | Variance: ");
Serial.print(variance, 5);

if (tempSensor.isSteadyState())
{
    Serial.print(" | System has reached steady state.\n");
}
else
{
    Serial.print(" | System is still stabilizing.\n");
} */
