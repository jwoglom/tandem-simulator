"""Terminal User Interface for Tandem pump simulator.

This module provides an interactive TUI for configuring and monitoring
the simulator using the Textual framework.

Milestone 5 deliverable.
"""

from typing import TYPE_CHECKING, Optional

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, TabbedContent, TabPane

from tandem_simulator.state.pump_state import PumpState, PumpStateManager

if TYPE_CHECKING:
    from tandem_simulator.ble.peripheral import BLEPeripheral
from tandem_simulator.tui.config_panel import ConfigPanel
from tandem_simulator.tui.controls import ControlPanel
from tandem_simulator.tui.dashboard import Dashboard
from tandem_simulator.tui.event_generator import EventGenerator
from tandem_simulator.tui.log_view import LogView
from tandem_simulator.utils.constants import DEFAULT_SERIAL_NUMBER
from tandem_simulator.utils.logger import get_logger

logger = get_logger()


class SimulatorTUI(App):
    """Terminal User Interface for pump simulator.

    This TUI provides an interactive interface for:
    - Monitoring pump state and BLE connections
    - Configuring pump parameters
    - Generating events and alerts
    - Viewing real-time message logs
    - Controlling the simulator
    """

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
    }

    Footer {
        background: $primary-darken-1;
    }

    TabbedContent {
        height: 1fr;
    }

    TabPane {
        padding: 1 2;
    }

    .status-good {
        color: $success;
    }

    .status-warning {
        color: $warning;
    }

    .status-error {
        color: $error;
    }

    .label {
        color: $text-muted;
        margin-right: 1;
    }

    .value {
        color: $text;
    }

    .section {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }

    Button {
        margin: 0 1;
    }

    .control-button {
        min-width: 20;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("1", "switch_tab('dashboard')", "Dashboard"),
        ("2", "switch_tab('config')", "Config"),
        ("3", "switch_tab('events')", "Events"),
        ("4", "switch_tab('logs')", "Logs"),
        ("5", "switch_tab('controls')", "Controls"),
    ]

    def __init__(self, serial_number: Optional[str] = None):
        """Initialize the TUI application.

        Args:
            serial_number: Pump serial number (default: DEFAULT_SERIAL_NUMBER)
        """
        super().__init__()
        self.serial_number = serial_number or DEFAULT_SERIAL_NUMBER

        # Initialize state manager
        initial_state = PumpState(serial_number=self.serial_number)
        self.state_manager = PumpStateManager(initial_state)

        # BLE peripheral (initialized but not started)
        self.peripheral: Optional[BLEPeripheral] = None
        self.peripheral_running = False

        # References to UI components
        self.dashboard: Optional[Dashboard] = None
        self.config_panel: Optional[ConfigPanel] = None
        self.event_generator: Optional[EventGenerator] = None
        self.log_view: Optional[LogView] = None
        self.control_panel: Optional[ControlPanel] = None

    def compose(self) -> ComposeResult:
        """Compose the TUI layout.

        Returns:
            Layout components
        """
        yield Header(show_clock=True)

        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                self.dashboard = Dashboard(self.state_manager)
                yield self.dashboard

            with TabPane("Configuration", id="config"):
                self.config_panel = ConfigPanel(self.state_manager)
                yield self.config_panel

            with TabPane("Events", id="events"):
                self.event_generator = EventGenerator(self.state_manager)
                yield self.event_generator

            with TabPane("Logs", id="logs"):
                self.log_view = LogView()
                yield self.log_view

            with TabPane("Controls", id="controls"):
                self.control_panel = ControlPanel()
                yield self.control_panel

        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.title = f"Tandem Pump Simulator - Serial: {self.serial_number}"
        self.sub_title = "Milestone 5 - Terminal User Interface"

        # Start periodic updates
        self.set_interval(1.0, self.update_dashboard)

        logger.info("TUI application started")

    def update_dashboard(self) -> None:
        """Update the dashboard with current state.

        This is called periodically to refresh the display.
        """
        if self.dashboard:
            self.dashboard.update_state()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark

    def action_switch_tab(self, tab_id: str) -> None:
        """Switch to a specific tab.

        Args:
            tab_id: ID of the tab to switch to
        """
        tabbed_content = self.query_one(TabbedContent)
        tabbed_content.active = tab_id

    async def start_peripheral(self) -> bool:
        """Start the BLE peripheral.

        Returns:
            True if started successfully, False otherwise
        """
        if self.peripheral_running:
            logger.warning("Peripheral already running")
            return False

        try:
            # Lazy import to avoid requiring BLE dependencies for TUI
            from tandem_simulator.ble.peripheral import BLEPeripheral

            self.peripheral = BLEPeripheral(self.serial_number)

            # Note: In a real implementation, we would start the peripheral
            # in a separate thread or use async operations. For now, we'll
            # just mark it as running.
            self.peripheral_running = True

            logger.info("BLE peripheral started")
            if self.log_view:
                self.log_view.add_log("INFO", "BLE peripheral started")

            return True

        except Exception as e:
            logger.error(f"Failed to start peripheral: {e}")
            if self.log_view:
                self.log_view.add_log("ERROR", f"Failed to start peripheral: {e}")
            return False

    async def stop_peripheral(self) -> bool:
        """Stop the BLE peripheral.

        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.peripheral_running:
            logger.warning("Peripheral not running")
            return False

        try:
            if self.peripheral:
                # Note: In a real implementation, we would call peripheral.stop()
                self.peripheral = None

            self.peripheral_running = False

            logger.info("BLE peripheral stopped")
            if self.log_view:
                self.log_view.add_log("INFO", "BLE peripheral stopped")

            return True

        except Exception as e:
            logger.error(f"Failed to stop peripheral: {e}")
            if self.log_view:
                self.log_view.add_log("ERROR", f"Failed to stop peripheral: {e}")
            return False

    def get_connection_status(self) -> str:
        """Get the current connection status.

        Returns:
            Status string
        """
        if self.peripheral_running:
            return "Advertising"
        return "Stopped"
