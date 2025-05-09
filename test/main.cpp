#include "esp_camera.h"
#include <WiFi.h>

// Replace with your network credentials
const char *ssid = "VTR-1334483";
const char *password = "Vq3pqvcxhMcy";

// Uncomment the relevant camera model configuration

// AI Thinker Module Configuration
// #define CAMERA_MODEL_AI_THINKER
// #include "camera_pins.h"

// RHXY-M21-45 Camera Configuration (your camera model)
#define CAMERA_MODEL_RHXY_M21_45
#define PWDN_GPIO_NUM -1
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

// M5Stack Camera Module (example)
// #define CAMERA_MODEL_M5STACK_PSRAM
// #include "camera_pins.h"

// Additional modules can be defined similarly...

void startCameraServer();

void setup()
{
  Serial.begin(115200);
  Serial.println("Booting...");

  // Camera configuration
  camera_config_t config;

  // Check the model you're testing and select the correct pinout
#if defined(CAMERA_MODEL_RHXY_M21_45)
  // RHXY-M21-45 Camera settings
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000;         // Lower clock for stability
  config.pixel_format = PIXFORMAT_RGB565; // RGB format for display apps
  config.frame_size = FRAMESIZE_QQVGA;    // Low resolution to reduce lag
  config.jpeg_quality = 10;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
#elif defined(CAMERA_MODEL_AI_THINKER)
  // AI Thinker Camera settings (default for ESP32-CAM)
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 12;
  config.pin_d1 = 13;
  config.pin_d2 = 14;
  config.pin_d3 = 15;
  config.pin_d4 = 16;
  config.pin_d5 = 17;
  config.pin_d6 = 18;
  config.pin_d7 = 19;
  config.pin_xclk = 21;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;
  config.pin_pwdn = -1;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;       // Standard 20 MHz clock for ESP32-CAM
  config.pixel_format = PIXFORMAT_JPEG; // Common JPEG format
  config.frame_size = FRAMESIZE_VGA;    // VGA resolution
  config.jpeg_quality = 10;
  config.fb_count = 2;
  config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
#endif

  // Initialize the camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK)
  {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println("Camera Stream Ready! Go to:");
  Serial.println(WiFi.localIP());

  // Start camera server
  startCameraServer();
}

void loop()
{
  delay(10000); // nothing to do here
}

// Basic camera stream server
#include "esp_http_server.h"

esp_err_t stream_handler(httpd_req_t *req)
{
  camera_fb_t *fb = NULL;
  esp_err_t res;

  res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");
  if (res != ESP_OK)
    return res;

  while (true)
  {
    fb = esp_camera_fb_get();
    if (!fb)
    {
      Serial.println("Camera capture failed");
      return ESP_FAIL;
    }

    char header[64];
    sprintf(header, "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n", fb->len);
    res = httpd_resp_send_chunk(req, header, strlen(header));
    res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
    res = httpd_resp_send_chunk(req, "\r\n", 2);

    esp_camera_fb_return(fb);
    if (res != ESP_OK)
      break;
  }
  return res;
}

void startCameraServer()
{
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();

  httpd_uri_t uri = {
      .uri = "/",
      .method = HTTP_GET,
      .handler = stream_handler,
      .user_ctx = NULL};

  httpd_handle_t server = NULL;
  if (httpd_start(&server, &config) == ESP_OK)
  {
    httpd_register_uri_handler(server, &uri);
  }
}
