"""Current bolus status response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import (
    read_uint16_le,
    read_uint32_le,
    write_uint16_le,
    write_uint32_le,
)


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


# Register the message
MessageRegistry.register(45, CurrentBolusStatusResponse)
