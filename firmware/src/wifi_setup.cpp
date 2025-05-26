// WiFi Setup for ESP32
// This code connects the ESP32 to a WiFi network and configures 
// the local IP address if provided.

#include "wifi_setup.h"

void connectToWiFi(const char* ssid, const char* password, IPAddress local_IP) {
    if (local_IP != IPAddress(0,0,0,0)) {
        IPAddress gateway(192, 168, 1, 1);
        IPAddress subnet(255, 255, 255, 0);
        WiFi.config(local_IP, gateway, subnet);
    }

    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");

    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
        delay(500);
        Serial.print(".");
        retries++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nConnected to WiFi!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nFailed to connect to WiFi.");
    }
}
