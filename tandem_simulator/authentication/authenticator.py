"""Authentication flow coordinator for Tandem pump simulator.

This module coordinates the complete authentication flow including
challenge-response, JPake key exchange, and session management.

Milestone 3 deliverable.
"""

import logging
import secrets
from enum import Enum
from typing import Callable, Optional

from tandem_simulator.authentication.jpake import JPakeProtocol
from tandem_simulator.authentication.jpake_encoding import (
    decode_ec_jpake_key_kp,
    decode_jpake_round1_pair,
    decode_jpake_round2,
    encode_jpake_round1_pair,
    encode_jpake_round2,
    generate_jpake4_hash_digest,
)
from tandem_simulator.authentication.pairing import PairingManager
from tandem_simulator.authentication.session import SessionManager
from tandem_simulator.protocol.messages import (
    CentralChallengeRequest,
    CentralChallengeResponse,
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
    PumpChallengeRequest,
    PumpChallengeResponse,
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
        self.app_instance_id: int = 0

        # Challenge data
        self.central_challenge: Optional[bytes] = None
        self.pump_challenge: Optional[bytes] = None

        # JPake EC points (stored for potential verification)
        self.g1_point: Optional[bytes] = None
        self.g2_point: Optional[bytes] = None
        self.g3_point: Optional[bytes] = None
        self.g4_point: Optional[bytes] = None
        self.a_point: Optional[bytes] = None
        self.b_point: Optional[bytes] = None

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

        # Generate app instance ID (16-bit random value)
        self.app_instance_id = secrets.randbelow(0xFFFF)
        logger.debug(f"Generated app_instance_id: {self.app_instance_id}")

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

        # Store app instance ID from request
        self.app_instance_id = message.app_instance_id

        # Store challenge
        self.central_challenge = message.central_challenge

        # Generate pump's response to the challenge (SIMULATOR: random values)
        # Production should hash the challenge properly
        central_challenge_hash = secrets.token_bytes(20)  # 20 bytes SHA1 hash
        hmac_key = secrets.token_bytes(8)  # 8 bytes HMAC key

        self._set_state(AuthenticationState.CENTRAL_CHALLENGE_SENT)

        return CentralChallengeResponse(
            transaction_id=message.transaction_id,
            app_instance_id=self.app_instance_id,
            central_challenge_hash=central_challenge_hash,
            hmac_key=hmac_key,
        )

    def handle_pump_challenge_request(self, message: PumpChallengeRequest) -> PumpChallengeResponse:
        """Handle pump challenge request from app.

        Args:
            message: Pump challenge request

        Returns:
            Pump challenge response
        """
        logger.info("Received pump challenge request")

        # Update app instance ID from request (in case it changed)
        self.app_instance_id = message.app_instance_id

        # Generate pump challenge (stored for later use)
        self.pump_challenge = secrets.token_bytes(16)

        self._set_state(AuthenticationState.PUMP_CHALLENGE_READY)

        return PumpChallengeResponse(
            transaction_id=message.transaction_id,
            app_instance_id=self.app_instance_id,
            success=True,
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

        # Generate Round 1 values (G1, G2 are 65-byte EC points)
        g1, g2 = self.jpake_protocol.generate_round1()
        self.g1_point = g1
        self.g2_point = g2

        # Encode G1 into 165-byte ECJPAKEKeyKP format (Point + ZKP)
        jpake1a_data, _ = encode_jpake_round1_pair(g1, g2)

        self._set_state(AuthenticationState.JPAKE_ROUND1_SENT)

        return Jpake1aRequest(
            transaction_id=self._next_transaction_id(),
            app_instance_id=self.app_instance_id,
            central_challenge=jpake1a_data,
        )

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

        # Update app instance ID from request
        self.app_instance_id = message.app_instance_id

        # Decode the incoming 165-byte payload (app's JPake round 1b data)
        # Extract the EC point (first 65 bytes of the ECJPAKEKeyKP structure)
        point, _, _ = decode_ec_jpake_key_kp(message.central_challenge)

        # Store as G4 (the app's second public key in JPake protocol)
        # Note: G3 would have been received in a previous message (for full flow)
        self.g4_point = point

        # For SIMULATOR: Generate a valid placeholder EC point for G3 if not already set
        # In production, G3 would come from Jpake1aResponse message
        if self.g3_point is None and self.jpake_protocol:
            # Generate a valid EC point by using the JPake protocol's scalar mult
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import ec

            # Generate a temporary private key to get a valid point
            temp_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
            temp_public = temp_key.public_key()
            self.g3_point = temp_public.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint,
            )

        # Process Round 1 data in jpake_protocol so it can generate Round 2
        # SIMULATOR: ZKP verification is skipped
        if self.jpake_protocol and self.g3_point:
            self.jpake_protocol.process_round1(self.g3_point, self.g4_point)

        # Encode G2 into response (165-byte ECJPAKEKeyKP format)
        if not self.g2_point:
            raise ValueError("G2 not generated yet")

        _, jpake1b_data = encode_jpake_round1_pair(self.g1_point or b"", self.g2_point)

        self._set_state(AuthenticationState.JPAKE_ROUND1_COMPLETE)

        return Jpake1bResponse(
            transaction_id=message.transaction_id,
            app_instance_id=self.app_instance_id,
            central_challenge_hash=jpake1b_data,
        )

    def generate_jpake2(self) -> Jpake2Request:
        """Generate JPake Round 2 message.

        Returns:
            Jpake2 request message
        """
        logger.info("Generating JPake Round 2")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Generate Round 2 value (A is 65-byte EC point)
        a_value = self.jpake_protocol.generate_round2()
        self.a_point = a_value

        # Encode A into 165-byte ECJPAKEKeyKP format (Point + ZKP)
        jpake2_data = encode_jpake_round2(a_value)

        self._set_state(AuthenticationState.JPAKE_ROUND2_SENT)

        return Jpake2Request(
            transaction_id=self._next_transaction_id(),
            app_instance_id=self.app_instance_id,
            data=jpake2_data,
        )

    def handle_jpake2_response(self, message: Jpake2Response):
        """Handle JPake Round 2 response from app.

        Args:
            message: Jpake2 response
        """
        logger.info("Received JPake Round 2 response")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Update app instance ID from response
        self.app_instance_id = message.app_instance_id

        # Decode B value from the 165 or 168-byte payload
        b_value = decode_jpake_round2(message.data)
        self.b_point = b_value

        # Process Round 2 data in jpake_protocol so it can derive session key
        # SIMULATOR: ZKP verification is skipped, but we need to set B for key derivation
        self.jpake_protocol.process_round2(b_value)

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

        # challenge_param triggers session validation (input is always 0 in pumpx2)
        logger.debug(f"Challenge param: {message.challenge_param}")

        # Derive session key from EC-JPAKE
        _ = self.jpake_protocol.derive_session_key()

        logger.info("Session key successfully derived")

        # Generate device key nonce (random 8 bytes)
        device_key_nonce = secrets.token_bytes(8)
        # Reserved field (8 zero bytes as per pumpx2)
        device_key_reserved = b"\x00" * 8

        return Jpake3SessionKeyResponse(
            transaction_id=message.transaction_id,
            app_instance_id=self.app_instance_id,
            device_key_nonce=device_key_nonce,
            device_key_reserved=device_key_reserved,
        )

    def generate_jpake4(self) -> Jpake4KeyConfirmationRequest:
        """Generate JPake Round 4 key confirmation.

        Returns:
            Jpake4 key confirmation request
        """
        logger.info("Generating JPake Round 4 (key confirmation)")

        if not self.jpake_protocol:
            raise ValueError("JPake protocol not initialized")

        # Get session key
        session_key = self.jpake_protocol.get_session_key()
        if not session_key:
            raise ValueError("Session key not derived yet")

        # Generate nonce and reserved fields
        nonce = secrets.token_bytes(8)
        reserved = b"\x00" * 8  # 8 zero bytes as per pumpx2

        # Generate hash digest for key confirmation
        hash_digest = generate_jpake4_hash_digest(
            session_key=session_key, role="pump", nonce=nonce, reserved=reserved
        )

        self._set_state(AuthenticationState.KEY_CONFIRMATION_SENT)

        return Jpake4KeyConfirmationRequest(
            transaction_id=self._next_transaction_id(),
            app_instance_id=self.app_instance_id,
            nonce=nonce,
            reserved=reserved,
            hash_digest=hash_digest,
        )

    def handle_jpake4_response(self, message: Jpake4KeyConfirmationResponse):
        """Handle JPake Round 4 confirmation response.

        Args:
            message: Jpake4 confirmation response
        """
        logger.info("Received JPake Round 4 response")

        if not self.jpake_protocol:
            logger.error("JPake protocol not initialized")
            self._set_state(AuthenticationState.FAILED)
            return

        # Get session key for verification
        session_key = self.jpake_protocol.get_session_key()
        if not session_key:
            logger.error("Session key not available")
            self._set_state(AuthenticationState.FAILED)
            return

        # Verify the response hash_digest (SIMULATOR: simplified verification)
        # Production should use constant-time comparison and verify all exchanged points
        # For now, we accept the response if it has valid structure
        logger.debug(f"Received hash_digest: {message.hash_digest.hex()}")
        logger.debug(f"Nonce: {message.nonce.hex()}, Reserved: {message.reserved.hex()}")

        # Authentication successful!
        if self.current_device_address:
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

        logger.error("Authentication failed: no device address")
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
