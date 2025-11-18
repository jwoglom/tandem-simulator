"""Cryptographic utilities for Tandem pump protocol.

This module provides HMAC-SHA1 calculation and other cryptographic
operations for signed messages.

Signed Message Format (24 bytes authentication block):
- Timestamp: 4 bytes (little-endian, pump time since reset in seconds)
- HMAC-SHA1: 20 bytes

Milestone 2 deliverable.
"""

import hashlib
import hmac
import struct
import time
from typing import Optional

# Signed message authentication block size
HMAC_SHA1_SIZE = 20  # bytes
TIMESTAMP_SIZE = 4  # bytes
AUTH_BLOCK_SIZE = TIMESTAMP_SIZE + HMAC_SHA1_SIZE  # 24 bytes


def calculate_hmac_sha1(key: bytes, message: bytes) -> bytes:
    """Calculate HMAC-SHA1 for a message.

    Args:
        key: HMAC key (session key from authentication)
        message: Message to sign

    Returns:
        HMAC-SHA1 signature (20 bytes)
    """
    return hmac.new(key, message, hashlib.sha1).digest()


def validate_hmac(key: bytes, message: bytes, signature: bytes) -> bool:
    """Validate HMAC-SHA1 signature.

    Args:
        key: HMAC key
        message: Message that was signed
        signature: HMAC signature to validate (20 bytes)

    Returns:
        True if signature is valid, False otherwise
    """
    if len(signature) != HMAC_SHA1_SIZE:
        return False

    calculated_hmac = calculate_hmac_sha1(key, message)
    return hmac.compare_digest(calculated_hmac, signature)


def create_signed_message_auth(key: bytes, message: bytes, timestamp: Optional[int] = None) -> bytes:
    """Create authentication block for a signed message.

    Args:
        key: HMAC key (session key)
        message: Message to sign
        timestamp: Pump time since reset in seconds (if None, uses current time)

    Returns:
        24-byte authentication block (4-byte timestamp + 20-byte HMAC)
    """
    # Use provided timestamp or current time
    if timestamp is None:
        timestamp = int(time.time())

    # Pack timestamp (little-endian 4 bytes)
    timestamp_bytes = struct.pack("<I", timestamp & 0xFFFFFFFF)

    # Calculate HMAC over message + timestamp
    data_to_sign = message + timestamp_bytes
    hmac_signature = calculate_hmac_sha1(key, data_to_sign)

    # Return authentication block: timestamp + HMAC
    return timestamp_bytes + hmac_signature


def validate_signed_message(
    key: bytes, message: bytes, auth_block: bytes, max_time_diff: Optional[int] = None
) -> tuple[bool, int]:
    """Validate a signed message.

    Args:
        key: HMAC key
        message: Message that was signed
        auth_block: 24-byte authentication block (timestamp + HMAC)
        max_time_diff: Maximum allowed time difference in seconds (None = no check)

    Returns:
        Tuple of (is_valid, timestamp)
    """
    if len(auth_block) != AUTH_BLOCK_SIZE:
        return False, 0

    # Extract timestamp and HMAC
    timestamp_bytes = auth_block[:TIMESTAMP_SIZE]
    received_hmac = auth_block[TIMESTAMP_SIZE:]

    # Unpack timestamp
    timestamp = struct.unpack("<I", timestamp_bytes)[0]

    # Validate HMAC
    data_to_verify = message + timestamp_bytes
    is_valid = validate_hmac(key, data_to_verify, received_hmac)

    if not is_valid:
        return False, timestamp

    # Check timestamp if requested
    if max_time_diff is not None:
        current_time = int(time.time())
        time_diff = abs(current_time - timestamp)
        if time_diff > max_time_diff:
            return False, timestamp

    return True, timestamp


def extract_auth_block(signed_message: bytes) -> tuple[bytes, bytes]:
    """Extract message and authentication block from signed message.

    Args:
        signed_message: Complete signed message (message + 24-byte auth block)

    Returns:
        Tuple of (message, auth_block)

    Raises:
        ValueError: If message is too short for auth block
    """
    if len(signed_message) < AUTH_BLOCK_SIZE:
        raise ValueError(f"Message too short for auth block: {len(signed_message)} < {AUTH_BLOCK_SIZE}")

    message = signed_message[:-AUTH_BLOCK_SIZE]
    auth_block = signed_message[-AUTH_BLOCK_SIZE:]

    return message, auth_block
