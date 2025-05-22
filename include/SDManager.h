#pragma once

#include <Arduino.h>
#include "SD_MMC.h"

class SDManager
{
public:
    SDManager(uint8_t LED_PIN); // Constructor

    bool init();
    void deinit();
    void listFiles();

    bool createLogFile(const String &filename);
    bool saveLog(const String &logText, const String &filename = "/temps.txt");
    bool saveImage(const uint8_t *data, size_t length, const String &filename);

private:
    uint8_t LED_PIN;
};
