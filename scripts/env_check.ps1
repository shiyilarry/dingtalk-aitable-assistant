# dingtalk-aitable-assistant env check (Windows PowerShell, ASCII-safe)
# Usage: powershell -ExecutionPolicy Bypass -File env_check.ps1
# Exit: 0=ready 1=not-win 2=dws-missing 3=install-failed 4=not-logged 5=api-fail
$ErrorActionPreference = "Continue"
Write-Host "[env] OS check"
$os = [System.Environment]::OSVersion.Platform
if ($os -ne "Win32NT") { Write-Host "ERR: Windows only"; exit 1 }
Write-Host "[env] dws check"
$cmd = Get-Command dws -ErrorAction SilentlyContinue
if (-not $cmd) {
  Write-Host "WARN: dws not found. Run install_dws.ps1 first, then rerun."
  exit 2
}
Write-Host "[env] dws version:"
dws version --format json
Write-Host "[env] auth check"
dws auth status --format json
if ($LASTEXITCODE -ne 0) { Write-Host "ERR: not logged in. Run: dws auth login (or --device)"; exit 4 }
Write-Host "[env] api smoke"
dws aitable base list --limit 1 --format json
if ($LASTEXITCODE -ne 0) { Write-Host "ERR: api call failed"; exit 5 }
Write-Host "[env] OK"
exit 0
