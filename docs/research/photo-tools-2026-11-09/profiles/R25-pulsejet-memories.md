# R25 — pulsejet/memories

[Repository](<https://github.com/pulsejet/memories>) · 3,875 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Nextcloud-integrated photo/video timeline with metadata editing, maps, albums, advanced media formats and optional recognition/transcoding services.

**Deployment:** Nextcloud app with responsive browser UI; NativeX Android client on Google Play/F-Droid/GitHub; Optional go-vod Docker service; Optional current-source Lens semantic-search daemon and Qdrant

**Storage:** Originals remain in Nextcloud's existing folder structure, including configured external/object storage. Memories stores metadata indexes in the Nextcloud database, uses preview derivatives and optionally caches video keyframes/storyboards. Archive moves files into .archive rather than merely toggling a database flag.

**Privacy/network behavior:** Data remains on the device and chosen Nextcloud/services, not necessarily on a single local machine. Recognition depends on separately configured apps; optional Lens executes its embedding model on the chosen daemon. Reverse geocoding uses an imported local planet dataset, while map tiles/location search can contact configured providers. Nextcloud server-side encryption support is not E2EE. The website-oriented privacy policy also describes web logs and third-party libraries, so no blanket no-telemetry claim is made.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v11.1.1 (2026-11-09T03:33:35Z)
**Repository pushed at:** 2026-11-09T06:04:41Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a17051a1e63c](<https://github.com/pulsejet/memories/commit/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25>).
**Product lineage:** pulsejet/memories.

## Maturity and availability caveats

- Frozen master commit a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25; latest release v11.1.1 published 2026-11-09 (changelog dates it 2026-11-08).
- Current series requires Nextcloud 34+ per v9 release history. App, Android and go-vod have separate tags/version compatibility.
- Lens exists with setup/source in this snapshot but is not announced in the inspected release history; its packaged release availability is unverified.
- Current VIPS support supersedes older ImageMagick/RAW-plugin setup instructions. Comparison page explicitly labels itself outdated; no competitor claims are used.
- Million-photo testing and recent speedup ratios are developer claims, not benchmarks performed here.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Recognize object tags**<br>`ai.auto_tags` | P | Object/tag grouping is provided by Recognize rather than a built-in mandatory AI engine. | [R25-S1](<#r25-s1>), [R25-S3](<#r25-s3>) |
| **Merge and move faces**<br>`ai.face_corrections` | P | Merge face clusters, move photos between people, move unclustered faces and create a new cluster while moving; version requirements belong to Recognize. | [R25-S2](<#r25-s2>) |
| **Rename identified people**<br>`ai.face_naming` | P | Release history documents naming/renaming Recognize face groups rather than merely face detection. | [R25-S2](<#r25-s2>) |
| **Recognize/Face Recognition integration**<br>`ai.face_recognition` | P | Uses separately installed Nextcloud Recognize or Face Recognition; alternative Face Recognition integration is described as alpha with extra fine-tuning. | [R25-S3](<#r25-s3>) |
| **Lens model inference on chosen daemon**<br>`ai.local_inference` | O | Lens caches a pinned model snapshot and runs normalized image/text embeddings locally in its daemon, on CPU or CUDA. Initial model provisioning accesses Hugging Face unless complete offline cache exists. | [R25-S9](<#r25-s9>), [R25-S10](<#r25-s10>) |
| **Hierarchical places and missing-location view**<br>`albums.locations` | C | Places hierarchy and a filter for files without location, with configurable place covers; named places depend on geocoder setup. | [R25-S2](<#r25-s2>) |
| **Nextcloud photo albums**<br>`albums.manual` | P | Create albums of photos/videos, add to multiple albums, choose covers and sort lists; configuration explicitly requires the Nextcloud Photos app for album support. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>), [R25-S3](<#r25-s3>) |
| **People views from recognition apps**<br>`albums.people` | P | People grouping comes from Recognize or alternative Face Recognition app, with face thumbnails in sidebar and selectable person covers. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>), [R25-S3](<#r25-s3>) |
| **Breadcrumb and recursive folder views**<br>`browse.folders` | C | Choose folder-view root, use breadcrumbs, optionally show a recursive timeline, and browse folders within shares. | [R25-S2](<#r25-s2>) |
| **Desktop fullscreen viewer**<br>`browse.fullscreen` | C | Fullscreen viewing includes Shift+F keyboard shortcut and photo deep links. | [R25-S2](<#r25-s2>) |
| **On-this-day resurfacing**<br>`browse.memories` | C | Past photos appear in an On this day view and optionally at the top of the timeline, with age and direct-day navigation. | [R25-S2](<#r25-s2>) |
| **PhotoSphere viewer**<br>`browse.panorama` | C | v10 introduces interactive PhotoSphere panorama viewing; not a generic inference from a 2:1 image. | [R25-S2](<#r25-s2>) |
| **Photo/video slideshow**<br>`browse.slideshow` | C | Slideshow supports photos and videos with optional metadata display. | [R25-S2](<#r25-s2>) |
| **EXIF date timeline and direct date jumps**<br>`browse.timeline` | C | Sort photos/videos by capture date with a scrubber and #day/yyyy-mm-dd links; memories can jump to the corresponding day. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>), [R25-S15](<#r25-s15>) |
| **Bulk selection and mobile gestures**<br>`browse.touch` | C | Select entire days, shift-click or touch-drag, pinch/scroll zoom and swipe-to-refresh; later releases preserve navigation scroll position. | [R25-S2](<#r25-s2>), [R25-S15](<#r25-s15>) |
| **Adaptive or direct video playback**<br>`browse.video_playback` | C | Browser-supported codecs play directly; optional HLS transcoding handles other formats, with quality selection/fallback and user/admin autoplay controls. | [R25-S2](<#r25-s2>), [R25-S3](<#r25-s3>) |
| **Video timeline hover previews**<br>`browse.video_storyboards` | O | go-vod generates thumbnail sprites/VTT storyboards for video hover previews, cached persistently with keyframes. | [R25-S2](<#r25-s2>), [R25-S5](<#r25-s5>) |
| **Virtual scrolling timeline**<br>`browse.virtualization` | C | Official feature explanation explicitly identifies infinite virtual scrolling plus random-access date scrubber; no benchmark is inferred. | [R25-S15](<#r25-s15>) |
| **High-resolution image and video zoom**<br>`browse.zoom` | C | Full image can load upon zoom with configurable administrator defaults; desktop mouse wheel and newer video zoom are supported. | [R25-S3](<#r25-s3>), [R25-S2](<#r25-s2>) |
| **Android NativeX client**<br>`deployment.android` | C | Available through Google Play, F-Droid and separate GitHub Android releases; latest notes add mTLS client certificates and optional HDR disable. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>) |
| **Optional Docker companion services**<br>`deployment.docker` | O | Hardware-transcoding guide provides a separate radialapps/go-vod Docker service alongside Nextcloud; current-source Lens setup provides Docker Compose for its daemon and Qdrant. These are optional companions, not evidence that Memories is a standalone photo-server image independent of Nextcloud. | [R25-S5](<#r25-s5>), [R25-S9](<#r25-s9>) |
| **Multilingual Nextcloud interface**<br>`deployment.localization` | C | Release history explicitly adds localization with many languages from v2.0 and later localized metadata dates; README links the application's Transifex translation workflow. Separate from optional multilingual Lens queries. | [R25-S2](<#r25-s2>), [R25-S1](<#r25-s1>) |
| **Nextcloud app**<br>`deployment.selfhosted` | C | Install through Nextcloud's app store, configure the admin panel and index existing files; not a standalone service independent of Nextcloud. | [R25-S1](<#r25-s1>), [R25-S7](<#r25-s7>) |
| **Responsive browser application**<br>`deployment.web` | C | Browser UI works on desktop and Android/iOS with touch layouts; a native iOS Memories binary is not claimed. | [R25-S1](<#r25-s1>), [R25-S7](<#r25-s7>) |
| **Collapse presumed duplicate timeline entries**<br>`duplicates.metadata_collapse` | C | De-duplicate identical files setting collapses matching AUID entries and retains hidden copies for bulk actions. Missing AUID is derived from MD5(timestamp plus file size), not file bytes; this is presentation deduplication, not verified exact-content cleanup. | [R25-S13](<#r25-s13>), [R25-S14](<#r25-s14>), [R25-S2](<#r25-s2>) |
| **Tone, colour, detail and presets**<br>`editing.adjustments` | C | Brightness, exposure, contrast, highlights, shadows, saturation, vibrance, hue, temperature, blur, sharpen and vignette, plus warm/cool/monochrome/negative presets. | [R25-S12](<#r25-s12>) |
| **Server-side crop and straighten**<br>`editing.crop` | C | Current VIPS editor offers free/original/fixed aspect ratios and straightening from −45° to +45° in half-degree steps. | [R25-S2](<#r25-s2>), [R25-S12](<#r25-s12>) |
| **JPEG, PNG and AVIF editor output**<br>`editing.format_conversion` | C | Save dialog offers JPEG/PNG/AVIF, with 90/85/75 quality presets for lossy output and lossless PNG. | [R25-S11](<#r25-s11>) |
| **VA-API and NVENC acceleration**<br>`editing.hardware_encoding` | O | Intel QuickSync/compatible VA-API and NVIDIA NVENC require device/drivers/FFmpeg; newer NVENC uses Jellyfin GPU HDR tone mapping. | [R25-S5](<#r25-s5>), [R25-S2](<#r25-s2>) |
| **Rotate and flip images**<br>`editing.rotate_flip` | C | Editor state supports rotation and horizontal/vertical flips; separate bulk rotation updates EXIF losslessly. | [R25-S12](<#r25-s12>), [R25-S2](<#r25-s2>) |
| **Optional live HLS transcoding**<br>`editing.video_transcode` | O | go-vod adapts resolution to connection speed, supports quality selection and direct HLS-fMP4 streaming of HEVC/AV1/VP9. Disabled by default; CPU fallback without hardware. | [R25-S3](<#r25-s3>), [R25-S2](<#r25-s2>), [R25-S5](<#r25-s5>) |
| **AVIF support**<br>`formats.avif` | C | VIPS decodes AVIF; old files may require MIME repair and reindexing after upgrade. Editor also offers AVIF output. | [R25-S2](<#r25-s2>), [R25-S4](<#r25-s4>), [R25-S11](<#r25-s11>) |
| **Ultra-HDR, Samsung HDR and colour profiles**<br>`formats.hdr` | C | v11 VIPS decoder supports Ultra-HDR/Samsung HDR and ICC profiles; Android offers HDR-display disable. | [R25-S2](<#r25-s2>) |
| **HEIC and HEIF previews**<br>`formats.heic` | C | Bundled VIPS handles HEIC/HEIF with no extra image dependency when enabled; older provider fallback requires ImageMagick support. | [R25-S4](<#r25-s4>) |
| **Apple Live Photos**<br>`formats.live_photos` | C | Paired live-photo viewing, autoplay/loop settings and editing via a separate copy; earlier JPEG-only limitations are superseded by later HEVC/HEIC handling. | [R25-S2](<#r25-s2>), [R25-S11](<#r25-s11>) |
| **Google, Samsung and Huawei motion formats**<br>`formats.motion_photos` | C | Release history documents Google MVIMG, Samsung HEIC Motion Photos and Huawei Moving Picture. | [R25-S2](<#r25-s2>) |
| **Bundled camera RAW previews**<br>`formats.raw` | C | Current VIPS provider supports RAW out of the box and can be disabled. Older camera-raw-preview app is a fallback, not a current mandatory dependency. | [R25-S4](<#r25-s4>), [R25-S2](<#r25-s2>) |
| **RAW companion stacking**<br>`formats.raw_jpeg_pairs` | C | Can hide/stack RAWs beside another same-basename file; current releases support metadata edits of stacked JPEG+RAW pairs. | [R25-S2](<#r25-s2>) |
| **Photo map with selectable tile source**<br>`geo.map` | C | GPS-tagged photo map, configurable tile server, high-precision marker setting and Android local-photo geolocation; no bundled offline basemap established. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>) |
| **Local planet-boundary reverse geocoding**<br>`geo.offline_geocoding` | O | Download/import planet database into MySQL/MariaDB/PostgreSQL for server-side place lookup; can supply a custom planet ZIP. Map tiles remain an independent feature. | [R25-S3](<#r25-s3>), [R25-S6](<#r25-s6>) |
| **Administrative OCC commands**<br>`integration.cli` | C | Index, reverse-geocoder setup and Takeout migration are documented command-line actions; deprecated OCCWeb is explicitly incompatible. | [R25-S6](<#r25-s6>) |
| **Archive outside ordinary timeline**<br>`library.archive_folder` | C | Archive moves photos to .archive at timeline/storage root, which may be mounted to cold storage; this is a filesystem move, not just hiding. | [R25-S3](<#r25-s3>) |
| **Organize into year-month folders**<br>`library.auto_date_folders` | C | Move-to-folder workflow can organize selected files by year and month. | [R25-S2](<#r25-s2>) |
| **Web and Android manual uploads**<br>`library.batch_upload` | C | Direct web upload, Android destination-folder upload and selected local photo uploads are documented in release history. | [R25-S2](<#r25-s2>) |
| **Index and visibility exclusions**<br>`library.exclude_folders` | C | Supports .nomedia, app-specific .nomemories, hidden folders/files, regex filename/folder patterns and MIME blocklist; v11.1.1 fixes name-blocklist application to files. | [R25-S2](<#r25-s2>) |
| **Preserve existing Nextcloud files**<br>`library.existing_folders` | C | Uses existing files and their metadata without requiring a second proprietary original store; folder hierarchy remains intact. | [R25-S3](<#r25-s3>), [R25-S7](<#r25-s7>) |
| **Download media, albums and folders**<br>`library.export_originals` | C | Individual and whole album/public album/folder downloads are documented; v10 adds resumable file downloads. | [R25-S2](<#r25-s2>) |
| **Folder-preserving timeline**<br>`library.folder_structure` | C | Flat date display is layered on the unchanged directory hierarchy, with optional folder browsing. | [R25-S7](<#r25-s7>) |
| **Incremental indexing and upload hooks**<br>`library.incremental_scan` | C | Background jobs and immediate upload hooks index new/changed files. External modifications may need Nextcloud files:scan first; rerunning memories:index is incremental unless forced. | [R25-S3](<#r25-s3>), [R25-S6](<#r25-s6>) |
| **Automatic upload through Nextcloud clients**<br>`library.mobile_backup` | P | README directs automatic camera/photo/video upload to official Nextcloud Android/iOS apps rather than attributing background backup to Memories itself. | [R25-S1](<#r25-s1>), [R25-S7](<#r25-s7>) |
| **Move or copy selected media**<br>`library.move_copy` | C | Move from timeline to folders and, since 7.5.1, copy rather than move; copying triggers immediate indexing in later releases. | [R25-S2](<#r25-s2>) |
| **Multiple timeline roots and mounted storage**<br>`library.multiple_roots` | C | Configure multiple timeline paths and recursively include mounted volumes/shares within them; this is one user's scope, not separate catalogues. | [R25-S2](<#r25-s2>) |
| **Google Takeout metadata migration**<br>`library.takeout_import` | C | OCC command copies Takeout JSON into EXIF, optionally overriding existing fields and scoped by user/folder; it modifies source files and documentation requires backups. | [R25-S6](<#r25-s6>) |
| **Retry and refresh selected metadata**<br>`maintenance.selective_reset` | C | CLI supports retry failed entries, forced refresh or clear/reindex; UI supports Refresh Metadata on selected photos and lists failures in admin settings. | [R25-S6](<#r25-s6>), [R25-S2](<#r25-s2>) |
| **Bulk metadata and rotation**<br>`metadata.batch_edit` | C | Bulk date/other EXIF edits and collaborative tags; lossless bulk rotation writes orientation metadata rather than re-encoding pixels. | [R25-S2](<#r25-s2>) |
| **Correct capture dates**<br>`metadata.date_fix` | C | Edit EXIF date individually/in bulk, with a warning when a metadata edit would lose the date. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>) |
| **Edit original metadata**<br>`metadata.embedded_write` | C | Supports changing EXIF dates, title/description and GPS; RAW metadata editing is added in v11. These are source-file edits, not a default read-only catalogue. | [R25-S2](<#r25-s2>), [R25-S15](<#r25-s15>) |
| **EXIF sidebar and timeline metadata**<br>`metadata.exif_read` | C | Bundled ExifTool extracts photo/video capture and technical metadata, displayed in sidebar and used for timeline/maps. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>), [R25-S3](<#r25-s3>) |
| **Favourite media**<br>`metadata.favorites` | C | Select and favourite/unfavourite files, with a dedicated Favorites view. | [R25-S2](<#r25-s2>) |
| **Edit photo location**<br>`metadata.gps_write` | C | GPS editing supports precise coordinates and a configurable location-search provider. | [R25-S2](<#r25-s2>) |
| **Nextcloud collaborative tags**<br>`metadata.tags` | C | Edit/create collaborative tags individually or in bulk and show tags in sidebar; existing Nextcloud tags carry over. | [R25-S2](<#r25-s2>), [R25-S3](<#r25-s3>) |
| **CUDA Lens embedding option**<br>`performance.gpu_ml` | O | Lens embedding backend selects CUDA when configured/available, with Float16 there and Float32 CPU fallback. | [R25-S10](<#r25-s10>) |
| **External and distributed transcoding**<br>`performance.multiple_transcoders` | O | Deploy separate go-vod containers/hosts and list several addresses for load distribution with per-client sticky routing; supports external/object storage with documented setup. | [R25-S5](<#r25-s5>), [R25-S2](<#r25-s2>) |
| **Parallel metadata indexing**<br>`performance.parallel_scan` | C | Run multiple memories:index processes concurrently; can scope to user/group/path to avoid full-library work. | [R25-S6](<#r25-s6>) |
| **Preview pipelining and cache**<br>`performance.thumbnail_cache` | C | Preview derivatives and optimized loading reduce repeated work; optional Preview Generator app pre-generates previews. Sizes/quality are configurable and may otherwise exceed compact originals. | [R25-S3](<#r25-s3>), [R25-S15](<#r25-s15>) |
| **Nextcloud server-side encryption compatibility**<br>`privacy.at_rest_encryption` | P | Release history documents support for server-side encrypted storage. Encryption is supplied/configured by Nextcloud, and server-side readable originals are not E2EE. | [R25-S2](<#r25-s2>) |
| **Basic cached offline browsing**<br>`privacy.offline_use` | C | Release history documents basic offline support through cache, not a complete offline original-library replica. | [R25-S2](<#r25-s2>) |
| **Trash restore and permanent delete**<br>`safety.app_recovery` | C | v10.2 adds a Trash view for restoring or permanently deleting photos within the Nextcloud-backed application; retention is not specified here. | [R25-S2](<#r25-s2>) |
| **Configurable deletion confirmation**<br>`safety.confirmation` | C | Viewer deletion confirmation exists; v11 allows opting out. Metadata editor warns when a date would be lost. | [R25-S2](<#r25-s2>) |
| **Save edited copies**<br>`safety.nondestructive_edits` | C | Choose copy versus explicit overwrite; Live Photos always create copies and format changes force copy mode. This is save-as safety, not a full reversible edit recipe. | [R25-S11](<#r25-s11>), [R25-S2](<#r25-s2>) |
| **Basic built-in search**<br>`search.library_text` | C | v7.1 introduces basic search and album-picker/face-merge dialogs have search. Exact full-library query grammar is not established by these docs. | [R25-S2](<#r25-s2>) |
| **Optional Lens natural-language search**<br>`search.semantic_text` | O | Current-source Lens guide describes multilingual image description search after indexing, requiring a dedicated non-admin service account, separate daemon and Qdrant. Packaged release parity remains unverified. | [R25-S9](<#r25-s9>) |
| **Upload to public shares**<br>`sharing.guest_upload` | C | v7.8 adds upload to public shares; v9 fixes video uploads there. Availability still follows the underlying share permissions. | [R25-S2](<#r25-s2>) |
| **Nextcloud users and authentication**<br>`sharing.multiuser` | C | Uses Nextcloud user/auth ecosystem rather than reimplementing accounts; README and FAQ explicitly support multiple users. | [R25-S7](<#r25-s7>) |
| **Password-protected shares**<br>`sharing.password_links` | C | Password-protected folder shares and fixes for password link shares are explicitly documented. | [R25-S2](<#r25-s2>) |
| **External photo, album and folder shares**<br>`sharing.public_links` | C | Share individual or selected media and folders externally; album shares use Photos dependency and can be shared with Nextcloud users/groups or public links. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>), [R25-S3](<#r25-s3>) |
| **High/low-resolution and native sharing**<br>`sharing.resized_copy` | C | Share at high/low resolution, use native share interface, and transcode shared videos to smaller outputs. | [R25-S2](<#r25-s2>) |
| **Capture-date ordering**<br>`sort.capture_date` | C | Uses EXIF date rather than filesystem modification time; GPS can supply timezone information when camera EXIF lacks it. | [R25-S1](<#r25-s1>), [R25-S2](<#r25-s2>) |

## Limitations and evidence gaps

- **explicit:** Requires Nextcloud; albums require Photos, AI people/objects require Recognize or Face Recognition, and automatic mobile backup uses Nextcloud mobile clients. ([R25-S1](<#r25-s1>), [R25-S3](<#r25-s3>))
- **explicit:** Reverse geocoding does not support SQLite and needs a downloaded planet dataset. It is separate from network-served map tiles; offline basemap support is not established. ([R25-S3](<#r25-s3>), [R25-S6](<#r25-s6>))
- **explicit:** External-storage indexing downloads every file and may be slow. Transcoding is disabled by default, compute/storage intensive and documented as unsuitable for Raspberry Pi; failures can fall back to original streams. ([R25-S3](<#r25-s3>))
- **explicit:** Takeout migration and metadata edits modify files; backups are required before migration. Ordinary editor saves can overwrite originals unless copy mode is chosen/forced. ([R25-S6](<#r25-s6>), [R25-S11](<#r25-s11>))
- **explicit:** The UI's identical-file dedupe is not proof of content identity: source derives fallback AUID from date and size and collapses display entries, retaining copies for bulk actions. No exact-hash deletion feature is claimed. ([R25-S13](<#r25-s13>), [R25-S14](<#r25-s14>))
- **coverage-gap:** Lens optional source functionality and its packaging maturity are not established by release notes; model downloads and chosen daemon/Qdrant are additional dependencies. ([R25-S9](<#r25-s9>), [R25-S10](<#r25-s10>), [R25-S2](<#r25-s2>))
- **coverage-gap:** No durable per-file-operation recovery journal, E2EE guarantee, GPX synchronization or sidecar-write workflow is established. FAQ de-prioritizes advanced professional XMP/metadata features rather than promising them. ([R25-S7](<#r25-s7>))
- **Coverage gap:** Lens packaged release availability and exact basic-search fields unresolved.
- **Coverage gap:** No live Nextcloud/provider/hardware test; developer performance claims remain attributed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R25-S1

[Memories README](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/README.md>)
- Kind/ref: readme; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete README
- Establishes: Core timeline/features, Nextcloud dependency, Android and separate upload clients.

### R25-S2

[Complete release history](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/CHANGELOG.md>)
- Kind/ref: release; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: All entries v1.0.1 through v11.1.1
- Establishes: Current formats/editor/trash/video changes and established metadata, sharing, face and map workflows.

### R25-S3

[Configuration manual](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/docs/config.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document
- Establishes: Indexing hooks, ecosystem requirements, external storage, local geocoding and archive/preview behaviour.

### R25-S4

[File type support](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/docs/file-types.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document
- Establishes: Bundled VIPS and fallback preview providers, RAW/HEIC/AVIF and video requirements.

### R25-S5

[Hardware transcoding manual](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/docs/hw-transcoding.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document
- Establishes: CPU/VA-API/NVENC, internal/external/multiple transcoders, persistent caches and compatibility constraints.

### R25-S6

[OCC commands](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/docs/occ-commands.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document
- Establishes: Incremental/forced indexing, scopes/retry, local geocoder and Takeout mutation warning.

### R25-S7

[FAQ](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/docs/faq.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document
- Establishes: Folder preservation, multiuser/mobile support and intended non-professional scope.

### R25-S8

[Project privacy policy](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/docs/privacy.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document
- Establishes: Chosen-server data statement and separate website/logging caveats.

### R25-S9

[Memories Lens setup](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/lens/README.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document
- Establishes: Current-source multilingual natural-language search, dedicated account, daemon/models and Qdrant.

### R25-S10

[Lens embedding backend](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/lens/models/embedding.py>)
- Kind/ref: code; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Snapshot provisioning, load, image decode and normalized embedding functions
- Establishes: Pinned model download/cache and CPU/CUDA local inference.

### R25-S11

[Editor save controls](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/src/components/viewer/PhotoEditorSaveModal.vue>)
- Kind/ref: code; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete template and script
- Establishes: JPEG/PNG/AVIF choices, quality presets, copy/overwrite and Live Photo safety.

### R25-S12

[Editor control definitions](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/src/components/viewer/editor-controls/types.ts>)
- Kind/ref: code; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete file
- Establishes: Exact crop, tonal, colour, detail, straightening and preset controls.

### R25-S13

[Photo identity helper](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/src/services/utils/photo.ts>)
- Kind/ref: code; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete file, especially applyAuids
- Establishes: Dedupe identity can be MD5 of timestamp and size, not file-content hashing.

### R25-S14

[Timeline duplicate preprocessing](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/src/components/Timeline.vue>)
- Kind/ref: code; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: applyAuids call sites and complete duplicate-filter first pass in preprocessDay
- Establishes: Duplicate option hides AUID matches and retains references for bulk actions, rather than deleting originals.

### R25-S15

[Memories feature comparison (self-labelled outdated)](<https://github.com/pulsejet/memories/blob/a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25/docs/memories-vs-photos.md>)
- Kind/ref: manual; a17051a1e63cf6aa1a8dce1d3eec061d8b89cb25
- Sections inspected: Complete document; only explicit Memories behaviours used
- Establishes: Virtual timeline, scrubber and interaction design; newer docs/source take precedence.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
