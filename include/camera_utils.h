// include/camera_utils.h
#pragma once

#include <esp_camera.h>
#include <arduino.h>
#include <WebServer.h>
#include <ArduinoJson.h>

#include <FS.h>
#include <LittleFS.h>

extern WebServer server;

// Initializes the camera and returns true if successful
bool initCamera();
bool applyCameraSettingsFromJSON(const char *path = "/camera_settings.json");
bool saveCameraSettingsToJSON(const char *path = "/camera_settings.json");