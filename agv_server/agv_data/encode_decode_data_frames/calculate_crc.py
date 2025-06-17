def calculate_crc(data: bytearray) -> int:
    """
    Calculate CRC-8 checksum for the given data.
    Uses polynomial 0x07 (x^8 + x^2 + x + 1) for error detection.

    Args:
        data (bytearray): Data bytes to calculate CRC for

    Returns:
        int: CRC-8 checksum value (0-255)
    """
    # CRC-8 polynomial: 0x07 (x^8 + x^2 + x + 1)
    polynomial = 0x07
    crc = 0x00  # Initial CRC value

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
