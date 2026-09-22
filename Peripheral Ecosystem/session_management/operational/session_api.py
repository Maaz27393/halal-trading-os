from fastapi import FastAPI, HTTPException
from session_management.managers.session_manager import SessionManager
from session_management.health.central_health_aggregator import CentralHealthAggregator

app = FastAPI(
    title="Halal Trading OS - Session & Health Management API",
    version="1.0.0",
    description="Provider-neutral session lifecycle and health monitoring service (Read-Only / Non-Execution)."
)

session_manager = SessionManager()
health_aggregator = CentralHealthAggregator(session_manager)

@app.get("/health", summary="Central Health & Session Status")
def get_central_health():
    """
    Returns consolidated health and session lifecycle states for all peripheral providers
    (NSE, Screener, Chartink, TradingView, Kite) using a fail-closed evaluation model.
    """
    try:
        report = health_aggregator.refresh_all_health()
        return {
            "status": "success",
            "live_auto_execution": False,
            "data": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{provider_id}", summary="Get Specific Provider Session")
def get_provider_session(provider_id: str):
    """Retrieves session metadata for a specific provider."""
    session = session_manager.get_session(provider_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found or uninitialized.")
    return session.model_dump(mode="json")
