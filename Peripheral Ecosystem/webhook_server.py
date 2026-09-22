import os
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field
from datetime import datetime
import pandas as pd

# Import existing adapters and lifecycle manager
from opportunity_manager import get_or_create_opportunity_id
from adapter_chartink import ingest_chartink_signal
from adapter_tradingview import ingest_tradingview_technical
from adapter_governance import ingest_governance_audit

app = FastAPI(
    title="Trading OS Local Observability Ingestion Engine",
    version="1.0.0",
    docs_url=None,       # Disable Swagger docs in production for security
    redoc_url=None
)

# Strict Governance Guardrails
GOVERNANCE_CONFIG = {
    "READ_ONLY": True,
    "LIVE_AUTO_EXECUTION": False,
    "ORDER_CAPABILITY": "NONE",
    "EXECUTION_AUTHORITY": "NONE"
}

# Pydantic Schemas for Payload Validation
class ChartinkWebhookPayload(BaseModel):
    symbol: str = Field(..., description="Stock trading symbol e.g. RELIANCE")
    scanner_name: str = Field(..., description="Name of the Chartink scanner")
    signal_type: str = Field(..., description="Type of signal e.g. BREAKOUT")
    scanner_value: str = Field(default="1", description="Trigger value")

class TradingViewWebhookPayload(BaseModel):
    symbol: str = Field(..., description="Stock trading symbol")
    timeframe: str = Field(default="1D", description="Chart timeframe")
    indicator_state: str = Field(default="BULLISH_ALIGNMENT", description="Technical condition")
    confirmation: str = Field(default="CONFIRMED", description="Confirmation status")
    close_price: float = Field(default=0.0, description="Bar close price")

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """System health and boundary verification endpoint."""
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "guardrails": GOVERNANCE_CONFIG
    }

@app.get("/status", status_code=status.HTTP_200_OK)
def system_status():
    """Returns operational parameters and data directory status."""
    cache_dir = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"
    files_status = {}
    if os.path.exists(cache_dir):
        for f in os.listdir(cache_dir):
            if f.endswith(".csv"):
                f_path = os.path.join(cache_dir, f)
                files_status[f] = os.path.getsize(f_path)
                
    return {
        "service": "Trading OS Ingestion Server",
        "mode": "OBSERVATION_ONLY",
        "bound_interface": "127.0.0.1 (Local Loopback Only)",
        "tracked_feeders": files_status
    }

@app.post("/webhooks/chartink", status_code=status.HTTP_201_CREATED)
def receive_chartink_webhook(payload: ChartinkWebhookPayload):
    """Ingests Chartink screener alerts and routes them to canonical feeders."""
    try:
        opp_id = ingest_chartink_signal(
            symbol=payload.symbol.upper(),
            scanner_name=payload.scanner_name,
            signal_type=payload.signal_type,
            scanner_value=payload.scanner_value
        )
        
        # Automatically record a governance audit trail entry for observability
        ingest_governance_audit(
            symbol=payload.symbol.upper(),
            decision="RECEIVED",
            result="PASS",
            reason=f"Chartink webhook processed for {payload.scanner_name}"
        )
        
        return {
            "status": "SUCCESS",
            "opportunity_id": opp_id,
            "provider": "Chartink",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhooks/tradingview", status_code=status.HTTP_201_CREATED)
def receive_tradingview_webhook(payload: TradingViewWebhookPayload):
    """Ingests TradingView technical indicator triggers."""
    try:
        opp_id = ingest_tradingview_technical(
            symbol=payload.symbol.upper(),
            timeframe=payload.timeframe,
            indicator_state=payload.indicator_state,
            confirmation=payload.confirmation,
            close_price=payload.close_price
        )
        return {
            "status": "SUCCESS",
            "opportunity_id": opp_id,
            "provider": "TradingView",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # STRICT SECURITY: Bound explicitly to loopback 127.0.0.1
    uvicorn.run("webhook_server:app", host="127.0.0.1", port=8000, reload=True)