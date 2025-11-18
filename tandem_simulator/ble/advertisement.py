"""BLE advertisement management for Tandem pump simulator.

This module handles broadcasting the pump as a discoverable BLE peripheral
with the correct service UUIDs and device name.
"""

from typing import Optional
from tandem_simulator.utils.logger import get_logger
from tandem_simulator.utils.constants import (
    PUMP_SERVICE_UUID,
    DEVICE_NAME_PREFIX,
    DEFAULT_SERIAL_NUMBER,
)

logger = get_logger()


class Advertisement:
    """Manages BLE advertisement for the Tandem pump simulator.

    The advertisement broadcasts the device name and PUMP_SERVICE_UUID
    to make the simulator discoverable to Android/iOS apps.
    """

    def __init__(self, serial_number: Optional[str] = None):
        """Initialize the advertisement.

        Args:
            serial_number: Pump serial number (default: DEFAULT_SERIAL_NUMBER)
        """
        self.serial_number = serial_number or DEFAULT_SERIAL_NUMBER
        self.device_name = f"{DEVICE_NAME_PREFIX} {self.serial_number}"
        self.is_advertising = False

        logger.info(f"Advertisement initialized: {self.device_name}")

    def start(self):
        """Start broadcasting the BLE advertisement.

        This method will register the advertisement with BlueZ via D-Bus
        and begin broadcasting.
        """
        # TODO: Implement D-Bus advertisement registration
        logger.info(f"Starting advertisement: {self.device_name}")
        logger.info(f"Advertising service UUID: {PUMP_SERVICE_UUID}")
        self.is_advertising = True

    def stop(self):
        """Stop broadcasting the BLE advertisement."""
        # TODO: Implement D-Bus advertisement unregistration
        logger.info("Stopping advertisement")
        self.is_advertising = False

    def update_serial_number(self, serial_number: str):
        """Update the serial number and device name.

        Args:
            serial_number: New serial number
        """
        self.serial_number = serial_number
        self.device_name = f"{DEVICE_NAME_PREFIX} {self.serial_number}"

        if self.is_advertising:
            logger.info("Restarting advertisement with new device name")
            self.stop()
            self.start()
