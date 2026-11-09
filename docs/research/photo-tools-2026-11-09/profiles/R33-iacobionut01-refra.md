# R33 — IacobIonut01/ReFra

[Repository](<https://github.com/IacobIonut01/ReFra>) · 3,006 stars at the frozen snapshot · gallery-mobile · Not archived

**Purpose:** Android gallery combining local/removable/cloud media, optional on-device semantic search and people grouping, encrypted vaults, advanced photo/video editing and provider-aware backup workflows.

**Deployment:** Android APKs via GitHub/F-Droid/Obtainium; Paid Google Play distribution supporting development, not a separately documented feature tier; Standard/Offline and NoML/WithML build variants; Optional self-hosted ReFra Handover inference companion

**Storage:** Browses Android-indexed device/removable media in place, with app databases for collections, extracted metadata, people corrections and search indexes. Cloud account listings, cached previews, downloaded originals and backed-up device originals are distinct states. Vault files are encrypted; private folders are ordinary files hidden with .nomedia. Current editor writes copies; legacy editor can overwrite with a retained edit backup.

**Privacy/network behavior:** Local AI can run entirely on-device after models are installed or bundled. Offline builds remove network permissions, cloud and interactive maps. Standard optional features can send query text to Immich, thumbnails/sampled frames to self-hosted Handover, or an image/decrypted vault copy to an external visual-search app. Vault backups contain decrypted media inside optionally encrypted archives; logs can contain paths/server addresses despite release shorthand about anonymization.

**License metadata:** Apache-2.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 5.2.2 (2026-10-04T16:54:56Z)
**Repository pushed at:** 2026-11-09T12:14:43Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [632030899803](<https://github.com/IacobIonut01/ReFra/commit/632030899803846d31073a672e56ee2581f59f62>).
**Product lineage:** IacobIonut01/ReFra.

## Maturity and availability caveats

- Frozen commit 632030899803846d31073a672e56ee2581f59f62; latest release 5.2.2 (2026-10-04).
- Pinned website manuals describe current implementation including newer editor/remote-inference/search-engine behavior; do not assume all current-branch capabilities shipped in 5.2.2. Explicit legacy editor pages are kept separate.
- README still says minimum Android 11; 5.2.2 release says Android 10/API29. Trash and some replace flows still explicitly require Android 11+.
- Current docs list CLIP and EmbeddingGemma 2; model accuracy/speed/language comparisons are project claims, not tested benchmarks.
- Google Play payment is a distribution/support choice; free builds are also documented.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Deterministic person grouping**<br>`ai.face_clustering` | O | Local scan groups faces into New/Named people; regroup can rebuild after new media or mistaken merges. 5.2 release identifies deterministic batch clustering. | [R33-S4](<#r33-s4>), [R33-S7](<#r33-s7>) |
| **Correct and suppress person groups**<br>`ai.face_corrections` | O | Confirm/reject possible duplicates, merge groups, remove individual faces/photos from a person, hide/unhide and delete a person while suppressing those faces from future grouping; photos themselves remain. | [R33-S2](<#r33-s2>), [R33-S7](<#r33-s7>) |
| **Detect local face regions**<br>`ai.face_detection` | O | Face model pack enables detected-face strips, face scanning and editor blur/mosaic actions; current Standard tier uses UltraFace plus ArcFace. | [R33-S7](<#r33-s7>), [R33-S8](<#r33-s8>) |
| **Name and personalize people**<br>`ai.face_naming` | O | Name people, store birthdays and choose face covers; local/cloud person sources can be selected independently. | [R33-S7](<#r33-s7>) |
| **Alternative face model quality tiers**<br>`ai.face_quality_tiers` | R | Fast and Accurate face-grouping tiers are explicitly Coming soon; Standard is the available tier. | [R33-S8](<#r33-s8>) |
| **Identity matching across photos**<br>`ai.face_recognition` | O | Recognition models match recurring faces into person groups; 5.2.2 rescans preserve names using face matching rather than recreating unnamed groups. | [R33-S2](<#r33-s2>), [R33-S7](<#r33-s7>), [R33-S8](<#r33-s8>) |
| **Install feature-specific local models**<br>`ai.local_inference` | O | Intelligence Hub manages separate search (~150–320 MB), face (~131 MB) and cutout (~44 MB) packs. Bundled builds can restore without downloads; scan-only-while-charging and skip-hidden settings are available, while locked albums are never scanned. | [R33-S6](<#r33-s6>), [R33-S8](<#r33-s8>) |
| **Optional self-hosted Handover engine**<br>`ai.remote_inference` | P | Companion server receives resized JPEGs/video sample frames, not originals, and returns embeddings; choose device/server/both index placement and remote ranking. Bearer/HMAC authentication, per-user indexes, chunked background jobs and retries are documented; HTTP warns of unencrypted traffic. | [R33-S11](<#r33-s11>) |
| **Interactive subject segmentation**<br>`ai.subject_cutout` | O | Model-backed long-press or editor Cutout/Remove background uses include/exclude points with undo/redo/refinement; copy/share/save transparent PNG while keeping original. | [R33-S8](<#r33-s8>), [R33-S45](<#r33-s45>) |
| **Display-only album merging**<br>`albums.folder_merge_views` | C | Merge same-name albums across volumes or fold subfolders/parent subfolders into one view, with unmerge; no file movement or renaming occurs. | [R33-S26](<#r33-s26>), [R33-S39](<#r33-s39>) |
| **City/country/trip browsing**<br>`albums.locations` | C | Places list groups by cities/countries with photo/place/country counts, per-location timelines and recent trips when available, including builds without interactive map. | [R33-S25](<#r33-s25>) |
| **Virtual collections across folders**<br>`albums.manual` | C | Collections reference chosen media/whole albums without extra copies; same item can belong to several collections, and deleting/removing membership does not delete media. | [R33-S27](<#r33-s27>) |
| **Cross-folder media-type albums**<br>`albums.media_type_collections` | C | Virtual Photos/Videos/GIF/RAW albums cover all folders and can be shown/hidden as a Library section. | [R33-S39](<#r33-s39>) |
| **Album pins, groups and sections**<br>`albums.presentation_groups` | C | Pin albums, choose covers, create collapsible named groups and override automatic Common/Apps/Other sections; deleting a group does not remove folders. | [R33-S39](<#r33-s39>) |
| **Custom semantic collections**<br>`albums.semantic_categories` | O | Define categories with text description, optional example photos and Broad/Balanced/Strict/Exact preference; preview matches, pin/set cover and optionally exclude videos. Categories classify locally but do not imply embedded tag writing. | [R33-S28](<#r33-s28>) |
| **Wide-screen side-by-side browsing**<br>`browse.adaptive_split_view` | C | Wide windows open viewer beside timeline with current grid item outlined; smaller windows use fullscreen paging. | [R33-S32](<#r33-s32>) |
| **Compare edited and original images**<br>`browse.compare` | C | Hold canvas to view original or drag split-view divider; geometry changes switch to whole-original comparison because alignment no longer matches. | [R33-S16](<#r33-s16>) |
| **Pinch-adjustable grid and mosaic**<br>`browse.grid` | C | Current grid supports one to nine columns and mosaic three to six, with separate timeline/album sizing and long-press drag selection or full date-group selection. | [R33-S32](<#r33-s32>) |
| **Panorama and photosphere viewer**<br>`browse.panorama` | C | Uses appropriate spherical/cylindrical projections, drag/pinch controls, and for full spheres gyroscope steering with compass indicator. No projection picker or VR mode is offered. | [R33-S5](<#r33-s5>), [R33-S37](<#r33-s37>) |
| **Configurable album slideshows**<br>`browse.slideshow` | C | 5.1 changelog explicitly adds configurable album slideshows; timing/effect specifics were not established in inspected sources. | [R33-S3](<#r33-s3>) |
| **Material theme customization**<br>`browse.theme_customization` | C | Wallpaper-derived or preset palettes have live Material 3 previews; release notes describe customizable Library sections and shortcut visibility. | [R33-S2](<#r33-s2>), [R33-S5](<#r33-s5>) |
| **Unified date-grouped timeline**<br>`browse.timeline` | C | Local and connected-cloud media share date sections, fast month navigation, story cards and selectable day/month/year headers; capture or modified time can order ascending/descending. | [R33-S32](<#r33-s32>) |
| **Custom video player and HDR**<br>`browse.video_playback` | C | Media3 player supports frame seeking; 5.2.2 adds Dolby Vision/HDR10/HLG playback with a setting and compatible display requirement, reporting unsupported DV profiles. Actual codec support remains device-dependent. | [R33-S2](<#r33-s2>), [R33-S5](<#r33-s5>), [R33-S24](<#r33-s24>) |
| **Full-resolution and tiled viewing**<br>`browse.zoom` | C | Pinch/pan viewing supports heavy formats; released HDR HEIC path uses native tiles/gain maps, while current format guide offers smoothing control for pixel art. | [R33-S3](<#r33-s3>), [R33-S24](<#r33-s24>) |
| **Free space only after backup verification**<br>`cleanup.backed_up_device_copies` | O | Scan verified backed-up originals, retain favorites and choose age threshold (default Never); daily/three-day/weekly auto cleanup can run, but without All Files Access requests review instead of silent deletion. | [R33-S22](<#r33-s22>) |
| **Android gallery distributions**<br>`deployment.android` | C | APK/F-Droid/Obtainium distributions; 5.2.2 release lists Android 10/API29+, while README still states 11. Features such as Trash retain higher version requirements. | [R33-S1](<#r33-s1>), [R33-S2](<#r33-s2>), [R33-S30](<#r33-s30>) |
| **Translated Android interface**<br>`deployment.localization` | C | Pinned Compose resources contain French and German translations for Timeline/Albums, Settings, share/select/restore actions, metadata labels and editing dialogs. Some inspected French entries remain English, so full translation completeness is not claimed; this is independent of multilingual AI models. | [R33-S47](<#r33-s47>), [R33-S48](<#r33-s48>) |
| **Paid Play Store channel**<br>`deployment.play_store` | $ | README says Play price supports the project and automatic Play updates; no separate paid functional tier is documented. | [R33-S1](<#r33-s1>) |
| **Photo tone, color and effects**<br>`editing.adjustments` | C | Current tool catalogue includes light/color/curves/white balance, looks/detail/vignette/lens blur/grain/tone/posterize/edges/borders, with histogram channels and clipping display. | [R33-S16](<#r33-s16>) |
| **Crop, straighten and perspective**<br>`editing.crop` | C | Current editor includes crop/straighten/perspective tools, with on-canvas grid and explicit Apply/Reset recipe steps. | [R33-S16](<#r33-s16>) |
| **Blur a person's faces in copies**<br>`editing.face_blur` | O | Blur everywhere creates new copies of photos containing the selected person; face models also enable local blur/mosaic editor tools. | [R33-S7](<#r33-s7>), [R33-S8](<#r33-s8>) |
| **Explicit copy export formats**<br>`editing.format_conversion` | C | Current editor exports JPEG/PNG/WebP and encoder-dependent HEIF/JXL; Original copy preference retains JPEG quality or PNG losslessness. Removed-background copies become PNG. Legacy editor has different format/overwrite behavior. | [R33-S23](<#r33-s23>), [R33-S44](<#r33-s44>) |
| **Layered photo compositing**<br>`editing.layers` | C | Up to sixteen JPEG/PNG image layers, locked base, reorder/duplicate/hide/lock, transforms, five blend modes, opacity, clipping and erase/paint masks; output flattens visible layers and missing source media can be relinked on recovery. | [R33-S33](<#r33-s33>) |
| **Photo markup tools**<br>`editing.annotations` | C | Current catalogue includes Markup; with face models, blur/mosaic face operations are available. Detailed brush shapes are not inferred. | [R33-S8](<#r33-s8>), [R33-S16](<#r33-s16>) |
| **Extract motion clips or selected frames**<br>`editing.motion_extract` | C | Save embedded motion as a separate video or use frame picker for stills without changing source. Editing its still creates a separate image copy. | [R33-S36](<#r33-s36>) |
| **RAW sensor development controls**<br>`editing.raw_development` | C | White-balance presets/custom temp/tint; exposure/tone; sharpening; Linear/VNG/PPG/AHD/DCB demosaic; denoise and half resolution; sRGB/AdobeRGB/Wide/ProPhoto output; clip/blend/rebuild highlights. TIFF 8/16 export only holds development, not additional crop/markup/look edits. | [R33-S18](<#r33-s18>) |
| **Per-clip video picture changes**<br>`editing.video_adjustments` | C | Transform/crop Fit/Fill/Crop, scale/rotation/position/horizontal flip/background plus per-clip light/color/curves and opacity. | [R33-S17](<#r33-s17>) |
| **Voice-over and multitrack audio**<br>`editing.video_audio_mixing` | C | Import audio, record local voice-over or extract clip sound; mix gain/pan/fades/mute/solo/master limiter, channel routing/mono downmix, sidechain ducking and three-band EQ/high-pass. | [R33-S34](<#r33-s34>) |
| **Export H.264/AAC MP4 copies**<br>`editing.video_transcode` | C | Current export summary specifies size, constant fps, H.264/automatic bitrate and stereo 48 kHz AAC when audio reaches mix, with progress/retry and untouched source. | [R33-S17](<#r33-s17>) |
| **Multitrack video editing**<br>`editing.video_trim_join` | C | Current MP4/QuickTime editor supports frame-precise in/out trims, split/delete/duplicate/reorder, ripple insertion, linked audio, snapping, multiple tracks and overlays. | [R33-S17](<#r33-s17>) |
| **Animated image viewing**<br>`formats.animated` | C | GIF/animated WebP/APNG full-resolution rendering is in 5.1 release; moving GIF thumbnails can be disabled. Editing/export does not guarantee preserving animation. | [R33-S3](<#r33-s3>), [R33-S24](<#r33-s24>) |
| **AVIF viewing**<br>`formats.avif` | C | AVIF is a supported viewer format, including 12-bit decoding fixes in 5.2.2. | [R33-S2](<#r33-s2>), [R33-S24](<#r33-s24>) |
| **HEIC/HEIF and HDR images**<br>`formats.heic` | C | HEIC/HEIF viewing includes supported HDR/gain-map paths; 5.2.2 adds bundled deep-12-bit decoding fixes. Display HDR remains device-dependent and editing may flatten it. | [R33-S2](<#r33-s2>), [R33-S3](<#r33-s3>), [R33-S24](<#r33-s24>) |
| **JPEG XL viewing and conditional export**<br>`formats.jpegxl` | C | JXL viewer support and persistent heavy-format thumbnails are documented; exporting JXL from current editor additionally depends on encoder availability. | [R33-S2](<#r33-s2>), [R33-S23](<#r33-s23>), [R33-S24](<#r33-s24>) |
| **Embedded Motion Photo playback**<br>`formats.motion_photos` | C | Detects embedded clips, exposes Motion toggle and frame strip; listed families include Google Motion Photos/Samsung Live Photos/Micro Videos. This is not a claim of Apple image+MOV pairing. | [R33-S5](<#r33-s5>), [R33-S36](<#r33-s36>) |
| **RAW previews and development**<br>`formats.raw` | C | Viewer previews camera RAW; current editor develops DNG/CR2/CR3/NEF/NRW/ARW/RAF/ORF/RW2/PEF/SRW. Viewer format support alone does not mean every editor accepts the file. | [R33-S18](<#r33-s18>), [R33-S24](<#r33-s24>) |
| **RAW+JPEG display stacks**<br>`formats.raw_jpeg_pairs` | C | Timeline groups related RAW/JPEG members into a stack cell with access to members; not duplicate deletion. | [R33-S5](<#r33-s5>), [R33-S32](<#r33-s32>) |
| **SVG and design-image previews**<br>`formats.svg` | C | Viewer opens SVG, flattened PSD and JP2/J2K; SVG is rendered as pixels and PSD layers are not editable merely because the file previews. | [R33-S24](<#r33-s24>) |
| **Map clusters linked to media grid**<br>`geo.clustering` | O | Nearby markers form numbered clusters, tapping zooms or opens a colocated-photo sheet; marker selection and grid scrolling stay linked. | [R33-S25](<#r33-s25>) |
| **Interactive media location map**<br>`geo.map` | O | MapLibre-based map reads existing media GPS after permission, not live tracking; display follows app/light/dark styles and can need a CARTO key. Offline build substitutes place list without tiles. | [R33-S5](<#r33-s5>), [R33-S25](<#r33-s25>) |
| **Accept external Android edit requests**<br>`integration.android_editor` | C | Current editor accepts JPEG/PNG/video edit intents and returns the saved copy to caller while also retaining it in ReFra output folders. | [R33-S16](<#r33-s16>), [R33-S23](<#r33-s23>) |
| **Image handoff to Lens-like apps**<br>`integration.external_visual_search` | P | Separate Visual search shares current image/video frame with chosen installed app, can convert unsupported formats and needs explicit vault-item allowance because temporary decrypted data is exposed. | [R33-S10](<#r33-s10>) |
| **LAN photo/video casting**<br>`integration.fcast` | O | FCast-compatible receiver required, discovered by mDNS or entered manually at default port 46899; remote pause/seek/speed controls depend on receiver codec support. No Chromecast protocol is involved. | [R33-S5](<#r33-s5>), [R33-S38](<#r33-s38>) |
| **Photo and grid home-screen widgets**<br>`integration.home_widgets` | C | Single photo or size-dependent 2x2/4x4/6x6 grids with original, black-white or icon/emoji presentation; tap opens exact photo, styles do not edit files. Widget image has no separate unlock gate. | [R33-S2](<#r33-s2>), [R33-S40](<#r33-s40>) |
| **WebDAV and DAV-based providers**<br>`integration.webdav` | O | WebDAV/Nextcloud/ownCloud accounts browse/upload alongside SMB/NFS; server-side people/search/archive/memories cannot be assumed on simple shares. | [R33-S19](<#r33-s19>), [R33-S31](<#r33-s31>) |
| **Burst and edited-copy grouping**<br>`library.burst_stacking` | C | Optional smart grouping collapses burst shots and edited copies into timeline stacks without implying an automatic best-shot/culling score. | [R33-S5](<#r33-s5>), [R33-S32](<#r33-s32>) |
| **Multi-account server media access**<br>`library.cloud_import` | O | Connect Immich, Nextcloud, ownCloud, WebDAV, SMB or NFS depending on build; local/cloud listings merge but capabilities vary. Google Photos is explicitly not supported. | [R33-S19](<#r33-s19>) |
| **Scheduled listing sync and optional deletion propagation**<br>`library.cloud_sync` | O | 15-minute to daily approximate Android schedules, Wi-Fi-only auto sync, unrestricted manual sync and cold-start sync; opt-in remote deletions remove only app-downloaded copies, not arbitrary local originals. | [R33-S2](<#r33-s2>), [R33-S20](<#r33-s20>) |
| **Reuse identical downloaded copies**<br>`library.deduplicate_import` | O | 5.2.2 links identical existing local files instead of re-downloading Immich assets and places downloads in account/album folders, not the server's internal storage tree. | [R33-S2](<#r33-s2>) |
| **Browse Android-indexed files in place**<br>`library.existing_folders` | C | Device media is browsed in its existing albums/folders; app virtual organization does not require copying originals into a managed library. | [R33-S26](<#r33-s26>), [R33-S32](<#r33-s32>), [R33-S39](<#r33-s39>) |
| **Per-account album backup**<br>`library.mobile_backup` | O | Background upload selects local albums and destination accounts, separate cellular rules for photos/videos, charging requirement, album synchronization and account/video/per-album folder overrides; Immich manages its own physical layout. | [R33-S31](<#r33-s31>) |
| **Local and cloud file transfers**<br>`library.move_copy` | C | Copy/move picker supports new folders, device/removable/cloud destinations and authentication for locked albums. Read-only targets are disabled; partial transfers report retained sources. | [R33-S21](<#r33-s21>), [R33-S43](<#r33-s43>) |
| **Device, SD and USB storage roots**<br>`library.multiple_roots` | C | Mounted Android-indexed volumes share one library while retaining volume identity; same-name merges are optional display grouping, not separate catalogues or physical moves. | [R33-S26](<#r33-s26>), [R33-S39](<#r33-s39>) |
| **Offline browsing of cached remote previews**<br>`library.offline_cloud_previews` | O | Force offline uses only cache; account pinning downloads thumbnails/previews with partial-progress/retry status, and per-account/auto-only cache clears retain accounts/listings. | [R33-S41](<#r33-s41>) |
| **Rename original files**<br>`library.rename` | C | Viewer Rename changes actual filename with Android write permission as needed; distinct from description/label editing. Inspected docs establish individual rename, not batch templates. | [R33-S35](<#r33-s35>), [R33-S43](<#r33-s43>) |
| **Manage Immich albums**<br>`library.server_album_management` | O | 5.2.2 populates shared/v3 albums and allows owned-album rename/share/delete/member removal. Same-account Copy adds membership; Move is explicitly unsupported because albums are not folders. | [R33-S2](<#r33-s2>), [R33-S21](<#r33-s21>) |
| **Session and crash logs**<br>`maintenance.diagnostics` | C | Hidden Developer menu exposes grouped/recent logs, severity/date search, breadcrumbs, crash reports, ZIP/copy export and clear/disable controls. Docs warn filenames, paths and server URLs may remain; not an operation-recovery journal. | [R33-S2](<#r33-s2>), [R33-S46](<#r33-s46>) |
| **Conservative app-data health cleanup**<br>`maintenance.orphan_data_cleanup` | C | Daily/on-library-change or manual cleanup removes orphaned extracted data/memberships/edit backups, preserving cloud cache rows and user definitions such as people/collections/vaults. | [R33-S15](<#r33-s15>) |
| **Selective metadata/AI rebuilds**<br>`maintenance.selective_reset` | C | Independently refresh metadata, embeddings, categories or people, or run all in sequence; full refresh deliberately reprocesses complete items. Category reset deletes custom categories but not photos. | [R33-S28](<#r33-s28>), [R33-S29](<#r33-s29>) |
| **Edit labels and descriptions**<br>`metadata.comments` | C | Media Info edits labels/descriptions; video descriptions remain only in the app database rather than embedded file metadata. Direct filename rename is a separate action. | [R33-S35](<#r33-s35>) |
| **Correct capture dates with explicit fallback**<br>`metadata.date_fix` | C | Date/time edits drive capture-sorted timeline. Unsupported formats offer a dated PNG copy instead, warning that PNG flattens animation/HDR/layers/RAW; original can be kept or explicitly trashed. | [R33-S35](<#r33-s35>) |
| **Detailed media metadata viewer**<br>`metadata.exif_read` | C | Displays label/path, capture time, dimensions/size, video duration/fps/format, print density when present and complete metadata list, with cloud/encryption state badges. | [R33-S35](<#r33-s35>) |
| **Device and cloud favorites**<br>`metadata.favorites` | C | Favorite badges/filtering span local/cloud library; release routes supported local favorites through Android request APIs and backup can restore matched favorites. | [R33-S2](<#r33-s2>), [R33-S15](<#r33-s15>), [R33-S32](<#r33-s32>) |
| **Manual coordinate editing**<br>`metadata.gps_write` | N | Map manual explicitly says no in-app coordinate editing; removing existing location metadata is supported separately. | [R33-S25](<#r33-s25>) |
| **Selective lossless metadata sanitization**<br>`metadata.strip` | C | Remove all or selected found categories: location, dates, device/owner, captions/authorship, camera, people, edit history, credentials, thumbnail. Supports JPEG/PNG/WebP/GIF/JP2/JXL/HEIF/AVIF/MP4/MOV/3GP; preserves media data, orientation, profiles, HDR gain maps and motion clip. | [R33-S14](<#r33-s14>) |
| **Bound global cloud preview cache**<br>`performance.cache_limits` | O | 256/512 MB or 1/2/5 GB global cache limits evict oldest cached items; pin whole accounts for previews, cache while browsing and optionally Wi-Fi only. Preview cache is not downloaded originals. | [R33-S41](<#r33-s41>) |
| **Resume and retry Smart scans**<br>`performance.resume` | C | Incremental refresh preserves valid results, skips failures, supports paused/resumable states and retries failed items; cancelling keeps completed work. | [R33-S29](<#r33-s29>) |
| **Persistent heavy-format thumbnails**<br>`performance.thumbnail_cache` | C | 5.2.2 persists JXL/PSD/JP2/TIFF/RAW/deep-bit-depth HEIF thumbnails to disk rather than regenerating each launch. | [R33-S2](<#r33-s2>) |
| **Encrypted multiple vaults**<br>`privacy.at_rest_encryption` | C | Create multiple encrypted vaults with device security or custom PIN/pattern/password and timed lockout; optional list gate/one-lock mode. Encrypt &amp; Keep retains plaintext originals; Encrypt &amp; Delete removes them explicitly. | [R33-S12](<#r33-s12>) |
| **Password-protected backup archive**<br>`privacy.backup_encryption` | C | Optional archive password protects exported vault media, which is decrypted inside archive; vault custom credentials are included only with protected archives. Without archive password restored vault uses device lock. | [R33-S12](<#r33-s12>), [R33-S15](<#r33-s15>) |
| **Block app-content screen capture**<br>`privacy.capture_protection` | C | General Settings Secure Mode blocks screenshots, screen recordings and the recent-apps preview. It protects display/capture surfaces rather than encrypting ordinary files; vault encryption remains a separate feature. | [R33-S49](<#r33-s49>) |
| **Locked but unencrypted private folder**<br>`privacy.hidden_folders` | C | Choose internal/SD/USB directory and optional device/custom gate; .nomedia removes files from normal scans. Files remain readable by direct-storage tools; removal of configuration can keep or remove hiding marker. | [R33-S13](<#r33-s13>) |
| **No-network Offline build**<br>`privacy.offline_use` | C | Offline flavor removes network permissions, maps and cloud access; WithML bundles models for offline AI, whereas Offline NoML cannot download missing models afterward. | [R33-S1](<#r33-s1>), [R33-S2](<#r33-s2>), [R33-S8](<#r33-s8>) |
| **Selective app-state export and merge restore**<br>`safety.catalogue_backup` | C | Archive settings, favorites, cloud configs, groups/collections/categories, metadata/locations, people corrections and optional edit originals/vaults; merge restore keeps existing data and resumes after restart. Ordinary photos outside vaults and biometric/semantic embeddings are excluded. | [R33-S15](<#r33-s15>) |
| **Provider-aware delete review**<br>`safety.confirmation` | C | 5.2.2 lets backed-up selections target device/cloud/both with remembered preference and warns when sources lack trash. Trash confirmations can be enabled; remote-backup-row deletion has an explicit no-extra-confirmation exception. | [R33-S2](<#r33-s2>), [R33-S30](<#r33-s30>), [R33-S31](<#r33-s31>) |
| **Verify sanitization and restricted moves**<br>`safety.copy_verification` | C | Sanitization re-reads output to check removed/retained metadata and exact media payload before saving; restricted Android-folder moves copy/verify before requesting deletion permission. This is operation-specific, not perpetual integrity checking. | [R33-S14](<#r33-s14>), [R33-S43](<#r33-s43>) |
| **Number cloud destination collisions**<br>`safety.no_overwrite` | C | Folder-based WebDAV/SMB/NFS transfer collisions create numbered filenames rather than overwriting; current editor outputs also use random suffixes. | [R33-S21](<#r33-s21>), [R33-S23](<#r33-s23>), [R33-S43](<#r33-s43>) |
| **Current editor saves new copies**<br>`safety.nondestructive_edits` | C | Current photo/video editor never alters opened originals; outputs go to Pictures/ReFra or Movies/ReFra with randomized edited suffix. Unsaved changes/export cancellation require confirmation. | [R33-S16](<#r33-s16>), [R33-S17](<#r33-s17>), [R33-S23](<#r33-s23>) |
| **Android trash with restore**<br>`safety.os_trash` | C | On Android 11+ supported device media normally has roughly 30-day provider-controlled retention, individual/all restore or permanent empty. Disabling trash, unsupported sources and private-folder deletes are permanent. | [R33-S13](<#r33-s13>), [R33-S30](<#r33-s30>) |
| **Editing undo and original restoration**<br>`safety.undo` | C | Current recipes/layer actions have undo/redo and recover committed edits if Android stops app. Legacy editor can revert overwrite only while its separate original edit backup remains; not a general file-operation undo. | [R33-S16](<#r33-s16>), [R33-S33](<#r33-s33>), [R33-S44](<#r33-s44>) |
| **Timeline media filters**<br>`search.file_type` | C | Timeline controls filter type, favorite state, year or album, independently of descriptive AI search. | [R33-S32](<#r33-s32>) |
| **Filename and description search**<br>`search.filename_path` | C | Without AI, queries match stored filename/description; matching category/place/album shortcuts and removable search history appear during typing, excluding locked albums. | [R33-S9](<#r33-s9>) |
| **Metadata discovery categories**<br>`search.metadata` | C | Discovery exposes locations, media types, camera models, special modes and groupings; release notes add synced server tags into metadata search. | [R33-S4](<#r33-s4>), [R33-S5](<#r33-s5>), [R33-S9](<#r33-s9>) |
| **On-device descriptive search**<br>`search.semantic_text` | O | Installed CLIP indexes images; current EmbeddingGemma 2 engine also indexes sampled video content and is documented as multilingual. Results sort by accuracy/date and show indexing progress; engine changes rebuild index. | [R33-S8](<#r33-s8>), [R33-S9](<#r33-s9>) |
| **Delegate search to connected server**<br>`search.server_semantics` | O | Cloud smart-search setting lets capable servers, currently Immich, answer queries; separate provider-type switches download thumbnails for local indexing, including NAS providers without their own AI. | [R33-S6](<#r33-s6>), [R33-S19](<#r33-s19>), [R33-S29](<#r33-s29>) |
| **Image/video example search**<br>`search.similar_image` | O | Choose an example from timeline/albums for similarity-ranked results; current video-aware engine can sample several frames from a video query. Distinct from sending data to Google Lens. | [R33-S8](<#r33-s8>), [R33-S9](<#r33-s9>), [R33-S10](<#r33-s10>) |
| **Edit cloud-share expiry**<br>`sharing.expiring_links` | O | Existing link expiry choices range from one day to one year or never; app can revoke with confirmation, contingent on provider support. | [R33-S42](<#r33-s42>) |
| **Set password on existing cloud shares**<br>`sharing.password_links` | O | Where Immich share-management exposes it, edit a pre-existing link's password; creation remains in server UI. | [R33-S42](<#r33-s42>) |
| **Manage existing Immich shared links**<br>`sharing.public_links` | O | Shared Links lists existing provider links, copies URLs, edits description/download/upload/metadata permissions and revokes links without deleting media. Current app has no create-link screen. | [R33-S42](<#r33-s42>) |

## Limitations and evidence gaps

- **coverage-gap:** Current-branch manuals include newer editor/Handover/EmbeddingGemma behavior not proven shipped in 5.2.2; legacy and new editor storage/overwrite behavior differ. ([R33-S2](<#r33-s2>), [R33-S8](<#r33-s8>), [R33-S11](<#r33-s11>), [R33-S16](<#r33-s16>), [R33-S44](<#r33-s44>))
- **explicit:** README minimum Android 11 conflicts with newer 5.2.2 Android10 requirement; Trash and sanitizer Replace original require Android11+. Provider/private-folder exceptions can permanently delete. ([R33-S1](<#r33-s1>), [R33-S2](<#r33-s2>), [R33-S13](<#r33-s13>), [R33-S14](<#r33-s14>), [R33-S30](<#r33-s30>))
- **explicit:** Vault Encrypt &amp; Keep leaves plaintext originals; sharing/visual search decrypts readable copies. Backup carries vault contents decrypted and excludes ordinary photos, so unpassworded archive exposes those vault files. ([R33-S10](<#r33-s10>), [R33-S12](<#r33-s12>), [R33-S15](<#r33-s15>))
- **explicit:** Metadata cleaner excludes TIFF/RAW/PSD/SVG/BMP/MKV/WebM; some video GPS telemetry cannot be removed. It does not erase visible faces or identifying filenames. ([R33-S14](<#r33-s14>))
- **explicit:** No manual GPS editing, projection selector/VR panorama mode, Google Photos cloud provider or in-app share-link creation. Same-Immich-account Move and mixed local/cloud batch Move are unsupported. ([R33-S19](<#r33-s19>), [R33-S21](<#r33-s21>), [R33-S25](<#r33-s25>), [R33-S37](<#r33-s37>), [R33-S42](<#r33-s42>))
- **explicit:** Cloud sync generally refreshes listings, pinned offline cache holds previews, and ordinary app backups exclude media originals. These operations must not be mistaken for full independent photo backups. ([R33-S15](<#r33-s15>), [R33-S19](<#r33-s19>), [R33-S20](<#r33-s20>), [R33-S41](<#r33-s41>))
- **explicit:** Media Info backup-row deletion permanently removes that remote copy immediately without an additional confirmation or Trash step. ([R33-S31](<#r33-s31>))
- **explicit:** Current RAW TIFF export supports only development, not added crop/markup/look changes; unsupported date writes use PNG copies that flatten animation/HDR/layers/RAW. Viewing support does not guarantee editing/encoding support. ([R33-S18](<#r33-s18>), [R33-S24](<#r33-s24>), [R33-S35](<#r33-s35>))
- **explicit:** Offline NoML cannot fetch missing models. Face Fast/Accurate tiers remain planned. Remote search/Handover/Lens deliberately send queries or derived media elsewhere, and logs need review before sharing. ([R33-S8](<#r33-s8>), [R33-S10](<#r33-s10>), [R33-S11](<#r33-s11>), [R33-S46](<#r33-s46>))
- **coverage-gap:** No exact duplicate-cleanup tool, durable file-action crash journal, general E2EE cloud sync or bundled offline basemap was established; similar-media search is not exact deduplication. ([R33-S9](<#r33-s9>), [R33-S19](<#r33-s19>), [R33-S25](<#r33-s25>), [R33-S46](<#r33-s46>))
- **Coverage gap:** Release-to-current-branch feature boundary is not fully mapped; current manuals and legacy pages are explicitly distinguished.
- **Coverage gap:** Individual cloud-provider credentials/authorization and every appearance/accessibility preference were not exhaustively audited.
- **Coverage gap:** No runtime performance, cryptographic implementation or file-safety tests were performed; claims are documentary.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R33-S1

[ReFra README](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/README.md>)
- Kind/ref: readme; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete README
- Establishes: Distribution, offline variant, permissions and older Android requirement.

### R33-S2

[5.2.2 release](<https://github.com/IacobIonut01/ReFra/releases/tag/5.2.2>)
- Kind/ref: release; 5.2.2
- Sections inspected: Features, improvements, fixes, variants and download requirements
- Establishes: Released cloud/people/HDR/widget behavior and build matrix.

### R33-S3

[5.1.0 changelog](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/app/androidApp/src/main/assets/changelog/51006.md>)
- Kind/ref: release; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete file
- Establishes: RAW development, on-device cutout, local faces, full-resolution editing and metadata sanitization.

### R33-S4

[5.2.0 changelog](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/app/androidApp/src/main/assets/changelog/52001.md>)
- Kind/ref: release; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete file
- Establishes: Rebuilt people, two-way cloud workflows, server search and verified transfers.

### R33-S5

[Store feature description](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/fastlane/metadata/android/en-US/full_description.txt>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete file
- Establishes: Baseline gallery, grouping, viewer, theme, editor and AI scope.

### R33-S6

[Smart features](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/smart-features.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: AI controls, locked/ignored albums and cloud index choices.

### R33-S7

[People](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/people.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Naming, correction, birthdays, covers, suppression and face blurring.

### R33-S8

[AI models](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/ai-models.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Engine/model downloads, tier roadmap and offline prerequisites.

### R33-S9

[Search](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/search.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Text, semantic, image/video example searches and discovery.

### R33-S10

[External visual search](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/visual-search.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Third-party app handoff, vault consent and conversion.

### R33-S11

[Remote inference](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/remote-inference.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Handover deployment, data transfer, authentication and index placement.

### R33-S12

[Vault](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/vault.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: At-rest encryption, authentication, original-retention choices and export caveats.

### R33-S13

[Private folder](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/private-folder.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Unencrypted .nomedia hiding and permanent delete semantics.

### R33-S14

[Remove metadata](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/metadata-privacy.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Format/category-aware lossless sanitization and verification.

### R33-S15

[Backup and restore](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/backup-restore.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Selective settings/catalogue/vault archive and merge restoration.

### R33-S16

[Current photo editor](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/editor.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Tool catalogue, recipe undo/compare and Android lifecycle restoration.

### R33-S17

[Video editor](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/video-editor.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Multitrack video arrangement, clip adjustments and MP4 export.

### R33-S18

[RAW development](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/raw-development.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Demosaicing, tone/color spaces and high-bit-depth output limits.

### R33-S19

[Cloud providers](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/cloud-overview.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Six supported providers and distinction between listing/preview/download/backup.

### R33-S20

[Cloud sync](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/cloud-sync.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Listing schedules, Wi-Fi behavior and opt-in downloaded-copy deletion.

### R33-S21

[Cloud transfers](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/cloud-transfer.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Cross-provider moves/copies and unsupported combinations.

### R33-S22

[Free up space](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/cloud-free-up-space.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Verified backup-based local removal, age/favorite rules and automatic cleanup.

### R33-S23

[Saving current-editor copies](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/save-edits.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Save-as formats, encoder gates, output naming and cancellation.

### R33-S24

[Image formats](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/image-formats.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Viewer formats, flattened design/RAW previews and HDR/editor limitations.

### R33-S25

[Map and locations](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/maps-location.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Location permission, clusters, place timelines and no coordinate editing.

### R33-S26

[Removable storage](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/external-storage.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Android-indexed SD/USB roots and access restrictions.

### R33-S27

[Collections](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/collections.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Virtual manual collections independent of folders.

### R33-S28

[Categories](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/categories.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Text/example-image-defined semantic collections and strictness.

### R33-S29

[Smart scan data](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/smart-scan.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Incremental/selective refresh, progress, cancellation and retry.

### R33-S30

[Trash](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/trash.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Android/provider retention, confirmations and permanent exceptions.

### R33-S31

[Cloud backup](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/cloud-backup.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Album/network/charging rules and immediate remote-copy deletion caveat.

### R33-S32

[Timeline](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/timeline.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Date grid/mosaic, smart stacks, selection, filtering and split viewer.

### R33-S33

[Photo layers](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/editor-layers.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Sixteen image layers, blend modes, masks and source relinking.

### R33-S34

[Video audio tools](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/video-audio.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Voice-over, clip sound, mixer, ducking, channel routing and EQ.

### R33-S35

[Media details and metadata editing](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/metadata.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Technical details, labels/descriptions and dated-copy fallback.

### R33-S36

[Motion Photos](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/motion-photos.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Embedded clip playback, video extraction and frame picking.

### R33-S37

[Panoramas](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/panoramas.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Panoramic projection, gyroscope sphere viewing and explicit VR limit.

### R33-S38

[FCast](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/casting.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: LAN receiver discovery/manual connection and codec constraints.

### R33-S39

[Album organization](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/album-organization.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Pins, covers, display-only merges, groups and sections.

### R33-S40

[Home-screen widgets](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/widgets.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Single/grid widgets and nondestructive styles.

### R33-S41

[Offline cloud cache](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/cloud-offline.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Preview-only pinning, global cache bounds and force-offline mode.

### R33-S42

[Existing cloud share links](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/cloud-shared-links.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Immich link editing/revocation and no create-link screen.

### R33-S43

[Copy, move and rename](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/copy-move-rename.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Destination selection, collision handling and verified restricted-folder moves.

### R33-S44

[Legacy save/overwrite](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/legacy-save-edits.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Legacy overwrite backups/revert and format limitations.

### R33-S45

[Subject cutout](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/subject-cutout.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Point-refined subject masks and transparent PNG output.

### R33-S46

[Session logs](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/session-logs.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Diagnostics export/clear and explicit sensitive-log warning.

### R33-S47

[French Compose UI resources](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/app/commonApp/src/commonMain/composeResources/values-fr-rFR/strings.xml>)
- Kind/ref: code; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Opening resource block through library label: navigation, actions, settings, trash and edit-backup strings
- Establishes: Actual French interface translations with some English strings still present.

### R33-S48

[German Compose UI resources](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/app/commonApp/src/commonMain/composeResources/values-de-rDE/strings.xml>)
- Kind/ref: code; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Opening resource block through library label: navigation, actions, settings, trash and edit-backup strings
- Establishes: Actual German translations of application controls, not documentation or search-model language claims.

### R33-S49

[General settings](<https://github.com/IacobIonut01/ReFra/blob/632030899803846d31073a672e56ee2581f59f62/website/src/content/features/general-settings.mdx>)
- Kind/ref: manual; 632030899803846d31073a672e56ee2581f59f62
- Sections inspected: Complete page
- Establishes: Secure Mode capture protection, deletion policies, haptics and launcher identity.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
