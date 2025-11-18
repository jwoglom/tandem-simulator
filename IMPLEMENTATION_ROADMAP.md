# Tandem Simulator - Complete Implementation Roadmap

## Overview

This document outlines the complete implementation plan for bringing the tandem-simulator message implementations into exact alignment with pumpx2.

## Current Status (After Validation)

### ✅ Completed
- Comprehensive validation of all existing messages against pumpx2
- Fixed critical bug: InsulinStatusResponse now uses unsigned int16 (was signed)
- Added string helper functions (read_string, write_string)
- Validated directory structure requirements
- Generated detailed validation reports (AUTHENTICATION_VALIDATION_REPORT.md, CURRENTSTATUS_VALIDATION_REPORT.md)

### ⚠️ Partially Complete
- Current Status messages: 2/6 perfect, 2/6 partial, 2/6 stubs

### ✗ Needs Complete Rewrite
- Authentication messages: 0/14 match (all opcodes wrong, all field structures wrong)

---

## Phase 1: Critical Fixes (IMMEDIATE) ✅

**Status:** COMPLETE

1. ✅ InsulinStatusResponse: Changed read_int16_le() to read_uint16_le()
2. ✅ Added read_string() and write_string() helper functions

---

## Phase 2: Complete Status Message Implementations (HIGH PRIORITY)

### 2.1 CurrentBolusStatusResponse (15 bytes)
**File:** `/home/user/tandem-simulator/CurrentBolusStatusResponse_EXACT.py`

**Required Changes:**
```python
# Add enum
class CurrentBolusStatus(Enum):
    ALREADY_DELIVERED_OR_INVALID = 0
    DELIVERING = 1
    REQUESTING = 2

# Replace stub with 15-byte implementation
- Opcode: 45 (correct)
- Fields: status_id, bolus_id, timestamp, requested_volume, bolus_source_id, bolus_type_bitmask
- Byte offsets: 0, 1-2, 5-8, 9-12, 13, 14 (with 2-byte padding at 3-4)
```

### 2.2 PumpVersionResponse (48 bytes)
**File:** `/home/user/tandem-simulator/PumpVersionResponse_EXACT.py`

**Required Changes:**
```python
# Replace variable-length string stub with 48-byte binary structure
- Opcode: 85 (correct)
- Fields: arm_sw_ver, msp_sw_ver, config_a_bits, config_b_bits, serial_num,
          part_num, pump_rev, pcba_sn, pcba_rev, model_num
- All uint32 fields little-endian
- pump_rev and pcba_rev are 8-byte fixed-length null-padded strings
```

### 2.3 ApiVersionResponse Field Names (OPTIONAL)
- Consider renaming `major`/`minor` to `major_version`/`minor_version` to match Java
- OR document the naming convention difference
- **Decision:** Keep as-is for simplicity (works correctly, just different naming)

---

## Phase 3: Authentication Messages Complete Rewrite (HIGH PRIORITY)

**All 14 messages need complete rewrite with:**
1. Correct opcodes
2. Correct field structures
3. appInstanceId fields where required

### 3.1 Challenge Messages (4 messages)

#### CentralChallengeRequest
- ✗ Current opcode: 0x00 → ✓ Correct: 16 (0x10)
- ✗ Missing appInstanceId (2 bytes)
- ✗ challenge should be exactly 8 bytes

```python
class CentralChallengeRequest(Message):
    opcode = 16

    def __init__(self, transaction_id=0, app_instance_id=0, central_challenge=b''):
        # app_instance_id: uint16 (2 bytes)
        # central_challenge: bytes (8 bytes fixed)

    def build_payload(self):
        return write_uint16_le(self.app_instance_id) + self.central_challenge[:8]
```

#### CentralChallengeResponse
- ✗ Current opcode: 0x01 → ✓ Correct: 17 (0x11)
- ✗ Need 3 fields instead of 1 generic

```python
class CentralChallengeResponse(Message):
    opcode = 17

    def __init__(self, transaction_id=0, app_instance_id=0,
                 central_challenge_hash=b'', hmac_key=b''):
        # app_instance_id: uint16 (2 bytes)
        # central_challenge_hash: bytes (20 bytes)
        # hmac_key: bytes (8 bytes)

    def build_payload(self):
        return (write_uint16_le(self.app_instance_id) +
                self.central_challenge_hash[:20] +
                self.hmac_key[:8])
```

#### PumpChallengeRequest
- ✗ Current opcode: 0x02 → ✓ Correct: 18 (0x12)
- ✗ Empty payload → Should be 22 bytes

```python
class PumpChallengeRequest(Message):
    opcode = 18

    def __init__(self, transaction_id=0, app_instance_id=0, pump_challenge_hash=b''):
        # app_instance_id: uint16 (2 bytes)
        # pump_challenge_hash: bytes (20 bytes)
```

#### PumpChallengeResponse
- ✗ Current opcode: 0x03 → ✓ Correct: 19 (0x13)
- ✗ Generic challenge bytes → Should be 3 bytes: app_instance_id (2) + success bool (1)

