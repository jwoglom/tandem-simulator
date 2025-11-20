"""Configuration panel for the TUI.

This module provides the configuration interface for modifying pump parameters.

Milestone 5 deliverable.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Input, Label, Static

from tandem_simulator.state.pump_state import PumpStateManager
from tandem_simulator.utils.logger import get_logger

logger = get_logger()


class ConfigPanel(Container):
    """Configuration panel for modifying pump settings."""

    def __init__(self, state_manager: PumpStateManager):
        """Initialize the configuration panel.

        Args:
            state_manager: Pump state manager
        """
        super().__init__()
        self.state_manager = state_manager

    def compose(self) -> ComposeResult:
        """Compose the configuration panel layout.

        Returns:
            Layout components
        """
        with Vertical():
            yield Static("⚙️ Pump Configuration", classes="section")

            # Battery Configuration
            with Container(classes="section"):
                yield Static("🔋 Battery Configuration", classes="label")
                with Horizontal():
                    yield Label("Battery Percent (0-100):")
                    yield Input(
                        value=str(self.state_manager.state.battery_percent),
                        placeholder="0-100",
                        id="input-battery",
                    )
                    yield Button("Update Battery", id="btn-update-battery", variant="primary")

            # Basal Configuration
            with Container(classes="section"):
                yield Static("💉 Basal Configuration", classes="label")
                with Horizontal():
                    yield Label("Basal Rate (U/hr):")
                    yield Input(
                        value=str(self.state_manager.state.current_basal_rate),
                        placeholder="0.00",
                        id="input-basal-rate",
                    )
                    yield Button("Update Basal Rate", id="btn-update-basal", variant="primary")

            # Insulin Configuration
            with Container(classes="section"):
                yield Static("🧪 Insulin Configuration", classes="label")
                with Horizontal():
                    yield Label("Reservoir Volume (U):")
                    yield Input(
                        value=str(self.state_manager.state.reservoir_volume),
                        placeholder="0.0",
                        id="input-reservoir",
                    )
                    yield Button("Update Reservoir", id="btn-update-reservoir", variant="primary")

                with Horizontal():
                    yield Label("Insulin on Board (U):")
                    yield Input(
                        value=str(self.state_manager.state.insulin_on_board),
                        placeholder="0.0",
                        id="input-iob",
                    )
                    yield Button("Update IOB", id="btn-update-iob", variant="primary")

            # CGM Configuration
            with Container(classes="section"):
                yield Static("📈 CGM Configuration", classes="label")
                with Horizontal():
                    yield Label("Glucose (mg/dL):")
                    yield Input(
                        value=str(self.state_manager.state.cgm_glucose or ""),
                        placeholder="70-400",
                        id="input-cgm-glucose",
                    )
                    yield Button("Update Glucose", id="btn-update-glucose", variant="primary")

                with Horizontal():
                    yield Label("Trend Arrow:")
                    yield Input(
                        value=str(self.state_manager.state.cgm_trend or ""),
                        placeholder="↑ ↗ → ↘ ↓",
                        id="input-cgm-trend",
                    )
                    yield Button("Update Trend", id="btn-update-trend", variant="primary")

            # Device Info
            with Container(classes="section"):
                yield Static("ℹ️ Device Information", classes="label")
                with Horizontal():
                    yield Label("Serial Number:")
                    yield Input(
                        value=self.state_manager.state.serial_number,
                        placeholder="00000000",
                        id="input-serial",
                        disabled=True,
                    )

                with Horizontal():
                    yield Label("Firmware Version:")
                    yield Input(
                        value=self.state_manager.state.firmware_version,
                        placeholder="7.7.1",
                        id="input-firmware",
                    )
                    yield Button("Update Firmware", id="btn-update-firmware", variant="primary")

            # Status message
            yield Static("", id="config-status", classes="value")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button pressed event
        """
        button_id = event.button.id
        status_label = self.query_one("#config-status", Static)

        try:
            if button_id == "btn-update-battery":
                value = int(self.query_one("#input-battery", Input).value)
                if 0 <= value <= 100:
                    self.state_manager.update_battery(value)
                    status_label.update(f"✅ Battery updated to {value}%")
                    logger.info(f"Battery updated to {value}%")
                else:
                    status_label.update("❌ Battery must be between 0 and 100")

            elif button_id == "btn-update-basal":
                value = float(self.query_one("#input-basal-rate", Input).value)
                if value >= 0:
                    self.state_manager.update_basal_rate(value)
                    status_label.update(f"✅ Basal rate updated to {value:.2f} U/hr")
                    logger.info(f"Basal rate updated to {value:.2f} U/hr")
                else:
                    status_label.update("❌ Basal rate must be >= 0")

            elif button_id == "btn-update-reservoir":
                value = float(self.query_one("#input-reservoir", Input).value)
                if value >= 0:
                    self.state_manager.state.reservoir_volume = value
                    status_label.update(f"✅ Reservoir updated to {value:.1f} U")
                    logger.info(f"Reservoir updated to {value:.1f} U")
                else:
                    status_label.update("❌ Reservoir volume must be >= 0")

            elif button_id == "btn-update-iob":
                value = float(self.query_one("#input-iob", Input).value)
                if value >= 0:
                    self.state_manager.state.insulin_on_board = value
                    status_label.update(f"✅ IOB updated to {value:.1f} U")
                    logger.info(f"IOB updated to {value:.1f} U")
                else:
                    status_label.update("❌ IOB must be >= 0")

            elif button_id == "btn-update-glucose":
                value_str = self.query_one("#input-cgm-glucose", Input).value
                if value_str:
                    value = int(value_str)
                    if 20 <= value <= 600:
                        self.state_manager.state.cgm_glucose = value
                        status_label.update(f"✅ Glucose updated to {value} mg/dL")
                        logger.info(f"Glucose updated to {value} mg/dL")
                    else:
                        status_label.update("❌ Glucose must be between 20 and 600")
                else:
                    self.state_manager.state.cgm_glucose = None
                    status_label.update("✅ Glucose cleared")
                    logger.info("Glucose cleared")

            elif button_id == "btn-update-trend":
                value = self.query_one("#input-cgm-trend", Input).value
                if value:
                    self.state_manager.state.cgm_trend = value
                    status_label.update(f"✅ Trend updated to {value}")
                    logger.info(f"Trend updated to {value}")
                else:
                    self.state_manager.state.cgm_trend = None
                    status_label.update("✅ Trend cleared")
                    logger.info("Trend cleared")

            elif button_id == "btn-update-firmware":
                value = self.query_one("#input-firmware", Input).value
                if value:
                    self.state_manager.state.firmware_version = value
                    status_label.update(f"✅ Firmware version updated to {value}")
                    logger.info(f"Firmware version updated to {value}")
                else:
                    status_label.update("❌ Firmware version cannot be empty")

        except ValueError:
            status_label.update("❌ Invalid input value")
            logger.error("Invalid input value in configuration panel")
        except Exception as e:
            status_label.update(f"❌ Error: {e}")
            logger.error(f"Error updating configuration: {e}")
