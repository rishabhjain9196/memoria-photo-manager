# Changelog

## Unreleased

### Simpler duplicate comparison and explained Recovery totals
- Added Restore all available Recovery with a destination preview, explicit review of inferred unlogged paths
  and manual mapping for ambiguous groups. Conflicts offer Keep both, Leave in Recovery or Cancel, with exact-folder
  or all-remaining scope for the current restoration. Existing originals are never overwritten; no automatic
  emptying or unrelated export deletion is involved.
- Replaced the duplicate bulk-plan/keeper controls with a plain group list, two or three comparison panes, and a
  paged checkable table for four or more copies. Checked means move, unchecked means keep; recommendations are
  overridable. One Move selected to Recovery action affects only the current group.
- Subset comparisons select the smaller folder by default. Selecting the larger removes only verified shared
  content, never its unique files or containing folder; selecting both removes shared copies on both sides.
  Shared files attached to unique/unreviewed linked components are retained. Plans use reviewed file/directory
  snapshots and preserve source checks, metadata merging and Undo.
- Planned size includes linked components, and post-operation feedback states the bytes moved by that change.
  Kept groups remain remembered; cancellation preserves decisions. Quick remove still needs initial consent;
  subsets and linked components always confirm.
- Added read-only cumulative Recovery accounting: latest cleanup versus older retained content, per-root/per-change
  attribution, and untracked/ambiguous, missing, changed, interrupted or incomplete entries. Links/junctions are
  not followed. Inspect accounting and refresh do not create Recovery, read original media or delete anything.
- Uncertain accounting disables permanent emptying in the UI. Totals are logical measured bytes, not allocated
  disk space or space freed. This does not claim a diagnosis of a particular reported 56 GB without its local
  breakdown. No schema migration or cache reset is required.
- Full integrated suite: 445 passed, plus a seven-test production-style restoration-dialog check. Generated
  screenshots cover two/three/many-copy review, subset protection, accounting, restore preview and scoped conflict
  choices. Validation used generated files and 100k-entry metadata, never the user's real Recovery.

### Multi-folder organisation and responsive large-library views
- Added Library folders: keep the current catalogue home, register non-overlapping media roots, retain offline
  metadata/thumbnails and reconnect by source identity. Recovery stays on each source root; journal keys follow
  verified remapping. Existing standalone catalogues are not silently merged.
- Added reviewed same-folder/name companion groups for image/video parts, RAW+JPEG and AAE/XMP. Unique parts
  require explicit acknowledgement even in Quick remove. Compound preflight, shared collision names, rollback,
  cancellation and journaled Undo preserve linked parts; interruptions retain recoverable intents.
- Exact-duplicate removal merges useful catalogue organisation into keepers with undoable before/after snapshots.
  Tags/static albums/favourites combine; unset ratings/review states are filled and keepers win conflicts.
  Later manual edits and explicit resets cannot be overwritten by metadata Undo. Faces/health are not transferred.
- Added catalogue-only tags, 0-5 ratings, favourites and Unreviewed/Pick/Reject; combined organisation/root filters;
  persistent smart albums with editable rules and dynamic contents. Reject does not delete anything.
- Added Insights All files, immediately discoverable and largest-first: flat files across roots, metadata sorts,
  filters, organisation and existing Recovery/compressor actions. Recovery does not itself free space and compression
  still retains originals.
- Bounded/paged large album, group, plan, history, health and comparison views; asynchronous/coalesced media previews,
  editor/story work and compressor inputs. Stale results are rejected, shutdown is guarded, and selected live-index
  previews stay held until Update view. Full-plan group selections are labelled separately from page-scoped files.
- Schema v10 preserves existing IDs, analysis, keep decisions and history without a forced media re-analysis.
  The catalogue home remains required; companion links are filename-based, not Apple content-ID matching or edit
  rendering. Resource-adaptive processing and indexed similarity algorithms remain separate future work.
- Full integrated suite: 361 passed. Refreshed the quality report and generated-media UI screenshots, including
  Insights All files. Tests include 100,000-entry synthetic catalogues, delayed I/O, offline/reconnect scenarios,
  linked rollback/cancellation and metadata-conflict Undo; no real 300 GB media copy or drive benchmark was used.

### Apple sidecars and clearer analysis errors
- Apple .AAE edit sidecars are excluded from every Tidy up removal category, including empty files, and their
  folders remain protected from empty-folder cleanup. A protected-file count explains why they are not listed.
  Stale or manually supplied selections containing .AAE files are rejected with a visible message.
- Analysis errors no longer imply that a photo is damaged. Missing/unsupported codecs and access problems are
  explained, and Tidy's selected-file preview shows the escaped, selectable recorded error.
- HEIC/HEIF support already existed. Verified healthy HEIC and HEIF indexing/thumbnails, editing and rendering,
  unchanged originals, case-insensitive .AAE protection, cleanup/Undo and UI behavior with 11 targeted tests.
- No schema change or catalogue reset. This does not apply Apple's edit instructions, pair Live Photo components,
  or automatically retry/repair previously failing media.

### Suggest albums button
- Fixed the button passing Qt's checked-state flag as the album mode, which raised an error before a background
  task could start. It now uses the selected Events & trips, Places or People mode.
- Added real mouse-click regressions for all three modes, including visible results/empty states and unchanged
  original files. The end-to-end UI flow now clicks the button instead of calling the suggestion method directly.
- Extended that flow to click primary finder, preview, save, compression, cleanup and Undo buttons, requiring each
  background task to start and finish rather than accepting previously cached results as proof that a button worked.
- Verified with 14 album and end-to-end UI tests. No cache reset or library rescan is required.

