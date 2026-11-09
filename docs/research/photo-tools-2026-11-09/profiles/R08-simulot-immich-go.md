# R08 — simulot/immich-go

[Repository](<https://github.com/simulot/immich-go>) · 7,170 stars at the frozen snapshot · library-utility · Not archived

**Purpose:** Cross-platform bulk uploader, migration, archive and stacking CLI for Immich, with detailed Google/iCloud/Picasa metadata reconstruction.

**Deployment:** Standalone Windows, macOS, Linux and FreeBSD binaries; CLI with interactive terminal status or headless mode

**Storage:** Reads folders, ZIP archives or remote Immich assets and uploads to an Immich server; archive mode instead writes ordinary year/year-month folders with original files, JSON metadata and preserved XMP sidecars. It is not a standalone browsable photo catalogue.

**Privacy/network behavior:** Local sources can be organized into a local archive; uploads and server migrations transfer media and metadata to configured Immich API endpoints using API keys. Disabling TLS verification is offered but weakens transport verification. People names are imported metadata, not on-device face recognition.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v0.32.0 (2026-06-25T10:42:00Z)
**Repository pushed at:** 2026-11-07T08:52:38Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [bc54ad2485b3](<https://github.com/simulot/immich-go/commit/bc54ad2485b3e9c9b7c751445a28083950ffec60>).
**Product lineage:** simulot/immich-go.

## Maturity and availability caveats

- Frozen commit bc54ad2485b3e9c9b7c751445a28083950ffec60; latest release v0.32.0 (2026-06-25).
- README warns this is an early, not extensively tested tool and recommends retaining backups.
- v0.32.0 supports Immich V2/V3 and removes ReplaceAsset. Older upload reference still lists overwrite behavior; exact replacement semantics need version-specific verification.
- Claim of handling 100,000+ photos is from the project, not an independent benchmark.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Create albums from folders**<br>`albums.folder_mapping` | C | FOLDER or full PATH naming with customizable path joiner; alternatively put all media into one specified album or preserve Google/Picasa/iCloud associations. | [R08-S2](<#r08-s2>) |
| **FreeBSD command-line binary**<br>`deployment.freebsd` | C | README explicitly includes FreeBSD among the supported standalone executable platforms. | [R08-S1](<#r08-s1>) |
| **Linux command-line binary**<br>`deployment.linux` | C | Standalone Linux executable is documented; connects to a separate Immich server for upload/server operations rather than providing its own gallery. | [R08-S1](<#r08-s1>) |
| **macOS command-line binary**<br>`deployment.macos` | C | Standalone macOS executable distribution is documented for the upload/archive CLI; no desktop photo-browser UI is implied. | [R08-S1](<#r08-s1>) |
| **Windows command-line binary**<br>`deployment.windows` | C | README documents a standalone Windows release binary without NodeJS or Docker; this is the uploader/archive CLI, not a native desktop gallery. | [R08-S1](<#r08-s1>) |
| **Preview upload or stack effects**<br>`duplicates.dry_run` | C | --dry-run simulates upload transfers or stack mutations; recommended before keep-only stack operations. | [R08-S2](<#r08-s2>), [R08-S5](<#r08-s5>) |
| **Skip unwanted files and folders**<br>`duplicates.exclude_paths` | C | --ban-file distinguishes directory patterns by trailing slash; defaults exclude NAS thumbnail trees, Lightroom catalogues, OS artifacts and iCloud Recently Deleted. | [R08-S1](<#r08-s1>), [R08-S3](<#r08-s3>) |
| **Manage HEIC+JPEG companions**<br>`formats.heic_jpeg_pairs` | C | Offers separate, keep-HEIC, keep-JPEG and either-cover stacking modes based on matching basenames; this is not by itself proof of Live Photo video pairing. | [R08-S2](<#r08-s2>), [R08-S3](<#r08-s3>), [R08-S5](<#r08-s5>) |
| **Manage RAW+JPEG companions**<br>`formats.raw_jpeg_pairs` | C | Pairs same-basename assets using directory/time/size heuristics; can leave separate, keep only one type, or stack with RAW/JPEG chosen as cover. Existing-server keep-only modes delete the other type. | [R08-S2](<#r08-s2>), [R08-S3](<#r08-s3>), [R08-S5](<#r08-s5>) |
| **Standalone automation CLI**<br>`integration.cli` | C | Prebuilt cross-platform command-line program exposes upload, archive and stack operations without a NodeJS runtime. | [R08-S1](<#r08-s1>), [R08-S4](<#r08-s4>), [R08-S5](<#r08-s5>) |
| **Adapt to Immich V2/V3 APIs**<br>`integration.version_adaptive_api` | C | v0.32.0 detects server version and adapts errors/API behavior; album assets are retrieved through paginated metadata search for large collections. | [R08-S6](<#r08-s6>) |
| **Chronological archive layout**<br>`library.auto_date_folders` | C | Writes year/year-month folders while retaining original filenames where possible; archive destination is not wiped before an update. | [R08-S3](<#r08-s3>), [R08-S4](<#r08-s4>) |
| **Group photo bursts**<br>`library.burst_stacking` | C | Uses device filename patterns for Huawei/Pixel/Samsung/Sony/Nexus/Nothing and a 900 ms temporal rule; modes include stack and RAW/JPEG preference. Docs warn rapid unrelated photos may be grouped. | [R08-S3](<#r08-s3>), [R08-S5](<#r08-s5>) |
| **Skip already uploaded assets**<br>`library.deduplicate_import` | C | Technical guide describes SHA-1 content checksums combined with server metadata and size checks to avoid redundant uploads; no perceptual similarity matching is established. | [R08-S3](<#r08-s3>) |
| **Archive media from all input sources**<br>`library.export_originals` | C | archive supports folders/ZIPs, Google, iCloud, Picasa and Immich inputs, writing local media rather than requiring a destination server. | [R08-S4](<#r08-s4>) |
| **Import iCloud exports**<br>`library.icloud_export_import` | C | Reads iCloud export CSV metadata for dates and organization; optional --memories turns memories into albums. This is export ingestion, not documented live iCloud synchronization. | [R08-S1](<#r08-s1>), [R08-S2](<#r08-s2>) |
| **Folder and ZIP bulk uploads**<br>`library.import_copy` | C | Uploads images/videos recursively from local directories or ZIP files with optional headless operation; no NodeJS or Docker installation is required for the CLI itself. | [R08-S1](<#r08-s1>), [R08-S2](<#r08-s2>) |
| **Incrementally update archives**<br>`library.incremental_scan` | C | Adds new files, checks changed existing files and refreshes sidecars from current server state; archive operation does not propagate deletions. | [R08-S3](<#r08-s3>), [R08-S4](<#r08-s4>) |
| **Reconstruct Picasa albums**<br>`library.picasa_import` | C | from-picasa automatically reads .picasa.ini, and folder ingestion can enable the same album-name processing. | [R08-S1](<#r08-s1>), [R08-S2](<#r08-s2>) |
| **Replace existing server media**<br>`library.replace_existing_asset` | ? | Upload manual lists --overwrite, but v0.32.0 removes ReplaceAsset and its permission; exact surviving replacement behavior is not established by these conflicting docs. | [R08-S2](<#r08-s2>), [R08-S6](<#r08-s6>) |
| **Organize existing server assets**<br>`library.retroactive_stacking` | C | stack operates on existing Immich assets without uploading media, using the same burst/pair/scanner rules and an optional timezone override. | [R08-S5](<#r08-s5>) |
| **Epson FastFoto front/back grouping**<br>`library.scanner_stacking` | C | Groups original, _a corrected and _b reverse-side scans with corrected image as stack cover. | [R08-S3](<#r08-s3>), [R08-S5](<#r08-s5>) |
| **Immich-to-Immich transfer**<br>`library.server_migration` | C | Source and destination have separate server/API credentials and timeout/TLS settings; filters include dates, archived/trash state, favorites and minimum rating. | [R08-S2](<#r08-s2>) |
| **Google Takeout reconstruction**<br>`library.takeout_import` | C | Matches media with Google JSON and restores albums, descriptions, dates, locations and status flags. All split archive parts should be supplied together; unmatched media is excluded unless enabled. | [R08-S1](<#r08-s1>), [R08-S2](<#r08-s2>), [R08-S3](<#r08-s3>) |
| **Selective Takeout import**<br>`library.takeout_selection` | C | Archived and partner photos default to included; trashed, unmatched and untitled-album inclusion are separate switches. Can select an album and group partner photos into a named album. | [R08-S2](<#r08-s2>) |
| **API traces and terminal progress**<br>`maintenance.diagnostics` | C | Interactive terminal UI can be disabled; API tracing and log level/file controls support diagnosing upload and stacking operations. | [R08-S2](<#r08-s2>), [R08-S5](<#r08-s5>) |
| **Recover capture dates**<br>`metadata.date_fix` | C | Technical guide prioritizes embedded EXIF, XMP, JSON and filename fallback, including common phone/screenshot naming patterns; this establishes ingestion metadata, not embedded rewriting of source files. | [R08-S3](<#r08-s3>) |
| **Preserve hierarchical XMP keywords**<br>`metadata.hierarchical_tags` | C | XMP is passed unchanged for Immich to consume hierarchical tags, descriptions, GPS, capture time/timezone and camera settings; actual interpretation is server-dependent. | [R08-S3](<#r08-s3>) |
| **Export rich JSON metadata**<br>`metadata.sidecar_write` | C | Archive sidecars contain original filename/date, GPS, album titles/descriptions, hierarchical tags, rating and favorite/archive/trash/partner flags; original XMP companions are also retained. | [R08-S3](<#r08-s3>), [R08-S4](<#r08-s4>) |
| **Import and assign server tags**<br>`metadata.tags` | C | Custom repeated tags, folder-derived tags, upload-session tags, Takeout timestamp tags and people-name tags are supported; imported people names do not establish face recognition. | [R08-S2](<#r08-s2>), [R08-S3](<#r08-s3>) |
| **Pair XMP sidecars for server ingestion**<br>`metadata.xmp_read` | C | Folder uploads process associated XMP unless --ignore-sidecar-files is enabled; originals are forwarded without modification. | [R08-S2](<#r08-s2>), [R08-S3](<#r08-s3>) |
| **Bound concurrent upload work**<br>`performance.parallel_scan` | C | Parallel tasks default from CPU count and can be set within 1–20; timeouts and stop/continue/tolerated-error policies are configurable. | [R08-S2](<#r08-s2>), [R08-S3](<#r08-s3>) |
| **Pause server processing during import**<br>`performance.pause_server_jobs` | C | --pause-immich-jobs defaults true to reduce thumbnail/other server workload during a bulk upload, requiring appropriate server permissions. | [R08-S1](<#r08-s1>), [R08-S2](<#r08-s2>) |
| **Restart interrupted uploads safely**<br>`performance.resume` | C | Deduplication lets a restarted command skip files already on the destination; this is restart/idempotence behavior, not a byte-level partial-transfer checkpoint claim. | [R08-S3](<#r08-s3>) |
| **Resolve archive filename conflicts**<br>`safety.no_overwrite` | C | Archive output preserves names where possible, appends numbered suffixes on conflicts and sanitizes incompatible characters. | [R08-S3](<#r08-s3>) |
| **Filter transfer dates**<br>`search.date_range` | C | Accepts a year, year-month, day or explicit comma-separated date range; source-server transfer has a separate from-date-range option. | [R08-S2](<#r08-s2>), [R08-S3](<#r08-s3>) |
| **Filter ingestion by media type**<br>`search.file_type` | C | Include/exclude extensions and IMAGE/VIDEO/all filters constrain transfer/archive selection rather than providing a photo-browser search UI. | [R08-S2](<#r08-s2>), [R08-S4](<#r08-s4>) |

## Limitations and evidence gaps

- **explicit:** Google .tgz archives are explicitly unsupported directly: extract first, and supply all Takeout roots together rather than their enclosing parent. ([R08-S2](<#r08-s2>))
- **coverage-gap:** Upload/server stacking require a running Immich instance and adequately scoped API key; the CLI does not supply gallery browsing, ML recognition or sharing itself. ([R08-S1](<#r08-s1>), [R08-S5](<#r08-s5>))
- **explicit:** KeepRaw/KeepJPG/KeepHeic existing-server stack modes delete the alternate companion. Time-based bursts can group unrelated rapid shots; retain backups and preview. ([R08-S3](<#r08-s3>), [R08-S5](<#r08-s5>))
- **coverage-gap:** Overwrite documentation conflicts with v0.32.0 API removal; not counted as present with clear semantics. ([R08-S2](<#r08-s2>), [R08-S6](<#r08-s6>))
- **Coverage gap:** No standalone gallery/AI/map/share capabilities established; these belong to the separate Immich server.
- **Coverage gap:** Existing-asset overwrite semantics remain ambiguous after ReplaceAsset removal.
- **Coverage gap:** Actual decoder/rendering support follows Immich; importing a format does not prove local playback.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R08-S1

[Immich-Go README](<https://github.com/simulot/immich-go/blob/bc54ad2485b3e9c9b7c751445a28083950ffec60/readme.md>)
- Kind/ref: readme; bc54ad2485b3e9c9b7c751445a28083950ffec60
- Sections inspected: Complete README
- Establishes: Purpose, supported sources/platforms, compatibility, scale claim and backup warning.

### R08-S2

[Upload command](<https://github.com/simulot/immich-go/blob/bc54ad2485b3e9c9b7c751445a28083950ffec60/docs/commands/upload.md>)
- Kind/ref: manual; bc54ad2485b3e9c9b7c751445a28083950ffec60
- Sections inspected: Complete command reference
- Establishes: Source-specific ingestion, filters, album/tag preservation, parallelism and dry runs.

### R08-S3

[Technical details](<https://github.com/simulot/immich-go/blob/bc54ad2485b3e9c9b7c751445a28083950ffec60/docs/technical.md>)
- Kind/ref: manual; bc54ad2485b3e9c9b7c751445a28083950ffec60
- Sections inspected: Complete technical guide
- Establishes: Metadata priorities, pairing heuristics, SHA-1 deduplication and incremental archival.

### R08-S4

[Archive command](<https://github.com/simulot/immich-go/blob/bc54ad2485b3e9c9b7c751445a28083950ffec60/docs/commands/archive.md>)
- Kind/ref: manual; bc54ad2485b3e9c9b7c751445a28083950ffec60
- Sections inspected: Complete command reference
- Establishes: Local export format, supported sources and non-wiping incremental output.

### R08-S5

[Stack command](<https://github.com/simulot/immich-go/blob/bc54ad2485b3e9c9b7c751445a28083950ffec60/docs/commands/stack.md>)
- Kind/ref: manual; bc54ad2485b3e9c9b7c751445a28083950ffec60
- Sections inspected: Complete command reference
- Establishes: Existing-server burst/pair/scanner stacking and destructive keep-only choices.

### R08-S6

[v0.32.0 release notes](<https://github.com/simulot/immich-go/blob/bc54ad2485b3e9c9b7c751445a28083950ffec60/docs/releases/release-notes-v0.32.0.md>)
- Kind/ref: release; bc54ad2485b3e9c9b7c751445a28083950ffec60
- Sections inspected: Complete release note
- Establishes: V2/V3 adaptation, paginated album retrieval and removal of replacement API.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
