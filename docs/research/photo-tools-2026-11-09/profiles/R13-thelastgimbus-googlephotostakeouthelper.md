# R13 — TheLastGimbus/GooglePhotosTakeoutHelper

[Repository](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper>) · 5,985 stars at the frozen snapshot · library-utility · Not archived

**Purpose:** Local Takeout repair/organization utility that deduplicates exports, reconstructs albums and restores filesystem dates; current Dart version does not write JSON metadata into EXIF.

**Deployment:** Windows executable; macOS executable (README instructs Rosetta on Apple Silicon); Linux executable/AUR package; Interactive prompts or headless CLI

**Storage:** Consumes manually extracted, merged Takeout trees; moves by default or copies into ALL_PHOTOS and album directories, optionally year/month subfolders. Albums use shortcuts/symlinks, duplicate files or an albums-info.json manifest. There is no persistent browsable catalogue.

**Privacy/network behavior:** Processing works on local export files; obtaining Takeout is a prior Google service step. No mandatory third-party media upload appears in the documented workflow. Recommended ExifTool/Syncthing/other galleries are separate tools, not built-in features.

**License metadata:** Apache-2.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v3.4.3 (2023-09-24T02:23:28Z)
**Repository pushed at:** 2025-01-29T08:39:52Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a9de187efd9c](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/commit/a9de187efd9ce7cd072c5803dabc45079d416e64>).
**Product lineage:** TheLastGimbus/GooglePhotosTakeoutHelper.

## Maturity and availability caveats

