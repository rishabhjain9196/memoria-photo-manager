# R43 — HoshinoSuzumi/chronoframe

[Repository](<https://github.com/HoshinoSuzumi/chronoframe>) · 1,975 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Self-hosted photography gallery emphasizing timeline/album/map presentation, large-image viewing, Live Photos and web-based upload administration.

**Deployment:** Recommended self-hosted Docker image; Node.js 22 source deployment; Separate ChronoFrame Cloud hosted offering

**Storage:** Mounted data directory holds database, settings, session secret and local photos; dashboard uploads generate previews and indexing data. Supports multiple configured local/S3/OpenList storage schemes but switching the default affects future uploads only, not existing originals.

**Privacy/network behavior:** Self-hosted local storage is supported. Optional map tiles and reverse geocoding call MapTiler/Mapbox/Nominatim services, OAuth contacts GitHub and custom analytics can introduce tracking. Hidden/password albums protect application routes, not already public object-storage/CDN URLs; docs recommend local storage for protected files.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v1.2.0 (2026-11-09T06:26:05Z)
**Repository pushed at:** 2026-11-09T09:13:44Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [3f44c6b8d106](<https://github.com/HoshinoSuzumi/chronoframe/commit/3f44c6b8d10625698889bfe610a690e4e2379f98>).
**Product lineage:** HoshinoSuzumi/chronoframe.

## Maturity and availability caveats

- Frozen commit 3f44c6b8d10625698889bfe610a690e4e2379f98; latest v1.2.0 release published 2026-11-09.
- v1.0 introduced setup/database-managed settings and migration from earlier environment configuration; old configuration guides are explicitly archived.
- Current license is AGPL-3.0-only for application, with MIT exceptions for contracts/WebGL packages; hosted Cloud is separate from self-hosted deployment.
- No live demo was contacted and no uploaded private media was used.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Custom album slugs with redirects**<br>`albums.custom_urls` | C | Self-hosted titles generate slugs; numeric links redirect to current slug and historical slugs temporarily redirect. Renaming title alone keeps URL; editing/clearing frees the old slug for reassignment. | [R43-S2](<#r43-s2>) |
| **Create and reorder albums**<br>`albums.manual` | C | Organize albums and order photos inside them; batch Add to album skips items already in the target album. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Optional analytics scripts**<br>`analytics.custom_scripts` | O | Dashboard accepts custom tracking scripts in head/body; operators control the added privacy implications. | [R43-S2](<#r43-s2>) |
| **Customizable photo management table**<br>`browse.admin_table` | C | Admin table supports sorting/filtering, persistent visible-column choice, upload-date sorting and Shift-click range selection. | [R43-S2](<#r43-s2>) |
| **Masonry gallery**<br>`browse.grid` | C | Photo wall uses masonry presentation with filters/sorting; header can be embedded in the wall or fixed during scrolling. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Image histogram display**<br>`browse.histogram` | C | README photo-browsing feature list explicitly includes histograms. | [R43-S1](<#r43-s1>) |
| **Time-oriented browsing**<br>`browse.timeline` | C | README explicitly supports browsing by time; v1.2 release preserves mobile date-range controls while redesigning the header. | [R43-S1](<#r43-s1>), [R43-S6](<#r43-s6>) |
| **Mobile interaction and live playback**<br>`browse.touch` | C | Live/Motion assets play on hover or long press; v1.2 updates mobile gallery controls and accessible header behavior. | [R43-S1](<#r43-s1>), [R43-S6](<#r43-s6>) |
| **WebGL large-image viewer**<br>`browse.zoom` | C | Viewer provides pan/zoom and tiled rendering for large images, not merely a precomputed thumbnail grid. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Managed Cloud alternative**<br>`deployment.managed_cloud` | O | README links a separate sign-up hosted service for creating galleries without maintaining a server; inspected material does not establish pricing or entitlement limits. | [R43-S1](<#r43-s1>) |
| **Persistent Docker deployment**<br>`deployment.docker` | C | README recommends published Docker/Compose images with the data directory mounted for database, settings, session secret and local photos; this is a web-server deployment. | [R43-S1](<#r43-s1>), [R43-S5](<#r43-s5>) |
| **Dashboard language switching**<br>`deployment.localization` | C | README explicitly lists dashboard language switching as an application feature. Exact supported interface-language list is not specified in the inspected source; separate place-name language settings and translated README files are not treated as UI-localization evidence. | [R43-S1](<#r43-s1>) |
| **Self-hosted browser gallery**<br>`deployment.selfhosted` | C | Admin/browser UI and public gallery run on an operator-controlled server; Docker image with persistent data mount is recommended. | [R43-S1](<#r43-s1>) |
| **Browser gallery and dashboard**<br>`deployment.web` | C | Visitors browse the web gallery and administrators sign in to /dashboard for uploads, albums and configuration; setup is also browser-based. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **HEIC/HEIF image ingestion**<br>`formats.heic` | C | Documented image inputs include HEIC/HEIF alongside JPEG, PNG, WebP, GIF, BMP and TIFF. | [R43-S1](<#r43-s1>) |
| **Filename-paired Apple Live Photos**<br>`formats.live_photos` | C | Matches image and MOV sharing basename; either upload order works and pairing can be retried in dashboard. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Embedded Motion Photo playback**<br>`formats.motion_photos` | C | Supports embedded-video Motion Photos with hover/long-press playback; separate from image/MOV pair matching. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Configurable interactive map**<br>`geo.map` | O | Choose MapLibre with built-in MapTiler data or Mapbox, requiring appropriate tokens unless a custom MapLibre style is supplied. Photos need existing GPS; enabling maps cannot invent coordinates. | [R43-S4](<#r43-s4>) |
| **City/country place-name lookup**<br>`geo.online_geocoding` | O | Mapbox or Nominatim performs reverse geocoding separately from browser tile rendering; configurable language affects future lookups, and existing names require reindexing. | [R43-S4](<#r43-s4>) |
| **Custom map and geocoder endpoints**<br>`geo.selfhosted_services` | O | Custom MapLibre Style JSON can reference self-hosted tiles/fonts/sprites with browser CORS; Nominatim URL can target a self-hosted service/proxy. This is not a bundled offline basemap or geocoder. | [R43-S4](<#r43-s4>) |
| **Separate image-serving CDN URLs**<br>`integration.cdn_urls` | O | Remote storage can provide a separate CDN read base URL; R2 S3 upload endpoint must not be confused with its public image domain. | [R43-S3](<#r43-s3>) |
| **Optional GitHub administrator login**<br>`integration.oauth` | O | Email/password is established at setup; GitHub OAuth requires configured client credentials and returned email matching an existing administrator, not arbitrary GitHub-user admin access. | [R43-S2](<#r43-s2>) |
| **S3-compatible backends**<br>`integration.object_storage` | O | Supports endpoint/bucket/region/prefix/credentials/path-style/CDN URL configuration with examples for AWS S3, R2, OSS, COS and MinIO; browser direct uploads need CORS and multipart ETag exposure. | [R43-S3](<#r43-s3>) |
| **OpenList storage integration**<br>`integration.openlist` | O | Uses OpenList API token/root and configurable upload/delete/metadata endpoints; remote permissions and expiring download URLs affect accessibility. | [R43-S3](<#r43-s3>) |
| **Browser-first setup and settings**<br>`integration.setup_wizard` | C | Wizard creates an administrator and chooses site/storage; everyday settings persist in database and can be changed without rebuilding containers or editing .env. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Skip duplicate upload while adding album membership**<br>`library.deduplicate_import` | C | When duplicate handling is Skip, an already existing photo is added to the chosen album without uploading another file. Documentation does not specify the identity algorithm. | [R43-S2](<#r43-s2>) |
| **Scan media already in storage**<br>`library.existing_folders` | R | Storage guide explicitly says directly copied/uploaded backend files do not appear automatically and scanning/importing existing storage is planned. | [R43-S3](<#r43-s3>) |
| **Original and batch downloads**<br>`library.export_originals` | C | Public viewer offers original downloads and dashboard selection supports batch download; exact archive format is not established by inspected guide. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Batch and drag-and-drop uploads**<br>`library.import_copy` | C | Dashboard photo page accepts selected/dropped batches, optionally targeted to an album; successfully processed photos join the selected album. | [R43-S2](<#r43-s2>) |
| **Manage multiple storage schemes**<br>`library.storage_schemes` | C | Dashboard adds/edits/selects local, S3 and OpenList schemes. Changing active scheme affects new uploads only; this is not multiple independent user-selectable catalogues. | [R43-S2](<#r43-s2>), [R43-S3](<#r43-s3>) |
| **Startup database migrations**<br>`maintenance.automatic_migrations` | C | Migrations run automatically; current runtime image has no shell/package manager, and older manual in-container migration instructions no longer apply. | [R43-S5](<#r43-s5>) |
| **Live logs and recent activity**<br>`maintenance.diagnostics` | C | Dashboard exposes task errors/retries, live logs and activity; logs are not documented as a crash-recovery file operation journal. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Batch reindex and repair**<br>`maintenance.selective_reset` | C | Selected photos can be reindexed, location names rebuilt after language changes and Live Photo pairing retried without claiming a full user-data reset. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>), [R43-S4](<#r43-s4>) |
| **Edit title and description**<br>`metadata.comments` | C | Dashboard edits descriptive metadata; inspected guides do not establish embedded-file write-back. | [R43-S2](<#r43-s2>) |
| **Automatic EXIF extraction**<br>`metadata.exif_read` | C | Upload queue extracts EXIF and shooting coordinates, generates previews and resolves locations. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Photo ratings**<br>`metadata.ratings` | C | Rating is explicitly editable alongside title and description in dashboard. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Remove photo location data**<br>`metadata.strip` | C | Privacy setting automatically strips location from future uploads; existing photos require individual/batch removal jobs and queue-completion confirmation. This is not a claim to remove every identifying field. | [R43-S2](<#r43-s2>) |
| **Processing task queue**<br>`performance.background_jobs` | C | EXIF, thumbnails, locations and Live Photo pairing run after uploads; dashboard reports task progress/errors and failed-task retries. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Documented whole-instance backup**<br>`safety.catalogue_backup` | C | Update guide requires stopping container and backing up complete data, Compose, legacy environment and separately stored local/remote media. Rollback restores pre-upgrade database and files, not just an older image. | [R43-S5](<#r43-s5>) |
| **Password-protected albums**<br>`sharing.password_links` | C | Minimum six-character album password; visitors must unlock application access. External public image URLs remain outside this protection. | [R43-S2](<#r43-s2>), [R43-S3](<#r43-s3>) |
| **Public gallery and scoped photo shares**<br>`sharing.public_links` | C | README includes share previews; photo shares retain album access scope. Hidden-album membership restricts anonymous photo access even when the same photo also belongs to a public album. | [R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>) |
| **Configurable gallery reactions**<br>`sharing.reactions` | C | v1.2 release adds controls to disable gallery reactions; precise reaction types are not stated in inspected note. | [R43-S6](<#r43-s6>) |

## Limitations and evidence gaps

- **explicit:** Direct storage copying is not an ingestion path; scan/import of existing backend media is explicitly planned. ([R43-S3](<#r43-s3>))
- **explicit:** Changing storage does not migrate files. Keep old schemes/paths reachable and back up remote stores separately. ([R43-S2](<#r43-s2>), [R43-S3](<#r43-s3>), [R43-S5](<#r43-s5>))
- **explicit:** Public S3/OpenList/CDN links bypass album-password enforcement and caches are not revoked by password changes; guide recommends local storage for protected albums. ([R43-S2](<#r43-s2>), [R43-S3](<#r43-s3>))
- **explicit:** Hidden membership overrides anonymous access even through another public album; freed slugs may be reused and old links can then open a different album. ([R43-S2](<#r43-s2>))
- **explicit:** Location stripping at upload affects future files only; check older files, descriptions and tags separately. Map providers need credentials/network or separately provisioned custom infrastructure. ([R43-S2](<#r43-s2>), [R43-S4](<#r43-s4>))
- **coverage-gap:** No face recognition, perceptual duplicate scan, mobile backup, application trash, operation journal or encryption guarantee was established. ([R43-S1](<#r43-s1>), [R43-S2](<#r43-s2>), [R43-S3](<#r43-s3>))
- **Coverage gap:** Duplicate identity algorithm and fine-grained search fields are not specified in inspected user guides.
- **Coverage gap:** Cloud pricing/entitlements and arbitrary standalone-video playback were not established.
- **Coverage gap:** Offline map packs, AI and recoverable file operations are not documented.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R43-S1

[ChronoFrame README](<https://github.com/HoshinoSuzumi/chronoframe/blob/3f44c6b8d10625698889bfe610a690e4e2379f98/README.md>)
- Kind/ref: readme; 3f44c6b8d10625698889bfe610a690e4e2379f98
- Sections inspected: Complete README
- Establishes: Gallery capabilities, formats, deployment, privacy boundary and Cloud alternative.

### R43-S2

[Using ChronoFrame](<https://github.com/HoshinoSuzumi/chronoframe/blob/3f44c6b8d10625698889bfe610a690e4e2379f98/docs/guide/usage.md>)
- Kind/ref: manual; 3f44c6b8d10625698889bfe610a690e4e2379f98
- Sections inspected: Complete guide
- Establishes: Upload/batch workflows, duplicate handling, visibility, URL semantics, privacy cleanup and OAuth restrictions.

### R43-S3

[Storage schemes](<https://github.com/HoshinoSuzumi/chronoframe/blob/3f44c6b8d10625698889bfe610a690e4e2379f98/docs/configuration/storage-providers.md>)
- Kind/ref: manual; 3f44c6b8d10625698889bfe610a690e4e2379f98
- Sections inspected: Complete guide
- Establishes: Local/S3/OpenList setup, multipart/CORS and public direct-URL caveats; existing-storage scan roadmap.

### R43-S4

[Maps and locations](<https://github.com/HoshinoSuzumi/chronoframe/blob/3f44c6b8d10625698889bfe610a690e4e2379f98/docs/configuration/map-providers.md>)
- Kind/ref: manual; 3f44c6b8d10625698889bfe610a690e4e2379f98
- Sections inspected: Complete guide
- Establishes: Renderer versus map data, custom styles, geocoder tokens/languages and provider dependencies.

### R43-S5

[Update and backup guide](<https://github.com/HoshinoSuzumi/chronoframe/blob/3f44c6b8d10625698889bfe610a690e4e2379f98/docs/guide/updates.md>)
- Kind/ref: manual; 3f44c6b8d10625698889bfe610a690e4e2379f98
- Sections inspected: Complete guide
- Establishes: Backup scope, automatic migrations, v1 transition and full-database rollback.

### R43-S6

[v1.2.0 release](<https://github.com/HoshinoSuzumi/chronoframe/releases/tag/v1.2.0>)
- Kind/ref: release; v1.2.0
- Sections inspected: Complete release note
- Establishes: Mobile/header controls and configurable gallery reactions.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
