#include "SDManager.h"

SDManager::SDManager(uint8_t ledPin)
{
    LED_PIN = ledPin;
    pinMode(LED_PIN, OUTPUT);
}

// Constructor definition
bool SDManager::init()
{
    // Release any other resources using GPIO4 first
    pinMode(4, INPUT);
    delay(100);

    SD_MMC.begin("/sdcard", true); // Initialize SD card with default settings

    // Specify that LED pin
    /* pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW); */

    return true;
}

// Deinitialize the SD card
void SDManager::deinit()
{
    SD_MMC.end();
}

// Create (or overwrite) a new log file (Setup only)
bool SDManager::createLogFile(const String &filename)
{
    // For debugging
    Serial.printf("Creating log file: %s\n", filename);

    // Initialize SD card
    if (!init())
        return false;

    // Open the file in write mode to overwrite or create it
    File file = SD_MMC.open(filename, FILE_WRITE);
    if (!file) // if file opening failed then deinialize SD
    {
        Serial.println("Failed to open file for writing");
        deinit();
        return false;
    }

    // Optionally write a header line
    file.println("n, time (ms), temperature (°C)");
    file.close(); // Close file

    deinit(); // Deinitialize SD card

    return true;
}

// Save temperature log into SD.
bool SDManager::saveLog(const String &logText, const String &filename)
{
    Serial.println("[SD Manager] Saving log to: " + filename);

    // Check if the SD card is initialized
    if (!init())
        return false;

    // Open the file in append mode
    File file = SD_MMC.open(filename, FILE_APPEND);
    // Check if the file was opened successfully
    if (!file)
    {
        deinit();
        return false;
    }

    file.print(logText); // Write the log text to the file
    file.close();        // Close the file
    deinit();            // Deinitialize the SD card

    return true;
}

// Save image into SD.
bool SDManager::saveImage(const uint8_t *data, size_t length, const String &filename)
{
    // Check if the SD card is initialized
    if (!init())
        return false;
    // Open the file in write mode
    File file = SD_MMC.open(filename, FILE_WRITE);
    // Check if the file was opened successfully
    if (!file)
    {
        deinit();
        return false;
    }

    file.write(data, length); // Write the image data to the file
    file.close();             // Close the file
    deinit();                 // Deinitialize the SD card

    Serial.println("[SD Manager] Image saved to: " + filename); // For debugging

    return true;
}

// List files and directories on the SD card (for debugging)
void SDManager::listFiles()
{
    if (!init())
    {
        Serial.println("SD init failed. Cannot list files.");
        return;
    }

    File root = SD_MMC.open("/");
    if (!root)
    {
        Serial.println("Failed to open root directory");
        deinit();
        return;
    }

    if (!root.isDirectory())
    {
        Serial.println("Root is not a directory");
        root.close();
        deinit();
        return;
    }

    File file = root.openNextFile();
    while (file)
    {
        if (file.isDirectory())
        {
            Serial.print("\tDIR : ");
            Serial.println(file.name());
        }
        else
        {
            Serial.print("\tFILE: ");
            Serial.print(file.name());
            Serial.print("  SIZE: ");
            Serial.println(file.size());
        }
        file = root.openNextFile();
    }

    root.close();
    deinit(); // Deinitialize the SD card
}