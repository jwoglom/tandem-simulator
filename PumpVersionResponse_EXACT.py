"""Pump Version Response message - EXACT implementation from PumpX2 Java source.

This module implements PumpVersionResponse as defined in:
https://github.com/jwoglom/pumpX2/blob/main/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/currentStatus/PumpVersionResponse.java

Message Properties:
- Opcode: 85 (0x55)
- Type: RESPONSE
- Payload Size: 48 bytes (fixed)

Field Layout (48 bytes total):
- [0-3]    armSwVer      (uint32 LE)
- [4-7]    mspSwVer      (uint32 LE)
- [8-11]   configABits   (uint32 LE)
- [12-15]  configBBits   (uint32 LE)
- [16-19]  serialNum     (uint32 LE)
- [20-23]  partNum       (uint32 LE)
- [24-31]  pumpRev       (8-byte fixed string)
- [32-35]  pcbaSN        (uint32 LE)
- [36-43]  pcbaRev       (8-byte fixed string)
- [44-47]  modelNum      (uint32 LE)
"""

import struct
from typing import Optional


# Utility functions matching Java Bytes helper class
def read_uint32_le(data: bytes, offset: int = 0) -> int:
    """Read a 32-bit unsigned integer in little-endian format.

    Matches: Bytes.readUint32(data, offset)

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from

    Returns:
        Unsigned 32-bit integer
    """
    return struct.unpack_from("<I", data, offset)[0]


def write_uint32_le(value: int) -> bytes:
    """Write a 32-bit unsigned integer in little-endian format.

    Matches: Bytes.toUint32(value)

    Args:
        value: Integer value to encode (0-4294967295)

    Returns:
        4 bytes in little-endian format
    """
    return struct.pack("<I", value & 0xFFFFFFFF)


def read_string(data: bytes, offset: int, length: int) -> str:
    """Read a fixed-length string.

    Matches: Bytes.readString(data, offset, length)

    Args:
        data: Raw bytes
        offset: Byte offset to start reading from
        length: Number of bytes to read

    Returns:
        String (null-terminated, trailing nulls stripped)
    """
    raw_bytes = data[offset : offset + length]
    # Strip null terminators and decode
    return raw_bytes.rstrip(b'\x00').decode('utf-8', errors='ignore')


def write_string(value: str, length: int) -> bytes:
    """Write a string with fixed-length padding.

    Matches: Bytes.writeString(value, length)

    Args:
        value: String to encode
        length: Total length (pads with null bytes if needed)

    Returns:
        Fixed-length bytes (padded with nulls if necessary)
    """
    encoded = value.encode('utf-8', errors='ignore')
    # Pad to length with null bytes
    if len(encoded) < length:
        encoded = encoded + b'\x00' * (length - len(encoded))
    return encoded[:length]


def combine(*byte_arrays) -> bytes:
    """Combine multiple byte arrays.

    Matches: Bytes.combine(...)

    Args:
        *byte_arrays: Variable number of byte objects to combine

    Returns:
        Combined bytes
    """
    result = b''
    for ba in byte_arrays:
        result += ba
    return result


