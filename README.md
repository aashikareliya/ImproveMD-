    IMD-BLE-MQTT PUBLISHING DATA 


 1. To run the python script over BLE and publish it to MQTT Server. 

    Make a python script assigning the UUID and MAC address that parses the incoming data from UUID and shows the parsed data. 
    NOTIFICATION-UUID: “85fc567e-31d9-4185-87c6-339924d1c5be" 
    MAC-ADDRESS: "00:18:80:04:52:85" 
    Here is the script.: IMD-Parsed-data.py 

 

2. Enable the Bluetooth on IMX93 Using below procedure: 
    to run script on imx93: 

    To insert WiFi/Bluetooth driver modules and download firmware, execute the below command. 
     root@imx93-iwg50m-osm: ~# modprobe moal mod_para=nxp/wifi_mod_para.conf 

     Now, to insert the Bluetooth module, execute the below command. 
     root@imx93-iwg50m-osm: ~# modprobe btnxpuart 

     To enable the Bluetooth interface, execute the below command  
     root@imx93-iwg50m-osm: ~# hciconfig hci0 up 

     To check the Bluetooth interface, execute the command below. 
     root@imx93-iwg50m-osm: ~# hcitool dev 
     Devices: 
     e.g hci0 41:41:41:41:41:41 

 

3.  Now Make this parsed data publish over MQTT SERVER by making the IMX93 as a MQTT Broker. 

    Make a python script to publish the parsed data to MQTT Server where the IMX93 is MQTT Broker 
    NOTIFICATION-UUID: “85fc567e-31d9-4185-87c6-339924d1c5be" 
    MAC-ADDRESS: "00:18:80:04:52:85" 
    BROKER_ADDRESS: 192.168.6.104 (Ip of broker) 
    PORT : 1883 
    Here is the script to publish over Server: IMD-MQTT-Publish.py 

4.  Now to publish the data, set up IMX93 as a Broker. 
    	 
    Install Libraries in yocto source for MQTT Server: 
    IMAGE_INSTALL:append = " mosquitto" 
    IMAGE_INSTALL:append = " gtk+3 gtk+3-dev mosquitto mosquitto-dev libmosquitto1 libmosquittopp1 mosquitto-clients libxml2 zlib" 

    Here is local.conf : local.conf 

    Bitbake the IMX-IMAGE-FULL and flash the SD Card. 

    Check the MQTT Support on IMX93 Terminal: mosquitto –h  

    Inside sudo nano /etc/mosquitto/mosquitto.conf file, add these lines: 

    listener 1883 0.0.0.0 

    allow_anonymous true 

    Restart the mosquitto service: systemctl restart mosquitto 

    To test MQTT and publish the data: 

5.  on a remote device (connected to the same network), use the following commands: 

    Subscribe to the topic: 
     mosquitto_sub -h <ip_address_of_imx93> -t test/topic 

    Publish a message from i.MX93: 
     mosquitto_pub -h localhost -t test/topic -m "Hello from i.MX93" 
     or 
     mosquitto_sub -h 192.168.6.104 -t sensor/data (To view published data) 

    Once the test is successful start the Bluetooth (described in STEP-2) and run the python script to publish data: python3 IMD-MQTT-Publish.py 

    Subscribe the publish data using your local PC: 
     mosquitto_sub -h 192.168.6.104 -t sensor/data 

 

 
