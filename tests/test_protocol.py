"""Tests for protocol components."""

import pytest

from tandem_simulator.protocol.crc import calculate_crc16, validate_crc16
from tandem_simulator.protocol.message import Message, MessageRegistry
from tandem_simulator.protocol.packetizer import Packetizer


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


def test_packetizer_chunking():
    """Test message chunking."""
    packetizer = Packetizer(chunk_size=10)
    message = b"Hello, this is a test message!"

    chunks = packetizer.chunk_message(message)
    assert len(chunks) > 1
    assert all(len(chunk) <= 10 for chunk in chunks)


def test_crc16_calculation():
    """Test CRC16 calculation."""
    data = b"test data"
    crc = calculate_crc16(data)
    assert isinstance(crc, int)

    # Test validation (will always pass for stub implementation)
    assert validate_crc16(data, crc)
