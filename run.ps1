# Set up (first run only) and start Memoria.
#   .\run.ps1                 start the app
#   .\run.ps1 "D:\Photos"     open a specific library
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .venv\Scripts\python.exe)) {
    Write-Host "First run: creating .venv and installing dependencies..."
    python -m venv .venv
    .\.venv\Scripts\python -m pip install --upgrade pip -q
    .\.venv\Scripts\python -m pip install -r requirements.txt -q
}
& .\.venv\Scripts\pythonw.exe Memoria.pyw @args