```python
class PumpChallengeResponse(Message):
    opcode = 19

    def __init__(self, transaction_id=0, app_instance_id=0, success=False):
        # app_instance_id: uint16 (2 bytes)
        # success: bool (1 byte)
```

### 3.2 JPake Round 1 Messages (4 messages)

#### Jpake1aRequest
- ✗ Current opcode: 0x10 → ✓ Correct: 32 (0x20)
- ✗ Variable-length format → Fixed 167-byte format

```python
class Jpake1aRequest(Message):
    opcode = 32

    def __init__(self, transaction_id=0, app_instance_id=0, central_challenge=b''):
        # app_instance_id: uint16 (2 bytes)
        # central_challenge: bytes (165 bytes fixed)

    def build_payload(self):
        # Total: 167 bytes
        return write_uint16_le(self.app_instance_id) + self.central_challenge[:165]
```

#### Jpake1aResponse
- ✗ Current opcode: 0x11 → ✓ Correct: 33 (0x21)
- ✗ 1-byte status → 167-byte structure

```python
class Jpake1aResponse(Message):
    opcode = 33

    def __init__(self, transaction_id=0, app_instance_id=0, central_challenge_hash=b''):
        # app_instance_id: uint16 (2 bytes)
        # central_challenge_hash: bytes (165 bytes fixed)
```

#### Jpake1bRequest & Jpake1bResponse
- Similar structure to Jpake1a
- Opcodes: 34 (0x22) request, 35 (0x23) response
- Same 167-byte format

### 3.3 JPake Round 2 Messages (2 messages)

#### Jpake2Request
- ✗ Current opcode: 0x14 → ✓ Correct: 36 (0x24)
- ✗ Missing appInstanceId

#### Jpake2Response
- ✗ Current opcode: 0x15 → ✓ Correct: 37 (0x25)
- ✗ Missing appInstanceId

### 3.4 JPake Session Key Messages (2 messages)

#### Jpake3SessionKeyRequest
- ✗ Current opcode: 0x16 → ✓ Correct: 38 (0x26)
- ✗ Generic bytes → challengeParam (2-byte little-endian uint16)

```python
class Jpake3SessionKeyRequest(Message):
    opcode = 38

    def __init__(self, transaction_id=0, challenge_param=0):
        # challenge_param: uint16 (2 bytes) - NOT generic bytes!

    def build_payload(self):
        return write_uint16_le(self.challenge_param)
```

#### Jpake3SessionKeyResponse
- ✗ Current opcode: 0x17 → ✓ Correct: 39 (0x27)
- ✗ 1-byte status → 18-byte structure

```python
class Jpake3SessionKeyResponse(Message):
    opcode = 39

    def __init__(self, transaction_id=0, app_instance_id=0,
                 device_key_nonce=b'', device_key_reserved=b''):
        # app_instance_id: uint16 (2 bytes)
        # device_key_nonce: bytes (8 bytes)
        # device_key_reserved: bytes (8 bytes)
        # Total: 18 bytes
```

### 3.5 JPake Confirmation Messages (2 messages)

#### Jpake4KeyConfirmationRequest
- ✗ Current opcode: 0x18 → ✓ Correct: 40 (0x28)
- ✗ Generic bytes → 50-byte validated structure

```python
class Jpake4KeyConfirmationRequest(Message):
    opcode = 40

    def __init__(self, transaction_id=0, app_instance_id=0, nonce=b'',
                 reserved=b'', hash_digest=b''):
        # app_instance_id: uint16 (2 bytes)
        # nonce: bytes (8 bytes EXACTLY)
        # reserved: bytes (8 bytes EXACTLY)
        # hash_digest: bytes (32 bytes EXACTLY - SHA256)
        # Total: 50 bytes

    def validate(self):
        assert len(self.nonce) == 8
        assert len(self.reserved) == 8
        assert len(self.hash_digest) == 32
```

#### Jpake4KeyConfirmationResponse
- ✗ Current opcode: 0x19 → ✓ Correct: 41 (0x29)
- ✗ 1-byte status → 50-byte structure (same as request)

---

## Phase 4: Directory Restructuring (MEDIUM PRIORITY)

**Goal:** Match pumpx2 directory structure exactly

### Current Structure:
```
tandem_simulator/protocol/messages/
├── __init__.py
├── authentication.py  (all auth messages in one file)
└── status.py         (all status messages in one file)
```

