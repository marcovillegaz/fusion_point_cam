#pragma once
#include <OneWire.h>
#include <DallasTemperature.h>

class TemperatureSensor
{
public:
    TemperatureSensor(uint8_t pin); // constructor
    void begin();
    float readTemperature();
    bool isThresholdReached(float threshold);

private:
    uint8_t sensorPin;
    OneWire oneWire;
    DallasTemperature sensors;
};