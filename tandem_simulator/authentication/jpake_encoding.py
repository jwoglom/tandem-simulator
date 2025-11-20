"""JPake message encoding utilities for Tandem pump protocol.

This module handles encoding/decoding of EC-JPAKE protocol messages to match
pumpx2's mbedTLS-based implementation. The wire format follows IETF
draft-cragie-tls-ecjpake.

IMPORTANT: This is a SIMULATOR implementation using placeholder cryptography.
For production use, integrate with a proper EC-JPAKE library (e.g., mbedTLS).

Message Format Reference:
    - Jpake1a/1b: 165 bytes (EC Point + ZKP)
    - Jpake2: 165/168 bytes (EC Point + ZKP)
    - Jpake3: 2 bytes (challenge) / 18 bytes (response)
    - Jpake4: 50 bytes (nonce + reserved + hash)

EC Point Format (SEC1 Uncompressed):
    - Byte 0: 0x04 (uncompressed indicator)
    - Bytes 1-32: X coordinate (big-endian)
    - Bytes 33-64: Y coordinate (big-endian)
    - Total: 65 bytes

Zero-Knowledge Proof (Schnorr):
    - Point V: 65 bytes (SEC1 uncompressed)
    - r_length: 1 byte (always 34 for P-256)
    - r scalar: 34 bytes (big-endian)
    - Total: 100 bytes

Complete ECJPAKEKeyKP Structure:
    - EC Point X: 65 bytes
    - ZKP Point V: 65 bytes
    - ZKP r_length: 1 byte
    - ZKP r scalar: 34 bytes
    - Total: 165 bytes
"""

import hashlib
import secrets
from typing import Tuple


def encode_ec_jpake_key_kp(point_data: bytes) -> bytes:
    """Encode an EC-JPAKE Key-Knowledge Proof structure.

    Args:
        point_data: Public key point bytes (65 bytes, SEC1 uncompressed format)

    Returns:
        165-byte ECJPAKEKeyKP structure (point + ZKP)

    Note:
        SIMULATOR ONLY: Generates random ZKP values. A production implementation
        must use proper Schnorr Zero-Knowledge Proofs.
    """
    if len(point_data) != 65:
        raise ValueError(f"EC point must be 65 bytes, got {len(point_data)}")

    if point_data[0] != 0x04:
        raise ValueError("EC point must be in SEC1 uncompressed format (0x04 prefix)")

    # Point X (the actual public key): 65 bytes
    x_bytes = point_data

    # Generate placeholder ZKP (SIMULATOR ONLY - NOT CRYPTOGRAPHICALLY VALID)
    # In production, this would be a Schnorr ZKP: (V, r) where:
    #   V = G * v (random point)
    #   r = v - x * h (scalar, where h = hash(G || V || X || UserID))

    # ZKP Point V: 65 bytes (random P-256 point for simulation)
    # Format: 0x04 + random_x_coord (32 bytes) + random_y_coord (32 bytes)
    zkp_v = b"\x04" + secrets.token_bytes(64)

    # ZKP scalar r: 1-byte length + 34-byte value
    r_length = bytes([34])
    zkp_r = secrets.token_bytes(34)

    # Combine into 165-byte structure
    return x_bytes + zkp_v + r_length + zkp_r


def decode_ec_jpake_key_kp(data: bytes) -> Tuple[bytes, bytes, bytes]:
    """Decode an EC-JPAKE Key-Knowledge Proof structure.

    Args:
        data: 165-byte ECJPAKEKeyKP structure

    Returns:
        Tuple of (point_x, zkp_v, zkp_r):
            - point_x: 65-byte EC point (SEC1 uncompressed)
            - zkp_v: 65-byte ZKP commitment point
            - zkp_r: 34-byte ZKP scalar

    Raises:
        ValueError: If data is not 165 bytes or format is invalid
    """
    if len(data) != 165:
        raise ValueError(f"ECJPAKEKeyKP must be 165 bytes, got {len(data)}")

    # Extract Point X (bytes 0-64)
    point_x = data[0:65]
    if point_x[0] != 0x04:
        raise ValueError("Point X must be in SEC1 uncompressed format")

    # Extract ZKP Point V (bytes 65-129)
    zkp_v = data[65:130]
    if zkp_v[0] != 0x04:
        raise ValueError("ZKP Point V must be in SEC1 uncompressed format")

    # Extract ZKP r length (byte 130)
    r_length = data[130]
    if r_length != 34:
        raise ValueError(f"ZKP r length must be 34 for P-256, got {r_length}")

    # Extract ZKP scalar r (bytes 131-164)
    zkp_r = data[131:165]
    if len(zkp_r) != 34:
        raise ValueError(f"ZKP r must be 34 bytes, got {len(zkp_r)}")

    return point_x, zkp_v, zkp_r