### Direct duplicate removal and optional quick mode
- Remove 1 and Remove both/all now confirm and execute only the current group, instead of silently marking a bulk
  plan. The list refreshes afterwards; other marked groups are untouched. Keep both/all still saves a keep decision.
- Added Quick remove, off by default in every new library window. Enabling it requires one acknowledgement that
  Remove both/all can leave no shown copy in the library. Subsequent group actions skip confirmation popups, but still
  verify files, use Recovery/Undo and report changed files or failures. Bulk Apply and Empty Recovery still ask.
- Renamed plan-only controls to Use as bulk keeper, Bulk plan size and Apply marked groups to distinguish them from
  immediate group actions. Cancelling a group confirmation preserves its previous Keep choice.
- Fixed same-timestamp History ordering, which could make Undo last pick an earlier rapid action. New batches use
  microsecond timestamps, with insertion order breaking timestamp ties, including older records.
- Full regression suite: 240 passed. Refreshed the quality report and duplicate screenshots using generated test media,
  including direct/quick removal, actual list updates, Undo and rejection of changed files with unchanged size/mtime.
- No schema change, cache reset or media re-analysis is required.

### Video compressor opening freeze
- Replaced eager per-video table items and thumbnail icons with a virtual table model. Opening the page reads only
  the metadata needed for its columns; cached thumbnails are requested for visible rows rather than the whole library.
- Header sizing samples at most 50 rows. The complete video list and Select all semantics are preserved.
- Estimate probing has at most two outstanding requests to the existing single worker. Each completed probe updates
  only its row and incremental totals instead of recalculating the entire selection. Deselecting stops further queued work.
- Removed redundant selection-handoff reloads; external selections also work with an empty catalogue. Unavailable
  additions are reported, duplicate input paths are deduplicated, and late probe results are ignored after shutdown.
- Verified with 14 video/end-to-end UI tests, including 10,000 metadata-only video entries and real compression/Undo
  flows. In a local synthetic refresh check, 2,000 rows fell from 0.49 s to 0.03 s; 10,000 rows took 0.14 s and requested
  12 visible thumbnails. These are not real-library or drive throughput measurements. No schema change or reset.

### Explicit duplicate review choices
- Added Remove 1 (the selected copy/folder), Remove both/all shown copies, and Keep both/all for files and identical
  folder groups. Containing folders with unique files cannot both be removed.
- Remove both/all needs an explicit acknowledgement that no shown copy may remain in the library. It still uses
  per-file content/stat checks, Recovery and the existing Undo journal; normal cleanup retains survivor guards.
- Explicit all-folder removal uses reviewed file snapshots, never newly discovered contents. Changed files are
  skipped; folders are removed only when empty. Kept choices and other planned removals are respected across groups.
- Schema v7 remembers unchanged Keep both/all groups. Show previous choices reveals them without selecting them;
  new group members or detected changes invalidate the match. Removal choices are not automatically replayed.
- Safe rebuild preserves keep choices; a custom/hard reset can clear them with acknowledgement. No new media-analysis
  version or full re-analysis is required for an already-current catalogue.
- Selected-size/count summaries include explicit removals of every copy. A stale selection signal when the final
  duplicate group disappeared is now blocked while rebuilding the empty result list.
- Full regression suite: 234 passed. Refreshed the quality report and directly related duplicate/reset/safety screenshots
  using generated test media, without a large-library benchmark or access to original user photos.

### Offline map navigation and labels
- Wheel and pixel-only touchpad scrolling zoom immediately, including over map margins; zero-motion gesture
  events no longer zoom out. Added +/− buttons, keyboard zoom/arrow panning, and click-drag panning.
- Map navigation stays enabled while photo clusters refresh. View-only changes do not rerun storage, timeline or
  album queries; obsolete responses cannot reset a newer view. Dragging a marker does not open its photos.
- Reused bundled GeoNames data for country, city/town and accompanying state/region names, with zoom-dependent
  selection and collision-limited labels. Photo groups show approximate nearby place names, not street addresses.
- Cached vector paths avoid rebuilding every country outline for each interaction. Nearby-place lookup prefilters
  latitude without changing its distance/population ranking. No online tiles, GPS uploads, new dependencies or reset.
- Verified with 20 map, album/place and end-to-end UI regression tests; refreshed the map screenshots in both themes.

### Key-event notifications
- Desktop notifications default to background/minimised delivery; an active Memoria dialog/viewer counts as foreground.
- Sidebar Notifications offers per-device delivery/category settings and a bounded, in-memory recent-event list.
- Covers indexing/rebuild, analysis, cleanup/sync/export/compression, failures/skips, health problems and cancellation.
  Returned partial/cancelled batch results are classified separately from worker exceptions, without duplicate success messages.
- Desktop text uses fixed templates and optional counts, never paths, filenames, library names or raw error details.
  Existing Undo toasts and safety dialogs are unchanged. Clicking a message restores Memoria without applying actions.
- Unsupported desktops retain in-app events; Windows settings may suppress popups. Closing still exits and disarms
  notification delivery. No new dependency, catalogue migration, media scan or notification-history file.
- Notification/live-index/end-to-end UI regression run: 18 tests passed. Desktop routing uses a fake tray;
  actual Windows popup appearance/delivery is not asserted by the offscreen tests.

### Live browsing during indexing
- Photos & videos can browse completed catalogue entries before indexing finishes, including search, sort,
  paging and the viewer. Other utilities stay locked during active indexing.
- Analysis flushes at 200 results or approximately one-second intervals; UI refresh is throttled to two seconds.
- Analysis progress starts at zero for its own phase and updates on timed commits, avoiding stale "scan complete" progress.
- Selected previews, scrolled views and later pages are held until explicitly updated, preventing background jumps.
- Cancelling retains committed work; resume uses existing analysis. No schema change or full rebuild is required.

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
