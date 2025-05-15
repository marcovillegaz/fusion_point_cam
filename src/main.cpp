#include <Arduino.h>
#include "wifi_setup.h"
#include "camera_utils.h"
#include "web_server.h"

#include "CameraManager.h"
#include "TemperatureSensor.h"
// #include "MicroSDManager.h"
#include "WebServerManager.h"

#include "secrets.h" // Include your WiFi credentials here

#define TEMP_SENSOR_PIN 4
#define TEMP_READ_INTERVAL 3000 // in milliseconds

// IPAddress staticIP(192, 168, 1, 184); // Optional static IP
// IPAddress local_IP(0, 0, 0, 0); // forces DHCP instead of static
TemperatureSensor tempSensor(TEMP_SENSOR_PIN);
CameraManager cam;          // CameraManager instance
WebServerManager webServer; // WebServerManager instance

void setup()
{
    Serial.begin(115200); // Initialize serial communication
    delay(1000);

    // Camera initialization
    if (!cam.init())
    {
        Serial.println("Camera initialization failed!");
        while (1)
            delay(100);
    }

    // Load setting from json to camera
    /*     if (!applyCameraSettingsFromJSON())
        {
            Serial.println("Using default camera settings");
        } */

    if (!tempSensor.init())
    {
        Serial.println("Temperature sensor initialization failed!");
        while (1)
            delay(100);
    }

    /* connectToWiFi(ssid, password); // Connect to WiFi

    // Start web server
    setupWebServer(); */
}

void loop()
{
    // TEMPERATURE READING
    float temperature = tempSensor.readTemperature();
    float variance = tempSensor.getVariance();

    Serial.print("Temperature: ");
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
    }

    delay(TEMP_READ_INTERVAL);

    /* handleWebRequests();
    delay(2); // Allow background tasks */
}