"""Pump state model for Tandem pump simulator.

This module maintains the internal state of the simulated pump.

Milestone 4 deliverable.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PumpState:
    """Represents the current state of the simulated pump."""

    # Battery
    battery_percent: int = 100

    # Basal
    current_basal_rate: float = 0.0  # U/hr
    basal_active: bool = True

    # Bolus
    bolus_active: bool = False
    bolus_amount: float = 0.0  # U
    bolus_delivered: float = 0.0  # U

    # Insulin
    reservoir_volume: float = 300.0  # U
    insulin_on_board: float = 0.0  # U

    # CGM (if applicable)
    cgm_glucose: Optional[int] = None  # mg/dL
    cgm_trend: Optional[str] = None

    # Status
    suspended: bool = False
    time_since_reset: int = 0  # seconds

    # Device info
    serial_number: str = "00000000"
    firmware_version: str = "7.7.1"


class PumpStateManager:
    """Manages pump state and state transitions."""

    def __init__(self, initial_state: Optional[PumpState] = None):
        """Initialize the pump state manager.

        Args:
            initial_state: Initial pump state, or None to use defaults
        """
        self.state = initial_state if initial_state is not None else PumpState()

    def update_battery(self, percent: int):
        """Update battery percentage.

        Args:
            percent: Battery percentage (0-100)
        """
        self.state.battery_percent = max(0, min(100, percent))

    def update_basal_rate(self, rate: float):
        """Update current basal rate.

        Args:
            rate: Basal rate in U/hr
        """
        self.state.current_basal_rate = rate

    def start_bolus(self, amount: float):
        """Start a bolus delivery.

        Args:
            amount: Bolus amount in units
        """
        self.state.bolus_active = True
        self.state.bolus_amount = amount
        self.state.bolus_delivered = 0.0

    def suspend_pump(self):
        """Suspend the pump."""
        self.state.suspended = True
        self.state.basal_active = False

    def resume_pump(self):
        """Resume the pump."""
        self.state.suspended = False
        self.state.basal_active = True

    def get_state(self) -> PumpState:
        """Get the current pump state.

        Returns:
            Current PumpState
        """
        return self.state

    def set_state(self, state: PumpState):
        """Set the pump state.

        Args:
            state: New pump state
        """
        self.state = state
