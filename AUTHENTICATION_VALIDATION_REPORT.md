# Authentication Messages Validation Report

## Executive Summary

**CRITICAL FINDING: All 14 authentication messages have significant discrepancies with pumpx2 Java source.**

- ✗ **0 messages** match perfectly
- ✗ **14 messages** have critical discrepancies (opcode and/or field mismatches)
- ⚠️ **Severity:** CRITICAL - Complete rewrite required

---

## Message-by-Message Validation

### 1. CentralChallengeRequest ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         16 (0x10)
Size:           10 bytes
Type:           REQUEST
Characteristic: AUTHORIZATION
Response Class: CentralChallengeResponse

Fields:
  - appInstanceId:    int/short (2 bytes, little-endian)
  - centralChallenge: byte[] (8 bytes)

Payload Structure:
  Bytes 0-1:   appInstanceId (little-endian short)
  Bytes 2-9:   centralChallenge (8 bytes)

Build Logic:
  Bytes.combine(Bytes.firstTwoBytesLittleEndian(appInstanceId), centralChallenge)
  System.arraycopy(..., 0, cargo, 0, 10)

Parse Logic:
  appInstanceId = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
  centralChallenge = Arrays.copyOfRange(raw, 2, raw.length)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x00 (WRONG: should be 16)
Fields:
  - transaction_id: int
  - challenge: bytes (generic)

build_payload() returns: challenge (entire payload)
parse_payload() sets: challenge = payload (entire payload)
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x00, Java specifies 16 (0x10)
2. ✗ **Missing Field:** No `appInstanceId` in Python implementation
3. ✗ **Field Type WRONG:** Python challenge is entire payload, Java has fixed 8-byte challenge
4. ✗ **Payload Size WRONG:** Python treats entire payload as challenge, Java expects exactly 10 bytes
5. ✗ **Parse Logic WRONG:** Python doesn't parse appInstanceId
6. ✗ **Build Logic WRONG:** Python doesn't prepend appInstanceId

**Required Changes:**
- Change opcode to 16 (0x10)
- Add appInstanceId field (int, 2 bytes)
- Constrain challenge to 8 bytes
- Update parse_payload to extract appInstanceId and 8-byte challenge
- Update build_payload to combine appInstanceId + 8-byte challenge

---

### 2. CentralChallengeResponse ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         17 (0x11)
Size:           30 bytes
Type:           RESPONSE
Characteristic: AUTHORIZATION
Request Class:  CentralChallengeRequest

Fields:
  - appInstanceId:        int/short (2 bytes, little-endian)
  - centralChallengeHash: byte[] (20 bytes)
  - hmacKey:              byte[] (8 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-21:   centralChallengeHash (20 bytes)
  Bytes 22-29:  hmacKey (8 bytes)

Build Logic:
  Bytes.combine(Bytes.firstTwoBytesLittleEndian(byte0short), 
                Bytes.combine(bytes2to22, bytes22to30))

Parse Logic:
  appInstanceId = Bytes.readShort(raw, 0)
  centralChallengeHash = Arrays.copyOfRange(raw, 2, 22)
  hmacKey = Arrays.copyOfRange(raw, 22, 30)
  Validate: raw.length == 30
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x01 (WRONG: should be 17)
Fields:
  - transaction_id: int
  - response: bytes (generic)

build_payload() returns: response (entire payload)
parse_payload() sets: response = payload (entire payload)
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x01, Java specifies 17 (0x11)
2. ✗ **Missing Fields:** No appInstanceId, centralChallengeHash, or hmacKey
3. ✗ **Generic Implementation:** Python treats entire payload as one generic bytes field
4. ✗ **Size Validation MISSING:** Python doesn't validate 30-byte size
5. ✗ **Field Extraction WRONG:** Python doesn't split into three fields

**Required Changes:**
- Change opcode to 17 (0x11)
- Add appInstanceId field (int, 2 bytes)
- Add centralChallengeHash field (bytes, 20 bytes)
- Add hmacKey field (bytes, 8 bytes)
- Update parse_payload to extract all three fields at correct offsets
- Update build_payload to combine all fields
- Add payload size validation (must be 30 bytes)

---

### 3. PumpChallengeRequest ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         18 (0x12)
Size:           22 bytes
Type:           REQUEST
Characteristic: AUTHORIZATION
Response Class: PumpChallengeResponse

Fields:
  - appInstanceId:     int/short (2 bytes, little-endian)
  - pumpChallengeHash: byte[] (20 bytes)

Payload Structure:
  Bytes 0-1:   appInstanceId (little-endian short)
  Bytes 2-21:  pumpChallengeHash (20 bytes)

Build Logic:
  byte[] cargo = new byte[22]
  System.arraycopy(Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId), 
      pumpChallengeHash), 0, cargo, 0, 22)

