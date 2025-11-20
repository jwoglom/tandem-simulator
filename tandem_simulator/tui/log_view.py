"""Log view for the TUI.

This module provides a real-time message log viewer.

Milestone 5 deliverable.
"""

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Label, RichLog, Static

from tandem_simulator.utils.logger import get_logger

logger = get_logger()


class LogView(Container):
    """Log view for displaying real-time message traffic."""

    def __init__(self):
        """Initialize the log view."""
        super().__init__()
        self.log_count = 0

    def compose(self) -> ComposeResult:
        """Compose the log view layout.

        Returns:
            Layout components
        """
        with Vertical():
            yield Static("📋 Message Log", classes="section")

            # Log controls
            with Container(classes="section"):
                yield Label(f"Total Messages: {self.log_count}", id="log-count")
                yield Button("Clear Logs", id="btn-clear-logs", variant="warning")

            # Log display
            yield RichLog(id="message-log", highlight=True, markup=True, wrap=True)

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        # Add initial log message
        self.add_log("INFO", "Log view initialized")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: Button pressed event
        """
        if event.button.id == "btn-clear-logs":
            self.clear_logs()

    def add_log(self, level: str, message: str) -> None:
        """Add a log message to the view.

        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log message
        """
        log_widget = self.query_one("#message-log", RichLog)
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color code by level
        if level == "ERROR":
            color = "red"
        elif level == "WARNING":
            color = "yellow"
        elif level == "DEBUG":
            color = "cyan"
        elif level == "SUCCESS":
            color = "green"
        else:
            color = "white"

        log_widget.write(f"[{color}][{timestamp}] [{level}][/{color}] {message}")

        # Update log count
        self.log_count += 1
        count_label = self.query_one("#log-count", Label)
        count_label.update(f"Total Messages: {self.log_count}")

    def clear_logs(self) -> None:
        """Clear all log messages."""
        log_widget = self.query_one("#message-log", RichLog)
        log_widget.clear()
        self.log_count = 0

        count_label = self.query_one("#log-count", Label)
        count_label.update(f"Total Messages: {self.log_count}")

        self.add_log("INFO", "Logs cleared")
        logger.info("Logs cleared via TUI")

    def log_ble_event(self, event_type: str, details: str) -> None:
        """Log a BLE event.

        Args:
            event_type: Type of BLE event (connect, disconnect, read, write, etc.)
            details: Event details
        """
        self.add_log("DEBUG", f"[BLE] {event_type}: {details}")

    def log_message(self, direction: str, message_type: str, data: str) -> None:
        """Log a protocol message.

        Args:
            direction: Message direction (TX/RX)
            message_type: Type of message
            data: Message data (hex or description)
        """
        self.add_log("DEBUG", f"[MSG] {direction} {message_type}: {data}")

    def log_error(self, error: str) -> None:
        """Log an error.

        Args:
            error: Error message
        """
        self.add_log("ERROR", error)

    def log_warning(self, warning: str) -> None:
        """Log a warning.

        Args:
            warning: Warning message
        """
        self.add_log("WARNING", warning)

    def log_info(self, info: str) -> None:
        """Log an informational message.

        Args:
            info: Info message
        """
        self.add_log("INFO", info)

    def log_success(self, message: str) -> None:
        """Log a success message.

        Args:
            message: Success message
        """
        self.add_log("SUCCESS", message)