class PumpVersionResponse:
    """Pump version response message (Opcode 85).

    Provides firmware version and hardware information from the pump.
    """

    opcode = 85  # Type: RESPONSE
    payload_size = 48  # Fixed 48-byte payload

    def __init__(
        self,
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
        """Initialize PumpVersionResponse with exact field names from Java.

        Args:
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

    @staticmethod
    def parse(raw: bytes) -> "PumpVersionResponse":
        """Parse payload bytes into PumpVersionResponse.

        Implements the exact parse() logic from Java:
        - Validates size is 48 bytes
        - Reads each field in sequence using proper offsets and types
        - String fields are 8 bytes each (null-padded)

        Args:
            raw: Raw payload bytes (must be exactly 48 bytes)

        Returns:
            Parsed PumpVersionResponse instance

        Raises:
            ValueError: If payload size is not 48 bytes
        """
        if len(raw) != 48:
            raise ValueError(
                f"Invalid payload size: expected 48 bytes, got {len(raw)}"
            )

        # Parse in exact order from Java source
        arm_sw_ver = read_uint32_le(raw, 0)
        msp_sw_ver = read_uint32_le(raw, 4)
        config_a_bits = read_uint32_le(raw, 8)
        config_b_bits = read_uint32_le(raw, 12)
        serial_num = read_uint32_le(raw, 16)
        part_num = read_uint32_le(raw, 20)
        pump_rev = read_string(raw, 24, 8)
        pcba_sn = read_uint32_le(raw, 32)
        pcba_rev = read_string(raw, 36, 8)
        model_num = read_uint32_le(raw, 44)

        return PumpVersionResponse(
            arm_sw_ver=arm_sw_ver,
            msp_sw_ver=msp_sw_ver,
            config_a_bits=config_a_bits,
            config_b_bits=config_b_bits,
            serial_num=serial_num,
            part_num=part_num,
            pump_rev=pump_rev,
            pcba_sn=pcba_sn,
            pcba_rev=pcba_rev,
            model_num=model_num,
        )

    @staticmethod
    def build_cargo(
        arm_sw_ver: int,
        msp_sw_ver: int,
        config_a_bits: int,
        config_b_bits: int,
        serial_num: int,
        part_num: int,
        pump_rev: str,
        pcba_sn: int,
        pcba_rev: str,
        model_num: int,
    ) -> bytes:
        """Build payload bytes from fields.

        Implements the exact buildCargo() logic from Java:
        - Converts each uint32 to 4-byte little-endian
        - Converts strings to 8-byte fixed-length padded format
        - Combines all bytes in order

        Args:
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

        Returns:
            48-byte payload (Bytes.combine equivalent)
        """
        return combine(
            write_uint32_le(arm_sw_ver),      # [0-3]
            write_uint32_le(msp_sw_ver),      # [4-7]
            write_uint32_le(config_a_bits),   # [8-11]
            write_uint32_le(config_b_bits),   # [12-15]
            write_uint32_le(serial_num),      # [16-19]
            write_uint32_le(part_num),        # [20-23]
            write_string(pump_rev, 8),        # [24-31]
            write_uint32_le(pcba_sn),         # [32-35]
            write_string(pcba_rev, 8),        # [36-43]
            write_uint32_le(model_num),       # [44-47]
        )

    def build_payload(self) -> bytes:
        """Build payload from instance fields.

        Convenience method wrapping buildCargo() with instance values.

        Returns:
            48-byte payload
        """
        return self.build_cargo(
            arm_sw_ver=self.arm_sw_ver,
            msp_sw_ver=self.msp_sw_ver,
            config_a_bits=self.config_a_bits,
            config_b_bits=self.config_b_bits,
            serial_num=self.serial_num,
            part_num=self.part_num,
            pump_rev=self.pump_rev,
            pcba_sn=self.pcba_sn,
            pcba_rev=self.pcba_rev,
            model_num=self.model_num,
        )

    # Getter methods matching Java implementation
    def get_arm_sw_ver(self) -> int:
        """Get ARM software version."""
        return self.arm_sw_ver

    def get_msp_sw_ver(self) -> int:
        """Get MSP software version."""
        return self.msp_sw_ver

    def get_config_a_bits(self) -> int:
        """Get configuration A bits."""
        return self.config_a_bits

    def get_config_b_bits(self) -> int:
        """Get configuration B bits."""
        return self.config_b_bits

    def get_serial_num(self) -> int:
        """Get serial number."""
        return self.serial_num

    def get_part_num(self) -> int:
        """Get part number."""
        return self.part_num

    def get_pump_rev(self) -> str:
        """Get pump revision string."""
        return self.pump_rev

    def get_pcba_sn(self) -> int:
        """Get PCBA serial number."""
        return self.pcba_sn

    def get_pcba_rev(self) -> str:
        """Get PCBA revision string."""
        return self.pcba_rev

    def get_model_num(self) -> int:
        """Get model number."""
        return self.model_num

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PumpVersionResponse("
            f"opcode={self.opcode}, "
            f"arm_sw_ver=0x{self.arm_sw_ver:08X}, "
            f"msp_sw_ver=0x{self.msp_sw_ver:08X}, "
            f"config_a_bits=0x{self.config_a_bits:08X}, "
            f"config_b_bits=0x{self.config_b_bits:08X}, "
            f"serial_num={self.serial_num}, "
            f"part_num={self.part_num}, "
            f"pump_rev={repr(self.pump_rev)}, "
            f"pcba_sn={self.pcba_sn}, "
            f"pcba_rev={repr(self.pcba_rev)}, "
            f"model_num={self.model_num})"
        )


# Example usage and test cases
if __name__ == "__main__":
    # Test 1: Create instance with values
    print("Test 1: Create and serialize")
    response = PumpVersionResponse(
        arm_sw_ver=0x01020304,
        msp_sw_ver=0x05060708,
        config_a_bits=0x09000A00,
        config_b_bits=0x0B000C00,
        serial_num=12345,
        part_num=67890,
        pump_rev="T1.2.3",
        pcba_sn=11111,
        pcba_rev="V2.0.1",
        model_num=42,
    )
    payload = response.build_payload()
    print(f"Payload size: {len(payload)} bytes (expected 48)")
    print(f"Payload (hex): {payload.hex()}")
    print(f"Response: {response}\n")

    # Test 2: Parse payload
    print("Test 2: Parse payload")
    parsed = PumpVersionResponse.parse(payload)
    print(f"Parsed: {parsed}")
    print(f"arm_sw_ver match: {parsed.arm_sw_ver == response.arm_sw_ver}")
    print(f"pump_rev match: {parsed.pump_rev == response.pump_rev}")
    print(f"model_num match: {parsed.model_num == response.model_num}\n")

    # Test 3: Round-trip test
    print("Test 3: Round-trip verification")
    payload2 = parsed.build_payload()
    print(f"Payloads match: {payload == payload2}")
    print(f"Payload identical: {payload.hex() == payload2.hex()}\n")

    # Test 4: Byte offset verification
    print("Test 4: Byte offset verification")
    test_payload = PumpVersionResponse.build_cargo(
        arm_sw_ver=0xAAAABBBB,
        msp_sw_ver=0xCCCCDDDD,
        config_a_bits=0x11112222,
        config_b_bits=0x33334444,
        serial_num=0x55556666,
        part_num=0x77778888,
        pump_rev="abcdefgh",
        pcba_sn=0x99990000,
        pcba_rev="ijklmnop",
        model_num=0xAABBCCDD,
    )
    print(f"Total size: {len(test_payload)} bytes")
    print(f"arm_sw_ver @ [0:4]: {test_payload[0:4].hex()}")
    print(f"msp_sw_ver @ [4:8]: {test_payload[4:8].hex()}")
    print(f"pump_rev @ [24:32]: {test_payload[24:32]}")
    print(f"pcba_sn @ [32:36]: {test_payload[32:36].hex()}")
    print(f"model_num @ [44:48]: {test_payload[44:48].hex()}")
