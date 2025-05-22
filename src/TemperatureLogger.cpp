#include "TemperatureLogger.h"

// Constructor
TemperatureLogger::TemperatureLogger() {
    logBuffer = "";
}
// Add a temperature reading to the log
void TemperatureLogger::addReading(float temperature) {
    logBuffer += "Time: " + String(millis()) + " ms, Temp: " + String(temperature, 2) + " C\n";
}
// Get the log as a string
String TemperatureLogger::getLog() {
    return logBuffer;
}
// Clear the log
void TemperatureLogger::clear() {
    logBuffer = "";
}
