"""Byte utility functions for message encoding/decoding.

This module provides helper functions for reading and writing
binary data in little-endian format, used across all message types.
"""

import struct


def read_uint16_le(data: bytes, offset: int = 0) -> int:
    """Read a 16-bit unsigned integer in little-endian format.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from

    Returns:
        Unsigned 16-bit integer
    """
    value: int = struct.unpack_from("<H", data, offset)[0]
    return value


def read_uint32_le(data: bytes, offset: int = 0) -> int:
    """Read a 32-bit unsigned integer in little-endian format.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from

    Returns:
        Unsigned 32-bit integer
    """
    value: int = struct.unpack_from("<I", data, offset)[0]
    return value


def read_int16_le(data: bytes, offset: int = 0) -> int:
    """Read a 16-bit signed integer in little-endian format.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from

    Returns:
        Signed 16-bit integer
    """
    value: int = struct.unpack_from("<h", data, offset)[0]
    return value


def write_uint16_le(value: int) -> bytes:
    """Write a 16-bit unsigned integer in little-endian format.

    Args:
        value: Integer value to encode

    Returns:
        2 bytes in little-endian format
    """
    return struct.pack("<H", value)


def write_uint32_le(value: int) -> bytes:
    """Write a 32-bit unsigned integer in little-endian format.

    Args:
        value: Integer value to encode

    Returns:
        4 bytes in little-endian format
    """
    return struct.pack("<I", value)


def write_int16_le(value: int) -> bytes:
    """Write a 16-bit signed integer in little-endian format.

    Args:
        value: Integer value to encode

    Returns:
        2 bytes in little-endian format
    """
    return struct.pack("<h", value)


def read_string(data: bytes, offset: int, length: int) -> str:
    """Read a fixed-length null-padded string.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from
        length: Number of bytes to read

    Returns:
        Decoded UTF-8 string (null bytes stripped)
    """
    raw_bytes = data[offset : offset + length]
    # Strip null bytes and decode
    return raw_bytes.rstrip(b"\x00").decode("utf-8", errors="ignore")


def write_string(value: str, length: int) -> bytes:
    """Write a string as fixed-length null-padded bytes.

    Args:
        value: String to encode
        length: Fixed length of output (will be padded/truncated)

    Returns:
        Fixed-length bytes (UTF-8 encoded, null-padded)
    """
    encoded = value.encode("utf-8")[:length]  # Truncate if too long
    return encoded + b"\x00" * (length - len(encoded))  # Pad with nulls
