# R48 — jmathai/elodie

[Repository](<https://github.com/jmathai/elodie>) · 1,506 stars at the frozen snapshot · library-utility · Not archived

**Purpose:** Local EXIF-driven file organizer and metadata-repair CLI that names photos/videos/audio by date, place and album, tracks checksums and can verify a stored library.

**Deployment:** Python CLI with external ExifTool on macOS, Linux and Windows; Legacy experimental Electron taskbar GUI documentation

**Storage:** Organizes ordinary folders/files and embedded metadata rather than a proprietary media catalogue. It nevertheless maintains JSON checksum and location caches under its application directory (default .elodie), plus plugin JSON state; these are not a thumbnail browser catalogue.

**Privacy/network behavior:** Core file/metadata work is local. Current default geolocation uses installed ExifTool geolocation database; configuring deprecated MapQuest invokes its network geocoding service. Optional Google Photos plugin uploads media to Google using OAuth. External automation/watch tools are separate.

**License metadata:** Apache-2.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** No GitHub release returned
**Repository pushed at:** 2026-02-15T06:56:00Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [4494ff851451](<https://github.com/jmathai/elodie/commit/4494ff851451a6b8d2c68562c05968791bf5ad40>).
**Product lineage:** jmathai/elodie.

## Maturity and availability caveats

- Frozen commit 4494ff851451a6b8d2c68562c05968791bf5ad40; manifest records no latest release.
- Current README deprecates MapQuest in favor of ExifTool 13.13+ while sample config still shows a MapQuest key.
- Legacy GUI guide uses Electron 0.34.2/Node 5.1.0 examples and calls itself a work in progress; current distributed GUI availability is not established.
- Source inspection found dry-run initialization side effects and a trash-after-skipped-import caveat; no code was executed.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Use source folder as embedded album**<br>`albums.folder_mapping` | C | --album-from-folder derives album metadata from input folders and template fallbacks can prioritize album over place; this is file organization, not virtual shared albums. | [R48-S1](<#r48-s1>), [R48-S5](<#r48-s5>) |
| **Taskbar drag-and-drop album edits**<br>`deployment.legacy_taskbar_gui` | ? | GUI guide describes dragging Finder photos to create an album that writes EXIF and moves files, but calls the GUI unfinished and uses obsolete build tooling; manifest has no current release. | [R48-S8](<#r48-s8>) |
| **Preview imports, updates and plugin batches**<br>`duplicates.dry_run` | C | --dry-run reports file/metadata/plugin actions instead of media mutation; code guards hash/location writes. It is not a completely no-write process because directory/cache initialization can still occur. | [R48-S1](<#r48-s1>), [R48-S3](<#r48-s3>), [R48-S4](<#r48-s4>), [R48-S6](<#r48-s6>) |
| **SHA-256 content identity**<br>`duplicates.exact_hash` | C | Reads complete files in 64 KiB blocks into SHA-256 and maps hash to stored path; no perceptual similarity or byte-by-byte postverification is established. | [R48-S3](<#r48-s3>), [R48-S4](<#r48-s4>) |
| **Regex import exclusions**<br>`duplicates.exclude_paths` | C | Repeated --exclude-regex switches and named config exclusions skip matching file/folder paths, including examples for NAS artifacts and thumbnails. | [R48-S1](<#r48-s1>) |
| **Persistent checksum database**<br>`duplicates.hash_cache` | C | hash.json retains signatures and locations between runs; a hash maps to one recorded path rather than a full duplicate group catalogue. | [R48-S1](<#r48-s1>), [R48-S4](<#r48-s4>) |
| **HEIC metadata organization**<br>`formats.heic` | O | README requires ExifTool 11.50+ for HEIC support; this proves organization/metadata handling, not image decoding or playback. | [R48-S1](<#r48-s1>) |
| **Reuse previously resolved places**<br>`geo.location_cache` | C | Location lookup caches results in JSON and reuses a nearby cached location within a requested 3 km radius, reducing repeated lookups but potentially coarsening naming. | [R48-S2](<#r48-s2>), [R48-S4](<#r48-s4>) |
| **ExifTool local place lookup**<br>`geo.offline_geocoding` | O | With ExifTool 13.13+ geolocation database, current default derives city/region/country from coordinates and resolves names without a MapQuest key. Availability is tested against installed ExifTool database. | [R48-S1](<#r48-s1>), [R48-S2](<#r48-s2>) |
| **Legacy MapQuest geocoding**<br>`geo.online_geocoding` | O | When a MapQuest key exists, name/coordinate lookups still call its API; README marks this deprecated and intended for removal, with optional English names. | [R48-S1](<#r48-s1>), [R48-S2](<#r48-s2>) |
| **Scriptable file organization**<br>`integration.cli` | C | Commands import, update, generate-db, verify and batch operate on explicit files/directories with debug output. | [R48-S1](<#r48-s1>), [R48-S5](<#r48-s5>) |
| **Import lifecycle and batch plugins**<br>`integration.plugins` | C | Configured plugins expose before/after/batch hooks, JSON state and logging; a failing before-hook can prevent import. | [R48-S1](<#r48-s1>), [R48-S3](<#r48-s3>), [R48-S6](<#r48-s6>) |
| **Date/place/album folder templates**<br>`library.auto_date_folders` | C | Configurable folder placeholders include strftime date parts, city/state/country, camera make/model and album, with compound variables and ordered fallback choices. | [R48-S1](<#r48-s1>) |
| **Metadata-derived file naming**<br>`library.bulk_rename` | C | Filename templates combine capture timestamp, original name, title/album and extension, remove missing placeholders and allow lowercase/default or uppercase output. | [R48-S1](<#r48-s1>) |
| **Skip previously imported content**<br>`library.deduplicate_import` | C | Computes SHA-256 and skips an existing matching stored path; if cache says a match but that file is missing, import proceeds. --allow-duplicates overrides normal skipping. | [R48-S1](<#r48-s1>), [R48-S3](<#r48-s3>), [R48-S4](<#r48-s4>) |
| **Automated import triggers**<br>`library.filesystem_watch` | P | README explicitly relies on external inotify/cron/Automator/Hazel to invoke CLI when media arrives; Elodie itself is not documented as a persistent watcher. | [R48-S1](<#r48-s1>) |
| **Copy files into an organized library**<br>`library.import_copy` | C | Import accepts one/multiple source files/directories and a destination, preserving source placement by default and using embedded metadata to choose paths. | [R48-S1](<#r48-s1>), [R48-S3](<#r48-s3>) |
| **Organize camera RAW, video and audio files**<br>`library.raw_audio_video_organization` | C | README explicitly includes DNG/NEF and common video/audio alongside JPEG, with media-specific metadata precedence; no built-in playback is implied. | [R48-S1](<#r48-s1>) |
| **Regenerate checksum inventory**<br>`maintenance.cache_reset` | C | generate-db --source rebuilds hash.json for an existing library; resetting a baseline differs from verifying the old baseline. | [R48-S1](<#r48-s1>), [R48-S5](<#r48-s5>) |
| **Set missing or incorrect capture times**<br>`metadata.date_fix` | C | Import/update accept date or date-time overrides; import override replaces existing timestamp data, not merely fills missing values. | [R48-S1](<#r48-s1>) |
| **Update embedded metadata and reorganize**<br>`metadata.embedded_write` | C | update changes album, title, capture time or location through ExifTool and recalculates filenames/folders; it changes real files rather than only catalogue fields. | [R48-S1](<#r48-s1>), [R48-S3](<#r48-s3>) |
| **Photo EXIF capture/GPS extraction**<br>`metadata.exif_read` | C | Prefers DateTimeOriginal/CreateDate/ModifyDate then filesystem times; GPS and camera metadata drive folder naming. Missing location goes to a configurable fallback. | [R48-S1](<#r48-s1>) |
| **Assign GPS using a place name**<br>`metadata.gps_write` | C | Import/update location names are resolved to coordinates and written into supported media metadata; supplied import location overwrites existing location. | [R48-S1](<#r48-s1>), [R48-S2](<#r48-s2>) |
| **XMP and QuickTime metadata**<br>`metadata.xmp_read` | C | Uses XMP title/album/GPS and QuickTime/H264 timestamps for video/audio; README distinguishes photo Title from video/audio DisplayName and read-only Composite GPS. | [R48-S1](<#r48-s1>) |
| **Timestamped checksum-cache backups**<br>`safety.hash_database_backup` | C | Storage implementation provides timestamped copies of existing hash.json; this is backup of small integrity metadata, not copies of all media. | [R48-S4](<#r48-s4>) |
| **Verify stored checksum baseline**<br>`safety.integrity_check` | C | verify iterates hash/path records, reports missing files and recomputes content hashes to flag mismatches; it detects problems but does not repair corrupted files. | [R48-S1](<#r48-s1>), [R48-S5](<#r48-s5>) |
| **Optional source-file trash after import**<br>`safety.os_trash` | C | --trash calls send2trash on original sources. Important source caveat: this call is not conditional on process_file returning a successful destination, so a skipped import can still trigger source trash. | [R48-S1](<#r48-s1>), [R48-S5](<#r48-s5>) |
| **Google Photos upload plugin**<br>`sharing.social_export` | P | Bundled optional plugin queues imported photos for Google upload via batch, requiring a Google API project, OAuth client and stored credentials. Guide is legacy and current Google API compatibility was not independently established. | [R48-S7](<#r48-s7>) |

## Limitations and evidence gaps

- **explicit:** Location/time import overrides replace existing metadata. Metadata updates also relocate/rename files, so retain independent backups. ([R48-S1](<#r48-s1>), [R48-S3](<#r48-s3>))
- **explicit:** Source inspection shows --trash runs even when process_file returns no destination; users should not equate this switch with verified-copy-before-delete. ([R48-S5](<#r48-s5>))
- **explicit:** Dry run avoids media operations but initialization may create directories/empty state files; it is not a guaranteed zero-filesystem-write sandbox. ([R48-S3](<#r48-s3>), [R48-S4](<#r48-s4>), [R48-S6](<#r48-s6>))
- **explicit:** Although marketed without a proprietary database, implementation keeps JSON hash/location/plugin state; integrity checks require that baseline and only cover stored records. ([R48-S1](<#r48-s1>), [R48-S4](<#r48-s4>), [R48-S5](<#r48-s5>), [R48-S6](<#r48-s6>))
- **coverage-gap:** No collision-safe overwrite guarantee, copy-content verification, recoverable operation journal, modern GUI release or perceptual deduplication was established. ([R48-S1](<#r48-s1>), [R48-S3](<#r48-s3>), [R48-S8](<#r48-s8>))
- **coverage-gap:** MapQuest is deprecated but still invoked when configured; legacy Google Photos OAuth guide does not establish compatibility with current service restrictions. ([R48-S1](<#r48-s1>), [R48-S2](<#r48-s2>), [R48-S7](<#r48-s7>))
- **Coverage gap:** Legacy GUI and Google plugin current operability are unverified.
- **Coverage gap:** Format support means metadata/file handling, not browser-style rendering.
- **Coverage gap:** Source-derived safety caveats were inspected, not executed or benchmarked.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R48-S1

[Elodie README/manual](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/Readme.md>)
- Kind/ref: readme; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: Complete document across three ranges
- Establishes: Import/update/verify, dry run, templates, exclusions, metadata precedence and MapQuest deprecation.

### R48-S2

[Geolocation implementation](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/elodie/geolocation.py>)
- Kind/ref: code; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: Complete file
- Establishes: ExifTool versus MapQuest lookup, local cache and location fallback.

### R48-S3

[File organization implementation](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/elodie/filesystem.py>)
- Kind/ref: code; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: Initialization; _file_operation/create_directory; complete process_checksum/process_file
- Establishes: SHA-based skip rules, copy/move/ExifTool original handling and dry-run boundaries.

### R48-S4

[Checksum and location cache](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/elodie/localstorage.py>)
- Kind/ref: code; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: Complete file
- Establishes: SHA-256 streaming, timestamped cache backup, JSON persistence and dry-run writes.

### R48-S5

[CLI implementation](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/elodie.py>)
- Kind/ref: code; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: CLI definitions; complete import_file and _verify; generate-db options
- Establishes: Import flags, trash placement, missing-file/hash verification and hash regeneration.

### R48-S6

[Plugin lifecycle and state](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/elodie/plugins/plugins.py>)
- Kind/ref: code; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: PluginBase; PluginDb; loader and after-hook invocation
- Establishes: Before/after/batch extension points and per-plugin JSON state.

### R48-S7

[Google Photos plugin guide](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/elodie/plugins/googlephotos/Readme.markdown>)
- Kind/ref: manual; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: Complete document
- Establishes: Optional Google upload workflow, OAuth and separate batch execution.

### R48-S8

[Legacy taskbar GUI guide](<https://github.com/jmathai/elodie/blob/4494ff851451a6b8d2c68562c05968791bf5ad40/app/Readme.md>)
- Kind/ref: manual; 4494ff851451a6b8d2c68562c05968791bf5ad40
- Sections inspected: Complete document
- Establishes: Drag-and-drop album retagging workflow and old build requirements.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
