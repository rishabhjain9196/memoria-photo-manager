# R05 — LibrePhotos/librephotos

[Repository](<https://github.com/LibrePhotos/librephotos>) · 8,141 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Self-hosted photographic library with in-place indexing, local recognition/search, rich metadata interoperability, controlled sharing and explicit duplicate/stack workflows.

**Deployment:** Unified Docker container; Multi-container Docker Compose with optional NVIDIA acceleration; Kubernetes and Unraid; Windows standalone librephotos.exe without Docker/Python; Responsive web application; Official Android/iOS Expo app is source-only and explicitly unreleased; separate released UhuruPhotos client

**Storage:** Local originals remain in configured per-user library roots; uploads enter configured upload folders. Database holds edits, ownership, people, albums and metadata. protected_media contains thumbnails, face crops, downloaded models, similarity indexes, extracted motion video and temporary ZIPs. PostgreSQL is used by standard Docker; SQLite by Windows/unified internal database. Optional Nextcloud import downloads local copies and does not write back.

**Privacy/network behavior:** ML inference is local after model provisioning. New installs use offline ExifTool town geocoding, but default map tiles and address search contact external providers; release checks and explicitly enabled report sharing are additional network paths. Metadata write-back defaults off; OCR stores sensitive recognized text unencrypted. Public/shared-file delivery may strip metadata depending on permissions, but granting originals exposes embedded metadata. No E2EE or universal air-gap guarantee is claimed.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 1.6.0 (2026-11-09T12:43:57Z)
**Repository pushed at:** 2026-11-09T12:45:14Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [db7030275766](<https://github.com/LibrePhotos/librephotos/commit/db70302757661a8b82cc18266a2e79e29b0dccf9>).
**Product lineage:** OwnPhotos-LibrePhotos.

## Maturity and availability caveats

- Frozen dev commit db70302757661a8b82cc18266a2e79e29b0dccf9; latest release 1.6.0 was published 2026-11-09.
- Current repository consolidates backend, frontend, mobile, docs and deployment repositories. Detailed versioned guides supersede stale feature-comparison rows and older inline notes.
- Official Expo mobile app is explicitly not on stores/TestFlight/F-Droid or GitHub APK releases; its implemented source-preview capabilities are kept separate from normal released clients.
- 1.6.0 fixes sharing/user-management security issues and disables ONNX telemetry that 1.5.0/1.5.1 Docker images sent to Microsoft (models/hardware, not photos).
- Performance/accuracy measurements in release notes are author claims, not benchmarks performed here. README recommends 8 GB+ for ML.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **OpenCLIP content labels**<br>`ai.auto_tags` | C | Current model produces semantic embedding and tags in one pass; 1.6 caps five Things with class-specific thresholds. Manual retag refresh does not overwrite personal tags/captions. | [R05-S6](<#r05-s6>), [R05-S15](<#r05-s15>), [R05-S2](<#r05-s2>) |
| **Local LFM2.5-VL captions**<br>`ai.captioning` | O | Per-photo suggestion or manually initiated whole-library background generation, preserving manual captions. Optional recognized names/place context defaults on; no automatic whole-library caption job after scan. | [R05-S8](<#r05-s8>) |
| **Custom zero-shot vocabulary**<br>`ai.custom_tag_vocabulary` | O | Admin custom_tags.txt adds words or word=description with multiple prompt descriptions separated by \|; at most two custom/five total labels, no model retraining, and old photos need retagging. | [R05-S15](<#r05-s15>) |
| **Screenshot/document categories**<br>`ai.document_classification` | C | Screenshots are detected on scan; document inference combines OCR and content labels, so OCR is needed for automatic documents. Manual/bulk category corrections persist across rescans and support undo. | [R05-S7](<#r05-s7>), [R05-S23](<#r05-s23>) |
| **Configurable unknown-face clustering**<br>`ai.face_clustering` | C | Stable clustering has auto size thresholds, min-samples and merge epsilon; labels split outputs by known person. Upload-triggered training waits for sufficient new faces and user inactivity. | [R05-S16](<#r05-s16>) |
| **Reject, relabel, merge and restore faces**<br>`ai.face_corrections` | C | Not-person decisions persist across training and person merge; false detections are soft-deleted/excluded from training and can be restored. Merge people preserves target cover but cannot itself be undone. | [R05-S16](<#r05-s16>), [R05-S15](<#r05-s15>) |
| **InsightFace face detection**<br>`ai.face_detection` | C | SCRFD finds boxes, merges overlapping imported MWG regions and offers a minimum relative face-size setting; imported regions are retained regardless. | [R05-S16](<#r05-s16>) |
| **Name faces and propagate within captures**<br>`ai.face_naming` | C | Dashboard/lightbox naming with recent-person shortcuts; clearly matching unnamed faces in bursts/duplicate groups can be labelled together, respecting prior rejections. | [R05-S16](<#r05-s16>) |
| **ArcFace identity matching**<br>`ai.face_recognition` | C | 512-dimensional ArcFace embeddings with selectable speed/memory model packs and learned classification against manually named people; confidence shown separately from clusters. | [R05-S16](<#r05-s16>) |
| **Server-local ONNX models**<br>`ai.local_inference` | C | InsightFace, OpenCLIP and optional caption/OCR models execute locally; models download on demand or can be prepositioned for offline use. | [R05-S1](<#r05-s1>), [R05-S5](<#r05-s5>), [R05-S7](<#r05-s7>) |
| **Draw a missed face**<br>`ai.manual_face_regions` | C | Draw a box to request enlarged-area detection/encoding or retain manual box if no match/service unavailable; prevents overlapping duplicate regions and requires usable thumbnail. | [R05-S16](<#r05-s16>) |
| **Opt-in local text recognition**<br>`ai.ocr` | O | Admin selects PP-OCRv6 Tiny/Small/Medium and confirms plaintext privacy warning. Extract missing or all text; current versions queue after scan/upload, with three-failure suppression and retry-all override. | [R05-S7](<#r05-s7>) |
| **Sample video frames for people**<br>`ai.video_faces` | C | Up to eight frames from 5%–95%, at most one/second, consolidate matching identities using largest face. Faces retain timestamp for seek-to-person; clips under two seconds use first frame only. | [R05-S16](<#r05-s16>) |
| **Many-to-many album collections**<br>`albums.collections` | C | Private labels such as Travel/Family group an album into several collections; deleting a collection preserves albums/photos. Not a nested filesystem hierarchy. | [R05-S15](<#r05-s15>) |
| **Chronological event generation**<br>`albums.events` | C | Manual generation chains captures less than 36 hours apart with minimum two photos; people/place affect title, not grouping. Regeneration preserves chosen covers and localized web titles. | [R05-S15](<#r05-s15>) |
| **Generated place albums**<br>`albums.locations` | C | GPS/geocoded location generates place collections; private circular places can override local grouping while keeping provider names. | [R05-S15](<#r05-s15>), [R05-S20](<#r05-s20>) |
| **User albums and covers**<br>`albums.manual` | C | Create empty or selected-photo albums, upload into them, choose covers and remove membership without deleting originals. | [R05-S15](<#r05-s15>), [R05-S17](<#r05-s17>) |
| **Lock album membership**<br>`albums.membership_lock` | C | API-enforced lock blocks adding/removing photos including uploads, but not editing/deleting underlying photos, renaming/sharing album or deleting album. | [R05-S15](<#r05-s15>) |
| **Person albums and private groups**<br>`albums.people` | C | Per-person face covers, name merge/delete, private many-to-many people groups and birth date with age-at-capture display; birthdate also constrains recognition suggestions. | [R05-S15](<#r05-s15>), [R05-S16](<#r05-s16>) |
| **AI Things and caption hashtag albums**<br>`albums.things` | C | Object/scene classifications form Things albums separate from user tags; caption hashtags remain visible independent of selected tagging model. | [R05-S15](<#r05-s15>) |
| **Locally computed annual Rewind**<br>`analytics.annual_rewind` | C | 1.6.0 shows per-user busiest day/month and most photographed people/places from Dec 20–Jan 6, computed on own server and admin-disableable. | [R05-S2](<#r05-s2>) |
| **Face-cluster scatter visualization**<br>`analytics.face_embedding_plot` | C | Projected embeddings coloured by identity, hover thumbnails, click-to-photo and per-person highlights assist correction. | [R05-S18](<#r05-s18>) |
| **Library and processing totals**<br>`analytics.library_statistics` | C | Photo/day/person/face/event/place counts with inferred/labelled/unknown breakdown, plus data-volume usage bar that includes other content on that disk. | [R05-S22](<#r05-s22>) |
| **Person co-occurrence graph**<br>`analytics.people_cooccurrence_graph` | C | Unweighted edges connect people appearing together in at least one photo, with draggable nodes/zoom; not an inferred social relationship beyond co-occurrence. | [R05-S18](<#r05-s18>) |
| **Interactive place hierarchy**<br>`analytics.place_tree` | C | Country/region/town tree with horizontal/vertical/radial layouts, counts, collapse, pan and zoom. | [R05-S18](<#r05-s18>) |
| **Monthly counts and stay timeline**<br>`analytics.timeline_counts` | C | Monthly photo chart and chronological location-stay duration bar; timeline density scrubber also visualizes busy months/years. | [R05-S18](<#r05-s18>), [R05-S23](<#r05-s23>) |
| **Place, Things and people word clouds**<br>`analytics.word_clouds` | C | Top 100 terms sized by frequency, clickable to search their photos. | [R05-S18](<#r05-s18>) |
| **Light/dark theme and mobile layouts**<br>`browse.dark_theme` | C | 1.6.0 redesign covers pages, viewer, dialogs and sidebar; map display darkening is performed in-browser without a second tile source. | [R05-S2](<#r05-s2>), [R05-S20](<#r05-s20>) |
| **Lightbox and standalone photo page**<br>`browse.fullscreen` | C | Black-stage lightbox, thumbnail strip, fullscreen toggle and deep-link photo address; browser Back closes viewer and restores grid position. | [R05-S23](<#r05-s23>) |
| **Filtered photographic grids**<br>`browse.grid` | C | Views cover favourites, recent latest-import day, hidden/archive, photos/videos, screenshots/documents and missing-date/location/album cases; filter-aware select-all targets only displayed scope. | [R05-S23](<#r05-s23>) |
| **Command palette and viewer shortcuts**<br>`browse.keyboard` | C | Ctrl/Cmd+K, Ctrl/Cmd+P or / opens palette for people/places/albums/search/actions; viewer keys handle rating, text selection, archive, slideshow, navigation and video seek. | [R05-S6](<#r05-s6>), [R05-S23](<#r05-s23>) |
| **Cursor-paged large days**<br>`browse.pagination` | C | 1.6.0 uses cursor pages for /api/days rather than offset/page-number queries, retaining scroll geometry while rows load. Reported speedups are not independently measured. | [R05-S2](<#r05-s2>) |
| **Interactive 360-degree photo spheres**<br>`browse.panorama` | C | WebGL drag/swipe/pinch viewer uses GPano equirectangular metadata or exact 2:1 images at least 6000 px wide; cylindrical panoramas and 360 videos are not sphere-rendered. | [R05-S23](<#r05-s23>) |
| **Timed slideshow and public presentation link**<br>`browse.slideshow` | C | Intervals 3/5/10/15/30 seconds with keyboard control; public album ?slideshow=1 starts automatically, stops at last photo and respects reduced-motion preference. | [R05-S23](<#r05-s23>), [R05-S14](<#r05-s14>) |
| **Selectable OCR overlay**<br>`browse.text_selection` | O | Own-photo viewer T action overlays recognized text for mouse selection/copy; requires OCR results. | [R05-S7](<#r05-s7>) |
| **Day/place timeline and date scrubber**<br>`browse.timeline` | C | Capture-date grouped timeline with newest/oldest account-saved order, undated bucket and simple or photo-density scrubber; events always chronological. | [R05-S23](<#r05-s23>) |
| **Direct or fallback video playback**<br>`browse.video_playback` | C | Checks browser codec support, plays original when possible and falls back on decode failure. Keyboard seeks 10 seconds/one minute except during live conversion. | [R05-S23](<#r05-s23>) |
| **Load original on zoom**<br>`browse.zoom` | C | Signed-in authorized viewers fetch original when zooming; RAW/HEIC/TIFF/JXL/rotated images may remain preview-only with original-download link. Public visitors retain display-size previews. | [R05-S23](<#r05-s23>) |
| **Released third-party Android client**<br>`deployment.android` | P | Mobile guide points users needing an installable app to UhuruPhotos; 1.6.0 restores compatibility for its released builds. Official Expo client is separate and unreleased. | [R05-S10](<#r05-s10>), [R05-S2](<#r05-s2>) |
| **Unreleased official Android source preview**<br>`deployment.android_source_preview` | R | Implemented official Expo Android app runs through Expo Go or a development build, but has no Google Play, F-Droid or GitHub APK release. It is distinct from the released third-party UhuruPhotos integration; production distribution is not counted as present. | [R05-S10](<#r05-s10>) |
| **Unified or multi-container Docker**<br>`deployment.docker` | C | Single-container install or separated backend/frontend/proxy Compose; Kubernetes and Unraid are recorded separately rather than inferred from generic Docker compatibility. | [R05-S1](<#r05-s1>) |
| **Unreleased official iOS client**<br>`deployment.ios` | R | Official mobile guide explicitly supports running the implemented iPhone app from source through Expo Go or a development build, but says there is no App Store or TestFlight release. This is an upcoming/source-preview surface, not currently packaged native iOS availability. | [R05-S10](<#r05-s10>) |
| **Kubernetes deployment manifests**<br>`deployment.kubernetes` | C | README explicitly provides Kustomize manifests in deploy/k8s; 1.6.0 release notes confirm those manifests were updated to the 1.6.0 image version. | [R05-S1](<#r05-s1>), [R05-S2](<#r05-s2>) |
| **Translated web interface**<br>`deployment.localization` | C | Release notes identify translated UI labels maintained through Weblate; user-selected language changes translated event titles, Things labels and localized numeric formatting. English-only Things search vocabulary is a separate limitation. | [R05-S2](<#r05-s2>), [R05-S15](<#r05-s15>), [R05-S23](<#r05-s23>) |
| **Self-hosted photo server**<br>`deployment.selfhosted` | C | Own-server library with browser frontend and local ML; README recommends at least 4 GB RAM and preferably 8 GB+ for analysis. | [R05-S1](<#r05-s1>) |
| **Documented Unraid deployment**<br>`deployment.unraid` | C | README lists Unraid as an installation choice and links its dedicated installation guide. This records the documented deployment surface without asserting additional NAS integrations. | [R05-S1](<#r05-s1>) |
| **Responsive web client**<br>`deployment.web` | C | Light/dark desktop/mobile layouts, phone bottom sheets and configurable pinned sidebar plus recent albums in 1.6.0. | [R05-S2](<#r05-s2>) |
| **Standalone Windows application**<br>`deployment.windows` | C | One folder with librephotos.exe, no Docker/Python installation required; SQLite and protected-media data are local to the Windows application. | [R05-S1](<#r05-s1>), [R05-S7](<#r05-s7>), [R05-S12](<#r05-s12>) |
| **MD5 exact-copy grouping**<br>`duplicates.exact_hash` | C | Detects exact-copy candidates by MD5 file hash, distinct from visual hashes. No separate byte-comparison verification is documented. | [R05-S3](<#r05-s3>) |
| **Dismiss non-duplicate group**<br>`duplicates.keep_all` | C | Not duplicates preserves all photos, unlinks them and marks group dismissed; this action cannot be reverted through UI and dismissal list currently returns no groups despite counts. | [R05-S3](<#r05-s3>) |
| **Keep selected and trash others**<br>`duplicates.keeper_selection` | C | Highest-resolution photo is preselected but user can choose another; resolution moves other photos to application trash and can be reverted/restored for resolved groups. | [R05-S3](<#r05-s3>) |
| **Persist pending/resolved review records**<br>`duplicates.review_status` | C | Filter pending/resolved/type, delete group records individually/in bulk or clear pending groups before detection. Looser reruns exclude photos already in visual groups, so groups must be cleared to reconsider them. | [R05-S3](<#r05-s3>) |
| **Perceptual duplicate grouping**<br>`duplicates.similar_images` | C | 64-bit DCT pHash/Hamming distance from large thumbnails; strict/normal/loose sensitivity and two-pass BK-tree batches, default 10,000, including cross-batch comparisons. | [R05-S3](<#r05-s3>) |
| **Preview duplicate groups**<br>`duplicates.visual_review` | C | Thumbnails and group type/status/savings plus per-photo resolution,size,camera,date,path in review modal. | [R05-S3](<#r05-s3>) |
| **HDR-to-SDR previews and playback**<br>`editing.hdr_tonemap` | C | HDR phone video is tone-mapped during thumbnail/conversion paths; HDR badges and probe/rebuild job repair older previews. | [R05-S23](<#r05-s23>), [R05-S21](<#r05-s21>) |
| **Database-first image rotation**<br>`editing.rotate_flip` | C | Rotate stills in 90-degree steps and regenerate thumbnails; default originals unchanged. Optional sidecar orientation works across formats; original EXIF orientation writes limited to JPEG/PNG/TIFF/WebP. | [R05-S23](<#r05-s23>), [R05-S13](<#r05-s13>) |
| **Cached H.264 playback conversion**<br>`editing.video_transcode` | C | For signed-in viewers unsupported videos convert while playing to H.264 capped at 720 lines and are cached; public unauthenticated visitors do not receive this conversion. | [R05-S23](<#r05-s23>) |
| **Animated GIF viewing**<br>`formats.animated` | C | Viewer always uses the animated GIF original rather than enlarging a static display preview. | [R05-S23](<#r05-s23>) |
| **AVIF support**<br>`formats.avif` | C | Explicit upload support and supported ExifTool metadata-write format; browser presentation uses derived previews where required. | [R05-S17](<#r05-s17>), [R05-S13](<#r05-s13>) |
| **HEIC/HEIF support**<br>`formats.heic` | C | Upload/index/preview HEIC and HEIF; HEIC/AVIF display orientation follows container rotation/mirroring rather than blindly trusting EXIF. | [R05-S17](<#r05-s17>), [R05-S13](<#r05-s13>) |
| **JPEG XL support**<br>`formats.jpegxl` | C | README/upload/manual list JXL indexing and uploads; viewer may retain a derived preview and offer original download. | [R05-S1](<#r05-s1>), [R05-S17](<#r05-s17>), [R05-S23](<#r05-s23>) |
| **Paired still/video Live Photos**<br>`formats.live_photos` | C | Scan groups same-capture still and clip as variants of one photo, with all variants in ZIP downloads. | [R05-S4](<#r05-s4>) |
| **Embedded Google/Samsung motion video**<br>`formats.motion_photos` | C | Extracts embedded JPEG video into protected_media/embedded_media while preserving its embedded copy in original; enabled by default through feature toggle. | [R05-S12](<#r05-s12>) |
| **Camera RAW preview support**<br>`formats.raw` | C | Supports RAW indexing/preview, including upload formats browsers mislabel; paired RAWs can be downloaded even when browser zoom remains on preview. | [R05-S1](<#r05-s1>), [R05-S17](<#r05-s17>), [R05-S23](<#r05-s23>) |
| **Automatic RAW+JPEG file variants**<br>`formats.raw_jpeg_pairs` | C | Same-folder/base-name files represent one photo, no toggle; main-file preference JPEG then video then RAW. Repair job merges orphan RAW photos but not already separate Live Photo videos. | [R05-S4](<#r05-s4>) |
| **Companions stay attached during file operations**<br>`formats.sidecar_pairs` | C | Move, rename and ZIP keep RAW/Live variants and both XMP naming conventions paired; extracted motion-video derivatives remain in app storage. | [R05-S22](<#r05-s22>), [R05-S13](<#r05-s13>) |
| **Photo-count map clustering**<br>`geo.clustering` | C | Photos within about a metre combine at one point; zoomed-out clusters count photos once, not every administrative place name. | [R05-S20](<#r05-s20>) |
| **Interactive photo-location map**<br>`geo.map` | C | MapLibre displays actual photo coordinates, viewport-filtered place tiles and click-to-open previews; online PhotoPrism/OSM basemaps or None. | [R05-S20](<#r05-s20>) |
| **Built-in offline town lookup**<br>`geo.offline_geocoding` | C | New-install ExifTool/GeoNames geocoder finds nearest town ≥2000 population within 50 km plus district/region/country; no street/POI and borders can choose a town across a country line. | [R05-S20](<#r05-s20>), [R05-S5](<#r05-s5>) |
| **Optional online place providers**<br>`geo.online_geocoding` | O | Nominatim or keyed Mapbox/MapTiler/OpenCage/TomTom; Nominatim rate limit shared across workers around one request/sec. Language settings/provider switch only affect new lookups unless rerun. | [R05-S20](<#r05-s20>) |
| **Private named circular places**<br>`geo.private_places` | C | Define up to 100 places of 25 m–2 km radius with live photo counts; smaller overlapping circle wins. Names dynamically group photos/search and can title events, but never leave owner via sharing/write-back. | [R05-S20](<#r05-s20>) |
| **Interactive documented REST API**<br>`integration.api` | C | Swagger/ReDoc plus documented metadata/search/targeted-scan/processing-status/upload/retention endpoints; Basic/JWT authentication described for scripts. | [R05-S1](<#r05-s1>), [R05-S6](<#r05-s6>), [R05-S19](<#r05-s19>), [R05-S22](<#r05-s22>) |
| **Administrative management commands**<br>`integration.cli` | C | Scan selected/all/Nextcloud roots, rebuild index, write metadata with dry-run, rehash, strip derived metadata, back up SQLite and repair upgrade data. | [R05-S22](<#r05-s22>) |
| **Source-preview mobile share target**<br>`integration.mobile_share_target` | R | Implemented Android development-build share target accepts images from other apps, not Expo Go; iOS share extension explicitly still being finalized. | [R05-S10](<#r05-s10>) |
| **OpenID Connect sign-in**<br>`integration.oidc` | O | README explicitly supports OpenID Connect SSO; LDAP compatibility is not inferred as native directory integration. | [R05-S1](<#r05-s1>) |
| **Archive outside timeline and Memories**<br>`library.archive` | C | Archive removes photos from the main timeline and Memories while retaining them in albums, search, people, places, folders and other filtered views; Unarchive returns them. Unlike Hide, archive does not remove photos from all ordinary views. Neither mode changes original files. | [R05-S23](<#r05-s23>) |
| **Move into capture-date directories**<br>`library.auto_date_folders` | C | Choose year, year/month or year/month/day destinations with preview counts; undated photos remain until given dates. | [R05-S22](<#r05-s22>) |
| **Automatic exposure-bracket detection**<br>`library.automatic_bracket_stacks` | N | Detailed guide explicitly says Bracket is a reserved type not currently created; no bracket detection exists and Create stack always makes Manual, despite broader README wording. | [R05-S4](<#r05-s4>) |
| **Queued web drag/drop uploads**<br>`library.batch_upload` | C | Drop multiple photos/videos anywhere, append to active queue and upload directly into own unlocked albums; account scan directory and admin upload enablement are prerequisites. | [R05-S17](<#r05-s17>) |
| **Capture-date filename templates**<br>`library.bulk_rename` | C | Presets/custom year/month/day/hour/minute/second/original-name tokens rename photos and companions, preview changes and suffix collisions; over 100 photos runs in background. | [R05-S22](<#r05-s22>) |
| **Rule-based burst stacks**<br>`library.burst_stacking` | C | EXIF burst/sequence and explicit filename patterns group same-camera frames; default two-second temporal continuity with subsecond times and sequence restarts. Optional proximity/pHash rules are disabled by default. | [R05-S4](<#r05-s4>) |
| **Optional Nextcloud download/index**<br>`library.cloud_import` | O | Select remote folder, copy into nextcloud_media/user, reuse unchanged files and refresh changed media/XMP. Deleted remote files are marked missing, not silently deleted locally; no write-back to Nextcloud. | [R05-S22](<#r05-s22>) |
| **Content-aware upload skip**<br>`library.deduplicate_import` | C | Checks MD5 plus user ID before upload; existing photos can still be added to the target album without retransmitting bytes. | [R05-S17](<#r05-s17>) |
| **Exclude user subfolders**<br>`library.exclude_folders` | C | Leave out subfolders recursively, with optional trashing of already-indexed out-of-scope photos. Exclusion alone never deletes disk files; hidden/skip-pattern folders also stay out. | [R05-S22](<#r05-s22>) |
| **Index originals in place**<br>`library.existing_folders` | C | Scans existing image/video/RAW/XMP files without reorganizing them by default; unrelated sidecars/non-media are skipped. | [R05-S22](<#r05-s22>) |
| **Original and multi-variant export**<br>`library.export_originals` | C | Single-photo page selects original variant; multi-photo ZIP includes all file variants and XMP sidecars with collision-safe paired names, optionally adding all stack photos. | [R05-S4](<#r05-s4>), [R05-S13](<#r05-s13>), [R05-S23](<#r05-s23>) |
| **External watcher integration**<br>`library.filesystem_watch` | O | Official guide provides an inotifywait/curl/jq watcher feeding scan-files API, batching after 30 seconds; not an always-enabled native filesystem watcher. | [R05-S19](<#r05-s19>) |
| **Folder-tree browsing**<br>`library.folder_structure` | C | Browse indexed directories/subdirectories with recursive counts and newest-photo covers; empty/unindexed/hidden directories are not listed. | [R05-S23](<#r05-s23>), [R05-S15](<#r05-s15>) |
| **Safe incremental baseline**<br>`library.incremental_scan` | C | Rereads new/changed files and sidecars and retries prior metadata failures; cancelled/partial/failed scans do not replace the last complete-library baseline. | [R05-S19](<#r05-s19>), [R05-S21](<#r05-s21>), [R05-S22](<#r05-s22>) |
| **Manual stacks and cover selection**<br>`browse.stacks` | C | Group separate captures, merge stacks, pick cover and unstack/break apart while retaining photos; timeline shows cover only and lightbox opens members. | [R05-S4](<#r05-s4>) |
| **Official source-preview camera backup**<br>`library.mobile_backup` | R | Unreleased app implements album-selected photo/video backup, Wi-Fi/charging conditions, content skip and processing badges. OS background limits apply; not advertised as a released official backup client. | [R05-S10](<#r05-s10>) |
| **Move photos with companions**<br>`library.move_copy` | C | Move within library with all variants/XMP, retaining albums/faces/ratings/shares. Skip missing, shared-file and Nextcloud-copy cases; selections over 100 use a background job. Copy is not established by this workflow. | [R05-S22](<#r05-s22>) |
| **Several roots per user library**<br>`library.multiple_roots` | C | Main scan folder, additional admin-added folders and separate upload folder form one library; unreadable/unplugged roots are skipped without marking their photos missing. | [R05-S22](<#r05-s22>) |
| **Automatic per-library schedules**<br>`library.scheduled_indexing` | O | Admin chooses hourly, daily or custom weekdays/time, off by default. Overlapping queued/running scans are skipped and server timezone is shown. | [R05-S19](<#r05-s19>) |
| **Read Google Takeout sidecar JSON**<br>`library.takeout_import` | C | Scans adjacent JSON for capture UTC time, GPS/altitude and description only as lower-priority fallback; handles supplemental/truncated/duplicate/edited filenames without rewriting originals. | [R05-S11](<#r05-s11>) |
| **Scan named files or subtrees**<br>`library.targeted_scan` | C | API accepts up to 1000 changed paths and separately 1000 removed paths; validates library scope and detects move-out/move-in without losing personal edits. | [R05-S19](<#r05-s19>) |
| **Jobs, services, logs and server stats**<br>`maintenance.diagnostics` | C | Admin health/start/stop for ML services, job details, log refresh/download and JSON CPU/RAM/GPU/storage/per-user report; job-log removal is distinct from cancellation. | [R05-S21](<#r05-s21>), [R05-S22](<#r05-s22>) |
| **Source-preview local reminders**<br>`maintenance.mobile_memories_notifications` | R | Unreleased mobile app schedules on-this-day notifications locally two weeks ahead without push service; they stop if not reopened/synced within two weeks. | [R05-S10](<#r05-s10>) |
| **Targeted rescans and derived-data repair**<br>`maintenance.selective_reset` | C | Rescan up to 1000 chosen photos, re-detect selected/folder faces, retry particular stages, rebuild embeddings/geocoding and repair RAW variants/old video previews without indiscriminately clearing manual data. | [R05-S21](<#r05-s21>), [R05-S22](<#r05-s22>), [R05-S16](<#r05-s16>) |
| **Bulk ratings, dates, locations and tags**<br>`metadata.batch_edit` | C | Bulk UI edits use background write-back when enabled; Write now exports pre-existing catalogue edits in 200-photo batches with per-file errors and cancellation. | [R05-S13](<#r05-s13>), [R05-S23](<#r05-s23>) |
| **Manual captions alongside generated captions**<br>`metadata.comments` | C | User captions are editable and searchable; generated suggestions are separate and do not overwrite a manual caption during bulk generation. | [R05-S8](<#r05-s8>), [R05-S13](<#r05-s13>) |
| **Shift or set capture dates**<br>`metadata.date_fix` | C | Shift a selection by days/hours/minutes/seconds preserving intervals, or assign one timestamp. Manual dates survive rescans; Remove timestamp returns control to date rules. | [R05-S23](<#r05-s23>) |
| **Configurable metadata/date precedence**<br>`metadata.date_rules` | C | Ordered rules choose XMP/EXIF/video/GPS/Takeout/name times, use recorded or GPS/default timezone and can be reapplied without rewriting originals or overriding manually set dates. | [R05-S13](<#r05-s13>), [R05-S11](<#r05-s11>), [R05-S21](<#r05-s21>) |
| **Opt-in original metadata write-back**<br>`metadata.embedded_write` | O | Save to media file writes supported ratings/dates/manual captions/GPS/keywords/rights and optional face regions via ExifTool; support varies by format and image bytes are not re-encoded. | [R05-S13](<#r05-s13>) |
| **Extensive photographic metadata**<br>`metadata.exif_read` | C | ExifTool reads dates/UTC offsets/GPS/altitude/orientation, camera/lens/serial, exposure, rights, video duration/codec and dimensions; on-demand raw-metadata dialog filters groups/tags/values and copies JSON. | [R05-S13](<#r05-s13>) |
| **Portable named MWG face regions**<br>`metadata.face_regions` | C | Imports XMP RegionInfo faces/names and merges overlapping detections; optional face-write switch plus metadata-write mode exports normalized regions/names with rotation handling. | [R05-S13](<#r05-s13>), [R05-S16](<#r05-s16>) |
| **Favourite photos**<br>`metadata.favorites` | C | Favourites derive from rating threshold; removing a favourite sets rating to zero and therefore clears any existing star rating. | [R05-S23](<#r05-s23>) |
| **Assign, copy and remove locations**<br>`metadata.gps_write` | C | Map click/drag, address search, pasted coordinates, explicit browser location or nearby-in-time photos; bulk defaults to filling missing GPS, with replace-all choice and optional write-back. | [R05-S20](<#r05-s20>) |
| **IPTC keyword/caption/rights import**<br>`metadata.iptc_read` | C | Reads Keywords, Caption-Abstract, ObjectName, By-line and CopyrightNotice with documented XMP/EXIF precedence. | [R05-S13](<#r05-s13>) |
| **Export sidecars with variants**<br>`metadata.preserve_export` | C | ZIP export includes existing and newly written XMP beside originals/RAW companions, adjusting names together for collisions; privacy-constrained shared downloads intentionally strip metadata instead. | [R05-S13](<#r05-s13>), [R05-S14](<#r05-s14>) |
| **Interoperable zero-to-five stars**<br>`metadata.ratings` | C | Choose stars or favourite toggle; keyboard 0–5 and bulk selection ratings map to imported/exported XMP rating, with configurable favourite threshold. | [R05-S23](<#r05-s23>), [R05-S13](<#r05-s13>) |
| **Creator, copyright and licence metadata**<br>`metadata.rights` | C | Reads/displays creator/copyright and fixed Creative Commons/all-rights/public-domain licence choices, with supported write-back. Licence-bearing public photos expose relevant rights regardless of other detail switches. | [R05-S13](<#r05-s13>), [R05-S14](<#r05-s14>) |
| **Opt-in XMP sidecar write-back**<br>`metadata.sidecar_write` | O | Updates highest-priority existing main-file sidecar or creates filename.ext.xmp, preserving unrelated tags. RAW companion sidecars are read but writes target the main photo's sidecar. | [R05-S13](<#r05-s13>) |
| **Privacy-stripped shared derivatives**<br>`metadata.strip` | C | Thumbnails omit EXIF/XMP but retain colour profiles; restricted sharing serves full-size JPEG or video stream copies without recorded metadata. Old-thumbnail cleanup is available. | [R05-S14](<#r05-s14>), [R05-S21](<#r05-s21>) |
| **Personal tags with rename/merge**<br>`metadata.tags` | C | Comma-separated autocomplete, bulk additive tagging, single-photo replacement/removal and user-private tag albums; rename/merge/delete can update keywords with write-back enabled. | [R05-S15](<#r05-s15>), [R05-S13](<#r05-s13>) |
| **Embedded and sidecar XMP**<br>`metadata.xmp_read` | C | Reads basename.xmp and filename.ext.xmp, uppercase variants and RAW/video companion sidecars with field-specific precedence; hierarchy keywords flatten to last level. | [R05-S13](<#r05-s13>) |
| **Stage-aware processing queue**<br>`performance.background_jobs` | C | Progress card covers thumbnails/Things/search/places/faces/OCR/captions, run-missing-stage actions and per-item errors; ordinary user jobs serialize globally while upload processing can run alongside. | [R05-S22](<#r05-s22>), [R05-S21](<#r05-s21>) |
| **Cooperative job and upload cancellation**<br>`performance.cancel` | C | Jobs stop at checkpoints and clear queued steps; move/rename preserve completed changes. Model/ZIP downloads finish and clustering finishes current rebuild; upload-import jobs cannot cancel. | [R05-S21](<#r05-s21>), [R05-S17](<#r05-s17>) |
| **One-megabyte upload chunks**<br>`performance.chunked_upload` | C | Uploads one file at a time in 1 MB chunks; cancel stops after current chunk, retries failed/cancelled files while tab remains open and removes old partial uploads daily. | [R05-S17](<#r05-s17>) |
| **Optional NVIDIA ML deployment**<br>`performance.gpu_ml` | O | README documents optional NVIDIA acceleration in separated Docker Compose deployment; no GPU benchmark or universal model acceleration is asserted. | [R05-S1](<#r05-s1>) |
| **Browse as thumbnails become ready**<br>`performance.live_browsing` | C | Scan prioritizes thumbnails; upload progress distinguishes sent/processing/ready and timeline fills without reload while analysis continues. | [R05-S22](<#r05-s22>), [R05-S17](<#r05-s17>) |
| **Recover interrupted processing**<br>`performance.resume` | C | After restart previously taken queue work reruns around ten minutes later; failed/cancelled scans do not advance baseline and later jobs fill missing analysis. Stuck checks target lack of progress, not simply duration. | [R05-S21](<#r05-s21>) |
| **Separate preview and model caches**<br>`performance.thumbnail_cache` | C | Tiny/grid/large/face derivatives, extracted motion clips and persistent similarity/model files; bulk ZIPs auto-expire around one day. | [R05-S12](<#r05-s12>), [R05-S6](<#r05-s6>) |
| **Local-first sanitized error reports**<br>`privacy.error_reporting_control` | C | 1.6.0 retains at most 30 reports for 30 days locally, deduplicating repeats; admin may opt into maintainers or own Sentry/GlitchTip. Reports rebuilt from allowlisted fields remove paths/names/URLs/identifiers. | [R05-S2](<#r05-s2>) |
| **Hide media in a dedicated section**<br>`privacy.hidden_media` | C | Hide removes photos from ordinary timeline, album, people, place, search and folder views; they remain available in Hidden until unhidden. Hiding takes precedence when a photo is also archived. This is visibility control, not encryption, and the guide establishes no separate authentication guarantee for the Hidden section; original files are unchanged. | [R05-S23](<#r05-s23>) |
| **Official source-preview offline editing**<br>`privacy.mobile_offline_mirror` | R | Unreleased mobile app mirrors metadata/grid thumbnails and queues favourite/hide/trash/rating/caption/album edits; full originals still need network unless already on device, and resync rebuilds disposable mirror. | [R05-S10](<#r05-s10>) |
| **Server-local original analysis**<br>`privacy.no_upload_required` | C | Local ML and original-folder indexing do not require third-party photo upload; optional online maps, reports and Nextcloud have separate disclosures. | [R05-S1](<#r05-s1>), [R05-S5](<#r05-s5>), [R05-S20](<#r05-s20>) |
| **Configured offline operation**<br>`privacy.offline_use` | O | Preload model files, use offline ExifTool, hide online maps and disable release checks. OpenCLIP remains required; disabling caption/face features avoids their model downloads. | [R05-S5](<#r05-s5>) |
| **Trash and restoration**<br>`safety.app_recovery` | C | Trash marks photos deleted while retaining them; restore reverses it. Permanent/empty-trash deletes originals and derivatives. Auto-delete defaults 0/off and shows per-photo countdown when enabled. | [R05-S9](<#r05-s9>) |
| **SQLite backup command**<br>`safety.catalogue_backup` | C | backup_database keeps newest three by default, configurable, and can guard pending migrations. PostgreSQL needs separate pg_dump; originals/models/secret require their own backup. | [R05-S22](<#r05-s22>), [R05-S12](<#r05-s12>) |
| **Companion-aware move rollback**<br>`safety.companion_operation_rollback` | C | If one file of a photo cannot move, previously moved companion files are put back; rename also retains old names on failure. Docs establish per-photo rollback, not a durable crash-recovery journal. | [R05-S22](<#r05-s22>) |
| **Destructive and unsaved-edit review**<br>`safety.confirmation` | C | Confirm permanent deletion, retention reductions and key destructive actions; unsaved metadata prompts on viewer navigation, page leave and tab close. | [R05-S9](<#r05-s9>), [R05-S23](<#r05-s23>) |
| **Rehash unchanged-timestamp files**<br>`safety.content_change_check` | C | Check file contents rereads every byte to detect replacements retaining old mtime, then reimports/reindexes changes with appropriate personal-data preservation. It is not documented as bit-rot recovery or copy verification. | [R05-S21](<#r05-s21>), [R05-S22](<#r05-s22>) |
| **Safe move/rename collisions**<br>`safety.no_overwrite` | C | Move chooses rename-keep-both or skip; rename adds numbered suffixes. Destination files are never silently overwritten. | [R05-S22](<#r05-s22>) |
| **Default metadata read-only and sidecar mode**<br>`safety.read_only_originals` | C | Scans only read originals and write-back is Off by default; sidecar mode preserves media bytes. Read-only mounted files cannot be permanently deleted, but catalogue edits still work. | [R05-S13](<#r05-s13>), [R05-S9](<#r05-s9>) |
| **Unmounted/mass-missing protection**<br>`safety.unavailable_library_guard` | C | Missing-file detection checks whole result before changes, refuses apparently unmounted roots or configured excessive missing count and avoids flagging photos after unreadable-subfolder scans. | [R05-S19](<#r05-s19>), [R05-S21](<#r05-s21>), [R05-S22](<#r05-s22>) |
| **Undo selected catalogue actions**<br>`safety.undo` | C | Notifications undo favourites/hide/archive/public changes and face operations; timestamps can revert previous value, resolved duplicates restore trashed copies. Not a crash-recovery file journal. | [R05-S2](<#r05-s2>), [R05-S16](<#r05-s16>), [R05-S23](<#r05-s23>), [R05-S3](<#r05-s3>) |
| **Share/bookmark filter URLs**<br>`search.bookmarkable_filters` | C | Active filters live in page address, appear as removable chips and preserve words/media when cleared; this is URL persistence rather than a saved-query catalogue. | [R05-S6](<#r05-s6>) |
| **All-word and quoted-phrase text search**<br>`search.boolean` | C | Every word must appear somewhere in indexed text; commas split words and quotes preserve phrases. Case/diacritics are folded except OCR; semantic augmentation can return nonliteral matches. | [R05-S6](<#r05-s6>) |
| **Inclusive capture-date ranges**<br>`search.date_range` | C | Before/after dates plus current-year/last-year/last-12-month shortcuts combine with other filters. | [R05-S6](<#r05-s6>) |
| **Media, extension and RAW filters**<br>`search.file_type` | C | Photos/video/screenshots/documents plus main-file extension and Has a RAW file, including RAW companions. | [R05-S6](<#r05-s6>) |
| **File-path text matching**<br>`search.filename_path` | C | Text search includes indexed file paths alongside captions, people, location, cameras, lenses, types and ISO-format date fragments. | [R05-S6](<#r05-s6>) |
| **Place names and GPS-presence filters**<br>`search.location` | C | Find by place name, custom private place or whether GPS exists; Places map limits visible place albums to current viewport. | [R05-S6](<#r05-s6>), [R05-S20](<#r05-s20>) |
| **Technical camera/exposure filters**<br>`search.metadata` | C | Maker/model/lens plus inclusive min/max ISO, aperture, focal length and 35-mm equivalent; values absent from a photo cannot match their filter. | [R05-S6](<#r05-s6>) |
| **Search recognized photo text**<br>`search.ocr` | O | OCR text joins normal text search; PostgreSQL matches words whereas SQLite permits substring matches. | [R05-S7](<#r05-s7>) |
| **Find several people together**<br>`search.people` | C | Person-name search and repeat person filters require all chosen people in a photo; suggestions rank matches by face count. | [R05-S6](<#r05-s6>) |
| **Minimum stars or favourites filter**<br>`search.ratings` | C | Filter rating 1–5 threshold or favourites-only according to chosen rating UI. | [R05-S6](<#r05-s6>) |
| **Optional OpenCLIP semantic retrieval**<br>`search.semantic_text` | O | Disabled by default; choose top 10/50/100 semantic matches above threshold, merged with ordinary text results. Requires completed embeddings/index, persisted under protected_media/similarity. | [R05-S6](<#r05-s6>) |
| **Similar-photo recommendations**<br>`search.similar_image` | C | Lightbox shows semantically similar photos from OpenCLIP embeddings, distinct from pHash duplicate detection. | [R05-S6](<#r05-s6>) |
| **Personal and embedded keyword search**<br>`search.tags` | C | Matches user tags and XMP/IPTC keywords, including sidecars. Display-translated AI Things remain searchable by English word in current guide. | [R05-S6](<#r05-s6>), [R05-S15](<#r05-s15>) |
| **Album-specific comments and likes**<br>`sharing.comments_reactions` | C | Members can post plain-text comments up to 1000 chars/like photos, with own edit/delete and owner moderation; per-user 30/minute limit and membership/removal lifecycle. | [R05-S14](<#r05-s14>) |
| **Contribute own photos to shared albums**<br>`sharing.collaborative_albums` | C | Links contributors' media without copy/move; recipient details require intersection of owner and contributor switches. Contributor photos are never included on owner's album public link. | [R05-S14](<#r05-s14>) |
| **Album-link expiry**<br>`sharing.expiring_links` | C | Public album expiry supports exact date/time or 7/30/90-day presets and Never. Expiry is explicitly unavailable for single-photo links. | [R05-S14](<#r05-s14>) |
| **Read-only whole-library sharing**<br>`sharing.library_share` | C | Share ongoing own photos with another account and independently opt into location/people/camera/captions/originals; recipient may mix them into timeline but cannot edit or add to own albums. | [R05-S14](<#r05-s14>) |
| **Per-share detail and original controls**<br>`sharing.metadata_controls` | C | Public date/location/camera/caption/face-name switches default off. Original public delivery requires all five; otherwise metadata-free copies are served. Whole-library originals independently override embedded privacy expectations. | [R05-S14](<#r05-s14>) |
| **Per-user ownership and libraries**<br>`sharing.multiuser` | C | Multiple accounts retain their own photos/faces/ratings/albums; all sharing preserves source ownership. This is not a shared co-owned editable catalogue. | [R05-S14](<#r05-s14>) |
| **Password-protected photo links**<br>`sharing.password_links` | N | Guide explicitly says password protection is not available for photo shares yet; album password support is not established either. | [R05-S14](<#r05-s14>) |
| **Approval-gated person sharing**<br>`sharing.person_share` | C | Only manually labelled person photos count; existing labels initially approve, later labels await review. Inferred/unknown faces do not auto-share; metadata switches start off and originals are withheld. | [R05-S14](<#r05-s14>) |
| **Double-opt-in instance gallery**<br>`sharing.public_gallery` | O | Admin enables members-only/everyone and each user independently opts in. Gallery provides timeline/towns/named people/photographers, not private links or contributor photos; search engines default discouraged. | [R05-S14](<#r05-s14>) |
| **Public albums and revocable single-photo links**<br>`sharing.public_links` | C | Album custom/random slugs, replace/revoke single-photo random slugs and distinct Make public raw-image exposure; revoking burns slug instead of reviving old links later. | [R05-S14](<#r05-s14>) |
| **Album viewer/contributor/owner roles**<br>`sharing.roles` | C | Can view versus Can add photos; contributors remove only their own contributions, owner controls cover/lock/sharing. Contributions leave album when contributor exits or loses contribution rights. | [R05-S14](<#r05-s14>) |
| **Capture-time ordering**<br>`sort.capture_date` | C | User controls newest/oldest date order across lists; missing dates remain last. Per-album date sort refers to oldest member capture time, not album creation. | [R05-S23](<#r05-s23>), [R05-S15](<#r05-s15>) |

## Limitations and evidence gaps

- **explicit:** Official mobile app is unreleased/source-only. Current README summary does not establish store-distributed Android/iOS clients; released UhuruPhotos is a separate integration. ([R05-S10](<#r05-s10>), [R05-S2](<#r05-s2>))
- **explicit:** Automatic exposure brackets are not implemented despite broad README wording; only manual/burst stack workflows and file variants are established. ([R05-S4](<#r05-s4>))
- **explicit:** Metadata originals write-back uses ExifTool overwrite_original without backup; turning it off does not undo writes. Generated captions, album/hidden/archive state and title are not written; Nextcloud copies never receive write-back. ([R05-S13](<#r05-s13>))
- **explicit:** Sidecar removals do not erase original embedded metadata and removing the final keyword can expose original keywords again. Hierarchical keywords flatten; XMP PersonInImage/HierarchicalSubject are not rewritten. ([R05-S13](<#r05-s13>))
- **coverage-gap:** OCR stores all recognized text in plaintext and disabling OCR does not erase it or stop search finding it; no delete-OCR button exists. OCR guide says owner-only, while whole-library sharing guide says caption sharing includes recognized text: that privacy-documentation conflict remains unresolved. ([R05-S7](<#r05-s7>), [R05-S14](<#r05-s14>))
- **explicit:** Online tiles disclose the approximate photo area, tightly for mini-maps. Offline geocoding is town-level, not an offline basemap; cached-tile claims do not guarantee a usable completely disconnected map. ([R05-S20](<#r05-s20>), [R05-S5](<#r05-s5>))
- **explicit:** Granting original downloads exposes all embedded GPS/serial/keywords regardless of displayed-field switches. Already downloaded/shared copies cannot be recalled; collaborative public album links exclude contributor photos. ([R05-S14](<#r05-s14>))
- **explicit:** Single-photo links lack password/expiry; no jointly owned editable shared library exists. Album expiry and read-only library sharing are distinct capabilities. ([R05-S14](<#r05-s14>))
- **explicit:** Visual duplicate detection needs existing pHashes; older libraries require Rescan. Dismissed groups lose members, cannot be reverted and do not appear in the Dismissed filter despite its count. A looser run does not expand existing visual groups. ([R05-S3](<#r05-s3>))
- **explicit:** Changing InsightFace model packs does not re-encode existing faces automatically and can mix incomparable spaces; the guide requires deleting affected faces and rescanning to fully switch. Deleted-face rescan normally skips recorded deleted regions, making this operationally delicate. ([R05-S16](<#r05-s16>))
- **explicit:** Ordinary long-running jobs serialize across all users; bulk caption generation can block other jobs for hours. Transcoding prevents seeking while running and is not supplied to unauthenticated public visitors. ([R05-S22](<#r05-s22>), [R05-S8](<#r05-s8>), [R05-S23](<#r05-s23>))
- **coverage-gap:** Takeout import does not restore albums, people or favourites; invalid/over-512-KB/ambiguous JSON is skipped. Media corruption repair, GPX track sync, general crop/colour editor and E2EE are not established. ([R05-S11](<#r05-s11>), [R05-S23](<#r05-s23>))
- **coverage-gap:** Some inline guides retain stale statements: semantic-order claims differ between Search and Viewing, and older tag-write cautions conflict with versioned EXIF write-back documentation. This profile follows precise current write semantics and makes no guaranteed semantic ordering claim. ([R05-S6](<#r05-s6>), [R05-S13](<#r05-s13>), [R05-S15](<#r05-s15>), [R05-S23](<#r05-s23>))
- **Coverage gap:** OCR visibility under whole-library sharing and contradictory semantic-order text need source/runtime verification.
- **Coverage gap:** Official mobile release unavailable; preview functions deliberately separated.
- **Coverage gap:** No public code execution, benchmark, provider service test or private-library inspection performed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R05-S1

[LibrePhotos README](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/README.md>)
- Kind/ref: readme; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete README
- Establishes: Deployment, monorepo, formats, local ML, API and requirements.

### R05-S2

[1.6.0 release notes](<https://github.com/LibrePhotos/librephotos/releases/tag/1.6.0>)
- Kind/ref: release; 1.6.0
- Sections inspected: Complete release note
- Establishes: Current UI, cursor timeline, tag thresholds, Rewind, local error reporting and security/telemetry changes.

### R05-S3

[Duplicate detection](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/duplicate-detection.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: MD5 versus perceptual matching, batch algorithm, review, keeper, trash and dismissal limitations.

### R05-S4

[Stacks and file variants](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/stacks-and-file-variants.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Same-capture variants, RAW/Live pairing, sidecars, burst rules, manual stacks and unimplemented brackets.

### R05-S5

[Offline usage](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/offline-setup.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Model preload, optional models, offline geocoder and required map/update network exclusions.

### R05-S6

[Search](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/search.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Command palette, field text search, precise filters/API, optional semantic retrieval and similar photos.

### R05-S7

[Text recognition](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/text-recognition.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: OCR models, consent, plaintext privacy, search/selection, document categories and retention.

### R05-S8

[Image captioning](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/image-captioning.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Local LFM2.5-VL captions, optional identity/location context, manual batches and queue cost.

### R05-S9

[Trash](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/trash.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Restore, permanent originals deletion, optional retention and missing-record cleanup.

### R05-S10

[Official mobile source-preview guide](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/mobile/librephotos-mobile.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Explicit unreleased status, offline mirror, queued edits, camera backup and platform limitations.

### R05-S11

[Google Takeout import](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/google-takeout.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Read-only JSON fallback, filename matching, priorities and excluded Takeout fields.

### R05-S12

[Internal storage files](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/internal-files.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Derived files/models, signing secret, motion extraction, ZIP cleanup and database migration caution.

### R05-S13

[EXIF/XMP read and write semantics](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/exif-data.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Exact field precedence, sidecars, format-specific writes, personal-edit preservation and no automatic original backups.

### R05-S14

[Sharing](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/sharing.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Album roles/contributions, person/library shares, public links/settings/gallery and household ownership
- Establishes: Detailed recipient permissions, metadata-stripped delivery, revocation and public exposure boundaries.

### R05-S15

[Albums](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/albums.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Album types, events, people/birthdates/groups, sorting/covers, collections, tags and album locks
- Establishes: Precise organizational workflows and distinction between generated/curated groupings.

### R05-S16

[Face recognition workflow](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/face-recognition.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Detection/clustering/classification, manual regions, corrections, video faces, model changes and undo.

### R05-S17

[Uploads](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/upload.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: 1 MB chunks, hash preflight, album upload, cancellation/retry, processing progress and persistence prerequisites.

### R05-S18

[Statistics and visualizations](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/statistics.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Place hierarchy, monthly/stay charts, word clouds, social co-occurrence and face embedding plot.

### R05-S19

[Automatic and targeted scanning](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/auto-scan.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Schedule, incremental baseline, scan-files API, removed paths and watcher introduction
- Establishes: Native scheduling versus externally supplied filesystem watcher and safety checks.

### R05-S20

[Places and geolocation](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/places.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Offline/online lookup, tile exposure, photo-count clusters, private geofences and GPS edits.

### R05-S21

[Job system](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/job-system.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: All job categories, progress, failure/retry/restart, selective rebuilding and cancellation exceptions.

### R05-S22

[Library management](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/library.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Multiple roots, exclusions, safe move/rename, content replacement, Nextcloud, backups and administration.

### R05-S23

[Viewing photos](<https://github.com/LibrePhotos/librephotos/blob/db70302757661a8b82cc18266a2e79e29b0dccf9/apps/docs/docs/user-guide/viewing-photos.md>)
- Kind/ref: manual; db70302757661a8b82cc18266a2e79e29b0dccf9
- Sections inspected: Complete document
- Establishes: Timeline/view modes, ratings, viewer/zoom/panorama, bulk date correction and video compatibility.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
