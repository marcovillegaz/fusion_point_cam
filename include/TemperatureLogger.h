#ifndef TEMPERATURE_LOGGER_H
#define TEMPERATURE_LOGGER_H

#include <Arduino.h>

class TemperatureLogger
{
private:
    String logBuffer;

public:
    TemperatureLogger();

    void addReading(float temperature, int readCount);
    String getLog();
    void clear();
};

#endif
