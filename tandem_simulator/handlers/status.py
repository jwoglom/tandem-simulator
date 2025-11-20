"""Status request handlers for Tandem pump simulator.

This module handles status requests like battery, basal rate, bolus status, etc.

Milestone 4 deliverable.
"""

from tandem_simulator.protocol.message import Message
from tandem_simulator.protocol.messages.response.currentStatus.ApiVersionResponse import (
    ApiVersionResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.CurrentBasalStatusResponse import (
    CurrentBasalStatusResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.CurrentBatteryV1Response import (
    CurrentBatteryV1Response,
)
from tandem_simulator.protocol.messages.response.currentStatus.CurrentBolusStatusResponse import (
    CurrentBolusStatusResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.InsulinStatusResponse import (
    InsulinStatusResponse,
)
from tandem_simulator.protocol.messages.response.currentStatus.PumpVersionResponse import (
    PumpVersionResponse,
)
from tandem_simulator.state.pump_state import PumpStateManager


class StatusHandlers:
    """Handler class for status requests."""

    def __init__(self, state_manager: PumpStateManager):
        """Initialize status handlers.

        Args:
            state_manager: Pump state manager instance
        """
        self.state_manager = state_manager

    def handle_api_version_request(self, message: Message) -> Message:
        """Handle API version request.

        Args:
            message: API version request message

        Returns:
            API version response message
        """
        return ApiVersionResponse(transaction_id=message.transaction_id, major=1, minor=0)

    def handle_pump_version_request(self, message: Message) -> Message:
        """Handle pump version request.

        Args:
            message: Pump version request message

        Returns:
            Pump version response message
        """
        state = self.state_manager.get_state()

        # Convert serial number to integer if it's a string
        serial_num = int(state.serial_number) if state.serial_number.isdigit() else 0

        return PumpVersionResponse(
            transaction_id=message.transaction_id,
            arm_sw_ver=7070001,  # 7.7.1 firmware
            msp_sw_ver=7070001,
            config_a_bits=0,
            config_b_bits=0,
            serial_num=serial_num,
            part_num=0,
            pump_rev=state.firmware_version,
            pcba_sn=0,
            pcba_rev="",
            model_num=1,  # Mobi
        )

    def handle_battery_status_request(self, message: Message) -> Message:
        """Handle battery status request.

        Args:
            message: Battery status request message

        Returns:
            Battery status response message
        """
        state = self.state_manager.get_state()
        return CurrentBatteryV1Response(
            transaction_id=message.transaction_id,
            current_battery_abc=state.battery_percent,
            current_battery_ibc=state.battery_percent,
        )

    def handle_basal_status_request(self, message: Message) -> Message:
        """Handle basal status request.

        Args:
            message: Basal status request message

        Returns:
            Basal status response message
        """
        state = self.state_manager.get_state()
        # Convert basal rate to int (units/hr * 10000)
        basal_rate_int = int(state.current_basal_rate * 10000)

        return CurrentBasalStatusResponse(
            transaction_id=message.transaction_id,
            profile_basal_rate=basal_rate_int,
            current_basal_rate=basal_rate_int,
            basal_modified_bitmask=0,
        )

    def handle_bolus_status_request(self, message: Message) -> Message:
        """Handle bolus status request.

        Args:
            message: Bolus status request message

        Returns:
            Bolus status response message
        """
        state = self.state_manager.get_state()

        # Convert bolus amount to int (units * 10000)
        bolus_amount = int(state.bolus_amount * 10000)

        # Status: 0=ALREADY_DELIVERED_OR_INVALID, 1=DELIVERING, 2=REQUESTING
        status_id = (
            CurrentBolusStatusResponse.STATUS_DELIVERING
            if state.bolus_active
            else CurrentBolusStatusResponse.STATUS_ALREADY_DELIVERED_OR_INVALID
        )

        return CurrentBolusStatusResponse(
            transaction_id=message.transaction_id,
            status_id=status_id,
            bolus_id=1 if state.bolus_active else 0,
            timestamp=state.time_since_reset,
            requested_volume=bolus_amount,
            bolus_source_id=0,
            bolus_type_bitmask=0,
        )

    def handle_insulin_status_request(self, message: Message) -> Message:
        """Handle insulin status request.

        Args:
            message: Insulin status request message

        Returns:
            Insulin status response message
        """
        state = self.state_manager.get_state()

        # Convert reservoir volume to int (units * 100)
        reservoir_int = int(state.reservoir_volume * 100)

        return InsulinStatusResponse(
            transaction_id=message.transaction_id,
            current_insulin_amount=reservoir_int,
            is_estimate=0,
            insulin_low_amount=20,
        )
