#include <Arduino.h>

#include "wifi_setup.h"
#include "CameraManager.h"
#include "TemperatureSensor.h"
#include "TemperatureLogger.h"
#include "SDManager.h"
#include "WebServerManager.h"

#include "secrets.h" // Include your WiFi credentials here

// --- Constants ---
#define TEMP_SENSOR_PIN 4
#define TEMP_READ_INTERVAL 2000 // in milliseconds

// IPAddress staticIP(192, 168, 1, 184); // Optional static IP
// IPAddress local_IP(0, 0, 0, 0); // forces DHCP instead of static

// --- Instances ---
TemperatureSensor tempSensor(TEMP_SENSOR_PIN);
SDManager sdManager(TEMP_SENSOR_PIN);
TemperatureLogger tempLogger;
CameraManager camera;
// WebServerManager webServer;                    // WebServerManager instance

// --- Constants ---
const unsigned long READ_INTERVAL_MS = 2000; // 2 seconds between readings
unsigned long lastReadTime = 0;

const int PICTURE_INTERVAL = 20; // Take picture every 10 readings

int readCount = 0;
String experimentName = ""; // This can be set by the user in the future

void setup()
{
    // Initialize serial communication
    Serial.begin(115200);
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
    Serial.print("[SETUP] ");
    if (!camera.init())
    {
        Serial.println("Camera initialization failed!");
        while (1)
            delay(100);
    }
    camera.deinit();

    // Temperature sensor initialization
    Serial.print("[SETUP] ");
    if (!tempSensor.init())
    {
        Serial.println("Temperature sensor initialization failed!");
        while (1)
            delay(100);
    }

    // --- THIS IS OLD CODE ---
    /* // Prevent GPIO4 (flash LED) from interfering
    pinMode(4, INPUT);

    // Load setting from json to camera
    if (!camera.loadSettings())
    {
        Serial.println("camera_settting.json couldnt load");
    } */

    // --- web testing ---
    /* // Connect to WiFi
    connectToWiFi(ssid, password); // Connect to WiFi

    // Initialize web server and pass reference to camera and tempSensor
    webServer.init(&camera, &tempSensor); */
}

void loop()
{
    // --- Logic handling GPIO4 for multiples sensors ---
    unsigned long currentTime = millis();

    if (currentTime - lastReadTime >= READ_INTERVAL_MS)
    {
        lastReadTime = currentTime;

        // --- Temperature reading ---
        readCount++;                               // Increment read count
        float temp = tempSensor.readTemperature(); // Read temperature
        tempLogger.addReading(temp, readCount);    // Add reading to logger

        Serial.printf("#%d, %d ms, %.2f°C\n", readCount, lastReadTime, temp);

        // --- Every 20 readings: take photo and Write log to SD ---
        if (readCount % PICTURE_INTERVAL == 0)
        {
            tempSensor.deinit(); // Deinitialize sensor to save power
            delay(100);          // Wait for deinit to complete

            // Take log and save to SD
            String buffer = tempLogger.getLog();                      // Get log buffer
            sdManager.saveLog(buffer, "/" + experimentName + ".txt"); // Append to SD file
            tempLogger.clear();                                       // Clear log buffer

            // Take picture
            camera_fb_t *fb = camera.capturePhoto(); // Capture photo
            if (fb)
            {
                // Filename of the capture
                String filename = "/" + experimentName + "_" + String(readCount) + ".jpg";
                // Save image to SD
                sdManager.saveImage(fb->buf, fb->len, filename);
                // Deinit camera and return frame buffer
                camera.deinit(); //
            }

            tempSensor.init(); // Reinitialize sensor
        }
    }
    delay(TEMP_READ_INTERVAL);
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

// Web server handling
/* // Handle incoming web requests
    webServer.handleRequests(); */
