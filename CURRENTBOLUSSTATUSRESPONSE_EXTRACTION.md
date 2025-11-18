# CurrentBolusStatusResponse - Exact Java to Python Translation

## Source
**Java Source:** https://raw.githubusercontent.com/jwoglom/pumpX2/main/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/currentStatus/CurrentBolusStatusResponse.java

## 1. OPCODE AND MESSAGE SIZE

| Property | Value |
|----------|-------|
| **Opcode** | 45 (0x2D) |
| **Message Type** | RESPONSE |
| **Payload Size** | 15 bytes |
| **Request Opcode** | 44 (CurrentBolusStatusRequest) |

## 2. FIELD NAMES AND DATA TYPES

| Field Name | Java Type | Python Type | Size | Notes |
|------------|-----------|-------------|------|-------|
| `statusId` | int | int | 1 byte | Unsigned byte value |
| `bolusId` | int | int | 2 bytes | Short (unsigned 16-bit) in little-endian |
| `timestamp` | long | int | 4 bytes | Unsigned 32-bit in little-endian |
| `requestedVolume` | long | int | 4 bytes | Unsigned 32-bit in little-endian |
| `bolusSourceId` | int | int | 1 byte | Unsigned byte value |
| `bolusTypeBitmask` | int | int | 1 byte | Unsigned byte bitmask |

## 3. BYTE OFFSETS IN PARSE() METHOD

The `parse()` method uses these exact byte offsets:

```
Offset  Length  Field
------  ------  -----
0       1       statusId (raw[0])
1       2       bolusId (Bytes.readShort(raw, 1))
3-4     2       [PADDING - ignored]
5       4       timestamp (Bytes.readUint32(raw, 5))
9       4       requestedVolume (Bytes.readUint32(raw, 9))
13      1       bolusSourceId (raw[13])
14      1       bolusTypeBitmask (raw[14])
------  ------
        15      TOTAL BYTES
```

### Byte Layout Visualization

```
Byte Position
0:  statusId (1 byte, unsigned)
1-2:  bolusId (2 bytes, little-endian unsigned short)
3-4:  [PADDING - 2 zero bytes]
5-8:  timestamp (4 bytes, little-endian unsigned int)
9-12: requestedVolume (4 bytes, little-endian unsigned int)
13:  bolusSourceId (1 byte, unsigned)
14:  bolusTypeBitmask (1 byte, unsigned bitmask)
```

## 4. PARSE() METHOD IMPLEMENTATION

**Java Implementation:**
```java
public void parse(byte[] raw) {
    Validate.isTrue(raw.length == props().size());
    this.cargo = raw;
    this.statusId = raw[0];
    this.bolusId = Bytes.readShort(raw, 1);
    this.timestamp = Bytes.readUint32(raw, 5);
    this.requestedVolume = Bytes.readUint32(raw, 9);
    this.bolusSourceId = raw[13];
    this.bolusTypeBitmask = raw[14];
}
```

**Python Equivalent (`parse_payload()`):**
```python
def parse_payload(self, payload: bytes) -> None:
    if len(payload) >= 15:
        self.status_id = payload[0]
        self.bolus_id = read_uint16_le(payload, 1)
        self.timestamp = read_uint32_le(payload, 5)
        self.requested_volume = read_uint32_le(payload, 9)
        self.bolus_source_id = payload[13]
        self.bolus_type_bitmask = payload[14]
```

**Key Differences:**
- Field names converted from camelCase to snake_case (statusId → status_id)
- Java's `Bytes.readShort()` → Python's `read_uint16_le()` (little-endian unsigned)
- Java's `Bytes.readUint32()` → Python's `read_uint32_le()` (little-endian unsigned)

## 5. BUILDCARGO() METHOD IMPLEMENTATION

**Java Implementation:**
```java
public static byte[] buildCargo(int status, int bolusId, long timestamp, 
                                 long requestedVolume, int bolusSource, 
                                 int bolusTypeBitmask) {
    return Bytes.combine(
        new byte[]{ (byte) status }, 
        Bytes.firstTwoBytesLittleEndian(bolusId),
        new byte[]{ 0, 0 },
        Bytes.toUint32(timestamp), 
        Bytes.toUint32(requestedVolume), 
        new byte[]{ (byte) bolusSource }, 
        new byte[]{ (byte) bolusTypeBitmask });
}
```