Parse Logic:
  appInstanceId = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
  pumpChallengeHash = Arrays.copyOfRange(raw, 2, raw.length)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x02 (WRONG: should be 18)
Fields:
  - transaction_id: int (ONLY)

build_payload() returns: b"" (EMPTY!)
parse_payload() is empty
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x02, Java specifies 18 (0x12)
2. ✗ **Missing Fields:** No appInstanceId or pumpChallengeHash
3. ✗ **Payload EMPTY:** build_payload() returns empty bytes - completely wrong!
4. ✗ **No Parse Logic:** parse_payload() doesn't extract anything
5. ✗ **Size WRONG:** Python produces empty payload, Java expects 22 bytes

**Required Changes:**
- Change opcode to 18 (0x12)
- Add appInstanceId field (int, 2 bytes)
- Add pumpChallengeHash field (bytes, 20 bytes)
- Update build_payload to combine appInstanceId + 20-byte pumpChallengeHash
- Update parse_payload to extract both fields
- Ensure payload is exactly 22 bytes

---

### 4. PumpChallengeResponse ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         19 (0x13)
Size:           3 bytes
Type:           RESPONSE
Characteristic: AUTHORIZATION
Request Class:  PumpChallengeRequest

Fields:
  - appInstanceId: int/short (2 bytes, little-endian)
  - success:       boolean (1 byte: 1=true, other=false)

Payload Structure:
  Bytes 0-1:  appInstanceId (little-endian short)
  Byte 2:     success flag (1=true, 0=false)

Build Logic:
  Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId), 
      new byte[]{(byte)(success ? 1 : 0)})

Parse Logic:
  appInstanceId = Bytes.readShort(raw, 0)
  success = raw[2] == 1
  Validate: raw.length == 3
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x03 (WRONG: should be 19)
Fields:
  - transaction_id: int
  - challenge: bytes (generic)

build_payload() returns: challenge
parse_payload() sets: challenge = payload
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x03, Java specifies 19 (0x13)
2. ✗ **Field Type WRONG:** Python has generic challenge field, Java has appInstanceId + boolean success
3. ✗ **Missing Field:** No success boolean field
4. ✗ **Size WRONG:** Java expects 3 bytes, Python is generic
5. ✗ **Data Type WRONG:** Java has boolean success, Python has generic bytes
6. ✗ **Parse Logic WRONG:** Doesn't extract appInstanceId or parse boolean

**Required Changes:**
- Change opcode to 19 (0x13)
- Replace challenge field with appInstanceId (int, 2 bytes) and success (bool, 1 byte)
- Update parse_payload to extract appInstanceId and success boolean
- Update build_payload to combine appInstanceId + success byte
- Add payload size validation (must be 3 bytes)

---

### 5. Jpake1aRequest ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         32 (0x20)
Size:           167 bytes
Type:           REQUEST
Characteristic: AUTHORIZATION
Response Class: Jpake1aResponse
minApi:         V3.2

Fields:
  - appInstanceId:   int/short (2 bytes, little-endian)
  - centralChallenge: byte[] (165 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-166:  centralChallenge (165 bytes)

Build Logic:
  byte[] cargo = new byte[167]
  System.arraycopy(Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId), 
      centralChallenge), 0, cargo, 0, 167)

Parse Logic:
  appInstanceId = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
  centralChallenge = Arrays.copyOfRange(raw, 2, raw.length)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x10 (WRONG: should be 32)
Size:    Unlimited (should be 167)

Fields:
  - transaction_id: int
  - g1: bytes (length-prefixed with 2-byte header)
  - g2: bytes (length-prefixed with 2-byte header)

Payload Format: [g1_length(2)] [g1] [g2_length(2)] [g2]
(This is a length-prefixed format, NOT the Java fixed-size format)
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x10 (16), Java specifies 32 (0x20)
2. ✗ **Field Names WRONG:** Python has g1/g2, Java has centralChallenge
3. ✗ **Message Structure COMPLETELY DIFFERENT:** Python uses length-prefixed format with two fields; Java has single 165-byte payload
4. ✗ **Size WRONG:** Python has variable size, Java is fixed 167 bytes
5. ✗ **Missing appInstanceId:** Python doesn't have appInstanceId field
6. ✗ **Parse Logic COMPLETELY DIFFERENT:** Python parses length-prefixed g1/g2; Java reads 165 bytes as single field

