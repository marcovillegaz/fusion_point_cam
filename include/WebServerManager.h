#pragma once

#include <WebServer.h>
#include <WiFi.h>
#include <LittleFS.h>
#include <ArduinoJson.h>

#include "CameraManager.h"
#include "TemperatureSensor.h"

#include "html_pages.h"

class WebServerManager
{
public:
    WebServerManager(uint16_t port = 80);

    void init(CameraManager *myCam); // accepts a pointer to the camera manager
    void handleRequests();

private:
    WebServer server;
    CameraManager *myCam;

    void handleMainPage();
    void handleImageCapture();
    bool saveCameraSettings(const char *path = "/cam_settings.json");
    void handleSettingsPage();
    void handleCameraSettingUpdate();
    void handleNotFound();
};
