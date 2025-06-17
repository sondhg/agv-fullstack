import random

"""
Decoder for messages received from AGVs via MQTT.
Converts byte array messages into JSON format for server processing.
"""


def verify_crc(codeword: bytearray) -> bool:
    """
    Verify CRC by performing CRC calculation on the entire codeword.
    According to CRC protocol, the receiver should calculate CRC on the entire
    received codeword (data + CRC). If the result is zero, the data is error-free.

    Args:
        codeword (bytearray): The complete received data including CRC

    Returns:
        bool: True if CRC verification passes (result is zero), False otherwise
    """
    # CRC-8 polynomial: 0x07 (x^8 + x^2 + x + 1) - same as used by sender
    polynomial = 0x07
    crc = 0x00  # Initial CRC value

    # Process the entire codeword (data + CRC)
    for byte in codeword:
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

    # If CRC calculation on the entire codeword results in 0, data is valid
    return crc == 0


def example_frame_from_agv_to_server() -> bytes:
    """
    Generate an example frame that would be sent from AGV to server.
    Note: This is for testing purposes only. In actual implementation,
    AGV would generate the CRC using its own calculate_crc function.
    """
    FRAME_START = 0x7A
    # Total frame length: FRAME_START(1) + FRAME_LENGTH(1) + MESSAGE_TYPE(1) + AGV_ID(2) + CURRENT_NODE(2) + CRC(1) + FRAME_END(1) = 9 bytes
    FRAME_LENGTH = 0x09
    MESSAGE_TYPE = 0x02  # Type for AGV to server messages
    FRAME_END = 0x7F

    agv_id = random.randint(1, 999)
    current_node = random.randint(1, 100)

    agv_id_bytes = agv_id.to_bytes(2, byteorder='little')
    current_node_bytes = current_node.to_bytes(2, byteorder='little')

    data_for_crc = bytearray()
    data_for_crc.append(FRAME_LENGTH)
    data_for_crc.append(MESSAGE_TYPE)
    data_for_crc.extend(agv_id_bytes)
    data_for_crc.extend(current_node_bytes)

    # Simulate CRC calculation as AGV would do it
    # CRC-8 polynomial: 0x07 (x^8 + x^2 + x + 1)
    polynomial = 0x07
    crc = 0x00  # Initial CRC value

    for byte in data_for_crc:
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

    crc_bytes = crc.to_bytes(1, byteorder='little')

    frame = bytearray()
    frame.append(FRAME_START)
    frame.extend(data_for_crc)
    frame.extend(crc_bytes)
    frame.append(FRAME_END)

    return bytes(frame)


def validate_frame(data: bytearray) -> bool:
    """
    Validate the received data frame format and verify CRC for data integrity.
    As the receiver, we perform modulo-2 binary division on the entire codeword
    to check if the remainder is zero, indicating error-free transmission.

    Args:
        data (bytearray): The received byte array data

    Returns:
        bool: True if frame is valid and CRC check passes, False otherwise
    """
    # Check frame length - should be 9 bytes total
    if len(data) != 9:
        return False

    # Validate frame start and end markers
    if data[0] != 0x7A or data[-1] != 0x7F:
        return False

    # Validate frame length field (should be 0x09 for total frame length)
    if data[1] != 0x09:
        return False

    # Validate message type
    if data[2] != 0x02:
        return False

    # Perform CRC verification using receiver-side method
    # Extract the codeword (data portion + CRC, excluding frame markers)
    # [FRAME_LENGTH, MESSAGE_TYPE, AGV_ID_2_BYTES, CURRENT_NODE_2_BYTES, CRC]
    codeword = data[1:8]

    # Verify CRC using modulo-2 binary division
    if not verify_crc(codeword):
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
            # Extract payload data using little-endian byte order
            raise ValueError("Invalid frame format")
        agv_id = int.from_bytes(data[3:5], byteorder='little')
        current_node = int.from_bytes(data[5:7], byteorder='little')

        return {
            "agv_id": agv_id,
            "current_node": current_node
        }

    except Exception as e:
        raise ValueError(f"Failed to decode message: {str(e)}")
