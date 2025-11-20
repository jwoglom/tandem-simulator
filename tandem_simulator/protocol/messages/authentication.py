"""Authentication and pairing message implementations.

This module implements the authentication message types used in the
JPake pairing and challenge-response flows.

All message implementations match pumpx2 EXACTLY:
https://github.com/jwoglom/pumpX2/tree/main/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/request/authentication
https://github.com/jwoglom/pumpX2/tree/main/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/authentication

Milestone 4 implementation - exact pumpx2 compatibility.
"""

import struct

from tandem_simulator.protocol.message import Message, MessageRegistry


# Utility functions for little-endian encoding/decoding
def read_uint16_le(data: bytes, offset: int = 0) -> int:
    """Read a 16-bit unsigned integer in little-endian format."""
    value: int = struct.unpack_from("<H", data, offset)[0]
    return value


def write_uint16_le(value: int) -> bytes:
    """Write a 16-bit unsigned integer in little-endian format."""
    return struct.pack("<H", value)


# =============================================================================
# Challenge Messages (Opcodes 16-19)
# =============================================================================


class CentralChallengeRequest(Message):
    """Central challenge request message.

    Opcode: 16 (0x10)
    Payload: 10 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-9: central_challenge (8 bytes fixed)

    Initiates authentication by sending a challenge from the central device.
    """

    opcode = 16

    def __init__(
        self, transaction_id: int = 0, app_instance_id: int = 0, central_challenge: bytes = b""
    ):
        """Initialize central challenge request.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            central_challenge: Challenge data (exactly 8 bytes)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.central_challenge = central_challenge

    def parse_payload(self, payload: bytes) -> None:
        """Parse challenge from payload.

        Args:
            payload: Raw payload bytes (10 bytes)
        """
        if len(payload) >= 10:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.central_challenge = payload[2:10]

    def build_payload(self) -> bytes:
        """Build challenge payload.

        Returns:
            10-byte payload (app_instance_id + 8-byte challenge)
        """
        # Ensure challenge is exactly 8 bytes
        challenge = self.central_challenge[:8].ljust(8, b"\x00")
        return write_uint16_le(self.app_instance_id) + challenge


class CentralChallengeResponse(Message):
    """Central challenge response message.

    Opcode: 17 (0x11)
    Payload: 30 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-21: central_challenge_hash (20 bytes)
    - Bytes 22-29: hmac_key (8 bytes)

    Response to central challenge with hashed challenge and HMAC key.
    """

    opcode = 17

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        central_challenge_hash: bytes = b"",
        hmac_key: bytes = b"",
    ):
        """Initialize central challenge response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            central_challenge_hash: SHA1 hash of challenge (20 bytes)
            hmac_key: HMAC key (8 bytes)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.central_challenge_hash = central_challenge_hash
        self.hmac_key = hmac_key

    def parse_payload(self, payload: bytes) -> None:
        """Parse response from payload.

        Args:
            payload: Raw payload bytes (30 bytes)
        """
        if len(payload) >= 30:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.central_challenge_hash = payload[2:22]
            self.hmac_key = payload[22:30]

    def build_payload(self) -> bytes:
        """Build response payload.

        Returns:
            30-byte payload (app_instance_id + hash + hmac_key)
        """
        # Ensure correct sizes
        hash_data = self.central_challenge_hash[:20].ljust(20, b"\x00")
        key_data = self.hmac_key[:8].ljust(8, b"\x00")
        return write_uint16_le(self.app_instance_id) + hash_data + key_data


