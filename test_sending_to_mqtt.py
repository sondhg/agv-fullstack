import paho.mqtt.client as mqtt_client
import signal
import sys
import os

# MQTT Configuration
# Use localhost for both development and inside Docker container
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_KEEPALIVE = 60
CLIENT_ID = "test_client"

# Message format constants
FRAME_START = 0x7A
FRAME_LENGTH = 0x08
MESSAGE_TYPE = 0x02  # Type for AGV to server messages
FRAME_END = 0x7F


def validate_input(value: str, min_val: int, max_val: int, name: str) -> int:
    """
    Validate numeric input within a range.

    Args:
        value (str): Input string to validate
        min_val (int): Minimum allowed value
        max_val (int): Maximum allowed value
        name (str): Name of the input for error messages

    Returns:
        int: Validated integer value

    Raises:
        ValueError: If input is invalid
    """
    try:
        num = int(value)
        if min_val <= num <= max_val:
            return num
        raise ValueError(f"{name} must be between {min_val} and {max_val}")
    except ValueError as e:
        if "must be between" in str(e):
            raise e
        raise ValueError(f"{name} must be a valid integer")


def encode_agv_position(agv_id: int, current_node: int) -> bytes:
    """
    Encode AGV position update into byte array format.

    Args:
        agv_id (int): AGV identifier
        current_node (int): Current node ID where AGV is located

    Returns:
        bytes: Encoded message
    """
    try:
        # Convert values to bytes (little-endian)
        agv_id_bytes = agv_id.to_bytes(2, byteorder='little')
        node_bytes = current_node.to_bytes(2, byteorder='little')

        # Create frame
        frame = bytearray()
        frame.append(FRAME_START)
        frame.append(FRAME_LENGTH)
        frame.append(MESSAGE_TYPE)
        frame.extend(agv_id_bytes)
        frame.extend(node_bytes)
        frame.append(FRAME_END)

        return bytes(frame)

    except Exception as e:
        raise ValueError(f"Failed to encode message: {str(e)}")


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback when client connects to broker"""
    if rc == 0:
        print("Connected to MQTT broker successfully")
        # Subscribe to all AGV route topics using wildcard
        client.subscribe("agvroute/#")
        print("Subscribed to topic: agvroute/#")
    else:
        print(f"Failed to connect: {rc}")


def on_message(client, userdata, msg):
    """Handle incoming MQTT messages from server"""
    print("\nReceived message from server:")
    print(f"Topic: {msg.topic}")
    print(f"Raw message (hex): {msg.payload.hex()}")
    print("Raw message content:")
    data = msg.payload
    print(f"Frame start: 0x{data[0]:02x}")
    print(f"Frame length: 0x{data[1]:02x}")
    print(f"Message type: 0x{data[2]:02x}")
    print(f"Motion state: {data[3]}")
    print(f"Next node: {int.from_bytes(data[4:6], byteorder='little')}")
    print(f"Direction change: {data[6]}")
    print(f"Frame end: 0x{data[7]:02x}\n")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\nExiting program...')
    if 'client' in globals() and client.is_connected():
        client.loop_stop()
        client.disconnect()
    sys.exit(0)


def main():
    global client

    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    # Initialize MQTT client
    client = mqtt_client.Client(
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID
    )    # Set up callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker
    try:
        print(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return

    # Start client loop in background
    client.loop_start()
    print("\nPress Ctrl+C to exit the program")

    while True:
        try:
            # Get AGV ID
            while True:
                try:
                    agv_id_input = input("\nEnter AGV ID (1-999): ")
                    agv_id = validate_input(agv_id_input, 1, 999, "AGV ID")
                    break
                except ValueError as e:
                    print(f"Error: {e}")

            # Get current node
            while True:
                try:
                    current_node_input = input("Enter current node (1-999): ")
                    current_node = validate_input(
                        current_node_input, 1, 999, "Current node")
                    break
                except ValueError as e:
                    print(f"Error: {e}")

            # Encode message
            print("\nPreparing to send AGV position update:")
            print(f"Raw data - AGV ID: {agv_id}, Current Node: {current_node}")

            message = encode_agv_position(agv_id, current_node)
            print(f"Encoded message (hex): {message.hex()}")

            # Publish to AGV data topic
            topic = f"agvdata/{agv_id}"
            client.publish(topic, message)
            print(f"\nPublished position update to {topic}")
            print("Waiting for server response...")

        except Exception as e:
            print(f"\nError: {e}")
            continue


if __name__ == "__main__":
    main()
