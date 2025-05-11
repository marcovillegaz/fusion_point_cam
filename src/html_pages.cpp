// html_pages.cpp
#include "html_pages.h"

// Define the HTML main page
const char MAIN_page[] PROGMEM = R"rawliteral(
        <!DOCTYPE html>
        <html>
        <head>
          <title>ESP32-CAM Live</title>
          <meta http-equiv="refresh" content="0.5">
        </head>
        <body style="text-align:center;">
          <h2>Live Camera</h2>
          <img src="/cam.jpg" style="width:100%;max-width:640px;"><br>
          <a href="/settings">Camera Settings</a>
        </body>
        </html>
    )rawliteral";

// Define the HTML test page
const char TEST_page[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>ESP32 Web Page</title>
  <style>
    body { font-family: Arial; background-color: #f4f4f4; text-align: center; padding: 50px; }
    h1 { color: #333; }
  </style>
</head>
<body>
  <h1>Hello from ESP32-CAM!</h1>
  <p>This is a custom HTML page served by your ESP32.</p>
</body>
</html>
)rawliteral";

// Define the HTML camera settings page
const char CAMERA_SETTINGS_page[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>ESP32-CAM Settings</title>
</head>
<body>
  <h2>Camera Settings (Experimental)</h2>

  <label>Vertical Flip:
    <input type="checkbox" id="vflip" onchange="updateSetting()">
  </label><br>

  <label>Horizontal Mirror:
    <input type="checkbox" id="hmirror" onchange="updateSetting()">
  </label><br>

  <label>Brightness (-2 to 2):
    <input type="range" min="-2" max="2" value="0" id="brightness" onchange="updateSetting()">
  </label><br>

  <label>Contrast (-2 to 2):
    <input type="range" min="-2" max="2" value="0" id="contrast" onchange="updateSetting()">
  </label><br>

  <label>Saturation (-2 to 2):
    <input type="range" min="-2" max="2" value="0" id="saturation" onchange="updateSetting()">
  </label><br>

  <img id="preview" src="/cam.jpg" style="max-width:100%; margin-top:20px;"><br>

  <script>
    function updateSetting() {
      const settings = {
        vflip: document.getElementById('vflip').checked ? 1 : 0,
        hmirror: document.getElementById('hmirror').checked ? 1 : 0,
        brightness: parseInt(document.getElementById('brightness').value),
        contrast: parseInt(document.getElementById('contrast').value),
        saturation: parseInt(document.getElementById('saturation').value)
      };

      fetch('/update_setting', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      const img = document.getElementById("preview");
      img.src = "/cam.jpg?rand=" + Math.random();
    }
  </script>
</body>
</html>
)rawliteral";