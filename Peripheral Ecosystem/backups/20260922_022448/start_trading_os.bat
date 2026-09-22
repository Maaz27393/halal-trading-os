@echo off
TITLE Trading OS Observability Engine
COLOR 0A

echo ========================================================
echo       TRADING OS OBSERVABILITY ENGINE - STARTUP
echo ========================================================
echo Governance Check: READ_ONLY = TRUE
echo Governance Check: LIVE_AUTO_EXECUTION = FALSE
echo Governance Check: ORDER_CAPABILITY = NONE
echo Governance Check: EXECUTION_AUTHORITY = NONE
echo --------------------------------------------------------

echo [1/2] Launching FastAPI Ingestion Server...
start "Trading OS - FastAPI" cmd /k "cd /d D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem && python webhook_server.py"

TIMEOUT /T 3 /NOBREAK > nul

echo [2/2] Launching Cloudflare Quick Tunnel...
start "Trading OS - Cloudflare" cmd /k "cd /d D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem && .\cloudflared.exe tunnel --url http://localhost:8000"

echo --------------------------------------------------------
echo Trading OS startup commands issued.
echo FastAPI: http://127.0.0.1:8000
echo Cloudflare tunnel: check the Cloudflare terminal
echo ========================================================
pause