### Target Structure (matching pumpx2):
```
tandem_simulator/protocol/messages/
├── __init__.py
├── request/
│   ├── __init__.py
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── CentralChallengeRequest.py
│   │   ├── Jpake1aRequest.py
│   │   ├── Jpake1bRequest.py
│   │   ├── Jpake2Request.py
│   │   ├── Jpake3SessionKeyRequest.py
│   │   ├── Jpake4KeyConfirmationRequest.py
│   │   └── PumpChallengeRequest.py
│   ├── currentStatus/
│   │   ├── __init__.py
│   │   ├── ApiVersionRequest.py
│   │   ├── CurrentBasalStatusRequest.py
│   │   ├── CurrentBatteryV1Request.py
│   │   ├── CurrentBolusStatusRequest.py
│   │   ├── InsulinStatusRequest.py
│   │   └── PumpVersionRequest.py
│   └── control/
│       └── __init__.py
├── response/
│   ├── __init__.py
│   ├── authentication/
│   │   ├── __init__.py
│   │   ├── CentralChallengeResponse.py
│   │   ├── Jpake1aResponse.py
│   │   ├── Jpake1bResponse.py
│   │   ├── Jpake2Response.py
│   │   ├── Jpake3SessionKeyResponse.py
│   │   ├── Jpake4KeyConfirmationResponse.py
│   │   └── PumpChallengeResponse.py
│   ├── currentStatus/
│   │   ├── __init__.py
│   │   ├── ApiVersionResponse.py
│   │   ├── CurrentBasalStatusResponse.py
│   │   ├── CurrentBatteryV1Response.py
│   │   ├── CurrentBolusStatusResponse.py
│   │   ├── InsulinStatusResponse.py
│   │   └── PumpVersionResponse.py
│   └── control/
│       └── __init__.py
└── util/
    ├── __init__.py
    └── bytes.py  (helper functions)
```

### __all__ Exports

Each `__init__.py` should export all message classes:

```python
# messages/request/authentication/__init__.py
from .CentralChallengeRequest import CentralChallengeRequest
from .Jpake1aRequest import Jpake1aRequest
from .Jpake1bRequest import Jpake1bRequest
from .Jpake2Request import Jpake2Request
from .Jpake3SessionKeyRequest import Jpake3SessionKeyRequest
from .Jpake4KeyConfirmationRequest import Jpake4KeyConfirmationRequest
from .PumpChallengeRequest import PumpChallengeRequest

__all__ = [
    "CentralChallengeRequest",
    "Jpake1aRequest",
    "Jpake1bRequest",
    "Jpake2Request",
    "Jpake3SessionKeyRequest",
    "Jpake4KeyConfirmationRequest",
    "PumpChallengeRequest",
]
```

Then imports work as requested:
```python
from tandem_simulator.protocol.messages.request.authentication import Jpake1aRequest
```

---

## Phase 5: Testing & Validation (HIGH PRIORITY)

### 5.1 Update Existing Tests
- Update test_protocol.py for new message structures
- Add tests for all new authentication messages
- Add tests for CurrentBolusStatusResponse and PumpVersionResponse

### 5.2 Create Integration Tests
- Test complete JPake flow (all 4 rounds)
- Test challenge-response flow
- Test message serialization/deserialization round-trip for all messages

### 5.3 Validation Against Real Data
- If available, test against actual pump message captures
- Verify byte-for-byte compatibility with pumpx2

---

## Phase 6: Documentation (MEDIUM PRIORITY)

### 6.1 Update README.md
- Document the exact message structure matching
- Note which messages are implemented
- Provide examples of usage

### 6.2 Create Message Documentation
- Document each message's fields and purpose
- Provide byte layout diagrams
- Document the JPake authentication flow

### 6.3 API Documentation
- Generate Sphinx documentation
- Document all message classes
- Document helper utilities

---

## Implementation Priority

### CRITICAL (Do First)
1. ✅ Fix InsulinStatusResponse signed/unsigned bug
2. Implement CurrentBolusStatusResponse (15 bytes)
3. Implement PumpVersionResponse (48 bytes)
4. Rewrite authentication messages (14 messages)

### HIGH (Do Second)
5. Directory restructuring
6. Add __all__ exports
7. Update tests
8. Integration testing

### MEDIUM (Do Third)
9. Documentation
10. Additional status messages
11. Control messages

---

## Estimated Effort

| Phase | Estimated Time |
|-------|----------------|
| Phase 1 (Critical Fixes) | ✅ Complete |
| Phase 2 (Status Messages) | 2-3 hours |
| Phase 3 (Authentication) | 4-6 hours |
| Phase 4 (Directory Restructure) | 2-3 hours |
| Phase 5 (Testing) | 3-4 hours |
| Phase 6 (Documentation) | 2-3 hours |
| **Total** | **13-19 hours** |

---

## References

- pumpx2 GitHub: https://github.com/jwoglom/pumpX2
- pumpx2 Javadoc: https://jwoglom.github.io/pumpX2/javadoc/messages/
- Validation Reports:
  - AUTHENTICATION_VALIDATION_REPORT.md
  - CURRENTSTATUS_VALIDATION_REPORT.md
  - pumpX2_MESSAGE_STRUCTURE_MAP.md
- Exact Implementations:
  - CurrentBolusStatusResponse_EXACT.py
  - PumpVersionResponse_EXACT.py

---

## Next Steps

1. Commit critical bugfix (InsulinStatusResponse unsigned int)
2. Create GitHub issue for Phase 2 (Status Messages)
3. Create GitHub issue for Phase 3 (Authentication Messages)
4. Create GitHub issue for Phase 4 (Directory Restructuring)
5. Prioritize based on testing needs with actual pump communication
