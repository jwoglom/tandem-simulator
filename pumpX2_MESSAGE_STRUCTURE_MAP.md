# PumpX2 Message Directory Structure and Comprehensive Map

## Overview
The pumpX2 project implements a reverse-engineered Bluetooth protocol for Tandem insulin pumps (t:slim X2). Messages are organized into six main categories:
- **authentication**: J-PAKE cryptographic handshake
- **currentStatus**: Pump status and configuration queries
- **control**: Pump control commands
- **controlStream**: State streaming responses
- **historyLog**: Historical event logs
- **qualifyingEvent**: Special event notifications (response-only)

---

## Message Architecture Basics

### MessageProps Annotation
Each message is annotated with `@MessageProps` containing:
- **opCode**: Unique byte identifier (can be negative, e.g., -98)
- **size**: Message payload size in bytes
- **type**: REQUEST or RESPONSE
- **characteristic**: Bluetooth characteristic (CONTROL, MOBI_STATUS, HISTORY_LOG, CONTROL_STREAM)
- **request/response**: Linked class reference

### Message Enum (Messages.java)
Messages are registered in a Java enum with static initialization that maps:
- `Pair<Characteristic, opCode>` → Message class
- Request opcodes → Message type
- Response opcodes → Message type

### Base Message Class
All messages extend `Message` abstract class which provides:
- `parse(byte[] raw)`: Deserialize incoming data
- `removeSignedRequestHmacBytes()`: Strip 24-byte HMAC signatures
- `cargo`: Raw byte payload field
- `jsonToString()`: Structured output

---

## Category 1: AUTHENTICATION

**Purpose**: J-PAKE (Jacobi Pairing Authentication and Key Exchange) protocol handshake for pump connection authorization.

**Directory Paths**:
- Request: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/request/authentication/`
- Response: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/authentication/`

### Request Messages (8 files)

| File | Opcode | Key Fields | Data Types |
|------|--------|-----------|------------|
| AbstractCentralChallengeRequest.java | - | (Abstract base class) | - |
| CentralChallengeRequest.java | 16 | appInstanceId, centralChallenge, cargo | int, byte[], byte[] |
| Jpake1aRequest.java | 32 | appInstanceId, centralChallenge | int, byte[] |
| Jpake1bRequest.java | - | (Not extracted) | - |
| Jpake2Request.java | - | (Not extracted) | - |
| Jpake3SessionKeyRequest.java | - | (Not extracted) | - |
| Jpake4KeyConfirmationRequest.java | - | (Not extracted) | - |
| PumpChallengeRequest.java | - | (Not extracted) | - |

### Response Messages (9 files)

| File | Opcode | Key Fields | Data Types |
|------|--------|-----------|------------|
| AbstractCentralChallengeResponse.java | - | (Abstract base class) | - |
| AbstractPumpChallengeResponse.java | - | (Abstract base class) | - |
| CentralChallengeResponse.java | 17 | appInstanceId, centralChallengeHash, hmacKey | int, byte[], byte[] |
| Jpake1aResponse.java | 33 | appInstanceId, centralChallengeHash | int, byte[] (165 bytes) |
| Jpake1bResponse.java | - | (Not extracted) | - |
| Jpake2Response.java | - | (Not extracted) | - |
| Jpake3SessionKeyResponse.java | - | (Not extracted) | - |
| Jpake4KeyConfirmationResponse.java | - | (Not extracted) | - |
| PumpChallengeResponse.java | - | (Not extracted) | - |

---

## Category 2: CURRENTSTATUS

**Purpose**: Query pump status, configuration, and device information.

**Directory Paths**:
- Request: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/request/currentStatus/`
- Response: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/currentStatus/`

**Total**: 59 request files, 63 response files

### Notable Request Messages

