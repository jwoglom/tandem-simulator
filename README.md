# Tandem Mobi Insulin Pump Simulator

A Bluetooth Low Energy (BLE) simulator that emulates a Tandem Mobi insulin pump, designed to run on a Raspberry Pi Zero 2W for development and testing of Android (ControlX2/PumpX2) and iOS (TandemKit) applications.

[![CI](https://github.com/jwoglom/tandem-simulator/actions/workflows/ci.yml/badge.svg)](https://github.com/jwoglom/tandem-simulator/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Features

- **BLE Peripheral Emulation**: Simulates a Tandem pump as a BLE peripheral with all required GATT services and characteristics
- **Protocol Implementation**: Implements the Tandem pump protocol including message parsing, authentication, and response generation
- **Configurable State**: Configurable pump state (battery, basal rate, reservoir, etc.) for testing various scenarios
- **Terminal UI**: Interactive TUI for monitoring and controlling the simulator (Milestone 5)
- **Raspberry Pi Optimized**: Designed to run efficiently on Raspberry Pi Zero 2W hardware

## Project Status

**Current Milestone: 4 (Request/Response Handling) - Complete**

This project is under active development. See [PLAN.md](PLAN.md) for the complete implementation roadmap.

### Milestone Progress

- ✅ **Milestone 1**: BLE peripheral infrastructure
  - Basic Python project structure
  - Stub implementations for all major components
  - CI/CD pipeline configured
  - Unit tests framework
- ✅ **Milestone 2**: Message protocol implementation
  - CRC16 calculation and validation
  - Message header parsing and serialization
  - Packet assembly and disassembly (chunking/reassembly)
  - HMAC-SHA1 utilities for signed messages
  - Authentication message classes (stubs for JPake)
  - Status message classes (API version, battery, etc.)
  - Comprehensive test suite (29 tests passing)
- ✅ **Milestone 3**: Authentication and pairing
  - Full JPake (J-PAKE) protocol implementation using elliptic curve cryptography
  - JPake message classes for 4-round key exchange (Jpake1a/1b/2/3/4)
  - Pairing code management with timeout and attempt limiting
  - Session management with persistence to disk
  - Authentication flow coordinator (Authenticator class)
  - Challenge-response message handlers
  - Comprehensive authentication test suite (25+ tests)
- ✅ **Milestone 4**: Request/response handling
  - Request handler framework with routing and error handling
  - Status request handlers (battery, basal, bolus, insulin, API version, pump version)
  - Control request handlers (stub: bolus, suspend, resume)
  - History log handlers (stub implementation)
  - Qualifying events (alerts, alarms, notifications)
  - Pump state management with persistence to disk
  - Default state configuration (JSON)
  - Comprehensive test suite (30+ tests for handlers and state)
- 🔲 **Milestone 5**: Terminal User Interface
- 🔲 **Milestone 6**: Advanced features and polish

## Quick Start

### Installation

#### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. It's the recommended way to set up the project.

**On Development Machine (Linux/macOS):**

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/jwoglom/tandem-simulator.git
cd tandem-simulator

# Create a virtual environment and install dependencies
uv sync

# Run the simulator
uv run python simulator.py --help

# Or activate the virtual environment
source .venv/bin/activate
python simulator.py --help
```

**For development with all dev dependencies:**

```bash
# Install with dev dependencies (includes pytest, black, mypy, etc.)
uv sync --all-extras

# Run tests
uv run pytest

# Format code
uv run black tandem_simulator simulator.py
```

**Using Make (shortcuts for common commands):**

```bash
# Install dependencies
make install        # Production dependencies only
make install-dev    # With dev dependencies

# Run the simulator
make run            # Default settings
make run-debug      # With debug logging
make run-tui        # With TUI

# Development
make test           # Run tests
make test-cov       # Run tests with coverage
make format         # Format code
make lint           # Run linters
make type-check     # Run type checking

# See all available commands
make help
```

#### Using pip (Alternative)

**On Development Machine:**

```bash
# Clone the repository
git clone https://github.com/jwoglom/tandem-simulator.git
cd tandem-simulator

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt

# Run the simulator
python simulator.py --help
```

#### On Raspberry Pi Zero 2W

**Using uv:**

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    bluez

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/jwoglom/tandem-simulator.git
cd tandem-simulator
uv sync

# Run the simulator
uv run python simulator.py
```

**Using pip:**

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    bluez

# Clone and install
git clone https://github.com/jwoglom/tandem-simulator.git
cd tandem-simulator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the simulator
python simulator.py
```

### Usage

**With uv:**

```bash
# Run with default settings
uv run python simulator.py

# Specify a serial number
uv run python simulator.py --serial 12345678

# Enable debug logging
uv run python simulator.py --debug

# Run with Terminal UI (Milestone 5)
uv run python simulator.py --tui
```

**With activated virtual environment:**

```bash
# Activate the virtual environment first
source .venv/bin/activate  # or: uv venv && source .venv/bin/activate

# Run with default settings
python simulator.py

# Specify a serial number
python simulator.py --serial 12345678

# Enable debug logging
python simulator.py --debug

# Run with Terminal UI (Milestone 5)
python simulator.py --tui
```

## Project Structure

```
tandem-simulator/
├── simulator.py              # Main entry point
├── tandem_simulator/         # Main package
│   ├── ble/                  # BLE peripheral implementation
│   │   ├── peripheral.py     # Core BLE peripheral
│   │   ├── gatt_server.py    # GATT services and characteristics
│   │   ├── advertisement.py  # BLE advertisement
│   │   └── connection.py     # Connection management
│   ├── protocol/             # Protocol implementation
│   │   ├── message.py        # Message base classes
│   │   ├── packetizer.py     # Packet assembly/disassembly
│   │   ├── crc.py           # CRC16 calculation
│   │   └── crypto.py        # Cryptographic utilities
│   ├── authentication/       # Authentication/pairing
│   │   ├── jpake.py         # JPake protocol
│   │   ├── pairing.py       # Pairing code management
│   │   └── session.py       # Session management
│   ├── handlers/            # Request handlers
│   │   ├── request_handler.py
│   │   ├── status.py        # Status request handlers
│   │   └── control.py       # Control request handlers
│   ├── state/               # Pump state management
│   │   ├── pump_state.py    # State model
│   │   └── persistence.py   # State persistence
│   ├── tui/                 # Terminal UI
│   │   └── app.py          # TUI application
│   └── utils/               # Utilities
│       ├── logger.py        # Logging infrastructure
│       └── constants.py     # Constants and UUIDs
├── tests/                   # Test suite
├── config/                  # Configuration files
├── .github/workflows/       # CI/CD workflows
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── setup.py                # Package setup
├── pyproject.toml          # Modern Python packaging
└── PLAN.md                 # Implementation plan
```

## Development

### Running Tests

**With uv:**

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=tandem_simulator --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_basic.py -v
```

**With activated virtual environment:**

```bash
# Activate venv first
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=tandem_simulator --cov-report=term-missing

# Run specific test file
pytest tests/test_basic.py -v
```

### Code Quality

**With uv:**

```bash
# Format code
uv run black tandem_simulator simulator.py

# Sort imports
uv run isort tandem_simulator simulator.py

# Lint
uv run flake8 tandem_simulator

# Type check
uv run mypy tandem_simulator

# Run all quality checks at once
uv run black tandem_simulator simulator.py && \
uv run isort tandem_simulator simulator.py && \
uv run flake8 tandem_simulator && \
uv run mypy tandem_simulator
```

**With activated virtual environment:**

```bash
# Format code
black tandem_simulator simulator.py

# Sort imports
isort tandem_simulator simulator.py

# Lint
flake8 tandem_simulator

# Type check
mypy tandem_simulator
```

### Building

**With uv:**

```bash
# Build package
uv build

# Install locally in development mode
uv pip install -e .
```

**With pip:**

```bash
# Build package
python -m build

# Install locally in development mode
pip install -e .
```

## Configuration

The simulator can be configured via `config/default_config.json`:

```json
{
  "pump": {
    "serial_number": "00000000",
    "model_number": "Mobi",
    "firmware_version": "7.7.1"
  },
  "state": {
    "battery_percent": 100,
    "current_basal_rate": 0.85,
    "reservoir_volume": 300.0
  },
  "bluetooth": {
    "discoverable": true,
    "device_name_prefix": "tslim X2"
  }
}
```

## Technical Details

### BLE Protocol

The simulator implements the Tandem pump BLE protocol:

- **Primary Service**: `0000fdfb-0000-1000-8000-00805f9b34fb`
- **Device Information Service**: Standard BLE DIS
- **Authentication**: JPake key exchange with pairing codes
- **Message Protocol**: Custom message format with CRC16 checksums and HMAC signing

See [PLAN.md](PLAN.md) for complete protocol details.

### Hardware Requirements

- **Raspberry Pi Zero 2W** (or any Pi with Bluetooth)
- MicroSD card (16GB+ recommended)
- Power supply
- (Optional) USB-to-serial adapter for debugging

### Software Requirements

- **OS**: Raspberry Pi OS Lite (Debian 12 Bookworm or later)
- **Python**: 3.9+
- **BlueZ**: 5.50+
- **Dependencies**: See `requirements.txt`

## Related Projects

- **[PumpX2](https://github.com/jwoglom/pumpx2)**: Android library for Tandem pump communication
- **[ControlX2](https://github.com/jwoglom/controlx2)**: Android app for pump control
- **[TandemKit](https://github.com/jwoglom/TandemKit)**: iOS library for Tandem pump communication

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This simulator is for **development and testing purposes only**. It is not a medical device and should never be used for actual diabetes management or insulin delivery.

## Acknowledgments

This project is based on analysis of the [PumpX2](https://github.com/jwoglom/pumpx2) Android library and aims to facilitate development and testing of applications that communicate with Tandem insulin pumps.
