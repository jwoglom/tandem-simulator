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

    # CentralChallengeRequest: app_instance_id (2 bytes) + central_challenge (8 bytes)
    request = CentralChallengeRequest(
        transaction_id=1, app_instance_id=1234, central_challenge=b"testchal"
    )
    response = auth.handle_central_challenge_request(request)

    assert response.transaction_id == 1
    assert response.app_instance_id == 1234
    assert len(response.central_challenge_hash) == 20  # SHA1 hash
    assert len(response.hmac_key) == 8
    assert auth.state == AuthenticationState.CENTRAL_CHALLENGE_SENT


def test_authenticator_handle_pump_challenge():
    """Test handling pump challenge request."""
    auth = Authenticator()
    auth.start_pairing("AA:BB:CC:DD:EE:FF")

    # PumpChallengeRequest needs app_instance_id
    request = PumpChallengeRequest(transaction_id=2, app_instance_id=1234)
    response = auth.handle_pump_challenge_request(request)

    assert response.transaction_id == 2
    assert response.app_instance_id == 1234
    assert response.success is True
    assert auth.state == AuthenticationState.PUMP_CHALLENGE_READY


def test_authenticator_jpake_flow():
    """Test complete JPake authentication flow with new message structures."""
    from tandem_simulator.authentication.jpake_encoding import (
        decode_ec_jpake_key_kp,
        encode_ec_jpake_key_kp,
        encode_jpake_round2,
    )

    auth = Authenticator()
    pairing_code = auth.start_pairing("AA:BB:CC:DD:EE:FF")

    # Create app-side JPake to generate valid EC points
    app_jpake = JPakeProtocol(pairing_code=pairing_code, role="app")

    # Round 1a: Pump generates (165-byte encoded message)
    jpake1a_req = auth.generate_jpake1a()
    assert auth.state == AuthenticationState.JPAKE_ROUND1_SENT
    assert len(jpake1a_req.central_challenge) == 165

    # Round 1b: App generates valid EC points, pump receives
    g3, g4 = app_jpake.generate_round1()  # Generate valid EC points
    jpake1b_data = encode_ec_jpake_key_kp(g4)  # Encode G4 with ZKP

    jpake1b_req = Jpake1bRequest(
        transaction_id=2, app_instance_id=auth.app_instance_id, central_challenge=jpake1b_data
    )
    jpake1b_resp = auth.handle_jpake1b_request(jpake1b_req)
    assert len(jpake1b_resp.central_challenge_hash) == 165  # Response is 165 bytes
    assert auth.state == AuthenticationState.JPAKE_ROUND1_COMPLETE

    # App processes G1, G2 from pump
    # Decode G1 from jpake1a, G2 from jpake1b response
    g1_point, _, _ = decode_ec_jpake_key_kp(jpake1a_req.central_challenge)
    g2_point, _, _ = decode_ec_jpake_key_kp(jpake1b_resp.central_challenge_hash)
    app_jpake.process_round1(g1_point, g2_point)

    # Round 2: Pump generates A (165-byte encoded message)
    jpake2_req = auth.generate_jpake2()
    assert auth.state == AuthenticationState.JPAKE_ROUND2_SENT
    assert len(jpake2_req.data) == 165

    # App generates B and pump processes it
    b_value = app_jpake.generate_round2()  # Generate valid B point
    b_data = encode_jpake_round2(b_value)
    jpake2_resp = Jpake2Response(
        transaction_id=3, app_instance_id=auth.app_instance_id, data=b_data
    )
    auth.handle_jpake2_response(jpake2_resp)
    assert auth.state == AuthenticationState.JPAKE_ROUND2_COMPLETE

    # Round 3: Session key exchange
    jpake3_req = Jpake3SessionKeyRequest(transaction_id=4, challenge_param=0)
    jpake3_resp = auth.handle_jpake3_request(jpake3_req)
    assert len(jpake3_resp.device_key_nonce) == 8
    assert jpake3_resp.device_key_reserved == b"\x00" * 8

    # Round 4: Final confirmation
    jpake4_req = auth.generate_jpake4()
    assert auth.state == AuthenticationState.KEY_CONFIRMATION_SENT
    assert len(jpake4_req.hash_digest) == 32  # SHA256

    # Complete authentication (use placeholder values for response)
    import secrets

    jpake4_resp = Jpake4KeyConfirmationResponse(
        transaction_id=5,
        app_instance_id=auth.app_instance_id,
        nonce=secrets.token_bytes(8),
        reserved=b"\x00" * 8,
        hash_digest=secrets.token_bytes(32),
    )
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
    """Test JPake1a message serialization with new structure."""
    import secrets

    from tandem_simulator.authentication.jpake_encoding import encode_ec_jpake_key_kp

    # Create a 165-byte encoded payload (ECJPAKEKeyKP structure)
    dummy_point = b"\x04" + secrets.token_bytes(64)  # SEC1 uncompressed point
    central_challenge = encode_ec_jpake_key_kp(dummy_point)

    msg = Jpake1aRequest(
        transaction_id=5, app_instance_id=1234, central_challenge=central_challenge
    )
    serialized = msg.serialize()

    # Parse it back
    parsed = Jpake1aRequest.parse(serialized)
    assert parsed.transaction_id == 5
    assert parsed.app_instance_id == 1234
    assert parsed.central_challenge == central_challenge
    assert len(parsed.central_challenge) == 165


def test_jpake2_message_serialization():
    """Test JPake2 message serialization with new structure."""
    import secrets

    from tandem_simulator.authentication.jpake_encoding import encode_jpake_round2

    # Create a 165-byte encoded payload (ECJPAKEKeyKP structure)
    dummy_point = b"\x04" + secrets.token_bytes(64)
    data = encode_jpake_round2(dummy_point)

    msg = Jpake2Request(transaction_id=7, app_instance_id=5678, data=data)
    serialized = msg.serialize()

    parsed = Jpake2Request.parse(serialized)
    assert parsed.transaction_id == 7
    assert parsed.app_instance_id == 5678
    assert parsed.data == data
    assert len(parsed.data) == 165
