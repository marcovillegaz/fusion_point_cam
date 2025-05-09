void setup()
{
    Serial.begin(115200);
    delay(2000); // Wait for Serial Monitor to open
    Serial.println("ESP32-CAM is running");
}

void loop()
{
    Serial.println("Looping...");
    delay(1000); // Delay to avoid flooding the Serial Monitor
}
