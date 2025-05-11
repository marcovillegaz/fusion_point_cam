#include "web_server.h"
#include "camera_utils.h"
#include "html_page.h"

#include <WiFi.h>
#include <WebServer.h>

WebServer server(80);

void handleRoot()
{
  server.send(200, "text/html", TEST_page);
}

void testWebServer()
{
  server.on("/", handleRoot);
  server.begin();
  Serial.println("Web server started.");
}

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

  server.begin();
  Serial.println("HTTP server started");
}

// Handle incoming web requests
void handleWebRequests()
{
  server.handleClient();
}

/* void startWebServer()
{
  server.on("/", HTTP_GET, []()
            {
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            server.send(500, "text/plain", "Camera capture failed");
            return;
        }

        server.sendHeader("Content-Type", "image/jpeg");
        server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
        server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);
        esp_camera_fb_return(fb); });

  server.begin();
  Serial.println("HTTP server started");
} */
