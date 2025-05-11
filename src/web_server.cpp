#include "web_server.h"
#include "camera_utils.h"
#include "html_pages.h"

#include <WiFi.h>
#include <WebServer.h>

WebServer server(80);

// This function sets up the web server and its routes
void setupWebServer()
{
  // Main page route
  server.on("/", HTTP_GET, []()
            { server.send(200, "text/html", MAIN_page); });

  // Image route
  server.on("/cam.jpg", HTTP_GET, handleImageCapture);

  // Camera settings routes
  server.on("/settings", HTTP_GET, handleSettingsPage);
  server.on("/update_setting", HTTP_POST, handleCameraSettingUpdate);

  // LED control route (if you're using it)
  server.on("/led", HTTP_GET, []()
            {
    if (server.hasArg("state"))
    {
      String state = server.arg("state");
      /// Inverted logic: LOW = ON, HIGH = OFF
      digitalWrite(4, state == "on" ? LOW : HIGH);
      server.send(200, "text/plain", "LED " + state);

      // Debug output
      Serial.printf("LED set to: %s\n", state == "on" ? "ON" : "OFF");
    }
    else
    {
      server.send(400, "text/plain", "Missing state parameter");
    } });

  // Add status endpoint
  server.on("/led_status", HTTP_GET, []()
            {
  bool ledState = digitalRead(4) == LOW; // LOW means ON
  server.send(200, "text/plain", ledState ? "on" : "off"); });

  // Debug: Add a catch-all handler for undefined routes
  server.onNotFound([]()
                    {
    String message = "File Not Found\n\n";
    message += "URI: ";
    message += server.uri();
    message += "\nMethod: ";
    message += (server.method() == HTTP_GET) ? "GET" : "POST";
    message += "\nArguments: ";
    message += server.args();
    message += "\n";
    for (uint8_t i = 0; i < server.args(); i++) {
      message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
    }
    server.send(404, "text/plain", message); });

  server.begin();
  Serial.println("HTTP server started");
}

// Handle incoming web requests
void handleWebRequests()
{
  server.handleClient();
}

// Handle the Main page (verify)
void handleMainPage()
{
  server.send(200, "text/html", MAIN_page);
}

// Handle camera server (delete)
void startCameraServer()
{
  server.on("/", HTTP_GET, handleMainPage);
  server.on("/cam.jpg", HTTP_GET, handleImageCapture);
  server.on("/settings", HTTP_GET, handleSettingsPage);
  server.on("/update_setting", HTTP_POST, handleCameraSettingUpdate);
  server.begin();
}

// Handle image capture
void handleImageCapture()
{
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb)
  {
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }

  // Add cache control headers
  server.sendHeader("Cache-Control", "no-cache, no-store, must-revalidate");
  server.sendHeader("Pragma", "no-cache");
  server.sendHeader("Expires", "-1");

  // Send the image
  server.sendHeader("Content-Type", "image/jpeg");
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

// ------------------------- SETINGG FUNCTIONS -------------------------
// Handle the settings page
void handleSettingsPage()
{
  server.send(200, "text/html", CAMERA_SETTINGS_page);
}

// Handle camera setting updates from the web form
void handleCameraSettingUpdate()
{
  // Get current sensor reference
  sensor_t *s = esp_camera_sensor_get();
  if (!s)
  {
    server.send(500, "text/plain", "Camera sensor not found");
    return;
  }

  // Process each possible setting
  if (server.hasArg("vflip"))
  {
    s->set_vflip(s, server.arg("vflip").toInt());
  }
  if (server.hasArg("hmirror"))
  {
    s->set_hmirror(s, server.arg("hmirror").toInt());
  }
  if (server.hasArg("brightness"))
  {
    s->set_brightness(s, server.arg("brightness").toInt());
  }
  if (server.hasArg("contrast"))
  {
    s->set_contrast(s, server.arg("contrast").toInt());
  }
  if (server.hasArg("saturation"))
  {
    s->set_saturation(s, server.arg("saturation").toInt());
  }
  if (server.hasArg("framesize"))
  {
    s->set_framesize(s, (framesize_t)server.arg("framesize").toInt());
  }
  if (server.hasArg("quality"))
  {
    s->set_quality(s, server.arg("quality").toInt());
  }

  // Save settings to JSON file
  if (saveCameraSettingsToJSON())
  {
    server.send(200, "text/plain", "Settings updated and saved");
  }
  else
  {
    server.send(500, "text/plain", "Failed to save settings");
  }
}