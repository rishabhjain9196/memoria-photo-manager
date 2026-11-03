# Build a standalone Windows app folder: dist\Memoria\Memoria.exe
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .venv\Scripts\python.exe)) { & .\run.ps1; exit }
$py = ".\.venv\Scripts\python.exe"
& $py tools\make_icon.py
& $py -m PyInstaller --noconfirm --clean --windowed --name Memoria `
    --icon memoria\ui\assets\memoria.ico `
    --add-data "memoria\ui\assets;memoria\ui\assets" `
    --collect-binaries imageio_ffmpeg `
    --collect-data cv2 `
    --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets `
    --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick --exclude-module PySide6.Qt3DCore `
    --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtPdf --exclude-module tkinter `
    --exclude-module pytest `
    Memoria.pyw
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
Write-Host "`nBuilt: $PSScriptRoot\dist\Memoria\Memoria.exe"
