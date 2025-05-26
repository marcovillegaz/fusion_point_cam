#include "WebServerManager.h"
#include <WebServer.h>

WebServerManager::WebServerManager(uint16_t port)
    : server(port),
      myCam(nullptr)
{
}

// Setup web server and its routes
void WebServerManager::init(CameraManager *myCam)
{
    this->myCam = myCam;             // Store the pointer to the camera manager

    if (!LittleFS.begin(true))
    {
        Serial.println("LittleFS mount failed");
        // Handle error accordingly, maybe return early
    }

    // --- Web server routes ---
    // Main page route
    server.on("/", HTTP_GET, [this]()
              { handleMainPage(); });
    // Image route
    server.on("/cam.jpg", HTTP_GET, [this]()
              { handleImageCapture(); });
    // Setting route
    server.on("/settings", HTTP_GET, [this]()
              { handleSettingsPage(); });
    // Set setting route
    server.on("/set-config", HTTP_POST, [this]()
              { handleCameraSettingUpdate(); });
    // Include the logger fucntion here later.
    server.on("/start-log", HTTP_GET, [this]() {});

    // Catch-all handler for undefined routes
    server.onNotFound([this]()
                      { handleNotFound(); });

    server.begin();
    Serial.println("HTTP server started");
}

// Handle incoming web requests
void WebServerManager::handleRequests()
{
    server.handleClient();
}

// Main page handler
void WebServerManager::handleMainPage()
{
    File file = LittleFS.open("/main.html", "r");
    if (!file)
    {
        server.send(500, "text/plain", "Failed to open main page");
        return;
    }

    // Send the file content with the proper MIME type
    server.streamFile(file, "text/html");
    file.close();
}

// Image capture handler
void WebServerManager::handleImageCapture()
{
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb)
    {
        server.send(500, "text/plain", "Camera capture failed");
        return;
    }
    server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate");
    server.sendHeader("Pragma", "no-cache");
    server.sendHeader("Expires", "-1");
    server.sendHeader("Content-Type", "image/jpeg");
    server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
    esp_camera_fb_return(fb);
}

// Camera settings page
void WebServerManager::handleSettingsPage()
{
    server.send(200, "text/html", CAMERA_SETTINGS_page);
}

// Handle camera setting updates
void WebServerManager::handleCameraSettingUpdate()
{
    if (server.hasArg("plain") == false) {
        server.send(400, "text/plain", "Body not received");
        return;
    }

    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, server.arg("plain"));

    if (error) {
        server.send(400, "text/plain", "JSON parse failed");
        return;
    }

    // Save new settings to file
    File file = LittleFS.open("/cam_config.json", "w");
    if (!file) {
        server.send(500, "text/plain", "Failed to open config file");
        return;
    }

    serializeJson(doc, file);
    file.close();

    if (myCam->loadSettings("/cam_config.json")) {
        server.send(200, "text/plain", "Settings updated successfully");
    } else {
        server.send(500, "text/plain", "Failed to apply settings");
    }
}

// Save camera settings
bool WebServerManager::saveCameraSettings(const char *path)
{
    if (!LittleFS.begin(true))
    {
        Serial.println("Failed to mount LittleFS");
        return false;
    }

    // Get current camera settings
    sensor_t *s = esp_camera_sensor_get();
    if (!s)
    {
        Serial.println("Failed to get camera sensor");
        return false;
    }

    // Create JSON document
    JsonDocument doc;

    doc["vflip"] = s->status.vflip;
    doc["hmirror"] = s->status.hmirror;
    doc["brightness"] = s->status.brightness;
    doc["contrast"] = s->status.contrast;
    doc["saturation"] = s->status.saturation;
    doc["framesize"] = s->status.framesize;
    doc["quality"] = s->status.quality;

    // Write to file
    File file = LittleFS.open(path, "w");
    if (!file)
    {
        Serial.println("Failed to open file for writing");
        return false;
    }

    serializeJson(doc, file);
    file.close();

    Serial.println("Camera settings saved to JSON");
    return true;
}

// Handle not founds
void WebServerManager::handleNotFound()
{
    String message = "File Not Found\n\n";
    message += "URI: ";
    message += server.uri();
    message += "\nMethod: ";
    message += (server.method() == HTTP_GET) ? "GET" : "POST";
    message += "\nArguments: ";
    message += server.args();
    message += "\n";
    for (uint8_t i = 0; i < server.args(); i++)
    {
        message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
    }
    server.send(404, "text/plain", message);
}