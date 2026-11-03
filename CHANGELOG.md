# Changelog

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
