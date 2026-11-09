# R45 — Webreaper/Damselfly

[Repository](<https://github.com/Webreaper/Damselfly>) · 1,798 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Server-side, folder-based photographic DAM emphasizing fast IPTC keyword retrieval, face/object assistance and basket-based export to desktop editing workflows.

**Deployment:** Self-hosted web server; Docker, recommended/supported installation; 64-bit standalone server binaries on Windows/Linux/macOS when published; Separate desktop clients for Windows, Linux and universal macOS

**Storage:** Indexes originals in a server directory tree; SQLite catalogue and derived thumbnails live in configurable volumes. Keywords are queued and written into originals by ExifTool without JPEG re-encoding. Desktop basket downloads mirror server paths; return synchronization is manual.

**Privacy/network behavior:** Current README explicitly provides local/offline face detection and recognition, replacing legacy Azure Face API use. No mandatory external original upload is documented; WordPress publishing and desktop synchronization are explicit workflows. Authentication is disabled by default, granting anyone who can reach the server browsing/modification/download access. Map-provider offline behaviour and media encryption are not established.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 4.5.3 (2026-01-14T13:50:05Z)
**Repository pushed at:** 2026-09-29T11:54:04Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [e110926104cc](<https://github.com/Webreaper/Damselfly/commit/e110926104cc93d3c87a9617ba7ab4ae70dbb216>).
**Product lineage:** Webreaper/Damselfly.

## Maturity and availability caveats

- Frozen master commit e110926104cc93d3c87a9617ba7ab4ae70dbb216; latest release 4.5.3 dated 2026-01-14.
- 4.5.3 upgrades to .NET 10; README/FAQ retain older .NET 7 wording and some older installation examples.
- Claims of sub-second search over 500,000 images and multi-day initial processing are author-reported, hardware-dependent observations, not benchmarks performed here.
- Cropping/colour editing, deduplication, video and automatic desktop-to-server synchronization remain in README's planned section and are not counted as present.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Object recognition and colour classification**<br>`ai.auto_tags` | C | Recognized objects/faces appear as special icon-marked tags beside ordinary keywords; README also lists image-colour classification. | [R45-S1](<#r45-s1>), [R45-S3](<#r45-s3>) |
| **Merge split identity groups**<br>`ai.face_corrections` | C | Assigning an existing name to another unknown person prompts a merge of face data, handling differences such as pose; split/reject workflows are not established here. | [R45-S3](<#r45-s3>) |
| **Detect face regions**<br>`ai.face_detection` | C | Runs face detection after thumbnails are generated, using lower-resolution derived images for analysis. | [R45-S3](<#r45-s3>) |
| **Name unknown people**<br>`ai.face_naming` | C | Click a detected face to name its associated person; same-named different people need disambiguating names. | [R45-S3](<#r45-s3>) |
| **Match people across photos**<br>`ai.face_recognition` | C | Creates unknown people from distinctive face traits and matches future faces to the existing person; latest README says this now runs locally/offline. | [R45-S3](<#r45-s3>), [R45-S1](<#r45-s1>) |
| **Local offline face processing**<br>`ai.local_inference` | C | Current README explicitly replaces formerly used Microsoft Azure Face API with local/offline detection and recognition; older Azure lineage must not be treated as a current requirement. | [R45-S1](<#r45-s1>) |
| **Persistent image baskets**<br>`library.selection_baskets` | C | Collect images from search results into reusable baskets for keywording, download/export or WordPress publication. | [R45-S1](<#r45-s1>), [R45-S3](<#r45-s3>) |
| **Thumbnail browsing and selection**<br>`browse.grid` | C | Thumbnail browser supports selection for keyword edits or basket addition, while individual images show properties and AI tags. | [R45-S3](<#r45-s3>) |
| **Date-grouped browsing**<br>`browse.timeline` | C | README identifies browsing grouped by date and release 4.5.3 updates advanced date-range UI. | [R45-S1](<#r45-s1>), [R45-S2](<#r45-s2>) |
| **Video support**<br>`browse.video_playback` | R | Roadmap says additional formats and possibly video; no current playback claim is made. | [R45-S1](<#r45-s1>) |
| **Docker server**<br>`deployment.docker` | C | Recommended supported deployment mounts pictures, config/database and thumbnails separately; default port is 6363. | [R45-S5](<#r45-s5>) |
| **Linux desktop client and server binaries**<br>`deployment.linux` | C | Linux standalone client/server packages supplement Docker; 64-bit OS is required. | [R45-S1](<#r45-s1>), [R45-S5](<#r45-s5>) |
| **macOS desktop client and server binaries**<br>`deployment.macos` | C | Universal macOS desktop client plus standalone server packages are documented, subject to release availability and dependency setup. | [R45-S1](<#r45-s1>), [R45-S5](<#r45-s5>) |
| **Server-side photo catalogue**<br>`deployment.selfhosted` | C | Central server/library can be used from several devices without copying catalogue databases onto each client. | [R45-S1](<#r45-s1>) |
| **Browser frontend**<br>`deployment.web` | C | Web-based photo browsing, search, tagging and export UI with selectable themes. | [R45-S1](<#r45-s1>) |
| **Windows desktop client and server binaries**<br>`deployment.windows` | C | README/FAQ document Windows standalone server and desktop client distributions; non-Docker server builds are not published for every release. | [R45-S1](<#r45-s1>), [R45-S5](<#r45-s5>), [R45-S6](<#r45-s6>) |
| **Image deduplication**<br>`duplicates.cleanup` | R | README explicitly lists image de-duplication as in progress; existing visual-similarity search is not counted as duplicate cleanup. | [R45-S1](<#r45-s1>) |
| **General non-destructive photo edits**<br>`editing.nondestructive_photo_editor` | R | README places cropping and colour adjustments in planned/in-progress enhancements, separate from existing lossless metadata and export processing. | [R45-S1](<#r45-s1>) |
| **Export at chosen resolutions**<br>`editing.resize` | C | Basket export can generate files at different resolutions for publication/email; this is export processing, not a general in-place editor. | [R45-S3](<#r45-s3>) |
| **Watermark exports**<br>`editing.watermark` | C | Exports optionally add watermarks for social/email use; standalone installation requires fonts for watermark rendering. | [R45-S1](<#r45-s1>), [R45-S3](<#r45-s3>), [R45-S5](<#r45-s5>) |
| **HEIC photos**<br>`formats.heic` | C | HEIC is explicitly included in supported formats and indexing description. | [R45-S1](<#r45-s1>), [R45-S3](<#r45-s3>) |
| **RAW preview/index support**<br>`formats.raw` | C | README lists DNG, CR2, ORF and NEF alongside JPG/PNG/TIFF/WebP/BMP; decoder support beyond these examples is not enumerated. | [R45-S1](<#r45-s1>) |
| **Map photos with geolocation**<br>`geo.map` | C | Displays locations when image metadata provides them; offline basemap/geocoding or location-write support is not established. | [R45-S1](<#r45-s1>) |
| **Reuse Synology thumbnails**<br>`integration.synology_thumbnails` | O | SYNO_THUMBS uses Synology @eaDir layout so existing DSM thumbnails are reused and newly created ones can be used by Photo Station. | [R45-S5](<#r45-s5>) |
| **Automatic desktop-to-server synchronization**<br>`library.desktop_writeback_sync` | R | Current workflow requires manually copying/rclone-syncing edits back; automatic return synchronization is explicitly future work. | [R45-S1](<#r45-s1>), [R45-S5](<#r45-s5>) |
| **Exclude directories with .nomedia**<br>`library.exclude_folders` | C | A .nomedia file in a folder causes that folder to be skipped by indexing; this is scan exclusion, not an encrypted vault. | [R45-S1](<#r45-s1>), [R45-S3](<#r45-s3>) |
| **Index originals in place**<br>`library.existing_folders` | C | At startup scans the configured photo tree and extracts metadata from existing originals; files need not be imported into a proprietary store. | [R45-S3](<#r45-s3>) |
| **Basket download and local edit workflow**<br>`library.export_originals` | C | Download/export basket images, including ZIP, or Save Locally in the desktop client to mirror server paths for external editing. | [R45-S1](<#r45-s1>), [R45-S5](<#r45-s5>) |
| **Automatically observe file changes**<br>`library.filesystem_watch` | C | Creates OS-level watchers per folder, automatically indexing added/updated images after the initial metadata pass. | [R45-S3](<#r45-s3>), [R45-S5](<#r45-s5>) |
| **Folder-based library and desktop mirror**<br>`library.folder_structure` | C | Preserves server folder organization; desktop Save Locally copies basket images under the matching client-relative folder tree. | [R45-S1](<#r45-s1>), [R45-S5](<#r45-s5>) |
| **Incremental background indexing**<br>`library.incremental_scan` | C | After initial indexing, changes are processed without manually rebuilding the whole catalogue; initial metadata pass prioritizes recently modified files. | [R45-S3](<#r45-s3>) |
| **Reorganize image files**<br>`library.move_copy` | C | Move or copy images between folders through the application. | [R45-S1](<#r45-s1>) |
| **Combine multiple mounted roots**<br>`library.multiple_roots` | C | Server scans one top-level tree; documented Docker workaround mounts several shares/volumes as distinct subfolders beneath /pictures. | [R45-S5](<#r45-s5>) |
| **User audit reporting**<br>`maintenance.user_audit_reports` | R | User IDs are associated with some operations, but the roles manual explicitly says audit reporting will come in a future release. | [R45-S4](<#r45-s4>) |
| **Batch keyword edits**<br>`metadata.batch_edit` | C | Selected images and basket contents can receive keyword operations together; pending additions/removals are combined in the background queue. | [R45-S3](<#r45-s3>) |
| **Write metadata back without recompression**<br>`metadata.embedded_write` | C | ExifTool applies queued keyword and other metadata operations to underlying originals without re-encoding JPEG image pixels. Originals are modified, so this is not read-only storage. | [R45-S3](<#r45-s3>) |
| **Read photographic metadata**<br>`metadata.exif_read` | C | Indexer extracts resolution, capture timestamp and EXIF metadata into the searchable catalogue. | [R45-S3](<#r45-s3>) |
| **Index IPTC keywords**<br>`metadata.iptc_read` | C | MetadataExtractor-based IPTC keyword indexing supports the documented tagging/search workflow. | [R45-S1](<#r45-s1>), [R45-S3](<#r45-s3>) |
| **Manage photographic keywords**<br>`metadata.tags` | C | Add keywords to selected images, an entire basket or the current photo in the properties screen. | [R45-S3](<#r45-s3>) |
| **Scheduled and throttled AI work**<br>`performance.ai_schedule` | C | Set a processing time window and CPU throttling to limit intensive face/object jobs on shared NAS hardware. | [R45-S3](<#r45-s3>) |
| **Resume pending metadata writes**<br>`performance.resume` | C | Pending metadata operations survive restart and are processed later; batching coalesces updates to reduce disk work. | [R45-S3](<#r45-s3>) |
| **Background thumbnail generation**<br>`performance.thumbnail_cache` | C | Generates browsing previews separately after metadata indexing and analyzes those thumbnails rather than originals. | [R45-S3](<#r45-s3>) |
| **Trash-folder deletion**<br>`safety.app_recovery` | C | README specifies image deletion through a trashcan folder; automatic retention duration and restoration guarantees are not documented in inspected manuals. | [R45-S1](<#r45-s1>) |
| **Date interval selection**<br>`search.date_range` | C | Advanced search includes date ranges, with a redesigned date-range selector in release 4.5.3. | [R45-S1](<#r45-s1>), [R45-S2](<#r45-s2>) |
| **File-size filtering**<br>`search.file_size` | C | Advanced search explicitly lists file-size criteria. | [R45-S1](<#r45-s1>) |
| **Full-text partial phrase search**<br>`search.full_text` | C | README explicitly supports full-text multi-phrase, partial-word retrieval; exact filename/path tokenization is not specified in the inspected feature section. | [R45-S1](<#r45-s1>) |
| **Technical metadata filters**<br>`search.metadata` | C | Advanced search filters camera/lens make/model and orientation. | [R45-S1](<#r45-s1>) |
| **Face and identity filters**<br>`search.people` | C | Search objects, detected faces and identified faces; anonymous face detection and named-person matching are distinct. | [R45-S1](<#r45-s1>) |
| **Find visually similar images**<br>`search.similar_image` | C | README explicitly lists visual-similarity search. It does not establish exact hashes or duplicate-removal support. | [R45-S1](<#r45-s1>) |
| **Keyword and untagged filtering**<br>`search.tags` | C | Find by keyword tags and explicitly filter images with no keyword tags. | [R45-S1](<#r45-s1>) |
| **Alamy stock-service upload**<br>`sharing.alamy_export` | R | README roadmap names selection/upload to Alamy; not established as available. | [R45-S1](<#r45-s1>) |
| **Private and shared baskets**<br>`sharing.collaborative_albums` | C | With authentication enabled users get a private My Basket and can expose a shared basket to all users. Without auth, anyone can alter any basket. | [R45-S4](<#r45-s4>) |
| **Optional user authentication**<br>`sharing.multiuser` | O | Enable authentication in system settings and restart to obtain registered accounts, persistent user-associated baskets and user-tag operation attribution. | [R45-S4](<#r45-s4>) |
| **User, ReadOnly and Admin entitlements**<br>`sharing.roles` | O | ReadOnly cannot modify keywords or download high-resolution images; User can; Admin manages settings/accounts. First user becomes admin and last admin cannot be demoted. | [R45-S4](<#r45-s4>) |
| **Publish to WordPress media library**<br>`sharing.social_export` | P | Basket images upload directly to a configured WordPress site; requires a separate WordPress JWT Authentication plugin and site/server credential setup. | [R45-S6](<#r45-s6>), [R45-S3](<#r45-s3>) |

## Limitations and evidence gaps

- **explicit:** Authentication is off by default; anyone reaching the UI can browse, modify and download. Enabling authentication requires restart, and ReadOnly still permits browsing. ([R45-S4](<#r45-s4>))
- **explicit:** Initial thumbnails/AI can take days and saturate CPU on NAS hardware; time-window/throttling settings mitigate but do not eliminate processing costs. Watcher limits may need OS tuning. ([R45-S3](<#r45-s3>), [R45-S5](<#r45-s5>))
- **coverage-gap:** Metadata writes modify originals, despite avoiding recompression; no sidecar-only mode, end-to-end encryption or durable reversible file-action journal is established. ([R45-S3](<#r45-s3>))
- **explicit:** Non-Docker setups are explicitly unsupported by the maintainer, need manually supplied dependencies and may lack binaries in a given release. ([R45-S5](<#r45-s5>))
- **explicit:** Same-named people must be disambiguated to avoid unintended identity merging. Face matches are not guaranteed across poses. ([R45-S3](<#r45-s3>))
- **explicit:** SQLite is current; PostgreSQL/MySQL/MariaDB are only potential future alternatives in FAQ. ([R45-S6](<#r45-s6>))
- **coverage-gap:** Offline map operation and translated interface language selection are not established by the inspected manuals or focused localization path discovery. ([R45-S1](<#r45-s1>), [R45-S5](<#r45-s5>), [R45-S6](<#r45-s6>))
- **Coverage gap:** Old runtime/dependency wording conflicts with newer release; newest release takes precedence.
- **Coverage gap:** No exact duplicate algorithm, trash retention or offline map guarantee established; roadmap kept separate.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R45-S1

[Damselfly README](<https://github.com/Webreaper/Damselfly/blob/e110926104cc93d3c87a9617ba7ab4ae70dbb216/README.md>)
- Kind/ref: readme; e110926104cc93d3c87a9617ba7ab4ae70dbb216
- Sections inspected: Complete README including capabilities, local-face update, roadmap and workflow
- Establishes: Photo formats, advanced search, local AI, baskets and explicit future features.

### R45-S2

[Release 4.5.3](<https://github.com/Webreaper/Damselfly/releases/tag/4.5.3>)
- Kind/ref: release; 4.5.3
- Sections inspected: Complete release note
- Establishes: .NET 10 and updated date-range selection UI.

### R45-S3

[Technical overview](<https://github.com/Webreaper/Damselfly/blob/e110926104cc93d3c87a9617ba7ab4ae70dbb216/docs/Technical.md>)
- Kind/ref: manual; e110926104cc93d3c87a9617ba7ab4ae70dbb216
- Sections inspected: Complete document; own-product indexing, AI and metadata sections used as evidence, not competitor assessments
- Establishes: Filesystem watcher pipeline, CPU cost, naming/merging faces and durable metadata write queue.

### R45-S4

[Multi-user, roles and entitlements](<https://github.com/Webreaper/Damselfly/blob/e110926104cc93d3c87a9617ba7ab4ae70dbb216/docs/Multi-user.md>)
- Kind/ref: manual; e110926104cc93d3c87a9617ba7ab4ae70dbb216
- Sections inspected: Complete document
- Establishes: Open-by-default access, role permissions, private/shared baskets and planned audit reporting.

### R45-S5

[Installation and desktop client guide](<https://github.com/Webreaper/Damselfly/blob/e110926104cc93d3c87a9617ba7ab4ae70dbb216/docs/Installation.md>)
- Kind/ref: manual; e110926104cc93d3c87a9617ba7ab4ae70dbb216
- Sections inspected: Complete document
- Establishes: Persistent volumes, multiple mounts, Synology thumbnail reuse, watch limits and desktop sync.

### R45-S6

[FAQ and WordPress integration](<https://github.com/Webreaper/Damselfly/blob/e110926104cc93d3c87a9617ba7ab4ae70dbb216/docs/FAQ.md>)
- Kind/ref: manual; e110926104cc93d3c87a9617ba7ab4ae70dbb216
- Sections inspected: Complete document
- Establishes: SQLite storage, standalone distribution and WordPress JWT plugin dependency.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
