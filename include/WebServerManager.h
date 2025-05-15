#pragma once

#include <WebServer.h>
#include <WiFi.h>
#include "CameraManager.h"
#include "html_pages.h"

class WebServerManager
{
public:
    WebServerManager(uint16_t port = 80);

    void setup(CameraManager *myCam); // accepts a pointer to the camera manager
    void handleRequests();

private:
    WebServer server;
    CameraManager *myCam;

    void handleMainPage();
    void handleImageCapture();
    void handleSettingsPage();
    void handleCameraSettingUpdate();
    void handleLEDControl();
    void handleLEDStatus();
    void handleNotFound();
};