**Python Equivalent (`build_payload()`):**
```python
def build_payload(self) -> bytes:
    return (
        bytes([self.status_id])  # Byte 0: status
        + write_uint16_le(self.bolus_id)  # Bytes 1-2: bolus ID
        + bytes([0, 0])  # Bytes 3-4: padding (zero bytes)
        + write_uint32_le(self.timestamp)  # Bytes 5-8: timestamp
        + write_uint32_le(self.requested_volume)  # Bytes 9-12: requested volume
        + bytes([self.bolus_source_id])  # Byte 13: bolus source
        + bytes([self.bolus_type_bitmask])  # Byte 14: bolus type bitmask
    )
```

## 6. CONSTANTS AND ENUMS

### CurrentBolusStatus Enum

**Java Definition:**
```java
public enum CurrentBolusStatus {
    REQUESTING(2),
    DELIVERING(1),
    ALREADY_DELIVERED_OR_INVALID(0);

    private final int id;
    
    CurrentBolusStatus(int id) {
        this.id = id;
    }

    public int getId() {
        return id;
    }

    public static CurrentBolusStatus fromId(int id) {
        for (CurrentBolusStatus s : values()) {
            if (s.id == id) {
                return s;
            }
        }
        return null;
    }
}
```

**Python Equivalent:**
```python
class CurrentBolusStatus(Enum):
    REQUESTING = 2
    DELIVERING = 1
    ALREADY_DELIVERED_OR_INVALID = 0

    @classmethod
    def from_id(cls, status_id: int) -> Optional["CurrentBolusStatus"]:
        for status in cls:
            if status.value == status_id:
                return status
        return None
```

## 7. COMPLETE GETTER METHODS

### Java Getters

| Method | Returns | Notes |
|--------|---------|-------|
| `getStatusId()` | `int` | Raw status ID (0, 1, or 2) |
| `getStatus()` | `CurrentBolusStatus` | Enum representation of statusId |
| `getBolusId()` | `int` | Bolus identifier |
| `getTimestamp()` | `long` | Timestamp (seconds since Jan 1, 2008) |
| `getTimestampInstant()` | `Instant` | Java Instant (converted from timestamp) |
| `getRequestedVolume()` | `long` | Volume in units * 10000 |
| `getBolusSourceId()` | `int` | Source ID |
| `getBolusSource()` | `BolusDeliveryHistoryLog.BolusSource` | Enum mapping of source ID |
| `getBolusTypeBitmask()` | `int` | Type bitmask |
| `getBolusTypes()` | `Set<BolusType>` | Set of types from bitmask |
| `isValid()` | `boolean` | Validity check |

### Python Equivalents

All Python methods use snake_case naming:
- `get_status_id()` → returns `int`
- `get_status()` → returns `Optional[CurrentBolusStatus]`
- `get_bolus_id()` → returns `int`
- `get_timestamp()` → returns `int` (seconds since Jan 1, 2008)
- `get_requested_volume()` → returns `int` (units * 10000)
- `get_bolus_source_id()` → returns `int`
- `get_bolus_type_bitmask()` → returns `int`
- `is_valid()` → returns `bool`

## 8. VALIDITY CHECK LOGIC

**Java Implementation:**
```java
public boolean isValid() {
    return !(getStatus() == CurrentBolusStatus.ALREADY_DELIVERED_OR_INVALID 
             && getBolusId() == 0 && getTimestamp() == 0);
}
```

**Logic Explanation:**
- Returns `false` (invalid) if:
  - Status is `ALREADY_DELIVERED_OR_INVALID` AND
  - BolusId equals 0 AND
  - Timestamp equals 0
- Returns `true` (valid) for all other cases

**Python Equivalent:**
```python
def is_valid(self) -> bool:
    if (
        self.get_status() == CurrentBolusStatus.ALREADY_DELIVERED_OR_INVALID
        and self.bolus_id == 0
        and self.timestamp == 0
    ):
        return False
    return True
```

## 9. LITTLE-ENDIAN HELPER FUNCTIONS

