/**
 * @file wifi_setup.h
 * @brief WiFi network connection configuration for ESP32
 *
 * This module provides a simple interface for connecting the ESP32 to a WiFi network.
 * Supports both DHCP and static IP configuration for flexibility in different network
 * environments.
 *
 * Network Features:
 * - WPA/WPA2 authentication
 * - Optional static IP addressing
 * - Automatic retry mechanism
 * - Connection status feedback via Serial
 *
 * Scientific Application:
 * - Remote experiment monitoring via web interface
 * - Network access for camera control
 * - Potential for data upload/synchronization
 *
 * Security Considerations:
 * - WiFi credentials stored in secrets.h (not version controlled)
 * - Use WPA2 for secure connections
 * - Consider isolated network for sensitive experiments
 *
 * @note WiFi functionality currently disabled in production firmware
 * @note Enable for initial setup and remote monitoring needs
 */

#ifndef WIFI_SETUP_H
#define WIFI_SETUP_H

#include <WiFi.h>

/**
 * @brief Connect ESP32 to WiFi network with optional static IP
 *
 * Establishes WiFi connection using provided credentials. Supports both
 * DHCP (automatic IP assignment) and static IP configuration.
 *
 * Connection Process:
 * 1. Configure static IP if provided (otherwise uses DHCP)
 * 2. Begin WiFi connection with credentials
 * 3. Retry up to 20 times (10 seconds) with 500ms intervals
 * 4. Report success or failure via Serial monitor
 *
 * Static IP Configuration:
 * - Requires local_IP parameter
 * - Gateway assumed to be 192.168.1.1
 * - Subnet mask assumed to be 255.255.255.0
 * - Adjust if your network uses different settings
 *
 * DHCP Configuration:
 * - Pass IPAddress(0,0,0,0) for local_IP parameter
 * - Router assigns IP automatically
 * - Check Serial monitor for assigned IP address
 *
 * Scientific Use Cases:
 * - Static IP: Easier for repeated connections, stable URLs
 * - DHCP: Simpler setup, portable between networks
 *
 * Example Usage:
 * ```cpp
 * // Static IP:
 * IPAddress staticIP(192, 168, 1, 100);
 * connectToWiFi("MyNetwork", "password123", staticIP);
 *
 * // DHCP:
 * connectToWiFi("MyNetwork", "password123");
 * ```
 *
 * @param ssid WiFi network name (SSID)
 * @param password WiFi network password (WPA/WPA2)
 * @param local_IP Optional static IP address (default: IPAddress(0,0,0,0) for DHCP)
 *
 * @note Function blocks for up to 10 seconds during connection attempt
 * @note Connection status printed to Serial at configured baud rate
 * @note Successful connection displays assigned/configured IP address
 *
 * @warning Credentials should be stored in secrets.h, not hardcoded
 * @warning secrets.h should be added to .gitignore to prevent credential exposure
 */
void connectToWiFi(const char *ssid, const char *password, IPAddress local_IP = IPAddress(0, 0, 0, 0));

#endif