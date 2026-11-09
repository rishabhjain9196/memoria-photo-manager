# R42 — bpatrik/pigallery2

[Repository](<https://github.com/bpatrik/pigallery2>) · 2,315 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Directory-first self-hosted web gallery for browsing existing media with rich structured search, metadata-derived people/maps, scoped shares and scheduled derivative generation.

**Deployment:** Officially recommended Docker on low-resource servers including Raspberry Pi; Native Node.js installation possible but explicitly unsupported

**Storage:** Source directory tree is the source of truth; SQLite (recommended) or MySQL index is treated as rebuildable cache. Thumbnails, converted photos/videos and job data use separate writable locations. Core browsing is read-only, but explicitly enabled uploads write new files to the source directory.

**Privacy/network behavior:** Self-hosted originals with configurable authentication, roles and media/directory allow/block queries. Optional OIDC provider and online map tile/geocoding services add network dependencies. Reads externally assigned face metadata rather than claiming face recognition; shares cannot exceed creator access.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 3.5.2 (2026-01-24T20:20:16Z)
**Repository pushed at:** 2026-11-09T14:23:45Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [aea3bd3e5bb7](<https://github.com/bpatrik/pigallery2/commit/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c>).
**Product lineage:** bpatrik/pigallery2.

## Maturity and availability caveats

- Manifest release 3.5.2 (2026-01-24), pinned master aea3bd3e5bb77104dabc9adddbfaa1d5875c776c contains later documentation/settings.
- FAQ says no database upgrade scripts and no fixed release schedule; breaking changes can require resetting DB/config.
- README says source folder is never modified, but feature manual/release and UploadManager establish opt-in uploads; read-only claim applies to browsing, not every enabled operation.
- Feature/release prose says ORCID, while detailed config explicitly implements OIDC; generic OIDC is the precise supported claim.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Theme/color modes**<br>`browse.dark_theme` | C | Configurable automatic theme mode, selected theme and custom CSS theme definitions. | [R42-S5](<#r42-s5>) |
| **Hierarchy and optional flattened browsing**<br>`browse.folders` | C | Directory navigation includes recursive subfolders; optional flatten button lists all descendants, with documented same-path limitation. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Photo/video lightbox**<br>`browse.fullscreen` | C | Fullscreen viewer includes EXIF panel, captions/face overlays, low-resolution placeholder before full image and keyboard/swipe navigation. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Responsive on-scroll photo grid**<br>`browse.grid` | C | Phone/tablet/desktop grid renders on demand while scrolling and prioritizes visible thumbnails; no stronger virtualized-row guarantee is inferred. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Folder-local dated Markdown stories**<br>`browse.markdown_stories` | C | Displays .md files near gallery/map; pg-date comments attach sections to dates, enabling narrative photo presentation. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Query-driven photo-frame mode**<br>`browse.photo_frame_links` | C | Generates a looping display link for a directory or search, suitable for kiosk apps; recurring-date queries can produce anniversary frames. | [R42-S2](<#r42-s2>), [R42-S6](<#r42-s6>) |
| **Automatic lightbox slideshow**<br>`browse.slideshow` | C | Configurable interval (default five seconds), loop slideshow and separate video loop controls. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Date grouping with timezone policy**<br>`browse.timeline` | C | Photo/search default grouping is date; configurable timestamp-offset handling uses local wall-clock time or global time, assuming UTC where offset missing. | [R42-S5](<#r42-s5>) |
| **Browser video playback**<br>`browse.video_playback` | C | Direct formats MP4/WebM/OGV/OGG; other listed formats such as MKV/MOV/AVI require conversion. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Full-resolution on zoom**<br>`browse.zoom` | C | Lightbox can load original resolution when zoomed or cached previews are too small. | [R42-S5](<#r42-s5>) |
| **Official Docker deployment**<br>`deployment.docker` | C | Docker is official/recommended; native Node.js installation is possible but unsupported. | [R42-S1](<#r42-s1>) |
| **Translated web interface**<br>`deployment.localization` | C | Detailed feature manual explicitly lists internationalization with full translation support; it does not enumerate every available language or establish complete translation of every current string. | [R42-S2](<#r42-s2>) |
| **Self-hosted directory gallery**<br>`deployment.selfhosted` | C | Browser interface points at an existing photo tree and is intended for low-resource hardware; speed is a project claim, not a measured benchmark. | [R42-S1](<#r42-s1>), [R42-S2](<#r42-s2>) |
| **Responsive browser gallery**<br>`deployment.web` | C | PiGallery2 is explicitly a photo-gallery website with a responsive interface for phone, tablet and desktop browsers; Docker is the recommended server deployment rather than a native client-app distribution. | [R42-S1](<#r42-s1>), [R42-S2](<#r42-s2>) |
| **Possible duplicates by metadata**<br>`duplicates.metadata_candidates` | C | Admin-only duplicate view groups equal name+size or creation-date+size and merges overlapping groups; default listing limit 1000. No hashes, byte comparison or perceptual similarity are used in examined method. | [R42-S4](<#r42-s4>), [R42-S5](<#r42-s5>), [R42-S8](<#r42-s8>) |
| **FFmpeg derivative transcoding**<br>`editing.video_transcode` | C | Produces MP4 or WebM, with configurable bitrate, height, FPS, codecs, CRF, preset and custom input/output flags; thumbnails use ffmpeg/ffprobe. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Animated GIF derivative support**<br>`formats.animated` | C | animateGif converts GIF to animated WebP and defaults on. | [R42-S5](<#r42-s5>) |
| **AVIF configured format**<br>`formats.avif` | C | Current supported-photo list includes AVIF with browser/Sharp capability caveat. | [R42-S5](<#r42-s5>) |
| **Conditional HEIC rendering**<br>`formats.heic` | C | HEIC is listed with container/libvips compatibility caveat and browser/Sharp conversion requirements. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Apple Live Photo pairing**<br>`formats.live_photos` | C | Current config enables pairing still image and companion video by Content Identifier metadata; pinned-branch feature may postdate manifest release. | [R42-S5](<#r42-s5>) |
| **Conditional DNG/ARW support**<br>`formats.raw` | C | Feature list marks DNG/ARW support dependent on container libvips build; not a universal camera RAW decoder guarantee. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **SVG viewing with upload restriction**<br>`formats.svg` | C | SVG is in viewing format list but blocked for uploads by default because SVG can contain scripts. | [R42-S5](<#r42-s5>) |
| **Map photos via pluggable tile providers**<br>`geo.map` | C | Uses OpenStreetMap or configured Mapbox/custom tile URLs, with photo markers and clickable full-view photos; Mapbox requires token. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>), [R42-S6](<#r42-s6>) |
| **GPX routes with activity styles**<br>`geo.track_overlay` | C | Displays GPX paths and differentiates activities such as running/flying with colors/icons; configurable path bending handles long flight segments. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Lossy GPX compression**<br>`geo.track_simplification` | C | On-demand/scheduled compression removes too-close or near-collinear points using distance, temporal spacing and deviation thresholds. | [R42-S5](<#r42-s5>) |
| **Server-side extension system**<br>`integration.plugins` | P | Separate server.js extensions receive lifecycle/config/REST hooks and limited photo UI buttons; configured dependency installation may run at initialization and repository discovery reads an online list. | [R42-S2](<#r42-s2>), [R42-S9](<#r42-s9>) |
| **Random image endpoint links**<br>`integration.random_photo_url` | C | Creates a URL serving a random photo, useful for external wallpaper/photo-frame applications and subject to user rights. | [R42-S2](<#r42-s2>), [R42-S4](<#r42-s4>) |
| **In-place directory indexing**<br>`library.existing_folders` | C | Shows the original folder hierarchy recursively without mandatory reimport; database is a cache, not the authority for source organization. | [R42-S1](<#r42-s1>), [R42-S2](<#r42-s2>), [R42-S3](<#r42-s3>) |
| **ZIP download of visible results**<br>`library.export_originals` | C | Config enables zipped download of listed directory or search results. | [R42-S5](<#r42-s5>) |
| **Folder/file exclusion rules**<br>`library.exclude_folders` | C | Skip folder names/paths/globs, folders containing marker files, or photo/video filename globs; matching is case-sensitive and default excludes common trash directories. | [R42-S5](<#r42-s5>) |
| **Demand/scheduled reindexing**<br>`library.incremental_scan` | C | Cached-folder timeout and reindex sensitivity control scans; never mode indexes only unseen folders or explicit jobs, and scheduled default indexing processes changes only. | [R42-S5](<#r42-s5>) |
| **Opt-in directory uploads**<br>`library.managed_upload` | C | Disabled by default, minimum role Admin by default; optional .uploader.pg2conf requirement whitelists target directories, with blocked extensions and per-file errors. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>), [R42-S7](<#r42-s7>) |
| **Technical metadata panel**<br>`metadata.exif_read` | C | Viewer displays EXIF, tags/keywords, locations and GPS read from files. | [R42-S2](<#r42-s2>) |
| **IPTC captions in display**<br>`metadata.iptc_read` | C | captionFirstNaming optionally displays IPTC 120 caption instead of filenames; not metadata-writing support. | [R42-S5](<#r42-s5>) |
| **Imported face-region metadata**<br>`metadata.xmp_read` | C | Reads Adobe XMP face regions, draws bounding boxes and exposes people browsing/search. Does not perform automatic face detection/recognition according to inspected evidence. | [R42-S2](<#r42-s2>) |
| **Scheduled processing chains**<br>`performance.background_jobs` | C | Schedules indexing, cover filling, photo/video conversion, GPX compression and temp cleanup with after-job dependencies, bounded database batches and retained progress history. | [R42-S5](<#r42-s5>) |
| **Optional gallery auto-refresh**<br>`performance.gallery_polling` | C | AutoUpdate polls for new photos/videos at configurable interval, default 60 seconds when enabled; not a filesystem event watcher. | [R42-S5](<#r42-s5>) |
| **Concurrent thumbnail generation**<br>`performance.parallel_thumbnails` | C | Thumbnail workers default to CPU count minus one with configurable concurrency cap; this is derivative processing, not a claim of parallel scanning or perceptual matching. | [R42-S5](<#r42-s5>) |
| **Multisize cached derivatives**<br>`performance.thumbnail_cache` | C | On-demand thumbnail/preview sizes default 320/540/1080/2160, persisted outside originals with visible-photo priority; more sizes trade CPU/storage for quality. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Reject existing upload destinations**<br>`safety.no_overwrite` | C | Upload validates plain filename/root containment and rejects existing path with FileAlreadyExists before writing; no claim of race-proof transactional writes. | [R42-S7](<#r42-s7>) |
| **Read-only browsing pipeline**<br>`safety.read_only_originals` | C | Original media folder needs read permission; derived assets go to separate writable temp folder. Explicit upload mode is an exception that adds files. | [R42-S1](<#r42-s1>), [R42-S5](<#r42-s5>), [R42-S7](<#r42-s7>) |
| **Structured boolean/range queries**<br>`search.boolean` | C | Exact/wildcard and negated filters, AND/OR, comparator ranges and n-of expressions; autocomplete suggests files/directories/captions/places/people/keywords. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Date ranges and recurring memories**<br>`search.date_range` | C | Date ranges and relative recurring windows such as last four days every week/month/year or a shifted past period are documented. | [R42-S2](<#r42-s2>) |
| **Resolution/orientation filters**<br>`search.dimensions` | C | Resolution query uses megapixels with ranges/comparators; portrait/landscape orientation queries also supported. | [R42-S2](<#r42-s2>) |
| **Filename/directory/caption search**<br>`search.filename_path` | C | file_name, directory, caption and any_text queries support exact or wildcard forms; directory glob /* includes the directory and all descendants. | [R42-S2](<#r42-s2>), [R42-S4](<#r42-s4>) |
| **Refine the open directory or search result**<br>`search.local_result_filters` | C | Feature manual describes a local filter panel that further narrows the current directory or search results, distinct from submitting the full structured query language. | [R42-S2](<#r42-s2>) |
| **Place names and distance queries**<br>`search.location` | C | Position searches city/state/country; distance forms such as 5-km-from:(New York) query nearby photos. | [R42-S2](<#r42-s2>) |
| **Person names and face count filters**<br>`search.people` | C | person name queries and person-count numeric ranges search imported face metadata; faces tab access and starring require configurable roles. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Metadata rating filters**<br>`search.ratings` | C | Supports equality, ranges, comparisons and negation on ratings read from media; does not establish rating editing. | [R42-S2](<#r42-s2>) |
| **Logical albums**<br>`search.saved_queries` | C | Any search query can be saved as a logical album; .pg2conf is used for saved search/config behavior, distinct from conventional database-only manual albums. | [R42-S2](<#r42-s2>), [R42-S3](<#r42-s3>), [R42-S5](<#r42-s5>) |
| **Keyword metadata search**<br>`search.tags` | C | keyword searches can drive logical albums; FAQ suggests assigning unique keywords in external Lightroom/digiKam rather than editing them here. | [R42-S2](<#r42-s2>), [R42-S3](<#r42-s3>) |
| **Built-in accounts**<br>`sharing.multiuser` | C | Authentication/user management configurable; roles include Limited Guest, Guest, User, Admin and Developer, with sharing users constrained separately. | [R42-S4](<#r42-s4>), [R42-S5](<#r42-s5>) |
| **Optional OIDC login**<br>`integration.oidc` | O | Issuer/client/scopes/claims, allowed email domains, optional account creation and default role are configurable; strict linking can bind identity and cap eligible roles. | [R42-S5](<#r42-s5>) |
| **Password-protected shares**<br>`sharing.password_links` | C | Links optionally require passwords, and instance policy can require passwords for all shares. | [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>) |
| **Scoped directory/search links**<br>`sharing.public_links` | C | Share a folder with optional descendants or search results; effective access intersects share query with creator media/directory permissions, not merely opening-page scope. | [R42-S2](<#r42-s2>), [R42-S4](<#r42-s4>) |
| **Role capabilities and visibility rules**<br>`sharing.roles` | C | Admins manage settings/duplicate view; Users can share/list faces/random links. Per-user/global media and directory allow/block queries are independent; block wins and unavailable paths return 404. | [R42-S4](<#r42-s4>) |
| **Per-directory name/date/random sorting**<br>`sort.filename` | C | Empty .order_\[ORDER\].pg2conf overrides only that folder, choosing ascending/descending name/date or random; not recursive. | [R42-S2](<#r42-s2>) |

## Limitations and evidence gaps

- **explicit:** No database migrations are provided; release 3.5.2 warns search changes can break saved queries, shares/random links and config, and photo-button extension contracts changed. ([R42-S3](<#r42-s3>), [R42-S6](<#r42-s6>))
- **explicit:** Read-only browsing does not mean an instance with uploads enabled cannot write original folders; upload defaults off and must be permission/whitelist configured. ([R42-S1](<#r42-s1>), [R42-S5](<#r42-s5>), [R42-S7](<#r42-s7>))
- **explicit:** Duplicate candidates are metadata heuristics, not verified content equality; imported face regions are not machine recognition. ([R42-S2](<#r42-s2>), [R42-S8](<#r42-s8>))
- **explicit:** Metafiles are visible whenever their directory is available even if media filters hide photos; block the directory to hide its Markdown/GPX/config files. ([R42-S4](<#r42-s4>))
- **explicit:** Default search caps are 10,000 media and 200 directories. RAW/HEIC depend on libvips/browser conversion support. Disabled authentication defaults to Admin role unless changed. ([R42-S5](<#r42-s5>))
- **coverage-gap:** No inspected evidence establishes E2EE, guaranteed offline maps/geocoding, destructive duplicate cleanup, trash/undo, or built-in face recognition. ([R42-S1](<#r42-s1>), [R42-S2](<#r42-s2>), [R42-S5](<#r42-s5>), [R42-S8](<#r42-s8>))
- **Coverage gap:** Configuration decorative SVG and duplicate JSON representations omitted; functional option groups read.
- **Coverage gap:** Share expiry not established in inspected manual and not inferred.
- **Coverage gap:** No runtime performance or deployment tests; current-branch additions distinguished from release.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R42-S1

[PiGallery2 README](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/README.md>)
- Kind/ref: readme; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Complete key features and installation/support guidance
- Establishes: Directory-first/read-only philosophy, Docker recommendation and unsupported native installation.

### R42-S2

[Feature manual](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/docs/features.md>)
- Kind/ref: manual; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Complete key features, query examples and detailed feature list
- Establishes: Viewer, search, sharing, maps/GPX, logical albums, XMP people, blog/photo-frame and formats.

### R42-S3

[FAQ](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/docs/faq.md>)
- Kind/ref: manual; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Complete FAQ
- Establishes: Cache-only database philosophy, album design and migration/release constraints.

### R42-S4

[User rights and sharing](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/docs/user-guide/user-rights.md>)
- Kind/ref: manual; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Complete roles, allow/block queries, directory states and sharing behavior
- Establishes: Per-user filtering, parent navigation, metadata-file exposure and share scoping.

### R42-S5

[Configuration manual](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/docs/user-guide/configuration.md>)
- Kind/ref: manual; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Configuration introduction; complete option entries for Users, Gallery, Media, MetaFile, Album, Search, Sharing, Map, Faces, Upload, Database, Indexing, AlbumCover, Duplicates and Jobs; repeated JSON and decorative SVG omitted
- Establishes: Defaults/limits, OIDC, viewer settings, live photos, uploads, indexing and scheduling.

### R42-S6

[Release 3.5.2](<https://github.com/bpatrik/pigallery2/releases/tag/3.5.2>)
- Kind/ref: release; 3.5.2
- Sections inspected: Complete release notes
- Establishes: Photo frame, uploads, search improvements and breaking DB/config/sharing/extension changes.

### R42-S7

[Upload implementation](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/src/backend/model/UploadManager.ts>)
- Kind/ref: code; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Complete file
- Establishes: Opt-in writes, directory whitelist, filename/extension checks and existing-file refusal.

### R42-S8

[Possible-duplicate implementation](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/src/backend/model/database/GalleryManager.ts>)
- Kind/ref: code; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Complete getPossibleDuplicates method, lines 184-291
- Establishes: Candidate grouping is equal filename+size or creation date+size, not hashing or perceptual matching.

### R42-S9

[Extension manual](<https://github.com/bpatrik/pigallery2/blob/aea3bd3e5bb77104dabc9adddbfaa1d5875c776c/docs/development/extensions.md>)
- Kind/ref: manual; aea3bd3e5bb77104dabc9adddbfaa1d5875c776c
- Sections inspected: Complete installation, lifecycle, exposed API and discovery documentation
- Establishes: Server extensions, dependencies, init/cleanup and photo-button integration.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