| File | Opcode | Key Fields | Size (bytes) |
|------|--------|-----------|--------------|
| AlarmStatusRequest.java | - | (TBD) | - |
| AlertStatusRequest.java | - | (TBD) | - |
| ApiVersionRequest.java | 32 | cargo | 0 |
| BasalIQAlertInfoRequest.java | - | (TBD) | - |
| BasalIQSettingsRequest.java | - | (TBD) | - |
| BasalIQStatusRequest.java | - | (TBD) | - |
| CurrentBasalStatusRequest.java | - | (TBD) | - |
| CurrentBatteryV1Request.java | - | (TBD) | - |
| CurrentBatteryV2Request.java | - | (TBD) | - |
| HistoryLogRequest.java | - | (TBD) | - |
| HistoryLogStatusRequest.java | - | (TBD) | - |
| PumpSettingsRequest.java | 82 | (TBD) | - |
| PumpVersionRequest.java | 84 | cargo | 0 |
| ... (45 more files) | - | (TBD) | - |

### Notable Response Messages

| File | Opcode | Key Fields | Data Types | Size (bytes) |
|------|--------|-----------|-----------|--------------|
| ApiVersionResponse.java | 33 | majorVersion, minorVersion | int, int | 4 |
| CurrentBasalStatusResponse.java | 41 | profileBasalRate, currentBasalRate, basalModifiedBitmask | long, long, int | 9 |
| PumpSettingsResponse.java | 83 | lowInsulinThreshold, cannulaPrimeSize, autoShutdownEnabled, autoShutdownDuration, featureLock, oledTimeout, status | int (×7) | 9 |
| PumpVersionResponse.java | 85 | armSwVer, mspSwVer, configABits, configBBits, serialNum, partNum, pumpRev, pcbaSN, pcbaRev, modelNum | long (×8), String (×2) | - |
| ... (59 more files) | - | (TBD) | - |

---

## Category 3: CONTROL

**Purpose**: Send control commands to pump (bolus, temp rate, settings changes, etc.)

**Directory Paths**:
- Request: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/request/control/`
- Response: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/control/`

**Total**: 37 request files, 37 response files

### Request Messages

| File | Opcode | Key Fields | Data Types | Size (bytes) | Signed |
|------|--------|-----------|------------|--------------|--------|
| BolusPermissionRequest.java | -94 | (empty) | - | 0 | Yes |
| BolusPermissionReleaseRequest.java | - | (TBD) | - | - | - |
| CancelBolusRequest.java | - | (TBD) | - | - | - |
| ChangeControlIQSettingsRequest.java | - | (TBD) | - | - | - |
| ChangeTimeDateRequest.java | - | (TBD) | - | - | - |
| CreateIDPRequest.java | - | (TBD) | - | - | - |
| DeleteIDPRequest.java | - | (TBD) | - | - | - |
| DisconnectPumpRequest.java | - | (TBD) | - | - | - |
| DismissNotificationRequest.java | - | (TBD) | - | - | - |
| EnterChangeCartridgeModeRequest.java | - | (TBD) | - | - | - |
| EnterFillTubingModeRequest.java | - | (TBD) | - | - | - |
| ExitChangeCartridgeModeRequest.java | - | (TBD) | - | - | - |
| ExitFillTubingModeRequest.java | - | (TBD) | - | - | - |
| FillCannulaRequest.java | - | (TBD) | - | - | - |
| InitiateBolusRequest.java | -98 | totalVolume, bolusID, bolusTypeBitmask, foodVolume, correctionVolume, bolusCarbs, bolusBG, bolusIOB, extendedVolume, extendedSeconds, extended3 | long, int, int, long, long, int, int, long, long, long, long | 37 | Yes |
| PlaySoundRequest.java | - | (TBD) | - | - | - |
| RemoteBgEntryRequest.java | - | (TBD) | - | - | - |
| RemoteCarbEntryRequest.java | - | (TBD) | - | - | - |
| RenameIDPRequest.java | - | (TBD) | - | - | - |
| ResumePumpingRequest.java | - | (TBD) | - | - | - |
| SetActiveIDPRequest.java | - | (TBD) | - | - | - |
| SetDexcomG7PairingCodeRequest.java | - | (TBD) | - | - | - |
| SetG6TransmitterIdRequest.java | - | (TBD) | - | - | - |
| SetIDPSegmentRequest.java | - | (TBD) | - | - | - |
| SetIDPSettingsRequest.java | - | (TBD) | - | - | - |
| SetMaxBasalLimitRequest.java | - | (TBD) | - | - | - |
| SetMaxBolusLimitRequest.java | - | (TBD) | - | - | - |
| SetModesRequest.java | - | (TBD) | - | - | - |
| SetPumpAlertSnoozeRequest.java | - | (TBD) | - | - | - |
| SetPumpSoundsRequest.java | - | (TBD) | - | - | - |
| SetQuickBolusSettingsRequest.java | - | (TBD) | - | - | - |
| SetSleepScheduleRequest.java | - | (TBD) | - | - | - |
| SetTempRateRequest.java | -92 | minutes, percent | int, int | 6 | Yes |
| StartDexcomG6SensorSessionRequest.java | - | (TBD) | - | - | - |
| StopDexcomCGMSensorSessionRequest.java | - | (TBD) | - | - | - |
| StopTempRateRequest.java | - | (TBD) | - | - | - |
| SuspendPumpingRequest.java | - | (TBD) | - | - | - |

