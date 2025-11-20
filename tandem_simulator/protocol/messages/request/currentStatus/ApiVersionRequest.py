"""API version request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry


class ApiVersionRequest(Message):
    """API version request message.

    Opcode: 32 (0x20)
    Payload: 0 bytes (empty)

    Requests the pump's API version.
    Returns the major and minor API version of the pump.
    """

    opcode = 32

    def __init__(self, transaction_id: int = 0):
        """Initialize API version request.

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
MessageRegistry.register(32, ApiVersionRequest)
