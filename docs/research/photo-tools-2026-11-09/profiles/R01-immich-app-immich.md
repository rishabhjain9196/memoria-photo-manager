# R01 — immich-app/immich

[Repository](<https://github.com/immich-app/immich>) · 118,609 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Self-hosted photo/video server with mobile backup, managed and external libraries, local ML search/people organization, sharing and extensive background maintenance.

**Deployment:** Self-hosted Docker Compose server with PostgreSQL and separate ML service; Browser client; Android and iOS mobile clients; Node/npm or Docker upload CLI

**Storage:** Managed uploads retain unmodified originals under upload or optional template-organized library directories; database stores paths, user metadata and relationships. Thumbnails, encoded video, profiles and database backups occupy separate directories. External libraries index mounted folders without copying and may write XMP/delete originals only when mounts permit. Catalogue database and originals must both be backed up.

**Privacy/network behavior:** Core storage and inference can stay on the operator's server, but models initially download, default map styles/tiles use external infrastructure, optional Cast loads Google scripts, and configured OIDC/SMTP/remote ML can involve other systems. Remote ML receives previews and lacks its own authentication controls. PIN-locked assets are session access controls, not established E2EE or at-rest encryption. v3.3.6 disables unintended upstream ONNX Runtime telemetry.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v3.3.6 (2026-11-04T17:24:55Z)
**Repository pushed at:** 2026-11-09T14:26:02Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [dae37df1a70c](<https://github.com/immich-app/immich/commit/dae37df1a70c21493acdafd85bad8ab69e6b390d>).
**Product lineage:** immich-app/immich.

## Maturity and availability caveats

- Frozen main dae37df1a70c21493acdafd85bad8ab69e6b390d; latest manifest release v3.3.6 dated 2026-11-04. Pinned main documentation can be ahead of that release.
- Support documentation says all features remain free; purchasing a user/server license supports development rather than unlocking a feature tier.
- Experimental areas explicitly include external-library filesystem watching, hardware acceleration and Google Cast.
- Important current docs qualify older claims: read-only external metadata edits fail, video face analysis is thumbnail-only, and auto album ordering is not implemented.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **NSFW filtering**<br>`ai.content_moderation` | N | FAQ explicitly says NSFW image filtering is unavailable; an open request is not an implemented feature. | [R01-S25](<#r01-s25>) |
| **Incremental person clustering**<br>`ai.face_clustering` | C | DBSCAN-derived clustering uses recognition distance/core-point minimums, preserves prior people incrementally and revisits unassigned candidates nightly. | [R01-S5](<#r01-s5>) |
| **Merge and assign face groups**<br>`ai.face_corrections` | C | Merge detected people, manually assign unassigned faces and requeue missing/all recognition after tuning; existing results may need reprocessing. | [R01-S5](<#r01-s5>) |
| **Detect face regions**<br>`ai.face_detection` | C | ML service processes generated previews into scored boxes and face embeddings; configurable detection score filters false positives. | [R01-S5](<#r01-s5>) |
| **Name and curate people**<br>`ai.face_naming` | C | Name groups, change feature photo, hide people and favorite/pin them; set birthdate to show age when an image was taken. | [R01-S5](<#r01-s5>) |
| **Identity matching**<br>`ai.face_recognition` | C | Recognition compares saved face embeddings and assigns identities; on videos this is only faces visible in the generated thumbnail, not full-video analysis. | [R01-S5](<#r01-s5>), [R01-S25](<#r01-s25>) |
| **Full-video facial scanning**<br>`ai.full_video_face_scan` | R | FAQ limits current video face recognition to a generated thumbnail and mentions possible future whole-video scanning. | [R01-S25](<#r01-s25>) |
| **Self-hosted ML inference**<br>`ai.local_inference` | C | Default ML container processes previews on the self-hosted system and downloads missing models; inference is not synonymous with a guaranteed air-gapped first run. | [R01-S5](<#r01-s5>), [R01-S22](<#r01-s22>) |
| **Background text recognition**<br>`ai.ocr` | C | OCR is a first-class background processing task; optional supported acceleration also covers OCR model processing. | [R01-S17](<#r01-s17>), [R01-S21](<#r01-s21>) |
| **Optional remote ML worker**<br>`ai.remote_inference` | O | Send preview images to another ML container, optionally retaining local fallback. URLs are tried sequentially, not load-balanced; recognition clustering remains server/database-side. | [R01-S22](<#r01-s22>) |
| **CLI directory-to-album import**<br>`albums.folder_mapping` | C | CLI --album creates albums from each uploaded file's containing folder or --album-name targets one album. External-library scans do not natively create matching albums. | [R01-S19](<#r01-s19>), [R01-S25](<#r01-s25>) |
| **User-created albums**<br>`albums.manual` | C | Create albums and add uploaded/external assets; albums are independent of physical storage unless optional template behavior uses album names. | [R01-S2](<#r01-s2>), [R01-S7](<#r01-s7>), [R01-S26](<#r01-s26>) |
| **Custom album photo ordering**<br>`albums.manual_order` | R | FAQ says manual reordering is not yet available and links a planned-feature discussion. | [R01-S25](<#r01-s25>) |
| **Person collections**<br>`albums.people` | C | Explore people and view all assets containing a selected person's face. | [R01-S5](<#r01-s5>) |
| **Account usage and quota statistics**<br>`analytics.library_statistics` | C | Account settings show usage and admins can see per-user quota percentages in Server Stats. | [R01-S18](<#r01-s18>), [R01-S33](<#r01-s33>) |
| **Folder navigation alongside timeline**<br>`browse.folders` | C | Enable folder view to navigate external directory trees or template-organized managed assets. | [R01-S1](<#r01-s1>), [R01-S2](<#r01-s2>) |
| **Years-ago memories**<br>`browse.memories` | C | Both clients show past-date memories; scheduled generation defaults to nightly tasks. | [R01-S1](<#r01-s1>), [R01-S17](<#r01-s17>) |
| **360-degree image viewing**<br>`browse.panorama` | C | README marks 360-degree display available on web, not mobile. | [R01-S1](<#r01-s1>) |
| **Stack related assets**<br>`browse.stacks` | C | Both clients support stacked photos; duplicate review can stack multiple retained candidates. | [R01-S1](<#r01-s1>), [R01-S6](<#r01-s6>) |
| **Scrubbable chronological browsing**<br>`browse.timeline` | C | Mobile/web matrix documents draggable timeline scrollbars, with external and uploaded media appearing together. | [R01-S1](<#r01-s1>), [R01-S2](<#r01-s2>) |
| **Video viewing**<br>`browse.video_playback` | C | Both clients view uploaded videos and use separately generated compatibility transcodes; originals remain unchanged. | [R01-S1](<#r01-s1>), [R01-S15](<#r01-s15>), [R01-S25](<#r01-s25>) |
| **Virtual scrolling**<br>`browse.virtualization` | C | README explicitly lists virtual scroll on both mobile and web; this is stronger evidence than ordinary lazy image loading. | [R01-S1](<#r01-s1>) |
| **Free Up Space on device**<br>`cleanup.backed_up_device_copies` | C | Review/delete only device assets already backed up and not in server trash, with cutoff date, keep favorites/albums and keep photo/video options; iCloud Shared Album items are excluded. | [R01-S27](<#r01-s27>) |
| **Android client**<br>`deployment.android` | C | Android mobile app offers backup, viewing and platform-specific charging/delay controls. | [R01-S3](<#r01-s3>), [R01-S27](<#r01-s27>) |
| **Docker Compose services**<br>`deployment.docker` | C | Documented server/ML containers and volume mounts support split workers and optional remote ML. | [R01-S2](<#r01-s2>), [R01-S17](<#r01-s17>), [R01-S22](<#r01-s22>) |
| **iOS client**<br>`deployment.ios` | C | iOS app supports selective/background backup subject to OS scheduling and Background App Refresh. | [R01-S3](<#r01-s3>) |
| **Translated application interface**<br>`deployment.localization` | C | Weblate-managed application locales translate user-facing controls and use ICU for locale-specific plural/number/date messages. Inspected French catalogue covers account settings, albums, tags, uploads and actions; this is UI localization, not multilingual CLIP search. Translation completeness varies and was not measured. | [R01-S34](<#r01-s34>), [R01-S35](<#r01-s35>) |
| **Self-hosted media server**<br>`deployment.selfhosted` | C | Server manages owned uploads and mounted media without requiring a third-party photo-storage account. | [R01-S1](<#r01-s1>), [R01-S2](<#r01-s2>), [R01-S15](<#r01-s15>) |
| **Browser application**<br>`deployment.web` | C | Browser upload/view, administration, people, tags and sharing are explicitly in the client matrix. | [R01-S1](<#r01-s1>) |
| **Retain multiple candidates**<br>`duplicates.keep_all` | C | More than one asset can be retained and optionally stacked; retained assets then keep their own metadata rather than merging it. | [R01-S6](<#r01-s6>) |
| **Keeper choice and preselection**<br>`duplicates.keeper_selection` | C | Choose which candidates to retain/trash; suggested keeper preference uses larger byte size then richer EXIF count, not a measured aesthetic-quality score. | [R01-S6](<#r01-s6>) |
| **Preserve metadata when deduplicating**<br>`duplicates.metadata_merge` | C | Only exactly one keeper plus at least one trashed asset triggers merge: union albums/tags, any favorite, highest rating, combined descriptions, most restrictive visibility and GPS only when nonempty coordinates agree. | [R01-S6](<#r01-s6>) |
| **Visual duplicate suggestions**<br>`duplicates.similar_images` | C | Enabled-by-default ML utility groups visually similar assets for review; distinct from exact upload checksum deduplication. | [R01-S6](<#r01-s6>), [R01-S17](<#r01-s17>) |
| **Non-destructive crop**<br>`editing.crop` | C | Crop creates an edited version and can be reverted to the original. | [R01-S9](<#r01-s9>) |
| **Experimental hardware transcoding**<br>`editing.hardware_encoding` | O | NVENC/QSV/RKMPP/VAAPI can accelerate encoding, with optional decoding. Hardware, codec, Linux/WSL and quality/size tradeoffs apply; Raspberry Pi is unsupported in this guide. | [R01-S20](<#r01-s20>) |
| **Rotation and mirroring**<br>`editing.rotate_flip` | C | Photo edit controls include rotation and mirroring. | [R01-S9](<#r01-s9>) |
| **Compatibility video derivatives**<br>`editing.video_transcode` | C | Transcode policy generates web-compatible derivatives without replacing originals; changing policy and rerunning jobs can delete unnecessary transcodes. | [R01-S15](<#r01-s15>), [R01-S25](<#r01-s25>) |
| **AVIF support**<br>`formats.avif` | C | AVIF is explicitly supported. | [R01-S14](<#r01-s14>) |
| **HEIC/HEIF support**<br>`formats.heic` | C | Both HEIC and HEIF are explicitly supported image formats. | [R01-S14](<#r01-s14>) |
| **JPEG XL support**<br>`formats.jpegxl` | C | JPEG XL .jxl is explicitly supported. | [R01-S14](<#r01-s14>) |
| **Live Photo backup/playback**<br>`formats.live_photos` | C | README explicitly lists Apple Live Photo backup and playback on mobile and web. | [R01-S1](<#r01-s1>) |
| **Motion Photo backup/playback**<br>`formats.motion_photos` | C | Motion Photo backup/playback appears in both client columns. | [R01-S1](<#r01-s1>) |
| **RAW media support**<br>`formats.raw` | C | Client matrix and supported-format table establish RAW/RW2 support; full decoder/extension list is maintained separately. | [R01-S1](<#r01-s1>), [R01-S14](<#r01-s14>) |
| **SVG media support**<br>`formats.svg` | C | Supported-format table includes SVG. | [R01-S14](<#r01-s14>) |
| **Configurable map tile/style provider**<br>`geo.custom_map_provider` | O | Set separate light/dark style JSON URLs and choose another tile provider rather than the default tiles.immich.cloud styles. Offline basemap provisioning is not established. | [R01-S24](<#r01-s24>) |
| **Global media map**<br>`geo.map` | C | Both clients display geotagged assets on a global map; map tile/style services are distinct from local reverse geocoding. | [R01-S1](<#r01-s1>), [R01-S24](<#r01-s24>) |
| **Server-local reverse lookup**<br>`geo.offline_geocoding` | C | GeoNames data is loaded into PostgreSQL on minor upgrades; city/state/country queries then run locally. | [R01-S13](<#r01-s13>) |
| **OpenAPI and scoped API keys**<br>`integration.api` | C | Documented OpenAPI with generated TypeScript/Dart clients; web users create API keys with restricted permissions and can manage logged-in devices. | [R01-S19](<#r01-s19>), [R01-S31](<#r01-s31>), [R01-S33](<#r01-s33>) |
| **Opt-in web Google Cast**<br>`integration.cast` | O | Experimental photo/video Cast requires Google scripts, public HTTPS/reachable Google DNS and Cast-compatible video formats. | [R01-S23](<#r01-s23>) |
| **Recursive upload CLI**<br>`integration.cli` | C | CLI supports recursive paths, globs, albums, visibility, dry run, JSON output, upload concurrency, filesystem watching and explicit local-delete/delete-duplicate options. | [R01-S19](<#r01-s19>) |
| **Mobile Cast**<br>`integration.mobile_cast` | R | Cast manual explicitly reserves Android/iOS support for future development. | [R01-S23](<#r01-s23>) |
| **OIDC single sign-on**<br>`integration.oidc` | O | Configure third-party provider, mobile/web redirects, auto-registration/launch and backchannel logout. Role/quota claims can synchronize on login; default storage label is registration-only unless changed. | [R01-S30](<#r01-s30>) |
| **Optional storage templates**<br>`library.auto_date_folders` | O | Admin templates control directory/filename pattern using date/name/album and conditional fields; migration jobs apply changes retroactively. Date variables use server timezone. | [R01-S26](<#r01-s26>), [R01-S15](<#r01-s15>) |
| **iCloud-backed mobile asset retrieval**<br>`library.cloud_import` | C | Selected iOS albums can pull missing iCloud assets into temporary device cache for hashing/upload, then clear temporary files; requires extra data and device space. | [R01-S3](<#r01-s3>) |
| **Content-checksum upload deduplication**<br>`library.deduplicate_import` | C | Mobile/CLI hashes avoid re-uploading known content across upload methods/devices; server still hashes if CLI prehash is skipped. Upload-library scope is not global across accounts/external libraries. | [R01-S3](<#r01-s3>), [R01-S19](<#r01-s19>), [R01-S25](<#r01-s25>) |
| **Case-insensitive glob exclusions**<br>`library.exclude_folders` | C | Per-library full-path patterns exclude extensions/subtrees; matching existing assets are offlined on later scan. CLI also accepts ignore globs. | [R01-S2](<#r01-s2>), [R01-S19](<#r01-s19>) |
| **External folders indexed in place**<br>`library.existing_folders` | C | External files appear in normal timeline/maps/albums after scanning without managed-copy import; modified source files require rescan. | [R01-S2](<#r01-s2>) |
| **Download original or edited media**<br>`library.export_originals` | C | Clients download photos/videos; edited assets default to edited output but original version can be selected. | [R01-S1](<#r01-s1>), [R01-S9](<#r01-s9>) |
| **Experimental external-library watching**<br>`library.filesystem_watch` | O | Advanced-user watcher auto-imports changes but may fail on network drives and requires sufficient OS watcher capacity. | [R01-S2](<#r01-s2>) |
| **Managed uploads**<br>`library.import_copy` | C | Web/mobile/CLI originals are copied into managed upload storage with separate derivatives. | [R01-S15](<#r01-s15>) |
| **Scheduled external rescans**<br>`library.incremental_scan` | C | Nightly scans and manually triggered scans refresh libraries; admin can select presets or a cron schedule. | [R01-S2](<#r01-s2>) |
| **One-way device album synchronization**<br>`library.mobile_album_sync` | C | Creates/merges same-named server albums and backfills existing uploads. Later local deletes/reordering do not propagate; matching already-shared server albums share the newly added media. | [R01-S3](<#r01-s3>), [R01-S27](<#r01-s27>) |
| **Selective background mobile backup**<br>`library.mobile_backup` | C | Choose included/excluded device albums, upload on app open/resume and background opportunities; Wi-Fi-only is default, configurable. Individual local-only assets can be uploaded manually. | [R01-S3](<#r01-s3>), [R01-S27](<#r01-s27>) |
| **Multiple external import paths**<br>`library.multiple_roots` | C | One external library can recursively scan multiple mounted roots, adding a path only once when roots overlap. | [R01-S2](<#r01-s2>) |
| **Community Google Takeout importer**<br>`library.takeout_import` | P | Official CLI documentation recommends separate community-maintained immich-go for Google Photos Takeout rather than claiming native CLI Takeout parsing. | [R01-S19](<#r01-s19>) |
| **SMTP account/album notifications**<br>`maintenance.notifications` | O | Notify new users, users added to shared albums and collaborators about new assets; per-user controls and custom HTML templates are documented. | [R01-S28](<#r01-s28>) |
| **Regenerate or remove derivatives**<br>`maintenance.selective_reset` | C | Queue missing/all thumbnail/transcode jobs separately from originals; policy changes can remove unnecessary encoded video without deleting original media. | [R01-S16](<#r01-s16>), [R01-S25](<#r01-s25>) |
| **Archive without deletion**<br>`library.archive` | C | Archive hides media from main timeline/folder view but retains it in search and a dedicated archive view; not a privacy vault. | [R01-S25](<#r01-s25>) |
| **Asset descriptions**<br>`metadata.comments` | C | Descriptions are editable/searchable and written to dc:description/tiff:ImageDescription sidecar fields. | [R01-S4](<#r01-s4>), [R01-S12](<#r01-s12>) |
| **Edit capture timestamps**<br>`metadata.date_fix` | C | Timestamp edits are supported and XMP DateTimeOriginal/DateCreated fields are written; read-only external mounts prevent editing. | [R01-S12](<#r01-s12>), [R01-S25](<#r01-s25>) |
| **Camera and capture metadata**<br>`metadata.exif_read` | C | View EXIF/GPS and filter camera make/model/lens; extracted metadata drives location/date behavior. | [R01-S1](<#r01-s1>), [R01-S4](<#r01-s4>), [R01-S13](<#r01-s13>) |
| **Import existing face metadata**<br>`metadata.face_region_import` | C | FAQ says embedded asset face/person metadata creates faces and people on import; not limited to new ML discovery. | [R01-S25](<#r01-s25>) |
| **Favorite assets**<br>`metadata.favorites` | C | Favorites are available on both clients, usable as filters and merged when resolving a duplicate group to one keeper. | [R01-S1](<#r01-s1>), [R01-S4](<#r01-s4>), [R01-S6](<#r01-s6>) |
| **Edit location metadata**<br>`metadata.gps_write` | C | Location edits persist in database/XMP GPS latitude/longitude, not original file bytes; read-only external mounts cannot accept edits. | [R01-S12](<#r01-s12>), [R01-S25](<#r01-s25>) |
| **Hierarchical tag management**<br>`metadata.hierarchical_tags` | C | Enable Tags view, create/assign tags to photos/videos and navigate by tag; README limits Tags UI to web. | [R01-S1](<#r01-s1>), [R01-S11](<#r01-s11>) |
| **Import IPTC keywords**<br>`metadata.iptc_read` | C | Tags can be imported from IPTC Keywords as well as XMP hierarchical tag fields; not a claim of full IPTC coverage. | [R01-S11](<#r01-s11>), [R01-S12](<#r01-s12>) |
| **Star ratings**<br>`metadata.ratings` | C | Assign searchable star ratings and read/write XMP Rating; duplicate resolution preserves highest group rating. | [R01-S4](<#r01-s4>), [R01-S6](<#r01-s6>), [R01-S12](<#r01-s12>) |
| **Merged sidecar write-back**<br>`metadata.sidecar_write` | C | Selected edited metadata is written to XMP without replacing unrelated fields; managed imports copy sidecars, and external write-back requires a writable mount. Discover/Sync jobs handle later sidecars. | [R01-S12](<#r01-s12>) |
| **Read companion XMP**<br>`metadata.xmp_read` | C | Reads supported description/rating/date/GPS/tag fields; filename.ext.xmp wins over filename.xmp. Other sidecar fields remain stored but are not searchable. | [R01-S12](<#r01-s12>) |
| **Dependent background processing**<br>`performance.background_jobs` | C | Job pipeline covers metadata, template migration, thumbnails, smart search, faces, OCR, video and duplicates, plus separately configurable nightly jobs; admin views job state. | [R01-S17](<#r01-s17>) |
| **Optional GPU/NPU ML**<br>`performance.gpu_ml` | O | Experimental ARM NN, CUDA, ROCm, OpenVINO and RKNN backends have model/device/driver limits; ARM NN does not accelerate query-time text search. | [R01-S21](<#r01-s21>) |
| **Separate API and processing workers**<br>`performance.split_workers` | O | Include/exclude worker settings let containers isolate web/API work from background processing and distribute resources. | [R01-S17](<#r01-s17>) |
| **Multiple generated preview levels**<br>`performance.thumbnail_cache` | C | Maintains blurred thumbhash, WebP previews, JPEG thumbnails and person face thumbnails in derivative storage. | [R01-S15](<#r01-s15>), [R01-S25](<#r01-s25>) |
| **Mobile offline capability**<br>`privacy.offline_use` | C | README marks offline support on mobile, not web. Inspected docs do not specify guarantees that all remote originals/search/models are available offline. | [R01-S1](<#r01-s1>) |
| **PIN-locked assets**<br>`privacy.pin_locked_folder` | C | Locked Folder hides assets until session unlock; access initially lasts 15 minutes and can extend with activity. While unlocked, locked assets may appear in search/utilities; Lock/sign-out revokes access. | [R01-S10](<#r01-s10>) |
| **Application trash**<br>`safety.app_recovery` | C | Trash delays permanent deletion. Missing external files move to trash on rescan and restoration requires restoring the source; their metadata is discarded after documented 30-day removal. | [R01-S2](<#r01-s2>), [R01-S25](<#r01-s25>) |
| **Scheduled database backups and restore**<br>`safety.catalogue_backup` | C | Default daily 2am dumps retain 14 copies; manual backups and UI restore are supported. Restore creates a rollback point, migrates/checks health and rolls back on failure. Media is not in database dumps. | [R01-S15](<#r01-s15>) |
| **Persistent checksum integrity checking**<br>`safety.integrity_check` | C | Scheduled checks compare stored/actual checksums and detect missing/untracked paths; checks default nightly at 3am with configurable time/progress budgets and refresh-only-reported options. | [R01-S16](<#r01-s16>) |
| **Managed naming collisions avoided**<br>`safety.no_overwrite` | C | Default UUID names avoid filename collisions; template collisions append a sequence number rather than overwrite. | [R01-S25](<#r01-s25>), [R01-S26](<#r01-s26>) |
| **Original-preserving edits**<br>`safety.nondestructive_edits` | C | Image edits create another version; metadata writes use sidecars/database. Original bytes are retained, though emptying trash can delete originals. | [R01-S9](<#r01-s9>), [R01-S25](<#r01-s25>) |
| **Native trash for mobile cleanup**<br>`safety.os_trash` | C | Free Up Space confirms a reviewed list then moves assets to native trash in batches (Android 2000/iOS 10000); manually empty OS trash to reclaim space immediately. | [R01-S27](<#r01-s27>) |
| **Mobile read-only/kid mode**<br>`safety.read_only_client` | C | Read-only app mode permits timeline viewing while preventing accidental device photo deletion; not an encrypted vault. | [R01-S27](<#r01-s27>) |
| **Read-only external mounts**<br>`safety.read_only_originals` | C | Docker :ro protects external original files; metadata edits also cannot persist, and files trashed in UI can return after trash-empty/rescan because disk deletion is denied. | [R01-S2](<#r01-s2>), [R01-S12](<#r01-s12>), [R01-S25](<#r01-s25>) |
| **Startup storage health checks**<br>`safety.storage_mount_checks` | C | Read/write marker checks validate expected storage mounts and permissions; failed checks normally prevent server startup. | [R01-S16](<#r01-s16>) |
| **Time-frame filters**<br>`search.date_range` | C | Search with start/end time bucket dates. | [R01-S4](<#r01-s4>) |
| **Photo/video filters**<br>`search.file_type` | C | Restrict search to images, videos or both and filename extensions. | [R01-S4](<#r01-s4>) |
| **Filename, extension and path search**<br>`search.filename_path` | C | Full/partial filenames, extensions, folder names and original path fragments are searchable. | [R01-S4](<#r01-s4>) |
| **Place search**<br>`search.location` | C | Search city/state/country generated by local reverse geocoding. | [R01-S4](<#r01-s4>), [R01-S13](<#r01-s13>) |
| **Combined metadata filters**<br>`search.metadata` | C | Filter descriptions, camera/lens, albums and archive/favorite/not-in-album state alongside other search criteria. | [R01-S4](<#r01-s4>) |
| **Multilingual semantic models**<br>`search.multilingual_semantic` | O | Choose supported multilingual models; nllb uses the user's language setting while xlm/siglip2 understand language independently. Changing models requires rerunning Smart Search. | [R01-S4](<#r01-s4>) |
| **Recognized-text search**<br>`search.ocr` | C | Search text inside images; background pipeline explicitly includes an OCR job after thumbnail generation. | [R01-S4](<#r01-s4>), [R01-S17](<#r01-s17>) |
| **Multi-person search**<br>`search.people` | C | Filter assets containing one or more recognized faces and browse a named person's media. | [R01-S4](<#r01-s4>), [R01-S5](<#r01-s5>) |
| **Star-rating search**<br>`search.ratings` | C | Advanced search explicitly includes user-assigned star ratings. | [R01-S4](<#r01-s4>) |
| **CLIP semantic search**<br>`search.semantic_text` | C | PostgreSQL/VectorChord searches image embeddings against freeform text without requiring explicit keywords; supported model choices trade accuracy, latency and memory. | [R01-S4](<#r01-s4>), [R01-S25](<#r01-s25>) |
| **Tag search**<br>`search.tags` | C | Filter assigned/imported tags and open tag-specific media views. | [R01-S4](<#r01-s4>), [R01-S11](<#r01-s11>) |
| **Shared album contributions**<br>`sharing.collaborative_albums` | C | Instance users can contribute their own photos/videos to shared albums when given editor permission. | [R01-S7](<#r01-s7>) |
| **Expiring shares**<br>`sharing.expiring_links` | C | Public-link configuration includes an expiration date. | [R01-S7](<#r01-s7>) |
| **Upload through a shared link**<br>`sharing.guest_upload` | C | Permit non-account visitors to contribute photos/videos into the owner's account using a configured public share. | [R01-S7](<#r01-s7>) |
| **Separate user accounts**<br>`sharing.multiuser` | C | Multiple users own assets and libraries, with admin-managed passwords and per-user settings; accounts are not counted as selectable multiple catalogues. | [R01-S18](<#r01-s18>), [R01-S33](<#r01-s33>) |
| **One-way partner library sharing**<br>`sharing.partner_library` | C | Grant broad asset/metadata/download/resharing access with optional per-partner timeline inclusion. Person data and favorites are not shared; both parties must grant separately for reciprocity. | [R01-S8](<#r01-s8>) |
| **Password-protected shares**<br>`sharing.password_links` | C | Public links can require a password. | [R01-S7](<#r01-s7>) |
| **Public asset/album links**<br>`sharing.public_links` | C | Random-secret URLs share selected photos/videos or albums with non-users and configurable permitted actions. | [R01-S7](<#r01-s7>) |
| **Album editor/viewer permissions**<br>`sharing.roles` | C | Assign shared users read-write editor or read-only viewer permissions on albums. | [R01-S7](<#r01-s7>) |
| **Account storage quotas**<br>`sharing.storage_quotas` | C | Admins set GiB quotas that block further upload when exceeded; external libraries do not count against the quota. | [R01-S18](<#r01-s18>) |

## Limitations and evidence gaps

- **explicit:** Back up originals and database independently. Automatic database backups contain metadata only, not pictures/videos; managed originals must not be modified/moved manually. ([R01-S15](<#r01-s15>), [R01-S16](<#r01-s16>))
- **explicit:** Each external library has one immutable owner. Moving an external file is treated as a new asset on rescan and can lose Immich-only metadata/album membership. Read-only mounts block metadata writes, potentially silently. ([R01-S2](<#r01-s2>), [R01-S12](<#r01-s12>), [R01-S25](<#r01-s25>))
- **explicit:** Exact import deduplication is not global across users/external libraries. Visual duplicate suggestions are different from byte equality or full-video similarity. Face analysis of video is thumbnail-only. ([R01-S3](<#r01-s3>), [R01-S6](<#r01-s6>), [R01-S25](<#r01-s25>))
- **explicit:** Free Up Space also deletes from iCloud and other Apple devices when iCloud sync is enabled, and can remove media needed by WhatsApp chat history; keep relevant albums and maintain independent server backups. ([R01-S27](<#r01-s27>))
- **explicit:** iOS controls background timing; Android battery policies may suppress workers. Some custom network authentication/certificate features are experimental and can break media transfers/playback. ([R01-S3](<#r01-s3>), [R01-S25](<#r01-s25>))
- **explicit:** Remote ML exposes previews to its operator and has no built-in access security. Multiple configured ML URLs are sequential fallback, not load balancing. Models/maps/Cast can require external network access; v3.3.6 specifically disables unintended upstream telemetry. ([R01-S22](<#r01-s22>), [R01-S23](<#r01-s23>), [R01-S24](<#r01-s24>), [R01-S32](<#r01-s32>))
- **explicit:** Smart Search uses embeddings, not generated editable object tags/captions. Arbitrary custom CLIP models are unsupported; only listed compatible models work. Animal identity recognition and backup-time original-image compression are explicitly unavailable. ([R01-S4](<#r01-s4>), [R01-S25](<#r01-s25>))
- **explicit:** Hardware acceleration is experimental and platform/model dependent; transcodes can be larger/lower quality at comparable settings. HDR player color issues are acknowledged. ([R01-S20](<#r01-s20>), [R01-S21](<#r01-s21>), [R01-S25](<#r01-s25>))
- **coverage-gap:** Inspected evidence does not establish E2EE, encrypted originals, guaranteed offline basemaps or durable per-file-operation/crash-recovery journaling. Locked Folder, trash and catalogue rollback are distinct features. ([R01-S10](<#r01-s10>), [R01-S15](<#r01-s15>), [R01-S24](<#r01-s24>), [R01-S25](<#r01-s25>))
- **explicit:** Library guide says read-only mounts disallow UI deletion, while FAQ describes UI trash followed by reappearance. Both agree that filesystem originals cannot be deleted; exact UI behavior may vary by version. ([R01-S2](<#r01-s2>), [R01-S25](<#r01-s25>))
- **Coverage gap:** Model benchmark tables were sampled only after reading complete selection/methodology prose; no benchmark claims are presented as our measurements.
- **Coverage gap:** Mobile offline cache scope, encryption and operation journaling are not established.
- **Coverage gap:** Current pinned documentation may precede release availability and contains one qualified read-only-trash UI inconsistency.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R01-S1

[Immich README](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/README.md>)
- Kind/ref: readme; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete README and mobile/web feature matrix
- Establishes: Baseline client capabilities and backup warning.

### R01-S2

[External libraries](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/libraries.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Multi-path in-place scans, exclusions, watching, ownership, read-only and move/delete limitations.

### R01-S3

[Mobile backup](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/mobile-backup.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Album selection, checksums, background/network behavior and iCloud downloading.

### R01-S4

[Search and model selection](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/searching.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete search/filter/configuration/model-choice prose and benchmark-methodology reference; opening English model table
- Establishes: Metadata/OCR/semantic search, multilingual model choices and reindexing requirements; model tables are estimates.

### R01-S5

[Facial recognition](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/facial-recognition.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Face detection, embeddings, incremental DBSCAN-like groups, correction and tuning.

### R01-S6

[Duplicates utility](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/duplicates-utility.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Visual similarity review, keeper preselection, stacks and conditional metadata merge.

### R01-S7

[Sharing](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/sharing.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Editor/viewer albums and public links with password, expiry and guest upload.

### R01-S8

[Partner sharing](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/partner-sharing.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: One-way library sharing, timeline integration, metadata exposure and exclusions.

### R01-S9

[Photo editing](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/editing.mdx>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Reversible crop/rotate/mirror and original/edited download choice.

### R01-S10

[Locked folder](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/locked-folder.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: PIN/session elevation, temporary visibility and relocking.

### R01-S11

[Hierarchical tags](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/tags.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Create/browse tags, import XMP/IPTC and sidecar persistence.

### R01-S12

[XMP sidecars](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/xmp-sidecars.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page and read/write field table
- Establishes: Exact supported fields, merge behavior, naming, discovery/sync and read-only failures.

### R01-S13

[Local reverse geocoding](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/reverse-geocoding.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: GeoNames data in PostgreSQL for city/state/country lookup.

### R01-S14

[Supported media formats](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/supported-formats.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete image/video format tables
- Establishes: RAW, HEIC, AVIF, JPEG XL, SVG and video container coverage.

### R01-S15

[Backup and restore](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/administration/backup-and-restore.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Database/UI restore sections through Restore Process; complete Filesystem/storage-location/backup-order sections
- Establishes: Scheduled catalogue dumps, rollback, storage separation and mandatory independent original backups.

### R01-S16

[System integrity](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/administration/system-integrity.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Missing/untracked/checksum checks with bounded scheduling and storage mount markers.

### R01-S17

[Jobs and workers](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/administration/jobs-workers.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Background pipeline, job dependencies, nightly schedules and split workers.

### R01-S18

[User management](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/administration/user-management.mdx>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: All inline sections including quotas, labels, passwords and deletion; imported onboarding partials not inspected
- Establishes: Account quotas and deletion delays.

### R01-S19

[Upload CLI](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/command-line-interface.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Recursive/glob uploads, hash checks, albums, dry run, deletion/watch and community Takeout tool.

### R01-S20

[Hardware transcoding](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/hardware-transcoding.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: NVENC/QSV/RKMPP/VAAPI configuration, quality/platform limitations and optional hardware decoding.

### R01-S21

[ML hardware acceleration](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/ml-hardware-acceleration.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Overview, supported backends, limitations and complete prerequisite sections through RKNN
- Establishes: Mali/CUDA/ROCm/OpenVINO/RKNN, hardware/model restrictions and memory tradeoffs.

### R01-S22

[Remote ML](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/guides/remote-machine-learning.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Preview transmission, local fallback, sequential URLs and insecure internal-service boundary.

### R01-S23

[Chromecast](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/casting.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Opt-in web casting, external Google scripts and public HTTPS/DNS prerequisites.

### R01-S24

[Custom map styles](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/guides/custom-map-styles.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Default remote map styles and configurable tile/style providers.

### R01-S25

[FAQ capability boundaries](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/FAQ.mdx>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Mobile background/network questions; complete Assets, Albums and External Library sections; ML questions through animal recognition and face-threshold advice
- Establishes: Original preservation, trash, import scope, video-thumbnail ML and explicit unavailable features.

### R01-S26

[Storage-template content](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/partials/_storage-template.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete template-builder/migration content
- Establishes: Date/name/album templates, collision suffixes and migration.

### R01-S27

[Mobile selective upload and cleanup](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/mobile-app.mdx>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete inline selected-photo upload, Free Up Space, iCloud/app-dependency, Album Sync and read-only-mode sections
- Establishes: Selective upload, safe-review cleanup, iCloud deletion propagation and album-sync limits.

### R01-S28

[Email notifications](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/administration/email-notification.mdx>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: SMTP account/album events, per-user controls and custom HTML templates.

### R01-S29

[Support and purchase model](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/overview/support-the-project.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: User/server purchase is support; all features remain free.

### R01-S30

[OIDC authentication](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/administration/oauth.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Overview, prerequisites, full settings/claim semantics, Auto Launch and Mobile Redirect sections
- Establishes: External authentication, registration, role/quota claim sync and logout.

### R01-S31

[API documentation](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/api.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: OpenAPI and generated TypeScript/Dart clients.

### R01-S32

[v3.3.6 privacy fix](<https://github.com/immich-app/immich/releases/tag/v3.3.6>)
- Kind/ref: release; v3.3.6
- Sections inspected: Complete release note
- Establishes: Disables unexpected ONNX Runtime telemetry to Microsoft.

### R01-S33

[User account settings](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/features/user-settings.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page
- Establishes: Profile, features, API keys, logged-in devices and usage statistics.

### R01-S34

[Application translation guide](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/docs/docs/developer/translations.md>)
- Kind/ref: manual; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Complete page: Weblate, international message format and translation progress
- Establishes: Project localization process and locale-aware ICU message handling.

### R01-S35

[French application messages](<https://github.com/immich-app/immich/blob/dae37df1a70c21493acdafd85bad8ab69e6b390d/i18n/fr.json>)
- Kind/ref: code; dae37df1a70c21493acdafd85bad8ab69e6b390d
- Sections inspected: Account, account-settings and add-action/add-media/album/tag/upload messages, including ICU plural/select messages
- Establishes: Actual translated interface messages, distinct from translated documentation or semantic-search models.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
