"""Pump challenge request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(18, PumpChallengeRequest)
