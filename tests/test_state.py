"""Tests for pump state management."""

import pytest

from tandem_simulator.state.pump_state import PumpState, PumpStateManager


def test_pump_state_defaults():
    """Test default pump state values."""
    state = PumpState()
    assert state.battery_percent == 100
    assert state.current_basal_rate == 0.0
    assert not state.bolus_active
    assert not state.suspended
    assert state.reservoir_volume == 300.0


def test_pump_state_manager():
    """Test pump state manager."""
    manager = PumpStateManager()
    state = manager.get_state()

    assert state.battery_percent == 100

    # Test battery update
    manager.update_battery(50)
    assert manager.get_state().battery_percent == 50

    # Test basal rate update
    manager.update_basal_rate(1.5)
    assert manager.get_state().current_basal_rate == 1.5

    # Test suspend/resume
    manager.suspend_pump()
    assert manager.get_state().suspended
    assert not manager.get_state().basal_active

    manager.resume_pump()
    assert not manager.get_state().suspended
    assert manager.get_state().basal_active


def test_bolus_start():
    """Test bolus initiation."""
    manager = PumpStateManager()

    manager.start_bolus(5.0)
    state = manager.get_state()

    assert state.bolus_active
    assert state.bolus_amount == 5.0
    assert state.bolus_delivered == 0.0
