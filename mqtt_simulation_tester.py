import paho.mqtt.client as mqtt_client
import signal
import sys
import os
import json

# MQTT Configuration
# Use localhost for both development and inside Docker container
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_KEEPALIVE = 60
CLIENT_ID = "simulation_test_client"

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
        agv_id_bytes = agv_id.to_bytes(2, byteorder="little")
        node_bytes = current_node.to_bytes(2, byteorder="little")

        # Create data for CRC calculation (excluding frame start/end markers)
        data_for_crc = bytearray()
        data_for_crc.append(FRAME_LENGTH)
        data_for_crc.append(MESSAGE_TYPE)
        data_for_crc.extend(agv_id_bytes)
        data_for_crc.extend(node_bytes)

        # Calculate CRC for the data
        crc_value = calculate_crc(data_for_crc)
        crc_bytes = crc_value.to_bytes(1, byteorder="little")

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


def load_simulation_steps(file_path: str) -> list:
    """
    Load simulation steps from JSON or JSONC file.

    Args:
        file_path (str): Path to the JSON/JSONC file containing simulation steps

    Returns:
        list: List of simulation steps

    Raises:
        FileNotFoundError: If the JSON file is not found
        ValueError: If the JSON file is invalid
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove comments from JSONC format
        # This is a simple implementation that removes lines starting with //
        lines = content.split("\n")
        json_lines = []
        for line in lines:
            stripped_line = line.strip()
            # Skip lines that are comments or empty
            if not stripped_line.startswith("//") and stripped_line:
                json_lines.append(line)

        # Join the lines back and parse as JSON
        json_content = "\n".join(json_lines)
        steps = json.loads(json_content)

        if not isinstance(steps, list):
            raise ValueError("JSON file must contain an array of simulation steps")

        # Validate each step
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step {i + 1} must be an object")
            if "agv_id" not in step or "current_node" not in step:
                raise ValueError(
                    f"Step {i + 1} must contain 'agv_id' and 'current_node' fields"
                )
            if not isinstance(step["agv_id"], int) or not isinstance(
                step["current_node"], int
            ):
                raise ValueError(
                    f"Step {i + 1}: 'agv_id' and 'current_node' must be integers"
                )

        return steps
    except FileNotFoundError:
        raise FileNotFoundError(f"Simulation steps file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in file {file_path}: {str(e)}")


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
    data = msg.payload
    raw_data = bytes(data)
    hex_data = raw_data.hex()
    print(f"Raw message (bytes): {raw_data}")
    print(f"Raw message (hex): {hex_data}")
    # Display data as binary
    print("Raw message (binary):", " ".join(format(byte, "08b") for byte in raw_data))
    if len(data) >= 8:  # Server messages are 8 bytes
        print(f"Frame start: {hex(raw_data[0])}")
        print(f"Frame length: {hex(raw_data[1])}")
        print(f"Message type: {hex(raw_data[2])}")
        print(f"Motion state: {raw_data[3]}")
        print(f"Reserved node: {int.from_bytes(raw_data[4:6], byteorder='little')}")
        print(f"Direction change: {raw_data[6]}")
        print(f"CRC: {hex(raw_data[7])}")
        print(f"Frame end: {hex(raw_data[8])}")
    else:
        print("Message too short to decode")
    print("")  # Add extra newline to ensure prompt appears immediately


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting program...")
    if "client" in globals() and client.is_connected():
        client.loop_stop()
        client.disconnect()
    sys.exit(0)


def main():
    global client

    # Set up Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    # Load simulation steps
    simulation_file = os.path.join(
        os.path.dirname(__file__), "sample-data", "mqttSimulationSteps.jsonc"
    )
    print(f"Loading simulation steps from: {simulation_file}")

    try:
        simulation_steps = load_simulation_steps(simulation_file)
        print(f"Loaded {len(simulation_steps)} simulation steps")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading simulation steps: {e}")
        return

    # Initialize MQTT client
    client = mqtt_client.Client(
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
    )

    # Set up callbacks
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

    print("\n" + "=" * 60)
    print("MQTT SIMULATION TESTER")
    print("=" * 60)
    print("Press Enter to send the next simulation step")
    print("Press Ctrl+C to exit the program")
    print("=" * 60)

    # Display all simulation steps
    print("\nSimulation Steps:")
    for i, step in enumerate(simulation_steps, 1):
        print(f"  Step {i}: AGV {step['agv_id']} -> Node {step['current_node']}")
    print("")

    # Main simulation loop
    current_step = 0

    while current_step < len(simulation_steps):
        try:
            # Wait for user input
            input(
                f"Press Enter to send step {current_step + 1}/{len(simulation_steps)} (AGV {simulation_steps[current_step]['agv_id']} -> Node {simulation_steps[current_step]['current_node']})..."
            )

            # Get current simulation step
            step = simulation_steps[current_step]
            agv_id = step["agv_id"]
            current_node = step["current_node"]

            print(f"\nSending simulation step {current_step + 1}:")
            print(f"  AGV ID: {agv_id}")
            print(f"  Current Node: {current_node}")

            # Encode message
            message = encode_agv_position(agv_id, current_node)
            print(f"  Encoded message (hex): {message.hex()}")

            # Show frame breakdown
            print("  Frame breakdown:")
            print(f"    Frame start: {hex(message[0])}")
            print(f"    Frame length: {hex(message[1])}")
            print(f"    Message type: {hex(message[2])}")
            print(f"    AGV ID: {int.from_bytes(message[3:5], byteorder='little')}")
            print(
                f"    Current node: {int.from_bytes(message[5:7], byteorder='little')}"
            )
            print(f"    CRC: {hex(message[7])}")
            print(f"    Frame end: {hex(message[8])}")

            # Publish to AGV data topic
            topic = f"agvdata/{agv_id}"
            client.publish(topic, message)
            print(f"  Published to topic: {topic}")
            print("  Waiting for server response...")

            current_step += 1

        except KeyboardInterrupt:
            # Handle Ctrl+C during input
            signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"\nError in simulation step {current_step + 1}: {e}")
            current_step += 1
            continue

    print(f"\n{'=' * 60}")
    print("All simulation steps completed!")
    print("Press Ctrl+C to exit or continue listening for server responses...")

    # Keep the program running to listen for any remaining server responses
    try:
        while True:
            input("Press Enter to exit or Ctrl+C...")
            break
    except KeyboardInterrupt:
        pass
    finally:
        signal_handler(signal.SIGINT, None)


if __name__ == "__main__":
    main()