**Required Changes:**
- Change opcode to 32 (0x20)
- Replace g1/g2 fields with single appInstanceId + centralChallenge fields
- Remove length-prefix parsing logic
- Implement fixed 167-byte payload parsing
- Extract appInstanceId (2 bytes) + centralChallenge (165 bytes)
- Update build_payload to match Java structure

---

### 6. Jpake1aResponse ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         33 (0x21) [NOTE: Source has comment "or 35?" suggesting uncertainty]
Size:           167 bytes
Type:           RESPONSE
Characteristic: AUTHORIZATION
Request Class:  Jpake1aRequest
minApi:         V3.2

Fields:
  - appInstanceId:       int/short (2 bytes, little-endian)
  - centralChallengeHash: byte[] (165 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-166:  centralChallengeHash (165 bytes)

Build Logic:
  Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(byte0short), 
      bytes2to167)

Parse Logic:
  appInstanceId = Bytes.readShort(raw, 0)
  centralChallengeHash = Arrays.copyOfRange(raw, 2, 167)
  Validate: raw.length == 167
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x11 (WRONG: should be 33)
Fields:
  - transaction_id: int
  - status: int (1 byte)

Payload: [status_byte]
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x11 (17), Java specifies 33 (0x21)
2. ✗ **Field Names WRONG:** Python has status, Java has appInstanceId + centralChallengeHash
3. ✗ **Message Structure COMPLETELY DIFFERENT:** Python is 1-byte status; Java is 167 bytes with two fields
4. ✗ **Size CRITICAL:** Python expects 1 byte, Java expects 167 bytes
5. ✗ **Missing appInstanceId:** Python doesn't have appInstanceId
6. ✗ **Wrong Data Type:** Python status is 1 byte; Java centralChallengeHash is 165 bytes

**Required Changes:**
- Change opcode to 33 (0x21)
- Replace status field with appInstanceId + centralChallengeHash
- Update parse_payload to extract appInstanceId (2 bytes) + centralChallengeHash (165 bytes)
- Update build_payload to combine both fields
- Ensure fixed 167-byte payload size

---

### 7. Jpake1bRequest ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         34 (0x22)
Size:           167 bytes
Type:           REQUEST
Characteristic: AUTHORIZATION
Response Class: Jpake1bResponse
minApi:         V3.2

Fields:
  - appInstanceId:   int/short (2 bytes, little-endian)
  - centralChallenge: byte[] (165 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-166:  centralChallenge (165 bytes)

Build Logic:
  byte[] cargo = new byte[167]
  System.arraycopy(Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId), 
      centralChallenge), 0, cargo, 0, 167)

Parse Logic:
  appInstanceId = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
  centralChallenge = Arrays.copyOfRange(raw, 2, raw.length)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x12 (WRONG: should be 34)
Fields:
  - transaction_id: int
  - g3: bytes (length-prefixed with 2-byte header)
  - g4: bytes (length-prefixed with 2-byte header)

Payload Format: [g3_length(2)] [g3] [g4_length(2)] [g4]
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x12 (18), Java specifies 34 (0x22)
2. ✗ **Field Names WRONG:** Python has g3/g4, Java has centralChallenge
3. ✗ **Message Structure COMPLETELY DIFFERENT:** Python uses length-prefixed format; Java has fixed 165-byte payload
4. ✗ **Size WRONG:** Python variable, Java fixed 167 bytes
5. ✗ **Missing appInstanceId:** Python doesn't have this field
6. ✗ **Parse Logic DIFFERENT:** Length-prefixed vs. fixed-size

**Required Changes:**
- Change opcode to 34 (0x22)
- Replace g3/g4 with appInstanceId + centralChallenge
- Remove length-prefix parsing
- Implement fixed-size parsing: appInstanceId (2) + centralChallenge (165)

---

### 8. Jpake1bResponse ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         35 (0x23)
Size:           167 bytes
Type:           RESPONSE
Characteristic: AUTHORIZATION
Request Class:  Jpake1bRequest
minApi:         V3.2

