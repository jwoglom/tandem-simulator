"""Pairing code management for Tandem pump simulator.

This module handles pairing code generation, display, and verification.

Milestone 3 deliverable (stub).
"""

import random
from typing import Optional


class PairingManager:
    """Manages pairing codes and pairing flow."""

    def __init__(self):
        """Initialize the pairing manager."""
        self.current_pairing_code: Optional[str] = None
        self.pairing_timeout: int = 60  # seconds

    def generate_pairing_code(self) -> str:
        """Generate a new 6-digit pairing code.

        Returns:
            6-digit pairing code as string
        """
        code = f"{random.randint(0, 999999):06d}"
        self.current_pairing_code = code
        return code

    def verify_pairing_code(self, code: str) -> bool:
        """Verify a pairing code.

        Args:
            code: Pairing code to verify

        Returns:
            True if code matches current pairing code
        """
        return code == self.current_pairing_code

    def clear_pairing_code(self):
        """Clear the current pairing code."""
        self.current_pairing_code = None

    def get_current_code(self) -> Optional[str]:
        """Get the current pairing code.

        Returns:
            Current pairing code or None
        """
        return self.current_pairing_code
