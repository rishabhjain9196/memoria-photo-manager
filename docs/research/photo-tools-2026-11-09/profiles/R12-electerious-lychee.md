# R12 — electerious/Lychee

[Repository](<https://github.com/electerious/Lychee>) · 6,362 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Original legacy Lychee single-owner photo upload, album management and sharing server; not the modern LycheeOrg application.

**Deployment:** PHP 5.5+ web server and MySQL according to legacy documentation; README recommends a separate community Docker image

**Storage:** Managed upload/import directories, thumbnails and optional medium-size derivatives with MySQL albums/photos/settings. FAQ explicitly disallows using an existing folder structure in place. Duplicate uploads can share one physical file or be skipped.

**Privacy/network behavior:** Self-hosted photo storage with owner login and public/private/password album controls. Optional Dropbox imports and social-card sharing use external services. Original-file access hardening is listed as a separate plugin; no E2EE guarantee is established.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v3.1.6 (2017-03-20T08:45:24Z)
**Repository pushed at:** 2022-01-08T15:56:54Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [9cec5df56be3](<https://github.com/electerious/Lychee/commit/9cec5df56be3c06637406d9d83bdffc452f94569>).
**Product lineage:** Lychee.

## Maturity and availability caveats

- README says development moved to LycheeOrg on 2018-04-01; do not transfer modern fork features here.
- Manifest latest release is v3.1.6 from 2017-03-20; pinned master is 9cec5df56be3c06637406d9d83bdffc452f94569, last push 2022. Historical PHP/browser requirements are not current compatibility assurances.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Star-driven album covers**<br>`albums.favorite_cover_selection` | C | FAQ says covers are selected automatically from starred photos and upload order; starring an image influences the album thumbnail. | [R12-S3](<#r12-s3>) |
| **Create and manage albums**<br>`albums.manual` | C | Create albums, rename and describe them, move photos between albums and merge albums; documented hooks and changelog establish each action. | [R12-S5](<#r12-s5>), [R12-S6](<#r12-s6>) |
| **Built-in smart collections**<br>`albums.smart` | C | Changelog documents Recent and Unsorted smart albums and downloadable SmartAlbums; arbitrary user-defined query albums are not established. | [R12-S6](<#r12-s6>), [R12-S8](<#r12-s8>) |
| **Distraction-reduced image view**<br>`browse.fullscreen` | C | Changelog describes fullscreen entry/exit based on mouse activity and hiding the pointer in fullscreen. | [R12-S6](<#r12-s6>) |
| **Keyboard navigation and multiselect**<br>`browse.keyboard` | C | Shortcuts cover previous/next photo, search, metadata editing, favorites, select all, upload and delete. | [R12-S4](<#r12-s4>) |
| **Mobile swipe navigation**<br>`browse.touch` | C | Changelog documents swipe gestures and later touch/swipe fixes. | [R12-S6](<#r12-s6>) |
| **Video library support**<br>`browse.video_playback` | N | FAQ says videos cannot be uploaded and video support is not planned for this legacy application. | [R12-S3](<#r12-s3>) |
| **Community Docker deployment**<br>`deployment.docker` | P | README recommends kdelfour's separate lychee-docker image, not a native desktop/mobile application. | [R12-S1](<#r12-s1>) |
| **Single-owner web photo manager**<br>`deployment.selfhosted` | C | Runs on the owner's PHP/MySQL server and offers browser upload, management and sharing. | [R12-S1](<#r12-s1>), [R12-S3](<#r12-s3>) |
| **Browser photo-management interface**<br>`deployment.web` | C | Legacy Lychee exposes upload, photo/album management and sharing through a browser connected to its PHP/MySQL server. The FAQ lists supported browser families; its historical compatibility list is not a current-version guarantee. | [R12-S1](<#r12-s1>), [R12-S3](<#r12-s3>) |
| **Checksum-based duplicate storage**<br>`duplicates.exact_hash` | C | Changelog records stored photo checksums, switch from MD5 to SHA-1, and detection that stores only one file; no perceptual comparison or cleanup review workflow is established. | [R12-S6](<#r12-s6>) |
| **Upload watermark extension**<br>`editing.watermark` | P | README lists lychee-watermark, a separate plugin that adds a second watermarked photo on upload; not normal built-in editing. | [R12-S1](<#r12-s1>) |
| **Backend lifecycle hooks**<br>`integration.plugins` | C | Separately registered PHP observers receive before/after album, photo, session and import hooks; docs explicitly say plugins cannot modify the frontend. | [R12-S5](<#r12-s5>) |
| **Photo RSS feed extension**<br>`integration.rss_plugin` | P | README lists lychee-rss as a separate feed-generating extension. | [R12-S1](<#r12-s1>) |
| **Jekyll album embedding extension**<br>`integration.static_site_embed` | P | README lists a separate Jekyll Liquid tag for embedding Lychee albums in generated sites; no current Jekyll-version compatibility was established. | [R12-S1](<#r12-s1>) |
| **Dropbox import**<br>`library.cloud_import` | O | Requires a Dropbox drop-ins application key, requested on first use and configurable later. | [R12-S1](<#r12-s1>), [R12-S2](<#r12-s2>) |
| **Skip already uploaded photos**<br>`library.deduplicate_import` | C | skipDuplicates setting suppresses uploads of existing photos; older changelog also documents duplicate records sharing one stored file. | [R12-S2](<#r12-s2>), [R12-S6](<#r12-s6>) |
| **Core in-place source browsing**<br>`library.existing_folders` | N | FAQ explicitly says the app cannot use the existing folder structure and requires upload/import into its own storage/database. | [R12-S3](<#r12-s3>) |
| **Photo and album downloads**<br>`library.export_originals` | C | Download individual photos and album archives, including smart albums after the v3.1.6 fix; changelog notes title-based download filenames. | [R12-S5](<#r12-s5>), [R12-S6](<#r12-s6>), [R12-S8](<#r12-s8>) |
| **External folder synchronization**<br>`library.folder_sync_plugin` | P | README lists lycheesync as a separate extension for syncing an existing photo directory; this does not remove core managed-storage limitations. | [R12-S1](<#r12-s1>) |
| **Upload into a managed library**<br>`library.managed_upload` | C | Browser upload supports JPEG, PNG and GIF photos; server uses its own folder structure and database. | [R12-S1](<#r12-s1>), [R12-S3](<#r12-s3>) |
| **Recursive server-directory import**<br>`library.server_import` | C | Import accepts a chosen server directory, recurses into subdirectories and creates albums named from folders with an Import prefix; reserved Lychee derivative directories are excluded. | [R12-S7](<#r12-s7>) |
| **SSH photo-upload companion**<br>`library.ssh_upload_plugin` | P | README lists the separate lycheeupload extension for uploading photos to Lychee via SSH. This is an advertised companion capability, not a built-in upload transport or independently tested extension. | [R12-S1](<#r12-s1>) |
| **Import image URLs**<br>`library.url_import` | C | URL import accepts multiple comma-separated URLs, verifies extension and image type before download, then feeds the managed photo-add path. | [R12-S7](<#r12-s7>) |
| **Toshiba FlashAir import extension**<br>`library.wifi_sd_import` | P | README lists lychee-FlashAir for importing photos from a Toshiba FlashAir WiFi SD card. Hardware/network setup and current extension compatibility were not separately verified. | [R12-S1](<#r12-s1>) |
| **Built-in diagnostics page**<br>`maintenance.diagnostics` | C | FAQ points to plugins/Diagnostics/index.php for detected errors; changelog documents configuration/system checks. | [R12-S3](<#r12-s3>), [R12-S6](<#r12-s6>) |
| **Regenerate missing medium derivatives**<br>`maintenance.generate_missing_medium` | P | README lists lychee-create-medium for generating missing medium-size photos; this is an external maintenance extension, not built-in image editing. | [R12-S1](<#r12-s1>) |
| **Titles and descriptions**<br>`metadata.comments` | C | Photos and albums expose title/description editing and information panels; these are catalogue fields, not demonstrated embedded writes. | [R12-S4](<#r12-s4>), [R12-S5](<#r12-s5>) |
| **Strip metadata from derivatives**<br>`metadata.derivative_strip` | O | Imagick path removes metadata from medium images and thumbnails; this does not establish stripping metadata from downloadable originals. | [R12-S6](<#r12-s6>) |
| **EXIF information and orientation**<br>`metadata.exif_read` | C | Imports/displays EXIF including capture date and handles EXIF rotate/flip orientation with GD or Imagick. | [R12-S6](<#r12-s6>) |
| **Star photos**<br>`metadata.favorites` | C | Photo shortcut s/f and setStar hook mark favorites, also influencing album covers. | [R12-S3](<#r12-s3>), [R12-S4](<#r12-s4>), [R12-S5](<#r12-s5>) |
| **Import IPTC descriptive data**<br>`metadata.iptc_read` | C | Changelog documents headline/caption, title fallback when headline is absent, and photo-tag import. | [R12-S6](<#r12-s6>) |
| **Editable photo tags**<br>`metadata.tags` | C | Photo tagging is available through the UI and t shortcut; setTags hook exists and IPTC tags can seed imported tags. | [R12-S4](<#r12-s4>), [R12-S5](<#r12-s5>), [R12-S6](<#r12-s6>) |
| **Prefetch adjacent viewing assets**<br>`performance.image_prefetch` | C | Changelog documents preloading large photos then preferring medium images for prefetch, plus album caching and saved scroll positions. | [R12-S6](<#r12-s6>) |
| **Generated thumbnails and medium images**<br>`performance.thumbnail_cache` | C | Creates thumbnails; when Imagick is present it additionally provides medium-size images for small screens and documented quality/performance improvements. | [R12-S1](<#r12-s1>), [R12-S6](<#r12-s6>) |
| **Webroot access-control extension**<br>`privacy.original_access_plugin` | P | README describes lychee-webroot as a separate extension controlling photo accessibility and keeping Lychee files hidden. Its existence must not be interpreted as default core original-file protection. | [R12-S1](<#r12-s1>) |
| **Documented manual backup**<br>`safety.catalogue_backup` | C | FAQ instructs copying the whole installation folder and cloning albums/photos/settings tables; this is a manual procedure, not scheduled backups or a versioned action journal. | [R12-S3](<#r12-s3>) |
| **Search albums and photos**<br>`search.library_text` | C | Search is available from the album overview; changelog explicitly describes albums shown before photo results. Exact searchable field semantics were not traced. | [R12-S4](<#r12-s4>), [R12-S6](<#r12-s6>) |
| **Human-readable album-name redirect plugin**<br>`sharing.album_name_redirect` | P | README lists lychee-redirect as a separate extension that redirects an album name to a Lychee album, rather than a core routing guarantee. | [R12-S1](<#r12-s1>) |
| **Album download visibility control**<br>`sharing.download_permissions` | C | Public albums can be configured downloadable or not; no claim is made that this prevents saving images already displayed. | [R12-S6](<#r12-s6>) |
| **Multiple owner accounts**<br>`sharing.multiuser` | N | FAQ explicitly answers no/not yet to creating multiple users; public album viewers are not independent owner accounts. | [R12-S3](<#r12-s3>) |
| **Password-protected albums**<br>`sharing.password_links` | C | Album password setting/checking hooks and password-prompt/download behavior are documented; this is album-level, not a claimed per-image password capability. | [R12-S5](<#r12-s5>), [R12-S6](<#r12-s6>) |
| **Public images and albums**<br>`sharing.public_links` | C | Share individual photos and albums; hidden shared albums can be reachable only by direct link rather than public listing. | [R12-S5](<#r12-s5>), [R12-S6](<#r12-s6>) |
| **Social preview metadata**<br>`sharing.social_cards` | C | Shared images, but explicitly not albums, support Twitter Cards and Open Graph; historical Twitter domain approval instructions are not current service guarantees. | [R12-S1](<#r12-s1>) |
| **Capture-date sorting**<br>`sort.capture_date` | C | Changelog documents takedate sorting fixes; settings permit photo ORDER BY field/direction configuration. | [R12-S2](<#r12-s2>), [R12-S6](<#r12-s6>) |
| **Configurable album/photo sorting**<br>`sort.catalogue_fields` | C | sortingAlbums and sortingPhotos store SQL ordering fragments; some settings require direct database editing rather than a UI option. | [R12-S2](<#r12-s2>) |

## Limitations and evidence gaps

- **explicit:** This repository is legacy; contemporary LycheeOrg features must not be attributed to it. ([R12-S1](<#r12-s1>))
- **explicit:** Existing folders, video uploads and multiple users are explicitly unsupported in the FAQ; only PNG, JPEG and GIF uploads are listed. ([R12-S3](<#r12-s3>))
- **coverage-gap:** Core metadata embedded-write behavior is not established: plugin docs give writing changes back as a customization use case, not an installed capability. ([R12-S5](<#r12-s5>))
- **explicit:** Photos use PHP upload/time/memory limits; large uploads may need server configuration changes. Some settings are database-only. ([R12-S2](<#r12-s2>), [R12-S3](<#r12-s3>))
- **coverage-gap:** No inspected evidence establishes face recognition, maps, perceptual matching, app trash/undo, E2EE, or expiry-based shares. ([R12-S1](<#r12-s1>), [R12-S3](<#r12-s3>), [R12-S6](<#r12-s6>))
- **Coverage gap:** Modern LycheeOrg intentionally excluded.
- **Coverage gap:** Listed third-party plugins were not individually audited; only their advertised role is recorded.
- **Coverage gap:** Search field details and current runtime compatibility not established.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R12-S1

[Legacy Lychee README](<https://github.com/electerious/Lychee/blob/9cec5df56be3c06637406d9d83bdffc452f94569/README.md>)
- Kind/ref: readme; 9cec5df56be3c06637406d9d83bdffc452f94569
- Sections inspected: Complete README including migration, setup, advanced features and plugin table
- Establishes: Legacy scope, deployment, external imports, derivatives and extension ecosystem.

### R12-S2

[Settings reference](<https://github.com/electerious/Lychee/blob/9cec5df56be3c06637406d9d83bdffc452f94569/docs/Settings.md>)
- Kind/ref: manual; 9cec5df56be3c06637406d9d83bdffc452f94569
- Sections inspected: Complete database/login/sorting/Dropbox/Imagick/duplicate settings
- Establishes: Stored configuration, custom sorting and duplicate skipping.

### R12-S3

[Legacy FAQ](<https://github.com/electerious/Lychee/blob/9cec5df56be3c06637406d9d83bdffc452f94569/docs/FAQ.md>)
- Kind/ref: manual; 9cec5df56be3c06637406d9d83bdffc452f94569
- Sections inspected: Complete FAQ
- Establishes: Accepted formats, explicit unsupported workflows, backup procedure and diagnostics.

### R12-S4

[Keyboard shortcuts](<https://github.com/electerious/Lychee/blob/9cec5df56be3c06637406d9d83bdffc452f94569/docs/Keyboard%20Shortcuts.md>)
- Kind/ref: manual; 9cec5df56be3c06637406d9d83bdffc452f94569
- Sections inspected: Everywhere, Albums, Album and Photo tables
- Establishes: Search, selection, metadata, favorite and navigation actions.

### R12-S5

[Plugin system and hooks](<https://github.com/electerious/Lychee/blob/9cec5df56be3c06637406d9d83bdffc452f94569/docs/Plugins.md>)
- Kind/ref: manual; 9cec5df56be3c06637406d9d83bdffc452f94569
- Sections inspected: Complete use cases, registration and hook tables
- Establishes: Backend-only hooks, album/photo mutations and custom integration boundaries.

### R12-S6

[Legacy version history](<https://github.com/electerious/Lychee/blob/9cec5df56be3c06637406d9d83bdffc452f94569/docs/Changelog.md>)
- Kind/ref: release; 9cec5df56be3c06637406d9d83bdffc452f94569
- Sections inspected: Complete v2.0 through v3.1.6 history
- Establishes: Metadata, duplicate storage, hidden/password sharing, download controls, touch/fullscreen and managed imports.

### R12-S7

[Import implementation](<https://github.com/electerious/Lychee/blob/9cec5df56be3c06637406d9d83bdffc452f94569/php/Modules/Import.php>)
- Kind/ref: code; 9cec5df56be3c06637406d9d83bdffc452f94569
- Sections inspected: Complete photo, url and server methods
- Establishes: URL validation and recursive server-directory imports that create albums.

### R12-S8

[Lychee 3.1.6 release](<https://github.com/electerious/Lychee/releases/tag/v3.1.6>)
- Kind/ref: release; v3.1.6
- Sections inspected: Complete release body
- Establishes: Latest manifest release fixes SmartAlbum downloading and PHP7 htaccess handling.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
