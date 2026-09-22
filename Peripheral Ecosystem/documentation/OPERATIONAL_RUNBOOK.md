# Halal Trading OS — Operational Runbook

**Document:** `OPERATIONAL_RUNBOOK.md`  
**System:** Halal Trading OS — Observability & Webhook Ingestion Layer  
**Status:** Operational  
**Scope:** Phase 14 operational hardening  
**Execution mode:** Read-only / manual execution only

---

## 1. Purpose

This runbook defines the standard operating procedures for starting, monitoring, shutting down, recovering, and troubleshooting the Trading OS observability and webhook-ingestion layer.

The runbook covers:

- FastAPI local webhook ingestion
- Cloudflare Quick Tunnel external ingress
- OpportunityID lifecycle handling
- Canonical Power BI CSV feeders
- Power BI refresh and verification
- Daily startup and shutdown
- Restart and recovery procedures
- Webhook troubleshooting
- Basic data-cache protection and backup practices
- Governance verification

This runbook does **not** authorize automated trade execution.

---

## 2. Governance — Non-Negotiable Controls

The following controls must remain active unless the system's governance policy is explicitly changed through the appropriate controlled process:

```text
READ_ONLY = TRUE
LIVE_AUTO_EXECUTION = FALSE
ORDER_CAPABILITY = NONE
EXECUTION_AUTHORITY = NONE
```

### Operational rule

Webhook ingestion, opportunity creation, technical evidence collection, audits, telemetry, and Power BI reporting may operate continuously without granting the system authority to place broker orders.

If any health response, log, or diagnostic output indicates a change to the above controls, stop normal operation and investigate before processing further external webhook traffic.

---

## 3. Core Architecture

```text
Chartink / TradingView
          │
          ▼
 Cloudflare Quick Tunnel
          │
          ▼
 FastAPI — 127.0.0.1:8000
          │
          ▼
 Provider Webhook Adapter
          │
          ▼
 Opportunity Lifecycle Manager
          │
          ▼
 Canonical Event CSV Contracts
          │
          ▼
 Power BI
          │
          ▼
 Trading OS — Decision Journey
```

### Opportunity identity

Opportunity threads use the canonical format:

```text
OPP-YYYYMMDD-NNNN
```

Example:

```text
OPP-20260921-005
```

The orchestration/lifecycle layer owns `OpportunityID` generation. Power BI must never generate opportunity identifiers.

Cross-provider evidence for the same active opportunity must reuse the existing `OpportunityID` rather than create another opportunity thread.

---

## 4. Key Locations

### Trading OS root

```text
D:\OBSIDIAN VAULT\halal-trading-os
```

### Peripheral Ecosystem

```text
D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem
```

### Power BI data cache

```text
D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi
```

### Startup script

```text
D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\start_trading_os.bat
```

### FastAPI server

```text
D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\webhook_server.py
```

### Cloudflare client

```text
D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\cloudflared.exe
```

### Power BI report

```text
D:\OBSIDIAN VAULT\Trading Reports.pbix
```

---

## 5. Canonical Power BI Feeder Contracts

The current seven feeder files are:

```text
powerbi_screening.csv
powerbi_scanner_events.csv
powerbi_technical_events.csv
powerbi_market_context.csv
powerbi_audits.csv
powerbi_execution_events.csv
powerbi_opportunity_trade_bridge.csv
```

### Expected responsibilities

| Feeder | Purpose |
|---|---|
| `powerbi_screening.csv` | Periodic fundamental/Shariah screening eligibility |
| `powerbi_scanner_events.csv` | Scanner evidence and scanner outputs |
| `powerbi_technical_events.csv` | TradingView/technical observations |
| `powerbi_market_context.csv` | Market regime/context evidence |
| `powerbi_audits.csv` | Governance and audit decisions |
| `powerbi_execution_events.csv` | Execution-side/manual execution telemetry |
| `powerbi_opportunity_trade_bridge.csv` | Opportunity-to-trade lineage |

`Fact_Trades` remains the authoritative record of actual executed trades in Power BI.

Legacy signal feeders must not be reintroduced:

```text
powerbi_signals.csv
powerbi_signal_trade_bridge.csv
powerbi_telemetry.csv
```

---

## 6. Daily Startup Procedure

### Recommended method

Double-click:

```text
start_trading_os.bat
```

The script launches:

1. FastAPI on `127.0.0.1:8000`
2. Cloudflare Quick Tunnel targeting `http://localhost:8000`

Two dedicated command windows should appear.

### Manual startup equivalent

FastAPI:

```powershell
cd "D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem"
python webhook_server.py
```