def encode_jpake_round1_pair(g1_point: bytes, g2_point: bytes) -> Tuple[bytes, bytes]:
    """Encode JPake Round 1 data into two 165-byte messages.

    Args:
        g1_point: First public key (G1, 65 bytes SEC1 format)
        g2_point: Second public key (G2, 65 bytes SEC1 format)

    Returns:
        Tuple of (jpake1a_data, jpake1b_data), each 165 bytes

    Note:
        Matches pumpx2's split of getRound1() 330-byte output:
        - First 165 bytes: G1 + ZKP(G1)
        - Second 165 bytes: G2 + ZKP(G2)
    """
    jpake1a = encode_ec_jpake_key_kp(g1_point)
    jpake1b = encode_ec_jpake_key_kp(g2_point)
    return jpake1a, jpake1b


def decode_jpake_round1_pair(jpake1a: bytes, jpake1b: bytes) -> Tuple[bytes, bytes]:
    """Decode JPake Round 1 pair into public key points.

    Args:
        jpake1a: First 165-byte KKP structure (G3 + ZKP)
        jpake1b: Second 165-byte KKP structure (G4 + ZKP)

    Returns:
        Tuple of (g3_point, g4_point), each 65 bytes

    Note:
        For simulation, we extract the points but don't verify ZKPs.
        A production implementation MUST verify the Schnorr proofs.
    """
    g3_point, _, _ = decode_ec_jpake_key_kp(jpake1a)
    g4_point, _, _ = decode_ec_jpake_key_kp(jpake1b)
    return g3_point, g4_point


def encode_jpake_round2(a_point: bytes) -> bytes:
    """Encode JPake Round 2 data (A value with ZKP).

    Args:
        a_point: Derived public key A (65 bytes SEC1 format)

    Returns:
        165-byte ECJPAKEKeyKP structure
    """
    return encode_ec_jpake_key_kp(a_point)


def decode_jpake_round2(data: bytes) -> bytes:
    """Decode JPake Round 2 data to extract B value.

    Args:
        data: 165 or 168 bytes (pumpx2 response may have 3 extra bytes padding)

    Returns:
        65-byte B point (SEC1 format)

    Note:
        Handles both 165-byte and 168-byte variants seen in pumpx2.
    """
    # Handle 168-byte variant (extra 3 bytes padding in response)
    if len(data) == 168:
        data = data[0:165]

    b_point, _, _ = decode_ec_jpake_key_kp(data)
    return b_point


def generate_jpake4_hash_digest(
    session_key: bytes, role: str, nonce: bytes, reserved: bytes
) -> bytes:
    """Generate JPake Round 4 key confirmation hash.

    Args:
        session_key: Derived session key from EC-JPAKE
        role: "pump" or "app"
        nonce: 8-byte nonce value
        reserved: 8-byte reserved field (typically zeros)

    Returns:
        32-byte SHA-256 hash digest

    Note:
        SIMULATOR ONLY: Uses simplified hash. Production should use
        HMAC-SHA256 with all exchanged points as in pumpx2.
    """
    # SIMULATOR: Simple hash for simulation purposes
    # PRODUCTION: Should be HMAC-SHA256(session_key, "JPake-Confirmation-" + role)
    # and include all exchanged EC points (G1, G2, G3, G4, A, B)

    confirmation_string = f"JPake-Confirmation-{role}".encode("utf-8")
    hasher = hashlib.sha256()
    hasher.update(session_key)
    hasher.update(confirmation_string)
    hasher.update(nonce)
    hasher.update(reserved)
    return hasher.digest()  # 32 bytes


def verify_jpake4_hash_digest(
    received_hash: bytes, session_key: bytes, role: str, nonce: bytes, reserved: bytes
) -> bool:
    """Verify JPake Round 4 key confirmation hash.

    Args:
        received_hash: 32-byte hash from other party
        session_key: Derived session key from EC-JPAKE
        role: "pump" or "app" (counterparty role)
        nonce: 8-byte nonce value
        reserved: 8-byte reserved field

    Returns:
        True if hash matches expected value

    Note:
        SIMULATOR ONLY: Uses simplified verification. Production needs
        proper HMAC verification with constant-time comparison.
    """
    expected_hash = generate_jpake4_hash_digest(session_key, role, nonce, reserved)
    return received_hash == expected_hash
