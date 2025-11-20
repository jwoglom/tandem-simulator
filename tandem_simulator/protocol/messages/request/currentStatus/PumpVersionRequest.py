"""Pump version request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry


class PumpVersionRequest(Message):
    """Pump version request message.

    Opcode: 84 (0x54)
    Payload: 0 bytes (empty)

    Requests the pump's firmware version.
    """

    opcode = 84

    def __init__(self, transaction_id: int = 0):
        """Initialize pump version request.

        Args:
            transaction_id: Transaction ID
        """
        super().__init__(transaction_id)

    def build_payload(self) -> bytes:
        """Build empty payload.

        Returns:
            Empty bytes
        """
        return b""


# Register the message
MessageRegistry.register(84, PumpVersionRequest)
