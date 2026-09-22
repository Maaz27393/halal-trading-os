import os
import pandas as pd

OUTPUT_DIR = (
    r"D:\OBSIDIAN VAULT\halal-trading-os"
    r"\Peripheral Ecosystem\data_cache\powerbi"
)

SCHEMAS = {
    "powerbi_screening.csv": [
        "ScreeningRecordID", "ScreeningCycleID", "Symbol", "ScreeningTimestamp",
        "FundamentalStatus", "MarketCap", "ROE", "DebtEquity", "CurrentRatio",
        "QuickRatio", "OtherIncomePct", "ShariahStatus", "ShariahProvider",
        "EligibilityStatus", "ValidFrom", "ValidTo", "Source"
    ],
    "powerbi_scanner_events.csv": [
        "ScannerEventID", "OpportunityID", "Symbol", "ScanTimestamp",
        "Provider", "ScannerName", "SignalType", "ScannerStatus",
        "ScannerValue", "SourceEventID"
    ],
    "powerbi_technical_events.csv": [
        "TechnicalEventID", "OpportunityID", "Symbol", "Timestamp",
        "Provider", "Timeframe", "IndicatorState", "EMA20", "EMA50",
        "VWAP", "RSI50", "RSI10", "AVPUsed", "FRVPUsed", "PivotContext",
        "Confirmation", "SourceEventID"
    ],
    "powerbi_market_context.csv": [
        "MarketSnapshotID", "OpportunityID", "Timestamp", "NiftyTrend",
        "IndiaVIX", "Advances", "Declines", "MarketRegime", "Source"
    ],
    "powerbi_audits.csv": [
        "AuditID", "OpportunityID", "Timestamp", "Component", "AuditType",
        "Rule", "Decision", "Result", "Severity", "Reason", "InputSource",
        "Model", "ReadOnly", "LiveAutoExecution", "OrderCapability",
        "ExecutionAuthority"
    ],
    "powerbi_execution_events.csv": [
        "ExecutionEventID", "OpportunityID", "TradeID", "Timestamp",
        "ExecutionSource", "ExecutionType", "Status", "FillPrice",
        "Quantity", "CapitalUsed", "StopLoss", "Target", "Notes"
    ],
    "powerbi_opportunity_trade_bridge.csv": [
        "BridgeID", "OpportunityID", "TradeID", "LinkType",
        "FinalStage", "RejectionReason", "LinkTimestamp"
    ]
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename, expected_cols in SCHEMAS.items():
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        df = pd.DataFrame(columns=expected_cols)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"Created new contract with headers: {filename}")
    else:
        df = pd.read_csv(file_path, nrows=0)
        actual_cols = list(df.columns)
        if actual_cols == expected_cols:
            print(f"Existing contract verified (headers match): {filename}")
        else:
            print(f"WARNING: Header mismatch in {filename}!")
            print(f"  Expected: {expected_cols}")
            print(f"  Found:    {actual_cols}")

print("\nStep 8E Feeder Initialization & Header Verification Complete.")