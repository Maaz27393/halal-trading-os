import logging
from typing import Optional

logger = logging.getLogger("EmergencyKillSwitch")

class KillSwitchTriggeredError(PermissionError):
    """Raised when an order attempt occurs while the emergency kill-switch is active."""
    pass

class EmergencyKillSwitch:
    """
    Emergency circuit breaker designed to immediately halt all execution pipelines,
    freeze order dispatches, and isolate the trading ecosystem.
    """

    def __init__(self):
        self._tripped = False
        self._trip_reason: Optional[str] = None
        logger.info("EmergencyKillSwitch initialized in ARMED (standby) state.")

    def trip(self, reason: str) -> None:
        """Manually or automatically trip the kill-switch."""
        self._tripped = True
        self._trip_reason = reason
        logger.critical(f"EMERGENCY KILL-SWITCH TRIPPED! Reason: {reason}")

    def reset(self, authorization_token: str) -> None:
        """Reset the kill-switch (requires administrative authorization)."""
        if authorization_token != "ADMIN_OVERRIDE_RESET_2026":
            raise PermissionError("Kill-switch reset denied: Invalid administrative token.")
        self._tripped = False
        self._trip_reason = None
        logger.warning("Emergency kill-switch has been reset by administrator.")

    @property
    def is_tripped(self) -> bool:
        return self._tripped

    @property
    def trip_reason(self) -> Optional[str]:
        return self._trip_reason

    def check_state(self) -> None:
        """Raises KillSwitchTriggeredError if the kill-switch is currently active."""
        if self._tripped:
            raise KillSwitchTriggeredError(
                f"Execution Blocked by Emergency Kill-Switch. Trip Reason: {self._trip_reason}"
            )