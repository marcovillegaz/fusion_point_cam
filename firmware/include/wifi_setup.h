#ifndef WIFI_SETUP_H
#define WIFI_SETUP_H

#include <WiFi.h>

void connectToWiFi(const char* ssid, const char* password, IPAddress local_IP = IPAddress(0,0,0,0));

#endif