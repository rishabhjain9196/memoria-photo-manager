# Local diagnostic reports

On the photo device, run Memoria from this source checkout and open **Diagnostics** in the sidebar.
Enable recording for the current library. Consent is saved in that device's local application settings,
not in git. Recording is off by default for other libraries/devices.

An already-scanned library works: the report reads its existing SQLite catalogue without rescanning
media or resetting anything. It cannot reconstruct old timings. Enable recording before running
finders, browsing or editing; a normal F5 rescan can measure warm-cache performance.

Reports are automatically updated under `diagnostics/reports/report-<random>.json` after main tasks,
about once a minute while recording, and when closing normally. Each library opened in an app session
gets a separate randomly named report. An interrupted write leaves the previous complete report intact.
Previous recording sessions' reports are retained; there is no automatic commit, upload or deletion.
Browsing/preview timings accumulate in memory between snapshots, rather than querying the whole catalogue after
every click. **Refresh report** takes an on-demand snapshot. Collection adds some overhead and is not a benchmark.

## What is included

- Aggregate file counts/bytes, allowlisted formats and codecs, coarse size/resolution/video duration,
  frame-rate and estimated-bitrate distributions.
- Metadata coverage and record counts, including missing/recovered records and face-analysis counts.
- Fixed error categories and journal outcome counts; no raw messages.
- Operation timing totals, means/maxima, completion/failure/cancellation counters and an in-progress
  main-task snapshot. CPU/memory measure the app process, not FFmpeg child processes. CPU deltas can overlap with
  UI/background work; these are diagnostics, not isolated encoder benchmarks.
- App/schema/Python/Windows versions, local git HEAD when available, CPU count, physical RAM,
  process working-set/peak memory and coarse disk capacity/free space.
  Drive categories do not distinguish SSDs from hard disks; git HEAD does not identify uncommitted source changes.

## What is excluded

Photos/thumbnails, filenames and paths, actual capture dates, GPS coordinates, camera/lens/person/album
names, face vectors, hashes of file content, hostnames, usernames, drive letters/serials and raw error traces.
Unknown formats/codecs and error messages map to fixed categories rather than being copied into reports.

Aggregates are **not guaranteed anonymous**: counts and system information still describe your collection
and computer. Review the JSON in the app or editor before sharing. Disable recording before committing
so the file does not keep changing while you review it. Turning recording off or resetting a library does
not erase previously written reports or git history.

## Share deliberately

From the repository root, after reviewing the reports:

```powershell
git add diagnostics\reports
git diff --cached -- diagnostics\reports
git commit -m "Add reviewed library diagnostics"
git push
```

Stage only reports you intend to share, not the catalogue (`.memoria`) or raw logs. Do not copy your
photo library into the repository. Reports may be incomplete while indexing, after interruption, or
if the catalogue/checkout is unavailable. The UI reports write failures and preserves previous reports.
