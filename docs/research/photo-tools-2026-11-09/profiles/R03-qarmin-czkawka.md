# R03 — qarmin/czkawka

[Repository](<https://github.com/qarmin/czkawka>) · 35,004 stars at the frozen snapshot · cleanup · Not archived

**Purpose:** Local file-cleanup toolkit with exact and perceptual duplicate scanning, media validation and corrective tools; Krokiet is the current desktop frontend and Czkawka GTK is legacy.

**Deployment:** Portable Windows, macOS and Linux desktop binaries; Command-line frontend; Reusable Rust core library; Cedinia Android frontend with different tool availability

**Storage:** Scans user-selected filesystem paths in place. Shared on-disk caches store content/perceptual hashes, media checks and thumbnails; JSON configuration holds presets. Deletion, links, moves, EXIF cleaning and video optimization act on real files rather than a managed photo catalogue.

**Privacy/network behavior:** README explicitly states no Internet access or user-statistics collection. Processing is local; external ffmpeg/ffprobe installations are needed for several video operations. This is not an encryption claim.

**License metadata:** NOASSERTION. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 12.0.2 (2026-09-09T19:48:14Z)
**Repository pushed at:** 2026-11-09T11:00:23Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [c8a690aa1f69](<https://github.com/qarmin/czkawka/commit/c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5>).
**Product lineage:** qarmin/czkawka.

## Maturity and availability caveats

- Frozen commit c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5; latest frozen release 12.0.2 (2026-09-09).
- GTK 12.0 is the last GTK release; new development and binaries target Krokiet. Current-commit manuals include newer capabilities and must not all be assumed available in 12.0.2.
- Cedinia has frontend-specific restrictions; README comparison and prose disagree about some Android audio/video availability, so desktop capabilities are not attributed wholesale to Android.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Interactive disk-usage charts**<br>`analytics.storage_distribution` | C | Treemap and sunburst views provide file-type toggles, folder drilldown, type detection choices and detail thresholds. Uses file sizes rather than allocated space, counts hardlinks per name and does not follow symlinks. | [R03-S3](<#r03-s3>) |
| **Immediate dark/light switching**<br>`browse.dark_theme` | C | Dark theme and UI language settings apply without restarting. | [R03-S3](<#r03-s3>) |
| **Keyboard-driven result review**<br>`browse.keyboard` | C | Arrow/page/home/end navigation, shift-range highlighting, Space check/uncheck, Enter open and Ctrl+A highlight are documented. | [R03-S3](<#r03-s3>) |
| **Detect and correct extension mismatches**<br>`cleanup.bad_extensions` | C | Magic-byte detection produces compatible-extension suggestions; Rename applies fixes and skips collisions with a warning. | [R03-S3](<#r03-s3>) |
| **Detect and repair problematic names**<br>`cleanup.bad_names` | C | Configurable rules cover uppercase extensions, emoji, edge whitespace, non-ASCII/transliteration, restricted character sets and repeated punctuation; results show proposed names and collision failures are reported. | [R03-S3](<#r03-s3>) |
| **Validate media and other files**<br>`cleanup.broken_media` | C | Parses images, audio, PDFs, archives, fonts and markup using type-specific libraries; errors are candidates for manual verification, not guaranteed corruption. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Find empty and content-empty files**<br>`cleanup.empty_files` | C | Finds zero-byte files, with extra checks for all-null content and non-visible-ASCII-only content; the latter can match non-Latin text, an explicit caution in the GUI manual. | [R03-S3](<#r03-s3>) |
| **Find recursively empty folder trees**<br>`cleanup.empty_folders` | C | Reports topmost all-empty branches. Excluded/unreadable folders, symlinks or entries on another filesystem prevent a directory being declared empty. | [R03-S3](<#r03-s3>) |
| **Find broken or cyclic symbolic links**<br>`cleanup.invalid_symlinks` | C | Flags nonexistent targets and excessive/circular link chains; deletion removes the link, not its target. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Find largest or smallest files**<br>`cleanup.large_files` | C | Returns configurable N biggest or smallest files, default 50, excluding zero-byte files. | [R03-S3](<#r03-s3>) |
| **Find configurable temporary artifacts**<br>`cleanup.temporary_junk` | C | Case-insensitive suffix matching includes download remnants, backups, cache/dump files and OS artifacts; users can replace/reset the suffix list. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Quick or full video validation**<br>`cleanup.video_validation` | O | Off-by-default ffprobe header checks and slow ffmpeg full-decode checks require external ffmpeg; videos are otherwise not checked by Broken Files. | [R03-S3](<#r03-s3>) |
| **Cedinia Android frontend**<br>`deployment.android` | C | Repository supplies a touch-oriented Cedinia frontend; its supported tools differ from Krokiet and GTK. | [R03-S1](<#r03-s1>), [R03-S4](<#r03-s4>) |
| **Linux desktop binaries**<br>`deployment.linux` | C | Krokiet supplies prebuilt Linux desktop executables; the manual documents glibc 2.17+ and optional ffmpeg requirements for relevant video tools. | [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **Translated desktop interface**<br>`deployment.localization` | C | README explicitly documents multiple interface languages including Polish, English and Italian. Krokiet's Language setting changes the UI immediately without restart; this is interface translation, not multilingual content search. | [R03-S1](<#r03-s1>), [R03-S3](<#r03-s3>) |
| **macOS desktop binaries**<br>`deployment.macos` | C | Release distribution includes Krokiet macOS x86_64 and ARM64 desktop builds; this is a native frontend, not a browser served from a container. | [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **Portable desktop binaries**<br>`deployment.portable` | C | Prebuilt Windows 10/11, macOS and Linux binaries require no installation; optional media builds/runtime dependencies remain separate. | [R03-S1](<#r03-s1>), [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **Windows desktop binaries**<br>`deployment.windows` | C | Krokiet has prebuilt portable Windows 10/11 desktop binaries; release notes distinguish current Krokiet from legacy GTK packages. | [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **Music tag and fingerprint matching**<br>`duplicates.audio` | C | Match selected title/artist/bitrate/genre/year/length tags, optionally approximate title/artist; alternatively compare content fingerprints with minimum matching segment and difference thresholds. Empty selected tags are not grouped. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Bytewise verification**<br>`duplicates.byte_compare` | N | Krokiet manual explicitly says hash duplicate matching does not perform byte-by-byte comparison. | [R03-S3](<#r03-s3>) |
| **Whole-file duplicate hashing**<br>`duplicates.exact_hash` | C | Groups by size, then first/last 4 KB prehash, then full-file hash. Blake3 is default; CRC32 and XXH3 are alternatives with different collision characteristics. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Exclude paths and patterns**<br>`duplicates.exclude_paths` | C | Excluded directories, whole-path glob patterns, include/exclude extensions and image/video/music/text extension groups restrict scans; default exclusions cover common system/cache locations. | [R03-S3](<#r03-s3>) |
| **Rotated and mirrored duplicate matching**<br>`duplicates.geometric_invariance` | C | Optional comparison setting adds mirror/flip and 90-degree rotation variants; changed invariance/hash/filter parameters create distinct cached signatures. | [R03-S3](<#r03-s3>) |
| **Replace selected duplicates with hard links**<br>`duplicates.hardlinks` | C | Group action keeps the reference or first checked file and links other checked members; requires at least two checked members without a reference. Applicable even to similar-media groups, so user judgment matters. | [R03-S3](<#r03-s3>) |
| **Shared signature caches**<br>`duplicates.hash_cache` | C | CLI and Krokiet share full/prehash, perceptual image/video, music and scan caches; binary caches have JSON fallback and optional JSON export, with image parameters in cache keys. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Leave groups unchanged**<br>`duplicates.keep_all` | C | Unselect-all or removing rows only from displayed results leaves files on disk; result hiding is not documented as a persistent review decision. | [R03-S3](<#r03-s3>) |
| **Group-aware keeper rules**<br>`duplicates.keeper_selection` | C | Select one or all except oldest/newest/biggest/smallest, shortest/longest path, and for images resolution; custom selection and group inversion are available. Highlighting and action checkboxes are deliberately distinct. | [R03-S3](<#r03-s3>) |
| **Name and size candidate matching**<br>`duplicates.metadata_candidates` | C | Name, size and combined name+size modes avoid content reads; case sensitivity is configurable and docs explicitly warn these methods produce false positives. | [R03-S3](<#r03-s3>) |
| **Protected reference folders**<br>`duplicates.reference_folders` | C | Ref paths participate as keeper references but are protected from selection/removal; all-reference scans are refused. Link actions target a group's reference file where present. | [R03-S3](<#r03-s3>) |
| **Allow every group member to be selected**<br>`duplicates.remove_all` | C | Select-all/inversion may check every member; deletion popup reports how many groups have every file checked rather than silently treating all actions as keep-one. | [R03-S3](<#r03-s3>) |
| **Export scan reports**<br>`duplicates.report_export` | C | Save creates text, pretty JSON and compact JSON files; results cannot be loaded back into the GUI. | [R03-S3](<#r03-s3>) |
| **Configurable perceptual image grouping**<br>`duplicates.similar_images` | C | BK-tree/Hamming-distance matching with six hash algorithms, 8/16/32/64 hash sizes, resize filters and distance threshold; optionally ignores same-size or same-resolution groups. EXIF orientation is applied before hashing. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Visual video and subclip matching**<br>`duplicates.similar_videos` | O | Requires ffmpeg/ffprobe. Compares perceptual frame sequences in temporal windows with duration tolerance, minimum matching-window fraction, letterbox detection and shorter-clip containment thresholds; presets include near-identical, similar and long-skip movie scans. | [R03-S3](<#r03-s3>) |
| **Bound scan file sizes**<br>`duplicates.size_bounds` | C | Global minimum/maximum size filters apply to appropriate tools; empty files, temporary files and largest/smallest scans explicitly ignore these bounds. | [R03-S3](<#r03-s3>) |
| **Replace selected duplicates with symbolic links**<br>`duplicates.symlinks` | C | Softlink action follows the same reference/first-checked keeper rule as hardlink; release notes explicitly mention surfacing rollback rename failures. | [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **Video audio-fingerprint matching**<br>`duplicates.video_audio_fingerprints` | C | Separate audio comparison mode uses similarity, shorter/longer duration ratio, minimum duration and maximum audio difference; Krokiet manual says this mode itself does not require ffmpeg, unlike visual hashing/thumbnails. | [R03-S3](<#r03-s3>) |
| **Preview and compare duplicate images**<br>`duplicates.visual_review` | C | Preview pane displays a highlighted image; Similar Images has a side-by-side Compare overlay. Video preview uses separately enabled thumbnails or thumbnail grids. | [R03-S3](<#r03-s3>) |
| **Hardware video encoding**<br>`editing.hardware_encoding` | O | Optimizer offers NVENC, VAAPI, QSV, VideoToolbox and AMF, contingent on ffmpeg and the platform encoder. | [R03-S3](<#r03-s3>) |
| **Detect static video borders**<br>`editing.video_auto_crop` | O | ffmpeg-backed optimization detects black bars or static edge content using thresholds/sample limits and applies the proposed crop to selected files. | [R03-S2](<#r03-s2>), [R03-S3](<#r03-s3>) |
| **Find and transcode inefficient videos**<br>`editing.video_transcode` | O | Requires ffmpeg; excludes configurable already-efficient codecs and offers target codec, CRF, denoising, frame-size/fps limits, fail-if-bigger, overwrite and custom commands. | [R03-S3](<#r03-s3>) |
| **AVIF similar-image decoding**<br>`formats.avif` | O | Requires the libavif build feature and associated libraries. | [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **HEIF/HEIC similar-image decoding**<br>`formats.heic` | O | Similar-image support requires a build with the heif feature and relevant system libraries; not inferred from EXIF-cleaning format support. | [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **JPEG XL similar-image scanning**<br>`formats.jpegxl` | C | JXL is listed among supported similar-image extensions in the current Krokiet manual. | [R03-S3](<#r03-s3>) |
| **RAW decoding for similar-image scans**<br>`formats.raw` | C | Current manual documents built-in rawler RAW decoding; optional libraw replaces the decoder rather than being mandatory. | [R03-S3](<#r03-s3>) |
| **Automatable CLI frontend**<br>`integration.cli` | C | Separate command-line frontend shares the core and caches; release 12.0.2 also adds starting a Krokiet scan through command-line arguments. | [R03-S1](<#r03-s1>), [R03-S3](<#r03-s3>), [R03-S4](<#r03-s4>) |
| **Embeddable scanning core**<br>`integration.rust_library` | C | UI-independent czkawka_core exposes scan configuration, typed results and shared functionality for other applications. | [R03-S1](<#r03-s1>), [R03-S2](<#r03-s2>) |
| **Persist scan configurations**<br>`integration.scan_presets` | C | Ten user presets save roots, filters and tool parameters, plus a reserved command-line-path slot; custom selection rules are separately persisted. | [R03-S3](<#r03-s3>) |
| **Move or copy checked files**<br>`library.move_copy` | C | Move popup can copy instead, preserve folder structure and either skip conflicts or rename to avoid them. | [R03-S3](<#r03-s3>) |
| **Scan multiple filesystem roots**<br>`library.multiple_roots` | C | Included paths accepts multiple directories with recursive traversal and optional other-filesystem exclusion; scans operate on existing files without import. | [R03-S3](<#r03-s3>) |
| **Notify on scan completion**<br>`maintenance.notifications` | C | General settings include completion sound and desktop notification switches. | [R03-S3](<#r03-s3>) |
| **Clean stale scan caches**<br>`maintenance.selective_reset` | C | Automatic stale-record cleanup and a manual Clean outdated cache action remove entries for changed/missing files; separate global and per-preset settings are stored as JSON. | [R03-S3](<#r03-s3>) |
| **Selective EXIF removal**<br>`metadata.strip` | C | Finds metadata-bearing images and strips non-ignored tags; default preserved tag is Orientation. Cleaning supports library-dependent JPEG/PNG/TIFF/WebP/JXL/HEIF formats and creates a named cleaned copy unless overwrite is enabled. | [R03-S3](<#r03-s3>) |
| **Stop active scans**<br>`performance.cancel` | C | Action bar switches between Scan and Stop during work. | [R03-S3](<#r03-s3>) |
| **Configurable multithreading**<br>`performance.parallel_scan` | C | Thread count can be set, with zero meaning all CPU threads; changing it requires restart. Speed claims are project claims, not tested benchmarks. | [R03-S1](<#r03-s1>), [R03-S3](<#r03-s3>) |
| **Reusable video thumbnails**<br>`performance.thumbnail_cache` | O | With ffmpeg, generate a single position-based thumbnail or tiled grid; CLI pre-scanning populates GUI cache, and unused thumbnails older than seven days can be cleaned at startup. | [R03-S3](<#r03-s3>) |
| **Local operation without telemetry**<br>`privacy.offline_use` | C | README explicitly states no Internet access and no collection of user information/statistics. | [R03-S1](<#r03-s1>) |
| **Review destructive selections**<br>`safety.confirmation` | C | Checkboxes determine actions independently of highlighted preview rows, and delete popup flags groups with all members selected; reference rows are protected. | [R03-S3](<#r03-s3>) |
| **EXIF-cleaned copies by default**<br>`safety.nondestructive_edits` | C | EXIF cleaning defaults to writing a .czkawka_cleaned_exif copy; overwrite is an explicit popup option. | [R03-S3](<#r03-s3>) |
| **Use system trash**<br>`safety.os_trash` | C | Separate Trash action for checked scan results is recoverable through the OS, while Delete is permanent; trash may fail on network shares. Disk-usage chart's similarly named action is explicitly not functional. | [R03-S3](<#r03-s3>) |

## Limitations and evidence gaps

- **explicit:** Current-branch capabilities are not a guarantee of inclusion in frozen release 12.0.2; GTK is discontinued as a released frontend. ([R03-S1](<#r03-s1>), [R03-S4](<#r03-s4>))
- **explicit:** Disk Usage's Move to trash currently only hides a chart item; it does not move the underlying file to trash. ([R03-S3](<#r03-s3>))
- **explicit:** Similar-image scanning excludes GIF and ICO; HEIC/AVIF depend on build features. Broken-file results can be false positives. ([R03-S3](<#r03-s3>))
- **coverage-gap:** Saved result reports cannot be reloaded. No durable undo journal, persistent duplicate-review decisions, encrypted vault or photo-library AI is established by inspected documentation. ([R03-S3](<#r03-s3>))
- **explicit:** Hash-cache minimum-size UI is labelled KB although current core comparison uses bytes, according to the manual. Settings other than immediate preset actions are saved only on normal exit. ([R03-S3](<#r03-s3>))
- **Coverage gap:** No evidence of catalogue-style face recognition, maps or sharing; not the toolkit's documented focus.
- **Coverage gap:** Android tool availability is not fully reconciled across README statements.
- **Coverage gap:** Inventory is pinned-current documentation, not a feature-by-feature verification of the older release.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R03-S1

[Project README](<https://github.com/qarmin/czkawka/blob/c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5/README.md>)
- Kind/ref: readme; c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5
- Sections inspected: Features; frontend descriptions; comparison; supported projects; licenses
- Establishes: Toolkit scope, local privacy statement, platforms and GTK succession.

### R03-S2

[Czkawka Core library guide](<https://github.com/qarmin/czkawka/blob/c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5/instructions/Instruction_Core.md>)
- Kind/ref: manual; c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5
- Sections inspected: Complete Tools and Cache sections; common scan configuration
- Establishes: Algorithm distinctions, hash choices, media checker formats, transformations and cache design.

### R03-S3

[Krokiet instructions](<https://github.com/qarmin/czkawka/blob/c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5/instructions/Instruction_Krokiet.md>)
- Kind/ref: manual; c8a690aa1f692a48b52f6ad1e3c7f7227dac53a5
- Sections inspected: Complete manual
- Establishes: User-facing selection, scan filters, safety, image/video settings, disk usage and configuration behavior.

### R03-S4

[12.0.2 release notes](<https://github.com/qarmin/czkawka/releases/tag/12.0.2>)
- Kind/ref: release; 12.0.2
- Sections inspected: Deprecation; Core; CLI; Krokiet; binary legend
- Establishes: Released frontend transition, link rollback error handling and distribution requirements.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