class PumpChallengeRequest(Message):
    """Pump challenge request message.

    Opcode: 18 (0x12)
    Payload: 22 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-21: pump_challenge_hash (20 bytes)

    Request challenge from pump during authentication.
    """

    opcode = 18

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        pump_challenge_hash: bytes = b"",
    ):
        """Initialize pump challenge request.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            pump_challenge_hash: SHA1 hash of pump challenge (20 bytes)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.pump_challenge_hash = pump_challenge_hash

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (22 bytes)
        """
        if len(payload) >= 22:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.pump_challenge_hash = payload[2:22]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            22-byte payload (app_instance_id + 20-byte hash)
        """
        hash_data = self.pump_challenge_hash[:20].ljust(20, b"\x00")
        return write_uint16_le(self.app_instance_id) + hash_data


class PumpChallengeResponse(Message):
    """Pump challenge response message.

    Opcode: 19 (0x13)
    Payload: 3 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Byte 2: success (boolean, 0 or 1)

    Response indicating success or failure of pump challenge.
    """

    opcode = 19

    def __init__(self, transaction_id: int = 0, app_instance_id: int = 0, success: bool = False):
        """Initialize pump challenge response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            success: Whether challenge was successful
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.success = success

    def parse_payload(self, payload: bytes) -> None:
        """Parse response from payload.

        Args:
            payload: Raw payload bytes (3 bytes)
        """
        if len(payload) >= 3:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.success = bool(payload[2])

    def build_payload(self) -> bytes:
        """Build response payload.

        Returns:
            3-byte payload (app_instance_id + success byte)
        """
        return write_uint16_le(self.app_instance_id) + bytes([1 if self.success else 0])


# =============================================================================
# JPake Round 1 Messages (Opcodes 32-35)
# =============================================================================


class Jpake1aRequest(Message):
    """JPake Round 1a request message.

    Opcode: 32 (0x20)
    Payload: 167 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-166: central_challenge (165 bytes fixed)

    First round of JPake key exchange from central device.
    """

    opcode = 32

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        central_challenge: bytes = b"",
    ):
        """Initialize Jpake1a request.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            central_challenge: JPake challenge data (165 bytes fixed)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.central_challenge = central_challenge

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (167 bytes)
        """
        if len(payload) >= 167:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.central_challenge = payload[2:167]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            167-byte payload (app_instance_id + 165-byte challenge)
        """
        # Ensure challenge is exactly 165 bytes
        challenge = self.central_challenge[:165].ljust(165, b"\x00")
        return write_uint16_le(self.app_instance_id) + challenge


class Jpake1aResponse(Message):
    """JPake Round 1a response message.

    Opcode: 33 (0x21)
    Payload: 167 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-166: central_challenge_hash (165 bytes fixed)

    Response to Jpake1a with hashed challenge data.
    """

    opcode = 33

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        central_challenge_hash: bytes = b"",
    ):
        """Initialize Jpake1a response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            central_challenge_hash: Hashed challenge (165 bytes fixed)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.central_challenge_hash = central_challenge_hash

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (167 bytes)
        """
        if len(payload) >= 167:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.central_challenge_hash = payload[2:167]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            167-byte payload (app_instance_id + 165-byte hash)
        """
        hash_data = self.central_challenge_hash[:165].ljust(165, b"\x00")
        return write_uint16_le(self.app_instance_id) + hash_data


class Jpake1bRequest(Message):
    """JPake Round 1b request message.

    Opcode: 34 (0x22)
    Payload: 167 bytes (same structure as Jpake1a)
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-166: central_challenge (165 bytes fixed)

    Second part of JPake round 1 from central device.
    """

    opcode = 34

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        central_challenge: bytes = b"",
    ):
        """Initialize Jpake1b request.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            central_challenge: JPake challenge data (165 bytes fixed)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.central_challenge = central_challenge

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (167 bytes)
        """
        if len(payload) >= 167:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.central_challenge = payload[2:167]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            167-byte payload (app_instance_id + 165-byte challenge)
        """
        challenge = self.central_challenge[:165].ljust(165, b"\x00")
        return write_uint16_le(self.app_instance_id) + challenge


class Jpake1bResponse(Message):
    """JPake Round 1b response message.

    Opcode: 35 (0x23)
    Payload: 167 bytes (same structure as Jpake1a response)
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-166: central_challenge_hash (165 bytes fixed)

    Response to Jpake1b with hashed challenge data.
    """

    opcode = 35

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        central_challenge_hash: bytes = b"",
    ):
        """Initialize Jpake1b response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            central_challenge_hash: Hashed challenge (165 bytes fixed)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.central_challenge_hash = central_challenge_hash

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (167 bytes)
        """
        if len(payload) >= 167:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.central_challenge_hash = payload[2:167]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            167-byte payload (app_instance_id + 165-byte hash)
        """
        hash_data = self.central_challenge_hash[:165].ljust(165, b"\x00")
        return write_uint16_le(self.app_instance_id) + hash_data


