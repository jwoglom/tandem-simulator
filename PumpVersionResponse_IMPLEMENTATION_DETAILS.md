# PumpVersionResponse - EXACT Java to Python Implementation

## Source Repository
**Java Source**: https://github.com/jwoglom/pumpX2/blob/main/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/response/currentStatus/PumpVersionResponse.java

## Message Properties

| Property | Value |
|----------|-------|
| Opcode | 85 (0x55) |
| Message Type | RESPONSE |
| Payload Size | 48 bytes (fixed) |
| Encoding | Little-endian (LE) |
| Base Class | Message (extends protocol.Message) |
| Request Pair | PumpVersionRequest (opcode 84) |

## Field Layout & Byte Offsets

| Offset | Field Name | Type | Size | Java Type | Description |
|--------|------------|------|------|-----------|-------------|
| [0-3] | arm_sw_ver | uint32 LE | 4 bytes | long | ARM software version |
| [4-7] | msp_sw_ver | uint32 LE | 4 bytes | long | MSP software version |
| [8-11] | config_a_bits | uint32 LE | 4 bytes | long | Configuration A bits |
| [12-15] | config_b_bits | uint32 LE | 4 bytes | long | Configuration B bits |
| [16-19] | serial_num | uint32 LE | 4 bytes | long | Serial number |
| [20-23] | part_num | uint32 LE | 4 bytes | long | Part number |
| [24-31] | pump_rev | String | 8 bytes | String | Pump revision (null-padded) |
| [32-35] | pcba_sn | uint32 LE | 4 bytes | long | PCBA serial number |
| [36-43] | pcba_rev | String | 8 bytes | String | PCBA revision (null-padded) |
| [44-47] | model_num | uint32 LE | 4 bytes | long | Model number |

**Total Payload: 48 bytes**

## Java Implementation Details

### Class Definition
```java
@MessageProps(
    opCode=85,
    size=48,
    type=MessageType.RESPONSE,
    request=PumpVersionRequest.class
)
public class PumpVersionResponse extends Message { ... }
```

### Field Declarations (Java)
```java
private long armSwVer;      // camelCase in Java
private long mspSwVer;
private long configABits;
private long configBBits;
private long serialNum;
private long partNum;
private String pumpRev;
private long pcbaSN;
private String pcbaRev;
private long modelNum;
```

### parse() Method (Exact Java Logic)
```java
public void parse(byte[] raw) {
    Validate.isTrue(raw.length == props().size());  // Must be 48 bytes
    this.cargo = raw;
    this.armSwVer = Bytes.readUint32(raw, 0);      // 4 bytes @ offset 0
    this.mspSwVer = Bytes.readUint32(raw, 4);      // 4 bytes @ offset 4
    this.configABits = Bytes.readUint32(raw, 8);   // 4 bytes @ offset 8
    this.configBBits = Bytes.readUint32(raw, 12);  // 4 bytes @ offset 12
    this.serialNum = Bytes.readUint32(raw, 16);    // 4 bytes @ offset 16
    this.partNum = Bytes.readUint32(raw, 20);      // 4 bytes @ offset 20
    this.pumpRev = Bytes.readString(raw, 24, 8);   // 8 bytes @ offset 24
    this.pcbaSN = Bytes.readUint32(raw, 32);       // 4 bytes @ offset 32
    this.pcbaRev = Bytes.readString(raw, 36, 8);   // 8 bytes @ offset 36
    this.modelNum = Bytes.readUint32(raw, 44);     // 4 bytes @ offset 44
}
```

### buildCargo() Method (Exact Java Logic)
```java
public static byte[] buildCargo(long armSwVer, long mspSwVer, long configABits, 
                                 long configBBits, long serialNum, long partNum, 
                                 String pumpRev, long pcbaSN, String pcbaRev, 
                                 long modelNum) {
    return Bytes.combine(
        Bytes.toUint32(armSwVer),      // Convert to 4-byte LE
        Bytes.toUint32(mspSwVer),
        Bytes.toUint32(configABits),
        Bytes.toUint32(configBBits),
        Bytes.toUint32(serialNum),
        Bytes.toUint32(partNum),
        Bytes.writeString(pumpRev, 8), // 8-byte fixed-length string
        Bytes.toUint32(pcbaSN),
        Bytes.writeString(pcbaRev, 8),
        Bytes.toUint32(modelNum));
}
```

### Getter Methods (Java)
```java
public long getArmSwVer() { return armSwVer; }
public long getMspSwVer() { return mspSwVer; }
public long getConfigABits() { return configABits; }
public long getConfigBBits() { return configBBits; }
public long getSerialNum() { return serialNum; }
public long getPartNum() { return partNum; }
public String getPumpRev() { return pumpRev; }
public long getPcbaSN() { return pcbaSN; }
public String getPcbaRev() { return pcbaRev; }
public long getModelNum() { return modelNum; }
```

## Python Implementation Details

### Python File: PumpVersionResponse_EXACT.py

**Location**: `/home/user/tandem-simulator/PumpVersionResponse_EXACT.py`

**Key Classes**:
- `PumpVersionResponse`: Main message class
  - `opcode = 85`
  - `payload_size = 48`

