"""Dashboard view for the TUI.

This module provides the main dashboard showing pump state and connection status.

Milestone 5 deliverable.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Label, Static

from tandem_simulator.state.pump_state import PumpStateManager


class Dashboard(Container):
    """Dashboard view showing current pump state and connection status."""

    def __init__(self, state_manager: PumpStateManager):
        """Initialize the dashboard.

        Args:
            state_manager: Pump state manager
        """
        super().__init__()
        self.state_manager = state_manager

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout.

        Returns:
            Layout components
        """
        with Vertical():
            yield Static("📊 Pump Status Dashboard", classes="section")

            # Connection Status
            with Container(classes="section"):
                yield Static("🔗 Connection Status", classes="label")
                yield Label("Status: Disconnected", id="connection-status", classes="value")
                yield Label("Device Name: tslim X2", id="device-name", classes="value")
                yield Label("Uptime: 0s", id="uptime", classes="value")

            # Battery & Power
            with Container(classes="section"):
                yield Static("🔋 Battery & Power", classes="label")
                yield Label("Battery: 100%", id="battery-status", classes="value")
                yield Label("Status: Normal", id="power-status", classes="value status-good")

            # Basal Delivery
            with Container(classes="section"):
                yield Static("💉 Basal Delivery", classes="label")
                yield Label("Current Rate: 0.00 U/hr", id="basal-rate", classes="value")
                yield Label("Active: Yes", id="basal-active", classes="value status-good")

            # Bolus Status
            with Container(classes="section"):
                yield Static("💊 Bolus Status", classes="label")
                yield Label("Active: No", id="bolus-active", classes="value")
                yield Label("Amount: 0.00 U", id="bolus-amount", classes="value")
                yield Label("Delivered: 0.00 U", id="bolus-delivered", classes="value")

            # Insulin
            with Container(classes="section"):
                yield Static("🧪 Insulin", classes="label")
                yield Label("Reservoir: 300.0 U", id="reservoir", classes="value")
                yield Label("Insulin on Board: 0.0 U", id="insulin-on-board", classes="value")

            # CGM (if applicable)
            with Container(classes="section"):
                yield Static("📈 CGM", classes="label")
                yield Label("Glucose: -- mg/dL", id="cgm-glucose", classes="value")
                yield Label("Trend: --", id="cgm-trend", classes="value")

            # Device Info
            with Container(classes="section"):
                yield Static("ℹ️ Device Information", classes="label")
                yield Label(
                    f"Serial: {self.state_manager.state.serial_number}",
                    id="serial-number",
                    classes="value",
                )
                yield Label(
                    f"Firmware: {self.state_manager.state.firmware_version}",
                    id="firmware-version",
                    classes="value",
                )

    def update_state(self) -> None:
        """Update the dashboard with current state."""
        state = self.state_manager.state

        # Update battery
        battery_label = self.query_one("#battery-status", Label)
        battery_label.update(f"Battery: {state.battery_percent}%")

        # Update power status with color coding
        power_label = self.query_one("#power-status", Label)
        if state.battery_percent > 50:
            power_label.update("Status: Normal")
            power_label.set_classes("value status-good")
        elif state.battery_percent > 20:
            power_label.update("Status: Low")
            power_label.set_classes("value status-warning")
        else:
            power_label.update("Status: Critical")
            power_label.set_classes("value status-error")

        # Update basal
        basal_rate_label = self.query_one("#basal-rate", Label)
        basal_rate_label.update(f"Current Rate: {state.current_basal_rate:.2f} U/hr")

        basal_active_label = self.query_one("#basal-active", Label)
        if state.basal_active and not state.suspended:
            basal_active_label.update("Active: Yes")
            basal_active_label.set_classes("value status-good")
        else:
            basal_active_label.update("Active: No (Suspended)" if state.suspended else "Active: No")
            basal_active_label.set_classes("value status-warning")

        # Update bolus
        bolus_active_label = self.query_one("#bolus-active", Label)
        bolus_active_label.update(f"Active: {'Yes' if state.bolus_active else 'No'}")

        bolus_amount_label = self.query_one("#bolus-amount", Label)
        bolus_amount_label.update(f"Amount: {state.bolus_amount:.2f} U")

        bolus_delivered_label = self.query_one("#bolus-delivered", Label)
        bolus_delivered_label.update(f"Delivered: {state.bolus_delivered:.2f} U")

        # Update insulin
        reservoir_label = self.query_one("#reservoir", Label)
        reservoir_label.update(f"Reservoir: {state.reservoir_volume:.1f} U")

        iob_label = self.query_one("#insulin-on-board", Label)
        iob_label.update(f"Insulin on Board: {state.insulin_on_board:.1f} U")

        # Update CGM
        cgm_glucose_label = self.query_one("#cgm-glucose", Label)
        if state.cgm_glucose is not None:
            cgm_glucose_label.update(f"Glucose: {state.cgm_glucose} mg/dL")
        else:
            cgm_glucose_label.update("Glucose: -- mg/dL")

        cgm_trend_label = self.query_one("#cgm-trend", Label)
        if state.cgm_trend is not None:
            cgm_trend_label.update(f"Trend: {state.cgm_trend}")
        else:
            cgm_trend_label.update("Trend: --")
