"""Request handler framework for Tandem pump simulator.

This module routes incoming requests to appropriate handlers and
manages response queue.

Milestone 4 deliverable.
"""

import logging
from typing import Callable, Dict, Optional

from tandem_simulator.handlers.control import ControlHandlers
from tandem_simulator.handlers.status import StatusHandlers
from tandem_simulator.protocol.message import Message
from tandem_simulator.state.pump_state import PumpStateManager

logger = logging.getLogger(__name__)


class RequestHandler:
    """Routes requests to appropriate handlers."""

    def __init__(self, state_manager: PumpStateManager):
        """Initialize the request handler.

        Args:
            state_manager: Pump state manager instance
        """
        self.state_manager = state_manager
        self.handlers: Dict[int, Callable] = {}

        # Initialize handler classes
        self.status_handlers = StatusHandlers(state_manager)
        self.control_handlers = ControlHandlers(state_manager)

        # Register status request handlers
        self._register_status_handlers()

    def _register_status_handlers(self):
        """Register all status request handlers."""
        # API Version (opcode 32)
        self.register_handler(32, self.status_handlers.handle_api_version_request)

        # Pump Version (opcode 84)
        self.register_handler(84, self.status_handlers.handle_pump_version_request)

        # Current Battery V1 (opcode 52)
        self.register_handler(52, self.status_handlers.handle_battery_status_request)

        # Current Basal Status (opcode 40)
        self.register_handler(40, self.status_handlers.handle_basal_status_request)

        # Current Bolus Status (opcode 44)
        self.register_handler(44, self.status_handlers.handle_bolus_status_request)

        # Insulin Status (opcode 36)
        self.register_handler(36, self.status_handlers.handle_insulin_status_request)

    def register_handler(self, opcode: int, handler: Callable):
        """Register a handler for an opcode.

        Args:
            opcode: Message opcode
            handler: Handler function
        """
        self.handlers[opcode] = handler
        logger.debug(f"Registered handler for opcode {opcode}")

    def handle_request(self, message: Message) -> Optional[Message]:
        """Handle a request message.

        Args:
            message: Request message

        Returns:
            Response message or None
        """
        handler = self.handlers.get(message.opcode)
        if handler:
            logger.debug(f"Handling request with opcode {message.opcode}")
            try:
                return handler(message)
            except Exception as e:
                logger.error(
                    f"Error handling request with opcode {message.opcode}: {e}",
                    exc_info=True,
                )
                return None
        else:
            logger.warning(f"No handler registered for opcode {message.opcode}")
            return None
