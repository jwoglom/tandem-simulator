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
    Payload: 15 bytes

    Field layout (exact byte offsets from Java implementation):
    - Byte 0: status_id (int, 1 byte)
    - Bytes 1-2: bolus_id (short, 2 bytes, little-endian)
    - Bytes 3-4: padding (2 zero bytes)
    - Bytes 5-8: timestamp (uint32, 4 bytes, little-endian)
    - Bytes 9-12: requested_volume (uint32, 4 bytes, little-endian)
    - Byte 13: bolus_source_id (int, 1 byte)
    - Byte 14: bolus_type_bitmask (int, 1 byte)

    Total: 15 bytes

    Status ID values:
    - 0: ALREADY_DELIVERED_OR_INVALID
    - 1: DELIVERING
    - 2: REQUESTING

    Response with current bolus delivery status.
    """

    opcode = 45

    # Status enum values
    STATUS_ALREADY_DELIVERED_OR_INVALID = 0
    STATUS_DELIVERING = 1
    STATUS_REQUESTING = 2

    def __init__(
        self,
        transaction_id: int = 0,
        status_id: int = 0,
        bolus_id: int = 0,
        timestamp: int = 0,
        requested_volume: int = 0,
        bolus_source_id: int = 0,
        bolus_type_bitmask: int = 0,
    ):
        """Initialize bolus status response.

        Args:
            transaction_id: Transaction ID
            status_id: Status ID (0=ALREADY_DELIVERED_OR_INVALID, 1=DELIVERING,
                       2=REQUESTING)
            bolus_id: Bolus identifier (unsigned short, 2 bytes)
            timestamp: Timestamp in seconds (unsigned int, 4 bytes)
            requested_volume: Requested volume in insulin units * 10000
                              (unsigned int, 4 bytes)
            bolus_source_id: Bolus source ID (unsigned byte)
            bolus_type_bitmask: Bitmask of bolus types (unsigned byte)
        """
        super().__init__(transaction_id)
        self.status_id = status_id
        self.bolus_id = bolus_id
        self.timestamp = timestamp
        self.requested_volume = requested_volume
        self.bolus_source_id = bolus_source_id
        self.bolus_type_bitmask = bolus_type_bitmask

    def parse_payload(self, payload: bytes) -> None:
        """Parse bolus status from payload.

        Implements exact byte parsing from Java CurrentBolusStatusResponse.parse():
        - Offset 0: statusId = raw[0]
        - Offset 1-2: bolusId = Bytes.readShort(raw, 1) [little-endian unsigned]
        - Offset 5-8: timestamp = Bytes.readUint32(raw, 5)
        - Offset 9-12: requestedVolume = Bytes.readUint32(raw, 9)
        - Offset 13: bolusSourceId = raw[13]
        - Offset 14: bolusTypeBitmask = raw[14]

        Args:
            payload: Raw payload bytes (must be 15 bytes)
        """
        if len(payload) >= 15:
            # Byte 0: status_id (unsigned byte)
            self.status_id = payload[0]

            # Bytes 1-2: bolus_id (unsigned short, little-endian)
            self.bolus_id = read_uint16_le(payload, 1)

            # Bytes 3-4: padding (skipped)
            # (2 zero bytes reserved in the Java implementation)

            # Bytes 5-8: timestamp (unsigned int, little-endian)
            self.timestamp = read_uint32_le(payload, 5)

            # Bytes 9-12: requested_volume (unsigned int, little-endian)
            self.requested_volume = read_uint32_le(payload, 9)

            # Byte 13: bolus_source_id (unsigned byte)
            self.bolus_source_id = payload[13]

            # Byte 14: bolus_type_bitmask (unsigned byte)
            self.bolus_type_bitmask = payload[14]

    def build_payload(self) -> bytes:
        """Build bolus status payload.

        Implements exact byte layout from Java buildCargo():
        - Byte 0: status (1 byte)
        - Bytes 1-2: bolusId (2 bytes, little-endian)
        - Bytes 3-4: padding (2 zero bytes)
        - Bytes 5-8: timestamp (4 bytes, little-endian)
        - Bytes 9-12: requestedVolume (4 bytes, little-endian)
        - Byte 13: bolusSource (1 byte)
        - Byte 14: bolusTypeBitmask (1 byte)

        Returns:
            15-byte payload buffer
        """
        return (
            bytes([self.status_id])
            + write_uint16_le(self.bolus_id)
            + b"\x00\x00"  # 2 bytes padding
            + write_uint32_le(self.timestamp)
            + write_uint32_le(self.requested_volume)
            + bytes([self.bolus_source_id])
            + bytes([self.bolus_type_bitmask])
        )

    def is_valid(self) -> bool:
        """Check if this bolus status represents a valid/active bolus.

        Returns:
            True if status is DELIVERING or REQUESTING, False otherwise
        """
        return self.status_id in (self.STATUS_DELIVERING, self.STATUS_REQUESTING)


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
    Payload: 48 bytes (fixed-size binary structure)

    Field layout (exact byte offsets from Java implementation):
    - Bytes 0-3: arm_sw_ver (uint32, little-endian)
    - Bytes 4-7: msp_sw_ver (uint32, little-endian)
    - Bytes 8-11: config_a_bits (uint32, little-endian)
    - Bytes 12-15: config_b_bits (uint32, little-endian)
    - Bytes 16-19: serial_num (uint32, little-endian)
    - Bytes 20-23: part_num (uint32, little-endian)
    - Bytes 24-31: pump_rev (8-byte null-padded string)
    - Bytes 32-35: pcba_sn (uint32, little-endian)
    - Bytes 36-43: pcba_rev (8-byte null-padded string)
    - Bytes 44-47: model_num (uint32, little-endian)

    Total: 48 bytes

    Response with pump's firmware version and hardware information.
    """

    opcode = 85

    def __init__(
        self,
        transaction_id: int = 0,
        arm_sw_ver: int = 0,
        msp_sw_ver: int = 0,
        config_a_bits: int = 0,
        config_b_bits: int = 0,
        serial_num: int = 0,
        part_num: int = 0,
        pump_rev: str = "",
        pcba_sn: int = 0,
        pcba_rev: str = "",
        model_num: int = 0,
    ):
        """Initialize pump version response.

        Args:
            transaction_id: Transaction ID
            arm_sw_ver: ARM software version (uint32)
            msp_sw_ver: MSP software version (uint32)
            config_a_bits: Configuration A bits (uint32)
            config_b_bits: Configuration B bits (uint32)
            serial_num: Serial number (uint32)
            part_num: Part number (uint32)
            pump_rev: Pump revision string (8 bytes max)
            pcba_sn: PCBA serial number (uint32)
            pcba_rev: PCBA revision string (8 bytes max)
            model_num: Model number (uint32)
        """
        super().__init__(transaction_id)
        self.arm_sw_ver = arm_sw_ver
        self.msp_sw_ver = msp_sw_ver
        self.config_a_bits = config_a_bits
        self.config_b_bits = config_b_bits
        self.serial_num = serial_num
        self.part_num = part_num
        self.pump_rev = pump_rev
        self.pcba_sn = pcba_sn
        self.pcba_rev = pcba_rev
        self.model_num = model_num

    def parse_payload(self, payload: bytes) -> None:
        """Parse version fields from payload.

        Implements exact byte parsing from Java PumpVersionResponse.parse():
        - Validates size is 48 bytes
        - Reads each field in sequence using proper offsets and types
        - String fields are 8 bytes each (null-padded)

        Args:
            payload: Raw payload bytes (must be exactly 48 bytes)

        Raises:
            ValueError: If payload size is not 48 bytes
        """
        if len(payload) != 48:
            raise ValueError(f"Invalid payload size: expected 48 bytes, got {len(payload)}")

        # Parse in exact order from Java source
        self.arm_sw_ver = read_uint32_le(payload, 0)
        self.msp_sw_ver = read_uint32_le(payload, 4)
        self.config_a_bits = read_uint32_le(payload, 8)
        self.config_b_bits = read_uint32_le(payload, 12)
        self.serial_num = read_uint32_le(payload, 16)
        self.part_num = read_uint32_le(payload, 20)
        self.pump_rev = read_string(payload, 24, 8)
        self.pcba_sn = read_uint32_le(payload, 32)
        self.pcba_rev = read_string(payload, 36, 8)
        self.model_num = read_uint32_le(payload, 44)

    def build_payload(self) -> bytes:
        """Build version payload.

        Implements exact buildCargo() logic from Java:
        - Converts each uint32 to 4-byte little-endian
        - Converts strings to 8-byte fixed-length padded format
        - Combines all bytes in order

        Returns:
            48-byte payload
        """
        return (
            write_uint32_le(self.arm_sw_ver)  # [0-3]
            + write_uint32_le(self.msp_sw_ver)  # [4-7]
            + write_uint32_le(self.config_a_bits)  # [8-11]
            + write_uint32_le(self.config_b_bits)  # [12-15]
            + write_uint32_le(self.serial_num)  # [16-19]
            + write_uint32_le(self.part_num)  # [20-23]
            + write_string(self.pump_rev, 8)  # [24-31]
            + write_uint32_le(self.pcba_sn)  # [32-35]
            + write_string(self.pcba_rev, 8)  # [36-43]
            + write_uint32_le(self.model_num)  # [44-47]
        )


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
