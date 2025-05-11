#include "web_server.h"
#include "camera_utils.h"
#include "html_pages.h"

#include <WiFi.h>
#include <WebServer.h>

WebServer server(80);

/* void handleRoot()
{
  server.send(200, "text/html", TEST_page);
}

// Web server to perform tests
void testWebServer()
{
  server.on("/", handleRoot);
  server.begin();
  Serial.println("Web server started.");
} */

// This function sets up the web server and its routes
void setupWebServer()
{
  // Main page route
  server.on("/", HTTP_GET, []()
            { server.send(200, "text/html", MAIN_page); });

  // Image route
  server.on("/jpg", HTTP_GET, []()
            {
      camera_fb_t* fb = esp_camera_fb_get();
      if (!fb) {
          server.send(500, "text/plain", "Camera capture failed");
          return;
      }

      server.sendHeader("Content-Type", "image/jpeg");
      server.send_P(200, "image/jpeg", (const char*)fb->buf, fb->len);
      esp_camera_fb_return(fb); });

  // LED control route
  server.on("/led", HTTP_GET, []()
            {
        String state = server.arg("state");
        digitalWrite(4, state == "on" ? HIGH : LOW);
        server.send(200, "text/plain", "LED " + state); });

  // Camera settings routes
  server.on("/settings", HTTP_GET, handleSettingsPage);
  server.on("/update_setting", HTTP_POST, handleCameraSettingUpdate);

  server.begin();
  Serial.println("HTTP server started");
}

// Handle incoming web requests
void handleWebRequests()
{
  server.handleClient();
}

// Handle the Main page
void handleMainPage()
{
  server.send(200, "text/html", MAIN_page);
}

// Handle camera server
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

  server.sendHeader("Content-Type", "image/jpeg");
  server.send_P(200, "image/jpeg", (char *)fb->buf, fb->len);
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