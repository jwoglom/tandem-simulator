"""Current basal status response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import read_uint32_le, write_uint32_le


class CurrentBasalStatusResponse(Message):
    """Current basal status response message.

    Opcode: 41 (0x29)
    Payload: 9 bytes
    - Bytes 0-3: Profile basal rate (little-endian uint32, units/hr * 10000)
    - Bytes 4-7: Current basal rate (little-endian uint32, units/hr * 10000)
    - Byte 8: Basal modified bitmask

    Response with current basal rate information.
    """

    opcode = 41

    def __init__(
        self,
        transaction_id: int = 0,
        profile_basal_rate: int = 8500,  # 0.85 units/hr * 10000
        current_basal_rate: int = 8500,  # 0.85 units/hr * 10000
        basal_modified_bitmask: int = 0,
    ):
        """Initialize basal status response.

        Args:
            transaction_id: Transaction ID
            profile_basal_rate: Profile basal rate (units/hr * 10000)
            current_basal_rate: Current basal rate (units/hr * 10000)
            basal_modified_bitmask: Bitmask indicating modifications
        """
        super().__init__(transaction_id)
        self.profile_basal_rate = profile_basal_rate
        self.current_basal_rate = current_basal_rate
        self.basal_modified_bitmask = basal_modified_bitmask

    def parse_payload(self, payload: bytes) -> None:
        """Parse basal status from payload.

        Args:
            payload: Raw payload bytes (9 bytes)
        """
        if len(payload) >= 9:
            self.profile_basal_rate = read_uint32_le(payload, 0)
            self.current_basal_rate = read_uint32_le(payload, 4)
            self.basal_modified_bitmask = payload[8]

    def build_payload(self) -> bytes:
        """Build basal status payload.

        Returns:
            Basal status bytes (9 bytes)
        """
        return (
            write_uint32_le(self.profile_basal_rate)
            + write_uint32_le(self.current_basal_rate)
            + bytes([self.basal_modified_bitmask])
        )


# Register the message
MessageRegistry.register(41, CurrentBasalStatusResponse)
