import asyncio
from bleak import BleakClient, BleakScanner

# UUID for BLE notifications
NOTIFICATION_UUID = "85fc567e-31d9-4185-87c6-339924d1c5be"

def parse_int24(data):
    """Parses a 24-bit signed integer."""
    # Convert 3 bytes to an unsigned integer
    value = int.from_bytes(data, byteorder='little', signed=False)
    print(f"Raw ECG Bytes: {data.hex()}, Parsed Value: {value}")  # Debug print

    # Check if the sign bit (23rd bit) is set
    if value & 0x800000:
        value -= 0x1000000  # Convert to negative (two's complement)
    return value

def parse_data(data):
    """Parses the incoming Bluetooth packet according to the specification."""
    try:
        # Parse 24-bit ECG, RED, and IR values
        ecg = parse_int24(data[0:3])
        red = int.from_bytes(data[3:6], byteorder='little', signed=False)
        ir = int.from_bytes(data[6:9], byteorder='little', signed=False)

        # Parse HR and its signal quality
        hr_val = data[9]
        hr_quality = data[10]
        hr_combined = f"{hr_val} bpm ({hr_quality}%)"

        # Parse Respiratory Rate and its signal quality
        rr_val = int.from_bytes(data[11:13], byteorder='little', signed=False)
        rr_quality = data[13]
        rr_combined = f"{rr_val} ms ({rr_quality}%)"

        # Parse SpO2, signal quality, and reliability
        spo2_val = data[14]
        spo2_quality = data[15]
        spo2_reliable = data[16]
        spo2_status = "OK" if spo2_reliable else "WAIT"
        spo2_combined = f"{spo2_val} % ({spo2_quality}%) {spo2_status}"

        # Parse temperature from bytes 18-22 as a string
        temperature_str = "".join([chr(data[i]) for i in range(18, 23)])
        temperature = float(temperature_str)

        # Print the parsed data in the required format
        print(
            f"ECG: {ecg}, RED: {red}, IR: {ir}, "
            f"HR: {hr_combined}, RR: {rr_combined}, "
            f"SpO2: {spo2_combined}, Temperature: {temperature:.2f} °C"
        )

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
    # Run Bluetooth connection asynchronously
    mac_address = "00:18:80:04:52:85"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_to_device(mac_address))