Fields:
  - appInstanceId:       int/short (2 bytes, little-endian)
  - centralChallengeHash: byte[] (165 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-166:  centralChallengeHash (165 bytes)

Parse Logic:
  Validate: raw.length == 167
  appInstanceId = Bytes.readShort(raw, 0)
  centralChallengeHash = Arrays.copyOfRange(raw, 2, 167)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x13 (WRONG: should be 35)
Fields:
  - transaction_id: int
  - status: int (1 byte)

Payload: [status_byte]
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x13 (19), Java specifies 35 (0x23)
2. ✗ **Message Structure COMPLETELY DIFFERENT:** Python 1-byte status; Java 167 bytes with two fields
3. ✗ **Missing appInstanceId:** Python doesn't have this
4. ✗ **Size CRITICAL:** Python 1 byte, Java 167 bytes

**Required Changes:**
- Change opcode to 35 (0x23)
- Replace status with appInstanceId + centralChallengeHash
- Update payload parsing for 167-byte fixed size

---

### 9. Jpake2Request ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         36 (0x24)
Size:           167 bytes
Type:           REQUEST
Characteristic: AUTHORIZATION
Response Class: Jpake2Response
minApi:         V3.2

Fields:
  - appInstanceId:   int/short (2 bytes, little-endian)
  - centralChallenge: byte[] (165 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId
  Bytes 2-166:  centralChallenge (165 bytes)

Build Logic:
  byte[] cargo = new byte[167]
  System.arraycopy(Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId), 
      centralChallenge), 0, cargo, 0, 167)

Parse Logic:
  appInstanceId = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
  centralChallenge = Arrays.copyOfRange(raw, 2, raw.length)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x14 (WRONG: should be 36)
Fields:
  - transaction_id: int
  - a_value: bytes (generic)

Payload: Raw bytes, no structure
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x14 (20), Java specifies 36 (0x24)
2. ✗ **Field Names WRONG:** Python has a_value, Java has centralChallenge
3. ✗ **Missing appInstanceId:** Python doesn't include it
4. ✗ **Size:** Python generic, Java fixed 167 bytes
5. ✗ **Structure:** Python is generic bytes; Java has appInstanceId + data

**Required Changes:**
- Change opcode to 36 (0x24)
- Rename a_value to match Java structure
- Add appInstanceId field
- Implement fixed-size 167-byte parsing

---

### 10. Jpake2Response ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         37 (0x25)
Size:           170 bytes
Type:           RESPONSE
Characteristic: AUTHORIZATION
Request Class:  Jpake2Request
minApi:         V3.2

Fields:
  - appInstanceId:       int/short (2 bytes, little-endian)
  - centralChallengeHash: byte[] (168 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId
  Bytes 2-169:  centralChallengeHash (168 bytes)

Build Logic:
  Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(byte0short), 
      bytes2to170)

Parse Logic:
  Validate: raw.length == 170
  appInstanceId = Bytes.readShort(raw, 0)
  centralChallengeHash = Arrays.copyOfRange(raw, 2, 170)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x15 (WRONG: should be 37)
Fields:
  - transaction_id: int
  - b_value: bytes (generic)

Payload: Raw bytes
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x15 (21), Java specifies 37 (0x25)
2. ✗ **Field Names WRONG:** Python b_value, Java centralChallengeHash
3. ✗ **Missing appInstanceId:** Python doesn't include it
4. ✗ **Size CRITICAL:** Python generic, Java fixed 170 bytes
5. ✗ **Structure:** Python generic; Java has appInstanceId + 168-byte hash

**Required Changes:**
- Change opcode to 37 (0x25)
- Rename b_value to match Java structure
- Add appInstanceId field
- Implement fixed-size 170-byte parsing

---

### 11. Jpake3SessionKeyRequest ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         38 (0x26)
Size:           2 bytes
Type:           REQUEST
Characteristic: AUTHORIZATION
Response Class: Jpake3SessionKeyResponse
minApi:         V3.2
Note:           "triggers Jpake session validation. Input is always '0'"

Fields:
  - challengeParam: int/short (2 bytes, little-endian)

Payload Structure:
  Bytes 0-1:  challengeParam (little-endian short)

Build Logic:
  byte[] cargo = new byte[2]
  System.arraycopy(Bytes.firstTwoBytesLittleEndian(challengeParam), 0, cargo, 0, 2)

Parse Logic:
  challengeParam = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x16 (WRONG: should be 38)
Size:    Unlimited (should be 2 bytes)
Fields:
  - transaction_id: int
  - key_confirmation: bytes (generic)

Payload: Raw bytes
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x16 (22), Java specifies 38 (0x26)
2. ✗ **Field Names WRONG:** Python key_confirmation, Java challengeParam
3. ✗ **Size CRITICAL:** Python generic/variable, Java is fixed 2 bytes
4. ✗ **Field Type WRONG:** Python bytes, Java short (2 bytes)
5. ✗ **Structure:** Completely different - Java is 2-byte little-endian int; Python is generic bytes

