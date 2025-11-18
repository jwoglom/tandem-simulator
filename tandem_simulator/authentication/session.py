"""Session management for Tandem pump simulator.

This module handles session key storage, paired device tracking,
and session persistence to disk.

Milestone 3 deliverable.
"""

import base64
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


@dataclass
class Session:
    """Represents an authenticated session."""

    device_address: str
    session_key_b64: str  # Base64-encoded session key
    paired_at: str
    device_name: Optional[str] = None
    last_connected: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create Session from dictionary.

        Args:
            data: Dictionary with session data

        Returns:
            Session instance
        """
        return cls(**data)

    def to_dict(self) -> dict:
        """Convert Session to dictionary.

        Returns:
            Dictionary with session data
        """
        return asdict(self)


class SessionManager:
    """Manages authenticated sessions and paired devices with persistence."""

    def __init__(self, storage_path: str = "config/paired_devices.json"):
        """Initialize the session manager.

        Args:
            storage_path: Path to store paired device data
        """
        self.storage_path = storage_path
        self.sessions: Dict[str, Session] = {}
        self.current_session: Optional[Session] = None

        # Create config directory if it doesn't exist
        self._ensure_config_dir()

        # Load existing sessions
        self.load_sessions()

    def _ensure_config_dir(self):
        """Ensure config directory exists."""
        config_dir = Path(self.storage_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)

    def create_session(
        self,
        device_address: str,
        session_key: bytes,
        device_name: Optional[str] = None,
    ) -> Session:
        """Create a new authenticated session.

        Args:
            device_address: BLE address of device
            session_key: Derived session key (binary)
            device_name: Optional device name

        Returns:
            New Session instance
        """
        # Encode session key to base64 for JSON storage
        session_key_b64 = base64.b64encode(session_key).decode("ascii")

        session = Session(
            device_address=device_address,
            session_key_b64=session_key_b64,
            paired_at=datetime.now().isoformat(),
            device_name=device_name,
            last_connected=datetime.now().isoformat(),
        )

        self.sessions[device_address] = session
        self.current_session = session

        # Persist to disk
        self.save_sessions()

        return session

    def get_session(self, device_address: str) -> Optional[Session]:
        """Get session for a device.

        Args:
            device_address: BLE address of device

        Returns:
            Session if found, None otherwise
        """
        return self.sessions.get(device_address)

    def get_session_key(self, device_address: str) -> Optional[bytes]:
        """Get session key for a device.

        Args:
            device_address: BLE address of device

        Returns:
            Session key bytes if found, None otherwise
        """
        session = self.get_session(device_address)
        if session:
            return base64.b64decode(session.session_key_b64)
        return None

    def update_last_connected(self, device_address: str):
        """Update last connected timestamp for a device.

        Args:
            device_address: BLE address of device
        """
        session = self.get_session(device_address)
        if session:
            session.last_connected = datetime.now().isoformat()
            self.save_sessions()

    def remove_session(self, device_address: str) -> bool:
        """Remove a paired device session.

        Args:
            device_address: BLE address of device

        Returns:
            True if session was removed, False if not found
        """
        if device_address in self.sessions:
            del self.sessions[device_address]
            if self.current_session and self.current_session.device_address == device_address:
                self.current_session = None
            self.save_sessions()
            return True
        return False

    def save_sessions(self):
        """Save paired device data to storage."""
        try:
            data = {
                "version": 1,
                "saved_at": datetime.now().isoformat(),
                "sessions": {addr: session.to_dict() for addr, session in self.sessions.items()},
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Failed to save sessions: {e}")

    def load_sessions(self):
        """Load paired device data from storage."""
        try:
            if not os.path.exists(self.storage_path):
                return

            with open(self.storage_path, "r") as f:
                data = json.load(f)

            # Check version
            if data.get("version") != 1:
                print(f"Warning: Unknown session file version: {data.get('version')}")
                return

            # Load sessions
            sessions_data = data.get("sessions", {})
            for addr, session_dict in sessions_data.items():
                try:
                    session = Session.from_dict(session_dict)
                    self.sessions[addr] = session
                except Exception as e:
                    print(f"Warning: Failed to load session for {addr}: {e}")

        except Exception as e:
            print(f"Warning: Failed to load sessions: {e}")

    def clear_all_sessions(self):
        """Clear all paired devices."""
        self.sessions.clear()
        self.current_session = None
        self.save_sessions()

    def get_paired_devices(self) -> list[dict]:
        """Get list of all paired devices.

        Returns:
            List of device information dictionaries
        """
        devices = []
        for addr, session in self.sessions.items():
            devices.append(
                {
                    "address": addr,
                    "name": session.device_name or "Unknown",
                    "paired_at": session.paired_at,
                    "last_connected": session.last_connected,
                }
            )
        return devices

    def is_device_paired(self, device_address: str) -> bool:
        """Check if a device is already paired.

        Args:
            device_address: BLE address of device

        Returns:
            True if device is paired
        """
        return device_address in self.sessions

    def get_statistics(self) -> dict:
        """Get session statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_paired_devices": len(self.sessions),
            "current_session_active": self.current_session is not None,
            "storage_path": self.storage_path,
        }
