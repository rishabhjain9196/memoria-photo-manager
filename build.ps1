# Build a standalone Windows app folder: dist\Memoria\Memoria.exe
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .venv\Scripts\python.exe)) { & .\run.ps1; exit }
$py = ".\.venv\Scripts\python.exe"
& $py tools\make_icon.py
& $py -m PyInstaller --noconfirm --clean --windowed --name Memoria `
    --icon memoria\ui\assets\memoria.ico `
    --add-data "memoria\ui\assets;memoria\ui\assets" `
    --add-data "memoria\engine\data;memoria\engine\data" `
    --add-data "memoria\sample_faces;memoria\sample_faces" `
    --collect-binaries imageio_ffmpeg `
    --collect-data cv2 `
    --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets `
    --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick --exclude-module PySide6.Qt3DCore `
    --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtPdf --exclude-module tkinter `
    --exclude-module pytest `
    Memoria.pyw
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

# Remove bundled parts Memoria never loads (verified by tools\verify_build.ps1):
#  - OpenCV's VideoCapture FFmpeg backend (Memoria uses its own FFmpeg)
#  - Qt's software OpenGL fallback (the app uses plain widgets, no OpenGL)
#  - Qt Quick/QML/PDF libraries and the plugins that depend on them
#  - Haar cascades other than the frontal-face model used for best-shot scoring
$int = "dist\Memoria\_internal"
$prune = @(
    "$int\cv2\opencv_videoio_ffmpeg*.dll",
    "$int\PySide6\opengl32sw.dll",
    "$int\PySide6\Qt6Quick*.dll", "$int\PySide6\Qt6Qml*.dll", "$int\PySide6\Qt6Pdf*.dll",
    "$int\PySide6\Qt6VirtualKeyboard*.dll",
    "$int\PySide6\plugins\imageformats\qpdf.dll",
    "$int\PySide6\plugins\platforminputcontexts\qtvirtualkeyboardplugin.dll",
    "$int\PySide6\translations"
)
$before = (Get-ChildItem dist\Memoria -Recurse -File | Measure-Object Length -Sum).Sum
foreach ($p in $prune) { Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue }
Get-ChildItem "$int\cv2\data" -Filter *.xml -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne "haarcascade_frontalface_default.xml" } | Remove-Item -Force
$after = (Get-ChildItem dist\Memoria -Recurse -File | Measure-Object Length -Sum).Sum
Write-Host ("Trimmed {0:N0} MB → {1:N0} MB" -f ($before / 1MB), ($after / 1MB))
Write-Host "`nBuilt: $PSScriptRoot\dist\Memoria\Memoria.exe"
