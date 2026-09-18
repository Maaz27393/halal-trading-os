import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any

PERIPHERAL_ROOT = "D:\\OBSIDIAN VAULT\\halal-trading-os\\Peripheral Ecosystem"
if PERIPHERAL_ROOT not in sys.path:
    sys.path.insert(0, PERIPHERAL_ROOT)

from security.gateway import PermissionGateway
from connectors.broker_base import LIVE_AUTO_EXECUTION
from provider_connectors.step1_fundamental_halal import FundamentalHalalIngestionConnector
from provider_connectors.step2_chartink_scanner import ChartinkScannerConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("OperationalDailyRunner")

class OperationalDailyRunner:
    """
    Operational Layer v1.1 (Provenance-Aware):
    Executes morning pipeline and stamps explicit data status (LIVE / FALLBACK)
    into the Obsidian Pre-Market Briefing.
    """

    def __init__(self):
        if LIVE_AUTO_EXECUTION:
            raise RuntimeError("CRITICAL SECURITY VIOLATION: LIVE_AUTO_EXECUTION is enabled!")
        
        self.perm_gateway = PermissionGateway()
        self.perm_gateway.grant_permission("analyst_agent", "READ")
        self.perm_gateway.grant_permission("analyst_agent", "WRITE")
        
        self.vault_briefing_dir = "D:\\OBSIDIAN VAULT\\Daily_Briefings"
        self.audit_log_path = os.path.join(PERIPHERAL_ROOT, "Canonical Universe", "run_audit_log.json")
        os.makedirs(self.vault_briefing_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)

    def run_morning_pipeline(self) -> Dict[str, Any]:
        start_time = datetime.now()
        timestamp_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        date_str = start_time.strftime("%Y-%m-%d")
        
        audit_record = {
            "date": date_str,
            "start_time": timestamp_str,
            "status": "STARTED",
            "screener_provenance": "FALLBACK",
            "chartink_provenance": "FALLBACK",
            "halal_universe_count": 0,
            "technical_candidates_count": 0,
            "error": None
        }

        try:
            logger.info("=== STEP 1: Ingesting Fundamentals & Halal Filtering ===")
            step1_conn = FundamentalHalalIngestionConnector(self.perm_gateway, "analyst_agent")
            step1_conn.connect()

            raw_screener = [
                {"symbol": "RELIANCE", "company_name": "Reliance Industries", "sector": "Energy", "market_cap_cr": 1800000, "roe": 15.5, "debt_to_equity": 0.35},
                {"symbol": "TCS", "company_name": "Tata Consultancy Services", "sector": "IT", "market_cap_cr": 1400000, "roe": 45.2, "debt_to_equity": 0.02},
                {"symbol": "INFY", "company_name": "Infosys Ltd", "sector": "IT", "market_cap_cr": 650000, "roe": 30.1, "debt_to_equity": 0.10}
            ]
            musaffa_halal = ["RELIANCE", "TCS", "INFY"]

            halal_universe = step1_conn.ingest_screener_and_filter_halal(raw_screener, musaffa_halal)
            step1_conn.disconnect()
            
            audit_record["screener_provenance"] = "FALLBACK" # Default until live scraper is wired
            audit_record["halal_universe_count"] = len(halal_universe)
            halal_symbols = [s.symbol for s in halal_universe]

            logger.info("=== STEP 2: Running Chartink Technical Scans ===")
            step2_conn = ChartinkScannerConnector(self.perm_gateway, "analyst_agent")
            step2_conn.connect()
            
            scan_clause = "( {cash} ( latest close > latest ema ( latest close , 20 ) and latest volume > 100000 ) )"
            raw_candidates, chartink_prov = step2_conn.run_technical_scan_with_provenance(halal_symbols, scan_clause)
            step2_conn.disconnect()

            audit_record["chartink_provenance"] = chartink_prov

            logger.info("=== STEP 3: Candidate Scoring & Ranking ===")
            scored_candidates = []
            for c in raw_candidates:
                score = (c.per_change * 2.0) + (min(c.volume / 100000.0, 50.0) * 0.5)
                scored_candidates.append({
                    "symbol": c.symbol,
                    "company_name": c.company_name,
                    "close_price": c.close_price,
                    "volume": c.volume,
                    "per_change": c.per_change,
                    "score": round(score, 2)
                })

            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            audit_record["technical_candidates_count"] = len(scored_candidates)

            logger.info("=== STEP 4 & 5: Generating Pre-Market Briefing & Obsidian Export ===")
            briefing_content = self._generate_markdown_briefing(date_str, audit_record, halal_universe, scored_candidates)
            obsidian_file_path = os.path.join(self.vault_briefing_dir, f"Briefing_{date_str}.md")
            
            with open(obsidian_file_path, "w", encoding="utf-8") as f:
                f.write(briefing_content)

            audit_record["status"] = "SUCCESS"
            logger.info(f"Pre-market briefing with provenance successfully exported: {obsidian_file_path}")

        except Exception as e:
            audit_record["status"] = "FAILED"
            audit_record["error"] = str(e)
            logger.error(f"Pipeline execution failed: {e}")

        self._append_audit_log(audit_record)
        return audit_record

    def _generate_markdown_briefing(self, date_str: str, audit_record: dict, halal_universe: list, scored_candidates: list) -> str:
        scr_prov = audit_record["screener_provenance"]
        chk_prov = audit_record["chartink_provenance"]
        
        is_fully_live = (scr_prov == "LIVE" and chk_prov == "LIVE")
        banner_callout = "[!NOTE]" if is_fully_live else "[!WARNING]"
        banner_title = "DATA STATUS: LIVE MARKET DATA VERIFIED" if is_fully_live else "DATA STATUS: FALLBACK / SIMULATED DATA ACTIVE"

        md = f"""# Pre-Market Trading Briefing — {date_str}

> {banner_callout}
> **{banner_title}**
> * **Screener.in / Musaffa:** `{scr_prov}`
> * **Chartink Scanner:** `{chk_prov}`
> * *Execution Boundary:* `LIVE_AUTO_EXECUTION = FALSE` (Manual Gate Enforced)

---

## 📊 System Overview
* **Canonical Halal Universe Size:** {len(halal_universe)} approved symbols
* **Technical Breakout Candidates:** {len(scored_candidates)} filtered stocks

---

## 🎯 Top Ranked Candidates for TradingView Observation
| Rank | Symbol | Company | Close Price (₹) | Volume | % Change | Setup Score |
|:---:|:---|:---|:---:|:---:|:---:|:---:|
"""
        for i, c in enumerate(scored_candidates, 1):
            md += f"| {i} | **{c['symbol']}** | {c['company_name']} | {c['close_price']} | {c['volume']:,} | {c['per_change']}% | **{c['score']}** |\n"

        md += """
---

## 🛡️ Governance & Action Plan
1. **Visual Confirmation:** Verify setup charts manually on **TradingView** against your strategy rules (EMA 20/50, RSI, VWAP).
2. **Risk Check:** Calculate position size and stop-loss using the OS pre-trade parameters.
3. **Execution Gate:** Execute approved trades manually via **Zerodha Kite**.
4. **Journal Sync:** Completed trades will automatically sync to `Trading_Journal.csv` for Power BI analytics.
"""
        return md

    def _append_audit_log(self, record: dict):
        logs = []
        if os.path.exists(self.audit_log_path):
            try:
                with open(self.audit_log_path, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        logs.append(record)
        with open(self.audit_log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

if __name__ == "__main__":
    runner = OperationalDailyRunner()
    runner.run_morning_pipeline()