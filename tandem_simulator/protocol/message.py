"""Base message classes for Tandem pump protocol.

This module defines the base Message class and message registry for
parsing and constructing Tandem protocol messages.

Milestone 2 deliverable (stub).
"""

from dataclasses import dataclass
from typing import Dict, Optional, Type


@dataclass
class MessageHeader:
    """Tandem protocol message header."""

    opcode: int  # 1 byte
    transaction_id: int  # 1 byte
    payload_length: int  # 1 byte


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

    @classmethod
    def parse(cls, data: bytes) -> "Message":
        """Parse a message from bytes.

        Args:
            data: Raw message data

        Returns:
            Parsed Message instance

        Raises:
            ValueError: If data is invalid
        """
        # TODO: Implement message parsing
        raise NotImplementedError("Message parsing not yet implemented")

    def serialize(self) -> bytes:
        """Serialize the message to bytes.

        Returns:
            Serialized message data
        """
        # TODO: Implement message serialization
        raise NotImplementedError("Message serialization not yet implemented")

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
