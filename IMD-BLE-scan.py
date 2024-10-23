import asyncio
from bleak import BleakClient, BleakScanner

# The UUID for the characteristic to receive notifications
NOTIFICATION_UUID = "85fc567e-31d9-4185-87c6-339924d1c5be"

def notification_handler(sender, data):
    """Notification handler that prints the received data in hex format."""
    hex_str = '-'.join([f'{byte:02X}' for byte in data])  # Convert each byte to a 2-character hex
    formatted_output = f"(0x) {hex_str}"
    print(f"Notification received from {sender}: {formatted_output}")

# Callback function to handle notifications
#def notification_handler(sender, data):
#Simple notification handler that prints the received data."""
#    print(f"Notification received from {sender}: {data}")

async def connect_to_device(mac_address):
    print(f"Scanning for device with MAC address: {mac_address}...")
    # Scan to find the device by address
    device = await BleakScanner.find_device_by_address(mac_address, timeout=10.0)

    if not device:
        print(f"Device with MAC address {mac_address} not found. Ensure it is powered on and in range.")
        return

    print(f"Attempting to connect to {mac_address}...")
    try:
        async with BleakClient(device) as client:
            if client.is_connected:  # Ensure the client is connected
                print(f"Connected to {mac_address} successfully!")
                
                # Print available services and characteristics
                services = await client.get_services()
                print("Available services and characteristics:")
                for service in services:
                    print(f"[Service] {service.uuid}")
                    for characteristic in service.characteristics:
                        print(f"  [Characteristic] {characteristic.uuid} - Properties: {characteristic.properties}")
                
                # Start notification for the specific UUID
                await client.start_notify(NOTIFICATION_UUID, notification_handler)
                
                print(f"Waiting for notifications from UUID {NOTIFICATION_UUID}...")
                await asyncio.sleep(30)  # Wait to receive notifications for 30 seconds
                
                # Stop notifications after waiting
                await client.stop_notify(NOTIFICATION_UUID)
            else:
                print(f"Failed to connect to {mac_address}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    mac_address = "00:18:80:04:52:85"  # Hardcoded MAC address
    asyncio.run(connect_to_device(mac_address))
