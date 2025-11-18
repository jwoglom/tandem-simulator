"""State persistence for Tandem pump simulator.

This module handles saving and loading pump state to/from disk.

Milestone 4 deliverable (stub).
"""

import json

from tandem_simulator.state.pump_state import PumpState


class StatePersistence:
    """Handles pump state persistence."""

    def __init__(self, storage_path: str = "config/pump_state.json"):
        """Initialize state persistence.

        Args:
            storage_path: Path to store pump state
        """
        self.storage_path = storage_path

    def save_state(self, state: PumpState):
        """Save pump state to disk.

        Args:
            state: Pump state to save
        """
        # TODO: Implement state saving
        pass

    def load_state(self) -> PumpState:
        """Load pump state from disk.

        Returns:
            Loaded PumpState or default state
        """
        # TODO: Implement state loading
        return PumpState()
