#pragma once
#include <Arduino.h> // Required for PROGMEM

// Declare the variables as 'extern const' (pointing to PROGMEM data)
extern const char MAIN_page[] PROGMEM;
extern const char TEST_page[] PROGMEM;
extern const char CAMERA_SETTINGS_page[] PROGMEM;