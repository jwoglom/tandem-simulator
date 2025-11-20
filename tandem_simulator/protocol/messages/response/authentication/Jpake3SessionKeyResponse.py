"""JPake Round 3 session key response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint16_le, write_uint16_le


class Jpake3SessionKeyResponse(Message):
    """JPake Round 3 session key response message.

    Opcode: 39 (0x27)
    Payload: 18 bytes
    - Bytes 0-1: app_instance_id (uint16, little-endian)
    - Bytes 2-9: device_key_nonce (8 bytes)
    - Bytes 10-17: device_key_reserved (8 bytes)

    Session key response with device keys.
    """

    opcode = 39

    def __init__(
        self,
        transaction_id: int = 0,
        app_instance_id: int = 0,
        device_key_nonce: bytes = b"",
        device_key_reserved: bytes = b"",
    ):
        """Initialize Jpake3 session key response.

        Args:
            transaction_id: Transaction ID
            app_instance_id: Application instance ID (uint16, 2 bytes)
            device_key_nonce: Device key nonce (8 bytes)
            device_key_reserved: Device key reserved (8 bytes)
        """
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.device_key_nonce = device_key_nonce
        self.device_key_reserved = device_key_reserved

    def parse_payload(self, payload: bytes) -> None:
        """Parse payload.

        Args:
            payload: Raw payload bytes (18 bytes)
        """
        if len(payload) >= 18:
            self.app_instance_id = read_uint16_le(payload, 0)
            self.device_key_nonce = payload[2:10]
            self.device_key_reserved = payload[10:18]

    def build_payload(self) -> bytes:
        """Build payload.

        Returns:
            18-byte payload (app_instance_id + nonce + reserved)
        """
        nonce = self.device_key_nonce[:8].ljust(8, b"\x00")
        reserved = self.device_key_reserved[:8].ljust(8, b"\x00")
        return write_uint16_le(self.app_instance_id) + nonce + reserved


# Register the message
MessageRegistry.register(39, Jpake3SessionKeyResponse)
