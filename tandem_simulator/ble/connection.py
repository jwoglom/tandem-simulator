"""BLE connection management for Tandem pump simulator.

This module handles tracking connected central devices, managing MTU negotiation,
and handling connection/disconnection events.
"""

from typing import Optional, Dict
from dataclasses import dataclass
from tandem_simulator.utils.logger import get_logger

logger = get_logger()


@dataclass
class ConnectionInfo:
    """Information about a connected BLE device."""

    device_address: str
    device_name: Optional[str] = None
    mtu: int = 23  # Default BLE MTU
    bonded: bool = False
    connected_at: Optional[str] = None


class ConnectionManager:
    """Manages BLE connections and connection state.

    Tracks connected central devices, handles connection events,
    and manages MTU negotiation.
    """

    def __init__(self):
        """Initialize the connection manager."""
        self.connections: Dict[str, ConnectionInfo] = {}
        self.current_connection: Optional[ConnectionInfo] = None
        logger.info("Connection manager initialized")

    def handle_connection(self, device_address: str, device_name: Optional[str] = None):
        """Handle a new device connection.

        Args:
            device_address: BLE address of the connected device
            device_name: Name of the connected device (optional)
        """
        from datetime import datetime

        connection_info = ConnectionInfo(
            device_address=device_address,
            device_name=device_name,
            connected_at=datetime.now().isoformat()
        )

        self.connections[device_address] = connection_info
        self.current_connection = connection_info

        logger.log_connection(device_address)
        logger.info(f"Connected device: {device_name or 'Unknown'} ({device_address})")

    def handle_disconnection(self, device_address: str):
        """Handle device disconnection.

        Args:
            device_address: BLE address of the disconnected device
        """
        if device_address in self.connections:
            connection_info = self.connections.pop(device_address)
            logger.log_disconnection(device_address)
            logger.info(f"Disconnected device: {connection_info.device_name or 'Unknown'}")

            if self.current_connection and self.current_connection.device_address == device_address:
                self.current_connection = None

    def handle_mtu_exchange(self, device_address: str, mtu: int):
        """Handle MTU exchange negotiation.

        Args:
            device_address: BLE address of the device
            mtu: Negotiated MTU value
        """
        if device_address in self.connections:
            self.connections[device_address].mtu = mtu
            logger.info(f"MTU negotiated for {device_address}: {mtu} bytes")

    def get_connection(self, device_address: str) -> Optional[ConnectionInfo]:
        """Get connection information for a device.

        Args:
            device_address: BLE address of the device

        Returns:
            ConnectionInfo if device is connected, None otherwise
        """
        return self.connections.get(device_address)

    def is_connected(self) -> bool:
        """Check if any device is currently connected.

        Returns:
            True if at least one device is connected
        """
        return len(self.connections) > 0

    def get_current_mtu(self) -> int:
        """Get the MTU of the current connection.

        Returns:
            MTU value (default 23 if no connection)
        """
        if self.current_connection:
            return self.current_connection.mtu
        return 23
