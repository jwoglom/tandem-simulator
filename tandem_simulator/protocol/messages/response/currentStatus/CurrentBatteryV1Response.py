"""Current battery status response (V1)."""

from tandem_simulator.protocol.message import Message, MessageRegistry


class CurrentBatteryV1Response(Message):
    """Current battery status response (V1).

    Opcode: 53 (0x35)
    Payload: 2 bytes
    - Byte 0: Current battery ABC value
    - Byte 1: Current battery IBC value

    Response with battery status.
    """

    opcode = 53

    def __init__(
        self,
        transaction_id: int = 0,
        current_battery_abc: int = 100,
        current_battery_ibc: int = 100,
    ):
        """Initialize battery response.

        Args:
            transaction_id: Transaction ID
            current_battery_abc: Battery ABC measurement
            current_battery_ibc: Battery IBC measurement
        """
        super().__init__(transaction_id)
        self.current_battery_abc = current_battery_abc
        self.current_battery_ibc = current_battery_ibc

    def parse_payload(self, payload: bytes) -> None:
        """Parse battery level from payload.

        Args:
            payload: Raw payload bytes (2 bytes)
        """
        if len(payload) >= 2:
            self.current_battery_abc = payload[0]
            self.current_battery_ibc = payload[1]

    def build_payload(self) -> bytes:
        """Build battery level payload.

        Returns:
            Battery level bytes (2 bytes)
        """
        return bytes([self.current_battery_abc, self.current_battery_ibc])


# Register the message
MessageRegistry.register(53, CurrentBatteryV1Response)
