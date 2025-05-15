// include/CameraManager.h
#pragma once

#include <esp_camera.h>
#include <WebServer.h>

// This class manages the camera settings and interactions with the web server
class CameraManager
{
public:
    CameraManager();

    bool init(); // Unit camera, alway first
    bool loadSettings(const char *path = "/camera_settings.json");
    bool saveSettings(const char *path = "/camera_settings.json");
   
    sensor_t *sensor;

};
