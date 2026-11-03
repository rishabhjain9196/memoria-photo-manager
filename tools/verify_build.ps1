# Smoke-test the packaged app: index a copy of the test library with the real exe and check the results.
#   .\tools\verify_build.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot)
$exe = "dist\Memoria\Memoria.exe"
if (-not (Test-Path $exe)) { throw "Build first: .\build.ps1" }
$data = "dist\Memoria\_internal\memoria"
foreach ($f in "engine\data\face_detection_yunet_2023mar.onnx", "engine\data\face_recognition_sface_2021dec.onnx",
               "engine\data\places.tsv.gz", "sample_faces\CREDITS.txt") {
    if (-not (Test-Path "$data\$f")) { throw "Missing from the build: $f" }
}
$report = Join-Path $env:TEMP "memoria-selftest.json"
Remove-Item $report -ErrorAction SilentlyContinue
$st = Start-Process -FilePath $exe -ArgumentList "--self-test", "`"$report`"" -PassThru -Wait
$result = if (Test-Path $report) { Get-Content $report -Raw } else { "no report" }
Remove-Item $report -ErrorAction SilentlyContinue
if ($st.ExitCode -ne 0) { throw "Packaged self-test failed: $result" }
Write-Host "Self-test (face models, places): $result"
$work = Join-Path $env:TEMP "memoria-verify"
Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue
& .\.venv\Scripts\python tools\make_test_library.py "$work\library" --small | Out-Null
$env:QT_QPA_PLATFORM = "offscreen"
$env:MEMORIA_PROFILE = "Memoria-Tools"
$p = Start-Process -FilePath $exe -ArgumentList "`"$work\library`"" -PassThru
Start-Sleep 20
$alive = -not $p.HasExited
if ($alive) { Stop-Process -Id $p.Id }
$check = @'
import sqlite3, sys, json
c = sqlite3.connect(sys.argv[1])
files, analysed, videos, heic, errors = c.execute(
    "select count(*), sum(analyzed), sum(kind='video' and duration>0), sum(ext='.heic' and width>0), "
    "sum(error is not null) from files").fetchone()
exp = json.load(open(sys.argv[2]))
ok = files == exp["total_files"] and analysed == files and videos >= len(exp["videos"]) and heic == len(exp["heic"]) \
    and errors == len(exp["corrupt"]) + len([f for f in exp["empty_files"] + exp["junk"] if f.lower().endswith((".jpg", ".jpeg", ".mp4"))])
print(f"files={files} analysed={analysed} videos={videos} heic={heic} errors={errors} -> {'OK' if ok else 'FAILED'}")
sys.exit(0 if ok else 1)
'@
$check | & .\.venv\Scripts\python - "$work\library\.memoria\memoria.db" "$work\library\expected.json"
if ($LASTEXITCODE -ne 0 -or -not $alive) { throw "Packaged app check failed (alive=$alive)" }
Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Packaged app verified."
