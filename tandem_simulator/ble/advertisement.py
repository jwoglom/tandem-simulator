"""BLE advertisement management for Tandem pump simulator.

This module handles broadcasting the pump as a discoverable BLE peripheral
with the correct service UUIDs and device name.
"""

from typing import Optional

import dbus
import dbus.service

from tandem_simulator.utils.constants import (
    DEFAULT_SERIAL_NUMBER,
    DEVICE_NAME_PREFIX,
    PUMP_SERVICE_UUID,
)
from tandem_simulator.utils.logger import get_logger

logger = get_logger()

BLUEZ_SERVICE_NAME = "org.bluez"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"


class BLEAdvertisement(dbus.service.Object):
    """D-Bus service object implementing the BlueZ LEAdvertisement1 interface."""

    PATH_BASE = "/org/bluez/tandem/advertisement"

    def __init__(self, bus: dbus.Bus, index: int, ad_type: str = "peripheral"):
        """Initialize the BLE advertisement D-Bus object.

        Args:
            bus: D-Bus system bus
            index: Advertisement index (for unique path)
            ad_type: Advertisement type (default: "peripheral")
        """
        self.path = f"{self.PATH_BASE}{index}"
        self.bus = bus
        self.ad_type = ad_type
        self.service_uuids: list = []
        self.local_name: Optional[str] = None
        self.include_tx_power = True

        super().__init__(bus, self.path)

    def get_properties(self) -> dict:
        """Get advertisement properties for D-Bus.

        Returns:
            Dictionary of advertisement properties
        """
        properties = {"Type": self.ad_type}

        if self.service_uuids:
            properties["ServiceUUIDs"] = dbus.Array(self.service_uuids, signature="s")

        if self.local_name:
            properties["LocalName"] = dbus.String(self.local_name)

        if self.include_tx_power:
            properties["IncludeTxPower"] = dbus.Boolean(True)

        return {LE_ADVERTISEMENT_IFACE: properties}

    def get_path(self) -> str:
        """Get the D-Bus object path.

        Returns:
            D-Bus object path
        """
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface: str) -> dict:
        """Get all properties for the given interface.

        Args:
            interface: D-Bus interface name

        Returns:
            Dictionary of properties
        """
        if interface != LE_ADVERTISEMENT_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs", "Invalid interface"
            )

        return self.get_properties()[LE_ADVERTISEMENT_IFACE]

    @dbus.service.method(LE_ADVERTISEMENT_IFACE, in_signature="", out_signature="")
    def Release(self):
        """Release the advertisement (called by BlueZ when unregistering)."""
        logger.debug(f"Advertisement {self.path} released")


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
        self.bus: Optional[dbus.Bus] = None
        self.adapter: Optional[dbus.Interface] = None
        self.ad_manager: Optional[dbus.Interface] = None
        self.advertisement: Optional[BLEAdvertisement] = None

        logger.info(f"Advertisement initialized: {self.device_name}")

    def _find_adapter(self) -> Optional[str]:
        """Find the Bluetooth adapter object path.

        Returns:
            Adapter object path if found, None otherwise
        """
        try:
            assert self.bus is not None
            remote_om = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, "/"), DBUS_OM_IFACE)
            objects = remote_om.GetManagedObjects()

            for path, ifaces in objects.items():
                if LE_ADVERTISING_MANAGER_IFACE in ifaces:
                    return path

            logger.error("No Bluetooth adapter with advertising support found")
            return None

        except dbus.exceptions.DBusException as e:
            logger.error(f"Error finding Bluetooth adapter: {e}")
            return None

    def start(self):
        """Start broadcasting the BLE advertisement.

        This method will register the advertisement with BlueZ via D-Bus
        and begin broadcasting.
        """
        if self.is_advertising:
            logger.warning("Advertisement already active")
            return

        try:
            # Get the system bus
            self.bus = dbus.SystemBus()

            # Find the Bluetooth adapter
            adapter_path = self._find_adapter()
            if not adapter_path:
                raise RuntimeError("No Bluetooth adapter found")

            # Get the advertising manager
            self.ad_manager = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, adapter_path),
                LE_ADVERTISING_MANAGER_IFACE,
            )

            # Create the advertisement D-Bus object
            self.advertisement = BLEAdvertisement(self.bus, 0)
            self.advertisement.service_uuids = [PUMP_SERVICE_UUID]
            self.advertisement.local_name = self.device_name

            # Register the advertisement
            self.ad_manager.RegisterAdvertisement(
                self.advertisement.get_path(), dbus.Dictionary({}, signature="sv")
            )

            self.is_advertising = True
            logger.info(f"Advertisement started: {self.device_name}")
            logger.info(f"Advertising service UUID: {PUMP_SERVICE_UUID}")

        except dbus.exceptions.DBusException as e:
            logger.error(f"Failed to start advertisement: {e}")
            raise RuntimeError(f"Advertisement failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error starting advertisement: {e}")
            raise

    def stop(self):
        """Stop broadcasting the BLE advertisement."""
        if not self.is_advertising:
            logger.warning("Advertisement not active")
            return

        try:
            # Unregister the advertisement
            if self.ad_manager and self.advertisement:
                self.ad_manager.UnregisterAdvertisement(self.advertisement.get_path())
                logger.info("Advertisement stopped")

            # Clean up
            if self.advertisement:
                self.advertisement.remove_from_connection()
                self.advertisement = None

            self.ad_manager = None
            self.is_advertising = False

        except dbus.exceptions.DBusException as e:
            logger.error(f"Failed to stop advertisement: {e}")
            # Still mark as not advertising even if unregistration failed
            self.is_advertising = False
        except Exception as e:
            logger.error(f"Unexpected error stopping advertisement: {e}")
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
