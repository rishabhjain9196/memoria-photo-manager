# Changelog

## Unreleased

### Local diagnostics
- Added opt-in, per-library/device recording of aggregate catalogue statistics and bounded timing metrics.
- Reports work from existing caches without rescanning media, and include periodic in-progress snapshots and
  app-process memory/CPU measurements. Previous unrecorded timings cannot be recovered.
- Aggregate JSON is written atomically inside the source checkout's diagnostics/reports folder for manual review
  and git sharing. No raw metadata, paths, coordinates, names, biometric vectors or file hashes are exported.
- Consent is stored locally, not in the repository. Disabling or switching libraries prevents stale reports from
  being published; write failures are visible and leave prior reports intact. No automatic uploads or git actions.

### Extended metadata
- Added ascending/descending video-duration, pixel-resolution, estimated overall bitrate and FPS sorting.
- Added codec, format, modified-date, camera/lens and EXIF ISO, aperture, exposure-time and focal-length sorting.
- Tabbed metadata filters combine numeric ranges, minimum dimensions, displayed orientation and exact camera/codecs;
  preview details and grid captions show units and distinguish missing metadata from zero/no audio.
- Schema v6 adds extended metadata with a per-file analysis version. A one-time resumable refresh preserves original
  files, IDs, albums, people, journal and health baselines; older retained rows refresh on return.
- Compression still uses bundled FFmpeg with CPU libx264/AAC; HandBrakeCLI has not been added.

### Documentation
- Updated the complete HTML documentation set and README for the current source, including safety limits,
  selective reset, insights, filters, paging, schema v6 and offline map attribution.
- Regenerated the quality report and screenshots from disposable test media; large media benchmarks are explicitly
  not rerun. Existing executable/package measurements are labelled historical rather than current build verification.

### Library insights
- Read-only folder/file-format storage bars, drilldown year/month/day counts with saved-album links,
  and an offline India-first/world GPS map with zoom and clustered markers.
- Chart clicks open matching files or albums; map coordinates never leave this computer.
- Photos support size/name/date sorting and combined folder, format, date, size, GPS and people filters.
- SQL-backed browsing is bounded to 500 rows per page; Ctrl+A and batch selection are page-scoped.
- Sidebar navigation scrolls on smaller windows; existing Ctrl+number shortcuts remain unchanged.
- Public-domain Natural Earth country outlines are bundled with attribution; no new runtime dependency.
- Album cleanup retains membership for missing files so a later return does not lose saved organisation.

### Storage & reset
- Sidebar controls offer a safe rebuild, selectable categories, and an acknowledged hard-reset preset.
- Original media, exported files, Recovery, stable file IDs and Undo history are always retained.
- Optional database compaction has a free-space check and can be skipped when resuming.
- Catalogue schema v5 records reset progress durably. Interrupted resets resume without repeating
  personal-data clearing; other library actions are paused until the rebuild completes.
- Tests cover abrupt process exit, rollback, cancellation, changed media, low space and the reset UI.

### Safety
- Copies record a fingerprint before publication; Undo refuses changed or unverified copies.
- Catalogue schema v4 prevents recycled IDs from being reassigned to newly imported files.
- Missing files and their metadata survive rescans and are shown in Health check.
- Temporary file-access failures retain catalogue entries and are reported.
- Interrupted moves reconcile catalogue state and History counts as well as file locations.
- Recovery deletion failures surface as errors instead of discarding recovery records.
- Editor, story and video output publication is journaled, including partial cancelled batches.
- Unavailable or unreadable backup folders cannot produce a successful comparison.

### Usability and resource use
- Analysis submission is bounded; decoded thumbnail pixels have a 64 MiB cache budget.
- Thumbnail caches refresh after library changes.
- Similarity no longer retains a Python set of every matching pair.
- Similar photo/video cleanup starts unticked; single-item selections show their action toolbar.
- Overview distinguishes Recovery from backup; Health check reports missing/unreadable problems
  rather than showing a misleading "No damage found" message.