**Required Changes:**
- Change opcode to 38 (0x26)
- Replace key_confirmation with challengeParam (int/short, 2 bytes)
- Implement fixed-size 2-byte parsing
- Parse as little-endian short value

---

### 12. Jpake3SessionKeyResponse ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         39 (0x27)
Size:           18 bytes
Type:           RESPONSE
Characteristic: AUTHORIZATION
Request Class:  Jpake3SessionKeyRequest
minApi:         V3.2

Fields:
  - appInstanceId:    int/short (2 bytes, little-endian)
  - deviceKeyNonce:   byte[] (8 bytes)
  - deviceKeyReserved: byte[] (8 bytes)

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-9:    deviceKeyNonce (8 bytes)
  Bytes 10-17:  deviceKeyReserved (8 bytes)

Build Logic:
  Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId), 
      nonce, 
      reserved)
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x17 (WRONG: should be 39)
Fields:
  - transaction_id: int
  - status: int (1 byte)

Payload: [status_byte]
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x17 (23), Java specifies 39 (0x27)
2. ✗ **Field Names COMPLETELY DIFFERENT:** Python status, Java has appInstanceId + deviceKeyNonce + deviceKeyReserved
3. ✗ **Message Structure COMPLETELY DIFFERENT:** Python 1-byte status; Java 18 bytes with 3 fields
4. ✗ **Size CRITICAL:** Python 1 byte, Java 18 bytes
5. ✗ **Missing All Fields:** Python has no appInstanceId, nonce, or reserved fields

**Required Changes:**
- Change opcode to 39 (0x27)
- Replace status with appInstanceId (2), deviceKeyNonce (8), deviceKeyReserved (8)
- Update parse_payload to extract all three fields
- Implement fixed 18-byte payload parsing

---

### 13. Jpake4KeyConfirmationRequest ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         40 (0x28)
Size:           50 bytes
Type:           REQUEST
Characteristic: AUTHORIZATION
Response Class: Jpake4KeyConfirmationResponse
minApi:         V3.2

Fields:
  - appInstanceId: int/short (2 bytes, little-endian)
  - nonce:         byte[] (8 bytes) - MUST BE 8 BYTES
  - reserved:      byte[] (8 bytes) - MUST BE 8 BYTES
  - hashDigest:    byte[] (32 bytes) - MUST BE 32 BYTES

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-9:    nonce (8 bytes)
  Bytes 10-17:  reserved (8 bytes)
  Bytes 18-49:  hashDigest (32 bytes)

Build Logic:
  Validate: nonce.length == 8
  Validate: reserved.length == 8
  Validate: hashDigest.length == 32
  
  System.arraycopy(Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId),
      nonce,
      reserved,
      hashDigest
  ), 0, cargo, 0, 50)

Parse Logic:
  appInstanceId = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
  nonce = Arrays.copyOfRange(raw, 2, 10)
  reserved = Arrays.copyOfRange(raw, 10, 18)
  hashDigest = Arrays.copyOfRange(raw, 18, 50)

Static Fields:
  RESERVED = byte[]{0, 0, 0, 0, 0, 0, 0, 0}
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x18 (WRONG: should be 40)
Fields:
  - transaction_id: int
  - confirmation: bytes (generic)

Payload: Raw bytes
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x18 (24), Java specifies 40 (0x28)
2. ✗ **Field Names WRONG:** Python confirmation, Java has appInstanceId + nonce + reserved + hashDigest
3. ✗ **Missing All Fields:** Python doesn't have any of the four fields
4. ✗ **Size:** Python generic, Java fixed 50 bytes
5. ✗ **Field Sizes:** Java has strict size requirements (8+8+32); Python has none
6. ✗ **Validation:** Python has none; Java validates field sizes

**Required Changes:**
- Change opcode to 40 (0x28)
- Replace confirmation with four distinct fields: appInstanceId, nonce, reserved, hashDigest
- Implement strict size validation (nonce=8, reserved=8, hashDigest=32)
- Update parse_payload for fixed offsets
- Add RESERVED constant

---

### 14. Jpake4KeyConfirmationResponse ✗ CRITICAL MISMATCH

