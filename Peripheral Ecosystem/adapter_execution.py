import os
import pandas as pd
from datetime import datetime
from opportunity_manager import get_or_create_opportunity_id

OUTPUT_DIR = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"

def ingest_execution_event(
    symbol: str, 
    execution_status: str = "EXECUTED", 
    trade_id: str = "TRD-20260921-001",
    final_stage: str = "Execution",
    rejection_reason: str = "None"
):
    """
    Ingests manual/execution telemetry, binds them to the canonical OpportunityID,
    appends execution events, and populates the opportunity-to-trade bridge contract.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get or reuse canonical OpportunityID via Lifecycle Manager
    opportunity_id = get_or_create_opportunity_id(symbol)
    
    exec_path = os.path.join(OUTPUT_DIR, "powerbi_execution_events.csv")
    exec_df = pd.read_csv(exec_path) if os.path.exists(exec_path) else pd.DataFrame()
    
    execution_event_id = f"EXE-{opportunity_id}"
    
    # Prevent duplicate execution logs for the same opportunity thread
    if not exec_df.empty and "ExecutionEventID" in exec_df.columns:
        if execution_event_id in exec_df["ExecutionEventID"].values:
            print(f"[Execution Adapter] Execution event {execution_event_id} already logged. Skipping duplicate.")
            return opportunity_id

    new_exec = pd.DataFrame([{
        "ExecutionEventID": execution_event_id,
        "OpportunityID": opportunity_id,
        "Symbol": symbol,
        "Timestamp": timestamp,
        "ExecutionProvider": "KiteManual",
        "ExecutionStatus": execution_status,
        "FilledPrice": 2545.0,
        "FilledQuantity": 100,
        "Slippage": 2.0,
        "SourceExecutionID": f"ORD-{opportunity_id}"
    }])
    exec_df = pd.concat([exec_df, new_exec], ignore_index=True)
    exec_df.to_csv(exec_path, index=False, encoding="utf-8-sig")

    # Update Opportunity-Trade Bridge contract
    bridge_path = os.path.join(OUTPUT_DIR, "powerbi_opportunity_trade_bridge.csv")
    bridge_df = pd.read_csv(bridge_path) if os.path.exists(bridge_path) else pd.DataFrame()
    
    new_bridge = pd.DataFrame([{
        "OpportunityID": opportunity_id,
        "TradeID": trade_id if execution_status == "EXECUTED" else "",
        "ExecutionStatus": execution_status,
        "FinalStage": final_stage,
        "RejectionReason": rejection_reason
    }])
    
    # If bridge already has this OpportunityID, update or append
    if not bridge_df.empty and "OpportunityID" in bridge_df.columns:
        bridge_df = bridge_df[bridge_df["OpportunityID"] != opportunity_id]
        
    bridge_df = pd.concat([bridge_df, new_bridge], ignore_index=True)
    bridge_df.to_csv(bridge_path, index=False, encoding="utf-8-sig")
    
    print(f"[Execution Adapter] Successfully recorded execution telemetry and bridge link for {symbol} under {opportunity_id}")
    return opportunity_id

if __name__ == "__main__":
    # Test ingestion for RELIANCE
    ingest_execution_event("RELIANCE", "EXECUTED", "TRD-20260921-001", "Execution", "None")