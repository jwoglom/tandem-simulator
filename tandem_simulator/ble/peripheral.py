"""Core BLE peripheral implementation for Tandem pump simulator.

This module implements the main BLE peripheral that integrates the GATT server,
advertisement, and connection management using BlueZ via D-Bus.
"""

from typing import Optional

import dbus
import dbus.mainloop.glib

try:
    from gi.repository import GLib
except ImportError:
    GLib = None  # type: ignore

from tandem_simulator.ble.advertisement import Advertisement
from tandem_simulator.ble.connection import ConnectionManager
from tandem_simulator.ble.gatt_server import GATTServer
from tandem_simulator.utils.constants import DEFAULT_SERIAL_NUMBER
from tandem_simulator.utils.logger import get_logger

logger = get_logger()


class BLEPeripheral:
    """BLE peripheral for Tandem pump simulator.

    This class integrates all BLE components and provides the main
    interface for running the pump simulator as a BLE peripheral.
    """

    def __init__(self, serial_number: Optional[str] = None):
        """Initialize the BLE peripheral.

        Args:
            serial_number: Pump serial number (default: DEFAULT_SERIAL_NUMBER)
        """
        self.serial_number = serial_number or DEFAULT_SERIAL_NUMBER
        self.running = False
        self.mainloop: Optional[GLib.MainLoop] = None

        # Initialize D-Bus main loop
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        # Initialize components
        self.gatt_server = GATTServer(self.serial_number)
        self.advertisement = Advertisement(self.serial_number)
        self.connection_manager = ConnectionManager()

        logger.info(f"BLE Peripheral initialized with serial number: {self.serial_number}")

    def start(self):
        """Start the BLE peripheral.

        This method will:
        1. Register the GATT server with BlueZ
        2. Start advertising
        3. Begin listening for connections
        """
        if self.running:
            logger.warning("BLE peripheral already running")
            return

        logger.info("Starting BLE peripheral...")

        try:
            # Register GATT server with BlueZ via D-Bus
            self.gatt_server.register()
            logger.debug("GATT server registered")

            # Start advertising
            self.advertisement.start()
            logger.debug("Advertisement started")

            # Set up connection event handlers
            self._setup_connection_handlers()

            self.running = True
            logger.info("BLE peripheral started successfully")
            logger.info(f"Device name: {self.advertisement.device_name}")
            logger.info("Waiting for connections...")

        except Exception as e:
            logger.error(f"Failed to start BLE peripheral: {e}")
            # Clean up on failure
            try:
                self.advertisement.stop()
                self.gatt_server.unregister()
            except Exception:
                pass
            raise

    def stop(self):
        """Stop the BLE peripheral.

        This method will:
        1. Stop advertising
        2. Disconnect all clients
        3. Unregister the GATT server
        """
        if not self.running:
            logger.warning("BLE peripheral not running")
            return

        logger.info("Stopping BLE peripheral...")

        try:
            # Stop advertising
            self.advertisement.stop()
            logger.debug("Advertisement stopped")

            # Disconnect all clients
            self._disconnect_all_clients()

            # Unregister GATT server from BlueZ
            self.gatt_server.unregister()
            logger.debug("GATT server unregistered")

            # Stop the main loop if running
            if self.mainloop and self.mainloop.is_running():
                self.mainloop.quit()
                self.mainloop = None

            self.running = False
            logger.info("BLE peripheral stopped")

        except Exception as e:
            logger.error(f"Error stopping BLE peripheral: {e}")
            self.running = False

    def run(self):
        """Run the BLE peripheral main loop.

        This method starts the peripheral and runs until interrupted.
        """
        try:
            self.start()

            if GLib is None:
                logger.error("GLib not available - cannot run main loop")
                logger.info("Install PyGObject: pip install PyGObject")
                return

            # Run D-Bus main loop
            logger.info("Starting D-Bus main loop")
            logger.info("Press Ctrl+C to stop")

            self.mainloop = GLib.MainLoop()
            self.mainloop.run()

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.stop()

    def handle_read_request(self, service_uuid: str, char_uuid: str) -> bytes:
        """Handle a characteristic read request.

        Args:
            service_uuid: Service UUID
            char_uuid: Characteristic UUID

        Returns:
            Characteristic value
        """
        characteristic = self.gatt_server.get_characteristic(service_uuid, char_uuid)
        if characteristic:
            return characteristic.read()

        logger.warning(f"Read request for unknown characteristic: {char_uuid}")
        return b""

    def handle_write_request(self, service_uuid: str, char_uuid: str, value: bytes):
        """Handle a characteristic write request.

        Args:
            service_uuid: Service UUID
            char_uuid: Characteristic UUID
            value: Value to write
        """
        characteristic = self.gatt_server.get_characteristic(service_uuid, char_uuid)
        if characteristic:
            characteristic.write(value)
        else:
            logger.warning(f"Write request for unknown characteristic: {char_uuid}")

    def send_notification(self, service_uuid: str, char_uuid: str, value: bytes):
        """Send a notification for a characteristic.

        Args:
            service_uuid: Service UUID
            char_uuid: Characteristic UUID
            value: Value to send in notification
        """
        try:
            # Find the D-Bus characteristic object
            if not self.gatt_server.application:
                logger.warning("Cannot send notification: GATT server not registered")
                return

            # Find the service
            for dbus_service in self.gatt_server.application.services:
                if dbus_service.service.uuid == service_uuid:
                    # Find the characteristic
                    for dbus_char in dbus_service.characteristics:
                        if dbus_char.char.uuid == char_uuid:
                            # Check if notifications are enabled
                            if not dbus_char.notifying:
                                logger.debug(f"Notifications not enabled for {char_uuid}")
                                return

                            # Update the characteristic value
                            dbus_char.char.value = value

                            # Send PropertiesChanged signal
                            if self.gatt_server.bus:
                                from tandem_simulator.ble.gatt_server import (
                                    DBUS_PROP_IFACE,
                                    GATT_CHARACTERISTIC_IFACE,
                                )

                                props = {"Value": dbus.Array(value, signature="y")}
                                dbus_char.PropertiesChanged(GATT_CHARACTERISTIC_IFACE, props, [])

                                logger.debug(
                                    f"Sent notification for {char_uuid}: " f"{value.hex()}"
                                )
                            return

            logger.warning(f"Characteristic {char_uuid} not found for notification")

        except Exception as e:
            logger.error(f"Error sending notification: {e}")

    def _setup_connection_handlers(self):
        """Set up D-Bus signal handlers for connection events."""
        try:
            if not self.gatt_server.bus:
                logger.warning("Cannot set up connection handlers: no D-Bus bus")
                return

            # Listen for PropertiesChanged signals on device objects
            # This allows us to detect when devices connect/disconnect
            from tandem_simulator.ble.gatt_server import BLUEZ_SERVICE_NAME, DBUS_PROP_IFACE

            self.gatt_server.bus.add_signal_receiver(
                self._on_properties_changed,
                dbus_interface=DBUS_PROP_IFACE,
                signal_name="PropertiesChanged",
                bus_name=BLUEZ_SERVICE_NAME,
                path_keyword="path",
            )

            logger.debug("Connection event handlers set up")

        except Exception as e:
            logger.error(f"Error setting up connection handlers: {e}")

    def _on_properties_changed(self, interface, changed, invalidated, path):
        """Handle D-Bus PropertiesChanged signals for connection events.

        Args:
            interface: D-Bus interface that changed
            changed: Dictionary of changed properties
            invalidated: List of invalidated properties
            path: D-Bus object path
        """
        try:
            # Check if this is a device connection/disconnection
            if "org.bluez.Device1" in interface:
                if "Connected" in changed:
                    connected = changed["Connected"]
                    device_address = path.split("/")[-1].replace("_", ":")

                    if connected:
                        # Device connected
                        self.connection_manager.handle_connection(device_address)
                    else:
                        # Device disconnected
                        self.connection_manager.handle_disconnection(device_address)

        except Exception as e:
            logger.error(f"Error handling properties changed: {e}")

    def _disconnect_all_clients(self):
        """Disconnect all connected clients."""
        try:
            if not self.connection_manager.is_connected():
                logger.debug("No clients to disconnect")
                return

            # Get list of connected device addresses
            connected_devices = list(self.connection_manager.connections.keys())

            for device_address in connected_devices:
                try:
                    # Notify connection manager
                    self.connection_manager.handle_disconnection(device_address)
                except Exception as e:
                    logger.error(f"Error disconnecting device {device_address}: {e}")

            logger.info(f"Disconnected {len(connected_devices)} client(s)")

        except Exception as e:
            logger.error(f"Error disconnecting clients: {e}")

    def is_running(self) -> bool:
        """Check if the peripheral is running.

        Returns:
            True if running, False otherwise
        """
        return self.running