**Java Source (pumpX2):**
```
Opcode:         41 (0x29)
Size:           50 bytes
Type:           RESPONSE
Characteristic: AUTHORIZATION
Request Class:  Jpake4KeyConfirmationRequest
minApi:         V3.2

Fields:
  - appInstanceId: int/short (2 bytes, little-endian)
  - nonce:         byte[] (8 bytes) - MUST BE 8 BYTES
  - reserved:      byte[] (8 bytes) - MUST BE 8 BYTES
  - hashDigest:    byte[] (32 bytes) - MUST BE 32 BYTES

Payload Structure:
  Bytes 0-1:    appInstanceId (little-endian short)
  Bytes 2-9:    nonce (8 bytes)
  Bytes 10-17:  reserved (8 bytes)
  Bytes 18-49:  hashDigest (32 bytes)

Build Logic:
  Validate: nonce.length == 8
  Validate: reserved.length == 8
  Validate: hashDigest.length == 32
  
  System.arraycopy(Bytes.combine(
      Bytes.firstTwoBytesLittleEndian(appInstanceId),
      nonce,
      reserved,
      hashDigest
  ), 0, cargo, 0, 50)

Parse Logic:
  appInstanceId = Bytes.readShort(Arrays.copyOfRange(raw, 0, 2), 0)
  nonce = Arrays.copyOfRange(raw, 2, 10)
  reserved = Arrays.copyOfRange(raw, 10, 18)
  hashDigest = Arrays.copyOfRange(raw, 18, 50)

Static Fields:
  RESERVED = byte[]{0, 0, 0, 0, 0, 0, 0, 0}
```

**Python Implementation (tandem-simulator):**
```
Opcode:  0x19 (WRONG: should be 41)
Fields:
  - transaction_id: int
  - status: int (1 byte)

Payload: [status_byte]
```

**DISCREPANCIES:**
1. ✗ **Opcode WRONG:** Python has 0x19 (25), Java specifies 41 (0x29)
2. ✗ **Field Names COMPLETELY DIFFERENT:** Python status (1 byte), Java has appInstanceId + nonce + reserved + hashDigest (50 bytes total)
3. ✗ **Message Structure COMPLETELY DIFFERENT:** Python 1-byte response; Java 50-byte authentication payload
4. ✗ **Size CRITICAL:** Python 1 byte, Java 50 bytes
5. ✗ **Missing All Fields:** Python has no appInstanceId, nonce, reserved, or hashDigest

**Required Changes:**
- Change opcode to 41 (0x29)
- Replace status with four fields: appInstanceId, nonce, reserved, hashDigest
- Implement size validation (nonce=8, reserved=8, hashDigest=32)
- Update parse_payload for fixed 50-byte offsets
- Add RESERVED constant

---

## Summary Table

| Message | Java Opcode | Python Opcode | Opcode Match | Fields Match | Size Match | Status |
|---------|-------------|---------------|--------------|--------------|------------|--------|
| CentralChallengeRequest | 16 | 0x00 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| CentralChallengeResponse | 17 | 0x01 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| PumpChallengeRequest | 18 | 0x02 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| PumpChallengeResponse | 19 | 0x03 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake1aRequest | 32 | 0x10 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake1aResponse | 33 | 0x11 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake1bRequest | 34 | 0x12 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake1bResponse | 35 | 0x13 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake2Request | 36 | 0x14 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake2Response | 37 | 0x15 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake3SessionKeyRequest | 38 | 0x16 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake3SessionKeyResponse | 39 | 0x17 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake4KeyConfirmationRequest | 40 | 0x18 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |
| Jpake4KeyConfirmationResponse | 41 | 0x19 | ✗ NO | ✗ NO | ✗ NO | CRITICAL |

---

## Critical Issues

### Issue #1: ALL Opcodes Are Wrong

Every single authentication message has an incorrect opcode:

```
Challenge Messages:
  CentralChallengeRequest:  Python 0x00 → should be 0x10 (16)
  CentralChallengeResponse: Python 0x01 → should be 0x11 (17)
  PumpChallengeRequest:     Python 0x02 → should be 0x12 (18)
  PumpChallengeResponse:    Python 0x03 → should be 0x13 (19)

JPake Round 1:
  Jpake1aRequest:           Python 0x10 → should be 0x20 (32)
  Jpake1aResponse:          Python 0x11 → should be 0x21 (33)
  Jpake1bRequest:           Python 0x12 → should be 0x22 (34)
  Jpake1bResponse:          Python 0x13 → should be 0x23 (35)

JPake Round 2:
  Jpake2Request:            Python 0x14 → should be 0x24 (36)
  Jpake2Response:           Python 0x15 → should be 0x25 (37)

JPake Session Key:
  Jpake3SessionKeyRequest:  Python 0x16 → should be 0x26 (38)
  Jpake3SessionKeyResponse: Python 0x17 → should be 0x27 (39)

JPake Key Confirmation:
  Jpake4KeyConfirmationRequest:  Python 0x18 → should be 0x28 (40)
  Jpake4KeyConfirmationResponse: Python 0x19 → should be 0x29 (41)
```

