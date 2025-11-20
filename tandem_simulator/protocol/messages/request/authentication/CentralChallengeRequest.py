"""Central challenge request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(16, CentralChallengeRequest)
