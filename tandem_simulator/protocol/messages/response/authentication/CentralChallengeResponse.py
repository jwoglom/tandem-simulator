"""Central challenge response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(17, CentralChallengeResponse)
