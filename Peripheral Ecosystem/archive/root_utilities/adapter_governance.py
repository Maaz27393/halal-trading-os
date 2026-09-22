import os
import pandas as pd
from datetime import datetime
from opportunity_manager import get_or_create_opportunity_id

OUTPUT_DIR = r"D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi"

def ingest_governance_audit(
    symbol: str, 
    decision: str = "APPROVED", 
    result: str = "PASS", 
    reason: str = "Risk limits and Shariah criteria verified"
):
    """
    Ingests governance and risk audit results, binds them to the canonical 
    OpportunityID, and appends telemetry to powerbi_audits.csv while enforcing 
    read-only observational guardrails.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get or reuse canonical OpportunityID via Lifecycle Manager
    opportunity_id = get_or_create_opportunity_id(symbol)
    
    audit_path = os.path.join(OUTPUT_DIR, "powerbi_audits.csv")
    audit_df = pd.read_csv(audit_path) if os.path.exists(audit_path) else pd.DataFrame()
    
    audit_id = f"AUD-{opportunity_id}"
    
    # Prevent duplicate audit logs for the same opportunity thread
    if not audit_df.empty and "AuditID" in audit_df.columns:
        if audit_id in audit_df["AuditID"].values:
            print(f"[Governance Adapter] Audit {audit_id} already logged. Skipping duplicate.")
            return opportunity_id

    new_audit = pd.DataFrame([{
        "AuditID": audit_id,
        "OpportunityID": opportunity_id,
        "Timestamp": timestamp,
        "Component": "RiskEngine",
        "AuditType": "GOVERNANCE_CHECK",
        "Rule": "MAX_RISK_2_PERCENT",
        "Decision": decision,
        "Result": result,
        "Severity": "LOW",
        "Reason": reason,
        "InputSource": "LocalOS",
        "Model": "Qwen-Advisory",
        "ReadOnly": "True",
        "LiveAutoExecution": "False",
        "OrderCapability": "None",
        "ExecutionAuthority": "None"
    }])
    
    audit_df = pd.concat([audit_df, new_audit], ignore_index=True)
    audit_df.to_csv(audit_path, index=False, encoding="utf-8-sig")
    
    print(f"[Governance Adapter] Successfully recorded audit telemetry for {symbol} under {opportunity_id}")
    return opportunity_id

if __name__ == "__main__":
    # Test ingestion for RELIANCE
    ingest_governance_audit("RELIANCE", "APPROVED", "PASS", "Within capital and risk parameters")