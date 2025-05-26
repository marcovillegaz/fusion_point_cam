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
    pinMode(sensorPin, INPUT); // <-- Explicitly set pin as INPUT
    sensors.begin();

    if (sensors.getDeviceCount() == 0)
    {
        Serial.println("No DS18B20 sensor found!");
    }

    sensors.setWaitForConversion(false); // non-blocking read
    sensors.setResolution(12);

    Serial.println("Temperature sensor initialized.");

    return true;
}

// Deinitialize the temperature sensor
void TemperatureSensor::deinit()
{
    // Reset internal buffer state
    /* bufferIndex = 0;
    bufferFilled = false;
    for (int i = 0; i < BUFFER_SIZE; ++i)
        tempBuffer[i] = 0.0f; */

    // There is no direct deinit for DallasTemperature
    // But to "release" the pin and free it for other uses:
    pinMode(sensorPin, INPUT); // Set pin as input to release control
    Serial.println("TemperatureSensor deinitialized and pin released.");
}

// Read temperature from the sensor
float TemperatureSensor::readTemperature()
{
    // ADD INIT HERE
    // Disable the flash LED (GPIO4)
    // digitalWrite(sensorPin, LOW); // Turn off flash LED

    // Request temperature read
    sensors.requestTemperatures();
    delay(100); // wait ~100ms for 9-bit resolution

    // Read temperature
    float temp = sensors.getTempCByIndex(0);

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

    auto [mean, variance] = getMeanAndVariance();     // FIX THIS IN FUTURE

    // Here we can add more complex logic to determine if the system is in a steady state
    return variance < VARIANCE_THRESHOLD;
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

// Update the buffer with the latest temperature reading
/* void TemperatureSensor::updateBuffer(float temp)
{
    tempBuffer[bufferIndex] = temp;
    bufferIndex = (bufferIndex + 1) % BUFFER_SIZE;
    if (bufferIndex == 0)
        bufferFilled = true;
}
 */

// Privates:
// Get the slope of the lienar regression done to the buffer points.
float TemperatureSensor::getSlope()
{
    if (!bufferFilled)
        return 0.0; // Not enough data

    float sumX = 0.0, sumY = 0.0;
    float sumXY = 0.0, sumXX = 0.0;

    for (int i = 0; i < BUFFER_SIZE; ++i)
    {
        sumX += i;
        sumY += tempBuffer[i];
        sumXY += i * tempBuffer[i];
        sumXX += i * i;
    }

    float n = BUFFER_SIZE;
    float numerator = (n * sumXY) - (sumX * sumY);
    float denominator = (n * sumXX) - (sumX * sumX);

    if (denominator == 0.0)
        return 0.0; // Prevent division by zero

    return numerator / denominator; // slope m
}

// Determine the max and min temperature in the buffer
std::pair<float, float> TemperatureSensor::getMinMax()
{
    if (!bufferFilled)
        return {999.0, -999.0};

    float minVal = tempBuffer[0];
    float maxVal = tempBuffer[0];

    for (int i = 1; i < BUFFER_SIZE; ++i)
    {
        if (tempBuffer[i] < minVal)
            minVal = tempBuffer[i];
        if (tempBuffer[i] > maxVal)
            maxVal = tempBuffer[i];
    }

    return {minVal, maxVal};
}