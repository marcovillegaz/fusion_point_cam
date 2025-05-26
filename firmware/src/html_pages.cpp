// html_pages.cpp
#include "html_pages.h"

// Define the HTML main page
const char MAIN_page[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>ESP32-CAM Live</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      text-align: center;
      margin: 20px;
    }
    #liveImg {
      max-width: 100%;
      height: auto;
      margin: 10px 0;
    }
    .btn {
      display: inline-block;
      padding: 10px 20px;
      margin: 5px;
      color: white;
      text-decoration: none;
      border-radius: 5px;
      border: none;
      cursor: pointer;
    }
    #ledBtn {
      background-color: #4CAF50;
    }
    #ledBtn.off {
      background-color: #f44336;
    }
    .settings-btn {
      background-color: #2196F3;
    }
  </style>
</head>
<body>
  <h2>ESP32-CAM Live Stream</h2>
  <img id="liveImg" src="/cam.jpg">
  <div>
    <button id="ledBtn" class="btn" onclick="toggleLED()">LED OFF</button>
    <a href="/settings" class="btn settings-btn">Settings</a>
    <button onclick="refreshImage()" class="btn">Refresh</button>
  </div>

  <script>
    let ledState = false;
    
    // Toggle LED function
    function toggleLED() {
      ledState = !ledState;
      const btn = document.getElementById('ledBtn');
      btn.textContent = ledState ? 'LED ON' : 'LED OFF';
      btn.classList.toggle('off', !ledState);
      
      fetch(`/led?state=${ledState ? 'on' : 'off'}`)
        .then(response => response.text())
        .then(data => console.log(data))
        .catch(err => console.error('Error:', err));
    }

    // Auto-refresh image every 60 seconds
    setInterval(updateImage, 60000);
    
    function updateImage() {
      document.getElementById('liveImg').src = '/cam.jpg?t=' + Date.now();
    }
    
    function refreshImage() {
      updateImage();
    }
    
    // Initial load
    window.onload = updateImage;
  </script>
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
  <title>Camera Settings</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    form { max-width: 500px; }
    .form-group { margin-bottom: 15px; }
    label { display: inline-block; width: 150px; }
    button { padding: 8px 15px; margin-top: 10px; }
  </style>
</head>
<body>
  <h1>Camera Settings</h1>
  <form action="/update_setting" method="POST">
    <div class="form-group">
      <label for="vflip">Vertical Flip:</label>
      <input type="checkbox" id="vflip" name="vflip" value="1">
    </div>
    <div class="form-group">
      <label for="hmirror">Horizontal Mirror:</label>
      <input type="checkbox" id="hmirror" name="hmirror" value="1">
    </div>
    <div class="form-group">
      <label for="brightness">Brightness (-2 to 2):</label>
      <input type="number" id="brightness" name="brightness" min="-2" max="2" value="0">
    </div>
    <div class="form-group">
      <label for="contrast">Contrast (-2 to 2):</label>
      <input type="number" id="contrast" name="contrast" min="-2" max="2" value="0">
    </div>
    <div class="form-group">
      <label for="saturation">Saturation (-2 to 2):</label>
      <input type="number" id="saturation" name="saturation" min="-2" max="2" value="0">
    </div>
    <div class="form-group">
      <label for="framesize">Frame Size:</label>
      <select id="framesize" name="framesize">
        <option value="0">96x96</option>
        <option value="4">640x480</option>
        <option value="5">800x600</option>
        <option value="6">1024x768</option>
        <option value="7">1280x1024</option>
        <option value="8">1600x1200</option>
      </select>
    </div>
    <div class="form-group">
      <label for="quality">Quality (0-63):</label>
      <input type="number" id="quality" name="quality" min="0" max="63" value="10">
    </div>
    <button type="submit">Save Settings</button>
  </form>
  <p><a href="/">Back to Main Page</a></p>
</body>
</html>
)rawliteral";