### Response Messages

| File | Opcode | Key Fields | Data Types | Size (bytes) |
|------|--------|-----------|------------|--------------|
| BolusPermissionResponse.java | -93 | status, bolusId, nackReasonId | int, int, int | 6 |
| BolusPermissionReleaseResponse.java | - | (TBD) | - | - |
| CancelBolusResponse.java | - | (TBD) | - | - |
| ChangeControlIQSettingsResponse.java | - | (TBD) | - | - |
| ChangeTimeDateResponse.java | - | (TBD) | - | - |
| CreateIDPResponse.java | - | (TBD) | - | - |
| DeleteIDPResponse.java | - | (TBD) | - | - |
| DisconnectPumpResponse.java | - | (TBD) | - | - |
| DismissNotificationResponse.java | - | (TBD) | - | - |
| EnterChangeCartridgeModeResponse.java | - | (TBD) | - | - |
| EnterFillTubingModeResponse.java | - | (TBD) | - | - |
| ExitChangeCartridgeModeResponse.java | - | (TBD) | - | - |
| ExitFillTubingModeResponse.java | - | (TBD) | - | - |
| FillCannulaResponse.java | - | (TBD) | - | - |
| InitiateBolusResponse.java | - | (TBD) | - | - |
| PlaySoundResponse.java | - | (TBD) | - | - |
| RemoteBgEntryResponse.java | - | (TBD) | - | - |
| RemoteCarbEntryResponse.java | - | (TBD) | - | - |
| RenameIDPResponse.java | - | (TBD) | - | - |
| ResumePumpingResponse.java | - | (TBD) | - | - |
| SetActiveIDPResponse.java | - | (TBD) | - | - |
| SetDexcomG7PairingCodeResponse.java | - | (TBD) | - | - |
| SetG6TransmitterIdResponse.java | - | (TBD) | - | - |
| SetIDPSegmentResponse.java | - | (TBD) | - | - |
| SetIDPSettingsResponse.java | - | (TBD) | - | - |
| SetMaxBasalLimitResponse.java | - | (TBD) | - | - |
| SetMaxBolusLimitResponse.java | - | (TBD) | - | - |
| SetModesResponse.java | - | (TBD) | - | - |
| SetPumpAlertSnoozeResponse.java | - | (TBD) | - | - |
| SetPumpSoundsResponse.java | - | (TBD) | - | - |
| SetQuickBolusSettingsResponse.java | - | (TBD) | - | - |
| SetSleepScheduleResponse.java | - | (TBD) | - | - |
| SetTempRateResponse.java | -91 | status, tempRateId | int, int | 4 |
| StartDexcomG6SensorSessionResponse.java | - | (TBD) | - | - |
| StopDexcomCGMSensorSessionResponse.java | - | (TBD) | - | - |
| StopTempRateResponse.java | - | (TBD) | - | - |
| SuspendPumpingResponse.java | - | (TBD) | - | - |

---

## Category 4: CONTROLSTREAM

**Purpose**: Handle real-time state streaming for pump operations (filling, pumping, etc.)

**Directory Paths**:
- Request: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/request/controlStream/`
- Response: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/controlStream/`

**Total**: 6 request files, 7 response files

### Request Messages (Mostly Placeholder/Nonexistent)

