# Logwork LAN demo — colleagues on same WiFi/VPN can open http://<your-ip>:5173/
# Run PowerShell as Administrator if firewall blocks inbound connections.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$logworkDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $logworkDir
$uiDir = Join-Path $logworkDir "ui"
Set-Location $repoRoot

function Get-LanIPv4 {
    $addrs = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*" -and
            $_.PrefixOrigin -ne "WellKnown"
        } |
        Sort-Object InterfaceMetric |
        Select-Object -ExpandProperty IPAddress -First 1
    if ($addrs) { return $addrs }
    return "127.0.0.1"
}

function Ensure-FirewallRule {
    param([int]$Port, [string]$Label)
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host "  Skip firewall $Label (run PowerShell as Admin if peers cannot connect)"
        return
    }
    $name = "Logwork-$Label-$Port"
    $existing = Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue
    if (-not $existing) {
        New-NetFirewallRule -DisplayName $name -Direction Inbound -Action Allow -Protocol TCP `
            -LocalPort $Port -Profile Any | Out-Null
        Write-Host "  Firewall: opened inbound TCP $Port ($Label)"
    } else {
        Enable-NetFirewallRule -DisplayName $name | Out-Null
        Write-Host "  Firewall: rule exists for $Label port $Port"
    }
}

function Get-LanIPv4All {
    Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*" -and
            $_.PrefixOrigin -ne "WellKnown"
        } |
        Sort-Object InterfaceMetric |
        ForEach-Object {
            $alias = (Get-NetAdapter -InterfaceIndex $_.InterfaceIndex -ErrorAction SilentlyContinue).Name
            [PSCustomObject]@{
                IP = $_.IPAddress
                Interface = $alias
            }
        }
}

function Test-LocalPortListen {
    param([int]$Port)
    $listeners = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -eq $Port }
    return ($listeners | Where-Object { $_.LocalAddress -eq "0.0.0.0" -or $_.LocalAddress -eq "::" }).Count -gt 0
}

$lanIp = Get-LanIPv4
$allIps = Get-LanIPv4All
$uiPort = if ($env:LOGWORK_UI_PORT) { $env:LOGWORK_UI_PORT } else { "5173" }
$apiPort = if ($env:LOGWORK_API_PORT) { $env:LOGWORK_API_PORT } else { "8000" }

Write-Host ""
Write-Host "=== Logwork LAN ===" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot"
Write-Host "UI dir: $uiDir"
Write-Host "This machine IP (primary): $lanIp"
if ($allIps.Count -gt 1) {
    Write-Host "All LAN IPs:"
    $allIps | ForEach-Object { Write-Host "  $($_.IP)  ($($_.Interface))" }
}
$netProfile = Get-NetConnectionProfile -ErrorAction SilentlyContinue | Where-Object { $_.IPv4Connectivity -eq "Internet" -or $_.IPv4Connectivity -eq "LocalNetwork" } | Select-Object -First 1
if ($netProfile -and $netProfile.NetworkCategory -eq "Public") {
    Write-Host ""
    Write-Host "WARN: Network profile is Public — if peers cannot connect, set Ethernet/WiFi to Private:" -ForegroundColor Yellow
    Write-Host "  Settings > Network > Properties > Private network"
}
Write-Host ""

Write-Host "Firewall (optional, needs Admin)..."
Ensure-FirewallRule -Port ([int]$uiPort) -Label "UI"
Ensure-FirewallRule -Port ([int]$apiPort) -Label "API"
Write-Host ""

Write-Host "Starting API on 0.0.0.0:$apiPort ..."
$apiCmd = "cd '$repoRoot'; `$env:LOGWORK_DISABLE_SCHEDULER='1'; `$env:LOGWORK_ALLOW_LAN='1'; python -m uvicorn logwork.api.main:app --host 0.0.0.0 --port $apiPort --reload"
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $apiCmd)

Start-Sleep -Seconds 2

Write-Host "Starting UI on 0.0.0.0:$uiPort ..."
$uiCmd = "cd '$uiDir'; npm run dev:lan -- --port $uiPort"
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $uiCmd)

Start-Sleep -Seconds 4

Write-Host "Checking listeners..."
$uiOk = Test-LocalPortListen -Port ([int]$uiPort)
$apiOk = Test-LocalPortListen -Port ([int]$apiPort)
if ($uiOk) { Write-Host "  UI  port $uiPort listening on 0.0.0.0 (OK)" -ForegroundColor Green }
else { Write-Host "  UI  port $uiPort NOT on 0.0.0.0 — check UI window for errors" -ForegroundColor Red }
if ($apiOk) { Write-Host "  API port $apiPort listening on 0.0.0.0 (OK)" -ForegroundColor Green }
else { Write-Host "  API port $apiPort only on localhost — restart API window (must use --host 0.0.0.0)" -ForegroundColor Yellow }

Write-Host ""
Write-Host "Share with colleagues (same LAN/VPN):" -ForegroundColor Green
Write-Host "  http://${lanIp}:${uiPort}/"
if ($allIps.Count -gt 1) {
    Write-Host "  Or try other IPs above if primary fails."
}
Write-Host ""
Write-Host "If laptops cannot open the link:" -ForegroundColor Yellow
Write-Host "  1. Same office LAN or company VPN (WiFi guest often blocks peer access)"
Write-Host "  2. Colleague runs: ping $lanIp"
Write-Host "  3. Colleague runs: Test-NetConnection $lanIp -Port $uiPort"
Write-Host "  4. Or use Windows Mobile Hotspot on this PC, share WiFi, open http://192.168.137.1:${uiPort}/"
Write-Host ""
Write-Host "API health (optional): http://${lanIp}:${apiPort}/api/health"
Write-Host ""
Write-Host "Each user logs in with their own Jira account."
Write-Host "Set LOGWORK_QA_USERS on this machine before start for QA features."
Write-Host "Stop servers with Ctrl+C in both windows when done."
Write-Host ""
