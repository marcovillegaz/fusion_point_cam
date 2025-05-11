#include <Arduino.h>
#include "wifi_setup.h"
#include "camera_utils.h"
#include "web_server.h"

#include "secrets.h" // Include your WiFi credentials here

// IPAddress staticIP(192, 168, 1, 184); // Optional static IP
IPAddress local_IP(0, 0, 0, 0); // forces DHCP instead of static

void setup()
{
    Serial.begin(115200); // Initialize serial communication
    delay(1000);

    connectToWiFi(ssid, password, local_IP); // Connect to WiFi
    // testWebServer();                    // Setup web server (shows a simple HTML page)

    // Initialize camera
    if (!initCamera())
    {
        Serial.println("Camera initialization failed!");
        while (1)
            delay(100);
    }

    // Load saved settings
    if (!applyCameraSettingsFromJSON())
    {
        Serial.println("Using default camera settings");
    }

    Serial.println("Camera ready");

    // Start web server
    setupWebServer();
}

void loop()
{
    handleWebRequests();
    delay(2); // Allow background tasks
}