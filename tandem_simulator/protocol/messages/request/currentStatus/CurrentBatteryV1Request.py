"""Current battery status request (V1)."""

from tandem_simulator.protocol.message import Message, MessageRegistry


class CurrentBatteryV1Request(Message):
    """Current battery status request (V1).

    Opcode: 52 (0x34)
    Payload: 0 bytes (empty)

    Requests current battery level.
    """

    opcode = 52

    def __init__(self, transaction_id: int = 0):
        """Initialize battery request.

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
MessageRegistry.register(52, CurrentBatteryV1Request)
