# R24 — 0x90d/videoduplicatefinder

[Repository](<https://github.com/0x90d/videoduplicatefinder>) · 3,879 stars at the frozen snapshot · cleanup · Not archived

**Purpose:** Local image/video similarity scanner with desktop, CLI and LAN web interfaces, audio clip detection and optional neural matching for transformed or silent partial copies.

**Deployment:** Windows, Linux x64/ARM64 and macOS Intel/Apple Silicon desktop GUI; Self-contained CLI and web-server archives; Docker web image for linux/amd64 and linux/arm64

**Storage:** Scans existing paths, storing reusable fingerprints in ScannedFiles.db and optional dense visual embeddings in DenseEmbeddings.db. Database can live beside the executable or OS state directory; settings/auth live separately. Docker recommends separate persistent config/state volumes and read-only media mounts.

**Privacy/network behavior:** Classic and optional AI processing run locally; AI uses CPU ONNX/DINOv2 and downloads components once on enablement. FFmpeg may auto-download. Web access has a password but is explicitly for local/Docker use, not public Internet exposure.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v4.1.1 (2026-09-25T21:08:47Z)
**Repository pushed at:** 2026-10-09T16:42:03Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [4ab0e821e941](<https://github.com/0x90d/videoduplicatefinder/commit/4ab0e821e941acebffefcc18484e9e1ca406e6cb>).
**Product lineage:** 0x90d/videoduplicatefinder.

## Maturity and availability caveats

- Pinned master 4ab0e821e941acebffefcc18484e9e1ca406e6cb; stable v4.1.1 is built from 21ec967, so the pinned README/source may describe post-release changes.
- Rolling 4.1.x assets change on commits; numbered releases are immutable. Final classic UI remains in 4.0.x, with settings/database compatibility both ways.
- 3.x databases auto-migrate; image hashes recompute after moving image processing to FFmpeg, video hashes remain, and downgrade is not recommended.
- Speed, 50 ms/file and embedding footprint numbers are project claims, not reproduced measurements.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **CPU-local optional AI**<br>`ai.local_inference` | O | ONNX runtime/model download is about 100 MB once; model is checked against pinned SHA256. GUI asks before download; enabled CLI/web/Docker auto-download. No content is sent to a cloud AI account. | [R24-S1](<#r24-s1>) |
| **Multi-architecture Docker deployment**<br>`deployment.docker` | C | Web image bundles FFmpeg, supports amd64/arm64 and separates persistent settings/database from mounted media; numbered tags avoid rolling latest. | [R24-S1](<#r24-s1>) |
| **Translated desktop interface**<br>`deployment.localization` | C | GUI dynamically discovers bundled locale JSON files and reloads strings when CurrentLanguage changes; French menus, dialogs and result columns are explicitly translated. Default/load-failure fallback is English, while missing individual keys display the key. Localization parity for CLI/web is not inferred. | [R24-S5](<#r24-s5>), [R24-S6](<#r24-s6>) |
| **Local/LAN web interface**<br>`deployment.web` | C | Self-contained web server supports headless/NAS access, configurable listening port, generated or configured password and optional 30-day remember-me cookie. | [R24-S1](<#r24-s1>) |
| **Review AI-added groups**<br>`duplicates.ai_result_filter` | C | An AI filter retains groups containing an AI-only accepted member along with its comparison context; it is not an AI-only rescan. | [R24-S3](<#r24-s3>) |
| **Clip duration/audio/visual thresholds**<br>`duplicates.audio_clip_thresholds` | O | Audio clip mode defaults to minimum 10% clip/source duration, 80% audio similarity and 85% frame confirmation; the confirmation requirement is independently configurable. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Audio-based partial video detection**<br>`duplicates.audio_partial_clips` | O | A second phase uses chroma fingerprints and sliding-window Hamming similarity to find shorter clips within longer sources, reports a Clip Offset and defaults to visual confirmation at the offset. Both files need audio. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Classic algorithm and threshold controls**<br>`duplicates.configurable_similarity` | C | Choose grayscale percentage-difference or pHash, or combine both so either match qualifies. Controls include hash-difference threshold, minimum similarity and required fraction of matching sampled pHash frames. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Compare against prior/missing files**<br>`duplicates.database_comparison` | C | Settings can scan against the entire database and include non-existing files; tombstone mode also enables missing-file comparison. | [R24-S2](<#r24-s2>) |
| **Remember deleted content**<br>`duplicates.deleted_content_memory` | C | Optional RememberDeletedContent retains fingerprints when the last copy is deleted, so re-downloaded content can be recognized; database cleanup becomes tombstone-aware. This is not a general reviewed-pair ignore list. | [R24-S2](<#r24-s2>) |
| **Default action preview**<br>`duplicates.dry_run` | C | CLI action workflow defaults to dry-run and explicitly recommends reviewing before automatic deletion. | [R24-S1](<#r24-s1>) |
| **Duration candidate constraints**<br>`duplicates.duration_tolerance` | C | Configure percentage duration tolerance with minimum/maximum seconds bounds; with percentage disabled, seconds-only tolerance is supported. Maximum sampled duration is also configurable. | [R24-S2](<#r24-s2>) |
| **Path and filesystem exclusions**<br>`duplicates.exclude_paths` | C | Exclude directories, apply contains/not-contains path filters and optionally ignore read-only folders, reparse points or existing hard links. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Same/different-folder matching**<br>`duplicates.folder_relationship` | C | FolderMatchMode permits unrestricted, same-folder-only or different-folder-only matching with configurable same-folder depth. | [R24-S2](<#r24-s2>) |
| **Reusable scan database**<br>`duplicates.hash_cache` | C | Stores fingerprints for fast rescanning; optional embeddings are cached at roughly 2 KB/file, with dense keyframes in a separately cleaned sidecar at a claimed 25 KB/video. | [R24-S1](<#r24-s1>) |
| **Automatic quality/size keeper rules**<br>`duplicates.keeper_selection` | C | CLI can retain highest bitrate/resolution, largest file, longest duration or highest resolution per group. A 100-percent-only strategy acts only on fully matching reported groups; that label is not independently proven byte equality. | [R24-S1](<#r24-s1>) |
| **Neural transformed-copy detection**<br>`duplicates.neural_transformed_videos` | O | DINOv2 embeddings via ONNX add matches for cropped, mirrored, zoomed, letterboxed or heavily edited copies; classic results remain authoritative and are never hidden by enabling AI. Default threshold is 94%. | [R24-S1](<#r24-s1>) |
| **Hide resolved groups safely**<br>`duplicates.remaining_copy_filter` | C | Can hide groups with at most one remaining existing member; files on disconnected drives still count as offline rather than deleted. | [R24-S3](<#r24-s3>) |
| **Text/JSON/CSV reports**<br>`duplicates.report_export` | C | CLI writes selected text, JSON or CSV output to stdout or a named file and can load comprehensive JSON settings. | [R24-S1](<#r24-s1>) |
| **Similarity and selected-group filters**<br>`duplicates.result_similarity_filter` | C | Result filters support minimum/maximum similarity and groups with checked items. | [R24-S3](<#r24-s3>) |
| **Image similarity matching**<br>`duplicates.similar_images` | C | Image scanning is supported alongside videos; CLI --include-images is off by default, while the core settings default includes images. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Visual video duplicate matching**<br>`duplicates.similar_videos` | C | Finds related video content despite different resolution/frame rate and watermarks using sampled visual similarity rather than byte equality. | [R24-S1](<#r24-s1>) |
| **File-size restrictions**<br>`duplicates.size_bounds` | C | Core scan settings expose enabled minimum/maximum file-size filtering. | [R24-S2](<#r24-s2>) |
| **Silent/retimed clip matching**<br>`duplicates.visual_partial_clips` | O | Independent AI partial-detection switch compares dense keyframes by a consistent time offset; at least four hits must agree, default frame threshold 89%. Works without audio, including muted/re-dubbed clips. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Generated preview thumbnails**<br>`duplicates.visual_review` | C | Core settings expose generation of preview thumbnails with count and maximum width, supporting visual inspection of similarity results. | [R24-S2](<#r24-s2>) |
| **Flip/background matching controls**<br>`duplicates.visual_transform_controls` | C | Core settings expose horizontal-flip comparison and ignoring black/white pixels, distinct from optional neural transformed-copy detection. | [R24-S2](<#r24-s2>) |
| **Headless automation**<br>`integration.cli` | C | Separate scan/compare and combined CLI workflows are suitable for scripts and scheduled jobs without a display. | [R24-S1](<#r24-s1>) |
| **Multiple input directories**<br>`library.multiple_roots` | C | CLI accepts repeatable include directories and core settings control recursive scanning. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Periodic scan database saves**<br>`performance.database_checkpoints` | C | Automatic checkpoint interval defaults to five minutes; zero disables interval saves but retains phase-boundary saves. This is not a file-operation undo journal. | [R24-S2](<#r24-s2>) |
| **Optional native FFmpeg bindings**<br>`performance.native_ffmpeg` | O | Can call FFmpeg functions natively for claimed speed improvement; requires compatible FFmpeg 8.x shared libraries rather than master builds. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **Storage-aware hashing concurrency**<br>`performance.parallel_scan` | C | Separate read/hashing and CPU matching limits; slow/network drives default to a low per-drive cap while SSDs share the global budget. Automatic drive classification can be overridden. | [R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>) |
| **No mandatory content upload**<br>`privacy.no_upload_required` | C | All documented comparison occurs on the scanning machine, with optional model/runtime downloads but no cloud content-analysis service. | [R24-S1](<#r24-s1>) |
| **Trash instead of permanent removal**<br>`safety.os_trash` | C | CLI --delete moves selected duplicates to trash; permanent deletion requires the distinct --delete-permanent option. Platform/container trash availability is not fully detailed. | [R24-S1](<#r24-s1>) |
| **Read-only container media mounts**<br>`safety.read_only_originals` | O | Documented Docker examples and guidance recommend :ro media mounts for scan-only safety; deletion needs a writable configuration. | [R24-S1](<#r24-s1>) |
| **Result type filter**<br>`search.file_type` | C | GUI filters results to all, videos or images. | [R24-S3](<#r24-s3>) |
| **Group-aware path filtering**<br>`search.filename_path` | C | GUI path search is case-insensitive substring matching or unanchored * and ? wildcards; matching a member preserves the surrounding duplicate group. | [R24-S3](<#r24-s3>) |

## Limitations and evidence gaps

- **explicit:** Web UI is password-protected but explicitly not intended for public Internet exposure; authentication can be disabled by an environment variable. ([R24-S1](<#r24-s1>))
- **explicit:** Audio clip detection skips videos without audio; optional visual AI is a separate solution and can produce false positives at looser thresholds. ([R24-S1](<#r24-s1>))
- **explicit:** FFmpeg/FFprobe are required; optional native binding and AI have additional runtime/download requirements. ([R24-S1](<#r24-s1>))
- **explicit:** Automatic deletion is discouraged by the project. Perceptual/AI or reported 100% matching is not established as cryptographic whole-file identity. ([R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>))
- **coverage-gap:** Metadata editing, photo albums, face recognition, maps, playback integration, duplicate-link replacement and a general operation journal are not established by the inspected sources. ([R24-S1](<#r24-s1>), [R24-S2](<#r24-s2>), [R24-S3](<#r24-s3>))
- **Coverage gap:** Primary detailed user manual is embedded in README; source clarifies additional current-branch options.
- **Coverage gap:** Features from the pinned branch are not all asserted to ship in stable v4.1.1; no execution/performance tests performed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R24-S1

[README and user guides](<https://github.com/0x90d/videoduplicatefinder/blob/4ab0e821e941acebffefcc18484e9e1ca406e6cb/README.md>)
- Kind/ref: readme; 4ab0e821e941acebffefcc18484e9e1ca406e6cb
- Sections inspected: Complete README including clip/AI detection, desktop, CLI, web, Docker and migration notes
- Establishes: Detailed matching modes, automation actions, download/privacy requirements and deployment.

### R24-S2

[Core scanner settings](<https://github.com/0x90d/videoduplicatefinder/blob/4ab0e821e941acebffefcc18484e9e1ca406e6cb/VDF.Core/Settings.cs>)
- Kind/ref: code; 4ab0e821e941acebffefcc18484e9e1ca406e6cb
- Sections inspected: Entire file
- Establishes: Matching controls, deleted-content tombstones, storage-aware concurrency, filters and database checkpointing.

### R24-S3

[Result filters](<https://github.com/0x90d/videoduplicatefinder/blob/4ab0e821e941acebffefcc18484e9e1ca406e6cb/VDF.GUI/ViewModels/MainWindowVM_Filter.cs>)
- Kind/ref: code; 4ab0e821e941acebffefcc18484e9e1ca406e6cb
- Sections inspected: Entire file
- Establishes: Group-aware path, type, similarity, AI and already-deleted result filtering.

### R24-S4

[Stable 4.1.1 release](<https://github.com/0x90d/videoduplicatefinder/releases/tag/v4.1.1>)
- Kind/ref: release; v4.1.1
- Sections inspected: Complete release body
- Establishes: Immutable stable build and its exact underlying short commit, distinct from rolling build.

### R24-S5

[Desktop UI localization service](<https://github.com/0x90d/videoduplicatefinder/blob/4ab0e821e941acebffefcc18484e9e1ca406e6cb/VDF.GUI/LanguageService.cs>)
- Kind/ref: code; 4ab0e821e941acebffefcc18484e9e1ca406e6cb
- Sections inspected: Entire file
- Establishes: Discovers bundled locale assets, reloads translated UI values on language change and falls back to English if a locale cannot load.

### R24-S6

[French desktop UI translations](<https://github.com/0x90d/videoduplicatefinder/blob/4ab0e821e941acebffefcc18484e9e1ca406e6cb/VDF.GUI/Assets/Locales/fr.json>)
- Kind/ref: code; 4ab0e821e941acebffefcc18484e9e1ca406e6cb
- Sections inspected: App/About, quality-selection dialog, duplicate-list headers, blacklist manager and initial algorithm-choice translation groups
- Establishes: Actual French application menus, dialogs, result columns and help strings; not a translated README.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
