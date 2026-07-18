
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "FAIL: Python was not found on PATH." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting Project Foreman..." -ForegroundColor Cyan
python -m project_foreman
