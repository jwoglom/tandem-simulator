"""Authentication flow coordinator for Tandem pump simulator.

This module coordinates the complete authentication flow including
challenge-response, JPake key exchange, and session management.

Milestone 3 deliverable.
"""

import logging
import secrets
from enum import Enum
from typing import Optional, Callable

from tandem_simulator.authentication.jpake import JPakeProtocol
from tandem_simulator.authentication.pairing import PairingManager
from tandem_simulator.authentication.session import SessionManager
from tandem_simulator.protocol.messages.authentication import (
    CentralChallengeRequest,
    CentralChallengeResponse,
    PumpChallengeRequest,
    PumpChallengeResponse,
    Jpake1aRequest,
    Jpake1aResponse,
    Jpake1bRequest,
    Jpake1bResponse,
    Jpake2Request,
    Jpake2Response,
    Jpake3SessionKeyRequest,
    Jpake3SessionKeyResponse,
    Jpake4KeyConfirmationRequest,
    Jpake4KeyConfirmationResponse,
)

logger = logging.getLogger(__name__)


class AuthenticationState(Enum):
    """Authentication flow states."""

    IDLE = "idle"
    WAITING_FOR_PAIRING_CODE = "waiting_for_pairing_code"
    CENTRAL_CHALLENGE_SENT = "central_challenge_sent"
    PUMP_CHALLENGE_READY = "pump_challenge_ready"
    JPAKE_ROUND1_SENT = "jpake_round1_sent"
    JPAKE_ROUND1_COMPLETE = "jpake_round1_complete"
    JPAKE_ROUND2_SENT = "jpake_round2_sent"
    JPAKE_ROUND2_COMPLETE = "jpake_round2_complete"
    KEY_CONFIRMATION_SENT = "key_confirmation_sent"
    AUTHENTICATED = "authenticated"
    FAILED = "failed"


