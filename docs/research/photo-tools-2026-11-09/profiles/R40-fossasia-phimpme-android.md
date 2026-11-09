# R40 — fossasia/phimpme-android

[Repository](<https://github.com/fossasia/phimpme-android>) · 2,588 stars at the frozen snapshot · gallery-mobile · Archived

**Purpose:** Legacy Android camera, local gallery, image editor and multi-service sharing application.

**Deployment:** Android application; historical Google Play and repository release distribution

**Storage:** Existing local media folders and all-photo views, local edits, favourites, descriptions and app-specific trash/upload-history data. Sources do not establish embedded-versus-catalogue storage for descriptions.

**Privacy/network behavior:** Local camera/gallery/editing do not require uploading to a provider. Sharing explicitly sends selected media to configured social/cloud services. Store description claims the project does not store user data; this is not a guarantee about destination services. Geotagging is disabled by default and embeds location when enabled.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v1.11.0 (2020-08-15T18:01:45Z)
**Repository pushed at:** 2026-06-10T10:49:13Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [60acbd2e5691](<https://github.com/fossasia/phimpme-android/commit/60acbd2e5691d3d2f794b86e1277bfedab481035>).
**Product lineage:** fossasia/phimpme-android.

## Maturity and availability caveats

- Repository is archived in the frozen manifest. Snapshot is development commit 60acbd2e5691d3d2f794b86e1277bfedab481035; latest release v1.11.0 is dated 2020-08-15.
- README says development contains ongoing work and master is stable; source-only UI options can be ahead of that release.
- Integrated service APIs, Android permissions and voice-assistant behaviour may have changed since the historical release; no live service compatibility was tested.
- Acknowledges Open Camera and LeafPic lineage, with OpenCV-based editing.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Dark and AMOLED themes**<br>`browse.dark_theme` | C | Choose white, dark or dark AMOLED themes, primary/accent colours, navigation styling and a separate media-viewer theme. | [R40-S4](<#r40-s4>), [R40-S2](<#r40-s2>) |
| **Folder albums and covers**<br>`browse.folders` | C | Gallery UI offers folder navigation, album rename, new folders and setting or clearing an album preview/cover. | [R40-S4](<#r40-s4>) |
| **Configurable gallery columns**<br>`browse.grid` | C | Separate folder/media column settings are provided for portrait and landscape layouts. | [R40-S4](<#r40-s4>) |
| **Timed image slideshow**<br>`browse.slideshow` | C | Gallery has slideshow and interval controls; later validation text restricts interval input to 2–10 seconds. | [R40-S4](<#r40-s4>) |
| **Internal video player**<br>`browse.video_playback` | C | Settings explicitly permit the embedded video player instead of another app; historical service compatibility is unrelated to this local feature. | [R40-S4](<#r40-s4>) |
| **Full-resolution zoom behaviour**<br>`browse.zoom` | C | Viewer settings allow delaying full-size loading or loading the full image only when zoomed in. | [R40-S4](<#r40-s4>) |
| **Built-in camera**<br>`capture.camera` | C | Take photographs inside the app with advanced scene and white-balance modes and front/rear camera selection. | [R40-S1](<#r40-s1>) |
| **Optional capture-time geotagging**<br>`capture.geotagging` | O | Camera introduction says geotagging starts disabled, requires location permission and records location in saved files when enabled. | [R40-S4](<#r40-s4>) |
| **Automatic and manual camera controls**<br>`capture.manual_controls` | C | Official application description explicitly documents automatic and manual camera control; device-specific support is not enumerated. | [R40-S3](<#r40-s3>) |
| **Voice-launched camera**<br>`capture.voice_trigger` | O | README describes Google voice actions for taking a picture and selecting front/rear cameras; requires the external voice-assistant integration. | [R40-S1](<#r40-s1>) |
| **Android camera and gallery application**<br>`deployment.android` | C | README provides Android distribution and development setup; latest frozen release is v1.11.0. | [R40-S1](<#r40-s1>), [R40-S2](<#r40-s2>) |
| **Filters and tonal adjustment**<br>`editing.adjustments` | C | OpenCV-based filters plus contrast, hue, saturation, temperature, tint and sharpness controls are explicitly documented. | [R40-S1](<#r40-s1>), [R40-S3](<#r40-s3>) |
| **Stickers and handwriting**<br>`editing.annotations` | C | Add facial/expression/object/comment/wish/emoji/hashtag stickers and draw handwritten content on images. | [R40-S1](<#r40-s1>) |
| **Affix selected images**<br>`editing.collage` | C | Affix combines at least two images horizontally or vertically, with output-format, quality and save-in-current-album controls; videos are explicitly rejected. | [R40-S4](<#r40-s4>) |
| **Crop with aspect ratios**<br>`editing.crop` | C | Transform section provides cropping, with free and preset ratios including 1:1, 3:2, 7:5 and 16:9 in UI resources. | [R40-S1](<#r40-s1>), [R40-S4](<#r40-s4>) |
| **Compress by dimensions or size**<br>`editing.resize` | C | Gallery action text exposes separate compression-by-dimensions and compression-by-size workflows; exact compression algorithm is not established. | [R40-S4](<#r40-s4>) |
| **Rotate images**<br>`editing.rotate_flip` | C | Transform rotates images; gallery UI specifically lists left/right 90-degree and 180-degree rotations. Flip is not established by the inspected feature list. | [R40-S1](<#r40-s1>), [R40-S4](<#r40-s4>) |
| **GIF media category**<br>`formats.animated` | C | Gallery offers GIF filtering and the release lists an Android GIF drawable dependency; exact animation performance is not measured. | [R40-S4](<#r40-s4>), [R40-S2](<#r40-s2>) |
| **ZIP a folder**<br>`library.archive_export` | C | Gallery exposes folder ZIP creation with progress, cancellation and saved-location feedback. | [R40-S4](<#r40-s4>) |
| **Browse local media in place**<br>`library.existing_folders` | C | README explicitly provides local folder and all-photos modes without a mandatory cloud import. | [R40-S1](<#r40-s1>) |
| **Copy and move images**<br>`library.move_copy` | C | Copy/move media to existing or newly created folders; UI asks whether to replace files or make copies. | [R40-S1](<#r40-s1>), [R40-S4](<#r40-s4>) |
| **Rename image and album**<br>`library.rename` | C | UI includes individual image and album rename actions, with a warning when changing an image extension. | [R40-S4](<#r40-s4>) |
| **Upload and archive progress**<br>`maintenance.notifications` | C | UI defines per-provider upload progress/success/retry notifications and ZIP operation progress/completion. | [R40-S4](<#r40-s4>) |
| **Photo descriptions**<br>`metadata.comments` | C | README supports adding descriptions; UI provides create, update and delete feedback. Embedded metadata writing is not established. | [R40-S1](<#r40-s1>), [R40-S4](<#r40-s4>) |
| **Image technical details**<br>`metadata.exif_read` | C | Details UI includes EXIF, device, orientation, location, path, type and resolution, with missing-data states. | [R40-S4](<#r40-s4>) |
| **Favourite photo collection**<br>`metadata.favorites` | C | Long-select or use the heart action to add/remove favourites, including multiple selected images; the collection has a dedicated view. | [R40-S4](<#r40-s4>) |
| **Defer high-resolution loading**<br>`performance.deferred_fullsize` | C | Viewer can delay full-size image loading until zoom, and automatic media refresh can be disabled for large libraries according to its setting help. | [R40-S4](<#r40-s4>) |
| **Hide versus exclude folders**<br>`privacy.hidden_folders` | C | Hide creates .nomedia and can affect other apps; exclusion affects this gallery recursively, with an option to choose a parent directory. Neither is described as encryption. | [R40-S4](<#r40-s4>) |
| **Local capture and editing**<br>`privacy.no_upload_required` | C | Local gallery and editing precede optional connected-service sharing; official store text claims the project does not store users' data. | [R40-S1](<#r40-s1>), [R40-S3](<#r40-s3>) |
| **App-specific trash and restore**<br>`safety.app_recovery` | C | Move to TrashBin, restore individually/all, or permanently delete; help says only images deleted inside Phimpme appear here. | [R40-S4](<#r40-s4>), [R40-S2](<#r40-s2>) |
| **Destructive-action and discard confirmation**<br>`safety.confirmation` | C | UI asks before deleting images/albums, permanently clearing trash and discarding crop/rotation/filter/annotation edits. | [R40-S4](<#r40-s4>) |
| **Editor undo and redo**<br>`safety.undo` | C | README documents back/forward editing steps; this is editing history, not a durable journal for file moves and deletions. | [R40-S1](<#r40-s1>), [R40-S3](<#r40-s3>) |
| **Images, video and GIF filters**<br>`search.file_type` | C | Filter menu distinguishes all media, images, videos and GIFs. | [R40-S4](<#r40-s4>) |
| **Connected social and cloud sharing**<br>`sharing.social_export` | O | Historical README lists Facebook, Messenger, Twitter, Nextcloud, ownCloud, Imgur, Dropbox, Box, Flickr, Pinterest, Instagram, WhatsApp and Tumblr. Some builds need service API keys/application IDs and external accounts; current provider compatibility is unverified. | [R40-S1](<#r40-s1>) |
| **Upload history**<br>`sharing.upload_history` | C | Dedicated history offers latest/last-first ordering and clear-history confirmation; clearing history is not documented as deleting provider copies. | [R40-S4](<#r40-s4>) |
| **Date-taken ordering**<br>`sort.capture_date` | C | Gallery sort menu includes date and date taken. | [R40-S4](<#r40-s4>) |
| **Order by file size**<br>`sort.file_size` | C | Size is explicitly listed among gallery sort choices. | [R40-S4](<#r40-s4>) |
| **Name and numeric ordering**<br>`sort.filename` | C | Sort controls include name, numeric interpretation and ascending order. | [R40-S4](<#r40-s4>) |

## Limitations and evidence gaps

- **coverage-gap:** Archived project with a 2020 latest release; provider authentication, Google voice actions and modern Android compatibility were not verified. Listed integrations are historical documented functionality, not a promise of current service availability. ([R40-S1](<#r40-s1>), [R40-S2](<#r40-s2>))
- **explicit:** Sharing builds require API keys/application IDs for several external services, and sharing intentionally sends images off-device. ([R40-S1](<#r40-s1>))
- **explicit:** Trash contains only images deleted in this application. Hiding uses .nomedia and is not a secure encrypted vault. ([R40-S4](<#r40-s4>))
- **explicit:** Affix cannot combine videos and needs at least two images; gallery auto-refresh help recommends disabling it for very large collections. ([R40-S4](<#r40-s4>))
- **coverage-gap:** No inspected evidence establishes semantic search, face recognition, exact duplicate detection, encrypted backup, sidecar writing or a durable file-operation journal. Isolated Tags/Timeline string labels were not treated as implemented features. ([R40-S1](<#r40-s1>), [R40-S4](<#r40-s4>))
- **Coverage gap:** No substantive separate manual beyond README-derived documentation; official store description, detailed UI guidance and release notes used.
- **Coverage gap:** Source-UI-only features marked medium confidence; external integrations not live-tested.
- **Coverage gap:** Focused pinned-tree localization discovery and inspected English UI documentation did not establish multiple translated interface languages; this remains undocumented, not explicitly unsupported.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations, interface localization.

## Inspected primary sources

### R40-S1

[Phimp.me README](<https://github.com/fossasia/phimpme-android/blob/60acbd2e5691d3d2f794b86e1277bfedab481035/README.md>)
- Kind/ref: readme; 60acbd2e5691d3d2f794b86e1277bfedab481035
- Sections inspected: Complete README including features, branch policy and sharing-key setup
- Establishes: Camera, gallery, editor, sharing integrations and build/API prerequisites.

### R40-S2

[Release v1.11.0](<https://github.com/fossasia/phimpme-android/releases/tag/v1.11.0>)
- Kind/ref: release; v1.11.0
- Sections inspected: Complete release notes
- Establishes: Release-era UI, trash, gallery, Android and provider compatibility context.

### R40-S3

[Official application description](<https://github.com/fossasia/phimpme-android/blob/60acbd2e5691d3d2f794b86e1277bfedab481035/fastlane/metadata/android/en-US/full_description.txt>)
- Kind/ref: manual; 60acbd2e5691d3d2f794b86e1277bfedab481035
- Sections inspected: Complete description and feature list
- Establishes: User-facing camera, manual control, privacy, editor and sharing claims.

### R40-S4

[English in-app feature and help text](<https://github.com/fossasia/phimpme-android/blob/60acbd2e5691d3d2f794b86e1277bfedab481035/app/src/main/res/values/strings.xml>)
- Kind/ref: code; 60acbd2e5691d3d2f794b86e1277bfedab481035
- Sections inspected: Camera introduction; complete gallery actions, dialogs, affix, settings, photo details, upload history and trash sections; later viewer and trash guidance
- Establishes: Precisely labelled UI capabilities and their safety/storage caveats; not proof of currently functioning external services.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
