"""JPake Round 1b request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(34, Jpake1bRequest)