- Frozen commit a9de187efd9ce7cd072c5803dabc45079d416e64; latest release v3.4.3 (2023-09-24), code version also 3.4.3.
- Dart rewrite supersedes legacy Python v2.x; older Python GPS/EXIF writing must not be attributed to current Dart.
- Source inspection exposes a significant &gt;64 MiB hashing limitation; no execution or empirical safety test was performed.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Portable album file copies**<br>`albums.duplicate_copy` | C | duplicate-copy materializes files per album, trading substantially more space for portability across systems. | [R13-S3](<#r13-s3>), [R13-S4](<#r13-s4>) |
| **Space-saving album links**<br>`albums.filesystem_links` | C | Default album strategy creates Windows .lnk shortcuts or Unix symlinks to originals using relative target paths; failed link creation falls back to materializing a file. | [R13-S3](<#r13-s3>), [R13-S4](<#r13-s4>) |
| **Ignore album-only assets**<br>`albums.ignore_mode` | C | nothing mode keeps year-folder photos without albums; documentation explicitly warns this omits Archive/Trash assets outside year folders. | [R13-S3](<#r13-s3>), [R13-S4](<#r13-s4>) |
| **Reconstruct album memberships**<br>`albums.takeout_reconstruction` | C | Groups identical exported instances across year/album folders and merges their album associations before output. | [R13-S2](<#r13-s2>), [R13-S5](<#r13-s5>) |
| **Linux executable**<br>`deployment.linux` | C | README documents a downloadable Linux binary and an AUR package, with interactive prompts or explicit CLI options for headless use. | [R13-S1](<#r13-s1>) |
| **macOS executable**<br>`deployment.macos` | C | README documents a downloadable macOS terminal executable and instructs Apple Silicon users to install Rosetta for the x86 build; native ARM64 distribution is not claimed. | [R13-S1](<#r13-s1>) |
| **Windows executable**<br>`deployment.windows` | C | README supplies a downloadable Windows .exe with prompted or command-line operation; it is an organization utility, not a desktop gallery viewer. | [R13-S1](<#r13-s1>) |
| **Size and SHA-256 grouping with size caveat**<br>`duplicates.exact_hash` | C | Groups candidates by size and hashes equal-size groups with SHA-256; cached in memory. Critically, files larger than 64 MiB receive the same constant digest instead of content hashing, so exactness does not hold for those assets. | [R13-S5](<#r13-s5>), [R13-S6](<#r13-s6>), [R13-S7](<#r13-s7>) |
| **Prompted or scripted operation**<br>`integration.interactive_cli` | C | Interactive mode prompts for folders/date division/album strategy; explicit input/output/album switches support headless NAS use and automation, with --help argument documentation. | [R13-S1](<#r13-s1>), [R13-S2](<#r13-s2>), [R13-S3](<#r13-s3>) |
| **Optional year/month organization**<br>`library.auto_date_folders` | C | --divide-to-dates creates year/month structure, including within album outputs; unknown dates go into date-unknown even without date subdivision. | [R13-S2](<#r13-s2>), [R13-S4](<#r13-s4>), [R13-S11](<#r13-s11>) |
| **Collapse duplicate export instances**<br>`library.deduplicate_import` | C | Drops repeated candidates within each album/year set, then merges album representations by size/hash; selects the best date-extraction accuracy when merging. Subject to the oversized-file digest limitation. | [R13-S5](<#r13-s5>), [R13-S6](<#r13-s6>), [R13-S7](<#r13-s7>) |
| **Interactive Takeout ZIP extraction**<br>`library.direct_zip_extraction` | N | Current README and commented-out CLI blocks explicitly disable interactive unzipping; users must unzip and merge beforehand despite stale help text suggesting auto-extraction. | [R13-S1](<#r13-s1>), [R13-S2](<#r13-s2>) |
| **Move by default or preserve source with copy**<br>`library.move_copy` | C | --copy avoids altering source file placement but needs additional space; default rename/move can leave a partly processed input on failure and does not support cross-drive moves. | [R13-S1](<#r13-s1>), [R13-S2](<#r13-s2>), [R13-S4](<#r13-s4>) |
| **Filter Google-generated extra images**<br>`library.skip_edited_extras` | C | --skip-extras removes recognized edited/effects/smile/mix suffix variants in several languages, with Unicode normalization for macOS names. | [R13-S2](<#r13-s2>), [R13-S10](<#r13-s10>) |
| **Flatten and repair Takeout exports**<br>`library.takeout_import` | C | Processes manually merged extracted Takeout folders and assembles photo/video output with reconstructed filesystem modification times. | [R13-S1](<#r13-s1>), [R13-S2](<#r13-s2>) |
| **Write Takeout JSON back to EXIF**<br>`metadata.embedded_write` | R | README TODO explicitly lists JSON-to-EXIF writing as unimplemented in Dart; suggested ExifTool command is an external follow-up, not a built-in function. | [R13-S1](<#r13-s1>) |
| **Fallback to embedded image dates**<br>`metadata.exif_read` | C | Within the size limit reads Image DateTime, then DateTimeOriginal, then DateTimeDigitized, normalizing separators; skips non-images and files above 64 MiB. | [R13-S7](<#r13-s7>), [R13-S9](<#r13-s9>) |
| **Restore filesystem modification dates**<br>`metadata.filesystem_date_fix` | C | Priority is Google JSON, embedded EXIF, optional filename guess, then aggressive JSON matching. --fix recursively applies dates to an arbitrary photo/video folder without running Takeout organization. | [R13-S2](<#r13-s2>) |
| **Restore JSON GPS into EXIF**<br>`metadata.gps_write` | R | README notes GPS transfer existed in older implementation but is missing in the Dart version. | [R13-S1](<#r13-s1>) |
| **Export album-membership JSON**<br>`metadata.sidecar_write` | C | json strategy puts all media including Archive/Trash in the general output and writes albums-info.json mapping output basenames to album lists; not a full metadata-preservation sidecar. | [R13-S3](<#r13-s3>), [R13-S4](<#r13-s4>) |
| **Handle Takeout sidecar naming anomalies**<br>`metadata.takeout_json_matching` | C | Matches photoTakenTime JSON through direct names, Google truncation, moved bracket suffixes, known edited suffixes and extension removal; last-resort aggressive suffix/digit removal is explicitly described as potentially dangerous in the pipeline. | [R13-S2](<#r13-s2>), [R13-S8](<#r13-s8>) |
| **Local export processing**<br>`privacy.no_upload_required` | C | Documented processing takes local input/output folders and operates on those files, without an upload step; downloading the initial Takeout remains external. | [R13-S1](<#r13-s1>), [R13-S2](<#r13-s2>), [R13-S4](<#r13-s4>) |
| **Disambiguate output filename collisions**<br>`safety.no_overwrite` | C | Repeatedly appends (1) before the extension until the output path is free; same helper protects link destinations. Separate startup logic may offer cleaning a pre-existing output directory. | [R13-S2](<#r13-s2>), [R13-S4](<#r13-s4>) |

## Limitations and evidence gaps

- **explicit:** Files above 64 MiB have a constant digest rather than a content hash. Equal-size distinct large assets can be treated as identical by grouping; do not assume safe exact deduplication for large videos/photos. ([R13-S5](<#r13-s5>), [R13-S6](<#r13-s6>), [R13-S7](<#r13-s7>))
- **explicit:** Default moves alter the input and cross-drive moves fail; README recommends retaining original ZIPs and re-extracting after failure. ([R13-S1](<#r13-s1>), [R13-S4](<#r13-s4>))
- **explicit:** Windows output dates before 1970 are clamped to 1970-01-01. Undated output gets current modification time and a date-unknown folder. ([R13-S4](<#r13-s4>))
- **explicit:** Album links are not guaranteed portable across systems; source notes non-ASCII shortcut issues, with fallback materialization. nothing album mode omits Archive/Trash. ([R13-S3](<#r13-s3>), [R13-S4](<#r13-s4>))
- **explicit:** Filesystem date repair is not embedded metadata writing; current Dart EXIF/GPS write features remain TODO. ([R13-S1](<#r13-s1>), [R13-S2](<#r13-s2>))
- **coverage-gap:** No persistent resume journal, file-content copy verification, full metadata round-trip or general gallery interface was established. ([R13-S1](<#r13-s1>), [R13-S2](<#r13-s2>), [R13-S4](<#r13-s4>))
- **Coverage gap:** Documentation is concentrated in README and inline CLI help, so source files provide the detailed evidence.
- **Coverage gap:** Large-file hashing limitation is source-derived, not runtime-tested.
- **Coverage gap:** No gallery, AI recognition or map features are established.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R13-S1

[Takeout Helper README](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/README.md>)
- Kind/ref: readme; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete README
- Establishes: Workflow, platforms, move default, separate ExifTool recipe and unimplemented metadata writing.

### R13-S2

[CLI and date pipeline](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/bin/gpth.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Argument definitions; interactive handling; extractor priority; fix mode; output checks; grouping workflow description
- Establishes: Actual CLI switches, fix-only behavior and safety-related defaults.

### R13-S3

[Album strategy definitions](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/interactive.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: albumOptions and interactive startup/help
- Establishes: Shortcut/copy/JSON/nothing choices and Archive/Trash differences.

### R13-S4

[Output movement and album materialization](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/moving.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete file
- Establishes: Collision renaming, relative links, date-unknown output, cross-drive and pre-1970 restrictions.

### R13-S5

[Duplicate and album grouping](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/grouping.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete file
- Establishes: Size/hash grouping and album association merge.

### R13-S6

[Media hashing](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/media.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete file
- Establishes: SHA-256 and constant digest for oversized files.

### R13-S7

[Media size limit and type selection](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/utils.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete file
- Establishes: 64 MiB read limit, image/video/MTS inclusion and version.

### R13-S8

[Takeout JSON matching](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/date_extractors/json_extractor.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete file
- Establishes: photoTakenTime extraction and filename mismatch heuristics.

### R13-S9

[EXIF date fallback](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/date_extractors/exif_extractor.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete file
- Establishes: Embedded date precedence and size/type guard.

### R13-S10

[Edited-extra filtering](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/blob/a9de187efd9ce7cd072c5803dabc45079d416e64/lib/extras.dart>)
- Kind/ref: code; a9de187efd9ce7cd072c5803dabc45079d416e64
- Sections inspected: Complete file
- Establishes: Language-specific edited/effects suffix filtering and Unicode normalization.

### R13-S11

[v3.4.3 release](<https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/releases/tag/v3.4.3>)
- Kind/ref: release; v3.4.3
- Sections inspected: Complete release notes
- Establishes: Unknown-date folder behavior, macOS extras detection and headless diagnostics.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
