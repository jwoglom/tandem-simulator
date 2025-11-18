"""GATT server implementation for Tandem pump simulator.

This module defines all BLE GATT services and characteristics used by the
Tandem pump, including the Pump Service, Device Information Service,
Generic Access Service, and Generic Attribute Service.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

import dbus
import dbus.service

from tandem_simulator.state.pump_state import PumpStateManager
from tandem_simulator.utils.constants import (  # Services; Pump Service Characteristics; Device Info Service Characteristics; Generic Access Service Characteristics; Device Information
    APPEARANCE_CHAR_UUID,
    AUTHORIZATION_CHAR_UUID,
    CONTROL_CHAR_UUID,
    CONTROL_STREAM_CHAR_UUID,
    CURRENT_STATUS_CHAR_UUID,
    DEVICE_INFO_SERVICE_UUID,
    DEVICE_NAME_CHAR_UUID,
    GENERIC_ACCESS_SERVICE_UUID,
    GENERIC_ATTRIBUTE_SERVICE_UUID,
    HISTORY_LOG_CHAR_UUID,
    MANUFACTURER_NAME,
    MANUFACTURER_NAME_CHAR_UUID,
    MODEL_NUMBER,
    MODEL_NUMBER_CHAR_UUID,
    PUMP_SERVICE_UUID,
    QUALIFYING_EVENTS_CHAR_UUID,
    SERIAL_NUMBER_CHAR_UUID,
    SOFTWARE_REVISION,
    SOFTWARE_REVISION_CHAR_UUID,
)
from tandem_simulator.utils.logger import get_logger

logger = get_logger()

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
GATT_SERVICE_IFACE = "org.bluez.GattService1"
GATT_CHARACTERISTIC_IFACE = "org.bluez.GattCharacteristic1"
GATT_DESCRIPTOR_IFACE = "org.bluez.GattDescriptor1"
DBUS_OM_IFACE = "org.freedesktop.DBus.ObjectManager"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"


@dataclass
class CharacteristicProperties:
    """BLE characteristic properties."""

    read: bool = False
    write: bool = False
    write_without_response: bool = False
    notify: bool = False
    indicate: bool = False


class Characteristic:
    """Represents a GATT characteristic."""

    def __init__(
        self,
        uuid: str,
        properties: CharacteristicProperties,
        value: Optional[bytes] = None,
        read_callback: Optional[Callable] = None,
        write_callback: Optional[Callable] = None,
    ):
        """Initialize a characteristic.

        Args:
            uuid: Characteristic UUID
            properties: Characteristic properties
            value: Initial value (optional)
            read_callback: Callback for read operations
            write_callback: Callback for write operations
        """
        self.uuid = uuid
        self.properties = properties
        self._value = value or b""
        self.read_callback = read_callback
        self.write_callback = write_callback
        self.notifying = False
        self.service_path: str = ""  # Set by DBusService when creating D-Bus objects

    @property
    def value(self) -> bytes:
        """Get the characteristic value."""
        return self._value

    @value.setter
    def value(self, new_value: bytes):
        """Set the characteristic value."""
        self._value = new_value

    def read(self) -> bytes:
        """Read the characteristic value.

        Returns:
            Characteristic value
        """
        if self.read_callback:
            value = self.read_callback()
            logger.log_characteristic_read(self.uuid, value)
            return value
        logger.log_characteristic_read(self.uuid, self._value)
        return self._value

    def write(self, value: bytes):
        """Write a value to the characteristic.

        Args:
            value: Value to write
        """
        logger.log_characteristic_write(self.uuid, value)
        self._value = value
        if self.write_callback:
            self.write_callback(value)


class Service:
    """Represents a GATT service."""

    def __init__(self, uuid: str, primary: bool = True):
        """Initialize a service.

        Args:
            uuid: Service UUID
            primary: Whether this is a primary service
        """
        self.uuid = uuid
        self.primary = primary
        self.characteristics: Dict[str, Characteristic] = {}

    def add_characteristic(self, characteristic: Characteristic):
        """Add a characteristic to the service.

        Args:
            characteristic: Characteristic to add
        """
        self.characteristics[characteristic.uuid] = characteristic
        logger.debug(f"Added characteristic {characteristic.uuid} to service {self.uuid}")

    def get_characteristic(self, uuid: str) -> Optional[Characteristic]:
        """Get a characteristic by UUID.

        Args:
            uuid: Characteristic UUID

        Returns:
            Characteristic if found, None otherwise
        """
        return self.characteristics.get(uuid)


class DBusCharacteristic(dbus.service.Object):
    """D-Bus object implementing the BlueZ GattCharacteristic1 interface."""

    def __init__(self, bus: dbus.Bus, index: int, char: Characteristic, service_path: str):
        """Initialize the D-Bus characteristic.

        Args:
            bus: D-Bus system bus
            index: Characteristic index (for unique path)
            char: Characteristic object
            service_path: Parent service D-Bus path
        """
        self.path = f"{service_path}/char{index:04d}"
        self.bus = bus
        self.char = char
        self.notifying = False
        super().__init__(bus, self.path)

    def get_properties(self) -> dict:
        """Get characteristic properties for D-Bus.

        Returns:
            Dictionary of characteristic properties
        """
        props = {"UUID": self.char.uuid, "Service": self.char.service_path}

        flags = []
        if self.char.properties.read:
            flags.append("read")
        if self.char.properties.write:
            flags.append("write")
        if self.char.properties.write_without_response:
            flags.append("write-without-response")
        if self.char.properties.notify:
            flags.append("notify")
        if self.char.properties.indicate:
            flags.append("indicate")

        props["Flags"] = dbus.Array(flags, signature="s")
        props["Value"] = dbus.Array(self.char.value, signature="y")

        return {GATT_CHARACTERISTIC_IFACE: props}

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface: str) -> dict:
        """Get all properties for the given interface.

        Args:
            interface: D-Bus interface name

        Returns:
            Dictionary of properties
        """
        if interface != GATT_CHARACTERISTIC_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs", "Invalid interface"
            )

        return self.get_properties()[GATT_CHARACTERISTIC_IFACE]

    @dbus.service.method(GATT_CHARACTERISTIC_IFACE, in_signature="a{sv}", out_signature="ay")
    def ReadValue(self, options: dict) -> dbus.Array:
        """Read the characteristic value.

        Args:
            options: Read options

        Returns:
            Characteristic value as byte array
        """
        value = self.char.read()
        return dbus.Array(value, signature="y")

    @dbus.service.method(GATT_CHARACTERISTIC_IFACE, in_signature="aya{sv}", out_signature="")
    def WriteValue(self, value: bytes, options: dict):
        """Write a value to the characteristic.

        Args:
            value: Value to write
            options: Write options
        """
        self.char.write(bytes(value))

    @dbus.service.method(GATT_CHARACTERISTIC_IFACE, in_signature="", out_signature="")
    def StartNotify(self):
        """Start notifications for this characteristic."""
        if self.notifying:
            return

        self.notifying = True
        logger.debug(f"Started notifications for {self.char.uuid}")

    @dbus.service.method(GATT_CHARACTERISTIC_IFACE, in_signature="", out_signature="")
    def StopNotify(self):
        """Stop notifications for this characteristic."""
        if not self.notifying:
            return

        self.notifying = False
        logger.debug(f"Stopped notifications for {self.char.uuid}")

    @dbus.service.signal(DBUS_PROP_IFACE, signature="sa{sv}as")
    def PropertiesChanged(self, interface, changed, invalidated):
        """Signal emitted when characteristic properties change.

        Args:
            interface: Interface name
            changed: Dictionary of changed properties
            invalidated: List of invalidated properties
        """
        pass

    def get_path(self) -> str:
        """Get the D-Bus object path.

        Returns:
            D-Bus object path
        """
        return dbus.ObjectPath(self.path)


class DBusService(dbus.service.Object):
    """D-Bus object implementing the BlueZ GattService1 interface."""

    def __init__(self, bus: dbus.Bus, index: int, service: Service, app_path: str):
        """Initialize the D-Bus service.

        Args:
            bus: D-Bus system bus
            index: Service index (for unique path)
            service: Service object
            app_path: Parent application D-Bus path
        """
        self.path = f"{app_path}/service{index:04d}"
        self.bus = bus
        self.service = service
        self.characteristics: List[DBusCharacteristic] = []
        super().__init__(bus, self.path)

        # Create D-Bus characteristics
        for idx, char in enumerate(service.characteristics.values()):
            char.service_path = self.path  # Store service path in characteristic
            dbus_char = DBusCharacteristic(bus, idx, char, self.path)
            self.characteristics.append(dbus_char)

    def get_properties(self) -> dict:
        """Get service properties for D-Bus.

        Returns:
            Dictionary of service properties
        """
        props = {"UUID": self.service.uuid, "Primary": self.service.primary}

        return {GATT_SERVICE_IFACE: props}

    @dbus.service.method(DBUS_PROP_IFACE, in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface: str) -> dict:
        """Get all properties for the given interface.

        Args:
            interface: D-Bus interface name

        Returns:
            Dictionary of properties
        """
        if interface != GATT_SERVICE_IFACE:
            raise dbus.exceptions.DBusException(
                "org.freedesktop.DBus.Error.InvalidArgs", "Invalid interface"
            )

        return self.get_properties()[GATT_SERVICE_IFACE]

    def get_path(self) -> str:
        """Get the D-Bus object path.

        Returns:
            D-Bus object path
        """
        return dbus.ObjectPath(self.path)

    def get_managed_objects(self) -> dict:
        """Get managed objects (characteristics) for this service.

        Returns:
            Dictionary of managed objects
        """
        objects = {}

        # Add characteristics
        for char in self.characteristics:
            objects[char.get_path()] = char.get_properties()

        return objects


class GATTApplication(dbus.service.Object):
    """D-Bus application implementing the ObjectManager interface."""

    PATH_BASE = "/org/bluez/tandem/gatt"

    def __init__(self, bus: dbus.Bus):
        """Initialize the GATT application.

        Args:
            bus: D-Bus system bus
        """
        self.path = self.PATH_BASE
        self.bus = bus
        self.services: List[DBusService] = []
        super().__init__(bus, self.path)

    def add_service(self, service: DBusService):
        """Add a service to the application.

        Args:
            service: D-Bus service to add
        """
        self.services.append(service)

    def get_path(self) -> str:
        """Get the D-Bus object path.

        Returns:
            D-Bus object path
        """
        return dbus.ObjectPath(self.path)

    @dbus.service.method(DBUS_OM_IFACE, out_signature="a{oa{sa{sv}}}")
    def GetManagedObjects(self) -> dict:
        """Get all managed objects (services and characteristics).

        Returns:
            Dictionary of managed objects
        """
        objects = {}

        for service in self.services:
            # Add service
            objects[service.get_path()] = service.get_properties()

            # Add characteristics
            char_objects = service.get_managed_objects()
            objects.update(char_objects)

        return objects


class GATTServer:
    """GATT server for the Tandem pump simulator.

    Implements all required GATT services and characteristics for
    emulating a Tandem Mobi insulin pump.
    """

    def __init__(self, serial_number: str):
        """Initialize the GATT server.

        Args:
            serial_number: Pump serial number
        """
        self.serial_number = serial_number
        self.services: Dict[str, Service] = {}
        self.bus: Optional[dbus.Bus] = None
        self.gatt_manager: Optional[dbus.Interface] = None
        self.application: Optional[GATTApplication] = None
        self.registered = False

        # Initialize pump state manager
        self.pump_state = PumpStateManager()
        self.pump_state.state.serial_number = serial_number

        self._setup_services()
        logger.info("GATT server initialized")

    def _setup_services(self):
        """Set up all GATT services and characteristics."""
        # Device Information Service
        self._setup_device_info_service()

        # Pump Service
        self._setup_pump_service()

        # Generic Access Service
        self._setup_generic_access_service()

        # Generic Attribute Service
        self._setup_generic_attribute_service()

    def _setup_device_info_service(self):
        """Set up the Device Information Service."""
        service = Service(DEVICE_INFO_SERVICE_UUID, primary=True)

        # Manufacturer Name
        service.add_characteristic(
            Characteristic(
                MANUFACTURER_NAME_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=MANUFACTURER_NAME.encode("utf-8"),
            )
        )

        # Model Number
        service.add_characteristic(
            Characteristic(
                MODEL_NUMBER_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=MODEL_NUMBER.encode("utf-8"),
            )
        )

        # Serial Number
        service.add_characteristic(
            Characteristic(
                SERIAL_NUMBER_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=self.serial_number.encode("utf-8"),
            )
        )

        # Software Revision
        service.add_characteristic(
            Characteristic(
                SOFTWARE_REVISION_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=SOFTWARE_REVISION.encode("utf-8"),
            )
        )

        self.services[service.uuid] = service
        logger.debug(f"Set up Device Information Service")

    def _setup_pump_service(self):
        """Set up the Pump Service."""
        service = Service(PUMP_SERVICE_UUID, primary=True)

        # Current Status (Read, Notify)
        service.add_characteristic(
            Characteristic(
                CURRENT_STATUS_CHAR_UUID,
                CharacteristicProperties(read=True, write=True, notify=True),
                read_callback=self._read_current_status,
                write_callback=self._write_current_status,
            )
        )

        # Qualifying Events (Read, Notify, Indicate)
        service.add_characteristic(
            Characteristic(
                QUALIFYING_EVENTS_CHAR_UUID,
                CharacteristicProperties(read=True, write=True, notify=True, indicate=True),
                read_callback=self._read_qualifying_events,
                write_callback=self._write_qualifying_events,
            )
        )

        # History Log (Read, Write)
        service.add_characteristic(
            Characteristic(
                HISTORY_LOG_CHAR_UUID,
                CharacteristicProperties(read=True, write=True),
                read_callback=self._read_history_log,
                write_callback=self._write_history_log,
            )
        )

        # Authorization (Read, Write)
        service.add_characteristic(
            Characteristic(
                AUTHORIZATION_CHAR_UUID,
                CharacteristicProperties(read=True, write=True),
                read_callback=self._read_authorization,
                write_callback=self._write_authorization,
            )
        )

        # Control (Write)
        service.add_characteristic(
            Characteristic(
                CONTROL_CHAR_UUID,
                CharacteristicProperties(write=True),
                write_callback=self._write_control,
            )
        )

        # Control Stream (Read, Notify)
        service.add_characteristic(
            Characteristic(
                CONTROL_STREAM_CHAR_UUID,
                CharacteristicProperties(read=True, notify=True),
                read_callback=self._read_control_stream,
            )
        )

        self.services[service.uuid] = service
        logger.debug(f"Set up Pump Service")

    def _setup_generic_access_service(self):
        """Set up the Generic Access Service."""
        service = Service(GENERIC_ACCESS_SERVICE_UUID, primary=True)

        # Device Name
        from tandem_simulator.utils.constants import DEVICE_NAME_PREFIX

        device_name = f"{DEVICE_NAME_PREFIX} {self.serial_number}"
        service.add_characteristic(
            Characteristic(
                DEVICE_NAME_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=device_name.encode("utf-8"),
            )
        )

        # Appearance
        service.add_characteristic(
            Characteristic(
                APPEARANCE_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=b"\x00\x00",  # Unknown appearance
            )
        )

        self.services[service.uuid] = service
        logger.debug(f"Set up Generic Access Service")

    def _setup_generic_attribute_service(self):
        """Set up the Generic Attribute Service."""
        service = Service(GENERIC_ATTRIBUTE_SERVICE_UUID, primary=True)
        self.services[service.uuid] = service
        logger.debug(f"Set up Generic Attribute Service")

    # Characteristic read/write callbacks
    # Note: Full protocol implementation is part of Milestone 2
    # These provide basic responses for BLE connectivity testing

    def _read_current_status(self) -> bytes:
        """Handle Current Status characteristic read.

        Returns basic pump status. Full protocol implementation in Milestone 2.
        """
        # Return a simple status byte: 0x00 = active, 0x01 = suspended
        status = 0x01 if self.pump_state.state.suspended else 0x00
        return bytes([status])

    def _write_current_status(self, value: bytes):
        """Handle Current Status characteristic write.

        Processes status requests. Full protocol implementation in Milestone 2.
        """
        logger.debug(f"Current status write request: {value.hex()}")
        # Protocol parsing will be implemented in Milestone 2
        pass

    def _read_qualifying_events(self) -> bytes:
        """Handle Qualifying Events characteristic read.

        Returns pending events. Full protocol implementation in Milestone 2.
        """
        # No pending events for now
        return b""

    def _write_qualifying_events(self, value: bytes):
        """Handle Qualifying Events characteristic write.

        Processes event acknowledgments. Full protocol implementation in Milestone 2.
        """
        logger.debug(f"Qualifying events write request: {value.hex()}")
        # Protocol parsing will be implemented in Milestone 2
        pass

    def _read_history_log(self) -> bytes:
        """Handle History Log characteristic read.

        Returns history log data. Full protocol implementation in Milestone 2.
        """
        # No history data for now
        return b""

    def _write_history_log(self, value: bytes):
        """Handle History Log characteristic write.

        Processes history log requests. Full protocol implementation in Milestone 2.
        """
        logger.debug(f"History log write request: {value.hex()}")
        # Protocol parsing will be implemented in Milestone 2
        pass

    def _read_authorization(self) -> bytes:
        """Handle Authorization characteristic read.

        Returns auth responses. Full protocol implementation in Milestone 3.
        """
        # Auth protocol will be implemented in Milestone 3
        return b""

    def _write_authorization(self, value: bytes):
        """Handle Authorization characteristic write.

        Processes auth requests. Full protocol implementation in Milestone 3.
        """
        logger.debug(f"Authorization write request: {value.hex()}")
        # Auth protocol will be implemented in Milestone 3
        pass

    def _write_control(self, value: bytes):
        """Handle Control characteristic write.

        Processes control commands. Full protocol implementation in Milestone 2.
        """
        logger.debug(f"Control write request: {value.hex()}")
        # Protocol parsing will be implemented in Milestone 2
        pass

    def _read_control_stream(self) -> bytes:
        """Handle Control Stream characteristic read.

        Returns control responses. Full protocol implementation in Milestone 2.
        """
        # No control responses for now
        return b""

    def get_service(self, uuid: str) -> Optional[Service]:
        """Get a service by UUID.

        Args:
            uuid: Service UUID

        Returns:
            Service if found, None otherwise
        """
        return self.services.get(uuid)

    def get_characteristic(self, service_uuid: str, char_uuid: str) -> Optional[Characteristic]:
        """Get a characteristic by service and characteristic UUID.

        Args:
            service_uuid: Service UUID
            char_uuid: Characteristic UUID

        Returns:
            Characteristic if found, None otherwise
        """
        service = self.get_service(service_uuid)
        if service:
            return service.get_characteristic(char_uuid)
        return None

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
                if GATT_MANAGER_IFACE in ifaces:
                    return path

            logger.error("No Bluetooth adapter with GATT manager found")
            return None

        except dbus.exceptions.DBusException as e:
            logger.error(f"Error finding Bluetooth adapter: {e}")
            return None

    def register(self):
        """Register the GATT server with BlueZ via D-Bus."""
        if self.registered:
            logger.warning("GATT server already registered")
            return

        try:
            # Get the system bus
            self.bus = dbus.SystemBus()

            # Find the Bluetooth adapter
            adapter_path = self._find_adapter()
            if not adapter_path:
                raise RuntimeError("No Bluetooth adapter found")

            # Get the GATT manager
            self.gatt_manager = dbus.Interface(
                self.bus.get_object(BLUEZ_SERVICE_NAME, adapter_path), GATT_MANAGER_IFACE
            )

            # Create the GATT application
            self.application = GATTApplication(self.bus)

            # Add all services to the application
            for idx, service in enumerate(self.services.values()):
                dbus_service = DBusService(self.bus, idx, service, self.application.path)
                self.application.add_service(dbus_service)

            # Register the application
            self.gatt_manager.RegisterApplication(
                self.application.get_path(), dbus.Dictionary({}, signature="sv")
            )

            self.registered = True
            logger.info("GATT server registered with BlueZ")

        except dbus.exceptions.DBusException as e:
            logger.error(f"Failed to register GATT server: {e}")
            raise RuntimeError(f"GATT registration failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error registering GATT server: {e}")
            raise

    def unregister(self):
        """Unregister the GATT server from BlueZ."""
        if not self.registered:
            logger.warning("GATT server not registered")
            return

        try:
            # Unregister the application
            if self.gatt_manager and self.application:
                self.gatt_manager.UnregisterApplication(self.application.get_path())
                logger.info("GATT server unregistered from BlueZ")

            # Clean up D-Bus objects
            if self.application:
                # Remove all service objects
                for service in self.application.services:
                    # Remove characteristic objects
                    for char in service.characteristics:
                        char.remove_from_connection()
                    # Remove service object
                    service.remove_from_connection()

                # Remove application object
                self.application.remove_from_connection()
                self.application = None

            self.gatt_manager = None
            self.registered = False

        except dbus.exceptions.DBusException as e:
            logger.error(f"Failed to unregister GATT server: {e}")
            # Still mark as not registered even if unregistration failed
            self.registered = False
        except Exception as e:
            logger.error(f"Unexpected error unregistering GATT server: {e}")
            self.registered = False
