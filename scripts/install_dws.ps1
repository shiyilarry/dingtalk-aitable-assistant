# ============================================================
# dws 安装脚本 (Windows PowerShell)
# 功能：安装 dingtalk-workspace-cli
# ============================================================

Write-Host "开始安装 dingtalk-workspace-cli ..." -ForegroundColor Cyan

# 首选方式：官方 install.ps1
try {
    Write-Host "尝试使用官方安装脚本..." -ForegroundColor Yellow
    irm https://raw.githubusercontent.com/DingTalk-Real-AI/dingtalk-workspace-cli/main/scripts/install.ps1 | iex
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: installed" -ForegroundColor Green
        # --- post-install: pull the newest release + dump authoritative schema ---
        $gate = Join-Path $PSScriptRoot "daily_upgrade_gate.ps1"
        if (Test-Path $gate) {
            Write-Host "post-install: checking for newer release ..." -ForegroundColor Cyan
            & powershell -ExecutionPolicy Bypass -File $gate -Force
            Write-Host "post-install: schema snapshot -> $env:USERPROFILE\.workbuddy\dws_schema_all.json" -ForegroundColor Cyan
        }
        exit 0
    }
} catch {
    Write-Host "官方脚本安装失败，尝试 npm 安装..." -ForegroundColor Yellow
}

# 备用方式：npm
try {
    npm install -g dingtalk-workspace-cli
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 通过 npm 安装成功" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "错误：npm 安装失败，请检查 Node.js 环境。" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "错误：安装过程异常 $_" -ForegroundColor Red
    exit 2
}