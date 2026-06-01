# Chay API + UI dev (2 cua so PowerShell) — chi may local
# De dong nghiep trong cong ty test: .\logwork\scripts\run_lan.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logworkDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $logworkDir
$uiDir = Join-Path $logworkDir "ui"
Set-Location $repoRoot

Write-Host "Starting Logwork API on :8000 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$repoRoot'; `$env:LOGWORK_DISABLE_SCHEDULER='1'; python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8000 --reload"
)

Start-Sleep -Seconds 2

Write-Host "Starting Logwork UI on :5173 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$uiDir'; npm run dev"
)

Write-Host "Done. API: http://127.0.0.1:8000/api/health  UI: http://localhost:5173"
