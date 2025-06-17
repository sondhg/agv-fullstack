from calculate_crc import calculate_crc

"""
Encoder for messages sent from server to AGVs via MQTT.
Converts JSON format instructions into byte array messages.
"""
# Frame constants
FRAME_START = 0x7A
# Include frame start, frame length, frame end, CRC, and all other fields
FRAME_LENGTH = 0x09
MESSAGE_TYPE = 0x03
FRAME_END = 0x7F


def encode_message(motion_state: int, next_node: int, direction_change: int) -> bytes:
    """
    Encode server message into byte array format.

    Args:
        motion_state (int): AGV motion state (0=IDLE, 1=MOVING, 2=WAITING)
        next_node (int or None): Next node ID for AGV to move to (None will be encoded as 0)
        direction_change (int): Direction change instruction
                              (0=GO_STRAIGHT, 1=TURN_AROUND, 
                               2=TURN_LEFT, 3=TURN_RIGHT)

    Returns:
        bytes: Encoded message as byte array

    Raises:
        ValueError: If input parameters are invalid
    """

    try:        # Convert values to bytes
        motion_state_bytes = motion_state.to_bytes(1, byteorder='little')
        # Handle None values for next_node (use 0 as default)
        next_node_value = next_node if next_node is not None else 0
        next_node_bytes = next_node_value.to_bytes(2, byteorder='little')
        direction_change_bytes = direction_change.to_bytes(
            1, byteorder='little')

        # Prepare data for CRC calculation (without CRC field itself)
        data_for_crc = bytearray()
        data_for_crc.append(FRAME_LENGTH)
        data_for_crc.append(MESSAGE_TYPE)
        data_for_crc.extend(motion_state_bytes)
        data_for_crc.extend(next_node_bytes)
        data_for_crc.extend(direction_change_bytes)

        crc = calculate_crc(data_for_crc)
        crc_bytes = crc.to_bytes(1, byteorder='little')

        # Create frame
        frame = bytearray()
        frame.append(FRAME_START)

        frame.extend(data_for_crc)
        frame.extend(crc_bytes)

        frame.append(FRAME_END)

        return bytes(frame)

    except Exception as e:
        raise ValueError(f"Failed to encode message: {str(e)}")
