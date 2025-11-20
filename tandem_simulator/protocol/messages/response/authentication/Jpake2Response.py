"""JPake Round 2 response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


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


# Register the message
MessageRegistry.register(37, Jpake2Response)
