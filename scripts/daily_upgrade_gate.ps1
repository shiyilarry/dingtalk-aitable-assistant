# dingtalk-aitable-assistant :: daily dws upgrade gate  (ASCII-safe, PowerShell 5.1)
# Purpose: keep dws CLI fresh WITHOUT user involvement.
#   - runs at most once per calendar day (stamp file in %USERPROFILE%\.workbuddy)
#   - checks for a newer release, upgrades silently, records version + writes a log
# Usage : powershell -ExecutionPolicy Bypass -File daily_upgrade_gate.ps1 [-Force]
# Exit  : 0 = up-to-date (no action)      10 = upgraded
#         2 = dws missing                 3 = upgrade command failed
#         4 = offline / check failed (non-fatal, continue with current version)
param([switch]$Force)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$stampDir  = Join-Path $env:USERPROFILE ".workbuddy"
if (-not (Test-Path $stampDir)) { New-Item -ItemType Directory -Path $stampDir -Force | Out-Null }
$stampFile = Join-Path $stampDir ".dws_daily_upgrade"
$logFile   = Join-Path $stampDir "dws_upgrade.log"
$today     = (Get-Date).ToString("yyyy-MM-dd")

# ---------- 0. dws present? ----------
$cmd = Get-Command dws -ErrorAction SilentlyContinue
$dws = if ($cmd) { "dws" } else { $null }
if (-not $dws) {
  $guess = Join-Path $env:APPDATA "npm\dws.cmd"
  if (Test-Path $guess) { $dws = $guess }
}
if (-not $dws) { Write-Host "ERR: dws not found; run install_dws.ps1"; exit 2 }

function Get-DwsVersion {
  try { return (& $dws version --format json 2>$null | Out-String).Trim() } catch { return "" }
}

# ---------- 1. already done today? ----------
$stampVer = ""
if (Test-Path $stampFile) {
  $line = (Get-Content $stampFile -TotalCount 1)
  if ($line -match "^(\d{4}-\d{2}-\d{2})\|(.*)$") {
    if ($matches[1] -eq $today -and -not $Force) {
      Write-Host "SKIP: already checked today ($today), version=$($matches[2])"
      exit 0
    }
    $stampVer = $matches[2]
  }
}

$before = Get-DwsVersion
Write-Host "[gate] date=$today  force=$Force"
Write-Host "[gate] current version: $before"

# ---------- 2. is there a newer release? ----------
$checkOut = ""
try { $checkOut = (& $dws upgrade --check --format json 2>&1 | Out-String).Trim() }
catch { $checkOut = "" }
Write-Host "[gate] check: $checkOut"

$hasNew = $false
if ($checkOut -match '"?(latest|latestVersion|newVersion)"?\s*[:=]\s*"?([0-9]+\.[0-9]+\.[0-9]+)') { $latest = $matches[2] }
elseif ($checkOut -match '([0-9]+\.[0-9]+\.[0-9]+)')                                    { $latest = $matches[1] }
else { $latest = "" }

if ($checkOut -match "up.?to.?date|no.?update|latest.?is") { $hasNew = $false }
elseif ($latest -and $before -and ($before -notmatch [regex]::Escape($latest))) { $hasNew = $true }
elseif ($latest -and -not $before) { $hasNew = $true }

if (-not $hasNew) {
  "$today|$before|no-update" | Set-Content -Path $stampFile -Encoding UTF8
  Add-Content -Path $logFile -Value "$(Get-Date -Format s) no-update  ver=$before  check=$checkOut"
  Write-Host "OK: already latest ($before)"
  exit 0
}

# ---------- 3. upgrade ----------
Write-Host "[gate] upgrading to $latest ..."
$upOut = ""
try { $upOut = (& $dws upgrade -y 2>&1 | Out-String).Trim() }
catch { $upOut = "EXCEPTION: $($_.Exception.Message)" }
Write-Host $upOut

$after = Get-DwsVersion
$ok = ($after -and ($after -ne $before)) -or ($upOut -match "success|upgraded|installed|complete")

if ($ok) {
  "$today|$after|upgraded-from:$before" | Set-Content -Path $stampFile -Encoding UTF8
  Add-Content -Path $logFile -Value "$(Get-Date -Format s) UPGRADED $before -> $after"
  # dump the authoritative command surface for the new version
  try { & $dws schema --all -f json > (Join-Path $stampDir "dws_schema_all.json") 2>$null } catch {}
  Write-Host "DONE: $before -> $after"
  exit 10
} else {
  "$today|$before|check-failed" | Set-Content -Path $stampFile -Encoding UTF8
  Add-Content -Path $logFile -Value "$(Get-Date -Format s) FAILED  ver=$before  out=$upOut"
  Write-Host "WARN: upgrade not confirmed; keep using $before"
  exit 3
}
