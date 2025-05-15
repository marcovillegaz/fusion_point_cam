

Hardware shoul ititlizae first:
-CameraManager
-TemperatureSensor
-SDHandler

Then the server is initalized
-WebServerManager

WebServerManager uget pointer of the hardware instance. 

# TemperatureSensor 
This class handle all the action related to the temperature measurment and calculations. 

A data point is pass to SDCardManager which write log the data into a file. 


# Settings
WebServerManager modify the cammera_settings.json, then CameraManager can apply the new ssetting via save setting.


*See want to do with wifi_setup*