**Impact:** Messages will not be recognized or routed correctly.

### Issue #2: First 4 Messages Missing Critical Fields

All challenge/pump messages lack `appInstanceId` field:

- CentralChallengeRequest: Missing appInstanceId (2 bytes)
- CentralChallengeResponse: Missing appInstanceId + has wrong fields (should be hash + HMAC key)
- PumpChallengeRequest: Missing appInstanceId + wrong structure
- PumpChallengeResponse: Missing appInstanceId + has wrong field type (should be boolean, not bytes)

**Impact:** Cannot properly correlate requests/responses with pump instances.

### Issue #3: JPake Messages Have Completely Wrong Structure

JPake1a/1b/2 messages in Python:
- Use length-prefixed format (NOT supported by Java)
- Split into g1/g2 or g3/g4 (Java uses single centralChallenge payload)
- Are variable-size (Java enforces 167 bytes)

**Impact:** Cannot exchange JPake authentication data with real pump.

### Issue #4: JPake3SessionKey Has Wrong Field Type

- Python: generic bytes (key_confirmation)
- Java: 2-byte little-endian short (challengeParam)

**Impact:** Cannot parse/build this critical message.

### Issue #5: JPake3SessionKeyResponse Completely Wrong

- Python: 1-byte status field
- Java: 18-byte structure with appInstanceId + nonce (8) + reserved (8)

**Impact:** Session key establishment will fail.

### Issue #6: JPake4KeyConfirmation Has Wrong Size and Fields

- Python: generic bytes (confirmation)
- Java: 50-byte structure with appInstanceId + nonce (8) + reserved (8) + hashDigest (32)

**Impact:** Key confirmation will fail completely.

---

## Recommended Actions

### Priority 1: Update All Opcodes (IMMEDIATE)

Update `/home/user/tandem-simulator/tandem_simulator/protocol/messages/authentication.py`:

```python
# Challenge Messages
CentralChallengeRequest.opcode = 16  # was 0x00
CentralChallengeResponse.opcode = 17  # was 0x01
PumpChallengeRequest.opcode = 18  # was 0x02
PumpChallengeResponse.opcode = 19  # was 0x03

# JPake Round 1
Jpake1aRequest.opcode = 32  # was 0x10
Jpake1aResponse.opcode = 33  # was 0x11
Jpake1bRequest.opcode = 34  # was 0x12
Jpake1bResponse.opcode = 35  # was 0x13

# JPake Round 2
Jpake2Request.opcode = 36  # was 0x14
Jpake2Response.opcode = 37  # was 0x15

# JPake Session Key
Jpake3SessionKeyRequest.opcode = 38  # was 0x16
Jpake3SessionKeyResponse.opcode = 39  # was 0x17

# JPake Key Confirmation
Jpake4KeyConfirmationRequest.opcode = 40  # was 0x18
Jpake4KeyConfirmationResponse.opcode = 41  # was 0x19
```

### Priority 2: Rewrite Challenge Messages (HIGH)

Completely rewrite first 4 messages:

```python
class CentralChallengeRequest(Message):
    opcode = 16
    def __init__(self, transaction_id: int = 0, app_instance_id: int = 0, challenge: bytes = b""):
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.challenge = challenge  # 8 bytes
    
    def parse_payload(self, payload: bytes) -> None:
        if len(payload) < 2:
            return
        self.app_instance_id = int.from_bytes(payload[0:2], "little")
        self.challenge = payload[2:10]
    
    def build_payload(self) -> bytes:
        payload = self.app_instance_id.to_bytes(2, "little")
        payload += self.challenge[:8].ljust(8, b'\x00')
        return payload
```

Similar rewrites needed for:
- CentralChallengeResponse (30 bytes: appInstanceId + hash 20 + hmacKey 8)
- PumpChallengeRequest (22 bytes: appInstanceId + hash 20)
- PumpChallengeResponse (3 bytes: appInstanceId + success boolean)

### Priority 3: Rewrite JPake1a/1b Messages (HIGH)

Remove length-prefix parsing and implement fixed-size (167-byte) structure:

```python
class Jpake1aRequest(Message):
    opcode = 32
    def __init__(self, transaction_id: int = 0, app_instance_id: int = 0, challenge: bytes = b""):
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.challenge = challenge  # 165 bytes
    
    def parse_payload(self, payload: bytes) -> None:
        if len(payload) < 2:
            return
        self.app_instance_id = int.from_bytes(payload[0:2], "little")
        self.challenge = payload[2:167]
    
    def build_payload(self) -> bytes:
        payload = self.app_instance_id.to_bytes(2, "little")
        payload += self.challenge[:165].ljust(165, b'\x00')
        return payload
```

