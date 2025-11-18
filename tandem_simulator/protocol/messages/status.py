"""Status and information message implementations.

This module implements status request and response messages for
querying pump state and information.

Milestone 2 deliverable (stub implementations - full handlers in Milestone 4).
"""

from tandem_simulator.protocol.message import Message, MessageRegistry


class ApiVersionRequest(Message):
    """API version request message.

    Opcode: 0x04 (example - verify with PumpX2)

    Requests the pump's API version.
    """

    opcode = 0x04

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


class ApiVersionResponse(Message):
    """API version response message.

    Opcode: 0x05 (example - verify with PumpX2)

    Response with pump's API version.
    """

    opcode = 0x05

    def __init__(self, transaction_id: int = 0, major: int = 1, minor: int = 0, patch: int = 0):
        """Initialize API version response.

        Args:
            transaction_id: Transaction ID
            major: Major version number
            minor: Minor version number
            patch: Patch version number
        """
        super().__init__(transaction_id)
        self.major = major
        self.minor = minor
        self.patch = patch

    def parse_payload(self, payload: bytes) -> None:
        """Parse version from payload.

        Args:
            payload: Raw payload bytes (3 bytes: major, minor, patch)
        """
        if len(payload) >= 3:
            self.major = payload[0]
            self.minor = payload[1]
            self.patch = payload[2]

    def build_payload(self) -> bytes:
        """Build version payload.

        Returns:
            Version bytes (3 bytes)
        """
        return bytes([self.major, self.minor, self.patch])


class PumpVersionRequest(Message):
    """Pump version request message.

    Opcode: 0x06 (example - verify with PumpX2)

    Requests the pump's firmware version.
    """

    opcode = 0x06

    def __init__(self, transaction_id: int = 0):
        """Initialize pump version request.

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


class PumpVersionResponse(Message):
    """Pump version response message.

    Opcode: 0x07 (example - verify with PumpX2)

    Response with pump's firmware version string.
    """

    opcode = 0x07

    def __init__(self, transaction_id: int = 0, version: str = "7.7.1"):
        """Initialize pump version response.

        Args:
            transaction_id: Transaction ID
            version: Firmware version string
        """
        super().__init__(transaction_id)
        self.version = version

    def parse_payload(self, payload: bytes) -> None:
        """Parse version string from payload.

        Args:
            payload: Raw payload bytes (UTF-8 encoded string)
        """
        self.version = payload.decode("utf-8", errors="ignore")

    def build_payload(self) -> bytes:
        """Build version string payload.

        Returns:
            Version string bytes (UTF-8 encoded)
        """
        return self.version.encode("utf-8")


class CurrentBatteryRequest(Message):
    """Current battery status request.

    Opcode: 0x08 (example - verify with PumpX2)

    Requests current battery level.
    """

    opcode = 0x08

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


class CurrentBatteryResponse(Message):
    """Current battery status response.

    Opcode: 0x09 (example - verify with PumpX2)

    Response with battery percentage.
    """

    opcode = 0x09

    def __init__(self, transaction_id: int = 0, battery_percent: int = 100):
        """Initialize battery response.

        Args:
            transaction_id: Transaction ID
            battery_percent: Battery level (0-100%)
        """
        super().__init__(transaction_id)
        self.battery_percent = battery_percent

    def parse_payload(self, payload: bytes) -> None:
        """Parse battery level from payload.

        Args:
            payload: Raw payload bytes (1 byte: battery %)
        """
        if len(payload) >= 1:
            self.battery_percent = payload[0]

    def build_payload(self) -> bytes:
        """Build battery level payload.

        Returns:
            Battery level byte
        """
        return bytes([self.battery_percent])


# Register status messages
MessageRegistry.register(ApiVersionRequest.opcode, ApiVersionRequest)
MessageRegistry.register(ApiVersionResponse.opcode, ApiVersionResponse)
MessageRegistry.register(PumpVersionRequest.opcode, PumpVersionRequest)
MessageRegistry.register(PumpVersionResponse.opcode, PumpVersionResponse)
MessageRegistry.register(CurrentBatteryRequest.opcode, CurrentBatteryRequest)
MessageRegistry.register(CurrentBatteryResponse.opcode, CurrentBatteryResponse)
