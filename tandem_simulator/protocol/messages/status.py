"""Status and information message implementations.

This module implements status request and response messages for
querying pump state and information.

Messages are implemented exactly as defined in PumpX2:
https://github.com/jwoglom/pumpX2

Milestone 4 implementation.
"""

import struct
from tandem_simulator.protocol.message import Message, MessageRegistry


# Utility functions for little-endian encoding/decoding
def read_uint16_le(data: bytes, offset: int = 0) -> int:
    """Read a 16-bit unsigned integer in little-endian format.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from

    Returns:
        Unsigned 16-bit integer
    """
    return struct.unpack_from("<H", data, offset)[0]


def read_uint32_le(data: bytes, offset: int = 0) -> int:
    """Read a 32-bit unsigned integer in little-endian format.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from

    Returns:
        Unsigned 32-bit integer
    """
    return struct.unpack_from("<I", data, offset)[0]


def read_int16_le(data: bytes, offset: int = 0) -> int:
    """Read a 16-bit signed integer in little-endian format.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from

    Returns:
        Signed 16-bit integer
    """
    return struct.unpack_from("<h", data, offset)[0]


def write_uint16_le(value: int) -> bytes:
    """Write a 16-bit unsigned integer in little-endian format.

    Args:
        value: Integer value to encode

    Returns:
        2 bytes in little-endian format
    """
    return struct.pack("<H", value)


def write_uint32_le(value: int) -> bytes:
    """Write a 32-bit unsigned integer in little-endian format.

    Args:
        value: Integer value to encode

    Returns:
        4 bytes in little-endian format
    """
    return struct.pack("<I", value)


def write_int16_le(value: int) -> bytes:
    """Write a 16-bit signed integer in little-endian format.

    Args:
        value: Integer value to encode

    Returns:
        2 bytes in little-endian format
    """
    return struct.pack("<h", value)


def read_string(data: bytes, offset: int, length: int) -> str:
    """Read a fixed-length null-padded string.

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from
        length: Number of bytes to read

    Returns:
        Decoded UTF-8 string (null bytes stripped)
    """
    raw_bytes = data[offset : offset + length]
    # Strip null bytes and decode
    return raw_bytes.rstrip(b"\x00").decode("utf-8", errors="ignore")


def write_string(value: str, length: int) -> bytes:
    """Write a string as fixed-length null-padded bytes.

    Args:
        value: String to encode
        length: Fixed length of output (will be padded/truncated)

    Returns:
        Fixed-length bytes (UTF-8 encoded, null-padded)
    """
    encoded = value.encode("utf-8")[:length]  # Truncate if too long
    return encoded + b"\x00" * (length - len(encoded))  # Pad with nulls


# =============================================================================
# API Version Messages (Opcodes 32/33)
# =============================================================================


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


# =============================================================================
# Insulin Status Messages (Opcodes 36/37)
# =============================================================================


class InsulinStatusRequest(Message):
    """Insulin status request message.

    Opcode: 36 (0x24)
    Payload: 0 bytes (empty)

    Requests current insulin reservoir status.
    """

    opcode = 36

    def __init__(self, transaction_id: int = 0):
        """Initialize insulin status request.

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


# =============================================================================
# Current Basal Status Messages (Opcodes 40/41)
# =============================================================================


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


# =============================================================================
# Current Battery Messages (Opcodes 52/53)
# =============================================================================


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


# =============================================================================
# Current Bolus Status Messages (Opcodes 44/45)
# =============================================================================


class CurrentBolusStatusRequest(Message):
    """Current bolus status request message.

    Opcode: 44 (0x2C)
    Payload: 0 bytes (empty)

    Requests current bolus delivery status.
    """

    opcode = 44

    def __init__(self, transaction_id: int = 0):
        """Initialize bolus status request.

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


class CurrentBolusStatusResponse(Message):
    """Current bolus status response message.

    Opcode: 45 (0x2D)
    Payload: Variable size (stub implementation returns empty)

    Response with current bolus delivery status.
    """

    opcode = 45

    def __init__(self, transaction_id: int = 0):
        """Initialize bolus status response.

        Args:
            transaction_id: Transaction ID
        """
        super().__init__(transaction_id)
        # Stub: Empty bolus status (no active bolus)

    def parse_payload(self, payload: bytes) -> None:
        """Parse bolus status from payload.

        Args:
            payload: Raw payload bytes
        """
        # Stub implementation
        pass

    def build_payload(self) -> bytes:
        """Build bolus status payload.

        Returns:
            Empty bytes (no active bolus)
        """
        # Stub: Return empty to indicate no active bolus
        return b""


# =============================================================================
# Pump Version Messages (Opcodes 84/85)
# =============================================================================


class PumpVersionRequest(Message):
    """Pump version request message.

    Opcode: 84 (0x54)
    Payload: 0 bytes (empty)

    Requests the pump's firmware version.
    """

    opcode = 84

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

    Opcode: 85 (0x55)
    Payload: Variable length string

    Response with pump's firmware version and hardware information.
    """

    opcode = 85

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


# Register all status messages
MessageRegistry.register(ApiVersionRequest.opcode, ApiVersionRequest)
MessageRegistry.register(ApiVersionResponse.opcode, ApiVersionResponse)
MessageRegistry.register(InsulinStatusRequest.opcode, InsulinStatusRequest)
MessageRegistry.register(InsulinStatusResponse.opcode, InsulinStatusResponse)
MessageRegistry.register(CurrentBasalStatusRequest.opcode, CurrentBasalStatusRequest)
MessageRegistry.register(CurrentBasalStatusResponse.opcode, CurrentBasalStatusResponse)
MessageRegistry.register(CurrentBatteryV1Request.opcode, CurrentBatteryV1Request)
MessageRegistry.register(CurrentBatteryV1Response.opcode, CurrentBatteryV1Response)
MessageRegistry.register(CurrentBolusStatusRequest.opcode, CurrentBolusStatusRequest)
MessageRegistry.register(CurrentBolusStatusResponse.opcode, CurrentBolusStatusResponse)
MessageRegistry.register(PumpVersionRequest.opcode, PumpVersionRequest)
MessageRegistry.register(PumpVersionResponse.opcode, PumpVersionResponse)
