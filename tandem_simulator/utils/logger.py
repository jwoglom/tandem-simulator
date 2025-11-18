"""Structured logging infrastructure for the Tandem pump simulator.

This module provides logging utilities for tracking BLE events, protocol
messages, and system operations.
"""

import logging
import sys
from typing import Optional
from datetime import datetime


class SimulatorLogger:
    """Structured logger for the Tandem pump simulator."""

    def __init__(self, name: str = "tandem_simulator", level: int = logging.INFO):
        """Initialize the logger.

        Args:
            name: Logger name
            level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create console handler with formatting
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_ble_event(self, event_type: str, details: dict):
        """Log a BLE event.

        Args:
            event_type: Type of BLE event (e.g., 'connection', 'disconnection', 'read', 'write')
            details: Dictionary containing event details
        """
        self.logger.info(f"BLE Event [{event_type}]: {details}")

    def log_characteristic_read(self, char_uuid: str, value: bytes):
        """Log a characteristic read operation.

        Args:
            char_uuid: Characteristic UUID
            value: Value read from the characteristic
        """
        hex_value = value.hex() if value else "empty"
        self.logger.debug(f"Characteristic Read [{char_uuid}]: {hex_value}")

    def log_characteristic_write(self, char_uuid: str, value: bytes):
        """Log a characteristic write operation.

        Args:
            char_uuid: Characteristic UUID
            value: Value written to the characteristic
        """
        hex_value = value.hex() if value else "empty"
        self.logger.debug(f"Characteristic Write [{char_uuid}]: {hex_value}")

    def log_connection(self, device_address: Optional[str] = None):
        """Log a device connection.

        Args:
            device_address: Address of the connected device
        """
        self.logger.info(f"Device connected: {device_address or 'Unknown'}")

    def log_disconnection(self, device_address: Optional[str] = None):
        """Log a device disconnection.

        Args:
            device_address: Address of the disconnected device
        """
        self.logger.info(f"Device disconnected: {device_address or 'Unknown'}")

    def log_message(self, direction: str, opcode: int, payload: bytes):
        """Log a protocol message.

        Args:
            direction: 'sent' or 'received'
            opcode: Message opcode
            payload: Message payload
        """
        self.logger.debug(
            f"Message {direction} - Opcode: 0x{opcode:02X}, "
            f"Payload: {payload.hex() if payload else 'empty'}"
        )

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)


# Global logger instance
_default_logger: Optional[SimulatorLogger] = None


def get_logger(name: str = "tandem_simulator") -> SimulatorLogger:
    """Get or create the default logger instance.

    Args:
        name: Logger name

    Returns:
        SimulatorLogger instance
    """
    global _default_logger
    if _default_logger is None:
        _default_logger = SimulatorLogger(name)
    return _default_logger
