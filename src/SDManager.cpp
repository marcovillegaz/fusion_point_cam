#include "SDManager.h"
#include "SD_MMC.h"

// Constructor definition
bool SDManager::init()
{
    return SD_MMC.begin();
}
// Deinitialize the SD card
void SDManager::deinit()
{
    SD_MMC.end();
}
// Save temperature log into SD.
bool SDManager::saveLog(const String &logText, const String &filename)
{
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

    return true;
}
