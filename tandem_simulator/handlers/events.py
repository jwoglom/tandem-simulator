"""Qualifying events handlers for Tandem pump simulator.

This module handles qualifying events (alerts, alarms, notifications) that
are sent from the pump to connected apps.

Milestone 4 deliverable.
"""

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Optional

from tandem_simulator.protocol.message import Message
from tandem_simulator.state.pump_state import PumpStateManager

logger = logging.getLogger(__name__)


class EventType(IntEnum):
    """Types of pump events."""

    ALERT = 1
    ALARM = 2
    NOTIFICATION = 3
    STATUS_CHANGE = 4


@dataclass
class PumpEvent:
    """Represents a pump event/alert/alarm."""

    event_type: EventType
    event_id: int
    severity: int  # 0=info, 1=warning, 2=critical
    message: str
    timestamp: int  # Seconds since pump reset
    acknowledged: bool = False


class EventHandlers:
    """Handler class for qualifying events (alerts, alarms, notifications)."""

    def __init__(self, state_manager: PumpStateManager):
        """Initialize event handlers.

        Args:
            state_manager: Pump state manager instance
        """
        self.state_manager = state_manager
        self.pending_events: List[PumpEvent] = []
        self.event_id_counter = 0

    def generate_low_battery_alert(self) -> PumpEvent:
        """Generate a low battery alert event.

        Returns:
            Low battery alert event
        """
        state = self.state_manager.get_state()
        event = PumpEvent(
            event_type=EventType.ALERT,
            event_id=self._next_event_id(),
            severity=1,  # Warning
            message=f"Low battery: {state.battery_percent}%",
            timestamp=state.time_since_reset,
        )
        self.pending_events.append(event)
        logger.info(f"Generated low battery alert: {event.message}")
        return event

    def generate_low_insulin_alert(self) -> PumpEvent:
        """Generate a low insulin/reservoir alert event.

        Returns:
            Low insulin alert event
        """
        state = self.state_manager.get_state()
        event = PumpEvent(
            event_type=EventType.ALERT,
            event_id=self._next_event_id(),
            severity=1,  # Warning
            message=f"Low insulin: {state.reservoir_volume}U remaining",
            timestamp=state.time_since_reset,
        )
        self.pending_events.append(event)
        logger.info(f"Generated low insulin alert: {event.message}")
        return event

    def generate_bolus_complete_notification(self, amount: float) -> PumpEvent:
        """Generate a bolus complete notification.

        Args:
            amount: Bolus amount delivered in units

        Returns:
            Bolus complete notification event
        """
        state = self.state_manager.get_state()
        event = PumpEvent(
            event_type=EventType.NOTIFICATION,
            event_id=self._next_event_id(),
            severity=0,  # Info
            message=f"Bolus complete: {amount}U delivered",
            timestamp=state.time_since_reset,
        )
        self.pending_events.append(event)
        logger.info(f"Generated bolus complete notification: {event.message}")
        return event

    def generate_occlusion_alarm(self) -> PumpEvent:
        """Generate an occlusion alarm (critical).

        Returns:
            Occlusion alarm event
        """
        state = self.state_manager.get_state()
        event = PumpEvent(
            event_type=EventType.ALARM,
            event_id=self._next_event_id(),
            severity=2,  # Critical
            message="Occlusion detected - delivery stopped",
            timestamp=state.time_since_reset,
        )
        self.pending_events.append(event)
        logger.warning(f"Generated occlusion alarm: {event.message}")
        return event

    def handle_event_acknowledgment(self, message: Message) -> Message:
        """Handle event acknowledgment from app.

        Args:
            message: Event acknowledgment message

        Returns:
            Acknowledgment response message
        """
        logger.debug(f"Event acknowledgment received: transaction_id={message.transaction_id}")

        # Stub implementation: mark all pending events as acknowledged
        for event in self.pending_events:
            event.acknowledged = True

        # In a real implementation, we would:
        # 1. Parse the event ID from the acknowledgment message
        # 2. Mark specific event as acknowledged
        # 3. Remove acknowledged events from pending list
        # 4. Return proper acknowledgment response

        return message

    def get_pending_events(self, acknowledged: bool = False) -> List[PumpEvent]:
        """Get list of pending events.

        Args:
            acknowledged: If True, include acknowledged events

        Returns:
            List of pending events
        """
        if acknowledged:
            return self.pending_events
        else:
            return [e for e in self.pending_events if not e.acknowledged]

    def clear_acknowledged_events(self):
        """Remove all acknowledged events from the pending list."""
        self.pending_events = [e for e in self.pending_events if not e.acknowledged]
        logger.debug(f"Cleared acknowledged events. {len(self.pending_events)} events remaining")

    def check_and_generate_alerts(self):
        """Check pump state and generate alerts if needed.

        This method should be called periodically to check for conditions
        that warrant alerts or alarms.
        """
        state = self.state_manager.get_state()

        # Check for low battery
        if state.battery_percent < 20 and not self._has_pending_event_type(EventType.ALERT):
            self.generate_low_battery_alert()

        # Check for low insulin
        if state.reservoir_volume < 30.0 and not self._has_pending_event_type(EventType.ALERT):
            self.generate_low_insulin_alert()

    def _has_pending_event_type(self, event_type: EventType) -> bool:
        """Check if there's already a pending event of this type.

        Args:
            event_type: Type of event to check

        Returns:
            True if there's a pending event of this type
        """
        return any(e.event_type == event_type and not e.acknowledged for e in self.pending_events)

    def _next_event_id(self) -> int:
        """Get next event ID.

        Returns:
            Next event ID
        """
        self.event_id_counter += 1
        return self.event_id_counter
