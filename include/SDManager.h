#ifndef SD_MANAGER_H
#define SD_MANAGER_H

#include <Arduino.h>

class SDManager
{
public:
    bool init();
    void deinit();

    bool saveLog(const String &logText, const String &filename = "/temps.txt");
    bool saveImage(const uint8_t *data, size_t length, const String &filename);
};

#endif
