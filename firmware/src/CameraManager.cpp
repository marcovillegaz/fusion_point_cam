// src/CameraManager.cpp
#include "CameraManager.h"
#include <ArduinoJson.h>
#include <LittleFS.h>

// Constructor definition using
CameraManager::CameraManager() : sensor(nullptr), lastFrameBuffer(nullptr) {}

// Initialize the camera manager
bool CameraManager::init()
{
    // Camera doesn't use GPIO4 directly, but ensure clean state
    pinMode(4, INPUT);
    delay(100); // Allow time for the pin state to stabilize

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
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 10;
        config.fb_count = 1;
        Serial.println("[CAMERA] PSRAM found, using higher resolution and quality settings.");
        Serial.printf("Free PSRAM: %d bytes\n", heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    }
    else
    {
        config.frame_size = FRAMESIZE_QVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
        Serial.println("[CAMERA] No PSRAM found, using lower resolution and quality settings.");
    }

    // Initialize the camera with the config settings
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK)
    {
        Serial.printf("[CAMERA] Camera init failed with error 0x%x", err);
        return false;
    }

    // SOMEHTING HERE
    pinMode(4, OUTPUT); // Prevent flash LED toggling, allow sensor to use it safely
    digitalWrite(4, LOW);

    // Initialize the camera sensor
    sensor = esp_camera_sensor_get();
    if (!sensor)
    {
        Serial.println("[CAMERA] Failed to get camera sensor");
        return false; // If sensor isn't available, initialization fails
    }

    /* // 1) Disable all “auto” features:
    sensor->set_gain_ctrl(sensor, 0);     // turn off auto‐gain
    sensor->set_exposure_ctrl(sensor, 0); // turn off auto‐exposure
    sensor->set_awb_gain(sensor, 1);      // use the fixed AWB table (no continuous WB changes)

    // 2) Fix your exposure‐gain combo:
    sensor->set_agc_gain(sensor, 10);   // set analog/digital gain to 10 out of 30
    sensor->set_aec_value(sensor, 500); // fix exposure target (long integration time) */

    // --- Additional sensor configuration ---
    sensor->set_brightness(sensor, 1);     // -2 to 2
    sensor->set_contrast(sensor, 2);       // -2 to 2
    sensor->set_saturation(sensor, -1);    // -2 to 2
    sensor->set_special_effect(sensor, 2); // 0=No effect, 1=Negative, 2=Grayscale, etc.
    sensor->set_whitebal(sensor, 1);       // Enable white balance
    sensor->set_awb_gain(sensor, 1);       // Auto white balance gain

    // sensor->set_wb_mode(sensor, 0);        // White balance mode (0=Auto, 1=Sunny...)
    // sensor->set_exposure_ctrl(sensor, 1);  // Enable exposure control
    // sensor->set_aec2(sensor, 1);           // Enable AE level adjustment
    // sensor->set_ae_level(sensor, 0);       // Adjust AE level, range -2 to 2
    // sensor->set_gain_ctrl(sensor, 1);      // Auto gain control
    // sensor->set_agc_gain(sensor, 0);       // AGC gain, 0 to 30
    // sensor->set_gainceiling(sensor, (gainceiling_t)0); // Gain ceiling
    // sensor->set_bpc(sensor, 0);            // Black pixel correction
    // sensor->set_wpc(sensor, 1);            // White pixel correction
    // sensor->set_raw_gma(sensor, 1);        // Raw gamma
    // sensor->set_lenc(sensor, 1);           // Lens correction

    // Optional flips/mirror for orientation correction
    sensor->set_hmirror(sensor, 1); // Horizontal mirror (0 or 1)
    sensor->set_vflip(sensor, 0);   // Vertical flip (0 or 1)

    Serial.println("[CAMERA] Camera initialized successfully");
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
    delay(200);

    Serial.println("[CAMERA] Camera deinitialized and frame buffer returned.");
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
        Serial.println("[CAMERA] Camera initialization failed!");
        return nullptr;
    }

    // loadSettings("/cam_config.json"); // Optional: load last settings

    Serial.println("[CAMERA] Capturing photo...");
    camera_fb_t *lastFrameBuffer = esp_camera_fb_get();
    if (!lastFrameBuffer)
    {
        Serial.println("[CAMERA] Failed to capture image");
        return nullptr;
    }

    Serial.printf("[CAMERA] Captured image: %d bytes\n", lastFrameBuffer->len);

    return lastFrameBuffer;
}
