"""Tests for authentication components (Milestone 3)."""

import os
import tempfile
import time
from datetime import datetime, timedelta

import pytest

from tandem_simulator.authentication.authenticator import AuthenticationState, Authenticator
from tandem_simulator.authentication.jpake import JPakeProtocol
from tandem_simulator.authentication.pairing import PairingManager
from tandem_simulator.authentication.session import Session, SessionManager
from tandem_simulator.protocol.messages import (
    CentralChallengeRequest,
    Jpake1aRequest,
    Jpake1bRequest,
    Jpake2Request,
    Jpake2Response,
    Jpake3SessionKeyRequest,
    Jpake4KeyConfirmationResponse,
    PumpChallengeRequest,
)

# JPake Protocol Tests


def test_jpake_initialization():
    """Test JPake protocol initialization."""
    jpake = JPakeProtocol(pairing_code="123456", role="pump")
    assert jpake.pairing_code == "123456"
    assert jpake.role == "pump"
    assert jpake.session_key is None


def test_jpake_generate_round1_pump():
    """Test JPake Round 1 generation for pump."""
    jpake = JPakeProtocol(pairing_code="123456", role="pump")
    g1, g2 = jpake.generate_round1()

    assert len(g1) > 0
    assert len(g2) > 0
    assert jpake.G1 is not None
    assert jpake.G2 is not None


def test_jpake_generate_round1_app():
    """Test JPake Round 1 generation for app."""
    jpake = JPakeProtocol(pairing_code="123456", role="app")
    g3, g4 = jpake.generate_round1()

    assert len(g3) > 0
    assert len(g4) > 0
    assert jpake.G3 is not None
    assert jpake.G4 is not None


def test_jpake_full_exchange():
    """Test complete JPake key exchange between pump and app."""
    pairing_code = "123456"

    # Create pump and app instances
    pump = JPakeProtocol(pairing_code=pairing_code, role="pump")
    app = JPakeProtocol(pairing_code=pairing_code, role="app")

    # Round 1a: Pump generates
    g1, g2 = pump.generate_round1()

    # Round 1a: App receives
    app.process_round1(g1, g2)

    # Round 1b: App generates
    g3, g4 = app.generate_round1()

    # Round 1b: Pump receives
    pump.process_round1(g3, g4)

    # Round 2: Pump generates A
    a_value = pump.generate_round2()

    # Round 2: App generates B
    b_value = app.generate_round2()

    # Exchange Round 2 values
    pump.process_round2(b_value)
    app.process_round2(a_value)

    # Both derive session key
    pump_key = pump.derive_session_key()
    app_key = app.derive_session_key()

    # Keys should match
    assert pump_key == app_key
    assert len(pump_key) == 32  # 256-bit key

    # Key confirmation
    pump_confirmation = pump.generate_key_confirmation()
    app_confirmation = app.generate_key_confirmation()

    # Verify confirmations
    assert app.verify_key_confirmation(pump_confirmation, "pump")
    assert pump.verify_key_confirmation(app_confirmation, "app")


def test_jpake_invalid_confirmation():
    """Test JPake with invalid key confirmation."""
    pairing_code = "123456"
    pump = JPakeProtocol(pairing_code=pairing_code, role="pump")
    app = JPakeProtocol(pairing_code=pairing_code, role="app")

    # Complete exchange
    g1, g2 = pump.generate_round1()
    app.process_round1(g1, g2)
    g3, g4 = app.generate_round1()
    pump.process_round1(g3, g4)
    a_value = pump.generate_round2()
    b_value = app.generate_round2()
    pump.process_round2(b_value)
    app.process_round2(a_value)
    pump.derive_session_key()
    app.derive_session_key()

    # Invalid confirmation should fail
    invalid_confirmation = b"invalid_confirmation_data_xyz"
    assert not pump.verify_key_confirmation(invalid_confirmation, "app")


# Pairing Manager Tests


def test_pairing_manager_generate_code():
    """Test pairing code generation."""
    manager = PairingManager()
    code = manager.generate_pairing_code()

    assert len(code) == 6
    assert code.isdigit()
    assert manager.get_current_code() == code


def test_pairing_manager_verify_code():
    """Test pairing code verification."""
    manager = PairingManager()
    code = manager.generate_pairing_code()

    valid, msg = manager.verify_pairing_code(code)
    assert valid
    assert msg == ""


