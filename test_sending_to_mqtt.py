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
FRAME_LENGTH = 0x09  # Total frame length: 9 bytes
MESSAGE_TYPE = 0x02  # Type for AGV to server messages
FRAME_END = 0x7F


def calculate_crc(data: bytearray) -> int:
    """
    Calculate CRC-8 for the given data using polynomial 0x07 (x^8 + x^2 + x + 1).
    This function generates the CRC that will be appended to the data for transmission.

    Args:
        data (bytearray): Data bytes to calculate CRC for

    Returns:
        int: Calculated CRC value (0-255)
    """
    # CRC-8 polynomial: 0x07 (x^8 + x^2 + x + 1)
    polynomial = 0x07
    crc = 0x00  # Initial CRC value

    # Process each byte in the data
    for byte in data:
        # XOR the current byte with the CRC
        crc ^= byte

        # Process each bit
        for _ in range(8):
            if crc & 0x80:  # If MSB is set
                crc = (crc << 1) ^ polynomial
            else:
                crc = crc << 1
            # Keep only 8 bits
            crc &= 0xFF

    return crc


def get_motion_state_display(state_value: int) -> str:
    """
    Get human-readable display for motion state value.
    Based on AGV model choices.
    """
    motion_state_choices = {
        0: "Idle",
        1: "Moving",
        2: "Waiting"
    }
    return motion_state_choices.get(state_value, f"Unknown ({state_value})")


def get_direction_change_display(direction_value: int) -> str:
    """
    Get human-readable display for direction change value.
    Based on AGV model choices.
    """
    direction_change_choices = {
        0: "Go straight",
        1: "Turn around",
        2: "Turn left",
        3: "Turn right"
    }
    return direction_change_choices.get(direction_value, f"Unknown ({direction_value})")


def get_reserved_node_display(node_value: int) -> str:
    """
    Get human-readable display for reserved node value.
    """
    if node_value == 0:
        return "None (0)"
    else:
        return f"Node {node_value}"


# def test_crc_compatibility():
#     """
#     Test that our CRC generation is compatible with the decoder's verification.
#     This simulates the decoder's verify_crc function to ensure compatibility.
#     """
#     # Test with sample data
#     test_agv_id = 123
#     test_node = 45

#     # Generate a message using our encoding
#     message = encode_agv_position(test_agv_id, test_node)

#     # Extract the codeword (data + CRC, excluding frame markers)
#     # Frame structure: [START, LENGTH, TYPE, AGV_ID(2), NODE(2), CRC, END]
#     codeword = bytearray(message[1:8])  # [LENGTH, TYPE, AGV_ID(2), NODE(2), CRC]

#     # Simulate decoder's verify_crc function
#     polynomial = 0x07
#     crc = 0x00

#     for byte in codeword:
#         crc ^= byte
#         for _ in range(8):
#             if crc & 0x80:
#                 crc = (crc << 1) ^ polynomial
#             else:
#                 crc = crc << 1
#             crc &= 0xFF

#     # If CRC verification passes, result should be 0
#     verification_passed = (crc == 0)

#     print(f"CRC Compatibility Test:")
#     print(f"  Test AGV ID: {test_agv_id}")
#     print(f"  Test Node: {test_node}")
#     print(f"  Generated message: {message.hex()}")
#     print(f"  Codeword: {codeword.hex()}")
#     print(f"  Verification result: {crc}")
#     print(f"  Verification passed: {verification_passed}")

#     return verification_passed


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
    Encode AGV position update into byte array format with CRC.

    Args:
        agv_id (int): AGV identifier
        current_node (int): Current node ID where AGV is located

    Returns:
        bytes: Encoded message with CRC
    """
    try:
        # Convert values to bytes (little-endian)
        agv_id_bytes = agv_id.to_bytes(2, byteorder='little')
        node_bytes = current_node.to_bytes(2, byteorder='little')

        # Create data for CRC calculation (excluding frame start/end markers)
        data_for_crc = bytearray()
        data_for_crc.append(FRAME_LENGTH)
        data_for_crc.append(MESSAGE_TYPE)
        data_for_crc.extend(agv_id_bytes)
        data_for_crc.extend(node_bytes)

        # Calculate CRC for the data
        crc_value = calculate_crc(data_for_crc)
        crc_bytes = crc_value.to_bytes(1, byteorder='little')

        # Create complete frame
        frame = bytearray()
        frame.append(FRAME_START)
        # This includes frame length, message type, agv_id, and current_node
        frame.extend(data_for_crc)
        frame.extend(crc_bytes)
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
    print("\nServer instructions:")
    print(f"Topic: {msg.topic}")
    data = msg.payload
    raw_data = bytes(data)
    hex_data = raw_data.hex()
    print(f"Raw message (bytes): {raw_data}")
    print(f"Raw message (hex): {hex_data}")
    # Display data as binary
    # print("Raw message (binary):", ' '.join(format(byte, '08b') for byte in raw_data))
    if len(data) >= 8:  # Server messages are 8 bytes
        frame_start = raw_data[0]
        frame_length = raw_data[1]
        message_type = raw_data[2]
        motion_state = raw_data[3]
        reserved_node = int.from_bytes(raw_data[4:6], byteorder='little')
        direction_change = raw_data[6]
        crc = raw_data[7]
        frame_end = raw_data[8]

        print(f"Frame start: {hex(frame_start)}")
        print(f"Frame length: {hex(frame_length)}")
        print(f"Message type: {hex(message_type)}")
        print(
            f"Motion state: {motion_state} ({get_motion_state_display(motion_state)})")
        print(
            f"Reserved node: {reserved_node} ({get_reserved_node_display(reserved_node)})")
        print(
            f"Direction change: {direction_change} ({get_direction_change_display(direction_change)})")
        print(f"CRC: {hex(crc)}")
        print(f"Frame end: {hex(frame_end)}")
    else:
        print("Message too short to decode")
    print("")  # Add extra newline to ensure prompt appears immediately


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\nExiting program...')
    if 'client' in globals() and client.is_connected():
        client.loop_stop()
        client.disconnect()
    sys.exit(0)


def main():
    global client

    # # Test CRC compatibility first
    # print("Testing CRC compatibility with decoder...")
    # if test_crc_compatibility():
    #     print("✓ CRC compatibility test passed!\n")
    # else:
    #     print("✗ CRC compatibility test failed!\n")
    #     return

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
                    print(f"Error: {e}")            # Encode message
            print("\nPreparing to send AGV position update:")
            print(f"Raw data - AGV ID: {agv_id}, Current Node: {current_node}")

            message = encode_agv_position(agv_id, current_node)
            print(f"Encoded message (hex): {message.hex()}")

            # Show frame breakdown
            print("Frame breakdown:")
            print(f"  Frame start: {hex(message[0])}")
            print(f"  Frame length: {hex(message[1])}")
            print(f"  Message type: {hex(message[2])}")
            print(
                f"  AGV ID: {int.from_bytes(message[3:5], byteorder='little')}")
            print(
                f"  Current node: {int.from_bytes(message[5:7], byteorder='little')}")
            print(f"  CRC: {hex(message[7])}")
            print(f"  Frame end: {hex(message[8])}")

            # Publish to AGV data topic
            topic = f"agvdata/{agv_id}"
            client.publish(topic, message)
            print(f"\nPublished position update to {topic}")
            print(f"AGV {agv_id} arrived at node {current_node}")
            print("Waiting for server response...")

        except Exception as e:
            print(f"\nError: {e}")
            continue


if __name__ == "__main__":
    main()
