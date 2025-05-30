// src/CameraManager.cpp
#include "CameraManager.h"
#include <ArduinoJson.h>
#include <LittleFS.h>

// Constructor definition using
CameraManager::CameraManager() : sensor(nullptr), lastFrameBuffer(nullptr) {}

// Initialize the camera manager
bool CameraManager::init()
{

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

    // Configure frame size and quality based on PSRAM availability
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

    // Initialize the camera with the config settings
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK)
    {
        Serial.printf("Camera init failed with error 0x%x", err);
        return false;
    }

    // SOMEHTING HERE
    pinMode(4, OUTPUT); // Prevent flash LED toggling, allow sensor to use it safely
    digitalWrite(4, LOW);

    // Initialize the camera sensor
    sensor = esp_camera_sensor_get();
    if (!sensor)
    {
        Serial.println("Failed to get camera sensor");
        return false; // If sensor isn't available, initialization fails
    }

    Serial.println("Camera initialized successfully");
    return true;
}

// Deinitialize the camera
void CameraManager::deinit()
{
    if (lastFrameBuffer)
    {
        esp_camera_fb_return(lastFrameBuffer);
        lastFrameBuffer = nullptr;
    }
    esp_camera_deinit();
    sensor = nullptr;

    Serial.println("Camera deinitialized and frame buffer returned.");
}

// Apply setting from a JSON file
bool CameraManager::loadSettings(const char *path)
{
    // Debug: Check if the file system is mounted
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
        Serial.printf("FS Found: %s\n", file_check.name());
        file_check = root.openNextFile();
    }

    // Debug: Try to open the settings file
    File file = LittleFS.open(path, "r");
    if (!file)
    {
        Serial.println("Failed to open settings file");
        return false;
    }

    // Debug: Check if the file exists
    if (!LittleFS.exists(path))
    {
        Serial.printf("File %s not found!\n", path);
        return false;
    }

    // Read the file and parse JSON
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, file);
    file.close();

    // handle errors
    if (error)
    {
        Serial.println("Failed to parse JSON");
        return false;
    }

    // Apply settings to the camera
    sensor_t *s = esp_camera_sensor_get(); // This fucntion alwys return the adress of camera sensor

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

// Capture a photo and return the frame buffer
camera_fb_t *CameraManager::capturePhoto()
{
    if (!init()) // Initialize the camera if not already done
    {
        Serial.println("Camera initialization failed!");
        return nullptr;
    }

    Serial.println("Capturing photo...");
    camera_fb_t *lastFrameBuffer = esp_camera_fb_get();
    if (!lastFrameBuffer)
    {
        Serial.println("Failed to capture image");
        return nullptr;
    }

    Serial.printf("Captured image: %d bytes\n", lastFrameBuffer->len);
    // deinit(); // Deinitialize the camera after capturing

    return lastFrameBuffer;
}
