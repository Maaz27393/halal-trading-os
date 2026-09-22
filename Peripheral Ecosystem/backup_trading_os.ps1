$ErrorActionPreference = "Stop"

$ROOT = "D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem"
$DATA = Join-Path $ROOT "data_cache\powerbi"
$BACKUP_ROOT = Join-Path $ROOT "backups"

$STAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_DIR = Join-Path $BACKUP_ROOT $STAMP

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       TRADING OS - BACKUP & ARCHIVE" -ForegroundColor Cyan
Write-Host "========================================================"

New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null

# --------------------------------------------------------
# Canonical Power BI feeders
# --------------------------------------------------------

$files = @(
    "powerbi_screening.csv",
    "powerbi_scanner_events.csv",
    "powerbi_technical_events.csv",
    "powerbi_market_context.csv",
    "powerbi_audits.csv",
    "powerbi_execution_events.csv",
    "powerbi_opportunity_trade_bridge.csv"
)

foreach ($file in $files) {
    $source = Join-Path $DATA $file

    if (Test-Path $source) {
        Copy-Item $source $BACKUP_DIR -Force
        Write-Host "[BACKUP] $file" -ForegroundColor Green
    }
    else {
        Write-Host "[WARN] Missing: $file" -ForegroundColor Yellow
    }
}

# --------------------------------------------------------
# Operational files
# --------------------------------------------------------

$operationalFiles = @(
    "webhook_server.py",
    "start_trading_os.bat",
    "verify_trading_os_health.ps1",
    "documentation\OPERATIONAL_RUNBOOK.md"
)

foreach ($file in $operationalFiles) {
    $source = Join-Path $ROOT $file

    if (Test-Path $source) {
        Copy-Item $source $BACKUP_DIR -Force
        Write-Host "[BACKUP] $file" -ForegroundColor Green
    }
}

# --------------------------------------------------------
# Create manifest
# --------------------------------------------------------

$manifest = [PSCustomObject]@{
    BackupTimestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    BackupDirectory = $BACKUP_DIR
    GovernanceReadOnly = $true
    LiveAutoExecution = $false
    OrderCapability = "NONE"
    ExecutionAuthority = "NONE"
}

$manifest |
    ConvertTo-Json |
    Set-Content (Join-Path $BACKUP_DIR "backup_manifest.json") -Encoding UTF8

Write-Host ""
Write-Host "Backup created:" -ForegroundColor Green
Write-Host $BACKUP_DIR

# --------------------------------------------------------
# Retention: keep latest 30 backup folders
# --------------------------------------------------------

$backups = Get-ChildItem $BACKUP_ROOT -Directory |
    Sort-Object CreationTime -Descending

if ($backups.Count -gt 30) {
    $backups | Select-Object -Skip 30 | ForEach-Object {
        Remove-Item $_.FullName -Recurse -Force
        Write-Host "[ARCHIVE CLEANUP] Removed old backup: $($_.Name)"
    }
}

Write-Host ""
Write-Host "TRADING OS BACKUP COMPLETE" -ForegroundColor Green