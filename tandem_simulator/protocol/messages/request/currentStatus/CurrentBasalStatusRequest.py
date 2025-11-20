"""Current basal status request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry


class CurrentBasalStatusRequest(Message):
    """Current basal status request message.

    Opcode: 40 (0x28)
    Payload: 0 bytes (empty)

    Requests current basal rate information.
    """

    opcode = 40

    def __init__(self, transaction_id: int = 0):
        """Initialize basal status request.

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
MessageRegistry.register(40, CurrentBasalStatusRequest)
