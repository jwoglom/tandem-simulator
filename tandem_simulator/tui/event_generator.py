"""Event generator for the TUI.

This module provides controls for generating pump events and alerts.

Milestone 5 deliverable.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Static

from tandem_simulator.state.pump_state import PumpStateManager
from tandem_simulator.utils.logger import get_logger

logger = get_logger()


class EventGenerator(Container):
    """Event generator for simulating pump events and alerts."""

    def __init__(self, state_manager: PumpStateManager):
        """Initialize the event generator.

        Args:
            state_manager: Pump state manager
        """
        super().__init__()
        self.state_manager = state_manager

    def compose(self) -> ComposeResult:
        """Compose the event generator layout.

        Returns:
            Layout components
        """
        with Vertical():
            yield Static("⚡ Event Generator", classes="section")

            # Pump Control Events
            with Container(classes="section"):
                yield Static("🎮 Pump Control", classes="label")
                with Horizontal():
                    yield Button("Suspend Pump", id="btn-suspend", variant="warning")
                    yield Button("Resume Pump", id="btn-resume", variant="success")

            # Bolus Events
            with Container(classes="section"):
                yield Static("💊 Bolus Simulation", classes="label")
                with Horizontal():
                    yield Button("Start Bolus (1.0 U)", id="btn-bolus-1", variant="primary")
                    yield Button("Start Bolus (2.5 U)", id="btn-bolus-2", variant="primary")
                    yield Button("Start Bolus (5.0 U)", id="btn-bolus-5", variant="primary")
                with Horizontal():
                    yield Button("Stop Bolus", id="btn-stop-bolus", variant="warning")

            # Battery Events
            with Container(classes="section"):
                yield Static("🔋 Battery Simulation", classes="label")
                with Horizontal():
                    yield Button("Set Battery Low (20%)", id="btn-battery-low", variant="warning")
                    yield Button(
                        "Set Battery Critical (5%)",
                        id="btn-battery-critical",
                        variant="error",
                    )
                    yield Button(
                        "Set Battery Full (100%)", id="btn-battery-full", variant="success"
                    )

            # Reservoir Events
            with Container(classes="section"):
                yield Static("🧪 Reservoir Simulation", classes="label")
                with Horizontal():
                    yield Button(
                        "Set Reservoir Low (20 U)", id="btn-reservoir-low", variant="warning"
                    )
                    yield Button(
                        "Set Reservoir Empty (0 U)",
                        id="btn-reservoir-empty",
                        variant="error",
                    )
                    yield Button(
                        "Set Reservoir Full (300 U)",
                        id="btn-reservoir-full",
                        variant="success",
                    )

            # CGM Events
            with Container(classes="section"):
                yield Static("📈 CGM Simulation", classes="label")
                with Horizontal():
                    yield Button("High Glucose (250)", id="btn-glucose-high", variant="warning")
                    yield Button("Low Glucose (60)", id="btn-glucose-low", variant="error")
                    yield Button("Normal Glucose (120)", id="btn-glucose-normal", variant="success")

            # Alert Events
            with Container(classes="section"):
                yield Static("🚨 Alert Simulation", classes="label")
                with Horizontal():
                    yield Button(
                        "Trigger Occlusion Alert", id="btn-alert-occlusion", variant="error"
                    )
                    yield Button(
                        "Trigger Low Battery Alert",
                        id="btn-alert-low-battery",
                        variant="warning",
                    )
                    yield Button("Clear All Alerts", id="btn-clear-alerts", variant="success")

            # Status message
            yield Static("", id="event-status", classes="value")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button pressed event
        """
        button_id = event.button.id
        status_label = self.query_one("#event-status", Static)

        try:
            # Pump Control
            if button_id == "btn-suspend":
                self.state_manager.suspend_pump()
                status_label.update("⏸️ Pump suspended")
                logger.info("Pump suspended via TUI")

            elif button_id == "btn-resume":
                self.state_manager.resume_pump()
                status_label.update("▶️ Pump resumed")
                logger.info("Pump resumed via TUI")

            # Bolus Events
            elif button_id == "btn-bolus-1":
                self.state_manager.start_bolus(1.0)
                status_label.update("💊 Started 1.0 U bolus")
                logger.info("Started 1.0 U bolus via TUI")

            elif button_id == "btn-bolus-2":
                self.state_manager.start_bolus(2.5)
                status_label.update("💊 Started 2.5 U bolus")
                logger.info("Started 2.5 U bolus via TUI")

            elif button_id == "btn-bolus-5":
                self.state_manager.start_bolus(5.0)
                status_label.update("💊 Started 5.0 U bolus")
                logger.info("Started 5.0 U bolus via TUI")

            elif button_id == "btn-stop-bolus":
                self.state_manager.state.bolus_active = False
                status_label.update("🛑 Bolus stopped")
                logger.info("Bolus stopped via TUI")

            # Battery Events
            elif button_id == "btn-battery-low":
                self.state_manager.update_battery(20)
                status_label.update("🔋 Battery set to 20% (Low)")
                logger.info("Battery set to 20% via TUI")

            elif button_id == "btn-battery-critical":
                self.state_manager.update_battery(5)
                status_label.update("🔋 Battery set to 5% (Critical)")
                logger.info("Battery set to 5% via TUI")

            elif button_id == "btn-battery-full":
                self.state_manager.update_battery(100)
                status_label.update("🔋 Battery set to 100% (Full)")
                logger.info("Battery set to 100% via TUI")

            # Reservoir Events
            elif button_id == "btn-reservoir-low":
                self.state_manager.state.reservoir_volume = 20.0
                status_label.update("🧪 Reservoir set to 20 U (Low)")
                logger.info("Reservoir set to 20 U via TUI")

            elif button_id == "btn-reservoir-empty":
                self.state_manager.state.reservoir_volume = 0.0
                status_label.update("🧪 Reservoir set to 0 U (Empty)")
                logger.info("Reservoir set to 0 U via TUI")

            elif button_id == "btn-reservoir-full":
                self.state_manager.state.reservoir_volume = 300.0
                status_label.update("🧪 Reservoir set to 300 U (Full)")
                logger.info("Reservoir set to 300 U via TUI")

            # CGM Events
            elif button_id == "btn-glucose-high":
                self.state_manager.state.cgm_glucose = 250
                self.state_manager.state.cgm_trend = "↑"
                status_label.update("📈 Glucose set to 250 mg/dL (High)")
                logger.info("Glucose set to 250 mg/dL via TUI")

            elif button_id == "btn-glucose-low":
                self.state_manager.state.cgm_glucose = 60
                self.state_manager.state.cgm_trend = "↓"
                status_label.update("📈 Glucose set to 60 mg/dL (Low)")
                logger.info("Glucose set to 60 mg/dL via TUI")

            elif button_id == "btn-glucose-normal":
                self.state_manager.state.cgm_glucose = 120
                self.state_manager.state.cgm_trend = "→"
                status_label.update("📈 Glucose set to 120 mg/dL (Normal)")
                logger.info("Glucose set to 120 mg/dL via TUI")

            # Alert Events
            elif button_id == "btn-alert-occlusion":
                status_label.update("🚨 Occlusion alert triggered (simulated)")
                logger.warning("Occlusion alert triggered via TUI")

            elif button_id == "btn-alert-low-battery":
                self.state_manager.update_battery(10)
                status_label.update("🚨 Low battery alert triggered")
                logger.warning("Low battery alert triggered via TUI")

            elif button_id == "btn-clear-alerts":
                status_label.update("✅ All alerts cleared (simulated)")
                logger.info("All alerts cleared via TUI")

        except Exception as e:
            status_label.update(f"❌ Error: {e}")
            logger.error(f"Error generating event: {e}")
