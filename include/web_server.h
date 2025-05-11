#pragma once
#include <WebServer.h>

extern WebServer server; // WebServer instance

void setupWebServer();
void handleWebRequests();
void handleMainPage();
void handleImageCapture();
void handleSettingsPage();
void handleCameraSettingUpdate();
void startCameraServer();
