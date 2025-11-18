"""Tests for protocol components."""

import pytest

from tandem_simulator.protocol.crc import (
    append_crc16,
    calculate_crc16,
    validate_crc16,
    verify_and_strip_crc16,
)
from tandem_simulator.protocol.crypto import (
    calculate_hmac_sha1,
    create_signed_message_auth,
    validate_signed_message,
)
from tandem_simulator.protocol.message import Message, MessageHeader, MessageRegistry
from tandem_simulator.protocol.messages.authentication import (
    CentralChallengeRequest,
    CentralChallengeResponse,
)
from tandem_simulator.protocol.messages.status import (
    ApiVersionRequest,
    ApiVersionResponse,
    CurrentBatteryResponse,
)
from tandem_simulator.protocol.packetizer import ControlPacketizer, Packetizer


def test_message_is_request():
    """Test message request/response detection."""
    msg = Message()
    msg.opcode = 0x10  # Even = request
    assert msg.is_request()
    assert not msg.is_response()

    msg.opcode = 0x11  # Odd = response
    assert msg.is_response()
    assert not msg.is_request()


def test_message_registry():
    """Test message registry."""

    class TestMessage(Message):
        opcode = 0x42

    MessageRegistry.register(0x42, TestMessage)
    msg_class = MessageRegistry.get_message_class(0x42)
    assert msg_class == TestMessage


def test_message_header_parse():
    """Test message header parsing."""
    data = bytes([0x10, 0x05, 0x0A])  # opcode=0x10, txid=5, length=10
    header = MessageHeader.parse(data)

    assert header.opcode == 0x10
    assert header.transaction_id == 0x05
    assert header.payload_length == 0x0A


def test_message_header_serialize():
    """Test message header serialization."""
    header = MessageHeader(opcode=0x20, transaction_id=0x03, payload_length=0x15)
    serialized = header.serialize()

    assert serialized == bytes([0x20, 0x03, 0x15])


def test_message_parse_and_serialize():
    """Test message parsing and serialization."""
    # Create a simple message
    msg = Message(transaction_id=7)
    msg.opcode = 0x10
    msg.payload = b"test_payload"

    # Serialize it
    serialized = msg.serialize()

    # Parse it back
    parsed = Message.parse(serialized)

    assert parsed.opcode == 0x10
    assert parsed.transaction_id == 7
    assert parsed.payload == b"test_payload"


def test_api_version_response():
    """Test API version response message."""
    msg = ApiVersionResponse(transaction_id=5, major=2, minor=3, patch=1)
    serialized = msg.serialize()

    # Parse it back
    parsed = ApiVersionResponse.parse(serialized)

    assert parsed.transaction_id == 5
    assert parsed.major == 2
    assert parsed.minor == 3
    assert parsed.patch == 1


def test_current_battery_response():
    """Test battery response message."""
    msg = CurrentBatteryResponse(transaction_id=10, battery_percent=75)
    serialized = msg.serialize()

    parsed = CurrentBatteryResponse.parse(serialized)

    assert parsed.transaction_id == 10
    assert parsed.battery_percent == 75


def test_packetizer_chunking():
    """Test message chunking."""
    packetizer = Packetizer(chunk_size=10)
    message = b"Hello, this is a test message!"

    chunks = packetizer.chunk_message(message)
    assert len(chunks) > 1
    assert all(len(chunk) <= 10 for chunk in chunks)

    # Verify we can reassemble
    reassembled = b"".join(chunks)
    assert reassembled == message


def test_packetizer_reassembly():
    """Test message reassembly with CRC validation."""
    # Create a test message
    msg = ApiVersionResponse(transaction_id=1, major=1, minor=0, patch=0)
    serialized = msg.serialize()

    # Add CRC
    with_crc = append_crc16(serialized)

    # Chunk it
    packetizer = Packetizer(chunk_size=10)
    chunks = packetizer.chunk_message(with_crc)

    # Reassemble
    reassembly_packetizer = Packetizer(chunk_size=10)
    reassembled = None

    for i, chunk in enumerate(chunks):
        result = reassembly_packetizer.add_chunk(chunk)
        if i < len(chunks) - 1:
            assert result is None  # Not complete yet
        else:
            reassembled = result  # Should be complete

    assert reassembled is not None
    assert reassembled == serialized


def test_control_packetizer():
    """Test control packetizer with larger chunks."""
    packetizer = ControlPacketizer()
    assert packetizer.chunk_size == 40

    message = b"A" * 100
    chunks = packetizer.chunk_message(message)

    assert len(chunks) == 3  # 40 + 40 + 20
    assert all(len(chunk) <= 40 for chunk in chunks)


def test_crc16_calculation():
    """Test CRC16 calculation."""
    data = b"test data"
    crc = calculate_crc16(data)

    assert isinstance(crc, int)
    assert 0 <= crc <= 0xFFFF

    # Test validation
    assert validate_crc16(data, crc)

    # Test with wrong CRC
    assert not validate_crc16(data, crc + 1)


def test_crc16_append_and_verify():
    """Test appending and verifying CRC16."""
    data = b"Hello, World!"
    with_crc = append_crc16(data)

    assert len(with_crc) == len(data) + 2

    # Verify and strip
    is_valid, stripped = verify_and_strip_crc16(with_crc)
    assert is_valid
    assert stripped == data


def test_hmac_calculation():
    """Test HMAC-SHA1 calculation."""
    key = b"secret_key_12345"
    message = b"test message"

    hmac_sig = calculate_hmac_sha1(key, message)

    assert len(hmac_sig) == 20  # SHA1 produces 20 bytes


def test_signed_message_auth():
    """Test signed message authentication."""
    key = b"session_key_test"
    message = b"important message"

    # Create auth block
    auth_block = create_signed_message_auth(key, message, timestamp=12345)

    assert len(auth_block) == 24  # 4 bytes timestamp + 20 bytes HMAC

    # Validate it
    is_valid, timestamp = validate_signed_message(key, message, auth_block)

    assert is_valid
    assert timestamp == 12345


def test_message_registry_parse():
    """Test parsing messages using registry."""
    # Create an API version response
    msg = ApiVersionResponse(transaction_id=3, major=1, minor=2, patch=3)
    serialized = msg.serialize()

    # Parse using registry
    parsed = MessageRegistry.parse_message(serialized)

    assert isinstance(parsed, ApiVersionResponse)
    assert parsed.transaction_id == 3
    assert parsed.major == 1
    assert parsed.minor == 2
    assert parsed.patch == 3


def test_central_challenge_messages():
    """Test central challenge request and response."""
    # Test request
    challenge_data = b"challenge_123456"
    req = CentralChallengeRequest(transaction_id=1, challenge=challenge_data)
    serialized = req.serialize()

    parsed = CentralChallengeRequest.parse(serialized)
    assert parsed.challenge == challenge_data

    # Test response
    response_data = b"response_654321"
    resp = CentralChallengeResponse(transaction_id=2, response=response_data)
    serialized = resp.serialize()

    parsed = CentralChallengeResponse.parse(serialized)
    assert parsed.response == response_data
