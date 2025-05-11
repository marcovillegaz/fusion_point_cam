// src/camera_utils.cpp
#include "camera_utils.h"
#include "html_pages.h"
#include <ArduinoJson.h>

#include <FS.h>
#include <LittleFS.h>

bool applyCameraSettingsFromJSON(const char *path)
{
    // Check if the file system is mounted
    if (!LittleFS.begin())
    {
        Serial.println("Failed to mount FS");
        return false;
    }

    // Debug: List all files (optional)
    File root = LittleFS.open("/");
    File file_check = root.openNextFile();
    while (file_check)
    {
        Serial.printf("Found: %s\n", file_check.name());
        file_check = root.openNextFile();
    }

    // Debug: List files in root
    File file = LittleFS.open(path, "r");
    if (!file)
    {
        Serial.println("Failed to open settings file");
        return false;
    }

    // Check if the file exists
    if (!LittleFS.exists(path))
    {
        Serial.printf("File %s not found!\n", path);
        return false;
    }

    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, file);
    file.close();

    if (error)
    {
        Serial.println("Failed to parse JSON");
        return false;
    }

    sensor_t *s = esp_camera_sensor_get();
    if (!s)
        return false;

    if (doc.containsKey("vflip"))
        s->set_vflip(s, doc["vflip"]);
    if (doc.containsKey("hmirror"))
        s->set_hmirror(s, doc["hmirror"]);
    if (doc.containsKey("brightness"))
        s->set_brightness(s, doc["brightness"]);
    if (doc.containsKey("contrast"))
        s->set_contrast(s, doc["contrast"]);
    if (doc.containsKey("saturation"))
        s->set_saturation(s, doc["saturation"]);
    if (doc.containsKey("framesize"))
        s->set_framesize(s, (framesize_t)doc["framesize"].as<int>());
    if (doc.containsKey("quality"))
        s->set_quality(s, doc["quality"]);

    Serial.println("Camera settings applied from JSON.");
    return true;
}

bool initCamera()
{
    // Set up camera configuration for OV2640
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = 5;
    config.pin_d1 = 18;
    config.pin_d2 = 19;
    config.pin_d3 = 21;
    config.pin_d4 = 36;
    config.pin_d5 = 39;
    config.pin_d6 = 34;
    config.pin_d7 = 35;
    config.pin_xclk = 0;
    config.pin_pclk = 22;
    config.pin_vsync = 25;
    config.pin_href = 23;
    config.pin_sccb_sda = 26;
    config.pin_sccb_scl = 27;
    config.pin_pwdn = 32;
    config.pin_reset = -1;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Set the frame size and quality based on PSRAM availability
    if (psramFound())
    {
        config.frame_size = FRAMESIZE_VGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
    }
    else
    {
        config.frame_size = FRAMESIZE_QVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
    }

    // Initialize the camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK)
    {
        Serial.printf("Camera init failed with error 0x%x", err);
        return false;
    }

    return true;
}

// Handle the settings page
void handleSettingsPage()
{
    server.send(200, "text/html", CAMERA_SETTINGS_page);
}

// Handle camera settings update
void handleCameraSettingUpdate()
{
    if (!server.hasArg("plain"))
    {
        server.send(400, "text/plain", "Body not received");
        return;
    }

    String body = server.arg("plain");
    JsonDocument doc;
    deserializeJson(doc, body);

    sensor_t *s = esp_camera_sensor_get();
    if (!s)
    {
        server.send(500, "text/plain", "Sensor not found");
        return;
    }

    s->set_vflip(s, doc["vflip"]);
    s->set_hmirror(s, doc["hmirror"]);
    s->set_brightness(s, doc["brightness"]);
    s->set_contrast(s, doc["contrast"]);
    s->set_saturation(s, doc["saturation"]);

    server.send(200, "text/plain", "Settings updated");
}