def test_pairing_manager_verify_invalid_code():
    """Test pairing code verification with invalid code."""
    manager = PairingManager()
    _ = manager.generate_pairing_code()

    valid, msg = manager.verify_pairing_code("999999")
    assert not valid
    assert "Invalid code" in msg


def test_pairing_manager_timeout():
    """Test pairing code timeout."""
    manager = PairingManager(timeout_seconds=1)
    _ = manager.generate_pairing_code()

    # Wait for timeout
    time.sleep(1.1)

    assert manager.is_code_expired()
    assert manager.get_current_code() is None


def test_pairing_manager_max_attempts():
    """Test max pairing attempts."""
    manager = PairingManager()
    manager.max_attempts = 3
    _ = manager.generate_pairing_code()

    # Try with wrong code 3 times
    for i in range(3):
        valid, msg = manager.verify_pairing_code("999999")
        assert not valid

    # Code should be cleared after max attempts
    assert manager.current_pairing_code is None


def test_pairing_manager_refresh():
    """Test refreshing pairing code."""
    manager = PairingManager()
    code1 = manager.generate_pairing_code()
    code2 = manager.refresh_code()

    assert code1 != code2
    assert manager.get_current_code() == code2


# Session Manager Tests


def test_session_manager_create_session():
    """Test creating a new session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "test_sessions.json")
        manager = SessionManager(storage_path=storage_path)

        session_key = b"test_session_key_32_bytes_long!!"
        session = manager.create_session("AA:BB:CC:DD:EE:FF", session_key)

        assert session.device_address == "AA:BB:CC:DD:EE:FF"
        assert manager.get_session_key("AA:BB:CC:DD:EE:FF") == session_key


def test_session_manager_persistence():
    """Test session persistence to disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "test_sessions.json")

        # Create session
        manager1 = SessionManager(storage_path=storage_path)
        session_key = b"test_session_key_32_bytes_long!!"
        manager1.create_session("AA:BB:CC:DD:EE:FF", session_key, "Test Device")

        # Load in new instance
        manager2 = SessionManager(storage_path=storage_path)
        loaded_key = manager2.get_session_key("AA:BB:CC:DD:EE:FF")

        assert loaded_key == session_key
        assert manager2.is_device_paired("AA:BB:CC:DD:EE:FF")


def test_session_manager_remove_session():
    """Test removing a session."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "test_sessions.json")
        manager = SessionManager(storage_path=storage_path)

        session_key = b"test_session_key_32_bytes_long!!"
        manager.create_session("AA:BB:CC:DD:EE:FF", session_key)

        assert manager.is_device_paired("AA:BB:CC:DD:EE:FF")

        manager.remove_session("AA:BB:CC:DD:EE:FF")

        assert not manager.is_device_paired("AA:BB:CC:DD:EE:FF")


def test_session_manager_get_paired_devices():
    """Test getting list of paired devices."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "test_sessions.json")
        manager = SessionManager(storage_path=storage_path)

        manager.create_session("AA:BB:CC:DD:EE:11", b"key1" * 8, "Device 1")
        manager.create_session("AA:BB:CC:DD:EE:22", b"key2" * 8, "Device 2")

        devices = manager.get_paired_devices()

        assert len(devices) == 2
        addresses = [d["address"] for d in devices]
        assert "AA:BB:CC:DD:EE:11" in addresses
        assert "AA:BB:CC:DD:EE:22" in addresses


# Authenticator Tests


def test_authenticator_start_pairing():
    """Test starting the pairing process."""
    auth = Authenticator()
    code = auth.start_pairing("AA:BB:CC:DD:EE:FF")

    assert len(code) == 6
    assert code.isdigit()
    assert auth.state == AuthenticationState.WAITING_FOR_PAIRING_CODE
    assert auth.current_device_address == "AA:BB:CC:DD:EE:FF"


def test_authenticator_handle_central_challenge():
    """Test handling central challenge request."""
    auth = Authenticator()
    auth.start_pairing("AA:BB:CC:DD:EE:FF")

    request = CentralChallengeRequest(transaction_id=1, challenge=b"test_challenge_123")
    response = auth.handle_central_challenge_request(request)

    assert response.transaction_id == 1
    assert len(response.response) > 0
    assert auth.state == AuthenticationState.CENTRAL_CHALLENGE_SENT