| File | Opcode | Key Fields | Notes |
|------|--------|-----------|-------|
| NonexistentDetectingCartridgeStateStreamRequest.java | - | (TBD) | Placeholder for state stream |
| NonexistentEnterChangeCartridgeModeStateStreamRequest.java | - | (TBD) | Placeholder for state stream |
| NonexistentExitFillTubingModeStateStreamRequest.java | - | (TBD) | Placeholder for state stream |
| NonexistentFillCannulaStateStreamRequest.java | - | (TBD) | Placeholder for state stream |
| NonexistentFillTubingStateStreamRequest.java | - | (TBD) | Placeholder for state stream |
| NonexistentPumpingStateStreamRequest.java | - | (TBD) | Placeholder for state stream |

### Response Messages

| File | Opcode | Key Fields | Data Types | Size (bytes) |
|------|--------|-----------|------------|--------------|
| ControlStreamMessages.java | - | (Support class) | - | - |
| DetectingCartridgeStateStreamResponse.java | - | (TBD) | - | - |
| EnterChangeCartridgeModeStateStreamResponse.java | - | (TBD) | - | - |
| ExitFillTubingModeStateStreamResponse.java | - | (TBD) | - | - |
| FillCannulaStateStreamResponse.java | - | (TBD) | - | - |
| FillTubingStateStreamResponse.java | -27 | buttonState | int | 5 (29 with padding) |
| PumpingStateStreamResponse.java | -23 | isPumpingStateSetAfterStartUp, stateBitmask | boolean, long | 5 (29 with padding) |

**Note**: ControlStream responses typically include a nested enum (e.g., `PumpingState`) that decodes the bitmask into individual state flags.

---

## Category 5: HISTORYLOG

**Purpose**: Query and stream historical event logs from pump memory.

**Directory Paths**:
- Request: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/request/historyLog/`
- Response: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/historyLog/`

**Total**: 1 request file, 55 response files

### Request Messages

| File | Opcode | Key Fields | Notes |
|------|--------|-----------|-------|
| NonexistentHistoryLogStreamRequest.java | - | (TBD) | Placeholder for history log stream |

### Response Messages (Selected Examples)

| File | Opcode | Key Fields | Data Types | Size (bytes) |
|------|--------|-----------|------------|--------------|
| AlarmActivatedHistoryLog.java | - | (TBD) | - | - |
| AlertActivatedHistoryLog.java | - | (TBD) | - | - |
| BasalDeliveryHistoryLog.java | 279 | commandedRateSource, commandedRate, profileBasalRate, algorithmRate, tempRate | int (×5) | - |
| BGHistoryLog.java | - | (TBD) | - | - |
| BasalRateChangeHistoryLog.java | - | (TBD) | - | - |
| BolusActivatedHistoryLog.java | - | (TBD) | - | - |
| BolusCompletedHistoryLog.java | 20 | completionStatusId, bolusId, iob, insulinDelivered, insulinRequested | int, int, float, float, float | - |
| BolusDeliveryHistoryLog.java | - | (TBD) | - | - |
| CannulaFilledHistoryLog.java | - | (TBD) | - | - |
| CarbEnteredHistoryLog.java | - | (TBD) | - | - |
| CartridgeFilledHistoryLog.java | - | (TBD) | - | - |
| CgmCalibrationHistoryLog.java | - | (TBD) | - | - |
| ControlIQPcmChangeHistoryLog.java | - | (TBD) | - | - |
| ControlIQUserModeChangeHistoryLog.java | - | (TBD) | - | - |
| DailyBasalHistoryLog.java | - | (TBD) | - | - |
| DateChangeHistoryLog.java | - | (TBD) | - | - |
| DexcomG6CGMHistoryLog.java | - | (TBD) | - | - |
| DexcomG7CGMHistoryLog.java | - | (TBD) | - | - |
| HistoryLog.java | - | Base class (pumpTimeSec, sequenceNum, cargo) | - | 26 bytes (standard size) |
| HistoryLogParser.java | - | Parser utility | - | - |
| HistoryLogStreamResponse.java | -127 | numberOfHistoryLogs, streamId, historyLogStreamBytes, historyLogs | int, int, List<byte[]>, List<HistoryLog> | Variable |
| HypoMinimizerResumeHistoryLog.java | - | (TBD) | - | - |
| HypoMinimizerSuspendHistoryLog.java | - | (TBD) | - | - |
| ParamChangePumpSettingsHistoryLog.java | - | (TBD) | - | - |
| PumpingResumedHistoryLog.java | - | (TBD) | - | - |
| PumpingSuspendedHistoryLog.java | - | (TBD) | - | - |
| TempRateActivatedHistoryLog.java | - | (TBD) | - | - |
| TempRateCompletedHistoryLog.java | - | (TBD) | - | - |
| TimeChangedHistoryLog.java | - | (TBD) | - | - |
| TubingFilledHistoryLog.java | - | (TBD) | - | - |
| UnknownHistoryLog.java | - | (TBD) | - | - |
| ... (28 more files) | - | (TBD) | - | - |

