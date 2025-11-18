#!/usr/bin/env python3
"""Tandem Mobi Insulin Pump Simulator - Main Entry Point.

This script starts the BLE peripheral simulator for the Tandem Mobi insulin pump.
It can be run in different modes:
- BLE mode: Run as a BLE peripheral (requires BlueZ on Linux)
- TUI mode: Run with Terminal User Interface
- Debug mode: Run with verbose logging

Usage:
    python simulator.py [options]

Options:
    --serial SERIAL     Pump serial number (default: 00000000)
    --tui              Enable Terminal User Interface
    --debug            Enable debug logging
    --help             Show this help message
"""

import argparse
import logging
import sys

from tandem_simulator.ble.peripheral import BLEPeripheral
from tandem_simulator.utils.constants import DEFAULT_SERIAL_NUMBER
from tandem_simulator.utils.logger import get_logger


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Tandem Mobi Insulin Pump Simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simulator.py
  python simulator.py --serial 12345678
  python simulator.py --tui
  python simulator.py --debug

For more information, see the README.md file.
        """,
    )

    parser.add_argument(
        "--serial",
        type=str,
        default=DEFAULT_SERIAL_NUMBER,
        help=f"Pump serial number (default: {DEFAULT_SERIAL_NUMBER})",
    )

    parser.add_argument("--tui", action="store_true", help="Enable Terminal User Interface")

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


def main():
    """Main entry point for the simulator."""
    args = parse_arguments()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = get_logger()
    logger.logger.setLevel(log_level)

    logger.info("=" * 60)
    logger.info("Tandem Mobi Insulin Pump Simulator")
    logger.info("=" * 60)
    logger.info(f"Serial Number: {args.serial}")
    logger.info(f"Debug Mode: {args.debug}")
    logger.info(f"TUI Mode: {args.tui}")
    logger.info("=" * 60)

    if args.tui:
        # Run with TUI
        logger.info("Starting in TUI mode...")
        from tandem_simulator.tui.app import SimulatorTUI

        tui = SimulatorTUI()
        tui.run()
    else:
        # Run in BLE mode
        logger.info("Starting BLE peripheral...")
        logger.info("")
        logger.info("NOTE: This is Milestone 1 (stub implementation)")
        logger.info("      BlueZ D-Bus integration not yet implemented")
        logger.info("      The peripheral will initialize but not actually advertise")
        logger.info("")

        peripheral = BLEPeripheral(serial_number=args.serial)

        try:
            peripheral.run()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error: {e}")
            if args.debug:
                import traceback

                traceback.print_exc()
            sys.exit(1)

    logger.info("Simulator stopped")


if __name__ == "__main__":
    main()