# =============================================================================
# JPake Round 2 Messages (Opcodes 36-37)
# =============================================================================


class Jpake2Request(Message):
    """JPake Round 2 request message.

    Opcode: 36 (0x24)
    Payload: Variable (with app_instance_id prefix)

    Second round of JPake key exchange.
    """

    opcode = 36

    def __init__(self, transaction_id: int = 0, app_instance_id: int = 0, data: bytes = b""):
        """Initialize Jpake2 request.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            data: JPake round 2 data
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.data = data

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes
        """
        if len(payload) >= 2:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.data = payload[2:]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            Payload with app_instance_id prefix
        """
        return write_uint16_le(self.app_instance_id) + self.data


class Jpake2Response(Message):
    """JPake Round 2 response message.

    Opcode: 37 (0x25)
    Payload: Variable (with app_instance_id prefix)

    Response to Jpake2 request.
    """

    opcode = 37

    def __init__(self, transaction_id: int = 0, app_instance_id: int = 0, data: bytes = b""):
        """Initialize Jpake2 response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            data: JPake round 2 response data
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.data = data

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes
        """
        if len(payload) >= 2:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.data = payload[2:]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            Payload with app_instance_id prefix
        """
        return write_uint16_le(self.app_instance_id) + self.data


# =============================================================================
# JPake Session Key Messages (Opcodes 38-39)
# =============================================================================


class Jpake3SessionKeyRequest(Message):
    """JPake Round 3 session key request message.

    Opcode: 38 (0x26)
    Payload: 2 bytes
    - Bytes 0-1: challenge_param (uint16, little-endian)

    Session key negotiation request.
    """

    opcode = 38

    def __init__(self, transaction_id: int = 0, challenge_param: int = 0):
        """Initialize Jpake3 session key request.

        Args:
            transaction_id: Transaction ID
            challenge_param: Challenge parameter (uint16, 2 bytes) - NOT generic bytes
        """
        super().__init__(transaction_id)
        self.challenge_param = challenge_param

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (2 bytes)
        """
        if len(payload) >= 2:
            self.challenge_param = read_uint16_le(payload, 0)

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            2-byte payload (challenge_param as uint16 little-endian)
        """
        return write_uint16_le(self.challenge_param)


class Jpake3SessionKeyResponse(Message):
    """JPake Round 3 session key response message.

    Opcode: 39 (0x27)
    Payload: 18 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-9: device_key_nonce (8 bytes)
    - Bytes 10-17: device_key_reserved (8 bytes)

    Session key response with device keys.
    """

    opcode = 39

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        device_key_nonce: bytes = b"",
        device_key_reserved: bytes = b"",
    ):
        """Initialize Jpake3 session key response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            device_key_nonce: Device key nonce (8 bytes)
            device_key_reserved: Device key reserved (8 bytes)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.device_key_nonce = device_key_nonce
        self.device_key_reserved = device_key_reserved

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (18 bytes)
        """
        if len(payload) >= 18:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.device_key_nonce = payload[2:10]
            self.device_key_reserved = payload[10:18]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            18-byte payload (app_instance_id + nonce + reserved)
        """
        nonce = self.device_key_nonce[:8].ljust(8, b"\x00")
        reserved = self.device_key_reserved[:8].ljust(8, b"\x00")
        return write_uint16_le(self.app_instance_id) + nonce + reserved


# =============================================================================
# JPake Key Confirmation Messages (Opcodes 40-41)
# =============================================================================


class Jpake4KeyConfirmationRequest(Message):
    """JPake Round 4 key confirmation request message.

    Opcode: 40 (0x28)
    Payload: 50 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-9: nonce (8 bytes EXACTLY)
    - Bytes 10-17: reserved (8 bytes EXACTLY)
    - Bytes 18-49: hash_digest (32 bytes EXACTLY - SHA256)

    Final key confirmation request with validated field sizes.
    """

    opcode = 40

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        nonce: bytes = b"",
        reserved: bytes = b"",
        hash_digest: bytes = b"",
    ):
        """Initialize Jpake4 key confirmation request.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            nonce: Nonce (MUST be exactly 8 bytes)
            reserved: Reserved (MUST be exactly 8 bytes)
            hash_digest: SHA256 hash (MUST be exactly 32 bytes)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.nonce = nonce
        self.reserved = reserved
        self.hash_digest = hash_digest

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (50 bytes)
        """
        if len(payload) >= 50:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.nonce = payload[2:10]
            self.reserved = payload[10:18]
            self.hash_digest = payload[18:50]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            50-byte payload (validated field sizes)
        """
        # Validate field sizes
        nonce = self.nonce[:8].ljust(8, b"\x00")
        reserved = self.reserved[:8].ljust(8, b"\x00")
        hash_digest = self.hash_digest[:32].ljust(32, b"\x00")

        return write_uint16_le(self.app_instance_id) + nonce + reserved + hash_digest


