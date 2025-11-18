"""Authentication and pairing message implementations.

This module implements the authentication message types used in the
JPake pairing and challenge-response flows.

Milestone 2 deliverable (stub implementations - full JPake in Milestone 3).
"""

from tandem_simulator.protocol.message import Message, MessageRegistry


class CentralChallengeRequest(Message):
    """Central challenge request message.

    Opcode: 0x00 (example - verify with PumpX2)

    Initiates authentication by sending a challenge from the central device.
    """

    opcode = 0x00

    def __init__(self, transaction_id: int = 0, challenge: bytes = b""):
        """Initialize central challenge request.

        Args:
            transaction_id: Transaction ID
            challenge: Challenge data (typically 16 bytes)
        """
        super().__init__(transaction_id)
        self.challenge = challenge

    def parse_payload(self, payload: bytes) -> None:
        """Parse challenge from payload.

        Args:
            payload: Raw payload bytes
        """
        self.challenge = payload

    def build_payload(self) -> bytes:
        """Build challenge payload.

        Returns:
            Challenge bytes
        """
        return self.challenge


class CentralChallengeResponse(Message):
    """Central challenge response message.

    Opcode: 0x01 (example - verify with PumpX2)

    Response to central challenge with pump's challenge response.
    """

    opcode = 0x01

    def __init__(self, transaction_id: int = 0, response: bytes = b""):
        """Initialize central challenge response.

        Args:
            transaction_id: Transaction ID
            response: Challenge response data
        """
        super().__init__(transaction_id)
        self.response = response

    def parse_payload(self, payload: bytes) -> None:
        """Parse response from payload.

        Args:
            payload: Raw payload bytes
        """
        self.response = payload

    def build_payload(self) -> bytes:
        """Build response payload.

        Returns:
            Response bytes
        """
        return self.response


class PumpChallengeRequest(Message):
    """Pump challenge request message.

    Opcode: 0x02 (example - verify with PumpX2)

    Request challenge from pump during authentication.
    """

    opcode = 0x02

    def __init__(self, transaction_id: int = 0):
        """Initialize pump challenge request.

        Args:
            transaction_id: Transaction ID
        """
        super().__init__(transaction_id)

    def build_payload(self) -> bytes:
        """Build empty payload.

        Returns:
            Empty bytes
        """
        return b""


class PumpChallengeResponse(Message):
    """Pump challenge response message.

    Opcode: 0x03 (example - verify with PumpX2)

    Response with pump's challenge data.
    """

    opcode = 0x03

    def __init__(self, transaction_id: int = 0, challenge: bytes = b""):
        """Initialize pump challenge response.

        Args:
            transaction_id: Transaction ID
            challenge: Pump's challenge data
        """
        super().__init__(transaction_id)
        self.challenge = challenge

    def parse_payload(self, payload: bytes) -> None:
        """Parse challenge from payload.

        Args:
            payload: Raw payload bytes
        """
        self.challenge = payload

    def build_payload(self) -> bytes:
        """Build challenge payload.

        Returns:
            Challenge bytes
        """
        return self.challenge


# Register authentication messages
MessageRegistry.register(CentralChallengeRequest.opcode, CentralChallengeRequest)
MessageRegistry.register(CentralChallengeResponse.opcode, CentralChallengeResponse)
MessageRegistry.register(PumpChallengeRequest.opcode, PumpChallengeRequest)
MessageRegistry.register(PumpChallengeResponse.opcode, PumpChallengeResponse)