**Base HistoryLog Class Fields**:
- `pumpTimeSec`: long - Pump timestamp in seconds
- `sequenceNum`: int - Sequence number
- `cargo`: byte[] - Raw payload

All history logs inherit these fields. Individual event types add specialized fields.

---

## Category 6: QUALIFYING EVENT

**Purpose**: Special event notifications for significant pump events.

**Directory Paths**:
- Response only: `messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/qualifyingEvent/`

**Total**: 1 response file (no request counterpart)

### Response Messages

| File | Opcode | Key Fields | Data Types |
|------|--------|-----------|------------|
| QualifyingEvent.java | - | (TBD) | - |

---

## Supporting Classes and Utilities

### Message Organization Files

| File | Location | Purpose |
|------|----------|---------|
| Message.java | `messages/.../messages/` | Abstract base class for all messages |
| MessageProps.java | `messages/.../messages/` | Annotation for message metadata |
| MessageType.java | `messages/.../messages/` | Enum: REQUEST, RESPONSE, HISTORY_LOG |
| Messages.java | `messages/.../messages/` | Message type enum with static registry |
| ErrorResponse.java | `messages/.../messages/response/` | Error message response |
| NonexistentErrorRequest.java | `messages/.../messages/request/` | Error message request placeholder |

### Supporting Packages

| Package | Contents | Purpose |
|---------|----------|---------|
| `annotations/` | Message property annotations | Metadata for message classes |
| `bluetooth/` | BLE characteristic models | Bluetooth specific structures |
| `builders/` | Message builders | Factory patterns with crypto support |
| `calculator/` | Calculation utilities | CRC, HMAC, crypto helpers |
| `helpers/` | Helper utilities | Byte manipulation, parsing helpers |
| `models/` | Data models | Reusable data structures |
| `util/` | General utilities | Common utility functions |

---

## Bluetooth Characteristics Mapping

Messages are organized by Bluetooth characteristic:

| Characteristic | Categories | Purpose |
|----------------|-----------|---------|
| CONTROL | authentication, control | Command/control communication |
| MOBI_STATUS | currentStatus | Status queries |
| HISTORY_LOG | historyLog | Historical logs |
| CONTROL_STREAM | controlStream | Real-time state streaming |

---

## Key Patterns Observed

### 1. Request-Response Pairing
- Each request message has a paired response message
- Opcodes differ: requests are "REQ" and responses are "RSP" in naming convention
- Example: ApiVersionRequest (opcode 32) ↔ ApiVersionResponse (opcode 33)

### 2. Signed HMAC Messages
- Control requests require 24-byte HMAC-SHA256 signature
- Signature appended to message payload
- `removeSignedRequestHmacBytes()` strips signature during parsing

### 3. Message Sizes
- Vary from 0 bytes (empty payload) to 167 bytes
- Size metadata in @MessageProps annotation
- Parsing validates byte array length

### 4. Opcode System
- Single-byte identifiers (can be negative, e.g., -98)
- Maps characteristic + opcode → message class
- Enables dynamic message type routing

### 5. History Log Streaming
- Base HistoryLog class: 26 bytes per entry
- HistoryLogStreamResponse: contains list of parsed history logs
- Each log type identified by opcode (279 for BasalDelivery, 20 for BolusCompleted, etc.)

