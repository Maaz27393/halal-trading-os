import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from session_management.contracts.session_contract import SessionState, SessionMetadata

logger = logging.getLogger("SessionManager")

class SessionManager:
    """
    Independent session and auth lifecycle manager implementing a fail-closed 
    state transition model for peripheral providers.
    """
    def __init__(self):
        self._sessions: Dict[str, SessionMetadata] = {}
        logger.info("SessionManager initialized in read-only / monitor mode.")

    def register_provider(self, provider_id: str, initial_state: SessionState = SessionState.UNAVAILABLE) -> SessionMetadata:
        """Register or reset a provider session state."""
        metadata = SessionMetadata(
            provider_id=provider_id,
            session_state=initial_state,
            authenticated=(initial_state == SessionState.VALID),
            last_validated_at=datetime.now(timezone.utc)
        )
        self._sessions[provider_id] = metadata
        logger.info(f"Registered provider '{provider_id}' with initial state: {initial_state}")
        return metadata

    def get_session(self, provider_id: str) -> Optional[SessionMetadata]:
        """Retrieve current session metadata for a provider."""
        return self._sessions.get(provider_id)

    def update_session_status(self, provider_id: str, success: bool, failure_reason: Optional[str] = None, raw_health: Optional[Dict[str, Any]] = None) -> SessionMetadata:
        """
        Applies state transition based on success/failure outcome using a fail-closed model:
        VALID -> EXPIRING -> REVALIDATE -> DEGRADED -> EXPIRED -> REAUTH_REQUIRED
        """
        if provider_id not in self._sessions:
            self.register_provider(provider_id)

        session = self._sessions[provider_id]
        now = datetime.now(timezone.utc)
        session.last_validated_at = now

        if raw_health:
            session.metadata.update(raw_health)

        if success:
            session.last_success = now
            session.session_state = SessionState.VALID
            session.authenticated = True
            session.reauth_required = False
            session.failure_reason = None
            logger.info(f"Session state for '{provider_id}' verified as VALID.")
        else:
            session.last_failure = now
            session.failure_reason = failure_reason or "Unknown operational or auth failure"
            
            # Fail-closed state progression
            if session.session_state == SessionState.VALID:
                session.session_state = SessionState.DEGRADED
                logger.warning(f"Provider '{provider_id}' transition: VALID -> DEGRADED due to failure: {session.failure_reason}")
            elif session.session_state == SessionState.DEGRADED:
                session.session_state = SessionState.EXPIRED
                logger.warning(f"Provider '{provider_id}' transition: DEGRADED -> EXPIRED")
            else:
                session.session_state = SessionState.REAUTH_REQUIRED
                session.authenticated = False
                session.reauth_required = True
                logger.error(f"Provider '{provider_id}' transition -> REAUTH_REQUIRED. Manual intervention needed.")

        return session

    def get_all_sessions(self) -> Dict[str, SessionMetadata]:
        """Retrieve all active session records."""
        return self._sessions
