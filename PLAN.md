# Tandem Mobi Insulin Pump Simulator - Implementation Plan

## Project Overview

This project implements a Bluetooth Low Energy (BLE) simulator that emulates a Tandem Mobi insulin pump. The simulator will run on a Raspberry Pi Zero 2W and enable developers to test Android (ControlX2/PumpX2) and iOS (TandemKit) applications without requiring physical pump hardware.

## Architecture Overview

The simulator is built in Python and interacts directly with the Raspberry Pi's Bluetooth stack using BlueZ (via D-Bus) to:
- Advertise as a Tandem pump with the correct BLE services and characteristics
- Handle BLE GATT server operations (read, write, notify)
- Implement the Tandem pump protocol including authentication, message handling, and responses
- Provide a Terminal User Interface (TUI) for configuration and monitoring

## Technical Foundation

### Bluetooth Protocol Details

Based on analysis of the PumpX2 Android library, the Tandem pump uses the following Bluetooth specifications:

**Device Discovery:**
- Device name pattern: `"tslim X2"` (prefix match)
- Advertised service: `0000fdfb-0000-1000-8000-00805f9b34fb` (PUMP_SERVICE_UUID)

**BLE GATT Services:**
1. **Pump Service** (`0000fdfb-0000-1000-8000-00805f9b34fb`)
   - Current Status: `7B83FFF6-9F77-4E5C-8064-AAE2C24838B9`
   - Qualifying Events: `7B83FFF7-9F77-4E5C-8064-AAE2C24838B9`
   - History Log: `7B83FFF8-9F77-4E5C-8064-AAE2C24838B9`
   - Authorization: `7B83FFF9-9F77-4E5C-8064-AAE2C24838B9`
   - Control: `7B83FFFC-9F77-4E5C-8064-AAE2C24838B9`
   - Control Stream: `7B83FFFD-9F77-4E5C-8064-AAE2C24838B9`

2. **Device Information Service** (`0000180A-0000-1000-8000-00805f9b34fb`)
   - Manufacturer Name: `00002A29-0000-1000-8000-00805f9b34fb`
   - Model Number: `00002A24-0000-1000-8000-00805f9b34fb`
   - Serial Number: `00002a25-0000-1000-8000-00805f9b34fb`
   - Software Revision: `00002a28-0000-1000-8000-00805f9b34fb`

3. **Generic Access Service** (`00001800-0000-1000-8000-00805f9b34fb`)
   - Device Name: `00002a00-0000-1000-8000-00805f9b34fb`
   - Appearance: `00002a01-0000-1000-8000-00805f9b34fb`
   - Preferred Connection Parameters: `00002a04-0000-1000-8000-00805f9b34fb`
   - Central Address Resolution: `00002aa6-0000-1000-8000-00805f9b34fb`

4. **Generic Attribute Service** (`00001801-0000-1000-8000-00805f9b34fb`)
   - Service Changed: `00002A05-0000-1000-8000-00805F9B34FB`

**Message Protocol:**
- Header: 3 bytes (opcode, transaction ID, payload length)
- Payload: Variable length cargo data
- Authentication: 24 bytes for signed messages (HMAC-SHA1 + timestamp)
- CRC16: Checksum appended to packet
- Chunking: Messages split into 18-byte chunks (40 bytes for control messages)
- Opcodes: Even = requests, Odd = responses

**Authentication Protocol:**
- JPake (Janssen-Peacock Authentication Key Exchange) - 4 stages
- Central Challenge / Pump Challenge flow
- Pairing code verification
- HMAC-SHA1 for signed message authentication

## Implementation Milestones

### Milestone 1: BLE Peripheral Infrastructure (Foundation)
**Goal:** Raspberry Pi advertises as a Tandem pump and logs all BLE interactions

**Components:**
1. **BlueZ/D-Bus Integration**
   - Python D-Bus bindings for BlueZ 5.x
   - GATT server application registration
   - Advertisement registration and management
   - Proper cleanup and error handling

2. **BLE Advertisement**
   - Device name: "tslim X2 [SERIAL]"
   - Advertise PUMP_SERVICE_UUID
   - Set appropriate advertisement flags and power level
   - Handle discoverable/connectable states

