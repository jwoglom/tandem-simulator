"""Insulin status response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


class InsulinStatusResponse(Message):
    """Insulin status response message.

    Opcode: 37 (0x25)
    Payload: 4 bytes
    - Bytes 0-1: Current insulin amount (little-endian int16, units * 100)
    - Byte 2: Is estimate flag (0 or 1)
    - Byte 3: Insulin low amount threshold

    Response with insulin reservoir status.
    """

    opcode = 37

    def __init__(
        self,
        transaction_id: int = 0,
        current_insulin_amount: int = 30000,  # 300.00 units * 100
        is_estimate: int = 0,
        insulin_low_amount: int = 20,
    ):
        """Initialize insulin status response.

        Args:
            transaction_id: Transaction ID
            current_insulin_amount: Current insulin amount (units * 100)
            is_estimate: Whether the amount is an estimate (0 or 1)
            insulin_low_amount: Low insulin threshold
        """
        super().__init__(transaction_id)
        self.current_insulin_amount = current_insulin_amount
        self.is_estimate = is_estimate
        self.insulin_low_amount = insulin_low_amount

    def parse_payload(self, payload: bytes) -> None:
        """Parse insulin status from payload.

        Args:
            payload: Raw payload bytes (4 bytes)
        """
        if len(payload) >= 4:
            # CRITICAL: Java Bytes.readShort() returns unsigned, not signed
            self.current_insulin_amount = read_uint16_le(payload, 0)
            self.is_estimate = payload[2]
            self.insulin_low_amount = payload[3]

    def build_payload(self) -> bytes:
        """Build insulin status payload.

        Returns:
            Insulin status bytes (4 bytes)
        """
        return (
            write_uint16_le(self.current_insulin_amount)
            + bytes([self.is_estimate])
            + bytes([self.insulin_low_amount])
        )


# Register the message
MessageRegistry.register(37, InsulinStatusResponse)
