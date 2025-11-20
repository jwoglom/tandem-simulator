"""Pump version response message."""

from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.messages.util.bytes import (
    read_string,
    read_uint32_le,
    write_string,
    write_uint32_le,
)


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


# Register the message
MessageRegistry.register(85, PumpVersionResponse)
