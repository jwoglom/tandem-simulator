"""Cryptographic utilities for Tandem pump protocol.

This module provides HMAC-SHA1 calculation and other cryptographic
operations for signed messages.

Milestone 2 deliverable (stub).
"""

import hmac
import hashlib
from typing import Optional


def calculate_hmac_sha1(key: bytes, message: bytes) -> bytes:
    """Calculate HMAC-SHA1 for a message.

    Args:
        key: HMAC key
        message: Message to sign

    Returns:
        HMAC-SHA1 signature (20 bytes)
    """
    # TODO: Verify this matches Tandem's HMAC implementation
    return hmac.new(key, message, hashlib.sha1).digest()


def validate_hmac(key: bytes, message: bytes, signature: bytes) -> bool:
    """Validate HMAC-SHA1 signature.

    Args:
        key: HMAC key
        message: Message that was signed
        signature: HMAC signature to validate

    Returns:
        True if signature is valid, False otherwise
    """
    calculated_hmac = calculate_hmac_sha1(key, message)
    return hmac.compare_digest(calculated_hmac, signature)


def extract_signed_message(data: bytes) -> tuple[bytes, bytes, Optional[bytes]]:
    """Extract message, timestamp, and HMAC from signed message.

    Args:
        data: Complete signed message data

    Returns:
        Tuple of (message, timestamp, hmac)
    """
    # TODO: Implement signed message parsing
    # Format: message + 4-byte timestamp + 20-byte HMAC
    return data, b"", None
