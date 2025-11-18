"""GATT server implementation for Tandem pump simulator.

This module defines all BLE GATT services and characteristics used by the
Tandem pump, including the Pump Service, Device Information Service,
Generic Access Service, and Generic Attribute Service.
"""

from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
from tandem_simulator.utils.logger import get_logger
from tandem_simulator.utils.constants import (
    # Services
    PUMP_SERVICE_UUID,
    DEVICE_INFO_SERVICE_UUID,
    GENERIC_ACCESS_SERVICE_UUID,
    GENERIC_ATTRIBUTE_SERVICE_UUID,
    # Pump Service Characteristics
    CURRENT_STATUS_CHAR_UUID,
    QUALIFYING_EVENTS_CHAR_UUID,
    HISTORY_LOG_CHAR_UUID,
    AUTHORIZATION_CHAR_UUID,
    CONTROL_CHAR_UUID,
    CONTROL_STREAM_CHAR_UUID,
    # Device Info Service Characteristics
    MANUFACTURER_NAME_CHAR_UUID,
    MODEL_NUMBER_CHAR_UUID,
    SERIAL_NUMBER_CHAR_UUID,
    SOFTWARE_REVISION_CHAR_UUID,
    # Generic Access Service Characteristics
    DEVICE_NAME_CHAR_UUID,
    APPEARANCE_CHAR_UUID,
    # Device Information
    MANUFACTURER_NAME,
    MODEL_NUMBER,
    SOFTWARE_REVISION,
)

logger = get_logger()


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
                value=MANUFACTURER_NAME.encode('utf-8')
            )
        )

        # Model Number
        service.add_characteristic(
            Characteristic(
                MODEL_NUMBER_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=MODEL_NUMBER.encode('utf-8')
            )
        )

        # Serial Number
        service.add_characteristic(
            Characteristic(
                SERIAL_NUMBER_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=self.serial_number.encode('utf-8')
            )
        )

        # Software Revision
        service.add_characteristic(
            Characteristic(
                SOFTWARE_REVISION_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=SOFTWARE_REVISION.encode('utf-8')
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
                value=device_name.encode('utf-8')
            )
        )

        # Appearance
        service.add_characteristic(
            Characteristic(
                APPEARANCE_CHAR_UUID,
                CharacteristicProperties(read=True),
                value=b'\x00\x00'  # Unknown appearance
            )
        )

        self.services[service.uuid] = service
        logger.debug(f"Set up Generic Access Service")

    def _setup_generic_attribute_service(self):
        """Set up the Generic Attribute Service."""
        service = Service(GENERIC_ATTRIBUTE_SERVICE_UUID, primary=True)
        self.services[service.uuid] = service
        logger.debug(f"Set up Generic Attribute Service")

    # Characteristic read/write callbacks (stubs for Milestone 1)

    def _read_current_status(self) -> bytes:
        """Handle Current Status characteristic read."""
        # TODO: Return actual pump status
        return b""

    def _write_current_status(self, value: bytes):
        """Handle Current Status characteristic write."""
        # TODO: Process status write
        pass

    def _read_qualifying_events(self) -> bytes:
        """Handle Qualifying Events characteristic read."""
        # TODO: Return pending events
        return b""

    def _write_qualifying_events(self, value: bytes):
        """Handle Qualifying Events characteristic write."""
        # TODO: Process event acknowledgment
        pass

    def _read_history_log(self) -> bytes:
        """Handle History Log characteristic read."""
        # TODO: Return history log data
        return b""

    def _write_history_log(self, value: bytes):
        """Handle History Log characteristic write."""
        # TODO: Process history log request
        pass

    def _read_authorization(self) -> bytes:
        """Handle Authorization characteristic read."""
        # TODO: Return auth response
        return b""

    def _write_authorization(self, value: bytes):
        """Handle Authorization characteristic write."""
        # TODO: Process auth request
        pass

    def _write_control(self, value: bytes):
        """Handle Control characteristic write."""
        # TODO: Process control command
        pass

    def _read_control_stream(self) -> bytes:
        """Handle Control Stream characteristic read."""
        # TODO: Return control response
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
