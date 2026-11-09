# R19 — julyx10/lap

[Repository](<https://github.com/julyx10/lap>) · 4,263 stars at the frozen snapshot · library-desktop · Not archived

**Purpose:** Offline-first, folder-oriented desktop photo/video manager combining local AI search, culling, collections, broad decoding and cached access to disconnected storage.

**Deployment:** macOS Apple Silicon/Intel DMG and Homebrew; Windows 10/11 x64/ARM64 MSI, currently unsigned; Linux x64/ARM64 DEB and AppImage; community Fedora packages; experimental unpublished Arch recipe

**Storage:** Originals remain ordinary existing files. SQLite/local configuration stores collections, tags, comments, favorites, ratings, culling decisions, smart albums, embeddings, faces and caches. These organization values are not written to EXIF/IPTC/XMP sidecars and do not accompany external file copies.

**Privacy/network behavior:** Photo analysis and AI run on-device, without required upload/account. Maps fetch online tiles; updates use GitHub; optional multilingual models require downloads. Privacy policy states backend Aptabase start/exit events are enabled by default in release builds and contain version/platform/OS, not library contents.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v0.3.3 (2026-10-12T12:53:12Z)
**Repository pushed at:** 2026-11-08T15:14:44Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a0af23c4c435](<https://github.com/julyx10/lap/commit/a0af23c4c4356e4cab2fbea2333f2398a6b03b50>).
**Product lineage:** julyx10/lap.

## Maturity and availability caveats

- Pinned a0af23c4c4356e4cab2fbea2333f2398a6b03b50; latest release v0.3.3, 2026-10-12. Current main documentation can be newer than that release.
- README claims optimization for 100k+ media files; not independently benchmarked.
- AppImage playback depends on host GStreamer plugins; AppImage upgrades use replacement packages or external delta-update tools.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Smart subject tags**<br>`ai.auto_tags` | C | Local smart tags and subject-based browsing/search are documented; user-managed tags are stored in the catalogue. | [R19-S1](<#r19-s1>), [R19-S2](<#r19-s2>) |
| **People clustering**<br>`ai.face_clustering` | C | Locally groups faces and exposes a People list with incremental loading and person avatars; manual correction/naming specifics are not established here. | [R19-S1](<#r19-s1>), [R19-S5](<#r19-s5>) |
| **Face detection**<br>`ai.face_detection` | C | Privacy policy explicitly lists local face detection and storage of derived face data. | [R19-S2](<#r19-s2>) |
| **On-device analysis**<br>`ai.local_inference` | C | Semantic search, smart tags, face detection/clustering and video indexing execute locally along with thumbnail/RAW preview generation. | [R19-S2](<#r19-s2>) |
| **Persistent virtual collections**<br>`albums.manual` | C | Collections accept drag/drop across the library, reordering and duplicate-aware additions; removing membership does not move originals to Trash. | [R19-S6](<#r19-s6>) |
| **Rule-driven Smart Albums**<br>`albums.smart` | C | Saved rules include file types with configurable grouping/sorting/order; built-ins include Recently Added and On This Day. | [R19-S6](<#r19-s6>) |
| **Four-pane culling comparison**<br>`browse.compare` | C | Compare up to four images side-by-side; optional navigator sharpness grid assists focus comparison, without documenting an automatic quality score. | [R19-S4](<#r19-s4>), [R19-S6](<#r19-s6>) |
| **Grid and filmstrip**<br>`browse.grid` | C | Toolbar switches mutually exclusive grid, filmstrip and map modes; configurable thumbnail badges expose format and exposure settings. | [R19-S3](<#r19-s3>), [R19-S4](<#r19-s4>), [R19-S6](<#r19-s6>) |
| **Keyboard navigation**<br>`browse.keyboard` | C | Page Up/Down navigation, viewer shortcuts and keyboard stepping for straighten are documented. | [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>) |
| **Filmstrip slideshow**<br>`browse.slideshow` | C | Release notes explicitly describe stopping slideshows when leaving filmstrip or entering map mode. | [R19-S5](<#r19-s5>) |
| **Calendar/date exploration**<br>`browse.timeline` | C | Hierarchical Years/Months/Days navigation supplies localized month names and counts; grouping adapts to dates, folders, cameras, lenses or locations. | [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>) |
| **Video playback and previews**<br>`browse.video_playback` | C | Viewer and hover playback support videos and paired motion content. H.264 has compatibility processing when native playback is unavailable; HEVC/VP9 are natively supported on macOS and Linux depends on GStreamer plugins. | [R19-S1](<#r19-s1>), [R19-S6](<#r19-s6>) |
| **Virtualized large-library views**<br>`browse.virtualization` | C | v0.3.0 explicitly improves virtualized viewport loading and grouped/search result loading to reduce browsing work. | [R19-S6](<#r19-s6>) |
| **Zoom navigator**<br>`browse.zoom` | C | File Info preview has scroll zoom, double-click fit and a draggable full-image viewport navigator; video zoom pans around the cursor. | [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>) |
| **Fifteen-language desktop interface**<br>`deployment.localization` | C | v0.3.3 adds Hungarian, Italian, Dutch, Polish, Ukrainian and Traditional Chinese, bringing documented UI languages to fifteen; v0.3.2 adds a welcome-screen language selector. Date/time formatting follows the system region independently of UI language. This is separate from optional multilingual semantic search. | [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>) |
| **Preserve per-set keep choices**<br>`duplicates.keeper_selection` | C | Bulk removal across duplicate sets explicitly preserves each set's keep choice. | [R19-S5](<#r19-s5>) |
| **Scoped and library-wide duplicate review**<br>`duplicates.review_cleanup` | C | Duplicate scans can target a collection or selection; library-wide cleanup reports reclaimable space and bulk removes chosen copies. Sources do not specify hash versus perceptual equality. | [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>) |
| **Basic image adjustments**<br>`editing.adjustments` | C | README documents basic image adjustments, without asserting a full RAW-development workflow. | [R19-S1](<#r19-s1>) |
| **Collage and print layouts**<br>`editing.collage` | C | Grid, justified mosaic and picture-pile layouts support layering/moving/rotating/scaling, randomization, backgrounds, spacing, borders and shadows; export from originals at full resolution or print at 300 dpi to configurable/A4/photo pages. | [R19-S4](<#r19-s4>) |
| **Crop and straighten**<br>`editing.crop` | C | Crop includes arbitrary-angle horizon straightening with a zero-snapping ruler, keyboard stepping and live result preview. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>) |
| **Resize images**<br>`editing.resize` | C | Resize is explicitly included in built-in editing. | [R19-S1](<#r19-s1>) |
| **Rotate and flip**<br>`editing.rotate_flip` | C | Built-in image editing supports rotation and flipping; saved edits write a resulting image to the selected destination. | [R19-S1](<#r19-s1>) |
| **AVIF**<br>`formats.avif` | C | AVIF is explicitly included in supported image formats. | [R19-S1](<#r19-s1>) |
| **HEIC/HEIF/HIF**<br>`formats.heic` | C | Listed image formats include HEIC/HEIF/HIF with FFmpeg/ImageIO fallback decoding discussed per platform. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>) |
| **JPEG XL**<br>`formats.jpegxl` | C | JXL is explicitly included alongside HDR/EXR/PSD and JPEG 2000 image formats. | [R19-S1](<#r19-s1>) |
| **Apple Live Photos**<br>`formats.live_photos` | C | Recognizes HEIC/MOV pairs, displays a LIVE badge and plays motion; companion MOV files are suppressed from ordinary lists. | [R19-S6](<#r19-s6>) |
| **Google Motion Photos**<br>`formats.motion_photos` | C | Plays embedded video in supported Android/Google Motion Photo JPEGs and can recognize them in existing libraries. | [R19-S5](<#r19-s5>) |
| **RAW decoding and selectable previews**<br>`formats.raw` | C | Supports many camera RAW families; choose rendered or embedded previews, adjust render brightness and request full rendering when zooming. Preview fallback works both directions. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>) |
| **RAW+JPEG/HEIC stacks**<br>`formats.raw_jpeg_pairs` | C | Enabled pairs appear as one item with viewer switching between RAW modes and paired JPEG/HEIC. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>) |
| **Companion-aware operations**<br>`formats.sidecar_pairs` | C | Live Photo MOV, Apple AAE adjustment sidecars and enabled RAW companions stay together during rename/move/copy/delete. | [R19-S1](<#r19-s1>), [R19-S6](<#r19-s6>) |
| **Clustered photo markers**<br>`geo.clustering` | C | Clusters geotagged media and provides configurable photo-marker size. | [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>) |
| **Optional Tianditu provider**<br>`geo.custom_map_provider` | O | Tianditu is available for China with the user's own API token; normal maps fetch online tiles, including OpenStreetMap. | [R19-S2](<#r19-s2>), [R19-S5](<#r19-s5>) |
| **Filtered photo/video map**<br>`geo.map` | C | Map follows current filters and can retain position/zoom across cluster exploration; map styles, density heatmap and nearby-photo panel are documented. | [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>) |
| **Multiple external applications**<br>`integration.external_editor` | C | Configure multiple external apps and a default; opening more than 100 files requires confirmation. | [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>) |
| **Set desktop wallpaper**<br>`integration.wallpaper` | C | Wallpaper action supports macOS, Windows and GNOME Linux, including suitable paired RAW companion images. | [R19-S5](<#r19-s5>) |
| **Date-organized imports**<br>`library.auto_date_folders` | C | Choose YYYY/YYYY-MM-DD, YYYY/YYYY-MM, YYYY or one folder; uses capture date with modification-time fallback and preserves filenames. | [R19-S5](<#r19-s5>) |
| **Skip duplicate import content**<br>`library.deduplicate_import` | C | Import skips duplicate content and reports imported/skipped/failed counts; identical or nested source/destination paths are guarded. | [R19-S1](<#r19-s1>), [R19-S5](<#r19-s5>) |
| **Folder-first originals**<br>`library.existing_folders` | C | Indexes existing ordinary files without mandatory managed re-import copies; uninstalling the app/catalogue does not delete original media. | [R19-S1](<#r19-s1>) |
| **Native file export/drag-out**<br>`library.export_originals` | C | Drag photos/videos into the OS file manager or other apps as actual files, up to 1,000 per operation; catalogue-only annotations do not travel with them. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>) |
| **Folder hierarchy browsing**<br>`library.folder_structure` | C | Folder-based albums and cached subfolder trees reflect existing directories; subfolder refresh can update hierarchy without full media rescanning. | [R19-S1](<#r19-s1>), [R19-S5](<#r19-s5>) |
| **Copy import**<br>`library.import_copy` | C | Album import, drag/drop and clipboard workflows copy media into chosen folders, respect exclusions and update the library without a separate full scan. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>) |
| **Rescan filesystem changes**<br>`library.incremental_scan` | C | Rescans detect many external changes, and Live Photo associations update incrementally; external renames/moves can disrupt database-only organization. | [R19-S1](<#r19-s1>), [R19-S6](<#r19-s6>) |
| **Catalogue-aware file operations**<br>`library.move_copy` | C | In-app rename/move/copy/delete updates catalogue records and carries supported grouped components together. | [R19-S1](<#r19-s1>) |
| **Separate libraries**<br>`library.multiple_libraries` | C | Supports multiple libraries with management controls and per-library cache sizes/cleanup. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>) |
| **Disconnected album browsing**<br>`library.offline_volumes` | C | Keeps removable/network albums visible with cached metadata/thumbnails and an availability warning; operations needing originals are gated until reconnection. | [R19-S3](<#r19-s3>), [R19-S4](<#r19-s4>) |
| **Per-album exclusion preview**<br>`library.exclude_folders` | C | Per-album file-type, small-image and folder exclusions have a scan preview; v0.3.3 replaces the previous global small-image filter. | [R19-S4](<#r19-s4>) |
| **Per-library thumbnail cleanup**<br>`maintenance.selective_reset` | C | Manage Libraries shows cache sizes and removes thumbnails per library without implying removal of personal organization data. | [R19-S4](<#r19-s4>) |
| **Generated-image prompt import**<br>`metadata.ai_prompt` | C | Scans PNG prompts from Automatic1111, InvokeAI, ComfyUI and NovelAI into empty comments without overwriting existing notes. | [R19-S6](<#r19-s6>) |
| **Local comments**<br>`metadata.comments` | C | Comments are library-only metadata and do not automatically appear in other photo applications or exported copies. | [R19-S1](<#r19-s1>) |
| **Picks and rejects**<br>`metadata.culling_flags` | C | Local catalogue preserves culling states including Picks and Rejects, separate from file-embedded metadata. | [R19-S1](<#r19-s1>) |
| **Embedded technical metadata**<br>`metadata.exif_read` | C | Reads capture time, camera, lens, orientation and GPS; video metadata includes Apple QuickTime tags and GPS where available. | [R19-S1](<#r19-s1>), [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>) |
| **Favorites**<br>`metadata.favorites` | C | Favorite state is exposed in library navigation and stored locally. | [R19-S1](<#r19-s1>), [R19-S6](<#r19-s6>) |
| **Local ratings**<br>`metadata.ratings` | C | Ratings support organization and filtering but remain in Lap's database, not embedded files or XMP sidecars. | [R19-S1](<#r19-s1>) |
| **Batch metadata refresh**<br>`metadata.refresh` | C | Refresh file info rereads selected files together; unchanged cloud-only OneDrive/macOS dataless entries are detected without forcing downloads. | [R19-S4](<#r19-s4>) |
| **Catalogue tags and groups**<br>`metadata.tags` | C | Bulk tag management supports collapsible/reorderable groups and moving tags between groups, with a protected Default group. Groups are not documented arbitrary-depth tag hierarchies. | [R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>) |
| **Cancelable imports**<br>`performance.cancel` | C | Date-based import exposes progress, cancellation and continuation controls. | [R19-S5](<#r19-s5>) |
| **Continue import**<br>`performance.resume` | C | Documented import continuation works with duplicate skipping and imported/skipped/failed feedback; not claimed as a universal durable task journal. | [R19-S5](<#r19-s5>) |
| **Configurable cached thumbnails**<br>`performance.thumbnail_cache` | C | Thumbnail quality/resolution is adjustable up to documented 1024 px, with grid sizes up to 720 px and reduced-resolution RAW previews. | [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>) |
| **No required cloud library**<br>`privacy.no_upload_required` | C | No forced cloud account or photo upload; policy says library paths, queries, annotations, embeddings and media are not sent in analytics. | [R19-S1](<#r19-s1>), [R19-S2](<#r19-s2>) |
| **Offline local library operation**<br>`privacy.offline_use` | C | Core browsing and provisioned local AI are designed for offline use, but map tiles explicitly need Internet and update/telemetry/model requests are separate exceptions. | [R19-S1](<#r19-s1>), [R19-S2](<#r19-s2>), [R19-S3](<#r19-s3>) |
| **Local database backup**<br>`safety.catalogue_backup` | C | Settings &gt; Storage controls database location and creates a backup; README recommends backing up database/configuration alongside originals. | [R19-S1](<#r19-s1>) |
| **Preserve corrupt catalogue**<br>`safety.corruption_preservation` | C | Detects per-library corruption and prompts a library switch while preserving the original database instead of silently rebuilding it. | [R19-S4](<#r19-s4>) |
| **Media type filters**<br>`search.file_type` | C | AI Search and Smart Albums accept file-type constraints, including a combined Live &amp; Motion Photos condition. | [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>) |
| **Filename/text search**<br>`search.filename_path` | C | Regular filename, text and metadata result caps were removed in v0.3.2; in-view/sidebar search added in v0.3.3. | [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>) |
| **Metadata facets**<br>`search.metadata` | C | Browse/filter by date, camera, lens, location, tags, ratings and faces; camera/lens sidebar tabs include counts. | [R19-S1](<#r19-s1>), [R19-S5](<#r19-s5>) |
| **Optional multilingual search**<br>`search.multilingual_semantic` | O | Optional downloaded model extends search to over 50 languages; download failures on slow connections are explicitly discussed in release notes. | [R19-S1](<#r19-s1>), [R19-S5](<#r19-s5>) |
| **Local semantic search**<br>`search.semantic_text` | C | CLIP-based image/text similarity supports natural-language prompts and similarity cutoffs; the earlier 1,000-result cap was removed. | [R19-S1](<#r19-s1>), [R19-S5](<#r19-s5>) |
| **Visual similarity search**<br>`search.similar_image` | C | Local image similarity finds visually related media; it is separate from documented duplicate cleanup, whose exact detection algorithm is not established by these docs. | [R19-S1](<#r19-s1>), [R19-S6](<#r19-s6>) |

## Limitations and evidence gaps

- **explicit:** Collections, annotations, tags, ratings, favorites and culling state are catalogue-only, not EXIF/IPTC/XMP sidecars. External file moves can break those associations. ([R19-S1](<#r19-s1>))
- **explicit:** Map tiles are online, and release builds enable Aptabase lifecycle events by default. Local-first is not synonymous with air-gapped operation. ([R19-S2](<#r19-s2>), [R19-S3](<#r19-s3>))
- **explicit:** Windows installers are unsigned; Linux/AppImage video playback depends on system multimedia plugins and codec support. ([R19-S1](<#r19-s1>), [R19-S3](<#r19-s3>))
- **coverage-gap:** Duplicate matching algorithm, face correction/naming detail, OS-trash semantics, shared albums, end-to-end encryption and metadata sidecar import are not established by the inspected sources. ([R19-S1](<#r19-s1>), [R19-S4](<#r19-s4>), [R19-S5](<#r19-s5>), [R19-S6](<#r19-s6>))
- **Coverage gap:** No runtime tests; 100k+ scalability remains a project claim.
- **Coverage gap:** Exact duplicate algorithm and metadata/face edge cases are deliberately not inferred from broad feature labels.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R19-S1

[README](<https://github.com/julyx10/lap/blob/a0af23c4c4356e4cab2fbea2333f2398a6b03b50/README.md>)
- Kind/ref: readme; a0af23c4c4356e4cab2fbea2333f2398a6b03b50
- Sections inspected: Complete README including features, metadata ownership, formats, privacy and uninstall
- Establishes: Core inventory, catalogue portability boundary and deployment/format support.

### R19-S2

[Privacy policy](<https://github.com/julyx10/lap/blob/a0af23c4c4356e4cab2fbea2333f2398a6b03b50/PRIVACY.md>)
- Kind/ref: manual; a0af23c4c4356e4cab2fbea2333f2398a6b03b50
- Sections inspected: Entire policy
- Establishes: Local analysis, third-party network access and default lifecycle telemetry.

### R19-S3

[Getting started](<https://github.com/julyx10/lap/blob/a0af23c4c4356e4cab2fbea2333f2398a6b03b50/docs/guide/getting-started.md>)
- Kind/ref: manual; a0af23c4c4356e4cab2fbea2333f2398a6b03b50
- Sections inspected: Entire guide
- Establishes: Ingestion, views, offline albums, cache controls and installation caveats.

### R19-S4

[v0.3.3 release notes](<https://github.com/julyx10/lap/blob/a0af23c4c4356e4cab2fbea2333f2398a6b03b50/docs/guide/release-notes/v0.3.3.md>)
- Kind/ref: release; a0af23c4c4356e4cab2fbea2333f2398a6b03b50
- Sections inspected: Complete release notes
- Establishes: Collage, tag groups, offline albums, RAW controls, exclusions and database safety.

### R19-S5

[v0.3.2 release notes](<https://github.com/julyx10/lap/blob/a0af23c4c4356e4cab2fbea2333f2398a6b03b50/docs/guide/release-notes/v0.3.2.md>)
- Kind/ref: release; a0af23c4c4356e4cab2fbea2333f2398a6b03b50
- Sections inspected: Complete release notes
- Establishes: Date imports, duplicate keeper handling, maps, motion photos and calendar navigation.

### R19-S6

[v0.3.0 release notes](<https://github.com/julyx10/lap/blob/a0af23c4c4356e4cab2fbea2333f2398a6b03b50/docs/guide/release-notes/v0.3.0.md>)
- Kind/ref: release; a0af23c4c4356e4cab2fbea2333f2398a6b03b50
- Sections inspected: Complete release notes
- Establishes: Smart albums, collections, Live Photo grouping, virtualization and generated-image prompts.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
