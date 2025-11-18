"""Current Bolus Status Response message implementation.

This module implements the CurrentBolusStatusResponse message (Opcode 45)
exactly as defined in the pumpX2 project:
https://github.com/jwoglom/pumpX2/blob/main/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/currentStatus/CurrentBolusStatusResponse.java

Milestone 4 implementation.
"""

import struct
from enum import Enum
from typing import Optional, Set
from tandem_simulator.protocol.message import Message, MessageRegistry


# =============================================================================
# Utility Functions for Little-Endian Encoding/Decoding
# =============================================================================


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


# =============================================================================
# CurrentBolusStatus Enum
# =============================================================================


class CurrentBolusStatus(Enum):
    """Enum representing the current bolus delivery status.

    Corresponds to the CurrentBolusStatus nested enum in the Java implementation.
    """

    REQUESTING = 2
    """Bolus delivery is being requested/prepared."""

    DELIVERING = 1
    """Bolus is currently being delivered."""

    ALREADY_DELIVERED_OR_INVALID = 0
    """Bolus has been delivered or is invalid (no active bolus)."""

    @classmethod
    def from_id(cls, status_id: int) -> Optional["CurrentBolusStatus"]:
        """Get enum value from status ID.

        Args:
            status_id: Status ID (0, 1, or 2)

        Returns:
            Corresponding CurrentBolusStatus enum value, or None if invalid
        """
        for status in cls:
            if status.value == status_id:
                return status
        return None


# =============================================================================
# Current Bolus Status Request (Opcode 44)
# =============================================================================


class CurrentBolusStatusRequest(Message):
    """Current bolus status request message.

    Opcode: 44 (0x2C)
    Payload: 0 bytes (empty)

    Requests current bolus delivery status from the pump.
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


# =============================================================================
# Current Bolus Status Response (Opcode 45)
# =============================================================================


class CurrentBolusStatusResponse(Message):
    """Current bolus status response message.

    Opcode: 45 (0x2D)
    Payload: 15 bytes

    Field layout (exact byte offsets from Java implementation):
    - Byte 0: statusId (int, 1 byte)
    - Bytes 1-2: bolusId (short, 2 bytes, little-endian)
    - Bytes 3-4: padding (2 zero bytes)
    - Bytes 5-8: timestamp (uint32, 4 bytes, little-endian)
    - Bytes 9-12: requestedVolume (uint32, 4 bytes, little-endian)
    - Byte 13: bolusSourceId (int, 1 byte)
    - Byte 14: bolusTypeBitmask (int, 1 byte)

    Total: 15 bytes

    Response with current bolus delivery status.
    """

    opcode = 45

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
            # Byte 0: statusId (unsigned byte)
            self.status_id = payload[0]

            # Bytes 1-2: bolusId (unsigned short, little-endian)
            self.bolus_id = read_uint16_le(payload, 1)

            # Bytes 3-4: padding (skipped)
            # (2 zero bytes reserved in the Java implementation)

            # Bytes 5-8: timestamp (unsigned int, little-endian)
            self.timestamp = read_uint32_le(payload, 5)

            # Bytes 9-12: requestedVolume (unsigned int, little-endian)
            self.requested_volume = read_uint32_le(payload, 9)

            # Byte 13: bolusSourceId (unsigned byte)
            self.bolus_source_id = payload[13]

            # Byte 14: bolusTypeBitmask (unsigned byte)
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
            bytes([self.status_id])  # Byte 0: status
            + write_uint16_le(self.bolus_id)  # Bytes 1-2: bolus ID
            + bytes([0, 0])  # Bytes 3-4: padding (zero bytes)
            + write_uint32_le(self.timestamp)  # Bytes 5-8: timestamp
            + write_uint32_le(self.requested_volume)  # Bytes 9-12: requested volume
            + bytes([self.bolus_source_id])  # Byte 13: bolus source
            + bytes([self.bolus_type_bitmask])  # Byte 14: bolus type bitmask
        )

    # =============================================================================
    # Getters (matching Java implementation)
    # =============================================================================

    def get_status_id(self) -> int:
        """Get the raw status ID.

        Returns:
            Status ID (0, 1, or 2)
        """
        return self.status_id

    def get_status(self) -> Optional[CurrentBolusStatus]:
        """Get the current bolus status enum.

        Corresponds to Java getStatus() which calls
        CurrentBolusStatus.fromId(statusId).

        Returns:
            CurrentBolusStatus enum value, or None if invalid
        """
        return CurrentBolusStatus.from_id(self.status_id)

    def get_bolus_id(self) -> int:
        """Get the bolus identifier.

        Returns:
            Bolus ID (unsigned short, 0-65535)
        """
        return self.bolus_id

    def get_timestamp(self) -> int:
        """Get the timestamp.

        Note: In the Java implementation, this is converted to a Java Instant
        using Dates.fromJan12008EpochSecondsToDate(timestamp), which uses
        January 1, 2008 00:00:00 UTC as epoch zero.

        Returns:
            Timestamp in seconds since Jan 1, 2008 00:00:00 UTC
        """
        return self.timestamp

    def get_requested_volume(self) -> int:
        """Get the requested volume.

        Note: The raw value should be divided by 10000 to get insulin units.
        For example, 50000 = 5.00 units.

        Returns:
            Requested volume (insulin units * 10000)
        """
        return self.requested_volume

    def get_bolus_source_id(self) -> int:
        """Get the bolus source ID.

        Returns:
            Bolus source ID (unsigned byte)
        """
        return self.bolus_source_id

    def get_bolus_type_bitmask(self) -> int:
        """Get the bolus type bitmask.

        In the Java implementation, this is converted to a Set of
        BolusDeliveryHistoryLog.BolusType values using
        BolusType.fromBitmask(bolusTypeBitmask).

        Returns:
            Bolus type bitmask (unsigned byte)
        """
        return self.bolus_type_bitmask

    def is_valid(self) -> bool:
        """Check if the bolus status is valid.

        Corresponds to Java isValid():
        return !(getStatus() == CurrentBolusStatus.ALREADY_DELIVERED_OR_INVALID
                 && getBolusId() == 0 && getTimestamp() == 0);

        Returns True if:
        - Status is NOT ALREADY_DELIVERED_OR_INVALID, OR
        - Status is ALREADY_DELIVERED_OR_INVALID but bolusId OR timestamp is non-zero

        Returns:
            True if the bolus data is meaningful, False if it's empty/invalid
        """
        if (
            self.get_status() == CurrentBolusStatus.ALREADY_DELIVERED_OR_INVALID
            and self.bolus_id == 0
            and self.timestamp == 0
        ):
            return False
        return True


# =============================================================================
# Message Registration
# =============================================================================

MessageRegistry.register(CurrentBolusStatusRequest.opcode, CurrentBolusStatusRequest)
MessageRegistry.register(CurrentBolusStatusResponse.opcode, CurrentBolusStatusResponse)
