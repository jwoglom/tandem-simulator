"""Basic tests for Tandem pump simulator."""

import pytest

from tandem_simulator import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_import_ble_modules():
    """Test that BLE modules can be imported."""
    from tandem_simulator.ble import advertisement, connection, gatt_server, peripheral

    assert peripheral is not None
    assert gatt_server is not None
    assert advertisement is not None
    assert connection is not None


def test_import_utils_modules():
    """Test that utils modules can be imported."""
    from tandem_simulator.utils import constants, logger

    assert logger is not None
    assert constants is not None


def test_import_protocol_modules():
    """Test that protocol modules can be imported."""
    from tandem_simulator.protocol import crc, crypto, message, packetizer

    assert message is not None
    assert packetizer is not None
    assert crc is not None
    assert crypto is not None


def test_constants():
    """Test that constants are defined correctly."""
    from tandem_simulator.utils.constants import (
        DEVICE_INFO_SERVICE_UUID,
        MANUFACTURER_NAME,
        MODEL_NUMBER,
        PUMP_SERVICE_UUID,
    )

    assert PUMP_SERVICE_UUID == "0000fdfb-0000-1000-8000-00805f9b34fb"
    assert DEVICE_INFO_SERVICE_UUID == "0000180A-0000-1000-8000-00805f9b34fb"
    assert MANUFACTURER_NAME == "Tandem Diabetes Care"
    assert MODEL_NUMBER == "Mobi"


def test_logger_creation():
    """Test that logger can be created."""
    from tandem_simulator.utils.logger import get_logger

    logger = get_logger()
    assert logger is not None
    assert hasattr(logger, "info")
    assert hasattr(logger, "debug")
    assert hasattr(logger, "error")


def test_gatt_server_creation():
    """Test that GATT server can be created."""
    from tandem_simulator.ble.gatt_server import GATTServer

    server = GATTServer(serial_number="12345678")
    assert server is not None
    assert server.serial_number == "12345678"
    assert len(server.services) > 0


def test_advertisement_creation():
    """Test that advertisement can be created."""
    from tandem_simulator.ble.advertisement import Advertisement

    ad = Advertisement(serial_number="12345678")
    assert ad is not None
    assert ad.serial_number == "12345678"
    assert "tslim X2" in ad.device_name


def test_connection_manager_creation():
    """Test that connection manager can be created."""
    from tandem_simulator.ble.connection import ConnectionManager

    cm = ConnectionManager()
    assert cm is not None
    assert not cm.is_connected()


def test_peripheral_creation():
    """Test that BLE peripheral can be created."""
    from tandem_simulator.ble.peripheral import BLEPeripheral

    peripheral = BLEPeripheral(serial_number="12345678")
    assert peripheral is not None
    assert peripheral.serial_number == "12345678"
    assert not peripheral.is_running()
