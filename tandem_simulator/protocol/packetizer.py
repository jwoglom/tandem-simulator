"""Packet assembly and disassembly for Tandem pump protocol.

This module handles chunking messages into BLE-sized packets and
reassembling received packets into complete messages.

Message Format:
- Header: 3 bytes (opcode, transaction_id, payload_length)
- Payload: Variable length
- HMAC: 24 bytes (for signed messages)
- CRC16: 2 bytes at the end

Chunking Strategy:
- Messages are split into MTU-sized chunks (18 bytes default, 40 for control)
- Reassembly uses header to determine total message size
- CRC is validated after complete message is reassembled

Milestone 2 deliverable.
"""

from typing import List, Optional

from tandem_simulator.protocol.crc import verify_and_strip_crc16
from tandem_simulator.utils.constants import (
    CONTROL_CHUNK_SIZE,
    DEFAULT_CHUNK_SIZE,
    MESSAGE_HEADER_SIZE,
)


class Packetizer:
    """Handles packet assembly and disassembly for the Tandem protocol."""

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """Initialize the packetizer.

        Args:
            chunk_size: Size of each packet chunk in bytes (default 18)
        """
        self.chunk_size = chunk_size
        self.reassembly_buffer: bytes = b""
        self.expected_message_size: Optional[int] = None

    def chunk_message(self, message: bytes) -> List[bytes]:
        """Split a message into BLE-sized chunks.

        The message should already include CRC16 checksum.

        Args:
            message: Complete message with CRC to chunk

        Returns:
            List of message chunks
        """
        chunks = []
        offset = 0

        while offset < len(message):
            # Extract chunk
            chunk_end = min(offset + self.chunk_size, len(message))
            chunk = message[offset:chunk_end]
            chunks.append(chunk)
            offset = chunk_end

        return chunks

    def add_chunk(self, chunk: bytes) -> Optional[bytes]:
        """Add a received chunk to the reassembly buffer.

        Returns the complete message (without CRC) if reassembly is complete
        and CRC validation passes.

        Args:
            chunk: Received chunk

        Returns:
            Complete message (without CRC) if reassembly is complete, None otherwise

        Raises:
            ValueError: If CRC validation fails
        """
        # Add chunk to buffer
        self.reassembly_buffer += chunk

        # If we don't know the expected size yet, try to parse the header
        if (
            self.expected_message_size is None
            and len(self.reassembly_buffer) >= MESSAGE_HEADER_SIZE
        ):
            # Parse header to determine message size
            payload_length = self.reassembly_buffer[2]  # Third byte is payload length

            # Calculate total message size:
            # Header (3) + Payload (N) + CRC (2)
            # Note: HMAC is part of the payload length if present
            self.expected_message_size = MESSAGE_HEADER_SIZE + payload_length + 2  # +2 for CRC

        # Check if we have the complete message
        if (
            self.expected_message_size is not None
            and len(self.reassembly_buffer) >= self.expected_message_size
        ):
            # Extract the complete message
            complete_message_with_crc = self.reassembly_buffer[: self.expected_message_size]

            # Verify CRC and strip it
            is_valid, message_data = verify_and_strip_crc16(complete_message_with_crc)

            if not is_valid:
                # Reset and raise error
                error_msg = "CRC validation failed for reassembled message"
                self.reset()
                raise ValueError(error_msg)

            # Reset the buffer (keep any extra bytes for next message)
            self.reassembly_buffer = self.reassembly_buffer[self.expected_message_size :]
            self.expected_message_size = None

            return message_data

        # Message not yet complete
        return None

    def reset(self):
        """Reset the reassembly buffer."""
        self.reassembly_buffer = b""
        self.expected_message_size = None

    def has_pending_data(self) -> bool:
        """Check if there is data in the reassembly buffer.

        Returns:
            True if buffer is not empty
        """
        return len(self.reassembly_buffer) > 0

    def get_buffer_size(self) -> int:
        """Get current size of reassembly buffer.

        Returns:
            Number of bytes in buffer
        """
        return len(self.reassembly_buffer)


class ControlPacketizer(Packetizer):
    """Packetizer for control messages with larger chunk size (40 bytes)."""

    def __init__(self):
        """Initialize control packetizer with 40-byte chunks."""
        super().__init__(chunk_size=CONTROL_CHUNK_SIZE)
