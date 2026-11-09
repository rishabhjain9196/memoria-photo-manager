# R21 — RhetTbull/osxphotos

[Repository](<https://github.com/RhetTbull/osxphotos>) · 3,989 stars at the frozen snapshot · library-utility · Not archived

**Purpose:** CLI/Python toolkit for querying, exporting, importing and repairing Apple Photos/iPhoto libraries, with unusually rich metadata/template preservation and optional direct original-file writes.

**Deployment:** macOS command-line tool/Python package; Standalone macOS Intel/Apple Silicon executables; Linux export/query and Python API subset; Photos-app-dependent commands unavailable

**Storage:** Reads a copy of the Apple Photos SQLite catalogue into in-memory structures; queries existing Photos libraries rather than creating a replacement gallery. Exports copy original/edited/companion files into chosen directories and track state in .osxphotos_export.db. Optional hardlink exports share underlying files. Import/edit/sync commands operate on the open Photos library; explicitly dangerous commands can change originals or database fields.

**Privacy/network behavior:** Local library queries/exports need no third-party photo hosting. iCloud download-missing explicitly requires Apple Photos, network and an iCloud-synced library. OCR uses Apple's local Vision framework on supported macOS. Export databases/sidecars can expose person names/GPS and should not be casually shared. User-configured post-functions/commands can run arbitrary integrations; none were executed in this research.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v0.78.1 (2026-11-08T14:05:39Z)
**Repository pushed at:** 2026-11-09T12:09:58Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [2bb7b0d896c8](<https://github.com/RhetTbull/osxphotos/commit/2bb7b0d896c8233068196acdd3c47b489ba3efef>).
**Product lineage:** RhetTbull/osxphotos.

## Maturity and availability caveats

- Frozen main 2bb7b0d896c8233068196acdd3c47b489ba3efef; latest release v0.78.1 dated 2026-11-08.
- README says Photos libraries across supported macOS versions can be read on another supported system, with limited iPhoto 9.6.1 support and incomplete testing of newer versions.
- README explicitly cannot read shared albums on macOS 26.x; audio-only assets are not handled.
- Uses reverse-engineered Apple database structures; v0.78.1 documents a schema compatibility fix and iPhoto sync-export support. Future Apple schema changes may break compatibility.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Local Apple Vision text recognition**<br>`ai.ocr` | C | On macOS 10.15+, detected_text runs Vision on edited/original/preview fallback with confidence thresholds and cached results; explicitly distinct from Monterey Live Text. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Read Apple-generated captions**<br>`ai.read_existing_captions` | C | PhotoInfo exposes mediaanalysisd metadata and an AI caption when one exists; OSXPhotos is reading existing analysis, not generating captions itself. | [R21-S2](<#r21-s2>) |
| **Expose Apple's hidden classification labels**<br>`ai.read_existing_labels` | C | Read normalized labels produced by Photos image categorization and use them in queries or export keyword templates; labels originate from Photos, not a new OSXPhotos classifier. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Read stored aesthetic/curation scores**<br>`ai.read_existing_scores` | C | Photos 5+ ScoreInfo exposes overall, composition, blur/focus, noise and other existing scores; the author explicitly has not fully decoded their semantics. Not claimed as newly computed culling or best-shot inference. | [R21-S2](<#r21-s2>) |
| **Import folders into album hierarchy**<br>`albums.folder_mapping` | C | Album templates and split-folder delimiter create nested Photos folders/albums; multiple target albums and relative-to path templates are supported. | [R21-S4](<#r21-s4>) |
| **Prune an export mirror**<br>`cleanup.export_mirror` | C | --cleanup deletes files not in the current export set, including unrelated user files unless protected by .osxphotos_keep/keep rules; dotfiles are excluded. Explicit dry run is recommended. | [R21-S1](<#r21-s1>), [R21-S11](<#r21-s11>) |
| **Find and recover orphan candidates**<br>`cleanup.orphaned_library_files` | C | Compare UUID-named files in originals/renders/derivatives/shared scopes against catalogue IDs including trash and burst members. List candidates or copy them to a destination with collision-safe names; not automatic deletion. | [R21-S10](<#r21-s10>) |
| **Linux read/export subset**<br>`deployment.linux` | C | Query, export and Python API can operate on copied Photos libraries on Linux; macOS-specific CLI commands are omitted. | [R21-S1](<#r21-s1>) |
| **macOS CLI distribution**<br>`deployment.macos` | C | macOS supports Photos-app interactions and Python/tool-manager or standalone Intel/Apple Silicon distributions. | [R21-S1](<#r21-s1>) |
| **Standalone executable**<br>`deployment.portable` | C | Prebuilt macOS binaries do not require a separate Python install, but README warns they are not notarized. | [R21-S1](<#r21-s1>) |
| **Fast possible-duplicate candidates**<br>`duplicates.metadata_candidates` | C | PhotoInfo.duplicates matches original byte size, creation time, height and width—not hashes or byte comparison—and works even with iCloud originals missing. Results are expressly only possible duplicates. | [R21-S2](<#r21-s2>) |
| **Stored original-content fingerprints**<br>`duplicates.stored_fingerprint` | C | Expose Photos' stored hash of original file for cross-library matching, distinct from the metadata-based duplicates property. | [R21-S2](<#r21-s2>) |
| **JPEG conversion on export**<br>`editing.format_conversion` | C | Convert non-JPEG images such as RAW/HEIC to JPEG with quality 0–1 and extension normalization; README says conversion requires a Mac GPU and may fail in VMs. | [R21-S1](<#r21-s1>), [R21-S11](<#r21-s11>) |
| **AAE edit round-trip**<br>`formats.adjustment_sidecars` | C | Export AAE adjustment files and re-import with original/edited companions to preserve non-destructive edits when Photos naming conventions match; unmatched edits become separate assets. | [R21-S4](<#r21-s4>), [R21-S11](<#r21-s11>) |
| **Burst companion preservation**<br>`formats.burst_groups` | C | Default export includes burst photos unless skipped; macOS 11+ import groups burst members, unlike older versions. Missing iCloud bursts remain a documented limitation. | [R21-S1](<#r21-s1>), [R21-S4](<#r21-s4>), [R21-S11](<#r21-s11>) |
| **Live Photo paired-media export/import**<br>`formats.live_photos` | C | Exports still plus live video and imports recognized pairs together on macOS 11+; optional auto-live creates pairing metadata for same-basename non-Apple pairs, modifying inputs. | [R21-S1](<#r21-s1>), [R21-S4](<#r21-s4>) |
| **RAW+JPEG companion handling**<br>`formats.raw_jpeg_pairs` | C | Exports associated RAW and JPEG components with skip controls; import groups paired assets on macOS 11+ and API distinguishes RAW-as-original from standalone RAW. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>), [R21-S4](<#r21-s4>) |
| **Python catalogue/export API**<br>`integration.api` | C | PhotosDB, PhotoInfo, QueryOptions, PhotoExporter and comparison objects expose structured metadata and programmable export rather than requiring GUI automation for reads. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Photos-library command-line toolkit**<br>`integration.cli` | C | Commands cover query/export/import, batch edits, timewarp, sync/compare, metadata inspection, orphan discovery, library inventories and interactive help/template tools. | [R21-S1](<#r21-s1>) |
| **Post-export commands and import functions**<br>`integration.postprocessing_hooks` | O | Export executes template-based commands by output category; import can call configured Python post-functions, and timewarp accepts a custom timestamp function. External scripts are user-controlled executable integrations. | [R21-S1](<#r21-s1>), [R21-S4](<#r21-s4>), [R21-S5](<#r21-s5>) |
| **Preserve folder/album hierarchy on export**<br>`library.album_export_layout` | C | folder_album templates reproduce Photos nested albums; multi-album/multi-keyword templates can export multiple copies and filters can restrict chosen hierarchy branches. | [R21-S1](<#r21-s1>) |
| **Date-organized exports**<br>`library.auto_date_folders` | C | --export-by-date organizes by capture year/month/day; template directories can choose arbitrary date formats. | [R21-S1](<#r21-s1>) |
| **Download missing originals from iCloud**<br>`library.cloud_import` | C | --download-missing asks Photos via AppleScript or optional PhotoKit to obtain originals before export; requires network and iCloud sync, may restart Photos after crashes, and does not retrieve all burst companions. | [R21-S1](<#r21-s1>), [R21-S11](<#r21-s11>) |
| **Compare two Photos libraries**<br>`library.compare_catalogues` | C | Compare identifies assets unique to each catalogue and same/different pairs, accepts custom signature functions/templates, outputs CSV/TSV/JSON and offers nonzero-difference exit status. | [R21-S2](<#r21-s2>), [R21-S7](<#r21-s7>) |
| **Skip or confirm duplicate imports**<br>`library.deduplicate_import` | C | Choose Photos' dialog-based duplicate checks or OSXPhotos --skip-dups. Default matching uses photo fingerprint, but video fallback uses lowercase filename+size; custom signatures compare with library state at import start. | [R21-S4](<#r21-s4>) |
| **Reuse existing duplicate in target albums**<br>`library.duplicate_album_reuse` | C | --dup-albums adds an existing matched asset to the albums skipped import would have created, preserving folder-to-album organization without extra copies. | [R21-S4](<#r21-s4>) |
| **Export edited versions separately**<br>`library.export_edited` | C | Defaults to original and edited versions with a configurable edited suffix; can skip edits or export only edited when one exists. | [R21-S1](<#r21-s1>) |
| **Metadata-driven exported names**<br>`library.export_filename_templates` | C | Directory/filename templates support defaults, nested conditionals, multi-valued fields and filters; use title, date, place, album, keyword or original name without renaming Photos originals. | [R21-S1](<#r21-s1>) |
| **Export original images and video**<br>`library.export_originals` | C | Copies original media out of Photos using original import names by default, with selectable inclusion of related versions/companions. | [R21-S1](<#r21-s1>) |
| **Export derivative previews**<br>`library.export_previews` | C | API exposes ordered preview paths and optional preview export/suffix, including derivative stills/video previews when available. | [R21-S2](<#r21-s2>) |
| **Optional hardlink export**<br>`library.hardlink_export` | C | Exporter supports creating hardlinks instead of copies. These share the underlying file and are not an independent backup. | [R21-S2](<#r21-s2>) |
| **Import into Apple Photos**<br>`library.import_copy` | C | Import files/directories into the most recently opened Photos library, optionally recursively and with glob filtering. Ordinary assets import individually, affecting Photos Imports grouping. | [R21-S4](<#r21-s4>) |
| **Update an existing export**<br>`library.incremental_export` | C | SQLite export state enables --update to export only new/changed files. --only-new ignores removed prior exports; --ignore-signature avoids replacing externally edited output merely because file size/mtime differs. | [R21-S1](<#r21-s1>) |
| **Legacy iPhoto library access**<br>`library.legacy_iphoto` | C | Limited iPhoto 9.6.1 support includes export/query metadata; v0.78.1 adds iPhoto support to sync --export. | [R21-S1](<#r21-s1>), [R21-S12](<#r21-s12>) |
| **Set or merge metadata across libraries**<br>`library.metadata_sync` | C | Sync matched assets using original filename/fingerprint from another library/database or exported SQLite metadata. Set overwrites chosen fields; merge preserves/combines them, and album sync only adds memberships. | [R21-S6](<#r21-s6>) |
| **Explicitly select Photos catalogues**<br>`library.multiple_libraries` | C | --library selects among distinct Photos libraries; absent that, uses last-opened or System Photo Library. Compare/sync accepts separate source catalogues. | [R21-S1](<#r21-s1>), [R21-S6](<#r21-s6>), [R21-S7](<#r21-s7>) |
| **Google Takeout JSON metadata import**<br>`library.takeout_import` | C | Import sidecar support recognizes standard and supplemental-metadata.json Takeout names; UTC-only sidecar dates can be ignored to preserve more accurate embedded timezone information. | [R21-S4](<#r21-s4>) |
| **Selected-photo and template inspection**<br>`maintenance.interactive_inspection` | C | CLI provides inspect, UUID, show, REPL and interactive template commands for exploring selected Photos items and developing repeatable workflows. | [R21-S1](<#r21-s1>) |
| **Structured action reports**<br>`maintenance.operation_reports` | C | Export/import/sync/push-exif reports support CSV/JSON/SQLite outcomes including new/updated/skipped/missing/errors; import/sync can append reports. These logs are not crash-recovery journals. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>), [R21-S4](<#r21-s4>), [R21-S6](<#r21-s6>), [R21-S9](<#r21-s9>) |
| **Batch Photos metadata editing**<br>`metadata.batch_edit` | C | Selected/query-matched assets can receive template titles/captions/keywords, GPS and favorite flags; an open album with no selected photos targets all its photos unless queries are provided. | [R21-S3](<#r21-s3>) |
| **Timewarp capture-time correction**<br>`metadata.date_fix` | C | Set or offset date/time, parse filenames, assign named IANA/UTC-offset zones and optionally preserve wall-clock time with --match-time; named zones account for DST. | [R21-S5](<#r21-s5>) |
| **Explicit original-file metadata writes**<br>`metadata.embedded_write` | O | push-exif uses separately installed ExifTool to write keywords, GPS, face regions/persons, timestamps, titles/descriptions into originals and optionally edits. Compare/dry-run and change tracking reduce repeated writes; this is intentionally destructive to original bytes. | [R21-S9](<#r21-s9>) |
| **Read stored EXIF and optional full file metadata**<br>`metadata.exif_read` | C | Photos 5+ API exposes the EXIF subset cached by Photos; a separately installed ExifTool reader provides complete file metadata when the original is locally available. | [R21-S2](<#r21-s2>) |
| **Compare/pull/push EXIF dates**<br>`metadata.exif_time_reconcile` | O | With ExifTool compare Photos versus embedded timestamps, collect mismatches in an album, pull metadata into Photos or push it into originals; missing EXIF can fall back to file time. | [R21-S5](<#r21-s5>) |
| **Selective metadata export**<br>`metadata.export_privacy_selection` | C | Exporter options control inclusion of location/persons, replacement/merging of keywords and generated metadata; this does not automatically remove every pre-existing embedded field. | [R21-S2](<#r21-s2>) |
| **Set/clear favorites and rating mapping**<br>`metadata.favorites` | C | Batch set/clear favorite; import optionally maps an XMP star-rating threshold to favorite. Native numeric ratings are iPhoto-specific, not Apple Photos ratings. | [R21-S2](<#r21-s2>), [R21-S3](<#r21-s3>), [R21-S4](<#r21-s4>) |
| **Export filesystem date adjustment**<br>`metadata.filesystem_date_fix` | C | --touch-file sets exported file modification time to photo date; separate from changing embedded EXIF or Photos capture time. | [R21-S1](<#r21-s1>), [R21-S11](<#r21-s11>) |
| **Finder tags/comments and Spotlight attributes**<br>`metadata.finder_attributes` | C | Write keywords to Finder tags and template-driven author/comment/copyright/description/headline attributes without altering image bytes. | [R21-S1](<#r21-s1>) |
| **Assign GPS in Photos**<br>`metadata.gps_write` | C | Batch/import set explicit latitude/longitude; add-locations fills missing GPS using nearby geotagged captures rather than a GPX track. | [R21-S3](<#r21-s3>), [R21-S4](<#r21-s4>), [R21-S8](<#r21-s8>) |
| **Infer import dates from names/directories**<br>`metadata.import_date_parsing` | C | Parse strptime-like filename or folder patterns and supply timezone overrides; missing components fall back to Photos' date behavior. Direct named-timezone writes carry an undocumented-database risk. | [R21-S4](<#r21-s4>) |
| **Restore metadata from sidecars/export state**<br>`metadata.sidecar_import` | C | Read JSON/XMP sidecars or OSXPhotos export database for title, description, keywords, GPS, albums and date/time. XMP parsing needs ExifTool; JSON wins if both sidecar types are found. | [R21-S4](<#r21-s4>) |
| **Adjust Photos added/imported date**<br>`metadata.import_timestamp_edit` | C | Set date-added independently or copy capture date to added date, useful for removing old scans from Recents without changing their capture timestamp. | [R21-S5](<#r21-s5>) |
| **Time-nearest photo GPS propagation**<br>`metadata.nearest_photo_geotag` | C | Find the nearest geotagged photo within a configurable ±time window (default one hour) and copy its location; assumes correct capture times and offers dry run. | [R21-S8](<#r21-s8>) |
| **Read Photos person/face records**<br>`metadata.people_read` | C | Expose names, face/person objects and region metadata from Apple's catalogue. This is not an independent face-recognition engine. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Preserve Photos metadata in exported media**<br>`metadata.preserve_export` | O | With separately installed ExifTool, writes Photos keywords, persons, GPS and other metadata into exported files, optionally merging existing keywords/persons and deriving hierarchical tags from albums. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **XMP/JSON metadata sidecars**<br>`metadata.sidecar_write` | C | Export XMP or ExifTool-compatible JSON without installing ExifTool; configure extension-dropping and keyword/description templates. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Add or replace keywords**<br>`metadata.tags` | C | Batch-edit adds keywords by default with an explicit replacement switch; import can merge rather than overwrite existing keywords. | [R21-S3](<#r21-s3>), [R21-S4](<#r21-s4>) |
| **Local or RAM export-state database**<br>`performance.export_database_location` | O | Place export state on a faster local disk or use RAM then flush on completion; RAM mode can improve NAS workloads but loses progress if interrupted. | [R21-S1](<#r21-s1>) |
| **Threaded export integration**<br>`performance.parallel_export_api` | O | API documents concurrent export using threads on Python 3.11+; PhotosDB cannot be pickled for multiprocessing. This is an API/example capability, not a claimed default CLI speedup. | [R21-S2](<#r21-s2>) |
| **Resume tracked import/export**<br>`performance.resume` | C | Import --resume skips files recorded in an import database; export database permits restarting/updating prior exports. Reports are not equivalent to transactional rollback. | [R21-S1](<#r21-s1>), [R21-S4](<#r21-s4>) |
| **Retry unreliable exports**<br>`performance.retry` | C | --retry sets export retry attempts for failures such as intermittent NAS connections. | [R21-S1](<#r21-s1>) |
| **Reset original capture timestamp**<br>`safety.date_reset` | C | Timewarp --reset restores original recorded date/time/timezone only on macOS 13+ and only where Photos stored those original values. | [R21-S5](<#r21-s5>) |
| **Preview imports, exports and edits**<br>`safety.dry_run` | C | Export/import/batch/sync/geotag/push-exif support dry-run paths; import also validates/render-checks templates and checks already-imported versus not-imported files without importing. | [R21-S1](<#r21-s1>), [R21-S3](<#r21-s3>), [R21-S4](<#r21-s4>), [R21-S6](<#r21-s6>), [R21-S8](<#r21-s8>), [R21-S9](<#r21-s9>) |
| **Increment export names on collision**<br>`safety.no_overwrite` | C | API exporter defaults overwrite=false and increment=true; it can instead fail on collision when increment is disabled. Orphan recovery increments names as well. | [R21-S2](<#r21-s2>), [R21-S10](<#r21-s10>) |
| **Undo last metadata batch edit**<br>`safety.undo` | C | Batch-edit keeps prior values in a local store and --undo restores last metadata changes, but cannot undo album additions; this is not a general crash-safe file-operation journal. | [R21-S3](<#r21-s3>) |
| **Combined query semantics**<br>`search.boolean` | C | Different query options combine as AND; repeated keyword values combine as OR. Regex/template and custom function/expression hooks support more specific selection. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Find missing/edited/cloud/deleted assets**<br>`search.catalogue_states` | C | Query missing originals, referenced versus managed, iCloud-managed/synced, hidden, favorite, edited/external-edit, in/no album, deleted and missing descriptive metadata states. | [R21-S2](<#r21-s2>) |
| **Capture/import time filters**<br>`search.date_range` | C | Filter capture start/end/year and added-before/after/recent intervals; tutorial also documents time-of-day selection. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Size filtering**<br>`search.file_size` | C | Query minimum/maximum original size, e.g. select large videos and add them to an album. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Photo/video and subtype filters**<br>`search.file_type` | C | Filter photos/movies, UTI, RAW companions, live/burst/HDR/portrait/panorama/screenshot/selfie/slow-motion/time-lapse states. | [R21-S2](<#r21-s2>) |
| **Filename and template-path queries**<br>`search.filename_path` | C | Query original/media names and match regular expressions against template values such as full folder/album hierarchy. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Place and GPS-presence queries**<br>`search.location` | C | Query Photos reverse-geocoded place names and presence/absence of location/place data; no offline-map UI implied. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Rich catalogue queries**<br>`search.metadata` | C | Search title, description, album/folder, EXIF values, UUID and Photos labels; support query expressions/functions for custom predicates. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |
| **Named-person filters**<br>`search.people` | C | Search people identified by Photos and combine them with export/query constraints. | [R21-S2](<#r21-s2>) |
| **Saved export/query option configurations**<br>`search.saved_queries` | C | Save and reload export options, including filters/templates, as TOML configuration files for repeatable workflows. | [R21-S1](<#r21-s1>) |
| **Keyword filters**<br>`search.tags` | C | Query repeated keywords and absent-keyword state; export only matching media. | [R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>) |

## Limitations and evidence gaps

- **coverage-gap:** Inspected CLI/help/API documentation does not establish translated interface languages. Locale-aware month names/date formatting in export templates are data formatting, not UI localization; no positive localization capability is inferred. ([R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>))
- **explicit:** Many commands require macOS and the Photos app; Linux covers export/query/API subset. Classic shared albums cannot be read on macOS 26.x, iPhoto coverage is limited, and Apple schema changes can break parsing. ([R21-S1](<#r21-s1>), [R21-S12](<#r21-s12>))
- **explicit:** Audio-only assets are not supported. Missing-iCloud burst export retrieves only the primary member; some tilted-face coordinates may be incorrect. ([R21-S1](<#r21-s1>), [R21-S11](<#r21-s11>))
- **explicit:** Metadata duplicate candidates use size/date/dimensions rather than content verification. Import video duplicate fallback uses name/size; custom-signature import does not detect duplicates newly introduced within the same input batch. Sync merges indistinguishable duplicate/edited-copy metadata. ([R21-S2](<#r21-s2>), [R21-S4](<#r21-s4>), [R21-S6](<#r21-s6>))
- **explicit:** batch-edit --library controls the query source but changes always target the library currently open in Photos; users must ensure they match. No-selection album workflows can affect the entire album. ([R21-S3](<#r21-s3>), [R21-S5](<#r21-s5>))
- **explicit:** push-exif changes original files, is discouraged for iCloud-managed libraries because bytes may not resync, and skips classic shared albums. auto-live modifies source pairing metadata; direct named-timezone database writes use undocumented behavior and carry corruption risk. ([R21-S4](<#r21-s4>), [R21-S5](<#r21-s5>), [R21-S9](<#r21-s9>))
- **explicit:** Export cleanup can remove unrelated destination files. Target volumes are expected to be case-insensitive; case-sensitive NAS/drives can cause unexpected duplicate/missing results. Hardlinks are shared files, not backup copies. ([R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>), [R21-S11](<#r21-s11>))
- **explicit:** Export state contains sensitive GPS/person metadata; RAM-state exports lose progress on interruption. Cached EXIF/Apple-derived AI data may be stale or have only partially understood semantics. ([R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>))
- **coverage-gap:** Batch undo does not reverse album additions; reports/import/export databases do not establish atomic per-file-operation recovery. No complete GUI gallery, encrypted vault, social hosting or independently trained face/caption model is established. ([R21-S1](<#r21-s1>), [R21-S2](<#r21-s2>), [R21-S3](<#r21-s3>), [R21-S4](<#r21-s4>))
- **Coverage gap:** Very large API manual inspected by complete relevant sections rather than every trivial property/example; all principal end-user command families were checked.
- **Coverage gap:** No code or library was executed; Apple OS/schema support and external tool behavior remain documented claims.
- **Coverage gap:** Existing Apple labels/scores/captions/face records are explicitly distinguished from OSXPhotos' own Vision OCR and from independent ML inference.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R21-S1

[OSXPhotos README and export tutorial](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/README.md>)
- Kind/ref: readme; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: Purpose, supported OS, installation forms, command inventory, complete export tutorial, Files Created, limitations/implementation notes; detected_text template row
- Establishes: Export/query workflows, naming, versions, incremental state, sidecars, external dependencies and safety/privacy limits.

### R21-S2

[Python API manual](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/API_README.md>)
- Kind/ref: manual; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: Complete Concurrency and QueryOptions; PhotoInfo identity/date/path/format/details through rating; labels/EXIF/scores/duplicates/fingerprint/media-analysis methods; detected_text; ScoreInfo; SearchInfo introduction; ExportOptions/ExportResults; complete Text Detection and Compare Libraries
- Establishes: Precise query capabilities, metadata-only duplicate heuristic, Apple-derived AI fields, OCR, exporter options and concurrency constraints.

### R21-S3

[Batch-edit command](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/batch_edit.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: All command options, full command docstring and processing loop
- Establishes: Templates for metadata, query/selection targets, partial undo and active-library warning.

### R21-S4

[Import command help and constraints](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/import_cli.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: All import_main options and complete command docstring
- Establishes: Metadata/sidecar/Takeout imports, pair grouping, duplicate handling, resume, date parsing and original-write risks.

### R21-S5

[Timewarp command](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/timewarp.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: All command options and full timewarp docstring
- Establishes: Date/timezone/added-date corrections, EXIF push/pull and reset limitations.

### R21-S6

[Metadata synchronization command](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/sync.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: All command options, full sync docstring and initial validation
- Establishes: Set-versus-merge library metadata, identity heuristic, reports and duplicate ambiguity.

### R21-S7

[Library comparison command](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/compare.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: Complete command declarations, comparison and output helpers
- Establishes: Two-library diff, custom signatures, machine-readable formats and exit status.

### R21-S8

[Nearest-neighbor geotagging command](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/add_locations.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: All options, complete docstring and add_locations processing function
- Establishes: Propagate GPS from time-nearest geotagged photos within a configurable window.

### R21-S9

[Push metadata into original files](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/push_exif.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: Command options and complete push_exif docstring; initial validation
- Establishes: ExifTool-based original/edited metadata writing, compare/dry run and iCloud/shared-album cautions.

### R21-S10

[Orphan-file discovery](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/orphans.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: Options and complete orphans function
- Establishes: Compare library file UUIDs against catalogue including trash/bursts and optionally copy orphan candidates.

### R21-S11

[Export option definitions](<https://github.com/RhetTbull/osxphotos/blob/2bb7b0d896c8233068196acdd3c47b489ba3efef/osxphotos/cli/export.py>)
- Kind/ref: code; 2bb7b0d896c8233068196acdd3c47b489ba3efef
- Sections inspected: Complete option definitions for update, touch-file, jpeg-quality, download-missing, export-aae, strip and cleanup
- Establishes: Exact mirror-cleanup danger, keep rules, burst/download limitation and adjustment-file export.

### R21-S12

[v0.78.1 release](<https://github.com/RhetTbull/osxphotos/releases/tag/v0.78.1>)
- Kind/ref: release; v0.78.1
- Sections inspected: Complete release note
- Establishes: Newer Photos database schema fix, iPhoto metadata sync export and person-name recovery example.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