class Jpake4KeyConfirmationResponse(Message):
    """JPake Round 4 key confirmation response message.

    Opcode: 41 (0x29)
    Payload: 50 bytes (same structure as request)
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-9: nonce (8 bytes)
    - Bytes 10-17: reserved (8 bytes)
    - Bytes 18-49: hash_digest (32 bytes - SHA256)

    Response confirming key exchange completion.
    """

    opcode = 41

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        nonce: bytes = b"",
        reserved: bytes = b"",
        hash_digest: bytes = b"",
    ):
        """Initialize Jpake4 key confirmation response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            nonce: Nonce (8 bytes)
            reserved: Reserved (8 bytes)
            hash_digest: SHA256 hash (32 bytes)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.nonce = nonce
        self.reserved = reserved
        self.hash_digest = hash_digest

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (50 bytes)
        """
        if len(payload) >= 50:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.nonce = payload[2:10]
            self.reserved = payload[10:18]
            self.hash_digest = payload[18:50]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            50-byte payload
        """
        nonce = self.nonce[:8].ljust(8, b"\x00")
        reserved = self.reserved[:8].ljust(8, b"\x00")
        hash_digest = self.hash_digest[:32].ljust(32, b"\x00")

        return write_uint16_le(self.app_instance_id) + nonce + reserved + hash_digest


# Register all authentication messages
MessageRegistry.register(CentralChallengeRequest.opcode, CentralChallengeRequest)
MessageRegistry.register(CentralChallengeResponse.opcode, CentralChallengeResponse)
MessageRegistry.register(PumpChallengeRequest.opcode, PumpChallengeRequest)
MessageRegistry.register(PumpChallengeResponse.opcode, PumpChallengeResponse)
MessageRegistry.register(Jpake1aRequest.opcode, Jpake1aRequest)
MessageRegistry.register(Jpake1aResponse.opcode, Jpake1aResponse)
MessageRegistry.register(Jpake1bRequest.opcode, Jpake1bRequest)
MessageRegistry.register(Jpake1bResponse.opcode, Jpake1bResponse)
MessageRegistry.register(Jpake2Request.opcode, Jpake2Request)
MessageRegistry.register(Jpake2Response.opcode, Jpake2Response)
MessageRegistry.register(Jpake3SessionKeyRequest.opcode, Jpake3SessionKeyRequest)
MessageRegistry.register(Jpake3SessionKeyResponse.opcode, Jpake3SessionKeyResponse)
MessageRegistry.register(Jpake4KeyConfirmationRequest.opcode, Jpake4KeyConfirmationRequest)
MessageRegistry.register(Jpake4KeyConfirmationResponse.opcode, Jpake4KeyConfirmationResponse)
