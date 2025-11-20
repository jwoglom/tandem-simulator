"""API version response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


class ApiVersionResponse(Message):
    """API version response message.

    Opcode: 33 (0x21)
    Payload: 4 bytes
    - Bytes 0-1: Major version (little-endian uint16)
    - Bytes 2-3: Minor version (little-endian uint16)

    Response with pump's API version.
    """

    opcode = 33

    def __init__(self, transaction_id: int = 0, major: int = 1, minor: int = 0):
        """Initialize API version response.

        Args:
            transaction_id: Transaction ID
            major: Major version number
            minor: Minor version number
        """
        super().__init__(transaction_id)
        self.major = major
        self.minor = minor

    def parse_payload(self, payload: bytes) -> None:
        """Parse version from payload.

        Args:
            payload: Raw payload bytes (4 bytes: major, minor as uint16 LE)
        """
        if len(payload) >= 4:
            self.major = read_uint16_le(payload, 0)
            self.minor = read_uint16_le(payload, 2)

    def build_payload(self) -> bytes:
        """Build version payload.

        Returns:
            Version bytes (4 bytes: major, minor as uint16 LE)
        """
        return write_uint16_le(self.major) + write_uint16_le(self.minor)


# Register the message
MessageRegistry.register(33, ApiVersionResponse)