Cloudflare Quick Tunnel:

```powershell
cd "D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem"
.\cloudflared.exe tunnel --url http://localhost:8000
```

Copy the current `trycloudflare.com` URL shown by Cloudflare when external webhook testing or provider configuration requires it.

### Important

The Quick Tunnel URL is tied to that tunnel session. Treat each newly issued URL as the active ingress address for that session.

---

## 7. Startup Health Check

### Local health check

Run:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

Expected result:

```text
200 OK
```

The health response must continue to report the required governance state, including:

```text
READ_ONLY = true
LIVE_AUTO_EXECUTION = false
```

### Public health check

Using the current Quick Tunnel hostname:

```powershell
Invoke-WebRequest https://<current-trycloudflare-host>/health
```

Expected result:

```text
200 OK
```

A successful public health check confirms that external ingress currently reaches the local FastAPI service.

---

## 8. Webhook Verification

When testing or activating an external webhook source:

1. Confirm FastAPI health locally.
2. Confirm the current Quick Tunnel URL.
3. Send one controlled webhook.
4. Confirm the endpoint returns a successful response.
5. Confirm the correct provider event was persisted.
6. Confirm the expected `OpportunityID` was created or reused.
7. Confirm no unintended duplicate opportunity was generated.
8. Refresh Power BI when a visual verification is required.

### Cross-provider binding

If Chartink creates:

```text
OPP-20260921-005
```

and TradingView subsequently provides technical evidence for the same active opportunity, the TradingView event must attach to:

```text
OPP-20260921-005
```

It must not create a new opportunity merely because it came from another provider.

---

## 9. Idempotency Rules

Repeated delivery of the same webhook must be handled safely.

### Required behavior

```text
Same provider
+ same underlying event
+ retry
       ↓
Existing event/opportunity recognized
       ↓
No duplicate opportunity thread
```

Never allow a retry to transform one event into an uncontrolled sequence such as:

```text
OPP-20260921-005
OPP-20260921-006
OPP-20260921-007
```

when all three represent the same underlying provider event.

If duplicate behavior is observed, stop external webhook traffic and investigate before continuing normal operation.

---

## 10. Power BI Refresh Procedure

After verified new telemetry has been ingested:

1. Open `Trading Reports.pbix`.
2. Select **Home → Refresh**.
3. Open **Trading OS — Decision Journey**.
4. Confirm the new opportunity appears.
5. Verify the evidence trail across the diagnostic matrix.
6. Confirm the KPI cards, funnel, scanner analysis, and outcome/rejection visuals are consistent.

### Do not modify the six core trading dashboard pages during routine telemetry refresh operations.

The existing core pages remain:

- Trading Overview
- Capital Growth & Risk
- Strategy & Emotion
- Monthly Performance
- Drawdown & Streaks
- Trading Journal

The observability page is:

- Trading OS — Decision Journey

---

## 11. Daily Shutdown Procedure

When external webhook ingestion is no longer required:

1. Stop/close the Cloudflare Quick Tunnel terminal.
2. Stop/close the FastAPI terminal.
3. Confirm the local server is no longer accepting requests if required.
4. Leave all historical CSV data intact.
5. Leave governance configuration unchanged.

### PowerShell verification after shutdown

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

This request should fail once FastAPI is fully stopped.

Shutdown must **not** modify historical opportunity or trade data.

---

## 12. Restart / Recovery Procedure

If Windows, Python, FastAPI, or the tunnel restarts:

1. Start `start_trading_os.bat`.
2. Wait for both FastAPI and Cloudflare terminals to initialize.
3. Run the local health check.
4. Run the public health check.
5. Verify governance state.
6. Confirm existing event data remains in the Power BI cache.
7. Perform one controlled webhook test if operationally necessary.
8. Verify idempotency if a retry/replay is suspected.
9. Refresh Power BI.

### Recovery principle

Do not manually invent or renumber an `OpportunityID` to repair a display problem.

Opportunity state must be reconstructed from the existing canonical event history and the lifecycle manager's deterministic logic.

---

## 13. Troubleshooting Matrix

| Symptom | Check | Action |
|---|---|---|
| FastAPI health fails | FastAPI terminal/process | Restart `webhook_server.py` |
| Local health works, public health fails | Cloudflare terminal | Restart Quick Tunnel and use new URL |
| Webhook returns `422` | Payload schema | Validate required fields and provider format |
| Webhook rejected | Provider/route mismatch | Confirm endpoint path and provider payload |
| Duplicate opportunity appears | Idempotency/lifecycle state | Stop external retries and inspect event identity handling |
| CSV not updated | Adapter/persistence path | Inspect server/adapter logs before retrying |
| CSV updated but Power BI unchanged | Refresh state | Run Power BI Refresh and inspect query source path |
| Power BI schema error | CSV header/type drift | Restore canonical schema; do not patch the PBIX blindly |
| Governance value changes unexpectedly | Runtime/config drift | Stop ingestion and perform governance audit |
| Cloudflare URL changed | Quick Tunnel restarted | Update external webhook URL for the current session |

