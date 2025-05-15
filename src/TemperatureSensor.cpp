#include "TemperatureSensor.h"

// TemperatureSensor class implementation
TemperatureSensor::TemperatureSensor(uint8_t pin)
    : sensorPin(pin), oneWire(pin), sensors(&oneWire), bufferIndex(0), bufferFilled(false)
{
    // Initialize buffer to zero
    for (int i = 0; i < BUFFER_SIZE; ++i)
        tempBuffer[i] = 0.0;
}

// Initialize the temperature sensor
bool TemperatureSensor::init()
{
    if (sensors.getDeviceCount() == 0)
    {
        Serial.println("No DS18B20 sensor found!");
    }

    pinMode(sensorPin, INPUT);           // <-- Explicitly set pin as INPUT
    sensors.setWaitForConversion(false); // non-blocking read
    sensors.begin();
    sensors.setResolution(12);

    Serial.println("Initializing temperature sensor...");
}

// Read temperature from the sensor
float TemperatureSensor::readTemperature()
{
    // Disable the flash LED (GPIO4)
    digitalWrite(sensorPin, LOW); // Turn off flash LED

    // Request temperature read
    sensors.requestTemperatures();
    delay(100); // wait ~100ms for 9-bit resolution

    // Read temperature
    float temp = sensors.getTempCByIndex(0);

    // Update buffer
    tempBuffer[bufferIndex] = temp;
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    if (bufferIndex == 0)
        bufferFilled = true;

    return temp;
}

// Check if steady state is reached using variance
bool TemperatureSensor::isSteadyState()
{
    if (!bufferFilled)
        return false;

    float sum = 0.0;
    float sumSq = 0.0;

    for (int i = 0; i < BUFFER_SIZE; ++i)
    {
        sum += tempBuffer[i];
        sumSq += tempBuffer[i] * tempBuffer[i];
    }

    float mean = sum / BUFFER_SIZE;
    float variance = (sumSq / BUFFER_SIZE) - (mean * mean);

    if (variance < VARIANCE_THRESHOLD)
    {
        // Serial.println("Steady state reached (low variance).");
        return true;
    }
    else
    {
        return false;
    }
}

// This is reapted above
float TemperatureSensor::getVariance()
{
    if (!bufferFilled)
        return -1.0; // Not enough data

    float sum = 0.0;
    float sumSq = 0.0;

    for (int i = 0; i < BUFFER_SIZE; ++i)
    {
        sum += tempBuffer[i];
        sumSq += tempBuffer[i] * tempBuffer[i];
    }

    float mean = sum / BUFFER_SIZE;
    float variance = (sumSq / BUFFER_SIZE) - (mean * mean);

    return variance;
}