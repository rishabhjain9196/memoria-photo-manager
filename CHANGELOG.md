# Changelog

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