**Key Methods**:
- `parse(raw: bytes) -> PumpVersionResponse`: Static method to parse 48-byte payload
- `build_cargo(...) -> bytes`: Static method to build 48-byte payload
- `build_payload() -> bytes`: Instance method to serialize

**Field Names** (Python snake_case):
- `arm_sw_ver` (matches Java camelCase: armSwVer)
- `msp_sw_ver` (matches: mspSwVer)
- `config_a_bits` (matches: configABits)
- `config_b_bits` (matches: configBBits)
- `serial_num` (matches: serialNum)
- `part_num` (matches: partNum)
- `pump_rev` (matches: pumpRev)
- `pcba_sn` (matches: pcbaSN)
- `pcba_rev` (matches: pcbaRev)
- `model_num` (matches: modelNum)

### Helper Functions (Byte Utilities)

| Python Function | Java Equivalent | Purpose |
|-----------------|-----------------|---------|
| `read_uint32_le(data, offset)` | `Bytes.readUint32()` | Read 32-bit unsigned LE integer |
| `write_uint32_le(value)` | `Bytes.toUint32()` | Write 32-bit unsigned LE integer |
| `read_string(data, offset, length)` | `Bytes.readString()` | Read fixed-length null-padded string |
| `write_string(value, length)` | `Bytes.writeString()` | Write fixed-length null-padded string |
| `combine(*byte_arrays)` | `Bytes.combine()` | Concatenate multiple byte arrays |

### Encoding Details

**Integer Encoding**: Little-endian (LE) format using `struct` module
- `struct.pack("<I", value)` for encoding (4 bytes)
- `struct.unpack_from("<I", data, offset)` for decoding

**String Encoding**: 
- UTF-8 encoding with null-byte padding
- Fixed 8-byte length for `pump_rev` and `pcba_rev`
- Trailing nulls stripped on read, padded on write

## Test Results

All tests pass:

1. **Serialization Test**: Creates valid 48-byte payload
2. **Parsing Test**: Correctly parses all 10 fields
3. **Round-Trip Test**: Serialize -> Parse -> Serialize produces identical bytes
4. **Byte Offset Verification**: All fields at correct offsets with correct endianness

### Example Payload
```
Test values:
  arm_sw_ver:    0x01020304
  msp_sw_ver:    0x05060708
  config_a_bits: 0x09000A00
  config_b_bits: 0x0B000C00
  serial_num:    12345
  part_num:      67890
  pump_rev:      "T1.2.3"
  pcba_sn:       11111
  pcba_rev:      "V2.0.1"
  model_num:     42

Generated Payload (48 bytes):
0403020108070605000a0009000c000b393000003209010054312e322e330000672b000056322e302e3100002a000000

Byte breakdown:
  [0-3]:   04030201 = 0x01020304 (little-endian armSwVer)
  [4-7]:   08070605 = 0x05060708 (little-endian mspSwVer)
  [8-11]:  000a0009 = 0x09000A00 (little-endian configABits)
  [12-15]: 000c000b = 0x0B000C00 (little-endian configBBits)
  [16-19]: 39300000 = 12345 (little-endian serialNum)
  [20-23]: 32090100 = 67890 (little-endian partNum)
  [24-31]: 54312e322e330000 = "T1.2.3\0\0" (pumpRev, null-padded)
  [32-35]: 672b0000 = 11111 (little-endian pcbaSN)
  [36-43]: 56322e302e310000 = "V2.0.1\0\0" (pcbaRev, null-padded)
  [44-47]: 2a000000 = 42 (little-endian modelNum)
```

## Integration Notes

The Python implementation can be integrated with the tandem-simulator project by:

1. **Standalone Usage**: Import and use directly
   ```python
   from PumpVersionResponse_EXACT import PumpVersionResponse
   
   # Parse
   response = PumpVersionResponse.parse(payload_bytes)
   
   # Serialize
   payload = response.build_payload()
   ```

2. **Message Handler Integration**: Extend existing Message base class
   ```python
   class PumpVersionResponse(Message):
       opcode = 85
       
       def parse_payload(self, payload: bytes) -> None:
           msg = PumpVersionResponse.parse(payload)
           # Copy fields from msg to self
   ```

3. **Register with MessageRegistry**:
   ```python
   from tandem_simulator.protocol.message import MessageRegistry
   MessageRegistry.register(85, PumpVersionResponse)
   ```

## Verification Against Java Source

✅ Opcode: 85 (confirmed)
✅ Message size: 48 bytes (confirmed)
✅ Field count: 10 fields (confirmed)
✅ Field names: Exact mapping camelCase → snake_case (confirmed)
✅ Field types: All uint32 except 2 strings (confirmed)
✅ Byte offsets: Verified with test payload (confirmed)
✅ Encoding: Little-endian integers, null-padded strings (confirmed)
✅ Parse logic: Sequential read with Bytes.readUint32/readString (confirmed)
✅ Build logic: Bytes.combine with toUint32/writeString (confirmed)
✅ Round-trip: Serialize -> Parse -> Serialize produces identical bytes (confirmed)

## Files Generated

1. **PumpVersionResponse_EXACT.py**: Complete Python implementation with tests
2. **PumpVersionResponse_IMPLEMENTATION_DETAILS.md**: This documentation

