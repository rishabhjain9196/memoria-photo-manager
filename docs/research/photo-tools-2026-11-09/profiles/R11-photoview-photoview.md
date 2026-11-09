# R11 — photoview/photoview

[Repository](<https://github.com/photoview/photoview>) · 6,570 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Read-only self-hosted gallery over existing photo/video folders, with nested folder albums, per-user roots, face grouping and controlled public sharing.

**Deployment:** Docker Compose; Linux server packages/source; documented Debian/Ubuntu, Arch, NixOS and appliance/community integrations; Browser client

**Storage:** Originals remain in filesystem directories, which map to albums. Separate database (SQLite, MariaDB or PostgreSQL) holds catalogue/user/share data and a configurable cache holds thumbnails, high-resolution web previews and transcoded video. Example media mounts are read-only.

**Privacy/network behavior:** Originals can remain on the operator's server; users are scoped to assigned roots and media requests use cookie tokens. Optional maps depend on Mapbox token/services. README explicitly warns that basic authentication alone is insufficient protection for Internet exposure and recommends external hardening; no E2EE guarantee is made.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v2.4.0 (2024-06-23T19:28:58Z)
**Repository pushed at:** 2026-11-07T18:21:43Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [f2f41dfc2333](<https://github.com/photoview/photoview/commit/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662>).
**Product lineage:** photoview/photoview.

## Maturity and availability caveats

- Frozen master f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662 is substantially newer than v2.4.0 (2024-06-23).
- v2.4.0 is described as the project-restart release; current README changes container registry and recommends PostgreSQL 18/17, which must not be retroactively assumed for older deployments.
- Hardware acceleration values are documented, but maintainers explicitly verified only Intel QSV. Third-party Docker abstraction support is limited.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Group people automatically**<br>`ai.face_clustering` | C | README describes grouping photos of the same person; schema stores face groups and counts. | [R11-S1](<#r11-s1>), [R11-S4](<#r11-s4>) |
| **Merge, move and detach faces**<br>`ai.face_corrections` | C | Merge source groups into a destination, move selected faces to another group or detach them into a newly created group. | [R11-S4](<#r11-s4>) |
| **Detect face rectangles**<br>`ai.face_detection` | C | Scanner detects faces and schema records normalized bounding boxes; custom builds can omit face support. | [R11-S1](<#r11-s1>), [R11-S2](<#r11-s2>), [R11-S4](<#r11-s4>) |
| **Name face groups**<br>`ai.face_naming` | C | Set or clear a person's group label. | [R11-S4](<#r11-s4>) |
| **Recognize unlabeled faces**<br>`ai.face_recognition` | C | API can compare unlabeled faces with labeled groups and move matches into those groups. | [R11-S4](<#r11-s4>) |
| **Choose album cover**<br>`albums.cover_selection` | C | API assigns a selected cover photo or resets the album cover. | [R11-S3](<#r11-s3>) |
| **Folders as albums**<br>`albums.folder_mapping` | C | Albums correspond to server directories, not a separately imported virtual organization. | [R11-S1](<#r11-s1>), [R11-S3](<#r11-s3>) |
| **Nested album browsing**<br>`albums.nested` | C | Browse parent/child albums, root-only lists and optionally empty albums. | [R11-S3](<#r11-s3>) |
| **High-resolution full-screen viewing**<br>`browse.fullscreen` | C | Viewer first displays a thumbnail until the high-resolution preview has loaded. | [R11-S1](<#r11-s1>) |
| **Lazy image loading**<br>`browse.lazy_images` | C | README says photos load when visible; this is image lazy loading, not evidence that DOM rows are virtualized. | [R11-S1](<#r11-s1>) |
| **Paginated catalogue APIs**<br>`browse.pagination` | C | Album/media/face/timeline API lists accept pagination to bound result sets. | [R11-S3](<#r11-s3>), [R11-S4](<#r11-s4>), [R11-S5](<#r11-s5>), [R11-S8](<#r11-s8>) |
| **Day and album timeline**<br>`browse.timeline` | C | Timeline orders media first by day then album and supports older-than-date pagination and favorite-only results. | [R11-S8](<#r11-s8>) |
| **Swipe gesture navigation**<br>`browse.touch` | C | v2.4.0 explicitly adds swipe gestures for media viewing. | [R11-S2](<#r11-s2>) |
| **Browser video playback**<br>`browse.video_playback` | C | Video media expose videoWeb resources and are optimized for browser delivery; v2.4.0 improves playback startup. | [R11-S1](<#r11-s1>), [R11-S2](<#r11-s2>), [R11-S5](<#r11-s5>) |
| **Docker Compose setup**<br>`deployment.docker` | C | Recommended/minimal Compose examples separate media cache, catalogue database and read-only media mounts. | [R11-S1](<#r11-s1>), [R11-S11](<#r11-s11>) |
| **Per-user translated web interface**<br>`deployment.localization` | C | User preferences store an interface language and changeUserPreferences accepts a language setting. The supported UI translation enum includes English, French, German, Japanese, Ukrainian, Turkish, Dutch and Simplified/Traditional Chinese variants among others; v2.4.0 explicitly adds/updates translations. | [R11-S9](<#r11-s9>), [R11-S2](<#r11-s2>) |
| **Self-hosted gallery server**<br>`deployment.selfhosted` | C | Server reads operator-managed photo/video directories; README lists Linux deployments and appliance/community wrappers. | [R11-S1](<#r11-s1>) |
| **Browser gallery**<br>`deployment.web` | C | Web UI offers gallery, timeline, face and map views with authentication. | [R11-S1](<#r11-s1>), [R11-S8](<#r11-s8>), [R11-S15](<#r11-s15>) |
| **Optional accelerated FFmpeg**<br>`editing.hardware_encoding` | O | Configure qsv, vaapi or nvenc and expose required devices/runtime; only QSV is explicitly maintainer-verified. | [R11-S1](<#r11-s1>), [R11-S10](<#r11-s10>) |
| **Automatic web video optimization**<br>`editing.video_transcode` | C | Server converts supported video into web-ready resources rather than requiring browser-native support for every original container. | [R11-S1](<#r11-s1>), [R11-S5](<#r11-s5>) |
| **HEIC processing**<br>`formats.heic` | C | v2.4.0 fixes HEIC EXIF extraction and README lists libheif as a server dependency. | [R11-S1](<#r11-s1>), [R11-S2](<#r11-s2>) |
| **RAW preview support**<br>`formats.raw` | C | README documents RAW photography support; release v2.4.0 specifically adds CR3. | [R11-S1](<#r11-s1>), [R11-S2](<#r11-s2>) |
| **RAW/web-image counterpart pairing**<br>`formats.raw_jpeg_pairs` | C | Same-stem compatible JPEG/web images can accompany a RAW/non-web image and be skipped as separate catalogue entries. Disabling RAW processing instead leaves compatible images standalone. | [R11-S13](<#r11-s13>), [R11-S17](<#r11-s17>) |
| **Cluster geotagged media**<br>`geo.clustering` | O | Map's GeoJSON source clusters nearby media with a 50-pixel radius and carries thumbnail properties into marker rendering. | [R11-S15](<#r11-s15>) |
| **Mapbox Places globe**<br>`geo.map` | O | MAPBOX_TOKEN enables a globe-projection map of geotagged media with map controls and media viewing; no offline map is established. | [R11-S10](<#r11-s10>), [R11-S15](<#r11-s15>) |
| **GraphQL catalogue and administration API**<br>`integration.api` | C | Typed GraphQL queries/mutations cover catalogue, accounts, scans, faces and share tokens; development mode exposes a playground. | [R11-S1](<#r11-s1>), [R11-S3](<#r11-s3>), [R11-S4](<#r11-s4>), [R11-S6](<#r11-s6>), [R11-S7](<#r11-s7>), [R11-S9](<#r11-s9>) |
| **Media download variants**<br>`library.download_variants` | C | Media exposes a list of downloadable file versions with role/title, URL, dimensions and file size; exact variants depend on processing. | [R11-S5](<#r11-s5>) |
| **Ignore-pattern filtering**<br>`library.exclude_folders` | C | Scanner compiles per-album ignore lines using gitignore semantics and skips matching file names. | [R11-S12](<#r11-s12>) |
| **Index existing media in place**<br>`library.existing_folders` | C | Filesystem paths are scanned without mandatory managed copying, preserving the operator's original organization. | [R11-S1](<#r11-s1>), [R11-S11](<#r11-s11>) |
| **Filesystem hierarchy reflected in gallery**<br>`library.folder_structure` | C | Directories become albums with parent/subalbum relations and breadcrumb paths. | [R11-S1](<#r11-s1>), [R11-S3](<#r11-s3>) |
| **Rescan for new media**<br>`library.incremental_scan` | C | Admin can scan all users or one user for new media; periodic scan interval is configurable and zero disables scheduled scans. | [R11-S7](<#r11-s7>) |
| **Multiple roots per user**<br>`library.multiple_roots` | C | Admin API adds/removes root albums for a user; Compose documents multiple media mounts with non-overlapping container paths. | [R11-S9](<#r11-s9>), [R11-S11](<#r11-s11>) |
| **Sidecar-sensitive RAW previews**<br>`library.sidecar_change_detection` | C | For non-web-compatible photos, discovers filename.ext.xmp, stores its hash and regenerates JPEG preview/thumbnail when sidecar changes or disappears. This establishes sidecar change detection, not a general XMP field reader/writer or searchable sidecar metadata. | [R11-S14](<#r11-s14>) |
| **Photographic EXIF display**<br>`metadata.exif_read` | C | Schema exposes description, camera/maker/lens, date shot, exposure, aperture, ISO, focal length, flash, exposure program and GPS. | [R11-S5](<#r11-s5>) |
| **Favorite photos and videos**<br>`metadata.favorites` | C | Mark/unmark media and filter albums/timeline to favorites or albums containing favorites. | [R11-S3](<#r11-s3>), [R11-S5](<#r11-s5>), [R11-S8](<#r11-s8>) |
| **Video technical metadata**<br>`metadata.video_read` | C | Displays dimensions, duration, codec, frame rate, bitrate, color profile and audio information. | [R11-S5](<#r11-s5>) |
| **Configurable scan concurrency**<br>`performance.parallel_scan` | C | Admin API sets the maximum concurrent scanner jobs; v2.4.0 also allows scanning to continue after individual-media failure. | [R11-S2](<#r11-s2>), [R11-S7](<#r11-s7>) |
| **Separate preview cache**<br>`performance.thumbnail_cache` | C | Generated previews are stored in configurable PHOTOVIEW_MEDIA_CACHE; media can include blurhash placeholders. | [R11-S1](<#r11-s1>), [R11-S5](<#r11-s5>), [R11-S10](<#r11-s10>) |
| **Read-only media access**<br>`safety.read_only_originals` | C | README calls the gallery read-only and Compose mounts media using :ro while cache/database remain separate writable volumes. | [R11-S1](<#r11-s1>), [R11-S11](<#r11-s11>) |
| **Album/media text query**<br>`search.library_text` | C | Search API returns albums and media with separate result limits; inspected contract does not establish semantic or arbitrary EXIF search semantics. | [R11-S16](<#r11-s16>) |
| **Expiring shares**<br>`sharing.expiring_links` | C | Share creation and update APIs accept an optional expiration time. | [R11-S6](<#r11-s6>) |
| **Multiple users with filesystem scope**<br>`sharing.multiuser` | C | Create users associated with assigned root paths, separating accessible directory trees. | [R11-S1](<#r11-s1>), [R11-S9](<#r11-s9>) |
| **Password-protected shares**<br>`sharing.password_links` | C | Shares can require a password and have password protection changed or cleared. | [R11-S1](<#r11-s1>), [R11-S6](<#r11-s6>) |
| **Share albums or individual media**<br>`sharing.public_links` | C | Generate revocable public share tokens, optionally labeled for their owner/administrator. | [R11-S1](<#r11-s1>), [R11-S6](<#r11-s6>) |
| **Admin/user access controls**<br>`sharing.roles` | C | User administration and scans require admin role; owned-media or valid share credentials authorize catalogue access. | [R11-S3](<#r11-s3>), [R11-S5](<#r11-s5>), [R11-S7](<#r11-s7>), [R11-S9](<#r11-s9>) |

## Limitations and evidence gaps

- **explicit:** README explicitly warns that basic authentication/read-only gallery access alone is insufficient protection for Internet exposure; TLS, VPN/reverse proxy and other controls are operator responsibilities. ([R11-S1](<#r11-s1>))
- **explicit:** Map features require a Mapbox token and remote provider. Container paths for separate media mounts must not overlap. Large-library speed descriptions and database rankings are project claims, not benchmarks performed here. ([R11-S1](<#r11-s1>), [R11-S11](<#r11-s11>), [R11-S15](<#r11-s15>))
- **explicit:** Pinned current branch and old latest release differ in database/registry configuration. Simply updating the v2.4.0 container without applying documented configuration changes is explicitly warned against. ([R11-S1](<#r11-s1>), [R11-S2](<#r11-s2>))
- **coverage-gap:** No inspected evidence establishes guest uploading, managed import/mobile backup, exact/perceptual duplicate cleanup, semantic/OCR search, embedded-metadata writes or an operation journal. ([R11-S1](<#r11-s1>), [R11-S3](<#r11-s3>), [R11-S5](<#r11-s5>), [R11-S7](<#r11-s7>), [R11-S16](<#r11-s16>))
- **coverage-gap:** Lazy image loading is not claimed as row virtualization; counterpart pairing is filename/type association, not content-based duplicate detection. ([R11-S1](<#r11-s1>), [R11-S13](<#r11-s13>), [R11-S17](<#r11-s17>))
- **Coverage gap:** No broad semantic/metadata-query semantics inferred from the generic search contract.
- **Coverage gap:** User manual coverage is principally comprehensive README and annotated deployment configuration, supplemented by capability schemas and implementations.
- **Coverage gap:** No runtime tests of codecs, GPU backends or remote Mapbox.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R11-S1

[Photoview README and deployment guide](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/README.md>)
- Kind/ref: readme; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete README including features, platforms/databases, setup, protection and acceleration
- Establishes: Core library, sharing, RAW/video/face capabilities, deployment and operational limits.

### R11-S2

[v2.4.0 restart release](<https://github.com/photoview/photoview/releases/tag/v2.4.0>)
- Kind/ref: release; v2.4.0
- Sections inspected: Complete additions/improvements/fixes
- Establishes: CR3, touch gestures, globe map, optional face builds, HEIC fixes and scan resilience.

### R11-S3

[Album API contract](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/album.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: Nested albums, breadcrumb paths, favorites filters and cover selection.

### R11-S4

[Face API contract](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/faces.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: Face groups, labeling, merge/move/detach and recognition against labeled groups.

### R11-S5

[Media API contract](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/media.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: EXIF/video metadata, favorites, downloads, previews and blurhash.

### R11-S6

[Sharing API contract](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/share_token.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: Public tokens, passwords, expiry, labels and revocation.

### R11-S7

[Scanner API contract](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/scanner.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: User/all scans, periodic scheduling and concurrency.

### R11-S8

[Timeline API contract](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/timeline.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: Day/album timeline grouping, favorite and date cursor filtering.

### R11-S9

[Users and root paths API](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/user.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: Admin roles, multiple roots and user preferences.

### R11-S10

[Environment configuration guide](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/example.env>)
- Kind/ref: manual; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete commented configuration
- Establishes: Separate media cache, database options, map token and video acceleration.

### R11-S11

[Annotated Compose deployment](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/docker-compose%20example/docker-compose.example.yml>)
- Kind/ref: manual; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete file
- Establishes: Read-only media mounts, cache/database volumes, multi-mount restrictions and optional updater.

### R11-S12

[Ignore-pattern scan task](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/scanner/scanner_tasks/ignorefile_task.go>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete file
- Establishes: Gitignore-style per-album filename exclusion.

### R11-S13

[RAW/web counterpart task](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/scanner/scanner_tasks/processing_tasks/counterpart_files_task.go>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete file
- Establishes: Avoid separate JPEG entries when RAW counterparts are processed.

### R11-S14

[XMP sidecar update task](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/scanner/scanner_tasks/processing_tasks/sidecar_task.go>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete file
- Establishes: Sidecar association/hash tracking and preview regeneration with rollback-on-failure.

### R11-S15

[Places map UI](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/ui/src/Pages/PlacesPage/PlacesPage.tsx>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete component
- Establishes: Mapbox globe, GPS media markers, clusters and media presentation.

### R11-S16

[Search API contract](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/graphql/resolvers/search.graphql>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete schema
- Establishes: Text query returns separately limited album and media lists.

### R11-S17

[Counterpart filename matching](<https://github.com/photoview/photoview/blob/f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662/api/scanner/media_type/counterpart.go>)
- Kind/ref: code; f2f41dfc2333b81fda2025ab5a9c8efb6ffbc662
- Sections inspected: Complete helper
- Establishes: Same-stem file pairing by web-compatible versus non-web-compatible image type.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
