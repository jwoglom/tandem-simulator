"""Base message classes for Tandem pump protocol.

This module defines the base Message class and message registry for
parsing and constructing Tandem protocol messages.

Message Structure:
- Header: 3 bytes (opcode, transaction ID, payload length)
- Payload: Variable length cargo data
- Authentication (for signed messages): 24 bytes (HMAC-SHA1 + timestamp)
- CRC16: 2 bytes appended to the complete packet

Milestone 2 deliverable.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Type

from tandem_simulator.utils.constants import HMAC_SIZE, MESSAGE_HEADER_SIZE


@dataclass
class MessageHeader:
    """Tandem protocol message header (3 bytes)."""

    opcode: int  # 1 byte
    transaction_id: int  # 1 byte
    payload_length: int  # 1 byte

    @classmethod
    def parse(cls, data: bytes) -> "MessageHeader":
        """Parse a message header from bytes.

        Args:
            data: Raw header data (at least 3 bytes)

        Returns:
            Parsed MessageHeader instance

        Raises:
            ValueError: If data is too short
        """
        if len(data) < MESSAGE_HEADER_SIZE:
            raise ValueError(
                f"Insufficient data for header: got {len(data)} bytes, need {MESSAGE_HEADER_SIZE}"
            )

        return cls(
            opcode=data[0],
            transaction_id=data[1],
            payload_length=data[2],
        )

    def serialize(self) -> bytes:
        """Serialize the header to bytes.

        Returns:
            3-byte header
        """
        return bytes([self.opcode, self.transaction_id, self.payload_length])


class Message:
    """Base class for all Tandem protocol messages."""

    opcode: int = 0x00

    def __init__(self, transaction_id: int = 0):
        """Initialize a message.

        Args:
            transaction_id: Transaction ID for this message
        """
        self.transaction_id = transaction_id
        self.payload: bytes = b""
        self.is_signed: bool = False
        self.hmac_data: Optional[bytes] = None  # 24 bytes for signed messages

    @classmethod
    def parse(cls, data: bytes) -> "Message":
        """Parse a message from bytes.

        This method parses the header and payload. Subclasses should override
        parse_payload() to handle their specific payload format.

        Args:
            data: Raw message data (header + payload, no CRC)

        Returns:
            Parsed Message instance

        Raises:
            ValueError: If data is invalid
        """
        if len(data) < MESSAGE_HEADER_SIZE:
            raise ValueError(
                f"Insufficient data for message: got {len(data)} bytes, "
                f"need at least {MESSAGE_HEADER_SIZE}"
            )

        # Parse header
        header = MessageHeader.parse(data)

        # Create message instance
        msg = cls(transaction_id=header.transaction_id)

        # Set opcode from header (important for base Message class)
        # Subclasses have opcode as a class attribute, but base Message needs instance attribute
        if cls == Message:
            msg.opcode = header.opcode

        # Extract payload
        payload_start = MESSAGE_HEADER_SIZE
        payload_end = payload_start + header.payload_length

        if len(data) < payload_end:
            raise ValueError(
                f"Insufficient data for payload: got {len(data)} bytes, need {payload_end}"
            )

        msg.payload = data[payload_start:payload_end]

        # Check for HMAC signature (24 bytes after payload)
        if len(data) >= payload_end + HMAC_SIZE:
            msg.is_signed = True
            msg.hmac_data = data[payload_end : payload_end + HMAC_SIZE]

        # Parse payload (can be overridden by subclasses)
        msg.parse_payload(msg.payload)

        return msg

    def parse_payload(self, payload: bytes) -> None:
        """Parse the message payload.

        Subclasses should override this to parse their specific payload format.

        Args:
            payload: Raw payload bytes
        """
        # Default implementation does nothing
        pass

    def build_payload(self) -> bytes:
        """Build the message payload.

        Subclasses should override this to build their specific payload format.

        Returns:
            Payload bytes
        """
        # Default implementation returns the raw payload
        return self.payload

    def serialize(self) -> bytes:
        """Serialize the message to bytes (without CRC).

        Returns:
            Serialized message data (header + payload + optional HMAC)
        """
        # Build payload
        payload = self.build_payload()

        # Create header
        header = MessageHeader(
            opcode=self.opcode,
            transaction_id=self.transaction_id,
            payload_length=len(payload),
        )

        # Serialize: header + payload
        data = header.serialize() + payload

        # Add HMAC if signed
        if self.is_signed and self.hmac_data:
            data += self.hmac_data

        return data

    def is_request(self) -> bool:
        """Check if this is a request message (even opcode).

        Returns:
            True if request, False if response
        """
        return self.opcode % 2 == 0

    def is_response(self) -> bool:
        """Check if this is a response message (odd opcode).

        Returns:
            True if response, False if request
        """
        return self.opcode % 2 == 1

    def __repr__(self) -> str:
        """String representation of the message."""
        return (
            f"{self.__class__.__name__}(opcode=0x{self.opcode:02X}, "
            f"transaction_id={self.transaction_id}, "
            f"payload_length={len(self.payload)}, "
            f"is_signed={self.is_signed})"
        )


class MessageRegistry:
    """Registry mapping opcodes to message classes."""

    _registry: Dict[int, Type[Message]] = {}

    @classmethod
    def register(cls, opcode: int, message_class: Type[Message]):
        """Register a message class for an opcode.

        Args:
            opcode: Message opcode
            message_class: Message class to register
        """
        cls._registry[opcode] = message_class

    @classmethod
    def get_message_class(cls, opcode: int) -> Optional[Type[Message]]:
        """Get the message class for an opcode.

        Args:
            opcode: Message opcode

        Returns:
            Message class if registered, None otherwise
        """
        return cls._registry.get(opcode)

    @classmethod
    def parse_message(cls, data: bytes) -> Message:
        """Parse a message using the registry.

        Args:
            data: Raw message data (header + payload, no CRC)

        Returns:
            Parsed Message instance (specific subclass if registered)

        Raises:
            ValueError: If data is invalid
        """
        if len(data) < MESSAGE_HEADER_SIZE:
            raise ValueError("Insufficient data for message header")

        # Extract opcode
        opcode = data[0]

        # Get message class from registry
        message_class = cls.get_message_class(opcode)

        if message_class is None:
            # Unknown message type - use base Message class
            message_class = Message

        # Parse using the appropriate class
        return message_class.parse(data)
