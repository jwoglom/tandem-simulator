"""JPake Round 3 session key request message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


class Jpake3SessionKeyRequest(Message):
    """JPake Round 3 session key request message.

    Opcode: 38 (0x26)
    Payload: 2 bytes
    - Bytes 0-1: challenge_param (uint16, little-endian)

    Session key negotiation request.
    """

    opcode = 38

    def __init__(self, transaction_id: int = 0, challenge_param: int = 0):
        """Initialize Jpake3 session key request.

        Args:
            transaction_id: Transaction ID
            challenge_param: Challenge parameter (uint16, 2 bytes) - NOT generic bytes
        """
        super().__init__(transaction_id)
        self.challenge_param = challenge_param

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (2 bytes)
        """
        if len(payload) >= 2:
            self.challenge_param = read_uint16_le(payload, 0)

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            2-byte payload (challenge_param as uint16 little-endian)
        """
        return write_uint16_le(self.challenge_param)


# Register the message
MessageRegistry.register(38, Jpake3SessionKeyRequest)
