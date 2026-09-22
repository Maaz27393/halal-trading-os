$ErrorActionPreference = "Stop"

$AUDIT_FILE = "D:\OBSIDIAN VAULT\halal-trading-os\Peripheral Ecosystem\data_cache\powerbi\powerbi_audits.csv"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       TRADING OS - AUDIT LOG REVIEW" -ForegroundColor Cyan
Write-Host "========================================================"

if (-not (Test-Path $AUDIT_FILE)) {
    Write-Host "[FAIL] Audit file not found:" -ForegroundColor Red
    Write-Host $AUDIT_FILE
    exit 1
}

$rows = Import-Csv $AUDIT_FILE

if (-not $rows -or $rows.Count -eq 0) {
    Write-Host "[INFO] powerbi_audits.csv contains no audit records." -ForegroundColor Yellow
    Write-Host "Audit review complete."
    exit 0
}

Write-Host ""
Write-Host "Total audit records: $($rows.Count)" -ForegroundColor Green

# --------------------------------------------------------
# Recent events
# --------------------------------------------------------

Write-Host ""
Write-Host "LATEST AUDIT EVENTS" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"

$rows |
    Sort-Object Timestamp -Descending |
    Select-Object -First 20 `
        Timestamp,
        OpportunityID,
        Component,
        AuditType,
        Decision,
        Result,
        Severity,
        Rule,
        Reason |
    Format-Table -AutoSize -Wrap

# --------------------------------------------------------
# Decision summary
# --------------------------------------------------------

Write-Host ""
Write-Host "DECISION SUMMARY" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"

$rows |
    Group-Object Decision |
    Sort-Object Count -Descending |
    Select-Object Name, Count |
    Format-Table -AutoSize

# --------------------------------------------------------
# Result summary
# --------------------------------------------------------

Write-Host ""
Write-Host "RESULT SUMMARY" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"

$rows |
    Group-Object Result |
    Sort-Object Count -Descending |
    Select-Object Name, Count |
    Format-Table -AutoSize

# --------------------------------------------------------
# Severity summary
# --------------------------------------------------------

Write-Host ""
Write-Host "SEVERITY SUMMARY" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"

$rows |
    Group-Object Severity |
    Sort-Object Count -Descending |
    Select-Object Name, Count |
    Format-Table -AutoSize

# --------------------------------------------------------
# Opportunity coverage
# --------------------------------------------------------

$opportunities = $rows |
    Where-Object { $_.OpportunityID -and $_.OpportunityID.Trim() -ne "" } |
    Select-Object -ExpandProperty OpportunityID -Unique

Write-Host ""
Write-Host "OPPORTUNITY COVERAGE" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"
Write-Host "Unique OpportunityIDs with audit records: $($opportunities.Count)"

# --------------------------------------------------------
# Governance verification
# --------------------------------------------------------

Write-Host ""
Write-Host "GOVERNANCE AUDIT" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------"

$readOnlyValues = $rows |
    Select-Object -ExpandProperty ReadOnly -Unique

$liveExecutionValues = $rows |
    Select-Object -ExpandProperty LiveAutoExecution -Unique

$orderValues = $rows |
    Select-Object -ExpandProperty OrderCapability -Unique

$authorityValues = $rows |
    Select-Object -ExpandProperty ExecutionAuthority -Unique

Write-Host "ReadOnly values:            $($readOnlyValues -join ', ')"
Write-Host "LiveAutoExecution values:   $($liveExecutionValues -join ', ')"
Write-Host "OrderCapability values:     $($orderValues -join ', ')"
Write-Host "ExecutionAuthority values:  $($authorityValues -join ', ')"

$governanceSafe = $true

if ($readOnlyValues -contains "False" -or $readOnlyValues -contains "false") {
    $governanceSafe = $false
}

if ($liveExecutionValues -contains "True" -or $liveExecutionValues -contains "true") {
    $governanceSafe = $false
}

if ($orderValues | Where-Object { $_ -and $_ -ne "NONE" }) {
    $governanceSafe = $false
}

if ($authorityValues | Where-Object { $_ -and $_ -ne "NONE" }) {
    $governanceSafe = $false
}

if ($governanceSafe) {
    Write-Host "[PASS] Audit records preserve required governance state." -ForegroundColor Green
}
else {
    Write-Host "[FAIL] Governance deviation detected in audit records." -ForegroundColor Red
}

# --------------------------------------------------------
# Final result
# --------------------------------------------------------

Write-Host ""
Write-Host "========================================================"

if ($governanceSafe) {
    Write-Host "AUDIT REVIEW: HEALTHY" -ForegroundColor Green
}
else {
    Write-Host "AUDIT REVIEW: ATTENTION REQUIRED" -ForegroundColor Red
}