3. **GATT Services and Characteristics**
   - Implement all 4 core services (Pump, DIS, Generic Access, Generic Attribute)
   - Configure characteristic properties (read, write, notify, indicate)
   - Set up Client Characteristic Configuration Descriptors (CCCD) for notifications
   - Implement characteristic read/write callbacks

4. **Connection Management**
   - Track connected central devices
   - Handle connection/disconnection events
   - Manage MTU negotiation
   - Support bonding/pairing workflows

5. **Logging Infrastructure**
   - Structured logging for all BLE events
   - Connection state changes
   - Characteristic read/write operations
   - Raw data dumps (hex format)
   - Performance metrics

**Deliverables:**
- `ble_peripheral.py`: Core BLE peripheral implementation
- `gatt_server.py`: GATT service and characteristic definitions
- `advertisement.py`: BLE advertisement management
- `logger.py`: Structured logging utilities
- `requirements.txt`: Python dependencies (python-dbus, pygobject, etc.)
- `README_SETUP.md`: Pi Zero 2W setup instructions

**Success Criteria:**
- Pi appears as "tslim X2" in BLE scans
- Android/iOS apps can discover the device
- Connection attempts are logged with full details
- Reads/writes to characteristics are captured and logged

---

### Milestone 2: Message Protocol Implementation (Core Protocol)
**Goal:** Parse and construct Tandem protocol messages in Python

**Components:**
1. **Message Structure Framework**
   - Base `Message` class with parse/serialize methods
   - Message registry mapping opcodes to message classes
   - Transaction ID management
   - Message type differentiation (Request/Response)

2. **Packet Assembly/Disassembly**
   - `Packetizer` class for chunking/reassembly
   - Header parsing (opcode, transaction ID, payload length)
   - CRC16 calculation and validation
   - Chunk sequencing and reconstruction
   - MTU-aware chunking (18 bytes default, 40 for control)

3. **Critical Message Types** (Ported from PumpX2)
   - **Authentication Messages:**
     - `CentralChallengeRequest` / `CentralChallengeResponse`
     - `PumpChallengeRequest` / `PumpChallengeResponse`
     - `Jpake1aRequest/Response`, `Jpake1bRequest/Response`
     - `Jpake2Request/Response`
     - `Jpake3SessionKeyRequest/Response`
     - `Jpake4KeyConfirmationRequest/Response`

   - **Core Status Messages:**
     - `ApiVersionRequest/Response`
     - `PumpVersionRequest/Response`
     - `TimeSinceResetRequest/Response`
     - `CurrentBatteryV1Request/Response`
     - `CurrentBasalStatusRequest/Response`
     - `CurrentBolusStatusRequest/Response`
     - `InsulinStatusRequest/Response`
     - `PumpSettingsRequest/Response`

   - **Device Information:**
     - Manufacturer name, model number, serial number responses
     - Software revision response

4. **Message Routing**
   - Map characteristics to message categories
   - Route incoming messages to appropriate handlers
   - Queue outgoing messages for transmission
   - Handle multi-chunk message assembly

5. **HMAC/Signed Message Support**
   - HMAC-SHA1 calculation for signed messages
   - Timestamp management (pump time since reset)
   - Signed message validation framework
   - 24-byte authentication block handling

**Deliverables:**
- `protocol/message.py`: Base message classes
- `protocol/packetizer.py`: Packet assembly/disassembly
- `protocol/messages/`: Directory with message implementations
  - `authentication/`: Auth message classes
  - `current_status/`: Status message classes
  - `control/`: Control message classes (stubs)
  - `history_log/`: History message classes (stubs)
- `protocol/message_registry.py`: Opcode to message class mapping
- `protocol/crypto.py`: HMAC and crypto utilities
- `protocol/crc.py`: CRC16 implementation
- `tests/test_messages.py`: Unit tests for message parsing

**Success Criteria:**
- Can parse any message from PumpX2 test data
- Can construct valid response messages
- CRC16 validation passes
- Transaction IDs are properly managed
- Messages serialize/deserialize correctly

---

### Milestone 3: Authentication and Pairing (Security Layer)
**Goal:** Android/iOS apps can successfully pair with the simulator