### 6. State Streaming
- ControlStream responses deliver real-time state via bitmasks
- Nested enums decode bitmask into individual state flags
- Example: PumpingState enum has 16 possible states

---

## Summary Statistics

| Category | Request Files | Response Files | Total |
|----------|---------------|-----------------|-------|
| Authentication | 8 | 9 | 17 |
| CurrentStatus | 59 | 63 | 122 |
| Control | 37 | 37 | 74 |
| ControlStream | 6 | 7 | 13 |
| HistoryLog | 1 | 55 | 56 |
| QualifyingEvent | 0 | 1 | 1 |
| **TOTAL** | **111** | **172** | **283** |

---

## Directory Structure Tree

```
messages/src/main/java/com/jwoglom/pumpx2/pump/messages/
├── Message.java
├── MessageType.java
├── MessageProps.java
├── Messages.java
├── ErrorResponse.java
├── NonexistentErrorRequest.java
├── annotations/
├── bluetooth/
├── builders/
├── calculator/
├── helpers/
├── models/
├── util/
├── request/
│   ├── NonexistentErrorRequest.java
│   ├── template.j2
│   ├── authentication/
│   │   ├── AbstractCentralChallengeRequest.java
│   │   ├── CentralChallengeRequest.java
│   │   ├── Jpake1aRequest.java
│   │   ├── Jpake1bRequest.java
│   │   ├── Jpake2Request.java
│   │   ├── Jpake3SessionKeyRequest.java
│   │   ├── Jpake4KeyConfirmationRequest.java
│   │   └── PumpChallengeRequest.java
│   ├── control/ (37 files)
│   │   ├── BolusPermissionRequest.java
│   │   ├── InitiateBolusRequest.java
│   │   ├── SetTempRateRequest.java
│   │   └── ... (34 more)
│   ├── controlStream/ (6 files)
│   │   ├── NonexistentDetectingCartridgeStateStreamRequest.java
│   │   └── ... (5 more)
│   ├── currentStatus/ (59 files)
│   │   ├── ApiVersionRequest.java
│   │   ├── PumpVersionRequest.java
│   │   ├── PumpSettingsRequest.java
│   │   └── ... (56 more)
│   └── historyLog/
│       └── NonexistentHistoryLogStreamRequest.java
└── response/
    ├── ErrorResponse.java
    ├── template.j2
    ├── authentication/ (9 files)
    │   ├── AbstractCentralChallengeResponse.java
    │   ├── CentralChallengeResponse.java
    │   ├── Jpake1aResponse.java
    │   └── ... (6 more)
    ├── control/ (37 files)
    │   ├── BolusPermissionResponse.java
    │   ├── SetTempRateResponse.java
    │   └── ... (35 more)
    ├── controlStream/ (7 files)
    │   ├── ControlStreamMessages.java
    │   ├── PumpingStateStreamResponse.java
    │   ├── FillTubingStateStreamResponse.java
    │   └── ... (4 more)
    ├── currentStatus/ (63 files)
    │   ├── ApiVersionResponse.java
    │   ├── PumpVersionResponse.java
    │   ├── CurrentBasalStatusResponse.java
    │   ├── PumpSettingsResponse.java
    │   └── ... (59 more)
    ├── historyLog/ (55 files)
    │   ├── HistoryLog.java (base class)
    │   ├── HistoryLogParser.java
    │   ├── HistoryLogStreamResponse.java
    │   ├── BasalDeliveryHistoryLog.java
    │   ├── BolusCompletedHistoryLog.java
    │   └── ... (50 more)
    └── qualifyingEvent/
        └── QualifyingEvent.java
```

---

## Usage in Python (Validation Reference)

For validating the Python implementation against pumpX2:

1. **Message Registration**: Ensure all 283 message types are registered with correct opcodes
2. **Field Extraction**: Validate field parsing matches Java byte offsets and data types
3. **Opcode Mapping**: Create bidirectional maps for request/response opcodes
4. **HMAC Handling**: Ensure 24-byte signature stripping for signed control requests
5. **History Log Streaming**: Implement proper streaming with variable-length message parsing
6. **State Decoding**: Implement bitmask decoding for stream response state enums

