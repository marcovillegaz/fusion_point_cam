#include <Arduino.h>
#include "wifi_setup.h"
#include "camera_utils.h"

const char *ssid = "yourSSID";
const char *password = "yourPASS";
IPAddress staticIP(192, 168, 1, 184); // Optional static IP

void setup()
{
    Serial.begin(115200);
    delay(1000);
    connectToWiFi(ssid, password, staticIP);
    // Setup camera or web server next

    if (!initCamera())
    {
        Serial.println("Camera failed to initialize");
        while (true)
            ; // Halt
    }

    Serial.println("Camera ready");
}

void loop()
{
    // Your main logic
}
