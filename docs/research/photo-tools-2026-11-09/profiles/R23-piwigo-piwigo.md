# R23 — Piwigo/Piwigo

[Repository](<https://github.com/Piwigo/Piwigo>) · 3,882 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Extensible self-hosted web media library with hierarchical albums, strong batch management and sharing; many advanced DAM, playback and contribution workflows require named plugins or Cloud plan entitlements.

**Deployment:** Self-hosted PHP/MySQL or MariaDB web application; Documented Docker installation; Commercial Piwigo Cloud; Separate Android/iOS upload clients

**Storage:** Server-hosted originals, database catalogue and on-demand configurable image derivatives. FTP synchronization maps files under galleries into physical albums; normal uploads use managed storage. One asset can belong to multiple virtual albums without file duplication. Extra file formats can be attached to a primary image.

**Privacy/network behavior:** Self-hosting allows chosen infrastructure; Cloud is a separate operated service with advertised French hosting and backups. Access uses public/private albums, user/group permissions, per-image privacy levels and download controls. Optional external video embeds, social scripts and AI integrations contact other services; no E2EE or air-gap guarantee is established.

**License metadata:** GPL-2.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 16.4.0 (2026-05-03T14:54:31Z)
**Repository pushed at:** 2026-11-05T14:55:51Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [7547b1bdb00a](<https://github.com/Piwigo/Piwigo/commit/7547b1bdb00a531a613042b9142493f19f64c6ce>).
**Product lineage:** Piwigo/Piwigo.

## Maturity and availability caveats

- Frozen commit 7547b1bdb00a531a613042b9142493f19f64c6ce; latest frozen release 16.4.0 (2026-05-03).
- Official live documentation mixes self-hosted and Cloud. Team/Enterprise restrictions quoted here apply to Cloud plans, not automatically to self-hosted plugin licensing.
- Release 16.4.0 includes API-key and original-URL fixes plus other fixes; live manuals can describe features beyond the frozen release.
- Marketing advertises AI tagging/OCR/captioning and maps without fully establishing installation/edition conditions; these are not silently attributed to repository core.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **AI-generated indexing tags**<br>`ai.auto_tags` | ? | Official page advertises tagging through Piwigo-operated AI and separately mentions Imagga/Azure integrations; repository-core availability and entitlement are not established. | [R23-S2](<#r23-s2>) |
| **Generated descriptions**<br>`ai.captioning` | ? | Official feature page advertises editable AI descriptions but does not clarify whether this is a Cloud entitlement or self-hostable module. | [R23-S2](<#r23-s2>) |
| **Recognize and group people**<br>`ai.face_recognition` | R | Official feature page explicitly says face recognition is coming soon. | [R23-S2](<#r23-s2>) |
| **Extract text from images**<br>`ai.ocr` | ? | OCR is advertised alongside AI indexing with insufficient deployment/edition detail to count as core. | [R23-S2](<#r23-s2>) |
| **FTP folder-to-album synchronization**<br>`albums.folder_mapping` | C | Self-hosted galleries scan the galleries directory to create albums at arbitrary nesting depth; database sync is required after filesystem changes. Cloud does not offer this method. | [R23-S6](<#r23-s6>) |
| **Many-to-many album membership**<br>`albums.manual` | C | Place one file in several albums without duplicated storage, select representative images and customize ordering. | [R23-S2](<#r23-s2>), [R23-S5](<#r23-s5>) |
| **Unlimited album hierarchy**<br>`albums.nested` | C | Albums/sub-albums can be nested and independently public/private; folder-backed albums have more restrictive physical rename/move workflows. | [R23-S2](<#r23-s2>), [R23-S6](<#r23-s6>) |
| **User-owned reusable selections**<br>`albums.personal_collections` | P | User Collections lets logged-in users maintain unlimited selections separate from albums; admins search/edit/export collections as CSV. Cloud Enterprise+. | [R23-S12](<#r23-s12>) |
| **Scheduled rule-based albums**<br>`albums.smart` | P | SmartAlbums combines all/any criteria including tags, dates, source album, name, dimensions, author and view counts. Defaults to three-day refresh, with manual or after-upload regeneration; not real-time by default. Cloud requires Enterprise+. | [R23-S7](<#r23-s7>) |
| **Visits and activity reporting**<br>`analytics.usage_history` | C | Official overview describes day/month/year visit graphs, activity search and upload/edit/delete logs. These are audit analytics, not rollback-capable file journals. | [R23-S2](<#r23-s2>) |
| **Audio player**<br>`browse.audio_playback` | P | VideoJS also exposes audio playback (including MP3) represented by an icon rather than a video frame. | [R23-S4](<#r23-s4>) |
| **Document previews and PDF reader**<br>`browse.document_preview` | O | Configured PDF/SVG/EPS/TIFF/PSD/AI types can have generated previews; v15 adds an inline PDF reader. Other office formats may be downloadable only with generic icons. Cloud premium formats require Team+. | [R23-S4](<#r23-s4>) |
| **Paged batch selection**<br>`browse.pagination` | C | Batch results default to 20 files with 50/100/all options and page controls. | [R23-S3](<#r23-s3>) |
| **180/360 panorama navigation**<br>`browse.panorama` | P | Panoramas selects special viewing using configurable filename markers, default _180 or _360. | [R23-S4](<#r23-s4>) |
| **Fullscreen selection slideshow**<br>`browse.slideshow` | C | Photo toolbar starts fullscreen slideshow over current album/tag/search selection, rather than always using the entire library. | [R23-S13](<#r23-s13>) |
| **Browser video playback**<br>`browse.video_playback` | P | VideoJS required on self-hosted servers, preactivated in Cloud; listed formats include MP4/M4V/WebM/OGG and configurable player preload/autoplay/loop/style. Uploaded MOV is not generally browser-playable. | [R23-S4](<#r23-s4>) |
| **Magnifying photo detail**<br>`browse.zoom` | P | Loupe adds hover magnification with mouse-wheel zoom; availability is explicitly an installed plugin. | [R23-S13](<#r23-s13>) |
| **Android companion application**<br>`deployment.android` | P | Official feature overview links a separate Piwigo Android mobile app for uploading phone photos to the server; it is a companion, not part of the PHP browser UI. | [R23-S2](<#r23-s2>) |
| **Documented Docker installation**<br>`deployment.docker` | C | README explicitly offers a Docker installation guide for the self-hosted web server; Docker availability does not establish a native Windows/macOS gallery application. | [R23-S1](<#r23-s1>) |
| **iOS companion application**<br>`deployment.ios` | P | Official sources document the separate iOS upload app, including converting MOV videos to MP4 during transfer; mobile companion availability is distinct from the server's web deployment. | [R23-S2](<#r23-s2>), [R23-S4](<#r23-s4>) |
| **Quick interface-language selector**<br>`deployment.language_switcher` | P | Language Switch adds a flag selector for one-click switching among enabled gallery languages; base per-user language preference works without this convenience plugin. | [R23-S15](<#r23-s15>) |
| **Per-user multilingual interface**<br>`deployment.localization` | C | Official manual documents over 70 interface languages. Administrators enable/disable languages and select the default; users choose a saved personal language that immediately translates menus/buttons. Database titles/descriptions are not automatically translated. | [R23-S14](<#r23-s14>), [R23-S15](<#r23-s15>) |
| **Managed Piwigo Cloud**<br>`deployment.managed_cloud` | $ | Separate hosted offering supplies operated infrastructure, backups and standby replication; advanced features differ by Team/Enterprise/VIP plan. | [R23-S1](<#r23-s1>), [R23-S2](<#r23-s2>), [R23-S4](<#r23-s4>) |
| **Self-hosted web library**<br>`deployment.selfhosted` | C | PHP web application with MySQL/MariaDB and GD or recommended ImageMagick; README links manual and Docker installation. | [R23-S1](<#r23-s1>) |
| **Browser media library**<br>`deployment.web` | C | README defines Piwigo as a photo gallery for the web; official manuals document its browser gallery and online administration panel. | [R23-S1](<#r23-s1>), [R23-S2](<#r23-s2>), [R23-S13](<#r23-s13>) |
| **Attribute duplicate candidates**<br>`duplicates.metadata_candidates` | C | Duplicate prefilter can group matching filenames, capture dates and dimensions, independently or together with checksums; these are not perceptual or necessarily exact duplicates. | [R23-S11](<#r23-s11>) |
| **Checksum duplicate filtering**<br>`duplicates.exact_hash` | C | Pinned batch-manager source supports md5sum matching alongside filename/date/dimension options and excludes null checksums; this goes beyond the manual's older name-only description. | [R23-S11](<#r23-s11>) |
| **Control derivative crop focus**<br>`editing.crop` | C | Center-of-interest tool marks the important region to retain in square/other cropped derivatives; this is not a full destructive original-image editor. | [R23-S9](<#r23-s9>), [R23-S13](<#r23-s13>) |
| **Rotate images**<br>`editing.rotate_flip` | P | Rotate Image adds a Rotate tab to the photo editor. | [R23-S9](<#r23-s9>) |
| **Watermark gallery renditions**<br>`editing.watermark` | C | Configuration selects a custom watermark image and position, commonly transparent PNG, for gallery presentation. | [R23-S13](<#r23-s13>) |
| **Multiple formats per image**<br>`formats.alternate_downloads` | O | enable_formats plus format_ext associates files such as CR2, CMYK JPEG or ZIP in pwg_format with one image. Cloud offers this from Enterprise; storing RAW companions does not prove RAW decoding. | [R23-S4](<#r23-s4>), [R23-S6](<#r23-s6>) |
| **Animated GIF/WebP media**<br>`formats.animated` | O | GIF originals animate while thumbnails can use the first frame; WebP support dates to v14 and may require config/server updates, especially animation. | [R23-S4](<#r23-s4>) |
| **Double-sided image pairs**<br>`formats.front_back_pairs` | P | Back2Front links a reverse-side photo to a front ID, can hide the back from album listings and exposes See back in the viewer. | [R23-S13](<#r23-s13>) |
| **HEIC ingestion and previews**<br>`formats.heic` | O | Since v14 supports HEIC with generated browser-compatible preview; self-hosting must enable all-type upload/extensions and have supporting server codecs. | [R23-S4](<#r23-s4>) |
| **Location browsing**<br>`geo.map` | ? | Official feature page advertises map display and manual coordinates but inspected implementation-specific manuals do not settle plugin/edition/provider requirements. | [R23-S2](<#r23-s2>) |
| **Automation API and external connectors**<br>`integration.api` | C | Official overview exposes API/script integrations; v16.4 fixes API-key token handling and original-protected URL responses. Lightroom/WordPress/auth providers require companion connectors. | [R23-S2](<#r23-s2>), [R23-S14](<#r23-s14>) |
| **Extensible themes and plugins**<br>`integration.plugins` | C | Repository advertises extension ecosystem; manuals name function-specific plugins, and release upgrade tool warns about version incompatibilities. | [R23-S1](<#r23-s1>), [R23-S5](<#r23-s5>), [R23-S14](<#r23-s14>) |
| **Embed hosted videos**<br>`integration.remote_video_embed` | P | Embedded Videos imports URLs or embed code from YouTube/Vimeo/Dailymotion and others, with optional title/tag extraction and player settings; playback depends on those external services. | [R23-S4](<#r23-s4>) |
| **Stage files for later batch actions**<br>`library.selection_baskets` | C | Administrators add individual photos or whole albums to a persistent caddie while browsing, then manage that set through batch manager. | [R23-S3](<#r23-s3>), [R23-S13](<#r23-s13>) |
| **Download selected rendition size**<br>`library.download_size_choice` | P | Download by Size adds size selection to the download action using configured derivatives. | [R23-S13](<#r23-s13>) |
| **Original downloads with permissions**<br>`library.export_originals` | C | Photo download returns original by default if user has Download permission; toolbar can be hidden and viewer sizes restricted. | [R23-S9](<#r23-s9>), [R23-S13](<#r23-s13>) |
| **Web uploads and application imports**<br>`library.import_copy` | C | Web administration uploads media; official overview also lists external clients such as digiKam, Lightroom and Shotwell, which are companion integrations rather than built-in editors. | [R23-S2](<#r23-s2>) |
| **Scoped filesystem and metadata resync**<br>`library.incremental_scan` | C | Synchronize directories only or directories+files, optionally restrict to an album/subtree, include previously synced metadata or overwrite with empty values. | [R23-S6](<#r23-s6>) |
| **Android/iOS upload companions**<br>`library.mobile_upload` | P | Separate mobile apps send photos to the server; cited overview establishes upload, not unrestricted automatic background camera-roll backup. | [R23-S2](<#r23-s2>) |
| **Replace media while keeping properties**<br>`library.replace_existing_asset` | P | Photo Update replaces an original or a non-image representative thumbnail while retaining catalogue properties. | [R23-S9](<#r23-s9>) |
| **Multi-criteria bulk management**<br>`metadata.batch_edit` | C | Batch manager filters then offers whole-page/set/invert/none selection and bulk delete, album association/move/dissociation, tags, author/title/date/privacy and metadata/derivative regeneration; single mode edits per-item values. | [R23-S3](<#r23-s3>) |
| **Descriptions and discussion**<br>`metadata.comments` | C | Editable title/author/description properties accompany optional photo-page comments; visual rich-text editing and multilingual descriptions use FCKEditor/Extended Description plugins. | [R23-S2](<#r23-s2>), [R23-S5](<#r23-s5>), [R23-S13](<#r23-s13>) |
| **Typed custom properties**<br>`metadata.custom_fields` | P | Manage Properties Photos adds text/select/radio/date/EXIF/IPTC-derived properties, ordering/visibility and batch edits; Properties Mass Update adds CSV changes. Cloud Enterprise+. | [R23-S5](<#r23-s5>) |
| **Edit catalogue creation dates**<br>`metadata.date_fix` | C | Creation date can be edited/unset individually or set in batches; changing upload/post date instead requires Posted Date Changer. | [R23-S3](<#r23-s3>), [R23-S5](<#r23-s5>) |
| **Write properties into IPTC**<br>`metadata.embedded_write` | P | Write Metadata writes title, description, authors and tags back into file IPTC; normal property changes are catalogue edits. Cloud Team+. | [R23-S5](<#r23-s5>) |
| **Read and display EXIF**<br>`metadata.exif_read` | C | Imports technical metadata; default display includes camera make/model, capture time and aperture, with configurable additional fields and ability to hide EXIF. | [R23-S5](<#r23-s5>) |
| **Personal favorites**<br>`metadata.favorites` | C | Photo-page heart saves favorites, browsable from Explore/Discover and available as a batch-manager prefilter. | [R23-S3](<#r23-s3>), [R23-S13](<#r23-s13>) |
| **Import IPTC metadata**<br>`metadata.iptc_read` | C | Supports IPTC field mapping into author/title/description/keywords; IPTC display is not enabled by default and requires configuration. | [R23-S5](<#r23-s5>) |
| **Localized EXIF presentation**<br>`metadata.localized_exif_display` | P | Exif View translates displayed EXIF values into the gallery language; it does not rewrite the photo's underlying metadata into a different language. | [R23-S5](<#r23-s5>), [R23-S15](<#r23-s15>) |
| **Language-specific titles and descriptions**<br>`metadata.multilingual_descriptions` | P | Extended Descriptions provides manually authored photo/album title and description variants selected by visitor language, with default/all-language fallbacks. This is separate from translating UI and is not automatic machine translation. | [R23-S5](<#r23-s5>), [R23-S15](<#r23-s15>) |
| **User photo ratings**<br>`metadata.ratings` | C | Official overview includes file rating as a collaboration mechanism; numeric scale details were not established here. | [R23-S2](<#r23-s2>) |
| **License and expiry workflows**<br>`metadata.rights_expiry` | P | Copyrights defines selectable rights; Expiry Date can leave, archive or delete expiring files and notify downloaders/admins before/on expiry. Expiry Date is Cloud Enterprise+. | [R23-S5](<#r23-s5>) |
| **Manage tags and keywords**<br>`metadata.tags` | C | Assign existing/new tags singly or in batch, combine tags for navigation and optionally map incoming metadata into keywords. | [R23-S3](<#r23-s3>), [R23-S5](<#r23-s5>) |
| **On-demand image sizes**<br>`performance.thumbnail_cache` | C | Stores originals and generates configured square/thumbnail/medium and optional sizes on request, with editable dimensions/quality; batch manager can delete/regenerate derivatives. | [R23-S3](<#r23-s3>), [R23-S13](<#r23-s13>) |
| **Preview synchronization**<br>`safety.sync_simulation` | C | Simulation-only mode reports prospective filesystem/database synchronization without applying changes; distinct from a general undo journal. | [R23-S6](<#r23-s6>) |
| **Color-palette search**<br>`search.colors` | P | Color Palette extracts a configurable number of colors and finds images sharing selected colors. Palettes are lazily generated when photos are viewed, so initial coverage is incomplete. | [R23-S13](<#r23-s13>) |
| **Capture and upload date filters**<br>`search.date_range` | C | Preset and custom year/month/day ranges have result counts; capture and post dates are independent filters. | [R23-S10](<#r23-s10>) |
| **Filter dimensions and aspect ratio**<br>`search.dimensions` | C | Width/height bounds and portrait/square/landscape/panorama ratios are available in gallery and batch filtering. | [R23-S3](<#r23-s3>), [R23-S10](<#r23-s10>) |
| **Filter minimum/maximum file size**<br>`search.file_size` | C | Size sliders restrict selection and combine with other criteria; gallery remembers visible filter controls per user, not a documented saved query library. | [R23-S3](<#r23-s3>), [R23-S10](<#r23-s10>) |
| **Filter media extensions**<br>`search.file_type` | C | Multi-criteria bar includes file type, uploader and author alongside album/tag criteria. | [R23-S10](<#r23-s10>) |
| **Search filenames and descriptive fields**<br>`search.filename_path` | C | Quick search covers title, filename, description, tags and photo ID; matching albums/tags appear as navigation results. Users can choose searched fields and all/any words. | [R23-S10](<#r23-s10>) |
| **Search mapped metadata properties**<br>`search.metadata` | O | Raw displayed EXIF/IPTC is not searchable by default; configuration can map metadata such as camera model to tags/properties for filtering. | [R23-S5](<#r23-s5>) |
| **AND/OR tags and related-tag browsing**<br>`search.tags` | C | Filter on all or any selected tags, combine with albums/authors, and search inside an existing album or tag selection. | [R23-S10](<#r23-s10>) |
| **Scoped contributor uploads**<br>`sharing.collaborative_albums` | P | Community grants selected users/groups upload destinations/subtree access, album creation and photo/storage quotas. Low-trust uploads require approval; contributors manage their own pending photos/tags. Cloud Team+. | [R23-S8](<#r23-s8>) |
| **Expiry and revocation of shares**<br>`sharing.expiring_links` | P | User Collections has expiry dates; Private Share offers 1/2 weeks or 1/3 months and admin history/revocation controls. | [R23-S12](<#r23-s12>), [R23-S13](<#r23-s13>) |
| **Anonymous uploads with moderation**<br>`sharing.guest_upload` | P | Community can permit any visitor, including anonymous users, with low/high trust, per-user limits and administrator approval notifications. | [R23-S8](<#r23-s8>) |
| **Users and groups**<br>`sharing.multiuser` | C | Official feature overview documents unlimited user accounts and permission assignment per user or group. Accounts are not separate user-selectable catalogues. | [R23-S2](<#r23-s2>) |
| **Password-protected collection links**<br>`sharing.password_links` | P | User Collections permits a password on generated public collection links; Cloud Enterprise+. | [R23-S12](<#r23-s12>) |
| **Share private-photo or collection links**<br>`sharing.public_links` | P | Private Share generates scoped photo URLs and emails them without granting general gallery access; User Collections separately shares personal selections. Ordinary public galleries remain core. | [R23-S12](<#r23-s12>), [R23-S13](<#r23-s13>) |
| **Album permissions and image privacy levels**<br>`sharing.roles` | C | Public/private albums, user/group access and independent Everybody/Contacts/Friends/Family/Admin image privacy levels combine; original download rights are separately controllable. | [R23-S2](<#r23-s2>), [R23-S3](<#r23-s3>), [R23-S5](<#r23-s5>), [R23-S13](<#r23-s13>) |
| **Social sharing buttons**<br>`sharing.social_export` | P | Social Buttons (or Bootstrap Darkroom theme) offers platform sharing; docs warn disabling light mode introduces platform tracking cookies. | [R23-S13](<#r23-s13>) |

## Limitations and evidence gaps

- **explicit:** Self-hosted defaults accept only JPG/JPEG/GIF according to format manual; other types need configuration/codecs, multimedia playback needs VideoJS and MOV often needs conversion or download. ([R23-S4](<#r23-s4>))
- **explicit:** FTP import is self-hosted only, requires database synchronization after changes and restricts file/directory names to letters, digits, hyphen, underscore and dot. ([R23-S6](<#r23-s6>))
- **explicit:** Displayed EXIF/IPTC fields are not searchable by default; map them into searchable properties. Source-file name editing needs Edit Filename rather than normal retitling. ([R23-S5](<#r23-s5>))
- **explicit:** Duplicate source query warns GROUP_CONCAT truncation can omit members of large groups (roughly 250+ under the documented default); hash filtering needs stored checksums. ([R23-S11](<#r23-s11>))
- **explicit:** SmartAlbums are scheduled, not immediately live by default; color palettes cover only photos processed/viewed since enabling the plugin. ([R23-S7](<#r23-s7>), [R23-S13](<#r23-s13>))
- **coverage-gap:** Trash-can icon documentation proves delete action, not recoverable application trash. RightClick plugin explicitly does not guarantee image security. ([R23-S9](<#r23-s9>), [R23-S13](<#r23-s13>))
- **coverage-gap:** AI and map availability/edition details remain unresolved; face recognition is explicitly upcoming. Cloud backup promises are not automatic self-hosted backup functionality. ([R23-S2](<#r23-s2>))
- **Coverage gap:** No claim to inventory every third-party plugin; inspected official manuals identify principal advanced workflows and gates.
- **Coverage gap:** Current AI service entitlement and map-plugin/provider details are unresolved.
- **Coverage gap:** No E2EE, offline maps, perceptual duplicate detection or undo journal established.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R23-S1

[Piwigo README](<https://github.com/Piwigo/Piwigo/blob/7547b1bdb00a531a613042b9142493f19f64c6ce/README.md>)
- Kind/ref: readme; 7547b1bdb00a531a613042b9142493f19f64c6ce
- Sections inspected: Complete README
- Establishes: Purpose, self-hosting prerequisites, Cloud and Docker alternatives.

### R23-S2

[Official feature overview](<https://piwigo.org/features>)
- Kind/ref: official-site; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Library workflows, albums, search, integrations, analytics and hosted-service distinctions.

### R23-S3

[Batch manager](<https://doc.piwigo.org/import-and-manage-photos/batch-manager-piwigo/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Filters, selection, batch changes, caddie and extension-specific additions.

### R23-S4

[File formats](<https://doc.piwigo.org/import-and-manage-photos/file-formats-compatible-piwigo/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page including panorama continuation
- Establishes: Default type restrictions, HEIC/WebP, VideoJS, MOV conversion, documents and embeds.

### R23-S5

[Properties and metadata](<https://doc.piwigo.org/import-and-manage-photos/properties-metadata-photos-piwigo/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page across three continuations
- Establishes: EXIF/IPTC mapping, database versus file metadata, custom properties and rights-expiry plugins.

### R23-S6

[FTP import and synchronization](<https://doc.piwigo.org/self-hosting-piwigo/importing-and-synchronizing-ftp-photos/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Physical folder hierarchy, simulation, metadata sync, scope and filename restrictions.

### R23-S7

[SmartAlbums](<https://doc.piwigo.org/organizing-albums/smart-albums-plugin-piwigo/>)
- Kind/ref: manual; live-docs/main inspected 2026-11-09
- Sections inspected: Complete document read via official docs repository
- Establishes: Rule-based album criteria, refresh schedules and permissions.

### R23-S8

[Community contribution plugin](<https://doc.piwigo.org/managing-users/community-plugin-piwigo/>)
- Kind/ref: manual; live-docs/main inspected 2026-11-09
- Sections inspected: Complete document read via official docs repository
- Establishes: Contributor scopes, guest uploads, quotas, trust, moderation and notification.

### R23-S9

[Photo editing](<https://doc.piwigo.org/import-and-manage-photos/modifying-or-deleting-photos/>)
- Kind/ref: manual; live-docs/main inspected 2026-11-09
- Sections inspected: Complete document read via official docs repository
- Establishes: Original downloads, center-of-interest crops, replacement and rotation plugins.

### R23-S10

[Gallery search](<https://doc.piwigo.org/browsing-your-piwigo-gallery/search-for-a-photo-in-your-gallery/>)
- Kind/ref: manual; live-docs/main inspected 2026-11-09
- Sections inspected: Complete document read via official docs repository
- Establishes: Search fields, multi-criteria filters, date ranges, AND/OR tags and subset searching.

### R23-S11

[Batch manager duplicate selection](<https://github.com/Piwigo/Piwigo/blob/7547b1bdb00a531a613042b9142493f19f64c6ce/admin/batch_manager.php>)
- Kind/ref: code; 7547b1bdb00a531a613042b9142493f19f64c6ce
- Sections inspected: Complete duplicate-option handling and duplicate prefilter query blocks
- Establishes: Filename/checksum/date/dimension criteria and GROUP_CONCAT limitation.

### R23-S12

[User Collections](<https://doc.piwigo.org/browsing-your-piwigo-gallery/user-collections-plugin-piwigo/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Personal collections, password/expiry share links, email and CSV export.

### R23-S13

[Photo-page features and plugins](<https://doc.piwigo.org/browsing-your-piwigo-gallery/the-photo-page-in-your-gallery/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page including continuation
- Establishes: Slideshow, downloads, derivatives, watermark, private shares, zoom, colors and double-sided images.

### R23-S14

[Piwigo 16.4.0 release](<https://piwigo.org/release-16.4.0>)
- Kind/ref: release; 16.4.0
- Sections inspected: Complete release note
- Establishes: Release date, fixes and upgrade/plugin compatibility cautions.

### R23-S15

[Managing interface and content languages](<https://doc.piwigo.org/customizing-your-gallery/managing-languages-available-gallery-piwigo/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Over 70 UI languages, per-user preferences, language activation and separate translation-related plugins.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
