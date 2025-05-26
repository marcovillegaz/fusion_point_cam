#pragma once
#include <OneWire.h>
#include <DallasTemperature.h>

#define BUFFER_SIZE 10          // number of samples to consider
#define VARIANCE_THRESHOLD 0.01 // adjust this for your system's stability

class TemperatureSensor
{
public:
    TemperatureSensor(uint8_t pin); // constructor

    bool init();
    void deinit();

    float readTemperature();
    bool isSteadyState();
    float getVariance(); // Returns current variance
    // void updateBuffer(float temp); // abstract buffer update logic

private:
    uint8_t sensorPin;
    OneWire oneWire;
    DallasTemperature sensors;

    float tempBuffer[BUFFER_SIZE];
    int bufferIndex;
    bool bufferFilled;

    std::pair<float, float> getMeanAndVariance();

    float getSlope(); // get the slope via linear regression of the buffer points
    std::pair<float, float> getMinMax();
};