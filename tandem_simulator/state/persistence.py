"""State persistence for Tandem pump simulator.

This module handles saving and loading pump state to/from disk.

Milestone 4 deliverable.
"""

import json
import logging
import os
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from tandem_simulator.state.pump_state import PumpState

logger = logging.getLogger(__name__)


class StatePersistence:
    """Handles pump state persistence."""

    def __init__(self, storage_path: str = "config/pump_state.json"):
        """Initialize state persistence.

        Args:
            storage_path: Path to store pump state
        """
        self.storage_path = storage_path

    def save_state(self, state: PumpState) -> bool:
        """Save pump state to disk.

        Args:
            state: Pump state to save

        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Ensure directory exists
            storage_dir = os.path.dirname(self.storage_path)
            if storage_dir:
                Path(storage_dir).mkdir(parents=True, exist_ok=True)

            # Convert dataclass to dictionary
            state_dict = asdict(state)

            # Write to file
            with open(self.storage_path, "w") as f:
                json.dump(state_dict, f, indent=2)

            logger.info(f"Pump state saved to {self.storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save pump state: {e}")
            return False

    def load_state(self) -> Optional[PumpState]:
        """Load pump state from disk.

        Returns:
            Loaded PumpState or None if load fails
        """
        try:
            if not os.path.exists(self.storage_path):
                logger.info(f"No saved state found at {self.storage_path}, using defaults")
                return None

            # Read from file
            with open(self.storage_path, "r") as f:
                state_dict = json.load(f)

            # Convert dictionary to dataclass
            state = PumpState(**state_dict)

            logger.info(f"Pump state loaded from {self.storage_path}")
            return state

        except Exception as e:
            logger.error(f"Failed to load pump state: {e}")
            return None