### Priority 4: Fix JPake3SessionKey (HIGH)

Change from generic bytes to 2-byte little-endian:

```python
class Jpake3SessionKeyRequest(Message):
    opcode = 38
    def __init__(self, transaction_id: int = 0, challenge_param: int = 0):
        super().__init__(transaction_id)
        self.challenge_param = challenge_param
    
    def parse_payload(self, payload: bytes) -> None:
        if len(payload) >= 2:
            self.challenge_param = int.from_bytes(payload[0:2], "little")
    
    def build_payload(self) -> bytes:
        return self.challenge_param.to_bytes(2, "little")
```

### Priority 5: Fix JPake3SessionKeyResponse (HIGH)

Change from 1-byte status to 18-byte structure:

```python
class Jpake3SessionKeyResponse(Message):
    opcode = 39
    def __init__(self, transaction_id: int = 0, app_instance_id: int = 0, 
                 nonce: bytes = b"", reserved: bytes = b""):
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.nonce = nonce  # 8 bytes
        self.reserved = reserved  # 8 bytes
    
    def parse_payload(self, payload: bytes) -> None:
        if len(payload) < 18:
            return
        self.app_instance_id = int.from_bytes(payload[0:2], "little")
        self.nonce = payload[2:10]
        self.reserved = payload[10:18]
    
    def build_payload(self) -> bytes:
        payload = self.app_instance_id.to_bytes(2, "little")
        payload += self.nonce[:8].ljust(8, b'\x00')
        payload += self.reserved[:8].ljust(8, b'\x00')
        return payload
```

### Priority 6: Fix JPake4KeyConfirmation (HIGH)

Change from generic bytes to 50-byte structure with validation:

```python
class Jpake4KeyConfirmationRequest(Message):
    opcode = 40
    RESERVED = b'\x00' * 8
    
    def __init__(self, transaction_id: int = 0, app_instance_id: int = 0,
                 nonce: bytes = b"", reserved: bytes = b"", hash_digest: bytes = b""):
        super().__init__(transaction_id)
        self.app_instance_id = app_instance_id
        self.nonce = nonce  # MUST be 8 bytes
        self.reserved = reserved  # MUST be 8 bytes
        self.hash_digest = hash_digest  # MUST be 32 bytes
    
    def parse_payload(self, payload: bytes) -> None:
        if len(payload) < 50:
            return
        self.app_instance_id = int.from_bytes(payload[0:2], "little")
        self.nonce = payload[2:10]
        self.reserved = payload[10:18]
        self.hash_digest = payload[18:50]
    
    def build_payload(self) -> bytes:
        if len(self.nonce) != 8 or len(self.reserved) != 8 or len(self.hash_digest) != 32:
            raise ValueError("Invalid field sizes for Jpake4KeyConfirmationRequest")
        payload = self.app_instance_id.to_bytes(2, "little")
        payload += self.nonce
        payload += self.reserved
        payload += self.hash_digest
        return payload
```

---

## Notes

1. **Byte Order:** All integer fields use LITTLE-ENDIAN (Java uses `Bytes.firstTwoBytesLittleEndian`)
2. **Size Validation:** JPake messages have strict fixed sizes; must validate on parse
3. **No Length Prefixes:** Java does NOT use length-prefixed formats; data is at fixed offsets
4. **Status Fields:** Only challenge messages have status; JPake messages have complex structures
5. **Reserved Field:** Jpake3SessionKeyResponse and Jpake4Confirmation messages have 8-byte reserved fields

---

## Validation Checklist for Implementation

After making changes, verify:

- [ ] All 14 opcodes match Java (16, 17, 18, 19, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41)
- [ ] All payload sizes match Java specifications
- [ ] Little-endian byte order used for all integer fields
- [ ] Field extraction at exact byte offsets matches Java
- [ ] parse_payload() correctly unpacks all fields
- [ ] build_payload() correctly packs all fields
- [ ] Payload size validation implemented where appropriate
- [ ] Tests verify round-trip parse/build for sample data
- [ ] No breaking changes to Message base class
- [ ] MessageRegistry updated if any message classes moved/renamed

---

*Report generated from pumpX2 Java source code comparison*
*Java source: https://github.com/jwoglom/pumpX2/tree/main/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/*