---

## 14. Data Integrity Rules

The following must remain true:

- Never overwrite historical trading records merely to correct a display issue.
- Never fabricate an opportunity solely to populate Power BI visuals.
- Never change canonical CSV headers casually.
- Never add legacy signal fields back into the event model to satisfy an old integration.
- Preserve provider provenance on all external evidence.
- Keep `OpportunityID` as text across the Power BI model.
- Keep execution telemetry separate from actual trade facts.
- Keep `Fact_Trades` restricted to actual trades.

---

## 15. Backup / Archive Practice

Before major structural changes to the Power BI model, event contracts, or provider adapters:

1. Stop external webhook ingestion.
2. Copy the current `data_cache\powerbi` directory to a dated archive.
3. Preserve the current PBIX file as a dated backup.
4. Apply the change.
5. Run health checks and regression tests.
6. Refresh Power BI.
7. Compare the new state with the saved baseline.

Recommended archive naming:

```text
powerbi_backup_YYYYMMDD_HHMM
Trading_Reports_backup_YYYYMMDD_HHMM.pbix
```

Do not delete historical backups until the newer architecture has been verified.

---

## 16. Safe Operational Boundaries

The following are deliberately outside the routine operational runbook:

- automatic broker order placement
- automatic order modification
- automatic order cancellation
- enabling `LIVE_AUTO_EXECUTION`
- changing `ORDER_CAPABILITY` to an executable mode
- granting execution authority to Qwen or another model
- bypassing deterministic governance checks

These require a separate controlled authorization and readiness process.

---

## 17. Phase 14 Acceptance Checklist

### Startup

- [ ] `start_trading_os.bat` launches FastAPI
- [ ] FastAPI binds to `127.0.0.1:8000`
- [ ] Cloudflare Quick Tunnel starts
- [ ] Local `/health` returns `200 OK`
- [ ] Public `/health` returns `200 OK`
- [ ] Governance values remain correct

### Ingestion

- [ ] Chartink webhook accepted
- [ ] TradingView webhook accepted
- [ ] OpportunityID generated deterministically
- [ ] Cross-provider evidence reuses the same OpportunityID
- [ ] Duplicate retries do not create duplicate opportunities
- [ ] Malformed payloads are rejected

### Power BI

- [ ] Canonical feeder CSVs remain schema-correct
- [ ] Power BI refresh succeeds
- [ ] Decision Journey page shows current opportunities
- [ ] Diagnostic matrix shows provider evidence lineage
- [ ] Existing six core dashboard pages remain intact

### Recovery

- [ ] FastAPI can be restarted cleanly
- [ ] Cloudflare Quick Tunnel can be restarted cleanly
- [ ] Existing historical data survives restart
- [ ] New tunnel URL can be substituted without architecture changes
- [ ] Governance remains unchanged after restart

### Governance

- [ ] `READ_ONLY = TRUE`
- [ ] `LIVE_AUTO_EXECUTION = FALSE`
- [ ] `ORDER_CAPABILITY = NONE`
- [ ] `EXECUTION_AUTHORITY = NONE`

---

## 18. Current Operational Status

**Phase 13:** Complete — local webhook ingestion and controlled external ingress verified.  
**Phase 14A/14B:** Operational procedures and startup automation established.  
**Phase 14 focus:** Operational reliability, maintenance, recovery, and governance preservation.

### Current execution posture

```text
ANALYSIS / TELEMETRY: ENABLED
WEBHOOK INGESTION: ENABLED WHEN SERVER IS RUNNING
POWER BI OBSERVABILITY: ENABLED
MANUAL EXECUTION: ALLOWED UNDER EXISTING GOVERNANCE
AUTOMATED LIVE EXECUTION: DISABLED
```

---

## 19. Future Phase Gate

Do not treat operational hardening as authorization for automated trading.

After Phase 14 is stable, the next workstream may focus on:

- advanced analytics and DAX
- opportunity time-in-stage analysis
- scanner conversion analysis
- rejection analysis
- execution slippage telemetry
- operational monitoring
- regression/invariant audits

Any future live-execution activation remains a separate explicit decision and must preserve all deterministic governance controls.
