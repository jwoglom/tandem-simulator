"""Pairing code management for Tandem pump simulator.

This module handles pairing code generation, display, and verification
with timeout management.

Milestone 3 deliverable.
"""

import random
import time
from datetime import datetime, timedelta
from typing import Optional


class PairingManager:
    """Manages pairing codes and pairing flow with timeout handling."""

    def __init__(self, timeout_seconds: int = 60):
        """Initialize the pairing manager.

        Args:
            timeout_seconds: Timeout for pairing code validity (default: 60 seconds)
        """
        self.current_pairing_code: Optional[str] = None
        self.pairing_timeout: int = timeout_seconds
        self.code_generated_at: Optional[datetime] = None
        self.pairing_attempts: int = 0
        self.max_attempts: int = 3

    def generate_pairing_code(self) -> str:
        """Generate a new 6-digit pairing code.

        The code is valid for the configured timeout period.

        Returns:
            6-digit pairing code as string
        """
        code = f"{random.randint(0, 999999):06d}"
        self.current_pairing_code = code
        self.code_generated_at = datetime.now()
        self.pairing_attempts = 0
        return code

    def is_code_expired(self) -> bool:
        """Check if the current pairing code has expired.

        Returns:
            True if code has expired or no code is active
        """
        if self.current_pairing_code is None or self.code_generated_at is None:
            return True

        elapsed = datetime.now() - self.code_generated_at
        return elapsed.total_seconds() >= self.pairing_timeout

    def get_remaining_time(self) -> float:
        """Get remaining time before code expires.

        Returns:
            Remaining time in seconds, or 0 if expired/no code
        """
        if self.is_code_expired():
            return 0.0

        assert self.code_generated_at is not None  # Checked by is_code_expired()
        elapsed = datetime.now() - self.code_generated_at
        remaining = self.pairing_timeout - elapsed.total_seconds()
        return max(0.0, remaining)

    def verify_pairing_code(self, code: str) -> tuple[bool, str]:
        """Verify a pairing code.

        Args:
            code: Pairing code to verify

        Returns:
            Tuple of (is_valid, error_message)
            - (True, "") if valid
            - (False, error_message) if invalid
        """
        # Check if code exists
        if self.current_pairing_code is None:
            return False, "No active pairing code"

        # Check if code has expired
        if self.is_code_expired():
            self.clear_pairing_code()
            return False, "Pairing code has expired"

        # Check attempt limit
        if self.pairing_attempts >= self.max_attempts:
            self.clear_pairing_code()
            return False, "Too many failed attempts"

        # Increment attempts
        self.pairing_attempts += 1

        # Verify code
        if code == self.current_pairing_code:
            return True, ""
        else:
            remaining_attempts = self.max_attempts - self.pairing_attempts
            if remaining_attempts > 0:
                return False, f"Invalid code. {remaining_attempts} attempts remaining."
            else:
                self.clear_pairing_code()
                return False, "Invalid code. Maximum attempts exceeded."

    def clear_pairing_code(self):
        """Clear the current pairing code and reset state."""
        self.current_pairing_code = None
        self.code_generated_at = None
        self.pairing_attempts = 0

    def get_current_code(self) -> Optional[str]:
        """Get the current pairing code if valid.

        Returns:
            Current pairing code or None if expired/no code
        """
        if self.is_code_expired():
            self.clear_pairing_code()
            return None

        return self.current_pairing_code

    def refresh_code(self) -> str:
        """Clear the current code and generate a new one.

        Returns:
            New 6-digit pairing code
        """
        self.clear_pairing_code()
        return self.generate_pairing_code()

    def get_status(self) -> dict:
        """Get current pairing status.

        Returns:
            Dictionary with pairing status information
        """
        code = self.get_current_code()

        if code is None:
            return {
                "active": False,
                "code": None,
                "remaining_time": 0,
                "attempts_remaining": self.max_attempts,
            }

        return {
            "active": True,
            "code": code,
            "remaining_time": self.get_remaining_time(),
            "attempts_remaining": self.max_attempts - self.pairing_attempts,
        }
