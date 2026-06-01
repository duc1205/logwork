# Tunnel chi API (port 8001) — dung voi UI tren GitHub Pages
# UI: https://duc1205.github.io/logwork/  +  config.json / VITE_API_BASE_URL = link tunnel
#
# Terminal 1 — API:
#   cd d:\
#   $env:LOGWORK_DATA_DIR="d:\logwork\fixtures\live"
#   $env:LOGWORK_DISABLE_SCHEDULER="1"
#   $env:LOGWORK_ALLOW_LAN="1"
#   python -m uvicorn logwork.api.main:app --host 127.0.0.1 --port 8001
#
# Terminal 2 — tunnel:
#   .\logwork\scripts\run_tunnel_api.ps1

$ErrorActionPreference = "Stop"
$apiPort = if ($env:LOGWORK_API_PORT) { [int]$env:LOGWORK_API_PORT } else { 8001 }

$cf = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cf) {
    Write-Host "Cai cloudflared: winget install Cloudflare.cloudflared" -ForegroundColor Yellow
    exit 1
}

Write-Host "Tunnel API http://127.0.0.1:$apiPort -> trycloudflare.com"
Write-Host "Dat URL (khong co / cuoi) vao:"
Write-Host "  - GitHub: Settings -> Actions -> Variables -> VITE_API_BASE_URL"
Write-Host "  - hoac ui/public/config.json -> apiBaseUrl"
Write-Host ""

& cloudflared tunnel --url "http://127.0.0.1:$apiPort"
