"""JPake Round 1a response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(33, Jpake1aResponse)