**Components:**
1. **JPake Protocol Implementation**
   - Full 4-round JPake key exchange
   - Elliptic curve cryptography (as used by Tandem)
   - Shared secret derivation
   - Session key generation

2. **Pairing Code Management**
   - Generate valid 6-digit pairing codes
   - Display codes in console/TUI
   - Timeout handling (typical 60-second window)
   - Code verification

3. **Challenge-Response Flow**
   - Central challenge generation and validation
   - Pump challenge response
   - Sequence state management
   - Error handling and retry logic

4. **Session Management**
   - Store paired device information
   - Persist pairing data across restarts
   - Session key caching
   - Re-authentication handling

5. **Bluetooth Security**
   - BLE pairing with PIN/passkey
   - Bonding information storage
   - Encrypted connection support
   - MITM protection

**Deliverables:**
- `authentication/jpake.py`: JPake protocol implementation
- `authentication/pairing.py`: Pairing code and flow management
- `authentication/session.py`: Session key and state management
- `authentication/challenge.py`: Challenge-response handlers
- `storage/paired_devices.json`: Persisted pairing data
- `tests/test_jpake.py`: JPake crypto tests
- `AUTHENTICATION.md`: Documentation of auth flow

**Success Criteria:**
- PumpX2 Android app completes pairing
- TandemKit iOS app completes pairing
- Pairing code is displayed and accepted
- Session persists across reconnections
- Can re-authenticate without re-pairing

---

### Milestone 4: Request/Response Handling (Functional Layer)
**Goal:** Respond to app commands with realistic stub data

**Components:**
1. **Request Handler Framework**
   - Route requests to appropriate handlers
   - Async request processing
   - Response queue management
   - Error response generation

2. **Status Request Handlers**
   - Battery status (configurable percentage)
   - Basal rate (configurable current rate)
   - Bolus status (idle/active states)
   - Insulin on board calculations
   - CGM data (configurable glucose value)
   - Alert/alarm status
   - Time synchronization

