"""Tests for request handlers."""

import json
import os
import tempfile

import pytest

from tandem_simulator.handlers.control import ControlHandlers
from tandem_simulator.handlers.request_handler import RequestHandler
from tandem_simulator.handlers.status import StatusHandlers
from tandem_simulator.protocol.messages.request.currentStatus.ApiVersionRequest import (
    ApiVersionRequest,
)
from tandem_simulator.protocol.messages.request.currentStatus.CurrentBasalStatusRequest import (
    CurrentBasalStatusRequest,
)
from tandem_simulator.protocol.messages.request.currentStatus.CurrentBatteryV1Request import (
    CurrentBatteryV1Request,
)
from tandem_simulator.protocol.messages.request.currentStatus.CurrentBolusStatusRequest import (
    CurrentBolusStatusRequest,
)
from tandem_simulator.protocol.messages.request.currentStatus.InsulinStatusRequest import (
    InsulinStatusRequest,
)
from tandem_simulator.protocol.messages.request.currentStatus.PumpVersionRequest import (
    PumpVersionRequest,
)
from tandem_simulator.protocol.messages.response.currentStatus.ApiVersionResponse import (
    ApiVersionResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.CurrentBasalStatusResponse import (
    CurrentBasalStatusResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.CurrentBatteryV1Response import (
    CurrentBatteryV1Response,
)
from tandem_simulator.protocol.messages.response.currentStatus.CurrentBolusStatusResponse import (
    CurrentBolusStatusResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.InsulinStatusResponse import (
    InsulinStatusResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.PumpVersionResponse import (
    PumpVersionResponse,
)
from tandem_simulator.state.persistence import StatePersistence
from tandem_simulator.state.pump_state import PumpState, PumpStateManager


class TestStatusHandlers:
    """Test status request handlers."""

    def test_handle_api_version_request(self):
        """Test API version request handler."""
        manager = PumpStateManager()
        handlers = StatusHandlers(manager)

        request = ApiVersionRequest(transaction_id=1)
        response = handlers.handle_api_version_request(request)

        assert isinstance(response, ApiVersionResponse)
        assert response.transaction_id == 1
        assert response.major == 1
        assert response.minor == 0

    def test_handle_pump_version_request(self):
        """Test pump version request handler."""
        manager = PumpStateManager()
        manager.state.serial_number = "12345678"
        manager.state.firmware_version = "7.7.1"

        handlers = StatusHandlers(manager)
        request = PumpVersionRequest(transaction_id=2)
        response = handlers.handle_pump_version_request(request)

        assert isinstance(response, PumpVersionResponse)
        assert response.transaction_id == 2
        assert response.serial_num == 12345678
        assert response.pump_rev == "7.7.1"
        assert response.arm_sw_ver == 7070001

    def test_handle_battery_status_request(self):
        """Test battery status request handler."""
        manager = PumpStateManager()
        manager.state.battery_percent = 75

        handlers = StatusHandlers(manager)
        request = CurrentBatteryV1Request(transaction_id=3)
        response = handlers.handle_battery_status_request(request)

        assert isinstance(response, CurrentBatteryV1Response)
        assert response.transaction_id == 3
        assert response.current_battery_abc == 75
        assert response.current_battery_ibc == 75

    def test_handle_basal_status_request(self):
        """Test basal status request handler."""
        manager = PumpStateManager()
        manager.state.current_basal_rate = 1.25  # units/hr

        handlers = StatusHandlers(manager)
        request = CurrentBasalStatusRequest(transaction_id=4)
        response = handlers.handle_basal_status_request(request)

        assert isinstance(response, CurrentBasalStatusResponse)
        assert response.transaction_id == 4
        # 1.25 units/hr * 10000 = 12500
        assert response.current_basal_rate == 12500
        assert response.profile_basal_rate == 12500

    def test_handle_bolus_status_request_inactive(self):
        """Test bolus status request handler when no bolus is active."""
        manager = PumpStateManager()
        manager.state.bolus_active = False

        handlers = StatusHandlers(manager)
        request = CurrentBolusStatusRequest(transaction_id=5)
        response = handlers.handle_bolus_status_request(request)

        assert isinstance(response, CurrentBolusStatusResponse)
        assert response.transaction_id == 5
        assert response.status_id == CurrentBolusStatusResponse.STATUS_ALREADY_DELIVERED_OR_INVALID
        assert response.bolus_id == 0

    def test_handle_bolus_status_request_active(self):
        """Test bolus status request handler when bolus is active."""
        manager = PumpStateManager()
        manager.state.bolus_active = True
        manager.state.bolus_amount = 3.5
        manager.state.time_since_reset = 12345

        handlers = StatusHandlers(manager)
        request = CurrentBolusStatusRequest(transaction_id=6)
        response = handlers.handle_bolus_status_request(request)

        assert isinstance(response, CurrentBolusStatusResponse)
        assert response.transaction_id == 6
        assert response.status_id == CurrentBolusStatusResponse.STATUS_DELIVERING
        assert response.bolus_id == 1
        # 3.5 units * 10000 = 35000
        assert response.requested_volume == 35000
        assert response.timestamp == 12345

    def test_handle_insulin_status_request(self):
        """Test insulin status request handler."""
        manager = PumpStateManager()
        manager.state.reservoir_volume = 250.5  # units

        handlers = StatusHandlers(manager)
        request = InsulinStatusRequest(transaction_id=7)
        response = handlers.handle_insulin_status_request(request)

        assert isinstance(response, InsulinStatusResponse)
        assert response.transaction_id == 7
        # 250.5 units * 100 = 25050
        assert response.current_insulin_amount == 25050
        assert response.is_estimate == 0


class TestControlHandlers:
    """Test control request handlers (stubs)."""

    def test_suspend_request(self):
        """Test pump suspend request handler."""
        manager = PumpStateManager()
        handlers = ControlHandlers(manager)

        # Create a dummy request message
        from tandem_simulator.protocol.message import Message

        request = Message(transaction_id=10)

        # Handle suspend
        handlers.handle_suspend_request(request)

        # Verify state changed
        assert manager.state.suspended
        assert not manager.state.basal_active

    def test_resume_request(self):
        """Test pump resume request handler."""
        manager = PumpStateManager()
        manager.suspend_pump()  # Start suspended

        handlers = ControlHandlers(manager)

        # Create a dummy request message
        from tandem_simulator.protocol.message import Message

        request = Message(transaction_id=11)

        # Handle resume
        handlers.handle_resume_request(request)

        # Verify state changed
        assert not manager.state.suspended
        assert manager.state.basal_active


class TestRequestHandler:
    """Test request handler routing."""

    def test_request_handler_initialization(self):
        """Test request handler initializes correctly."""
        manager = PumpStateManager()
        handler = RequestHandler(manager)

        # Verify handlers are registered
        assert 32 in handler.handlers  # API Version
        assert 84 in handler.handlers  # Pump Version
        assert 52 in handler.handlers  # Battery
        assert 40 in handler.handlers  # Basal
        assert 44 in handler.handlers  # Bolus
        assert 36 in handler.handlers  # Insulin

    def test_request_handler_routes_correctly(self):
        """Test request handler routes messages to correct handlers."""
        manager = PumpStateManager()
        handler = RequestHandler(manager)

        # Test API version request
        request = ApiVersionRequest(transaction_id=1)
        response = handler.handle_request(request)

        assert isinstance(response, ApiVersionResponse)
        assert response.transaction_id == 1

    def test_request_handler_unknown_opcode(self):
        """Test request handler handles unknown opcodes gracefully."""
        manager = PumpStateManager()
        handler = RequestHandler(manager)

        # Create a message with unknown opcode
        from tandem_simulator.protocol.message import Message

        request = Message(transaction_id=99)
        request.opcode = 999  # Unknown opcode

        response = handler.handle_request(request)

        # Should return None for unknown opcodes
        assert response is None


class TestStatePersistence:
    """Test state persistence."""

    def test_save_and_load_state(self):
        """Test saving and loading pump state."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            # Create and save state
            persistence = StatePersistence(temp_path)
            original_state = PumpState(
                battery_percent=85,
                current_basal_rate=1.5,
                reservoir_volume=200.0,
                serial_number="12345678",
            )

            result = persistence.save_state(original_state)
            assert result is True

            # Load state
            loaded_state = persistence.load_state()

            assert loaded_state is not None
            assert loaded_state.battery_percent == 85
            assert loaded_state.current_basal_rate == 1.5
            assert loaded_state.reservoir_volume == 200.0
            assert loaded_state.serial_number == "12345678"

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        persistence = StatePersistence("/tmp/nonexistent_pump_state.json")
        loaded_state = persistence.load_state()

        # Should return None for nonexistent file
        assert loaded_state is None

    def test_pump_state_manager_with_initial_state(self):
        """Test pump state manager with initial state."""
        initial_state = PumpState(battery_percent=50, current_basal_rate=2.0)

        manager = PumpStateManager(initial_state)

        assert manager.state.battery_percent == 50
        assert manager.state.current_basal_rate == 2.0
