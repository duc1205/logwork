# Chay API + UI dev (2 cua so PowerShell) — chi may local
# De dong nghiep trong cong ty test: .\logwork\scripts\run_lan.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logworkDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $logworkDir
$uiDir = Join-Path $logworkDir "ui"
Set-Location $repoRoot

$liveDir = Join-Path $logworkDir "fixtures\live"

function Stop-PortListener([int]$Port) {
    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object {
            $p = Get-Process -Id $_ -ErrorAction SilentlyContinue
            if ($p) {
                Write-Host "  Stop PID $_ ($($p.ProcessName)) on port $Port"
                Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
            }
        }
}

$apiPort = if ($env:LOGWORK_API_PORT) { [int]$env:LOGWORK_API_PORT } else { 8001 }
Write-Host "Freeing port $apiPort (stop old API if any)..."
Stop-PortListener $apiPort
Start-Sleep -Seconds 1

Write-Host "Starting Logwork API on :$apiPort (data: $liveDir) ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$repoRoot'; `$env:LOGWORK_DISABLE_SCHEDULER='1'; `$env:LOGWORK_DATA_DIR='$liveDir'; python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port $apiPort --reload"
)

Start-Sleep -Seconds 2

Write-Host "Starting Logwork UI on :5173 ..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$uiDir'; npm run dev"
)

Write-Host "Done. API: http://127.0.0.1:$apiPort/api/health  UI: http://localhost:5173"
Write-Host "UI proxy: ui/.env LOGWORK_API_PROXY=http://127.0.0.1:$apiPort"
