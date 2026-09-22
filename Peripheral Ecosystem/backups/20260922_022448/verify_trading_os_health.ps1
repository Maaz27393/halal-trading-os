$ErrorActionPreference = "Stop"

$ROOT = "D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem"
$DATA = Join-Path $ROOT "data_cache\powerbi"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       TRADING OS - HEALTH & DEPENDENCY CHECK" -ForegroundColor Cyan
Write-Host "========================================================"

$failed = $false

function Test-ItemPath {
    param(
        [string]$Path,
        [string]$Label
    )

    if (Test-Path $Path) {
        Write-Host "[PASS] $Label" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] $Label" -ForegroundColor Red
        $script:failed = $true
    }
}

# --------------------------------------------------------
# Core files
# --------------------------------------------------------

Test-ItemPath `
    (Join-Path $ROOT "webhook_server.py") `
    "FastAPI server"

Test-ItemPath `
    (Join-Path $ROOT "start_trading_os.bat") `
    "Startup script"

Test-ItemPath `
    (Join-Path $ROOT "cloudflared.exe") `
    "Cloudflare executable"

Test-ItemPath `
    $DATA `
    "Power BI data cache"

# --------------------------------------------------------
# Canonical feeder contracts
# --------------------------------------------------------

$feeders = @(
    "powerbi_screening.csv",
    "powerbi_scanner_events.csv",
    "powerbi_technical_events.csv",
    "powerbi_market_context.csv",
    "powerbi_audits.csv",
    "powerbi_execution_events.csv",
    "powerbi_opportunity_trade_bridge.csv"
)

foreach ($file in $feeders) {
    Test-ItemPath `
        (Join-Path $DATA $file) `
        $file
}

# --------------------------------------------------------
# Python
# --------------------------------------------------------

try {
    $pythonVersion = python --version 2>&1
    Write-Host "[PASS] Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Python unavailable" -ForegroundColor Red
    $failed = $true
}

# --------------------------------------------------------
# FastAPI health endpoint + governance
# --------------------------------------------------------

try {
    $health = Invoke-RestMethod `
        -Uri "http://127.0.0.1:8000/health" `
        -Method Get `
        -TimeoutSec 5

    Write-Host "[PASS] FastAPI health endpoint: 200 OK" -ForegroundColor Green

    if ($health.status -eq "HEALTHY") {
        Write-Host "[PASS] API status = HEALTHY" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] API status is not HEALTHY" -ForegroundColor Red
        $failed = $true
    }

    if ($null -eq $health.guardrails) {
        Write-Host "[FAIL] Governance guardrails missing" -ForegroundColor Red
        $failed = $true
    }
    else {
        if ($health.guardrails.READ_ONLY -eq $true) {
            Write-Host "[PASS] READ_ONLY = TRUE" -ForegroundColor Green
        }
        else {
            Write-Host "[FAIL] READ_ONLY is not TRUE" -ForegroundColor Red
            $failed = $true
        }

        if ($health.guardrails.LIVE_AUTO_EXECUTION -eq $false) {
            Write-Host "[PASS] LIVE_AUTO_EXECUTION = FALSE" -ForegroundColor Green
        }
        else {
            Write-Host "[FAIL] LIVE_AUTO_EXECUTION is not FALSE" -ForegroundColor Red
            $failed = $true
        }

        if ($health.guardrails.ORDER_CAPABILITY -eq "NONE") {
            Write-Host "[PASS] ORDER_CAPABILITY = NONE" -ForegroundColor Green
        }
        else {
            Write-Host "[FAIL] ORDER_CAPABILITY is not NONE" -ForegroundColor Red
            $failed = $true
        }

        if ($health.guardrails.EXECUTION_AUTHORITY -eq "NONE") {
            Write-Host "[PASS] EXECUTION_AUTHORITY = NONE" -ForegroundColor Green
        }
        else {
            Write-Host "[FAIL] EXECUTION_AUTHORITY is not NONE" -ForegroundColor Red
            $failed = $true
        }
    }
}
catch {
    Write-Host "[FAIL] FastAPI health endpoint unavailable" -ForegroundColor Red
    Write-Host "       $($_.Exception.Message)" -ForegroundColor Red
    $failed = $true
}

# --------------------------------------------------------
# Port 8000
# --------------------------------------------------------

try {
    $port = Get-NetTCPConnection `
        -LocalPort 8000 `
        -State Listen `
        -ErrorAction Stop

    if ($port) {
        Write-Host "[PASS] Port 8000 is listening" -ForegroundColor Green
    }
    else {
        Write-Host "[FAIL] Port 8000 is not listening" -ForegroundColor Red
        $failed = $true
    }
}
catch {
    Write-Host "[FAIL] Port 8000 is not listening" -ForegroundColor Red
    $failed = $true
}

# --------------------------------------------------------
# Cloudflare process
# --------------------------------------------------------

$cloudflared = Get-Process cloudflared -ErrorAction SilentlyContinue

if ($cloudflared) {
    Write-Host "[PASS] Cloudflare process is running" -ForegroundColor Green
}
else {
    Write-Host "[WARN] Cloudflare process is not running" -ForegroundColor Yellow
    Write-Host "       External ingress is currently offline."
}

# --------------------------------------------------------
# Final result
# --------------------------------------------------------

Write-Host ""
Write-Host "========================================================"

if ($failed) {
    Write-Host "TRADING OS STATUS: NOT READY" -ForegroundColor Red
    Write-Host "Resolve the failed checks before operating the system."
    exit 1
}
else {
    Write-Host "TRADING OS STATUS: HEALTHY" -ForegroundColor Green
    Write-Host "Governance and dependency checks passed." -ForegroundColor Green
    exit 0
}