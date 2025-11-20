"""Protocol message implementations.

This package contains specific message type implementations for
the Tandem pump protocol, organized to match pumpX2 structure.

Milestone 4 - Restructured to match Java implementation.
"""

# Import all authentication messages
from tandem_simulator.protocol.messages.request.authentication import (
    CentralChallengeRequest,
    Jpake1aRequest,
    Jpake1bRequest,
    Jpake2Request,
    Jpake3SessionKeyRequest,
    Jpake4KeyConfirmationRequest,
    PumpChallengeRequest,
)

# Import all status messages
from tandem_simulator.protocol.messages.request.currentStatus import (
    ApiVersionRequest,
    CurrentBasalStatusRequest,
    CurrentBatteryV1Request,
    CurrentBolusStatusRequest,
    InsulinStatusRequest,
    PumpVersionRequest,
)
from tandem_simulator.protocol.messages.response.authentication import (
    CentralChallengeResponse,
    Jpake1aResponse,
    Jpake1bResponse,
    Jpake2Response,
    Jpake3SessionKeyResponse,
    Jpake4KeyConfirmationResponse,
    PumpChallengeResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus import (
    ApiVersionResponse,
    CurrentBasalStatusResponse,
    CurrentBatteryV1Response,
    CurrentBolusStatusResponse,
    InsulinStatusResponse,
    PumpVersionResponse,
)

__all__ = [
    # Authentication requests
    "CentralChallengeRequest",
    "Jpake1aRequest",
    "Jpake1bRequest",
    "Jpake2Request",
    "Jpake3SessionKeyRequest",
    "Jpake4KeyConfirmationRequest",
    "PumpChallengeRequest",
    # Authentication responses
    "CentralChallengeResponse",
    "Jpake1aResponse",
    "Jpake1bResponse",
    "Jpake2Response",
    "Jpake3SessionKeyResponse",
    "Jpake4KeyConfirmationResponse",
    "PumpChallengeResponse",
    # Status requests
    "ApiVersionRequest",
    "CurrentBasalStatusRequest",
    "CurrentBatteryV1Request",
    "CurrentBolusStatusRequest",
    "InsulinStatusRequest",
    "PumpVersionRequest",
    # Status responses
    "ApiVersionResponse",
    "CurrentBasalStatusResponse",
    "CurrentBatteryV1Response",
    "CurrentBolusStatusResponse",
    "InsulinStatusResponse",
    "PumpVersionResponse",
]
