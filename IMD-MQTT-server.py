import asyncio
from bleak import BleakClient, BleakScanner
from datetime import datetime
import paho.mqtt.client as mqtt
import socket

# MQTT Configuration
BROKER_ADDRESS = "192.168.6.104"  # Replace with your MQTT broker's IP
BROKER_PORT = 1883  # Default port
TOPIC = "sensor/data"

# UUID for BLE notifications
NOTIFICATION_UUID = "85fc567e-31d9-4185-87c6-339924d1c5be"

# Enforce IPv4 if required by your network setup
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311, transport="tcp")  # Use latest Paho API
mqtt_client.socket = socket.AF_INET

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect with return code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects."""
    print(f"Disconnected from broker with return code {rc}")

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect

# Try connecting to the MQTT broker
try:
    mqtt_client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    mqtt_client.loop_start()  # Start the loop in a non-blocking way
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")

def parse_int24(data):
    """Parses a 24-bit signed integer."""
    value = int.from_bytes(data, byteorder='little', signed=False)
    if value & 0x800000:
        value -= 0x1000000  # Convert to negative (two's complement)
    return value

def parse_data(data):
    """Parses the incoming Bluetooth packet and publishes it to MQTT."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        ecg = parse_int24(data[0:3])
        red = int.from_bytes(data[3:6], byteorder='little', signed=False)
        ir = int.from_bytes(data[6:9], byteorder='little', signed=False)

        hr_val = data[9]
        rr_val = int.from_bytes(data[11:13], byteorder='little', signed=False)
        spo2_val = data[14]
        temperature_str = "".join([chr(data[i]) for i in range(18, 23)])
        temperature = float(temperature_str)

        # Create payload for MQTT
        payload = {
            "timestamp": timestamp,
            "ecg": ecg,
            "red": red,
            "ir": ir,
            "hr": hr_val,
            "rr": rr_val,
            "spo2": spo2_val,
            "temperature": temperature
        }
        print(f"Publishing: {payload}")

        # Publish data to MQTT broker
        mqtt_client.publish(TOPIC, str(payload))

    except Exception as e:
        print(f"Error parsing data: {e}")

def notification_handler(sender, data):
    """Handles incoming notifications from the BLE device."""
    parse_data(data)

async def connect_to_device(mac_address, retries=3):
    """Attempts to connect to the BLE device and handle notifications."""
    for attempt in range(retries):
        try:
            print(f"Connecting to {mac_address} (Attempt {attempt + 1})...")
            device = await BleakScanner.find_device_by_address(mac_address, timeout=10.0)

            if not device:
                print(f"Device {mac_address} not found. Retrying...")
                continue

            async with BleakClient(device) as client:
                if client.is_connected:
                    print(f"Connected to {mac_address}!")
                    await client.start_notify(NOTIFICATION_UUID, notification_handler)
                    await asyncio.sleep(30)  # Receive data for 30 seconds
                    await client.stop_notify(NOTIFICATION_UUID)
                    return  # Exit after successful connection
        except Exception as e:
            print(f"Connection failed: {e}")

    print("Failed to connect after multiple attempts.")

if __name__ == "__main__":
    mac_address = "00:18:80:04:52:85"  # Replace with your BLE device's MAC address
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_device(mac_address))
