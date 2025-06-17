"""
Decoder for messages received from AGVs via MQTT.
Converts byte array messages into JSON format for server processing.
"""


def validate_frame(data: bytearray) -> bool:
    """
    Validate the received data frame format.

    Args:
        data (bytearray): The received byte array data

    Returns:
        bool: True if frame is valid, False otherwise
    """
    # Check minimum length
    if len(data) != 8:  # Fixed length as per spec
        return False

    # Validate frame start and end markers
    if data[0] != 0x7A or data[-1] != 0x7F:
        return False

    # Validate frame length field
    if data[1] != 0x08:
        return False

    # Validate message type
    if data[2] != 0x02:
        return False

    return True


def decode_message(payload: bytes) -> dict:
    """
    Decode byte array message from AGV into JSON format.

    Args:
        payload (bytes): Raw byte array received from MQTT broker

    Returns:
        dict: Decoded message with agv_id and current_node

    Raises:
        ValueError: If message format is invalid
    """
    try:
        data = bytearray(payload)

        if not validate_frame(data):
            raise ValueError("Invalid frame format")

        # Extract payload data using little-endian byte order
        agv_id = int.from_bytes(data[3:5], byteorder='little')
        current_node = int.from_bytes(data[5:7], byteorder='little')

        return {
            "agv_id": agv_id,
            "current_node": current_node
        }

    except Exception as e:
        raise ValueError(f"Failed to decode message: {str(e)}")
