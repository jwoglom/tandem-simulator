"""Current bolus status request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry


class CurrentBolusStatusRequest(Message):
    """Current bolus status request message.

    Opcode: 44 (0x2C)
    Payload: 0 bytes (empty)

    Requests current bolus delivery status.
    """

    opcode = 44

    def __init__(self, transaction_id: int = 0):
        """Initialize bolus status request.

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
MessageRegistry.register(44, CurrentBolusStatusRequest)
