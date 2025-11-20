"""Control panel for the TUI.

This module provides system controls for managing the simulator.

Milestone 5 deliverable.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Label, Static

from tandem_simulator.utils.logger import get_logger

logger = get_logger()


class ControlPanel(Container):
    """Control panel for managing the simulator."""

    def compose(self) -> ComposeResult:
        """Compose the control panel layout.

        Returns:
            Layout components
        """
        with Vertical():
            yield Static("🎮 Simulator Controls", classes="section")

            # BLE Controls
            with Container(classes="section"):
                yield Static("📡 BLE Peripheral Control", classes="label")
                yield Label("Status: Stopped", id="ble-status", classes="value")
                with Horizontal():
                    yield Button(
                        "Start Advertising",
                        id="btn-start-ble",
                        variant="success",
                        classes="control-button",
                    )
                    yield Button(
                        "Stop Advertising",
                        id="btn-stop-ble",
                        variant="warning",
                        classes="control-button",
                    )

            # Connection Controls
            with Container(classes="section"):
                yield Static("🔌 Connection Control", classes="label")
                yield Label("Connected Clients: 0", id="client-count", classes="value")
                with Horizontal():
                    yield Button(
                        "Disconnect All",
                        id="btn-disconnect-all",
                        variant="warning",
                        classes="control-button",
                    )

            # Session Management
            with Container(classes="section"):
                yield Static("🔐 Session Management", classes="label")
                yield Label("Paired Devices: 0", id="paired-count", classes="value")
                with Horizontal():
                    yield Button(
                        "Clear Paired Devices",
                        id="btn-clear-paired",
                        variant="error",
                        classes="control-button",
                    )
                    yield Button(
                        "Clear Session",
                        id="btn-clear-session",
                        variant="warning",
                        classes="control-button",
                    )

            # State Management
            with Container(classes="section"):
                yield Static("💾 State Management", classes="label")
                with Horizontal():
                    yield Button(
                        "Save State",
                        id="btn-save-state",
                        variant="primary",
                        classes="control-button",
                    )
                    yield Button(
                        "Load State",
                        id="btn-load-state",
                        variant="primary",
                        classes="control-button",
                    )
                    yield Button(
                        "Reset to Defaults",
                        id="btn-reset-state",
                        variant="error",
                        classes="control-button",
                    )

            # Application Controls
            with Container(classes="section"):
                yield Static("⚙️ Application Control", classes="label")
                with Horizontal():
                    yield Button(
                        "Reload Configuration",
                        id="btn-reload-config",
                        variant="primary",
                        classes="control-button",
                    )
                    yield Button(
                        "Exit Application",
                        id="btn-exit",
                        variant="error",
                        classes="control-button",
                    )

            # Status message
            yield Static("", id="control-status", classes="value")

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.update_status()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button pressed event
        """
        button_id = event.button.id
        status_label = self.query_one("#control-status", Static)

        try:
            if button_id == "btn-start-ble":
                # Start BLE peripheral
                self.app.run_worker(self.app.start_peripheral())
                status_label.update("📡 Starting BLE advertising...")
                logger.info("Starting BLE peripheral via TUI")
                self.update_status()

            elif button_id == "btn-stop-ble":
                # Stop BLE peripheral
                self.app.run_worker(self.app.stop_peripheral())
                status_label.update("📡 Stopping BLE advertising...")
                logger.info("Stopping BLE peripheral via TUI")
                self.update_status()

            elif button_id == "btn-disconnect-all":
                status_label.update("🔌 Disconnecting all clients...")
                logger.info("Disconnecting all clients via TUI")

            elif button_id == "btn-clear-paired":
                status_label.update("🔐 Clearing paired devices...")
                logger.info("Clearing paired devices via TUI")
                # TODO: Implement paired device clearing

            elif button_id == "btn-clear-session":
                status_label.update("🔐 Clearing session...")
                logger.info("Clearing session via TUI")
                # TODO: Implement session clearing

            elif button_id == "btn-save-state":
                status_label.update("💾 Saving state...")
                logger.info("Saving state via TUI")
                # TODO: Implement state persistence

            elif button_id == "btn-load-state":
                status_label.update("💾 Loading state...")
                logger.info("Loading state via TUI")
                # TODO: Implement state loading

            elif button_id == "btn-reset-state":
                # Reset state to defaults
                from tandem_simulator.state.pump_state import PumpState

                self.app.state_manager.set_state(PumpState(serial_number=self.app.serial_number))
                status_label.update("💾 State reset to defaults")
                logger.info("State reset to defaults via TUI")

            elif button_id == "btn-reload-config":
                status_label.update("⚙️ Reloading configuration...")
                logger.info("Reloading configuration via TUI")
                # TODO: Implement config reloading

            elif button_id == "btn-exit":
                logger.info("Exiting application via TUI")
                self.app.exit()

        except Exception as e:
            status_label.update(f"❌ Error: {e}")
            logger.error(f"Error in control panel: {e}")

    def update_status(self) -> None:
        """Update the status displays."""
        # Update BLE status
        ble_status_label = self.query_one("#ble-status", Label)
        status = self.app.get_connection_status()
        ble_status_label.update(f"Status: {status}")

        # Update client count
        # client_count_label = self.query_one("#client-count", Label)
        # client_count_label.update(f"Connected Clients: {count}")

        # Update paired count
        # paired_count_label = self.query_one("#paired-count", Label)
        # paired_count_label.update(f"Paired Devices: {count}")