- Low-disk tests cover synthetic large catalogues, migration, cancellation and filesystem failures.

## 1.4.0 — 2026-11-04

### Added
- **People.** Finds faces in photos and groups them by person, entirely offline, using two small open models run by
  OpenCV: YuNet (MIT) to find faces and SFace (Apache 2.0) for face signatures.
  - Name a group, join groups ("Same person as…" or by typing an existing name), and remove wrong faces ("Not this
    person"). Corrections are remembered.
  - "Find look-alikes" searches the whole library for faces like the selected one.
  - Hide strangers; make an album of someone's photos.
  - Named people can be searched in Photos & videos.
  - Scans are incremental, parallel and cancellable, with progress.
  - Face data is stored only in the library's catalogue; "Forget all face data" deletes it. Photos are never changed.
- **Albums.** Albums record which photos belong to them and never move or copy files.
  - Suggested from events and trips (a pause of 8 hours starts a new album; a trip in one place stays together for up
    to 3 days between photos), from places, or from named people.
  - Albums are named after the place and dates, e.g. "Leh, Ladakh · 10–12 Jun 2023". Place names come from a bundled
    offline list of towns (GeoNames, CC BY 4.0).
  - Rename, remove items, set a cover, delete. "Add to album…" in Photos & videos.
  - Export one album or all albums to folders with verified copies, which History can undo.
- Overview cards for People and Albums.
- Test library: public-domain portraits of Abraham Lincoln, Mark Twain and Nikola Tesla from Wikimedia Commons, with
  ground truth for People.
- Catalogue schema v3 (people, faces, albums). Opening a library upgrades it automatically.
- Packaged app self-test (`Memoria.exe --self-test report.json`), used by `tools\verify_build.ps1`.

### Changed
- Sidebar: People under Library; Albums under Organise. Ctrl+number shortcuts follow the new order.

## 1.3.0 — 2026-11-04

### Added
- **Duplicate folders.** Duplicates now finds whole folders whose files all exist in another folder — exactly the same
  files ("same"), or all of them inside a bigger folder ("inside"). Sub-folders are included, names and layout don't
  matter, and Thumbs.db-style leftovers and empty files are ignored.
  - Results are shown at the highest level: a copied tree appears once, as its top folder, with its duplicate size.
  - Every folder involved shows total size, number and size of photos, number and size of videos, other files and
    sub-folders, plus the files inside.
  - Choose which identical folder to keep. An original-looking folder inside a backup folder is listed but not ticked.
  - Single-file groups below only list copies that a duplicate folder doesn't already cover.
  - A folder moves to Recovery as a whole. Each file is checked against an identical copy that stays, and folders are
    removed only once empty. Undo restores the whole folder.
- Test library: a nested album copied whole to "Old Laptop" and a USB stick holding some camera photos.

## 1.2.0 — 2026-11-04

### Added
- **Editor** (sidebar › Create, or *Edit…* from Photos & videos): simple editing for photos and videos. Every edit is
  saved as a new file ("name (edited).jpg"), listed in History and removable with Undo. Originals are never changed.
  - Photos: rotate, mirror/flip, straighten, crop with handles and aspect presets (free, original, 1:1, 4:5, 9:16, 16:9, 3:2, 4:3),
    brightness, contrast, saturation, warmth, sharpness, auto enhance, filters, resize, format and quality with a size
    estimate, and an option to remove GPS location. Split into a grid; join side by side or stacked.
  - Videos: frame-accurate trim from the timeline, split at the playhead, into equal parts or every N seconds, join clips
    of different sizes, rotate, mirror/flip, crop, brightness/contrast/saturation, speed (0.5×–2×, audio keeps its
    pitch), mute, max resolution and quality, and save the current frame as a photo.
  - "Apply to all" saves the same edit for every photo (or video) in the list, with progress and a per-file failure report.
- History shows Editor changes; undoing removes the created files only if they are unchanged.

### Fixed
- History now selects the newest change when one arrives, so Undo there can't silently target an older change.

## 1.1.0 — 2026-11-03

### Added
- **Similar videos**: finds compressed, resized and slightly trimmed copies using 8-frame signatures, which are cached.
  The best copy is chosen by resolution, quality and length, and the reason is shown.
- **Check everything**: one read-only pass runs every finder. The results feed the pages and appear as count badges in
  the sidebar.
- **Batch actions** in Photos & videos: Move to Recovery, Copy to folder (verified), Move to folder in the library,
  Add to Story maker, Compress videos. All undoable.
- **Themes**: Light, Dark and Match Windows. Match Windows follows the system setting live.
- **Built-in viewer** (arrow keys), thumbnail zoom (slider and Ctrl+wheel), keyboard shortcuts, drag a folder onto the
  window to open it, and window size and position are remembered.
- **Progress for all processing**: the task bar shows a percentage, elapsed time and time left, and multi-step tasks
  show the current step. The sample library, Tidy, Organise and Empty Recovery now report progress too.
- Confirmation dialogs show thumbnails of the affected files.
- `tools/verify_build.ps1` checks the packaged app; `tests/test_safety.py` and `tests/test_batch.py` add regression tests.

### Fixed
- An unplugged drive or unreadable folder could remove catalogue rows, losing thumbnails and health fingerprints.
  The scan now stops and keeps them.
- Undo re-created catalogue rows, so files were re-analysed and lost their fingerprints. Rows are now parked and
  restored.
- Two Memoria windows could change the same library. A cross-process lock now prevents this.
- The catalogue had no schema version. Versioned migrations were added, and catalogues from a newer version are refused.
- Paths longer than 260 characters failed. They are now supported in every file operation.
- Preview's Open could launch non-media files such as `.exe` or `.lnk`. It now works only for photos and videos.
- Overview ran heavy checks on the UI thread. They now run in the background.
- UI tests and tools wrote to the user's real settings. They now use a separate profile.

### Performance (lossless only)
- Pages are created on first visit, so start-up is faster.
- Tidy and Organise planning moved off the UI thread.
- The packaged app is trimmed from 381 MB to 299 MB by removing components the app never loads.

## 1.0.0 — 2026-11-03

First release of the desktop app. It replaces the earlier `memoria` command-line tool.

### Added
- Windows desktop app (PySide6) with 11 pages: Overview, Photos & videos, Duplicates,
  Similar & best shots, Tidy up, Organise by date, Story maker, Video compressor,
  Health check, Compare & sync, History & recovery.
- Safety model enforced by one journaled executor:
  - every change follows Find → Review → Confirm → Apply → Undo;
  - "removed" files go to Recovery (nothing is deleted);
  - files are re-checked just before acting;
  - copies are verified byte for byte;
  - the journal is reconciled after a crash.
- Similar photos and bursts:
  - the best pick is chosen from sharpness, exposure, faces and resolution, with the reason shown;
  - a blurry-photo review.
- Story maker: stories in 6 layouts, carousels with a seamless panorama split, and story
  videos with Ken Burns motion, crossfades and music.
- Video compressor:
  - quality presets or a target size;
  - every copy must play, keep the same length and be smaller;
  - an SSIM quality score is reported.
- Health check: fingerprints, silent-damage detection and decode checks.
- Generated test library with ground truth (`expected.json`), 65 automated tests, an offscreen
  UI harness, benchmark, quality report and HTML documentation.

### Fixed (compared with the CLI)
- Files over 1.28 MB were skipped by duplicate removal and reported as corrupt by verify,
  because a sampled hash was compared against a full hash.
- Duplicate copies were not re-verified before being moved.
- Startup crashed on Windows when output was redirected.

### Removed
- Online reverse geocoding (privacy), CSV export and the reset command.