3. **Control Request Handlers** (Stub Implementation)
   - Bolus initiation (acknowledge but don't "deliver")
   - Suspend/resume (update internal state)
   - Settings changes (accept and store)
   - Cartridge change mode
   - Profile switching

4. **History Log Handlers** (Stub Implementation)
   - Return empty or minimal history
   - Support history log sequence numbers
   - Handle date range queries

5. **Qualifying Events**
   - Generate simulated pump events
   - Send notifications for alerts (configurable)
   - Handle event acknowledgment

6. **State Management**
   - Internal pump state model
   - State persistence
   - State updates based on commands
   - Realistic state transitions

**Deliverables:**
- `handlers/request_handler.py`: Request routing
- `handlers/status.py`: Status request handlers
- `handlers/control.py`: Control request handlers (stubs)
- `handlers/history.py`: History request handlers (stubs)
- `handlers/events.py`: Qualifying event handlers
- `state/pump_state.py`: Internal pump state model
- `state/state_persistence.py`: State save/load
- `config/default_state.json`: Default pump configuration
- `tests/test_handlers.py`: Handler unit tests

**Success Criteria:**
- ControlX2 app displays pump status
- Battery level shows correctly
- Basal rate displays
- Can initiate a test bolus (simulator acknowledges)
- No crashes on any request type
- Unknown requests return appropriate errors

---

### Milestone 5: Terminal User Interface (Management Layer)
**Goal:** Interactive TUI for configuring simulator and monitoring activity

**Components:**
1. **TUI Framework**
   - Built with `textual` or `rich` library
   - Responsive layout
   - Keyboard navigation
   - Live updates

2. **Dashboard View**
   - Connection status (connected/disconnected, device name)
   - Current pump state (battery, basal, bolus, IOB, etc.)
   - Recent messages log (scrollable)
   - Active alerts/alarms
   - Session information (paired devices, uptime)

3. **Configuration Panel**
   - **Pump Identity:**
     - Serial number
     - Model number (Mobi, t:slim X2)
     - Firmware version
     - Manufacture date

   - **Pump Status:**
     - Battery level (0-100%)
     - Current basal rate (U/hr)
     - Active insulin (IOB)
     - Reservoir volume (U)
     - CGM glucose value (mg/dL)
     - CGM trend arrow

   - **Behavior Settings:**
     - Auto-generate events (on/off)
     - Event frequency
     - Enable/disable specific alerts
     - Response delay simulation

4. **Event Generator**
   - Manual event triggering
   - Scheduled event creation
   - Alert/alarm simulation
   - Low battery alerts
   - Occlusion alerts
   - CGM alert simulation

5. **Logging View**
   - Real-time message traffic
   - Filter by message type
   - Search functionality
   - Export to file

6. **Control Interface**
   - Start/stop advertising
   - Disconnect current client
   - Clear paired devices
   - Reset to defaults
   - Shutdown gracefully

**Deliverables:**
- `tui/app.py`: Main TUI application
- `tui/dashboard.py`: Dashboard view
- `tui/config_panel.py`: Configuration interface
- `tui/event_generator.py`: Event simulation controls
- `tui/log_view.py`: Message logging view
- `tui/controls.py`: System control widgets
- `config/tui_config.json`: TUI preferences
- `USAGE.md`: TUI user guide

**Success Criteria:**
- TUI launches and displays pump state
- Can modify battery level and see it reflected in app
- Can change basal rate and see it in app
- Can generate a low battery alert and see it in app
- Message log shows real-time traffic
- Configuration persists across restarts
- No TUI crashes or freezes

---

### Milestone 6: Advanced Features and Polish (Enhancement Layer)
**Goal:** Production-ready simulator with advanced testing capabilities

**Components:**
1. **Multiple Pump Profiles**
   - Save/load different pump configurations
   - Quick switch between profiles
   - Pre-defined scenarios (low battery, high glucose, active bolus, etc.)

2. **Scripted Scenarios**
   - YAML-based scenario definitions
   - Automated event sequences
   - Timeline-based state changes
   - Useful for regression testing

3. **Network API** (Optional)
   - REST API for remote control
   - WebSocket for real-time monitoring
   - Enable automation and CI/CD integration
   - Useful for automated testing

4. **Advanced Logging**
   - Packet capture to PCAP format
   - Message replay capability
   - Performance profiling
   - Statistical analysis

5. **Documentation**
   - Complete API documentation
   - Protocol reverse-engineering notes
   - Testing guide
   - Troubleshooting guide
   - Contributing guidelines

6. **Robust Error Handling**
   - Graceful degradation
   - Invalid message handling
   - Connection recovery
   - Resource cleanup

7. **Performance Optimization**
   - Reduce memory footprint
   - Optimize message processing
   - Efficient state updates
   - Battery optimization for Pi Zero 2W

**Deliverables:**
- `profiles/`: Directory with pre-defined profiles
- `scenarios/`: YAML scenario definitions
- `api/rest_server.py`: REST API (optional)
- `api/websocket_server.py`: WebSocket server (optional)
- `capture/pcap_writer.py`: PCAP export
- `capture/replay.py`: Message replay tool
- `docs/PROTOCOL.md`: Protocol documentation
- `docs/API.md`: API reference
- `docs/TESTING.md`: Testing guide
- `docs/TROUBLESHOOTING.md`: Common issues
- `CONTRIBUTING.md`: Contribution guide

**Success Criteria:**
- Can switch between pump profiles without restart
- Scripted scenarios execute correctly
- REST API (if implemented) responds to requests
- PCAP files can be opened in Wireshark
- Documentation is complete and accurate
- No memory leaks during extended operation

---

## Development Environment

### Hardware Requirements
- Raspberry Pi Zero 2W (or any Pi with built-in Bluetooth)
- MicroSD card (16GB+ recommended)
- Power supply
- (Optional) USB-to-serial adapter for debugging

### Software Requirements
- Raspberry Pi OS Lite (Debian 12 Bookworm or later)
- Python 3.9+
- BlueZ 5.50+
- Python packages:
  - `python-dbus` - D-Bus bindings
  - `pygobject` - GObject introspection
  - `textual` or `rich` - TUI framework
  - `cryptography` - Crypto operations
  - `pyyaml` - Configuration parsing
  - `pytest` - Testing framework

### Development Workflow
1. Develop and test on development machine (mock BLE stack)
2. Unit test all message parsing/generation
3. Deploy to Raspberry Pi for integration testing
4. Test with actual Android/iOS apps
5. Iterate based on app behavior

---

## Testing Strategy

### Unit Tests
- Message parsing and serialization
- CRC16 calculation
- JPake cryptographic operations
- Packet assembly/disassembly
- State transitions

### Integration Tests
- Full authentication flow
- Request/response cycles
- Multi-chunk message handling
- Connection/disconnection sequences
- Error conditions

### End-to-End Tests
- Pairing with ControlX2 (Android)
- Pairing with TandemKit (iOS)
- Reading pump status
- Sending control commands
- Event notification delivery
- Session persistence

### Performance Tests
- Message throughput
- Memory usage over time
- Connection stability
- Multiple reconnection cycles
- Concurrent operation stress

---

## Risk Mitigation

### Technical Risks
1. **JPake Implementation Complexity**
   - Mitigation: Reference existing implementations, extensive testing
   - Fallback: Simplified auth mode for development

2. **BlueZ API Changes**
   - Mitigation: Target specific BlueZ version, document dependencies
   - Fallback: Abstract BLE layer for portability

3. **Message Protocol Gaps**
   - Mitigation: Extensive logging to identify missing messages
   - Fallback: Generic message handler for unknowns

4. **Raspberry Pi Resource Constraints**
   - Mitigation: Profile early, optimize critical paths
   - Fallback: Support Pi 3/4 for development

### Project Risks
1. **Incomplete Protocol Documentation**
   - Mitigation: Analyze real pump traffic, collaborate with PumpX2 maintainer
   - Fallback: Implement subset for basic testing

2. **App Compatibility Issues**
   - Mitigation: Test with multiple app versions
   - Fallback: Document known incompatibilities

---

## Success Metrics

### Milestone 1 Success
- ✅ Device discoverable by apps
- ✅ Can connect and read characteristics
- ✅ All interactions logged

### Milestone 2 Success
- ✅ 90%+ message types parseable
- ✅ All critical messages implemented
- ✅ CRC validation 100% pass rate

### Milestone 3 Success
- ✅ ControlX2 pairs successfully
- ✅ TandemKit pairs successfully
- ✅ Session persists across reconnects

### Milestone 4 Success
- ✅ Apps display pump status
- ✅ Can initiate simulated bolus
- ✅ No crashes on any request

### Milestone 5 Success
- ✅ TUI operational and stable
- ✅ Configuration changes reflected in app
- ✅ Event simulation works correctly

### Milestone 6 Success
- ✅ Production-ready code quality
- ✅ Complete documentation
- ✅ Automated test suite passes

---

## Timeline Estimate

**Milestone 1:** 1-2 weeks
**Milestone 2:** 2-3 weeks
**Milestone 3:** 2-3 weeks
**Milestone 4:** 1-2 weeks
**Milestone 5:** 1-2 weeks
**Milestone 6:** 2-3 weeks

**Total Estimated Time:** 9-15 weeks

---

## References

### Source Repositories
- **PumpX2 (Android):** https://github.com/jwoglom/pumpx2
- **ControlX2 (Android App):** https://github.com/jwoglom/controlx2
- **TandemKit (iOS):** https://github.com/jwoglom/TandemKit

### Key Files to Reference
- `pumpx2/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/bluetooth/ServiceUUID.java`
- `pumpx2/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/bluetooth/CharacteristicUUID.java`
- `pumpx2/androidLib/src/main/java/com/jwoglom/pumpx2/pump/bluetooth/TandemBluetoothHandler.java`
- `pumpx2/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/Message.java`
- `pumpx2/messages/src/main/java/com/jwoglom/pumpx2/pump/messages/Packetize.java`

### Technical Documentation
- BlueZ D-Bus API: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/doc
- JPake Protocol: RFC 8235
- BLE GATT Specification: https://www.bluetooth.com/specifications/specs/

---

## Next Steps

Once this plan is approved, implementation will begin with Milestone 1. Each milestone will be developed iteratively with continuous testing against the real Android and iOS applications.

The modular architecture allows parallel development of different components and makes it easy to extend the simulator with additional features as the protocol understanding deepens.
