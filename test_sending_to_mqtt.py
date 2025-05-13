import paho.mqtt.client as mqtt_client

# MQTT Configuration
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
CLIENT_ID = "test_client"

# Message format constants
FRAME_START = 0x7A
FRAME_LENGTH = 0x08
MESSAGE_TYPE = 0x02  # Type for AGV to server messages
FRAME_END = 0x7F

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
      # Print raw message only since we don't have direct access to decoder
    print("Raw message content:")
    data = msg.payload
    print(f"Frame start: 0x{data[0]:02x}")
    print(f"Frame length: 0x{data[1]:02x}")
    print(f"Message type: 0x{data[2]:02x}")
    print(f"Motion state: {data[3]}")
    print(f"Next node: {int.from_bytes(data[4:6], byteorder='little')}")
    print(f"Direction change: {data[6]}")
    print(f"Frame end: 0x{data[7]:02x}")

def main():
    # Initialize MQTT client
    client = mqtt_client.Client(
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID
    )
    
    # Set up callbacks
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return

    # Start client loop in background
    client.loop_start()

    # Prepare AGV position update
    agv_id = 2
    current_node = 17

    try:
        # Encode message
        print("\nPreparing to send AGV position update:")
        print(f"Raw data - AGV ID: {agv_id}, Current Node: {current_node}")
        
        message = encode_agv_position(agv_id, current_node)
        print(f"Encoded message (hex): {message.hex()}")

        # Publish to AGV data topic
        topic = f"agvdata/{agv_id}"
        client.publish(topic, message)
        print(f"Published position update to {topic}")

        # Keep script running to receive response
        input("\nPress Enter to exit...\n")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()