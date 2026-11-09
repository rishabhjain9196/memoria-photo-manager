# R02 — photoprism/photoprism

[Repository](<https://github.com/photoprism/photoprism>) · 40,424 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Self-hosted photo/video catalogue with in-place indexing or managed import, local recognition, rich metadata/search, linked-media stacks and controlled sharing; paid memberships add specific roles, administration and formats/maps.

**Deployment:** Docker browser application on Windows/macOS/Linux hosts; AMD64 and ARM64 including Raspberry Pi/Apple Silicon; Installable browser PWA rather than native Windows/macOS mobile clients; Linux tar packages/manual source builds for experienced administrators; optional managed hosting

**Storage:** Originals folder preserves existing hierarchy when indexed; optional import copies/moves into canonical date-organized names. Storage folder holds derivatives, JSON/YAML sidecars, configuration, backups and SQLite where used; MariaDB is supported and October 2026 release adds experimental PostgreSQL. Multiple host roots can be mounted below one originals root. Accounts normally share that library, not separate catalogues.

**Privacy/network behavior:** Built-in ONNX labels/faces execute locally; optional Ollama may be self-hosted and OpenAI/Ollama Cloud require network/API keys. Maps and reverse geocoding contact PhotoPrism/MapTiler services. Read-only mode plus read-only mounts protect originals, while normal mode allows specific changes. Private media/people and role restrictions are access controls, not encryption; no E2EE or guaranteed air-gap claim.

**License metadata:** NOASSERTION. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 261029-963b58c50 (2026-10-29T22:20:43Z)
**Repository pushed at:** 2026-11-09T12:17:13Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [28c02df9312d](<https://github.com/photoprism/photoprism/commit/28c02df9312d81e8b8bf349727ab4131740bf2ec>).
**Product lineage:** photoprism/photoprism.

## Maturity and availability caveats

- Manifest release 261029-963b58c50 (2026-10-29); README pinned to develop 28c02df9312d81e8b8bf349727ab4131740bf2ec.
- Feature manuals are official live docs inspected 2026-11-09 and may describe later develop behavior. Historical TensorFlow/FaceNet defaults differ from current ONNX YuNet/SFace models; old libraries retain FaceNet until migrated.
- Community source is AGPL; standard images bundle paid extensions under Plus terms, while ce image is AGPL. Paid features below are separated from core.
- PostgreSQL is explicitly experimental. Official MySQL 8 support is discontinued; SQLite is documented as less suitable for high-concurrency/large libraries.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Local automatic content labels**<br>`ai.auto_tags` | C | Default ONNX classification generates labels/categories; model can be replaced or set to none without removing existing labels. | [R02-S9](<#r02-s9>), [R02-S30](<#r02-s30>) |
| **Optional generative captions**<br>`ai.captioning` | O | Configure Ollama or OpenAI for natural-language captions and labels; self-hosted Ollama recommends GPU, OpenAI needs API key/network. Not an established native semantic-search engine. | [R02-S9](<#r02-s9>) |
| **Background face grouping**<br>`ai.face_clustering` | C | Groups similar faces, updates clusters after new data/corrections and can auto-name a consistent cluster when enough recognized members agree; New Faces shows clusters, not every unknown face. | [R02-S8](<#r02-s8>) |
| **Reject/reassign/remove detections**<br>`ai.face_corrections` | C | Bad matches remove or replace identity and update cluster thresholds in background; false positives can be removed with undo only before reload. | [R02-S8](<#r02-s8>) |
| **Automatic face regions**<br>`ai.face_detection` | C | Current built-in YuNet detects faces; only primary stack image is scanned, and small/rotated/low-contrast faces may be missed. | [R02-S8](<#r02-s8>), [R02-S9](<#r02-s9>) |
| **Manual identity labels and covers**<br>`ai.face_naming` | C | Name in People, photo editor or info sidebar, rename person globally and select a representative face cover. | [R02-S8](<#r02-s8>) |
| **Identity matching by embeddings**<br>`ai.face_recognition` | C | Current SFace embeddings compare faces; legacy libraries keep FaceNet until migration. Recognition starts after full library scan and can be CPU-intensive. | [R02-S8](<#r02-s8>), [R02-S9](<#r02-s9>) |
| **Built-in offline inference**<br>`ai.local_inference` | C | ONNX label/NSFW/face models run locally without model-service setup; maps and optional hosted AI are separate network dependencies. | [R02-S9](<#r02-s9>), [R02-S26](<#r02-s26>) |
| **Mark missed faces manually**<br>`ai.manual_face_regions` | C | Info Sidebar permits manual region marking missed by detection; 360-degree content explicitly does not support manual marking yet. | [R02-S8](<#r02-s8>), [R02-S24](<#r02-s24>) |
| **Per-model execution policy**<br>`ai.model_scheduling` | O | vision.yml supports auto/manual/on-index/newly-indexed/on-demand/on-schedule/always/never modes; on-index limited to built-in local models to avoid blocking ingestion. | [R02-S9](<#r02-s9>) |
| **Optional private-content classification**<br>`ai.nsfw_detection` | O | NSFW detector can mark potentially objectionable images private; docs call it only partly reliable and older indexed images need rescan. | [R02-S4](<#r02-s4>), [R02-S9](<#r02-s9>) |
| **Explicit hosted model integration**<br>`ai.remote_inference` | O | OpenAI/Ollama Cloud send images to configured service endpoints with API keys; configurable prompts/models/thresholds and service credentials, no requests to these hosts without key. | [R02-S9](<#r02-s9>) |
| **Region/location collections**<br>`albums.locations` | C | Regions group images by location; time/place Moments supplement map navigation. | [R02-S21](<#r02-s21>), [R02-S23](<#r02-s23>) |
| **Curated virtual albums**<br>`albums.manual` | C | Create/edit albums, add selection to multiple albums, remove membership and choose cover; album deletion differs from file deletion. | [R02-S20](<#r02-s20>) |
| **People collections and downloads**<br>`albums.people` | C | View/download all a person's photos and add that selection to manual albums. | [R02-S8](<#r02-s8>) |
| **Automatically refreshed Moments**<br>`albums.smart` | C | Moments are continuously updated time/place or content-label collections such as country/year or pets; no arbitrary user-defined smart-query builder is claimed. | [R02-S21](<#r02-s21>) |
| **Light/dark themes**<br>`browse.dark_theme` | C | Result-view manual explicitly offers multiple light/dark themes; paid premium theme availability is not conflated with baseline theme switching. | [R02-S29](<#r02-s29>) |
| **Fullscreen viewer and information sidebar**<br>`browse.fullscreen` | C | Fullscreen viewing supports caption/sidebar toggles, editing and direct export/download. | [R02-S13](<#r02-s13>), [R02-S29](<#r02-s29>), [R02-S31](<#r02-s31>) |
| **Cards, mosaic and list browsing**<br>`browse.grid` | C | Cards show title/time/location, mosaic emphasizes imagery, list shows metadata; selectable light/dark themes. | [R02-S29](<#r02-s29>) |
| **Viewer/library shortcuts**<br>`browse.keyboard` | C | Shortcuts include fullscreen, slideshow, info/caption/mute/favorite, edit, archive/restore and download/export. | [R02-S13](<#r02-s13>), [R02-S27](<#r02-s27>), [R02-S29](<#r02-s29>), [R02-S31](<#r02-s31>) |
| **Interactive 360 photos/videos**<br>`browse.panorama` | C | Equirectangular content opens sphere viewer with pan/zoom/playback. Metadata identifies still projections; panorama flag plus roughly 2:1 frame identifies video; other projections stay flat. | [R02-S24](<#r02-s24>) |
| **Photo/video slideshow**<br>`browse.slideshow` | C | Viewer starts/pauses slideshows; Live Photos play when viewed in slideshow or hovered. | [R02-S1](<#r02-s1>), [R02-S29](<#r02-s29>) |
| **Calendar by capture time**<br>`browse.timeline` | C | Calendar organizes media by time taken, complemented by regions, people, labels, folders and favorites navigation. | [R02-S23](<#r02-s23>) |
| **Browser-aware video playback**<br>`browse.video_playback` | C | FFmpeg is required for video indexing stills; ExifTool supplies duration/resolution/codec. Supported browser codecs stream directly under documented bitrate rules. | [R02-S16](<#r02-s16>) |
| **Heuristic review queue**<br>`culling.quality_review` | C | Review score uses known date/GPS, resolution, non-screenshot classification and favorite/edit/approval; low scores are withheld until approved unless disabled. Not blur/aesthetic scoring; manual says 1–5 while filter reference permits 1–7. | [R02-S7](<#r02-s7>), [R02-S22](<#r02-s22>) |
| **Multi-architecture Docker images**<br>`deployment.docker` | C | Stable and preview images include converters/dependencies; CE and standard extension-bundled images have distinct licensing terms. | [R02-S1](<#r02-s1>), [R02-S26](<#r02-s26>) |
| **Native Linux server packages**<br>`deployment.linux` | C | Official tar packages can run the PhotoPrism server directly on compatible Linux distributions without Docker. They require manual configuration, updates and installation of system dependencies; this is a native server distribution with a browser interface, not a Linux desktop GUI package. | [R02-S1](<#r02-s1>), [R02-S2](<#r02-s2>), [R02-S26](<#r02-s26>) |
| **Translated interface and language selection**<br>`deployment.localization` | C | The October 2026 release explicitly discusses missing user-interface translations, fixes the sign-in language picker and invites native-speaker translation improvements. Account roles can retain a personal language preference; this is UI localization, not multilingual image search. | [R02-S2](<#r02-s2>), [R02-S17](<#r02-s17>) |
| **Paid managed hosting option**<br>`deployment.managed_cloud` | $ | Official documentation offers fully managed hosting through selected partners, and the personal-edition comparison lists PikaPods as a paid managed deployment. Provider plans and feature availability differ from a self-hosted installation. | [R02-S19](<#r02-s19>), [R02-S26](<#r02-s26>) |
| **Installable responsive PWA**<br>`deployment.pwa` | C | Browser app can be installed on phone/tablet/desktop home screen; this does not establish a native mobile background-backup service. | [R02-S1](<#r02-s1>) |
| **Self-hosted browser photo library**<br>`deployment.selfhosted` | C | Runs server under owner control with web UI; Docker supports AMD64/ARM64 on multiple host OSes, not native desktop installers. | [R02-S1](<#r02-s1>) |
| **Browser-based photo and video interface**<br>`deployment.web` | C | PhotoPrism provides its library browsing, metadata editing, organization and sharing interface through a web browser. PWA installation is optional and is not a native Windows/macOS or mobile application distribution. | [R02-S1](<#r02-s1>), [R02-S23](<#r02-s23>), [R02-S29](<#r02-s29>) |
| **SHA-1 and size duplicate detection**<br>`duplicates.exact_hash` | C | Index detects/skips matching SHA-1+size files so they appear once in results/albums; no byte-confirmation claim is documented. | [R02-S6](<#r02-s6>) |
| **Dedicated duplicate browse/delete UI**<br>`duplicates.visual_review` | R | Manual explicitly says browsing and deleting duplicates in web UI is future work; automatic suppression is already present. | [R02-S6](<#r02-s6>) |
| **Resolution/format export dialog**<br>`editing.export_renditions` | C | Admins/Users export originals, full-size previews, resized JPEGs or playable video renditions with per-download retry; Viewers/Guests/Visitors may download but not use Export. | [R02-S2](<#r02-s2>), [R02-S31](<#r02-s31>) |
| **Background Insta360 dewarping**<br>`editing.fisheye_dewarp` | C | INSV/INSP/fisheye DNG become equirectangular derivatives using known camera FOV or configured fallback; dual-lens video/proxy files stack and originals stay unchanged. | [R02-S11](<#r02-s11>), [R02-S24](<#r02-s24>) |
| **Optional hardware video transcoding**<br>`editing.hardware_encoding` | O | Video guide explicitly supports configured hardware transcoding; exact device/driver matrix was not inspected. | [R02-S16](<#r02-s16>) |
| **JPG/PNG orientation edit**<br>`editing.rotate_flip` | C | Choose correct orientation in Files tab; writes original metadata and is unavailable in read-only mode. | [R02-S32](<#r02-s32>) |
| **On-demand or precomputed AVC derivatives**<br>`editing.video_transcode` | C | Converts unsupported codecs to MPEG-4 AVC on first play or convert CLI; first-play latency/storage can be large. Existing AVC is not re-encoded even above bitrate limit. | [R02-S16](<#r02-s16>) |
| **Animated GIF playback**<br>`formats.animated` | C | GIF animation plays natively; ExifTool should remain enabled to extract duration/resolution. | [R02-S26](<#r02-s26>) |
| **AVIF image support**<br>`formats.avif` | C | Format table includes AVIF/sequences; preview conversion is distinct from browser-native display and converter resolution constraints. | [R02-S25](<#r02-s25>), [R02-S35](<#r02-s35>) |
| **HEIC/HEIF ingestion**<br>`formats.heic` | C | Supported with converted browser previews; heif-convert may not honor JPEG resolution limit. | [R02-S25](<#r02-s25>), [R02-S26](<#r02-s26>), [R02-S35](<#r02-s35>) |
| **JPEG XL conversion/previews**<br>`formats.jpegxl` | C | JPEG XL generates JPEG/PNG preview sidecars for thumbnail/recognition where browsers cannot render original. | [R02-S26](<#r02-s26>), [R02-S35](<#r02-s35>) |
| **Apple Live Photos**<br>`formats.live_photos` | C | Still/video companions stack and play on hover/slideshow; live search filters and dedicated navigation. | [R02-S1](<#r02-s1>), [R02-S11](<#r02-s11>), [R02-S16](<#r02-s16>) |
| **Motion Photo search/type support**<br>`formats.motion_photos` | C | Live filter explicitly includes Motion and Live Photos; detailed phone-specific extraction matrix not established. | [R02-S7](<#r02-s7>), [R02-S19](<#r02-s19>) |
| **RAW conversion with multiple engines**<br>`formats.raw` | C | Docker includes Darktable/RawTherapee; generated JPEG/PNG previews serve browser/ML use, outside originals by default. Camera support depends on converters. | [R02-S25](<#r02-s25>), [R02-S26](<#r02-s26>), [R02-S35](<#r02-s35>) |
| **Linked RAW/JPEG stacks**<br>`formats.raw_jpeg_pairs` | C | Same-folder basename companions always stack, including RAW/JPEG and hybrid image/video; this mandatory rule cannot be disabled. | [R02-S11](<#r02-s11>) |
| **Associated metadata companions**<br>`formats.sidecar_pairs` | C | XMP/JSON and other same-origin sidecars remain associated with media stack; permanent deletion removes related sidecars as well. | [R02-S11](<#r02-s11>), [R02-S14](<#r02-s14>) |
| **Vector graphics support**<br>`formats.svg` | $ | Plus edition includes vector graphics support, with SVG/AI/EPS/PS listed in format reference; not attributed to free core merely because format table lists them. | [R02-S19](<#r02-s19>), [R02-S35](<#r02-s35>) |
| **Interactive location clusters**<br>`geo.clustering` | C | Click grouped map markers for overlay and open associated photos in search; map can be restricted with most normal search filters. | [R02-S10](<#r02-s10>) |
| **Interactive 3D Earth view**<br>`geo.globe_view` | C | Places can switch to a globe that rotates, zooms and tilts; the guide says it works with all map styles and can combine with terrain mode. Paid satellite/terrain map services remain a separate capability. | [R02-S10](<#r02-s10>), [R02-S2](<#r02-s2>) |
| **Standard world photo map**<br>`geo.map` | C | All users receive hosted high-resolution OSM-based vector map; Places plots GPS media, supports search and requires WebGL 2. | [R02-S2](<#r02-s2>), [R02-S10](<#r02-s10>), [R02-S26](<#r02-s26>) |
| **External reverse geocoding**<br>`geo.online_geocoding` | C | PhotoPrism location service resolves coordinates to places; disabling Places retains indexed GPS but disables lookups/map UI. Community geocoding is rate-limited. | [R02-S19](<#r02-s19>), [R02-S25](<#r02-s25>), [R02-S26](<#r02-s26>) |
| **Satellite/terrain and enhanced location service**<br>`geo.premium_maps` | $ | Essentials/Plus provide additional MapTiler satellite/outdoor/3D styles and enhanced geocoding; standard hosted vector map remains free. Globe viewer works across styles. | [R02-S10](<#r02-s10>), [R02-S19](<#r02-s19>), [R02-S26](<#r02-s26>) |
| **Administration/maintenance CLI**<br>`integration.cli` | C | CLI provides index/import/convert/cleanup/thumb regeneration, backup, account management and database transfer; reset is destructive to index and requires backup. | [R02-S2](<#r02-s2>), [R02-S4](<#r02-s4>), [R02-S15](<#r02-s15>), [R02-S26](<#r02-s26>), [R02-S33](<#r02-s33>) |
| **Permission-aware MCP library tools**<br>`integration.mcp` | C | October release adds search/browse and metadata/format/command lookups, enabled for eligible roles with per-account/global disable options; external assistants can access authorized library information. | [R02-S2](<#r02-s2>), [R02-S25](<#r02-s25>), [R02-S33](<#r02-s33>) |
| **OAuth app authorization**<br>`integration.oauth_apps` | C | Release adds authorization-code app/remote-MCP connections; PHOTOPRISM_OAUTH_APPS=none can block external app authorization. | [R02-S2](<#r02-s2>) |
| **Built-in WebDAV and external sync**<br>`integration.webdav` | C | Mount originals/import to open/edit/delete remotely and sync external WebDAV servers; auth required, disabled in public mode, HTTPS required outside trusted local network. | [R02-S18](<#r02-s18>) |
| **Canonical import names/date folders**<br>`library.auto_date_folders` | C | Imports assign unique filenames and year/month directories while preserving original name as indexed property; advanced destination patterns can be configured but do not rename existing imports. | [R02-S3](<#r02-s3>), [R02-S26](<#r02-s26>) |
| **Skip duplicate imports**<br>`library.deduplicate_import` | C | Duplicates are skipped; Move import also deletes duplicate sources as though successfully moved, so it is a destructive source-cleanup choice. | [R02-S3](<#r02-s3>), [R02-S6](<#r02-s6>) |
| **Index originals in place**<br>`library.existing_folders` | C | Indexing leaves existing file/folder names unchanged, reads metadata and writes derived data outside originals by default. | [R02-S3](<#r02-s3>), [R02-S26](<#r02-s26>) |
| **Originals and configured stack downloads**<br>`library.export_originals` | C | Download selected photos, individual Files-tab items or whole albums/moments/person collections; configure which stack files are included. | [R02-S8](<#r02-s8>), [R02-S21](<#r02-s21>), [R02-S31](<#r02-s31>) |
| **Preserved folder hierarchy**<br>`library.folder_structure` | C | Folders and hierarchical Originals views reflect source organization; next index updates paths after media is moved within originals. | [R02-S3](<#r02-s3>), [R02-S23](<#r02-s23>) |
| **Scoped ignore rules**<br>`library.exclude_folders` | C | Automatic hidden-prefix exclusions plus directory-scoped .ppignore wildcard rules; rules do not retroactively remove already indexed items/stacks. | [R02-S4](<#r02-s4>) |
| **Managed copy or move import**<br>`library.import_copy` | C | Copies by default or moves from import to originals; unsupported files remain in import. Web uploads follow import semantics rather than direct originals upload. | [R02-S3](<#r02-s3>) |
| **Incremental and full rescan**<br>`library.incremental_scan` | C | Index all or selected subfolder; Complete Rescan includes unchanged files and preserves manually entered labels/people/titles/captions. | [R02-S4](<#r02-s4>) |
| **Companion mobile backup**<br>`library.mobile_backup` | P | Compatible apps such as PhotoSync can back up iOS/Android media in background via WebDAV; companion licensing/OS behavior is external to PhotoPrism. | [R02-S1](<#r02-s1>), [R02-S18](<#r02-s18>) |
| **Multiple mounted source folders**<br>`library.multiple_roots` | C | Host folders/drives can be mounted as subfolders below one originals tree; this is one catalogue over multiple mounts, not isolated per-user libraries. | [R02-S26](<#r02-s26>) |
| **Configurable related-image grouping**<br>`library.related_file_stacks` | C | Optional sequential-name, same-second/position and Unique Image/XMP Instance ID grouping; choose primary preview or unstack nonprimary image. Changing rules does not auto-unstack old groups. | [R02-S11](<#r02-s11>) |
| **Schedules and delayed WebDAV indexing**<br>`library.scheduled_indexing` | C | Optional scheduled rescans and default five-minute safety delay after WebDAV changes; concurrent scans and slow transfers can produce load or incomplete sets. | [R02-S4](<#r02-s4>), [R02-S18](<#r02-s18>) |
| **Google Photos metadata migration**<br>`library.takeout_import` | C | Reads Google Photos JSON sidecars and Apple XMP during indexing; this establishes metadata ingestion, not authenticated cloud sync or complete Takeout repair. | [R02-S5](<#r02-s5>), [R02-S26](<#r02-s26>) |
| **Library debug logs**<br>`maintenance.diagnostics` | C | Debug mode exposes logs under Library &gt; Logs after restart; advanced configuration changes require restart. | [R02-S25](<#r02-s25>) |
| **Remove orphan index/cache entries**<br>`maintenance.selective_reset` | C | Cleanup deletes unused thumbnails/orphan index entries when requested with indexing/CLI, not on schedule, and skips empty originals; thumbnail regeneration and full index reset are distinct operations. | [R02-S4](<#r02-s4>), [R02-S26](<#r02-s26>) |
| **Batch metadata/labels/albums**<br>`metadata.batch_edit` | C | When enabled, edits up to 999 selected pictures or a subset. Mixed values indicate replacement scope; partially assigned chips can add to all or remove from all. | [R02-S28](<#r02-s28>) |
| **Edit catalogue coordinates visually**<br>`metadata.catalogue_geotag` | C | Paste decimal coordinate pair or use built-in map/place search in Details. This is catalogue geotagging, not a claim that GPS is written into original EXIF. | [R02-S13](<#r02-s13>), [R02-S5](<#r02-s5>) |
| **Catalogue descriptive metadata**<br>`metadata.comments` | C | Edit title, caption, copyright, camera/lens and private notes; title/caption/keywords searchable, Notes ignored. Manual changes survive rescans. | [R02-S13](<#r02-s13>) |
| **Edit catalogue date/time**<br>`metadata.date_fix` | C | Details editor changes dates while preserving user overrides through indexing; release fixes timezone adjustment behavior. General embedded timestamp writing is not provided. | [R02-S2](<#r02-s2>), [R02-S13](<#r02-s13>), [R02-S5](<#r02-s5>) |
| **General metadata writeback**<br>`metadata.embedded_write` | N | Except image orientation, PhotoPrism explicitly does not write changed metadata back into originals to avoid conflicts/data loss. | [R02-S5](<#r02-s5>), [R02-S32](<#r02-s32>) |
| **Merged EXIF metadata**<br>`metadata.exif_read` | C | Built-in EXIF parser plus optional ExifTool normalizes and merges camera/time/location data; changed files are reread when mtime changes. | [R02-S5](<#r02-s5>) |
| **Media, person and label favorites**<br>`metadata.favorites` | C | Like media for Favorites view and quality review; starring people/labels sorts them first. | [R02-S8](<#r02-s8>), [R02-S22](<#r02-s22>), [R02-S23](<#r02-s23>), [R02-S30](<#r02-s30>) |
| **IPTC extraction via ExifTool**<br>`metadata.iptc_read` | C | ExifTool extracts IPTC together with embedded EXIF/XMP into JSON sidecars; disabling it reduces metadata support. | [R02-S5](<#r02-s5>), [R02-S26](<#r02-s26>) |
| **Built-in broader label categories**<br>`metadata.label_categories` | C | Generated labels belong to searchable broader groups such as vehicle; category grouping is not user-editable hierarchy. | [R02-S30](<#r02-s30>) |
| **Portable YAML metadata backup**<br>`metadata.sidecar_write` | C | Indexer/editor creates human-readable YAML sidecars unless disabled and ExifTool JSON extracts; manual YAML edits are not synchronized back to overwrite existing index. | [R02-S5](<#r02-s5>), [R02-S26](<#r02-s26>) |
| **Editable labels and suppression**<br>`metadata.tags` | C | Add/rename/remove labels; renaming affects all assigned pictures. Removing generated label sets confidence zero for reactivation; globally deleting prevents reapplication until deliberately restored. | [R02-S30](<#r02-s30>) |
| **Import external face names/regions**<br>`metadata.face_region_import` | O | Enable Import Faces from XMP to reuse names/regions from Bridge, Lightroom, digiKam, ACDSee or Windows rather than reentering them. | [R02-S5](<#r02-s5>), [R02-S8](<#r02-s8>), [R02-S25](<#r02-s25>) |
| **XMP sidecar priority**<br>`metadata.xmp_read` | C | Standalone XMP fields take precedence, including documented GPS/altitude/subject multiword keywords; embedded XMP requires ExifTool. Support is selective, not all XMP schemas. | [R02-S5](<#r02-s5>), [R02-S26](<#r02-s26>) |
| **Background metadata/face/conversion work**<br>`performance.background_jobs` | C | Face clusters update after indexing/corrections, optional AI has scheduled metadata-worker modes, and fisheye originals convert asynchronously. | [R02-S8](<#r02-s8>), [R02-S9](<#r02-s9>), [R02-S24](<#r02-s24>) |
| **Bound still-image conversion time**<br>`performance.conversion_timeout` | C | Still/document/RAW conversion defaults to ten-minute timeout; -1 disables it. Video uses a separate timeout disabled by default. | [R02-S25](<#r02-s25>) |
| **Trade precomputed storage for on-demand CPU**<br>`performance.dynamic_previews` | C | Independent static/dynamic size limits and Dynamic Previews reduce disk use at cost of latency/CPU; smaller/lower-quality analysis thumbnails can impair recognition. | [R02-S25](<#r02-s25>), [R02-S26](<#r02-s26>) |
| **NVIDIA acceleration**<br>`performance.gpu_ml` | O | Built-in ONNX models can use NVIDIA GPU; Ollama model/GPU/thread options are configurable. Documented timings are project claims, not benchmarks performed here. | [R02-S9](<#r02-s9>) |
| **Persistent multisize libvips previews**<br>`performance.thumbnail_cache` | C | JPEG thumbnail matrix is hash-addressed outside originals, with Lanczos3 rendering and up to 16K previews; static minimum 720 px supports ML. | [R02-S25](<#r02-s25>) |
| **Hide identities without hiding pictures**<br>`privacy.private_people` | C | Private/hidden people withhold names/regions from viewers/guests/visitors and remove names from generated titles after maintenance; pictures remain visible, so this is not redaction/encryption. | [R02-S8](<#r02-s8>), [R02-S17](<#r02-s17>) |
| **Archive/restore before permanent deletion**<br>`safety.app_recovery` | C | Archive hides without deleting, and restore returns media; album membership is removed on archive and not automatically restored. This is reversible catalogue archive, not OS trash or retained deleted bytes. | [R02-S27](<#r02-s27>) |
| **Scheduled SQL and metadata backups**<br>`safety.catalogue_backup` | C | Default daily database dumps retain up to three; album/YAML backup switches and manual commands available. Full recovery also needs originals and preferably storage/config, copied separately. | [R02-S15](<#r02-s15>), [R02-S25](<#r02-s25>) |
| **Archive-first permanent delete**<br>`safety.confirmation` | C | Delete must be enabled; archived files can be selected or all removed with confirmation. Originals and sidecars are removed permanently, cached derivatives on later cleanup. | [R02-S14](<#r02-s14>) |
| **Optional low-disk operation guard**<br>`safety.free_space_guard` | O | Can pause index/import/upload below configured free-space percentage with 100 MB floor; disabled by default because network/FUSE/container probes may be unreliable. | [R02-S4](<#r02-s4>) |
| **Automatic tagged-person YAML backup**<br>`safety.people_yaml_backup` | R | People manual lists automatic YAML backup of tagged people as upcoming; general metadata sidecars must not be assumed to fully back up face identities. | [R02-S8](<#r02-s8>) |
| **Explicit read-only source mode**<br>`safety.read_only_originals` | C | Disables original-writing features including import/upload/delete/WebDAV; optional Docker :ro mounts enforce OS-level protection. Derivative conversion remains possible outside originals. | [R02-S25](<#r02-s25>), [R02-S26](<#r02-s26>) |
| **Combined structured filters**<br>`search.boolean` | C | Space combines filters with AND; supported fields permit &amp; or \|, label groups permit leading !, and names/captions accept escaped operators/wildcards. Not universal arbitrary boolean syntax. | [R02-S7](<#r02-s7>) |
| **Color and chroma queries**<br>`search.colors` | C | Search standard dominant colors, chroma and monochrome flag; file-level results distinguish color/monochrome variants in stacks. | [R02-S7](<#r02-s7>) |
| **Capture and catalogue timestamps**<br>`search.date_range` | C | Year/month/day and taken/before/after plus added/edited/updated timestamps can be combined. | [R02-S7](<#r02-s7>) |
| **Megapixel and orientation filters**<br>`search.dimensions` | C | Resolution ranges plus portrait/landscape/square/panorama conditions are documented. | [R02-S7](<#r02-s7>) |
| **Media-type and stack filters**<br>`search.file_type` | C | Filter image/RAW/live/video/animated/audio/vector/document and stacked/unstacked/primary/unsorted states; filter presence alone does not establish each format's full playback semantics. | [R02-S7](<#r02-s7>) |
| **Current/original filename and path queries**<br>`search.filename_path` | C | Separate name, filename, original and path filters support wildcards. Searches operate on files, so narrowly matching extensions can exclude a stack's companion video. | [R02-S7](<#r02-s7>) |
| **Geographic filters**<br>`search.location` | C | Country/state/city/category, coordinates with distance, bounding boxes, altitude, Open Location Code, S2 cell and nearby-photo UID filters. | [R02-S7](<#r02-s7>) |
| **Camera/exposure/codec metadata filters**<br>`search.metadata` | C | Filter camera, lens, aperture, focal length, ISO, codec, captions/titles, hashes and source IDs, along with flags for private/archive/review/errors. | [R02-S7](<#r02-s7>) |
| **Person and face-count search**<br>`search.people` | C | Exact person or partial people names with conjunction/disjunction, face IDs/new faces and minimum face counts; can combine with date/place filters. | [R02-S7](<#r02-s7>), [R02-S8](<#r02-s8>) |
| **Keywords and category-aware labels**<br>`search.tags` | C | Search manual/generated labels, category expansion and keywords with supported boolean combinations. | [R02-S7](<#r02-s7>), [R02-S30](<#r02-s30>) |
| **Web account/session administration**<br>`sharing.account_admin_ui` | $ | Plus adds UI for accounts/sessions; account deletion disables/signs out but retains account record and uploaded pictures. CLI remains in all editions. | [R02-S33](<#r02-s33>) |
| **Multiple revocable expiring links**<br>`sharing.expiring_links` | C | Each collection can have different secret/expiry links; links can be deleted independently. | [R02-S12](<#r02-s12>) |
| **Multiple accounts on shared library**<br>`sharing.multiuser` | C | All editions have account CLI; Community includes Admin, Guest and Visitor, with full library or shared-only scope. Accounts are not separate selectable libraries. | [R02-S17](<#r02-s17>), [R02-S33](<#r02-s33>) |
| **Optional OpenID Connect sign-in**<br>`integration.oidc` | O | The edition comparison lists OpenID Connect SSO for self-hosted Community, Essentials and Plus. WebDAV documentation explains that OIDC-authenticated accounts use app passwords instead of their account password for WebDAV; provider-specific configuration was not inspected. | [R02-S19](<#r02-s19>), [R02-S18](<#r02-s18>) |
| **Password protection for album links**<br>`sharing.password_links` | R | Share manual explicitly describes optional password protection as planned, distinct from existing secret URLs and authenticated guest accounts. | [R02-S12](<#r02-s12>) |
| **User and Viewer roles**<br>`sharing.premium_roles` | $ | Essentials/Plus add editable-library User without global settings and read-only Viewer excluding private/archive and uploads/indexing. | [R02-S17](<#r02-s17>) |
| **Read-only secret album links**<br>`sharing.public_links` | C | Share manual albums, Moments, Months, Regions or Folders; visitors view/download only nonprivate media and cannot edit. Reusing secret can share multiple albums. | [R02-S12](<#r02-s12>) |
| **Community administrator/guest roles**<br>`sharing.roles` | C | Admins have unrestricted library/settings access; guests read shared content; anonymous visitors only shared resources. Superadmin flag prevents accidental role lockout and controls global flags. | [R02-S17](<#r02-s17>) |
| **Scoped device credentials**<br>`sharing.scoped_app_passwords` | C | App passwords support WebDAV-only scope; even Full Access app credentials cannot change account password or manage users. | [R02-S18](<#r02-s18>), [R02-S34](<#r02-s34>) |
| **Authenticator 2FA and recovery**<br>`privacy.two_factor_auth` | C | Account 2FA uses compatible authenticator, one-time recovery code disabling 2FA, and administrator reset path. | [R02-S34](<#r02-s34>) |
| **SQLite/MariaDB and experimental PostgreSQL**<br>`storage.database_choices` | C | SQLite and MariaDB supported; October release adds explicitly experimental PostgreSQL and database-transfer CLI. MySQL 8 support is discontinued. | [R02-S2](<#r02-s2>), [R02-S26](<#r02-s26>) |

## Limitations and evidence gaps

- **explicit:** Self-hosting is not fully offline: maps/reverse geocoding retrieve data from PhotoPrism/MapTiler; optional hosted AI transmits image inputs to configured services. ([R02-S9](<#r02-s9>), [R02-S26](<#r02-s26>))
- **explicit:** Paid User/Viewer roles, account/session UI, vector support and enhanced maps are not free core. Accounts share one catalogue rather than providing independent per-user libraries. ([R02-S17](<#r02-s17>), [R02-S19](<#r02-s19>), [R02-S33](<#r02-s33>))
- **explicit:** Move import deletes duplicate source files; archiving loses album memberships, permanent delete removes originals/sidecars, and rotation or basename-unstacking can modify original metadata/names. ([R02-S3](<#r02-s3>), [R02-S14](<#r02-s14>), [R02-S26](<#r02-s26>), [R02-S27](<#r02-s27>), [R02-S32](<#r02-s32>))
- **explicit:** Password-protected share links and dedicated duplicate cleanup UI remain planned. General original metadata writeback is unsupported except orientation. ([R02-S5](<#r02-s5>), [R02-S6](<#r02-s6>), [R02-S12](<#r02-s12>))
- **explicit:** Face matching is weaker for young children/age gaps and often misses nonupright faces; primary stack file only is analyzed. Private people hides names/regions, not pictures, and manual face marking is unsupported on 360 content. ([R02-S8](<#r02-s8>), [R02-S24](<#r02-s24>))
- **explicit:** FFmpeg is needed for video indexing and ExifTool for full metadata. AVC originals are not recompressed to meet bitrate limits; transcoded derivatives may exceed original storage. RAW/XMP changes do not regenerate existing JPEGs automatically. ([R02-S16](<#r02-s16>), [R02-S26](<#r02-s26>))
- **explicit:** Ignore rules do not retroactively remove entries, unsupported filename characters are skipped, and stack-setting changes do not automatically unstack existing items. ([R02-S2](<#r02-s2>), [R02-S4](<#r02-s4>), [R02-S11](<#r02-s11>))
- **explicit:** SQLite high-concurrency/large-library limitations and CPU/storage tradeoffs are documented claims, not measured here; low-disk runtime protection is disabled by default. ([R02-S4](<#r02-s4>), [R02-S25](<#r02-s25>), [R02-S26](<#r02-s26>))
- **coverage-gap:** Review guide says score 1–5 while filter reference permits 1–7; newer metadata page lists XMP features beyond older FAQ's abbreviated list. Precise version/model behavior may vary across live docs. ([R02-S5](<#r02-s5>), [R02-S7](<#r02-s7>), [R02-S22](<#r02-s22>), [R02-S26](<#r02-s26>))
- **coverage-gap:** Natural-language semantic search, OCR search, perceptual duplicate review, E2EE, offline basemap/geocoding, durable file-operation journal and separate per-user libraries were not established by inspected evidence. ([R02-S6](<#r02-s6>), [R02-S7](<#r02-s7>), [R02-S9](<#r02-s9>), [R02-S17](<#r02-s17>), [R02-S26](<#r02-s26>))
- **Coverage gap:** Live docs may lead frozen release; no operational/benchmark verification performed.
- **Coverage gap:** Only explicit text/labelled edition differences used; icon-only comparison cells not interpreted.
- **Coverage gap:** External mobile apps, hardware encoder matrix and enterprise Pro feature set not individually audited.
- **Coverage gap:** Generic diff perceptual-hash filter does not establish user-facing similar-image search or duplicate cleanup.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R02-S1

[PhotoPrism README](<https://github.com/photoprism/photoprism/blob/28c02df9312d81e8b8bf349727ab4131740bf2ec/README.md>)
- Kind/ref: readme; 28c02df9312d81e8b8bf349727ab4131740bf2ec
- Sections inspected: Complete feature overview, deployment, membership and roadmap overview
- Establishes: Core scope, PWA, formats, metadata, mobile companions and edition boundaries.

### R02-S2

[October 29, 2026 release](<https://github.com/photoprism/photoprism/releases/tag/261029-963b58c50>)
- Kind/ref: release; 261029-963b58c50
- Sections inspected: Complete upgrade notes, changes, export and maps sections
- Establishes: OAuth/MCP, export dialog, standard maps, experimental PostgreSQL and filename restrictions.

### R02-S3

[Index versus import](<https://docs.photoprism.app/user-guide/library/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete indexing/import workflows and comparison
- Establishes: Preserved roots, copied/moved canonical imports, dedup and source keyword extraction.

### R02-S4

[Indexing originals](<https://docs.photoprism.app/user-guide/library/originals/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete rescan, cleanup, schedules, disk thresholds and exclusions
- Establishes: Incremental/full indexing, delayed WebDAV scans, safe-space limits and unsupported names.

### R02-S5

[Metadata support](<https://docs.photoprism.app/user-guide/library/metadata/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete source merging, XMP locations/faces/subject, cloud migration, enrichment and export
- Establishes: Metadata precedence, sidecars, external edits and embedded-write boundary.

### R02-S6

[Duplicate detection](<https://docs.photoprism.app/user-guide/library/duplicates/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete duplicate/import/related-file explanation
- Establishes: SHA-1 plus size, skip semantics and planned duplicate cleanup UI.

### R02-S7

[Complete search-filter reference](<https://docs.photoprism.app/user-guide/search/filters/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete boolean/wildcard syntax, filter table and file-level search caveat
- Establishes: Rich technical, people, location, color, status and time filters; not general natural-language search.

### R02-S8

[Face recognition and people](<https://docs.photoprism.app/user-guide/organize/people/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete detection/clustering, naming, private people, corrections and limitations
- Establishes: Face lifecycle, manual marking, account-sensitive names and backup roadmap.

### R02-S9

[AI models and vision configuration](<https://docs.photoprism.app/user-guide/ai/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete engines, performance claims, models, run modes, options and service configuration
- Establishes: Local ONNX, optional Ollama/OpenAI captions/labels, model migration, scheduling and GPU options.

### R02-S10

[Places map](<https://docs.photoprism.app/user-guide/organize/places/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete map, clusters, search, terrain and 3D Earth
- Establishes: Map interactions and WebGL requirement; edition gate established separately.

### R02-S11

[Related-file stacks](<https://docs.photoprism.app/user-guide/organize/stacks/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete matching criteria, primary selection, unstack and related-file deletion
- Establishes: Mandatory basename grouping, optional time/ID/sequential rules and Insta360 lens pairing.

### R02-S12

[Album share links](<https://docs.photoprism.app/user-guide/share/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete secret-link creation, expiry, deletion and password roadmap
- Establishes: Read-only public links, exclusion of private content and multiple-album secrets.

### R02-S13

[Picture details editor](<https://docs.photoprism.app/user-guide/organize/edit/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete details, location selector, labels, people and files tabs
- Establishes: Catalogue edits preserve manual values; private notes are not searched; location picker is now built in.

### R02-S14

[Permanent file removal](<https://docs.photoprism.app/user-guide/organize/delete/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete enabled-feature, archive-first, confirm and removed-file semantics
- Establishes: Permanent original/sidecar deletion and later derivative cleanup.

### R02-S15

[Backups](<https://docs.photoprism.app/user-guide/backups/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete scheduled/manual dumps, required directories and migration notes
- Establishes: Daily database dumps/retention, separate original/config backup requirements.

### R02-S16

[Video and Live Photos](<https://docs.photoprism.app/user-guide/organize/video/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete browsing, live hover, transcoding and codec caveats
- Establishes: FFmpeg/ExifTool requirements, direct-play rules, pretranscode and AVC limitation.

### R02-S17

[Roles and permissions](<https://docs.photoprism.app/user-guide/users/roles/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete role descriptions and edition note
- Establishes: Community admin/guest/visitor, paid user/viewer and shared-library access semantics.

### R02-S18

[WebDAV integration](<https://docs.photoprism.app/user-guide/sync/webdav/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete mount, auto-index, credentials and HTTPS guidance
- Establishes: Remote original/import access, external sync, app passwords and public-mode restriction.

### R02-S19

[Personal edition comparison](<https://www.photoprism.app/kb/personal/>)
- Kind/ref: official-site; live-docs inspected 2026-11-09
- Sections inspected: Full compact HTML text of comparison and supporting page; only explicit labelled distinctions used
- Establishes: Community versus Essentials/Plus: account roles, admin UI, vectors and map services; inaccessible icon-only cells not inferred.

### R02-S20

[Albums](<https://docs.photoprism.app/user-guide/organize/albums/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete album creation/editing/membership/covers/deletion
- Establishes: Virtual manual collections and different backup retention for manual/automatic albums.

### R02-S21

[Moments](<https://docs.photoprism.app/user-guide/organize/moments/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete auto-moment criteria, removal, downloads and album conversion
- Establishes: Dynamic time/location/content collections without altering originals.

### R02-S22

[Quality review](<https://docs.photoprism.app/user-guide/organize/review/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete score inputs and approval behavior
- Establishes: Heuristic score based on metadata/resolution/classification/user approval, not aesthetic/blur model.

### R02-S23

[Browsing sections](<https://docs.photoprism.app/user-guide/search/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete views and navigation
- Establishes: Calendar/regions/folders/private/favorites, special media sections and excluded states.

### R02-S24

[Panorama and sphere viewer](<https://docs.photoprism.app/user-guide/organize/panoramas/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete identification, controls, supported projections, fisheye conversion and quality limits
- Establishes: 360 photos/videos, Insta360 dewarping, WebGL and unsupported manual face marking.

### R02-S25

[Advanced settings](<https://docs.photoprism.app/user-guide/settings/advanced/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete options, backups, thumbnail matrix/quality and converters
- Establishes: Read-only mode, feature switches, static/dynamic previews and converter timeouts.

### R02-S26

[Technical and privacy FAQ](<https://docs.photoprism.app/getting-started/faq/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Formats/sidecars; external services/maps; installation/editions; DB/storage/performance; originals roots; rescans; naming; read-only and original modification; network mounts
- Establishes: Network caveats, converter limitations, storage tradeoffs and exact write exceptions; unrelated trailing troubleshooting not used.

### R02-S27

[Archive and restore](<https://docs.photoprism.app/user-guide/organize/archive/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete archive/restore semantics
- Establishes: Archive hides but does not delete media; album membership is not restored.

### R02-S28

[Batch editor](<https://docs.photoprism.app/user-guide/organize/batch-edit/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete selection/mixed-field and label/album controls
- Establishes: Up to 999 selected pictures, subset changes and partial-assignment handling.

### R02-S29

[Search views and shortcuts](<https://docs.photoprism.app/user-guide/search/views/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete cards/mosaic/list/fullscreen/slideshow and shortcuts
- Establishes: Browser viewing modes, themes and quick actions.

### R02-S30

[Labels and categories](<https://docs.photoprism.app/user-guide/organize/labels/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete generated/manual labels, category expansion, removal and deletion
- Establishes: Editable labels, fixed broader categories and suppression/reinstatement semantics.

### R02-S31

[Download and export](<https://docs.photoprism.app/user-guide/organize/download/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete download paths and size/format export permissions
- Establishes: Original/preview/resized/video renditions, retries and role restrictions.

### R02-S32

[Rotation](<https://docs.photoprism.app/user-guide/organize/rotate/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete rotation instructions and storage caveat
- Establishes: JPG/PNG orientation writes original metadata and is unavailable read-only.

### R02-S33

[User/session management](<https://docs.photoprism.app/user-guide/users/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete edition boundary, account operations and sessions
- Establishes: CLI all editions, paid UI, disabled-account retention and session invalidation.

### R02-S34

[Two-factor authentication](<https://docs.photoprism.app/user-guide/users/2fa/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete authenticator, recovery and app-password workflows
- Establishes: 2FA setup, one-time recovery and scoped app passwords.

### R02-S35

[Format and extension reference](<https://www.photoprism.app/kb/file-formats/>)
- Kind/ref: official-site; live-docs inspected 2026-11-09
- Sections inspected: Complete image/RAW/sidecar/document/vector/video table
- Establishes: Enumerated formats, with edition/runtime caveats established by other docs.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
