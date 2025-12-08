/**
 * @file TemperatureLogger.h
 * @brief In-memory temperature data logging system for CSV export
 *
 * This module provides a lightweight logging system that accumulates temperature readings
 * in RAM before batch-writing to SD card. This approach minimizes SD card access frequency,
 * extending card lifetime and reducing power consumption.
 *
 * Design Rationale:
 * - Buffered logging reduces SD card wear
 * - Allows periodic batch writes (e.g., every 4-10 readings)
 * - Maintains CSV format compatibility for data analysis
 * - Memory-efficient string concatenation
 *
 * Scientific Application:
 * - Creates timestamped temperature logs for DES experiments
 * - Correlates with image capture events
 * - Provides data for thermal analysis and phase transition studies
 * - Exports in standard CSV format for processing in scientific software
 *
 * Output Format:
 * The log generates CSV data with the following structure:
 *   n, time (ms), temperature (°C)
 *   1, 2000, 25.34
 *   2, 4000, 25.56
 *   ...
 *
 * Where:
 * - n: Sequential reading number
 * - time (ms): Milliseconds since ESP32 boot (via millis())
 * - temperature: DS18B20 reading in degrees Celsius
 */

#ifndef TEMPERATURE_LOGGER_H
#define TEMPERATURE_LOGGER_H

#include <Arduino.h>

/**
 * @class TemperatureLogger
 * @brief Manages in-memory accumulation of temperature readings for batch SD card writes
 *
 * This class maintains a string buffer containing CSV-formatted temperature data.
 * Readings are accumulated in RAM and periodically flushed to SD card storage,
 * reducing write operations and improving system reliability.
 *
 * Key Features:
 * - String-based buffer for flexible size management
 * - CSV format with timestamp and reading number
 * - Simple append-only operations
 * - Explicit clear() for buffer management
 *
 * Usage Pattern:
 * 1. Create TemperatureLogger instance
 * 2. Call addReading() after each temperature measurement
 * 3. Periodically call getLog() to retrieve buffered data
 * 4. Write returned string to SD card
 * 5. Call clear() to reset buffer for next batch
 *
 * Memory Considerations:
 * - Each reading adds ~25-30 bytes to buffer
 * - Typical batch size: 4-10 readings = 100-300 bytes
 * - Buffer automatically grows as needed (Arduino String)
 * - Clear buffer regularly to prevent excessive memory use
 */
class TemperatureLogger
{
private:
    /**
     * @brief Internal string buffer storing CSV-formatted log entries
     *
     * Accumulates temperature readings as newline-separated CSV rows.
     * Growth is managed automatically by Arduino String class.
     */
    String logBuffer;

public:
    /**
     * @brief Default constructor
     *
     * Initializes an empty log buffer ready for temperature readings.
     */
    TemperatureLogger();

    /**
     * @brief Add a temperature reading to the in-memory log
     *
     * Appends a CSV-formatted line to the buffer containing:
     * - Reading sequence number
     * - Current system timestamp in milliseconds
     * - Temperature value with 2 decimal places
     *
     * Format: "readCount,millis(),temperature\n"
     * Example: "5,10234,25.67\n"
     *
     * Scientific Application:
     * - Creates timestamped record for each measurement
     * - Maintains chronological order of readings
     * - Provides temporal resolution for rate calculations
     * - Enables correlation with image capture events
     *
     * @param temperature Temperature reading in degrees Celsius from DS18B20
     * @param readCount Sequential reading number (typically increments from 1)
     * @note Temperature is formatted to 2 decimal places (0.01°C resolution)
     * @note Timestamp uses millis() which overflows after ~49.7 days
     */
    void addReading(float temperature, int readCount);

    /**
     * @brief Retrieve accumulated log data for SD card writing
     *
     * Returns the complete buffer contents as a single string containing
     * all CSV-formatted temperature readings since last clear().
     *
     * Use Case:
     * - Called periodically (e.g., every 4-10 readings)
     * - String passed to SDManager for file writing
     * - Followed by clear() to reset buffer
     *
     * @return String containing CSV-formatted log entries with newlines
     * @note Does not modify buffer - call clear() separately to reset
     * @note Returns empty string if no readings have been added
     */
    String getLog();

    /**
     * @brief Clear the log buffer to prepare for next batch
     *
     * Resets the internal buffer to empty state, freeing memory and
     * preparing for the next set of temperature readings.
     *
     * @note Should be called after successfully writing log to SD card
     * @note Buffer memory is released, reducing RAM usage
     */
    void clear();
};

#endif
