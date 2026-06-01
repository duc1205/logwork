# PC khong co Mobile Hotspot — tao link public qua Cloudflare Tunnel (chi can port 5173)
# UI proxy /api ve localhost:8000 nen chi tunnel UI la du.
#
# Cai cloudflared (mot lan):
#   winget install Cloudflare.cloudflared
# hoac: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
#
# Chay: .\logwork\scripts\run_tunnel.ps1
# Copy link https://....trycloudflare.com gui dong nghiep

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logworkDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $logworkDir
$uiDir = Join-Path $logworkDir "ui"
$uiPort = if ($env:LOGWORK_UI_PORT) { [int]$env:LOGWORK_UI_PORT } else { 5173 }
$apiPort = if ($env:LOGWORK_API_PORT) { [int]$env:LOGWORK_API_PORT } else { 8000 }

function Test-PortListen {
    param([int]$Port)
    return [bool](Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -eq $Port })
}

function Find-Cloudflared {
    $cmd = Get-Command cloudflared -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $paths = @(
        "$env:ProgramFiles\cloudflared\cloudflared.exe",
        "$env:LOCALAPPDATA\Microsoft\WinGet\Links\cloudflared.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

Set-Location $repoRoot

Write-Host ""
Write-Host "=== Logwork — Cloudflare Tunnel (khong can hotspot) ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-PortListen -Port $uiPort)) {
    Write-Host "UI chua chay tren port $uiPort — dang khoi dong API + UI (localhost)..." -ForegroundColor Yellow
    $apiCmd = "cd '$repoRoot'; `$env:LOGWORK_DISABLE_SCHEDULER='1'; `$env:LOGWORK_ALLOW_LAN='1'; python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port $apiPort --reload"
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $apiCmd)
    Start-Sleep -Seconds 2
    $uiCmd = "cd '$uiDir'; npm run dev -- --port $uiPort --host 127.0.0.1"
    Start-Process powershell -ArgumentList @("-NoExit", "-Command", $uiCmd)
    Write-Host "Doi UI khoi dong..."
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 1
        if (Test-PortListen -Port $uiPort) { break }
    }
    if (-not (Test-PortListen -Port $uiPort)) {
        Write-Host "Loi: UI khong len port $uiPort. Kiem tra cua so npm." -ForegroundColor Red
        exit 1
    }
    Write-Host "UI da san sang tren localhost:$uiPort" -ForegroundColor Green
    Write-Host ""
}

$cf = Find-Cloudflared
if ($cf) {
    Write-Host "Dang tao tunnel (cloudflared)..." -ForegroundColor Green
    Write-Host "Copy link https://....trycloudflare.com hien duoi va gui dong nghiep."
    Write-Host "Nhan Ctrl+C de dung tunnel."
    Write-Host ""
    & $cf tunnel --url "http://127.0.0.1:$uiPort"
    exit $LASTEXITCODE
}

Write-Host "Chua co cloudflared — thu localtunnel (npm)..." -ForegroundColor Yellow
Write-Host "Cai cloudflared de on dinh hon: winget install Cloudflare.cloudflared"
Write-Host ""
Set-Location $uiDir
npx --yes localtunnel --port $uiPort
