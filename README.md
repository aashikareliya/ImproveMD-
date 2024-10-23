# ImproveMD
Publish the characteristics of IMproveMD Device on MQTT Server.
  e.g Heart Rate , SPO2 , ECG ,PPG ,IR.
  
  1. Parse the incoming raw data of IMproveMD Device in HEX Format from its specific UUID and MAC Address.
  2. Publish the parsed data from I.MX93 (MQTT Broker) on MQTT Server with port 1883 and subscribe it on your application(client side).
