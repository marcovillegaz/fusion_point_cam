#pragma once

const char *MAIN_page = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM</title>
    <script>
        let refreshRate = 500;

        function refreshImage() {
            const cam = document.getElementById("cam");
            cam.src = "/jpg?" + new Date().getTime();
        }

        function setRefreshRate() {
            refreshRate = parseInt(document.getElementById("interval").value);
        }

        function startAutoRefresh() {
            setInterval(() => {
                refreshImage();
            }, refreshRate);
        }

        function toggleLED(state) {
            fetch(`/led?state=${state}`);
        }

        window.onload = () => {
            startAutoRefresh();
        };
    </script>
</head>
<body>
    <h1>ESP32-CAM</h1>
    <img id="cam" src="/jpg" width="100%"><br>
    <button onclick="toggleLED('on')">LED ON</button>
    <button onclick="toggleLED('off')">LED OFF</button><br>
    Refresh Interval (ms): <input type="number" id="interval" value="500" onchange="setRefreshRate()">
</body>
</html>
)rawliteral";

const char *TEST_page = R"rawliteral(
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
