"""JPake Round 4 key confirmation request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(40, Jpake4KeyConfirmationRequest)
