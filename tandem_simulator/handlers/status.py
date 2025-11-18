"""Status request handlers for Tandem pump simulator.

This module handles status requests like battery, basal rate, bolus status, etc.

Milestone 4 deliverable (stub).
"""

from tandem_simulator.protocol.message import Message


def handle_battery_status_request(message: Message) -> Message:
    """Handle battery status request.

    Args:
        message: Battery status request message

    Returns:
        Battery status response message
    """
    # TODO: Implement battery status response
    raise NotImplementedError("Battery status not yet implemented")


def handle_basal_status_request(message: Message) -> Message:
    """Handle basal status request.

    Args:
        message: Basal status request message

    Returns:
        Basal status response message
    """
    # TODO: Implement basal status response
    raise NotImplementedError("Basal status not yet implemented")


def handle_bolus_status_request(message: Message) -> Message:
    """Handle bolus status request.

    Args:
        message: Bolus status request message

    Returns:
        Bolus status response message
    """
    # TODO: Implement bolus status response
    raise NotImplementedError("Bolus status not yet implemented")
