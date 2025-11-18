"""Control request handlers for Tandem pump simulator.

This module handles control requests like bolus initiation, suspend/resume, etc.

Milestone 4 deliverable (stub).
"""

from tandem_simulator.protocol.message import Message


def handle_bolus_request(message: Message) -> Message:
    """Handle bolus initiation request.

    Args:
        message: Bolus request message

    Returns:
        Bolus response message
    """
    # TODO: Implement bolus request handling
    raise NotImplementedError("Bolus control not yet implemented")


def handle_suspend_request(message: Message) -> Message:
    """Handle pump suspend request.

    Args:
        message: Suspend request message

    Returns:
        Suspend response message
    """
    # TODO: Implement suspend request handling
    raise NotImplementedError("Suspend control not yet implemented")
