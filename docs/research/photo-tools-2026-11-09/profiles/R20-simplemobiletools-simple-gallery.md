# R20 — SimpleMobileTools/Simple-Gallery

[Repository](<https://github.com/SimpleMobileTools/Simple-Gallery>) · 4,031 stars at the frozen snapshot · gallery-mobile · Not archived

**Purpose:** Android local-media browser and editor with folder-oriented management, configurable viewing and application-level privacy locks.

**Deployment:** Android application; F-Droid build linked by README; Build flavours: foss, proprietary and prepaid

**Storage:** Browses existing Android media and folders rather than requiring a hosted photo library. Android MediaStore and permission differences affect access. Application cache and a 30-day recycle bin consume app storage; favourites can be exported as paths.

**Privacy/network behavior:** Local gallery with no required upload documented. PIN, pattern and fingerprint controls restrict app/folder/action access; hiding uses .nomedia and is not encryption. Proprietary editor distribution differs from the FOSS build.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 6.28.1 (2023-10-09T20:09:48Z)
**Repository pushed at:** 2024-08-18T04:23:47Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a3564013b7ac](<https://github.com/SimpleMobileTools/Simple-Gallery/commit/a3564013b7ac2828d3b0f11572ce225f094423ff>).
**Product lineage:** Simple-Gallery-Fossify.

## Maturity and availability caveats

- Frozen master commit a3564013b7ac2828d3b0f11572ce225f094423ff; manifest latest release 6.28.1 dated 2023-10-09 and last push in August 2024.
- This inventory concerns SimpleMobileTools/Simple-Gallery, not a feature union with the separate Fossify successor family.
- README's general editor claims need build-flavour qualification: Gradle applies IMG.LY SDK only for proprietary tasks. Current commercial-store behaviour is not verified.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Theme and interface customization**<br>`browse.dark_theme` | C | README allows appearance customization; release history adds automatic and Material You themes, with Material You default on Android 12+. | [R20-S1](<#r20-s1>), [R20-S2](<#r20-s2>) |
| **Folder navigation and ordering**<br>`browse.folders` | C | Switch folders/all-files, group direct subfolders, pin multiple folders, select a default folder and reorder folders by dragging. | [R20-S3](<#r20-s3>), [R20-S2](<#r20-s2>) |
| **Customizable fullscreen viewer**<br>`browse.fullscreen` | C | Hide system UI, choose black background or maximum brightness, select orientation policy and configure visible bottom actions and extended details. | [R20-S3](<#r20-s3>) |
| **Configurable thumbnails**<br>`browse.grid` | C | Square cropping, rounded or square corners, spacing, horizontal scrolling, file-type labels, duration labels and folder media counts are configurable. | [R20-S3](<#r20-s3>) |
| **Panoramic photo support**<br>`browse.panorama` | C | README explicitly lists panoramic photos among supported media; spherical metadata requirements are not specified. | [R20-S1](<#r20-s1>) |
| **Mixed-media slideshows**<br>`browse.slideshow` | C | Choose photo/video/GIF inclusion, interval, random or reverse ordering, looping and fade/slide/no transition. | [R20-S3](<#r20-s3>) |
| **Date-grouped media thumbnails**<br>`browse.timeline` | C | Group by capture date or last modification, daily or monthly, with optional per-section counts; grouping and sorting are independent. | [R20-S3](<#r20-s3>) |
| **Gesture-controlled viewing**<br>`browse.touch` | C | Vertical swipes adjust photo brightness or video volume/brightness; rotation gestures, edge taps and downward dismissal are configurable. | [R20-S3](<#r20-s3>) |
| **Configurable video player**<br>`browse.video_playback` | C | Supports autoplay, looping, remembered playback position, double-tap seeking, separate-screen horizontal gestures and double-tap video zoom. | [R20-S3](<#r20-s3>) |
| **Deep and one-finger zoom**<br>`browse.zoom` | C | Options include one-finger zoom, deeper zoom, 1:1 zoom with two double taps and highest-quality image rendering to reduce banding. | [R20-S3](<#r20-s3>) |
| **Remove folders emptied by deletion**<br>`cleanup.empty_folders` | C | Settings can delete empty folders after deleting their contents; this is not a whole-disk empty-folder scanner. | [R20-S3](<#r20-s3>) |
| **Android gallery**<br>`deployment.android` | C | Native Android application; version 6.26.0 raised minimum Android to 6 and README links the F-Droid package. | [R20-S1](<#r20-s1>), [R20-S2](<#r20-s2>) |
| **Translated Android interface**<br>`deployment.localization` | C | Changelog repeatedly documents translation updates and explicitly adds an Android 13+ app-language picker in 6.25.0, with in-app language change in 6.26.9. This establishes localized UI without inferring an exact completeness/language count. | [R20-S2](<#r20-s2>) |
| **Basic cropping**<br>`editing.crop` | C | Editor offers draggable corners and free, fixed and custom aspect ratios. | [R20-S1](<#r20-s1>), [R20-S3](<#r20-s3>) |
| **Advanced SDK filters and adjustments**<br>`editing.proprietary_adjustments` | O | Proprietary build conditionally includes IMG.LY advanced editor. UI defines exposure, highlights, shadows, clarity, gamma, colour, blur-focus, overlays, text and sticker controls; these must not be attributed to every FOSS build. | [R20-S3](<#r20-s3>), [R20-S4](<#r20-s4>) |
| **Single and batch resize**<br>`editing.resize` | C | Set width/height with aspect preservation or batch-resize selected images by a factor between 10% and 90%; batch resizing appears in 6.26.9. | [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>) |
| **Rotate and flip**<br>`editing.rotate_flip` | C | Rotate left/right/180 degrees and flip horizontally or vertically in the editing workflow. | [R20-S1](<#r20-s1>), [R20-S3](<#r20-s3>) |
| **Advanced video trimming and merging**<br>`editing.video_trim_join` | O | Video Trim UI and 6.26.4 merging belong to the Advanced Editor; its SDK is conditional on the proprietary flavour. | [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>), [R20-S4](<#r20-s4>) |
| **Animated image viewing and thumbnails**<br>`formats.animated` | C | Supports GIF, WebP thumbnail animation including folder thumbnails in 6.28.0, and APNG from 6.21.0. | [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>) |
| **AVIF on Android 12**<br>`formats.avif` | C | Version 6.23.2 adds .avif support specifically on Android 12. | [R20-S2](<#r20-s2>) |
| **HEIC display and zoom**<br>`formats.heic` | C | Version 6.21.0 includes HEIC zoom fixes, establishing the supported viewing path without a conversion claim. | [R20-S2](<#r20-s2>) |
| **RAW photo support**<br>`formats.raw` | C | README lists RAW and media filters provide a separate RAW category; individual camera decoder coverage is not specified. | [R20-S1](<#r20-s1>), [R20-S3](<#r20-s3>) |
| **SVG viewing**<br>`formats.svg` | C | README and file-type filters explicitly support SVG images. | [R20-S1](<#r20-s1>), [R20-S3](<#r20-s3>) |
| **Open media location on a map**<br>`geo.external_map` | C | UI exposes Show on map and an unknown-location state. An integrated offline basemap or geocoder is not established. | [R20-S3](<#r20-s3>) |
| **Folder photo widget**<br>`integration.home_widgets` | C | Widget settings select the displayed folder and whether to show its name. | [R20-S3](<#r20-s3>) |
| **Home and lock-screen wallpaper**<br>`integration.wallpaper` | C | Set home, lock or both wallpapers with portrait/landscape and adjustable aspect ratios. | [R20-S3](<#r20-s3>) |
| **Browse existing device media**<br>`library.existing_folders` | C | Folder and All Files views operate on device media; no managed re-import is required. Android 11+ storage permissions affect visibility. | [R20-S3](<#r20-s3>) |
| **Recursive folder inclusion and exclusion**<br>`library.folder_structure` | C | Manage Included Folders adds missed locations; exclusions are recursive and affect only this app. An included folder wins when also excluded, allowing a root exclusion plus selected inclusions. | [R20-S3](<#r20-s3>) |
| **Move and copy device files**<br>`library.move_copy` | C | Copy/move destination picker remembers the last folder, can show excluded folders and supports SD-card paths subject to Android permissions. | [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>) |
| **Rename media and folders**<br>`library.rename` | C | Release history documents file renaming and resizing-with-renaming; FAQ describes renaming dot-prefixed hidden folders. Batch-rename templates are not established. | [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>) |
| **Repair date-taken values**<br>`metadata.date_fix` | C | Select thumbnails and use Fix Date Taken when copied files sort incorrectly; exact embedded-versus-MediaStore write semantics are not documented by the FAQ. | [R20-S3](<#r20-s3>) |
| **Favourites with path export/import**<br>`metadata.favorites` | C | Mark favourites on thumbnails, toggle in the viewer and export/import favourite file paths; this export is not a full media backup. | [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>) |
| **Speed versus validity/quality controls**<br>`performance.loading_policy` | C | Settings expose file-loading priority choices including speed, compromise and avoiding invalid files, plus high-quality deep-zoom rendering. | [R20-S3](<#r20-s3>) |
| **Image-loading cache**<br>`performance.thumbnail_cache` | C | FAQ describes up to 250 MB of cache for faster image loading; recycle-bin media adds further application storage. | [R20-S3](<#r20-s3>) |
| **PIN, pattern and fingerprint protection**<br>`privacy.app_lock` | C | README documents app-level, selected-media and function locks; excluded-folder visibility can also be password protected. Locked folder copies require unlocking in 6.27.1. | [R20-S1](<#r20-s1>), [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>) |
| **Hide with .nomedia or app-only exclusions**<br>`privacy.hidden_folders` | C | Hide creates a removable .nomedia marker recursively; Exclude hides only within Simple Gallery. Hidden access requires All Files permission on affected Android versions. | [R20-S3](<#r20-s3>) |
| **Application recycle bin**<br>`safety.app_recovery` | C | Deleted items can be restored for 30 days, after which automatic deletion occurs. Restoration falls back to Pictures when the original folder is inaccessible; recent versions allow bypassing the bin. | [R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>) |
| **Deletion review**<br>`safety.confirmation` | C | Version 6.23.8 adds the size of items to be deleted to the confirmation dialog. | [R20-S2](<#r20-s2>) |
| **Media-type filtering**<br>`search.file_type` | C | Filters distinguish images, videos, GIFs, RAW, SVG and portrait categories; thumbnails can also be grouped by type or extension. | [R20-S3](<#r20-s3>) |
| **Device-wide visible-file search**<br>`search.filename_path` | C | Main screen can search files rather than folders and switch to searching across all visible folders; destination picker also supports search. | [R20-S3](<#r20-s3>), [R20-S2](<#r20-s2>) |
| **Share a resized version**<br>`sharing.resized_copy` | C | Viewer includes a dedicated Share a resized version action rather than requiring full-size transmission. | [R20-S3](<#r20-s3>) |
| **Sort by date taken**<br>`sort.capture_date` | C | FAQ documents date-taken sorting and its associated date-fix action for copied files. | [R20-S3](<#r20-s3>) |

## Limitations and evidence gaps

- **explicit:** App/folder locks and .nomedia hiding are not encrypted storage. The FAQ permits resetting a forgotten app password by clearing application data or reinstalling without deleting media. ([R20-S3](<#r20-s3>))
- **explicit:** Android 11+ storage restrictions affect hidden folders and real-path inclusion. All Files and Media management permissions, Android version and distribution flavour change behaviour; older restrictive FAQ text is supplemented by later All Files support. ([R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>))
- **explicit:** Recycle-bin contents are automatically removed after 30 days and deletion can bypass the bin; it is not guaranteed permanent recovery. ([R20-S2](<#r20-s2>), [R20-S3](<#r20-s3>))
- **coverage-gap:** Advanced proprietary editing is separated from core FOSS functionality. Exact current paid entitlement and store build parity are not established. ([R20-S4](<#r20-s4>))
- **coverage-gap:** No inspected evidence establishes face recognition, semantic search, duplicate detection, metadata sidecars, E2EE or cloud-library backup. ([R20-S1](<#r20-s1>), [R20-S3](<#r20-s3>))
- **Coverage gap:** Modern commercial-store behaviour not verified; profile is pinned repository and released-history evidence.
- **Coverage gap:** No broad AI, duplicate-cleanup or hosted-library capabilities established.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R20-S1

[Simple Gallery README](<https://github.com/SimpleMobileTools/Simple-Gallery/blob/a3564013b7ac2828d3b0f11572ce225f094423ff/README.md>)
- Kind/ref: readme; a3564013b7ac2828d3b0f11572ce225f094423ff
- Sections inspected: Complete README
- Establishes: Local management, formats, basic editing, recovery and security options.

### R20-S2

[Release changelog](<https://github.com/SimpleMobileTools/Simple-Gallery/blob/a3564013b7ac2828d3b0f11572ce225f094423ff/CHANGELOG.md>)
- Kind/ref: release; a3564013b7ac2828d3b0f11572ce225f094423ff
- Sections inspected: Complete entries 6.28.1 through 6.20.0
- Establishes: Recent released capabilities, format support, Android restrictions and recovery behaviour.

### R20-S3

[In-app settings and FAQ](<https://github.com/SimpleMobileTools/Simple-Gallery/blob/a3564013b7ac2828d3b0f11572ce225f094423ff/app/src/main/res/values/strings.xml>)
- Kind/ref: manual; a3564013b7ac2828d3b0f11572ce225f094423ff
- Sections inspected: Complete English user strings and FAQ
- Establishes: Detailed viewing, slideshow, include/exclude, editing, privacy and cache controls.

### R20-S4

[Application flavour configuration](<https://github.com/SimpleMobileTools/Simple-Gallery/blob/a3564013b7ac2828d3b0f11572ce225f094423ff/app/build.gradle.kts>)
- Kind/ref: code; a3564013b7ac2828d3b0f11572ce225f094423ff
- Sections inspected: Complete file, productFlavors and conditional PESDK plugin
- Establishes: Separates FOSS, proprietary and prepaid builds and identifies conditional advanced editor.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