def test_authenticator_handle_pump_challenge():
    """Test handling pump challenge request."""
    auth = Authenticator()
    auth.start_pairing("AA:BB:CC:DD:EE:FF")

    request = PumpChallengeRequest(transaction_id=2)
    response = auth.handle_pump_challenge_request(request)

    assert response.transaction_id == 2
    assert len(response.challenge) > 0
    assert auth.state == AuthenticationState.PUMP_CHALLENGE_READY


def test_authenticator_jpake_flow():
    """Test complete JPake authentication flow."""
    auth = Authenticator()
    pairing_code = auth.start_pairing("AA:BB:CC:DD:EE:FF")

    # Simulate app side
    app_jpake = JPakeProtocol(pairing_code=pairing_code, role="app")

    # Round 1a: Pump generates
    jpake1a_req = auth.generate_jpake1a()
    assert auth.state == AuthenticationState.JPAKE_ROUND1_SENT

    # App processes Round 1a
    app_jpake.process_round1(jpake1a_req.g1, jpake1a_req.g2)

    # Round 1b: App generates, pump receives
    g3, g4 = app_jpake.generate_round1()
    jpake1b_req = Jpake1bRequest(transaction_id=2, g3=g3, g4=g4)
    jpake1b_resp = auth.handle_jpake1b_request(jpake1b_req)
    assert jpake1b_resp.status == 0
    assert auth.state == AuthenticationState.JPAKE_ROUND1_COMPLETE

    # Round 2: Pump generates A
    jpake2_req = auth.generate_jpake2()
    assert auth.state == AuthenticationState.JPAKE_ROUND2_SENT

    # App processes A and generates B
    app_jpake.process_round2(jpake2_req.a_value)
    b_value = app_jpake.generate_round2()

    # Pump processes B
    jpake2_resp = Jpake2Response(transaction_id=3, b_value=b_value)
    auth.handle_jpake2_response(jpake2_resp)
    assert auth.state == AuthenticationState.JPAKE_ROUND2_COMPLETE

    # Derive session keys
    app_jpake.derive_session_key()
    app_confirmation = app_jpake.generate_key_confirmation()

    # Round 3: Key confirmation
    jpake3_req = Jpake3SessionKeyRequest(transaction_id=4, key_confirmation=app_confirmation)
    jpake3_resp = auth.handle_jpake3_request(jpake3_req)
    assert jpake3_resp.status == 0

    # Round 4: Final confirmation
    jpake4_req = auth.generate_jpake4()
    assert auth.state == AuthenticationState.KEY_CONFIRMATION_SENT

    # App verifies pump's confirmation
    assert app_jpake.verify_key_confirmation(jpake4_req.confirmation, "pump")

    # Complete authentication
    jpake4_resp = Jpake4KeyConfirmationResponse(transaction_id=5, status=0)
    auth.handle_jpake4_response(jpake4_resp)

    # Should be authenticated now
    assert auth.state == AuthenticationState.AUTHENTICATED
    assert auth.is_authenticated("AA:BB:CC:DD:EE:FF")


def test_authenticator_get_status():
    """Test getting authenticator status."""
    auth = Authenticator()
    status = auth.get_status()

    assert "state" in status
    assert "pairing_status" in status
    assert "session_stats" in status
    assert status["state"] == "idle"


# JPake Message Tests


def test_jpake1a_message_serialization():
    """Test JPake1a message serialization."""
    msg = Jpake1aRequest(transaction_id=5, g1=b"test_g1_data", g2=b"test_g2_data")
    serialized = msg.serialize()

    # Parse it back
    parsed = Jpake1aRequest.parse(serialized)
    assert parsed.transaction_id == 5
    assert parsed.g1 == b"test_g1_data"
    assert parsed.g2 == b"test_g2_data"


def test_jpake2_message_serialization():
    """Test JPake2 message serialization."""
    msg = Jpake2Request(transaction_id=7, a_value=b"test_a_value_data")
    serialized = msg.serialize()

    parsed = Jpake2Request.parse(serialized)
    assert parsed.transaction_id == 7
    assert parsed.a_value == b"test_a_value_data"
