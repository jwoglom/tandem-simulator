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


#
# JPake Authentication Messages (Milestone 3)
#
# NOTE: Opcodes for JPake messages are assigned sequentially here.
# These may need adjustment based on actual Tandem protocol analysis.
#


class Jpake1aRequest(Message):
    """JPake Round 1a request message (pump sends to app).

    Opcode: 0x10 (placeholder - verify with actual protocol)

    Round 1a: Pump sends its first ephemeral public keys (G1, G2) with ZKPs.
    """

    opcode = 0x10

    def __init__(self, transaction_id: int = 0, g1: bytes = b"", g2: bytes = b""):
        """Initialize JPake round 1a request.

        Args:
            transaction_id: Transaction ID
            g1: First ephemeral public key (G1 = g^x1)
            g2: Second ephemeral public key (G2 = g^x2)
        """
        super().__init__(transaction_id)
        self.g1 = g1
        self.g2 = g2

    def parse_payload(self, payload: bytes) -> None:
        """Parse JPake 1a payload.

        Payload format: [g1_length(2)] [g1] [g2_length(2)] [g2]

        Args:
            payload: Raw payload bytes
        """
        if len(payload) < 4:
            return

        # Parse G1
        g1_len = int.from_bytes(payload[0:2], "big")
        g1_start = 2
        g1_end = g1_start + g1_len
        self.g1 = payload[g1_start:g1_end]

        # Parse G2
        if len(payload) > g1_end + 2:
            g2_len = int.from_bytes(payload[g1_end : g1_end + 2], "big")
            g2_start = g1_end + 2
            g2_end = g2_start + g2_len
            self.g2 = payload[g2_start:g2_end]

    def build_payload(self) -> bytes:
        """Build JPake 1a payload.

        Returns:
            Payload bytes
        """
        payload = b""
        payload += len(self.g1).to_bytes(2, "big") + self.g1
        payload += len(self.g2).to_bytes(2, "big") + self.g2
        return payload


class Jpake1aResponse(Message):
    """JPake Round 1a response message (app acknowledges).

    Opcode: 0x11 (placeholder - verify with actual protocol)

    Simple acknowledgment of round 1a.
    """

    opcode = 0x11

    def __init__(self, transaction_id: int = 0, status: int = 0):
        """Initialize JPake round 1a response.

        Args:
            transaction_id: Transaction ID
            status: Status code (0 = success)
        """
        super().__init__(transaction_id)
        self.status = status

    def parse_payload(self, payload: bytes) -> None:
        """Parse status from payload.

        Args:
            payload: Raw payload bytes
        """
        if len(payload) >= 1:
            self.status = payload[0]

    def build_payload(self) -> bytes:
        """Build status payload.

        Returns:
            Status byte
        """
        return bytes([self.status])


class Jpake1bRequest(Message):
    """JPake Round 1b request message (app sends to pump).

    Opcode: 0x12 (placeholder - verify with actual protocol)

    Round 1b: App sends its first ephemeral public keys (G3, G4) with ZKPs.
    """

    opcode = 0x12

    def __init__(self, transaction_id: int = 0, g3: bytes = b"", g4: bytes = b""):
        """Initialize JPake round 1b request.

        Args:
            transaction_id: Transaction ID
            g3: Third ephemeral public key (G3 = g^x3)
            g4: Fourth ephemeral public key (G4 = g^x4)
        """
        super().__init__(transaction_id)
        self.g3 = g3
        self.g4 = g4

    def parse_payload(self, payload: bytes) -> None:
        """Parse JPake 1b payload.

        Args:
            payload: Raw payload bytes
        """
        if len(payload) < 4:
            return

        # Parse G3
        g3_len = int.from_bytes(payload[0:2], "big")
        g3_start = 2
        g3_end = g3_start + g3_len
        self.g3 = payload[g3_start:g3_end]

        # Parse G4
        if len(payload) > g3_end + 2:
            g4_len = int.from_bytes(payload[g3_end : g3_end + 2], "big")
            g4_start = g3_end + 2
            g4_end = g4_start + g4_len
            self.g4 = payload[g4_start:g4_end]

    def build_payload(self) -> bytes:
        """Build JPake 1b payload.

        Returns:
            Payload bytes
        """
        payload = b""
        payload += len(self.g3).to_bytes(2, "big") + self.g3
        payload += len(self.g4).to_bytes(2, "big") + self.g4
        return payload


