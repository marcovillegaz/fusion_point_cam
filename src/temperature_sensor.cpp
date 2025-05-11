#include "temperature_sensor.h"

// TemperatureSensor class implementation
TemperatureSensor::TemperatureSensor(uint8_t pin)
    : sensorPin(pin), oneWire(pin), sensors(&oneWire) {}

// Initialize the temperature sensor
void TemperatureSensor::begin()
{
    if (sensors.getDeviceCount() == 0)
    {
        Serial.println("No DS18B20 sensor found!");
    }

    pinMode(sensorPin, INPUT);           // <-- Explicitly set pin as INPUT
    sensors.setWaitForConversion(false); // non-blocking read
    sensors.begin();
    sensors.setResolution(12);
}

// Read temperature from the sensor
float TemperatureSensor::readTemperature()
{
    // Disable the flash LED (GPIO4)
    digitalWrite(sensorPin, LOW); // Turn off flash LED

    // Request temperature read
    sensors.requestTemperatures();

    delay(100); // wait ~100ms for 9-bit resolution

    return sensors.getTempCByIndex(0);
}

// Check if the temperature exceeds the threshold
bool TemperatureSensor::isThresholdReached(float threshold)
{
    return readTemperature() >= threshold;
}