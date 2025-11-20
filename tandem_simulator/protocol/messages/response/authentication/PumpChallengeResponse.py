"""Pump challenge response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(19, PumpChallengeResponse)