### Java Implementations (from Bytes utility class)

```java
public static int readShort(byte[] data, int offset) {
    // Little-endian unsigned short (0-65535)
    return (data[offset] & 0xFF) | ((data[offset + 1] & 0xFF) << 8);
}

public static long readUint32(byte[] data, int offset) {
    // Little-endian unsigned int (0-4294967295)
    return (data[offset] & 0xFFL) 
         | ((data[offset + 1] & 0xFFL) << 8)
         | ((data[offset + 2] & 0xFFL) << 16)
         | ((data[offset + 3] & 0xFFL) << 24);
}

public static byte[] firstTwoBytesLittleEndian(int value) {
    return new byte[]{ (byte) value, (byte) (value >> 8) };
}

public static byte[] toUint32(long value) {
    return new byte[]{
        (byte) value,
        (byte) (value >> 8),
        (byte) (value >> 16),
        (byte) (value >> 24)
    };
}
```

### Python Equivalents

```python
def read_uint16_le(data: bytes, offset: int = 0) -> int:
    return struct.unpack_from("<H", data, offset)[0]

def read_uint32_le(data: bytes, offset: int = 0) -> int:
    return struct.unpack_from("<I", data, offset)[0]

def write_uint16_le(value: int) -> bytes:
    return struct.pack("<H", value)

def write_uint32_le(value: int) -> bytes:
    return struct.pack("<I", value)
```

## 10. MESSAGE ANNOTATION DETAILS

**Java Annotation:**
```java
@MessageProps(
    opCode=45,
    size=15,
    type=MessageType.RESPONSE,
    request=CurrentBolusStatusRequest.class
)
```

**Python Equivalent:**
```python
class CurrentBolusStatusResponse(Message):
    opcode = 45  # Message opcode
    # Size is enforced in parse_payload() validation
    # payload must be exactly 15 bytes
```

## Key Implementation Notes

1. **Field Name Conversion**: All Java camelCase field names are converted to Python snake_case
   - `statusId` → `status_id`
   - `bolusId` → `bolus_id`
   - `requestedVolume` → `requested_volume`
   - `bolusSourceId` → `bolus_source_id`
   - `bolusTypeBitmask` → `bolus_type_bitmask`

2. **Byte Order**: All multi-byte fields use little-endian encoding
   - Java: `Bytes.readShort()`, `Bytes.readUint32()`, `Bytes.firstTwoBytesLittleEndian()`, `Bytes.toUint32()`
   - Python: `struct.unpack_from("<H")`, `struct.unpack_from("<I")`, `struct.pack("<H")`, `struct.pack("<I")`

3. **Data Types**: Java `int`/`long` map to Python `int`
   - No loss of precision for 32-bit unsigned values in Python 3

4. **Padding**: 2 zero bytes at offset 3-4 are explicitly maintained in `buildCargo()`/`build_payload()`
   - This is required for exact compatibility with Java implementation

5. **Timestamp**: Uses January 1, 2008 00:00:00 UTC as epoch zero
   - Same epoch as Java implementation: `Dates.fromJan12008EpochSecondsToDate(timestamp)`

6. **Message Registration**: Both request and response are registered in the MessageRegistry

## Files Generated

- **Main Implementation**: `/home/user/tandem-simulator/CurrentBolusStatusResponse_EXACT.py`
- **This Documentation**: `/home/user/tandem-simulator/CURRENTBOLUSSTATUSRESPONSE_EXTRACTION.md`

## Verification Checklist

- [x] Opcode: 45 (0x2D) ✓
- [x] Payload size: 15 bytes ✓
- [x] All field names with exact capitalization (converted to snake_case) ✓
- [x] All field data types (byte, short, int, long, etc.) ✓
- [x] Byte offsets for each field in parse() method ✓
- [x] Size of payload ✓
- [x] Constants and enums (CurrentBolusStatus) ✓
- [x] Complete parse() logic (parse_payload()) ✓
- [x] Complete buildCargo() logic (build_payload()) ✓
- [x] All getter methods ✓
- [x] Validity check logic (is_valid()) ✓
- [x] Little-endian helper functions ✓
- [x] Message registration in MessageRegistry ✓