class Jpake1bResponse(Message):
    """JPake Round 1b response message (pump acknowledges).

    Opcode: 0x13 (placeholder - verify with actual protocol)
    """

    opcode = 0x13

    def __init__(self, transaction_id: int = 0, status: int = 0):
        """Initialize JPake round 1b response.

        Args:
            transaction_id: Transaction ID
            status: Status code (0 = success)
        """
        super().__init__(transaction_id)
        self.status = status

    def parse_payload(self, payload: bytes) -> None:
        """Parse status from payload.

        Args:
            payload: Raw payload bytes
        """
        if len(payload) >= 1:
            self.status = payload[0]

    def build_payload(self) -> bytes:
        """Build status payload.

        Returns:
            Status byte
        """
        return bytes([self.status])


class Jpake2Request(Message):
    """JPake Round 2 request message (pump sends to app).

    Opcode: 0x14 (placeholder - verify with actual protocol)

    Round 2: Pump sends A = (G1*G3*G4)^(x2*s) with ZKP.
    """

    opcode = 0x14

    def __init__(self, transaction_id: int = 0, a_value: bytes = b""):
        """Initialize JPake round 2 request.

        Args:
            transaction_id: Transaction ID
            a_value: A value with ZKP
        """
        super().__init__(transaction_id)
        self.a_value = a_value

    def parse_payload(self, payload: bytes) -> None:
        """Parse JPake 2 payload.

        Args:
            payload: Raw payload bytes
        """
        self.a_value = payload

    def build_payload(self) -> bytes:
        """Build JPake 2 payload.

        Returns:
            A value bytes
        """
        return self.a_value


class Jpake2Response(Message):
    """JPake Round 2 response message (app sends to pump).

    Opcode: 0x15 (placeholder - verify with actual protocol)

    Round 2: App sends B = (G1*G2*G3)^(x4*s) with ZKP.
    """

    opcode = 0x15

    def __init__(self, transaction_id: int = 0, b_value: bytes = b""):
        """Initialize JPake round 2 response.

        Args:
            transaction_id: Transaction ID
            b_value: B value with ZKP
        """
        super().__init__(transaction_id)
        self.b_value = b_value

    def parse_payload(self, payload: bytes) -> None:
        """Parse JPake 2 response payload.

        Args:
            payload: Raw payload bytes
        """
        self.b_value = payload

    def build_payload(self) -> bytes:
        """Build JPake 2 response payload.

        Returns:
            B value bytes
        """
        return self.b_value


class Jpake3SessionKeyRequest(Message):
    """JPake Round 3 session key request (app sends key confirmation).

    Opcode: 0x16 (placeholder - verify with actual protocol)

    Round 3: App sends confirmation of derived session key.
    """

    opcode = 0x16

    def __init__(self, transaction_id: int = 0, key_confirmation: bytes = b""):
        """Initialize JPake round 3 request.

        Args:
            transaction_id: Transaction ID
            key_confirmation: Key confirmation value
        """
        super().__init__(transaction_id)
        self.key_confirmation = key_confirmation

    def parse_payload(self, payload: bytes) -> None:
        """Parse key confirmation from payload.

        Args:
            payload: Raw payload bytes
        """
        self.key_confirmation = payload

    def build_payload(self) -> bytes:
        """Build key confirmation payload.

        Returns:
            Key confirmation bytes
        """
        return self.key_confirmation


