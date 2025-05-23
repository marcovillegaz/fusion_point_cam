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
    camera_fb_t *capturePhoto(); // Capture a photo and return the frame buffer
    void deinit();               // Deinitialize the camera

    sensor_t *sensor;
    camera_fb_t *lastFrameBuffer;
};
