#include "WebServerManager.h"

WebServerManager::WebServerManager(uint16_t port) : server(port), myCam(nullptr) {}

// Setup web server and its routes
void WebServerManager::setup(CameraManager *myCam)
{
    this->myCam = myCam; // Store the pointer to the camera manager
    
    // Main page route
    server.on("/", HTTP_GET, [this]()
              { handleMainPage(); });
    // Image route
    server.on("/cam.jpg", HTTP_GET, [this]()
              { handleImageCapture(); });
    // Camera settings routes
    server.on("/settings", HTTP_GET, [this]()
              { handleSettingsPage(); });
    server.on("/update_setting", HTTP_POST, [this]()
              { handleCameraSettingUpdate(); });
    // LED control route
    server.on("/led", HTTP_GET, [this]()
              { handleLEDControl(); });
    // LED status route
    server.on("/led_status", HTTP_GET, [this]()
              { handleLEDStatus(); });

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

// Handlers
void WebServerManager::handleMainPage()
{
    server.send(200, "text/html", MAIN_page);
}

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

void WebServerManager::handleSettingsPage()
{
    server.send(200, "text/html", CAMERA_SETTINGS_page);
}

/* void WebServerManager::handleCameraSettingUpdate()
{
} */

void WebServerManager::handleLEDControl()
{
    if (server.hasArg("state"))
    {
        String state = server.arg("state");
        digitalWrite(4, state == "on" ? LOW : HIGH);
        server.send(200, "text/plain", "LED " + state);
        Serial.printf("LED set to: %s\n", state == "on" ? "ON" : "OFF");
    }
    else
    {
        server.send(400, "text/plain", "Missing state parameter");
    }
}

void WebServerManager::handleLEDStatus()
{
    bool ledState = digitalRead(4) == LOW; // LOW means ON
    server.send(200, "text/plain", ledState ? "on" : "off");
}

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