class Jpake3SessionKeyResponse(Message):
    """JPake Round 3 session key response (pump acknowledges).

    Opcode: 0x17 (placeholder - verify with actual protocol)
    """

    opcode = 0x17

    def __init__(self, transaction_id: int = 0, status: int = 0):
        """Initialize JPake round 3 response.

        Args:
            transaction_id: Transaction ID
            status: Status code (0 = success, non-zero = failure)
        """
        super().__init__(transaction_id)
        self.status = status

    def parse_payload(self, payload: bytes) -> None:
        """Parse status from payload.

        Args:
            payload: Raw payload bytes
        """
        if len(payload) >= 1:
            self.status = payload[0]

    def build_payload(self) -> bytes:
        """Build status payload.

        Returns:
            Status byte
        """
        return bytes([self.status])


class Jpake4KeyConfirmationRequest(Message):
    """JPake Round 4 key confirmation request (pump sends final confirmation).

    Opcode: 0x18 (placeholder - verify with actual protocol)

    Round 4: Pump sends its own key confirmation.
    """

    opcode = 0x18

    def __init__(self, transaction_id: int = 0, confirmation: bytes = b""):
        """Initialize JPake round 4 request.

        Args:
            transaction_id: Transaction ID
            confirmation: Pump's key confirmation value
        """
        super().__init__(transaction_id)
        self.confirmation = confirmation

    def parse_payload(self, payload: bytes) -> None:
        """Parse confirmation from payload.

        Args:
            payload: Raw payload bytes
        """
        self.confirmation = payload

    def build_payload(self) -> bytes:
        """Build confirmation payload.

        Returns:
            Confirmation bytes
        """
        return self.confirmation


class Jpake4KeyConfirmationResponse(Message):
    """JPake Round 4 key confirmation response (app acknowledges completion).

    Opcode: 0x19 (placeholder - verify with actual protocol)

    Final acknowledgment - authentication complete.
    """

    opcode = 0x19

    def __init__(self, transaction_id: int = 0, status: int = 0):
        """Initialize JPake round 4 response.

        Args:
            transaction_id: Transaction ID
            status: Status code (0 = success, authentication complete)
        """
        super().__init__(transaction_id)
        self.status = status

    def parse_payload(self, payload: bytes) -> None:
        """Parse status from payload.

        Args:
            payload: Raw payload bytes
        """
        if len(payload) >= 1:
            self.status = payload[0]

    def build_payload(self) -> bytes:
        """Build status payload.

        Returns:
            Status byte
        """
        return bytes([self.status])


# Register authentication messages
MessageRegistry.register(CentralChallengeRequest.opcode, CentralChallengeRequest)
MessageRegistry.register(CentralChallengeResponse.opcode, CentralChallengeResponse)
MessageRegistry.register(PumpChallengeRequest.opcode, PumpChallengeRequest)
MessageRegistry.register(PumpChallengeResponse.opcode, PumpChallengeResponse)

# Register JPake messages
MessageRegistry.register(Jpake1aRequest.opcode, Jpake1aRequest)
MessageRegistry.register(Jpake1aResponse.opcode, Jpake1aResponse)
MessageRegistry.register(Jpake1bRequest.opcode, Jpake1bRequest)
MessageRegistry.register(Jpake1bResponse.opcode, Jpake1bResponse)
MessageRegistry.register(Jpake2Request.opcode, Jpake2Request)
MessageRegistry.register(Jpake2Response.opcode, Jpake2Response)
MessageRegistry.register(Jpake3SessionKeyRequest.opcode, Jpake3SessionKeyRequest)
MessageRegistry.register(Jpake3SessionKeyResponse.opcode, Jpake3SessionKeyResponse)
MessageRegistry.register(Jpake4KeyConfirmationRequest.opcode, Jpake4KeyConfirmationRequest)
MessageRegistry.register(Jpake4KeyConfirmationResponse.opcode, Jpake4KeyConfirmationResponse)
