"""Terminal User Interface for simulator control.

This module provides an interactive TUI for configuring the simulator
and monitoring BLE activity in real-time.

Milestone 5 deliverable.
"""

from tandem_simulator.tui.app import SimulatorTUI
from tandem_simulator.tui.config_panel import ConfigPanel
from tandem_simulator.tui.controls import ControlPanel
from tandem_simulator.tui.dashboard import Dashboard
from tandem_simulator.tui.event_generator import EventGenerator
from tandem_simulator.tui.log_view import LogView

__all__ = [
    "SimulatorTUI",
    "Dashboard",
    "ConfigPanel",
    "EventGenerator",
    "LogView",
    "ControlPanel",
]
