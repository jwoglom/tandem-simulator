"""CRC16 calculation for Tandem pump protocol.

This module implements CRC16 checksum calculation and validation
for protocol messages.

The Tandem protocol uses CRC16-CCITT with polynomial 0x1021.

Milestone 2 deliverable.
"""

# CRC16-CCITT polynomial
CRC16_POLY = 0x1021
CRC16_INIT = 0xFFFF


def calculate_crc16(data: bytes, polynomial: int = CRC16_POLY, init_value: int = CRC16_INIT) -> int:
    """Calculate CRC16 checksum for data using CRC16-CCITT.

    This implementation uses the CRC16-CCITT algorithm with polynomial 0x1021,
    which is commonly used in medical devices and BLE protocols.

    Args:
        data: Data to calculate checksum for
        polynomial: CRC polynomial (default: 0x1021 for CRC16-CCITT)
        init_value: Initial CRC value (default: 0xFFFF)

    Returns:
        CRC16 checksum value (16-bit unsigned integer)
    """
    crc = init_value

    for byte in data:
        crc ^= byte << 8  # XOR byte into high byte of CRC

        # Process all 8 bits
        for _ in range(8):
            if crc & 0x8000:  # If MSB is set
                crc = (crc << 1) ^ polynomial
            else:
                crc = crc << 1

            # Keep it 16-bit
            crc &= 0xFFFF

    return crc


def validate_crc16(data: bytes, expected_crc: int) -> bool:
    """Validate CRC16 checksum.

    Args:
        data: Data to validate
        expected_crc: Expected CRC value

    Returns:
        True if CRC is valid, False otherwise
    """
    calculated_crc = calculate_crc16(data)
    return calculated_crc == expected_crc


def append_crc16(data: bytes) -> bytes:
    """Append CRC16 checksum to data.

    The CRC is appended in little-endian byte order.

    Args:
        data: Data to append checksum to

    Returns:
        Data with CRC16 checksum appended
    """
    crc = calculate_crc16(data)
    # Append in little-endian format
    return data + crc.to_bytes(2, byteorder="little")


def verify_and_strip_crc16(data: bytes) -> tuple[bool, bytes]:
    """Verify CRC16 and strip it from data.

    Expects CRC to be in little-endian byte order at the end of data.

    Args:
        data: Data with CRC16 checksum appended

    Returns:
        Tuple of (is_valid, data_without_crc)
    """
    if len(data) < 2:
        return False, data

    # Extract CRC from last 2 bytes (little-endian)
    message_data = data[:-2]
    received_crc = int.from_bytes(data[-2:], byteorder="little")

    # Validate
    is_valid = validate_crc16(message_data, received_crc)

    return is_valid, message_data
