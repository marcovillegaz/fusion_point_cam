# Classes
## TemperatureSensor 
This class handle all the action related to the temperature measurment and calculations. 

A data point is pass to SDCardManager which write log the data into a file. 

Temperature Logger

CameraManager

SDHandler

WebServerManger (future)

# Utils
**wifi_setup.h**
This code connects the ESP32 to a WiFi network and configures the local IP address if provided.






WebServerManager uget pointer of the hardware instance. 



# Settings (*modify in foture*)
If in main page you psuh the setting button you will be redirecto to /setting route. In this page you are able to change some setting of the camera and save it. If you push the save button, the method saveCameraSetting() is applied. 

WebServerManager modify the cammera_settings.json, then CameraManager can apply the new ssetting via save setting.

# wifi_setup.h and .cpp
wifi_setup is a utility file that contains a unique function to that contains the necessary configarution to connect to wifi one time. 



*See what to do with wifi_setup*

Vairos componentes in the ESP32-CAM use the GPIO4 pin. The most important is the temeprature sensor, which use onewire comunication trough this pin. 

To avoid conflict in temeprature reading we use the next approuch: 

Temperature sensor has priorty. When a certain condition is meet, for example steady state or a interval that do not conflict with reading interval, the camera and SD manager are initizalized to take a picture a save it into the SD. At the same time, the buffer of the temperature read at this moment, is append to a txt file wich contain the read temeprature. 