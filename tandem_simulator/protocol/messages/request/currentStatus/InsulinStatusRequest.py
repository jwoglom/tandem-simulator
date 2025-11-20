"""Insulin status request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry


class InsulinStatusRequest(Message):
    """Insulin status request message.

    Opcode: 36 (0x24)
    Payload: 0 bytes (empty)

    Requests current insulin reservoir status.
    """

    opcode = 36

    def __init__(self, transaction_id: int = 0):
        """Initialize insulin status request.

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
MessageRegistry.register(36, InsulinStatusRequest)
