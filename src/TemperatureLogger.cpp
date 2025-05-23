#include "TemperatureLogger.h"

// Constructor
TemperatureLogger::TemperatureLogger()
{
    logBuffer = "";
}
// Add a temperature reading to the log
void TemperatureLogger::addReading(float temperature, int readCount)
{
    logBuffer += String(readCount) + "," + String(millis()) + "," + String(temperature, 2) + "\n";
}
// Get the log as a string
String TemperatureLogger::getLog()
{
    return logBuffer;
}
// Clear the log
void TemperatureLogger::clear()
{
    logBuffer = "";
}
