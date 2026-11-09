# R31 — UnevenSoftware/LeafPic

[Repository](<https://github.com/UnevenSoftware/LeafPic>) · 3,260 stars at the frozen snapshot · gallery-mobile · Not archived

**Purpose:** Unmaintained Android local-media gallery with folder albums, file operations, themes, EXIF details, slideshow, crop and password/fingerprint gates; development-source capabilities are not all in the old released APK.

**Deployment:** Android application; README links F-Droid and Google Play

**Storage:** Browses existing Android media/files rather than a mandatory imported library. MediaStore is updated after file operations; local SQLite/Hawk state retains album settings, exclusions and authentication preferences. Crop output is copied as a new image.

**Privacy/network behavior:** Core browsing/file operations address on-device media. Hidden-album and delete password/fingerprint gates are UI authorization, not established file encryption. Static maps send coordinates to Google, Mapbox or Tyler/Stamen services; their legacy endpoints were not tested.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v0.6-beta-1 (2016-10-09T20:06:56Z)
**Repository pushed at:** 2024-02-14T23:27:23Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [cfec78746776](<https://github.com/UnevenSoftware/LeafPic/commit/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181>).
**Product lineage:** UnevenSoftware/LeafPic.

## Maturity and availability caveats

- README explicitly says the project is no longer maintained despite manifest archived=false.
- Frozen dev cfec78746776ed4bbccf9387bfc3f6ba1bb2c181; latest manifest release v0.6-beta-1 dates to 2016, while root changelog describes v0.7 features.
- Current-source observations are labeled where release availability or incomplete UI paths are uncertain.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Folder-backed albums**<br>`albums.folder_mapping` | C | Album settings and exclusions are keyed by folder path and album contents come from the Android content-provider helper. | [R31-S4](<#r31-s4>) |
| **Pinned albums**<br>`albums.pin` | C | Pin/unpin updates local album settings and re-sorts the grid. | [R31-S4](<#r31-s4>) |
| **Dark and AMOLED themes**<br>`browse.dark_theme` | C | Choose light, dark or AMOLED base theme and customize colors from a palette. | [R31-S9](<#r31-s9>) |
| **Immersive single-media viewer**<br>`browse.fullscreen` | C | Tap toggles toolbar/system bars, with an immersive full-screen mode and swipeable media pager. | [R31-S3](<#r31-s3>) |
| **Configurable album grid**<br>`browse.grid` | C | Album grid has separate portrait/landscape column settings, optional animations, pull-to-refresh and multi-selection. | [R31-S4](<#r31-s4>) |
| **Viewer rotation**<br>`browse.rotate_view` | C | Single-media menu sends ±90 or 180-degree rotations to the image fragment; persistent original-file rotation is not established by this inspected handler. | [R31-S3](<#r31-s3>) |
| **Looping slideshow**<br>`browse.slideshow` | C | Slideshow schedules automatic advancement modulo album size and hides system UI; stopping removes callbacks. | [R31-S2](<#r31-s2>), [R31-S3](<#r31-s3>) |
| **Calendar-grouped timeline implementation**<br>`browse.timeline` | C | Pinned development source defines day/week/month/year grouping and chronological group comparison; not asserted as present in 2016 release. | [R31-S16](<#r31-s16>), [R31-S10](<#r31-s10>) |
| **Video preview and player handoff**<br>`browse.video_playback` | C | Video fragment renders a thumbnail and launches ACTION_VIEW with media MIME and URI permission when played; do not assume all codecs are internally decoded. | [R31-S14](<#r31-s14>) |
| **Image zoom**<br>`browse.zoom` | C | Bundled release notes explicitly discuss a zoom-out fix with SubScaling ImageView enabled; exact current gesture behavior was not runtime-tested. | [R31-S17](<#r31-s17>) |
| **Android gallery**<br>`deployment.android` | C | Native Android gallery with F-Droid/Play distribution links; current store availability was not tested. | [R31-S1](<#r31-s1>) |
| **Localized Android gallery interface**<br>`deployment.localization` | C | Crowdin-maintained Android resource translations localize gallery controls and dialogs, not just README text. Inspected French resources cover filtering/sorting, copy/move/delete, sharing, confirmation and password/fingerprint controls; bundled release notes explicitly mention translation updates. No claim is made that every locale is complete. | [R31-S1](<#r31-s1>), [R31-S17](<#r31-s17>), [R31-S18](<#r31-s18>) |
| **Affix two-picture composite**<br>`editing.collage` | ? | Changelog lists Affix and source can concatenate two decoded pictures horizontally into a new JPEG, but grid menu starts hidden and available entry path/release completeness is not established. | [R31-S2](<#r31-s2>), [R31-S11](<#r31-s11>), [R31-S13](<#r31-s13>) |
| **Image color palette screen**<br>`metadata.color_palette` | C | v0.7 lists Color Palette and single-media handler opens PaletteActivity for the current file; color search/editing is not implied. | [R31-S2](<#r31-s2>), [R31-S3](<#r31-s3>) |
| **Free-style crop**<br>`editing.crop` | C | UCrop is launched with a PNG cache destination and free-style cropping enabled. | [R31-S3](<#r31-s3>) |
| **Animated GIF viewer**<br>`formats.animated` | C | A dedicated GifImageView loads the GIF URI, separate from ordinary image and video previews. | [R31-S15](<#r31-s15>) |
| **Online static-map provider support**<br>`geo.static_map` | O | Static-map URLs embed image coordinates for Google, Mapbox streets/dark/light or Tyler/Stamen; this is not an offline basemap or full-library map. | [R31-S7](<#r31-s7>) |
| **Album launcher shortcuts**<br>`integration.album_shortcuts` | C | Selected album paths can be sent to a shortcut-creation helper from the album menu. | [R31-S4](<#r31-s4>) |
| **Share, open, edit and use-as handoffs**<br>`integration.android_intents` | C | Android choosers receive file URIs with read permission for sharing, external editing/viewing and attach/use-as actions. | [R31-S3](<#r31-s3>) |
| **Android printing**<br>`integration.print` | C | PrintHelper renders the selected bitmap with fit-to-page scaling and reports failures. | [R31-S2](<#r31-s2>), [R31-S3](<#r31-s3>) |
| **Exclude folders or parents**<br>`library.exclude_folders` | C | Exclude selected album paths, or select a parent to remove all displayed descendants without deleting media. | [R31-S4](<#r31-s4>) |
| **On-device media in place**<br>`library.existing_folders` | C | Queries Android media albums and operates on their existing paths; local originals are not obligatorily re-imported. | [R31-S4](<#r31-s4>), [R31-S5](<#r31-s5>) |
| **Move and copy originals**<br>`library.move_copy` | C | Choose destination folders; helpers move/copy underlying files and rescan new paths in MediaStore. | [R31-S3](<#r31-s3>), [R31-S5](<#r31-s5>) |
| **Rename original file**<br>`library.rename` | C | Single-media action prompts for a new name, moves the file and updates MediaStore/path state. | [R31-S3](<#r31-s3>), [R31-S5](<#r31-s5>) |
| **Fix-date action**<br>`metadata.date_fix` | R | Details dialog includes Fix Date but its callback contains a TODO/commented implementation and only reports unable-to-fix-date. | [R31-S3](<#r31-s3>) |
| **EXIF and technical details**<br>`metadata.exif_read` | C | Shows path, MIME, size, orientation, dimensions, modification date, original capture date, camera/EXIF summary and GPS DMS; all-details enumerates extracted tags. | [R31-S8](<#r31-s8>) |
| **Cancellable file operations**<br>`performance.cancel` | C | v0.7 changelog documents progress dialogs and cancellation for delete/move/copy/rename; album code shows progress callbacks as items complete. | [R31-S2](<#r31-s2>), [R31-S4](<#r31-s4>) |
| **Password and fingerprint gates**<br>`privacy.authentication_gates` | C | Configure password checks for hidden content/deletion and fingerprint unlock when Android M+ and hardware support it; password checks compare a stored SHA-256 hash. | [R31-S6](<#r31-s6>) |
| **Hide and unhide albums**<br>`privacy.hidden_folders` | C | Album action calls hide/unhide helpers, remembers hidden paths and exposes a separate hidden display mode; it is not evidence of encryption. | [R31-S4](<#r31-s4>) |
| **Deletion confirmation and optional authentication**<br>`safety.confirmation` | C | Single-media and album deletion require a confirmation dialog and optionally password/fingerprint authentication before invoking deletion. | [R31-S3](<#r31-s3>), [R31-S4](<#r31-s4>), [R31-S6](<#r31-s6>) |
| **Crop saves a separate file**<br>`safety.nondestructive_edits` | C | Successful crop output is copied from cache into the album and the UI reports a new file, rather than overwriting the source through this handler. | [R31-S3](<#r31-s3>) |
| **Image, video and GIF filters**<br>`search.file_type` | C | Grid exposes all-media, video-only, image-only and GIF-only modes. | [R31-S11](<#r31-s11>) |
| **Album search roadmap**<br>`search.filename_path` | R | Album search menu explicitly displays a coming-soon hint; inspected album handlers do not establish an implemented search workflow. | [R31-S12](<#r31-s12>), [R31-S4](<#r31-s4>) |
| **File-size sorting**<br>`sort.file_size` | C | Compare media byte sizes and reverse order as selected. | [R31-S10](<#r31-s10>) |
| **Path and natural-number sorting**<br>`sort.filename` | C | Sort by full path or numeric-aware file-version comparison, ascending or descending. | [R31-S10](<#r31-s10>) |
| **MIME sorting**<br>`sort.media_type` | C | Type sorting compares media MIME strings. | [R31-S10](<#r31-s10>) |
| **Modification-date sorting**<br>`sort.modified_date` | C | Date comparator uses getDateModified, even though a menu identifier contains date_taken; not claimed as EXIF capture-date sorting. | [R31-S10](<#r31-s10>), [R31-S11](<#r31-s11>) |

## Limitations and evidence gaps

- **explicit:** Unmaintained source and very old release; development-branch features are not guaranteed in the downloadable v0.6-beta-1 APK or on modern Android storage restrictions. ([R31-S1](<#r31-s1>), [R31-S2](<#r31-s2>), [R31-S17](<#r31-s17>))
- **explicit:** Date sorting is modification-based, while date repair is explicitly unfinished. Search is marked coming soon; affix availability is uncertain. ([R31-S3](<#r31-s3>), [R31-S10](<#r31-s10>), [R31-S11](<#r31-s11>), [R31-S12](<#r31-s12>))
- **explicit:** Map implementations request remote URLs containing coordinates, including legacy HTTP endpoints; no offline-map or provider availability guarantee is established. ([R31-S7](<#r31-s7>))
- **coverage-gap:** Password/fingerprint checks gate actions but do not establish encryption of originals. Media deletion invokes filesystem removal and MediaStore deletion; no recovery journal was established. ([R31-S5](<#r31-s5>), [R31-S6](<#r31-s6>))
- **coverage-gap:** No inspected evidence establishes cloud backup, duplicate analysis, face recognition, semantic search, collaborative albums, RAW decoding or comprehensive embedded-metadata writes. ([R31-S1](<#r31-s1>), [R31-S3](<#r31-s3>), [R31-S4](<#r31-s4>), [R31-S8](<#r31-s8>))
- **Coverage gap:** No substantive end-user manual in repository; complete source handlers and both changelogs were used.
- **Coverage gap:** Development-source implementation was not built or executed; hidden/unfinished actions are not counted as present.
- **Coverage gap:** No claim of encrypted hidden storage, internally decoded video codecs or current map endpoint availability.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R31-S1

[LeafPic README](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/README.md>)
- Kind/ref: readme; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete README
- Establishes: Android gallery, distribution links, ad-free claim and discontinued maintenance.

### R31-S2

[v0.7 changelog](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/CHANGELOG.md>)
- Kind/ref: release; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete changelog
- Establishes: Palette, fingerprint, affix, slideshow, print and cancellable file actions.

### R31-S3

[Single-media UI implementation](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/activities/SingleMediaActivity.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: onActivityResult, rotateImage, complete onOptionsItemSelected through file end; slideshow runnable and menu setup
- Establishes: Crop/save-copy, viewer rotation, file sharing, printing, slideshow, confirmation and unfinished date fix.

### R31-S4

[Album browsing and actions](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/fragments/AlbumsFragment.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete fragment
- Establishes: Folder-backed grids, background loading, sorting, pinning, exclusion, hide and delete controls.

### R31-S5

[Media filesystem operations](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/data/MediaHelper.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete helper
- Establishes: Move/copy/rename/delete originals and update MediaStore.

### R31-S6

[Password and fingerprint gates](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/util/Security.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete helper
- Establishes: Hidden/deletion settings, password hash check and supported Android fingerprint callback.

### R31-S7

[Static map provider URLs](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/util/StaticMapProvider.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete enum
- Establishes: Google, Mapbox and Tyler map requests embed media coordinates.

### R31-S8

[Metadata detail extraction](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/data/metadata/MetadataHelper.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete helper
- Establishes: File info, date taken, camera, EXIF, GPS and complete metadata-tag display.

### R31-S9

[Theme settings](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/settings/ColorsSetting.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete settings class
- Establishes: Light/dark/AMOLED themes and configurable palette.

### R31-S10

[Media sort semantics](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/data/sort/MediaComparators.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete comparators
- Establishes: Path, numeric path, modification date, file size and MIME sorting.

### R31-S11

[Media grid menu](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/res/menu/grid_media.xml>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete menu
- Establishes: Media-type filters and batch operations; affix and cover entries initially hidden.

### R31-S12

[Album menu](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/res/menu/grid_albums.xml>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete menu
- Establishes: Search marked coming soon and album actions.

### R31-S13

[Affix composite activity](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/activities/AffixActivity.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete activity
- Establishes: Two-image horizontal compositing and JPEG output, but integration availability uncertain.

### R31-S14

[Video preview and launch](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/fragments/VideoFragment.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete fragment
- Establishes: Cached thumbnail and Android ACTION_VIEW playback handoff.

### R31-S15

[GIF viewer](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/fragments/GifFragment.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete fragment
- Establishes: Dedicated GifImageView loads the local media URI.

### R31-S16

[Timeline grouping](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/java/org/horaapps/leafpic/timeline/GroupingMode.java>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete enum
- Establishes: Day/week/month/year grouping implementation.

### R31-S17

[Bundled v0.6-beta-1 notes](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/assets/latest_changelog.md>)
- Kind/ref: release; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Complete bundled changelog
- Establishes: Legacy zoom, video and startup fixes; distinguishes bundled version from root changelog.

### R31-S18

[French Android UI resources](<https://github.com/UnevenSoftware/LeafPic/blob/cfec78746776ed4bbccf9387bfc3f6ba1bb2c181/app/src/main/res/values-fr-rFR/strings.xml>)
- Kind/ref: code; cfec78746776ed4bbccf9387bfc3f6ba1bb2c181
- Sections inspected: Crowdin header, welcome/actions/filter/sort/share/rotation/file-operation strings, deletion dialogs and initial security/settings strings
- Establishes: Localized gallery actions and dialogs in Android locale resources.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
