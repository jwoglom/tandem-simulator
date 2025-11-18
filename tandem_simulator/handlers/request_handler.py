"""Request handler framework for Tandem pump simulator.

This module routes incoming requests to appropriate handlers and
manages response queue.

Milestone 4 deliverable (stub).
"""

from typing import Callable, Dict, Optional

from tandem_simulator.protocol.message import Message


class RequestHandler:
    """Routes requests to appropriate handlers."""

    def __init__(self):
        """Initialize the request handler."""
        self.handlers: Dict[int, Callable] = {}

    def register_handler(self, opcode: int, handler: Callable):
        """Register a handler for an opcode.

        Args:
            opcode: Message opcode
            handler: Handler function
        """
        self.handlers[opcode] = handler

    def handle_request(self, message: Message) -> Optional[Message]:
        """Handle a request message.

        Args:
            message: Request message

        Returns:
            Response message or None
        """
        handler = self.handlers.get(message.opcode)
        if handler:
            return handler(message)
        return None