class Authenticator:
    """Coordinates the complete authentication flow for the simulator."""

    def __init__(
        self,
        pairing_manager: Optional[PairingManager] = None,
        session_manager: Optional[SessionManager] = None,
    ):
        """Initialize the authenticator.

        Args:
            pairing_manager: Pairing code manager (creates new if None)
            session_manager: Session manager (creates new if None)
        """
        self.pairing_manager = pairing_manager or PairingManager()
        self.session_manager = session_manager or SessionManager()

        self.state = AuthenticationState.IDLE
        self.jpake_protocol: Optional[JPakeProtocol] = None
        self.current_device_address: Optional[str] = None
        self.transaction_id: int = 0

        # Challenge data
        self.central_challenge: Optional[bytes] = None
        self.pump_challenge: Optional[bytes] = None

        # Callbacks
        self.on_state_change: Optional[Callable[[AuthenticationState], None]] = None
        self.on_pairing_code_generated: Optional[Callable[[str], None]] = None

    def _set_state(self, new_state: AuthenticationState):
        """Change authentication state and trigger callback.

        Args:
            new_state: New authentication state
        """
        old_state = self.state
        self.state = new_state
        logger.info(f"Authentication state: {old_state.value} -> {new_state.value}")

        if self.on_state_change:
            self.on_state_change(new_state)

    def _next_transaction_id(self) -> int:
        """Get next transaction ID.

        Returns:
            Next transaction ID
        """
        self.transaction_id = (self.transaction_id + 1) % 256
        return self.transaction_id

    def start_pairing(self, device_address: str) -> str:
        """Start the pairing process for a device.

        Generates a pairing code and prepares for authentication.

        Args:
            device_address: BLE address of device to pair

        Returns:
            Generated 6-digit pairing code
        """
        logger.info(f"Starting pairing for device {device_address}")

        self.current_device_address = device_address
        pairing_code = self.pairing_manager.generate_pairing_code()

        self._set_state(AuthenticationState.WAITING_FOR_PAIRING_CODE)

        if self.on_pairing_code_generated:
            self.on_pairing_code_generated(pairing_code)

        return pairing_code

    def handle_central_challenge_request(
        self, message: CentralChallengeRequest
    ) -> CentralChallengeResponse:
        """Handle central challenge request from app.

        Args:
            message: Central challenge request

        Returns:
            Central challenge response
        """
        logger.info("Received central challenge request")

        # Store challenge
        self.central_challenge = message.challenge

        # Generate pump's response to the challenge
        # For simulator, we'll create a simple response
        response_data = secrets.token_bytes(16)

        self._set_state(AuthenticationState.CENTRAL_CHALLENGE_SENT)

        return CentralChallengeResponse(
            transaction_id=message.transaction_id, response=response_data
        )

    def handle_pump_challenge_request(self, message: PumpChallengeRequest) -> PumpChallengeResponse:
        """Handle pump challenge request from app.

        Args:
            message: Pump challenge request

        Returns:
            Pump challenge response
        """
        logger.info("Received pump challenge request")

        # Generate pump challenge
        self.pump_challenge = secrets.token_bytes(16)

        self._set_state(AuthenticationState.PUMP_CHALLENGE_READY)

        return PumpChallengeResponse(
            transaction_id=message.transaction_id, challenge=self.pump_challenge
        )

    def generate_jpake1a(self) -> Jpake1aRequest:
        """Generate JPake Round 1a message.

        Returns:
            Jpake1a request message

        Raises:
            ValueError: If pairing code not available
        """
        pairing_code = self.pairing_manager.get_current_code()
        if not pairing_code:
            raise ValueError("No active pairing code")

        logger.info("Generating JPake Round 1a")

        # Initialize JPake protocol
        self.jpake_protocol = JPakeProtocol(pairing_code=pairing_code, role="pump")

        # Generate Round 1 values
        g1, g2 = self.jpake_protocol.generate_round1()

        self._set_state(AuthenticationState.JPAKE_ROUND1_SENT)

        return Jpake1aRequest(transaction_id=self._next_transaction_id(), g1=g1, g2=g2)

    def handle_jpake1b_request(self, message: Jpake1bRequest) -> Jpake1bResponse:
        """Handle JPake Round 1b message from app.

        Args:
            message: Jpake1b request

        Returns:
            Jpake1b response
        """
        logger.info("Received JPake Round 1b")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Process Round 1 data from app
        self.jpake_protocol.process_round1(message.g3, message.g4)

        self._set_state(AuthenticationState.JPAKE_ROUND1_COMPLETE)

        return Jpake1bResponse(transaction_id=message.transaction_id, status=0)

    def generate_jpake2(self) -> Jpake2Request:
        """Generate JPake Round 2 message.

        Returns:
            Jpake2 request message
        """
        logger.info("Generating JPake Round 2")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Generate Round 2 value
        a_value = self.jpake_protocol.generate_round2()

        self._set_state(AuthenticationState.JPAKE_ROUND2_SENT)

        return Jpake2Request(transaction_id=self._next_transaction_id(), a_value=a_value)

    def handle_jpake2_response(self, message: Jpake2Response):
        """Handle JPake Round 2 response from app.

        Args:
            message: Jpake2 response
        """
        logger.info("Received JPake Round 2 response")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Process Round 2 data from app
        self.jpake_protocol.process_round2(message.b_value)

        self._set_state(AuthenticationState.JPAKE_ROUND2_COMPLETE)

    def handle_jpake3_request(self, message: Jpake3SessionKeyRequest) -> Jpake3SessionKeyResponse:
        """Handle JPake Round 3 session key request.

        Args:
            message: Jpake3 session key request

        Returns:
            Jpake3 session key response
        """
        logger.info("Received JPake Round 3 (session key)")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Derive session key
        session_key = self.jpake_protocol.derive_session_key()

        # Verify app's key confirmation
        is_valid = self.jpake_protocol.verify_key_confirmation(message.key_confirmation, "app")

        if not is_valid:
            logger.error("Invalid key confirmation from app")
            self._set_state(AuthenticationState.FAILED)
            return Jpake3SessionKeyResponse(transaction_id=message.transaction_id, status=1)

        logger.info("Session key successfully derived")

        return Jpake3SessionKeyResponse(transaction_id=message.transaction_id, status=0)

    def generate_jpake4(self) -> Jpake4KeyConfirmationRequest:
        """Generate JPake Round 4 key confirmation.

        Returns:
            Jpake4 key confirmation request
        """
        logger.info("Generating JPake Round 4 (key confirmation)")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Generate pump's key confirmation
        confirmation = self.jpake_protocol.generate_key_confirmation()

        self._set_state(AuthenticationState.KEY_CONFIRMATION_SENT)

        return Jpake4KeyConfirmationRequest(
            transaction_id=self._next_transaction_id(), confirmation=confirmation
        )

    def handle_jpake4_response(self, message: Jpake4KeyConfirmationResponse):
        """Handle JPake Round 4 confirmation response.

        Args:
            message: Jpake4 confirmation response
        """
        logger.info("Received JPake Round 4 response")

        if message.status == 0:
            # Authentication successful!
            if self.jpake_protocol and self.current_device_address:
                session_key = self.jpake_protocol.get_session_key()
                if session_key:
                    # Create session
                    self.session_manager.create_session(
                        device_address=self.current_device_address,
                        session_key=session_key,
                    )

                    logger.info(f"Authentication complete for {self.current_device_address}")
                    self._set_state(AuthenticationState.AUTHENTICATED)

                    # Clear pairing code
                    self.pairing_manager.clear_pairing_code()
                    return

        logger.error("Authentication failed")
        self._set_state(AuthenticationState.FAILED)

    def is_authenticated(self, device_address: str) -> bool:
        """Check if a device is authenticated.

        Args:
            device_address: BLE address of device

        Returns:
            True if device has valid session
        """
        return self.session_manager.is_device_paired(device_address)

    def get_session_key(self, device_address: str) -> Optional[bytes]:
        """Get session key for a device.

        Args:
            device_address: BLE address of device

        Returns:
            Session key if found, None otherwise
        """
        return self.session_manager.get_session_key(device_address)

    def reset(self):
        """Reset authentication state."""
        self.state = AuthenticationState.IDLE
        self.jpake_protocol = None
        self.current_device_address = None
        self.central_challenge = None
        self.pump_challenge = None
        self.pairing_manager.clear_pairing_code()

    def get_status(self) -> dict:
        """Get current authentication status.

        Returns:
            Dictionary with status information
        """
        return {
            "state": self.state.value,
            "current_device": self.current_device_address,
            "pairing_status": self.pairing_manager.get_status(),
            "session_stats": self.session_manager.get_statistics(),
        }
