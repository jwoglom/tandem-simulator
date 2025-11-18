"""Authentication and pairing implementation.

This module handles JPake key exchange, pairing codes, challenge-response
flows, and session management.

Milestone 3 deliverable.
"""

from tandem_simulator.authentication.authenticator import AuthenticationState, Authenticator
from tandem_simulator.authentication.jpake import JPakeProtocol
from tandem_simulator.authentication.pairing import PairingManager
from tandem_simulator.authentication.session import Session, SessionManager

__all__ = [
    "Authenticator",
    "AuthenticationState",
    "JPakeProtocol",
    "PairingManager",
    "Session",
    "SessionManager",
]
