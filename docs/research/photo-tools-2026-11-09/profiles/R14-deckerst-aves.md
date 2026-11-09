# R14 — deckerst/aves

[Repository](<https://github.com/deckerst/aves>) · 5,496 stars at the frozen snapshot · gallery-mobile · Not archived

**Purpose:** Android gallery and detailed metadata explorer with strong geospatial browsing, media-format inspection and Android/TV integration.

**Deployment:** Android and Android TV; Play, Izzy and Libre flavors through GitHub and their respective stores

**Storage:** Manages local device media with Android media permissions. Catalogue scanning derives media classifications. Vault items are app-private and can be lost when application data is cleared or the application uninstalled; a vault lock is not evidence of encryption.

**Privacy/network behavior:** Policy says the developer does not receive personal photos/videos. Optional consent-based installed-app inspection improves album display; Play flavor offers optional Firebase Crashlytics. Internet access is used for maps and reverse geocoding. Libre excludes Google Maps and Crashlytics.

**License metadata:** BSD-3-Clause. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v1.15.9 (2026-11-05T12:56:25Z)
**Repository pushed at:** 2026-11-08T17:54:17Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [17a25dae9837](<https://github.com/deckerst/aves/commit/17a25dae9837d5a27d328b9c7d12b2a0f76b4c26>).
**Product lineage:** deckerst/aves.

## Maturity and availability caveats

- Pinned develop commit 17a25dae9837d5a27d328b9c7d12b2a0f76b4c26; latest release v1.15.9 dated 2026-11-05.
- Unreleased credential-section changes are separated from released C2PA display; v1.15.9 removes BMP export and v1.14.7 removes the dead OSM Liberty map layer.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Geographic and tag statistics**<br>`analytics.library_statistics` | C | Stats show geolocated-item count and top countries, states, places, tags and albums. | [R14-S1](<#r14-s1>), [R14-S5](<#r14-s5>) |
| **Photo spheres and 360 video**<br>`browse.panorama` | C | Catalogues panoramas/photo spheres and 360-degree videos; released changelog also adds panorama audio playback. | [R14-S1](<#r14-s1>), [R14-S4](<#r14-s4>) |
| **Configurable slideshow**<br>`browse.slideshow` | C | UI settings include repeat, shuffle, fill-screen, animated zoom, transition, interval and video-playback behavior. | [R14-S5](<#r14-s5>) |
| **Slow-motion range control**<br>`browse.slow_motion_control` | C | v1.14.6 adds detection/filtering of slow-motion clips and range control in the player. | [R14-S4](<#r14-s4>) |
| **Calendar collection layout**<br>`browse.timeline` | C | v1.15.4 adds calendar layout and a collection layout bar; later versions support Persian and Hijri calendars. | [R14-S4](<#r14-s4>) |
| **Customizable touch controls**<br>`browse.touch` | C | Reorder browsing/selection quick actions; long-press tag quick action supports applying multiple tags; video gestures are separately configurable. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Configurable video player**<br>`browse.video_playback` | C | Supports videos including older AVI; UI exposes autoplay, looping, resumption, background playback and picture-in-picture, plus seek/play gestures and brightness/volume swipes. | [R14-S1](<#r14-s1>), [R14-S5](<#r14-s5>) |
| **Android/TV gallery**<br>`deployment.android` | C | Native Android application built with Flutter, including Android TV integration and media read/write permissions. | [R14-S1](<#r14-s1>) |
| **Translated Android interface**<br>`deployment.localization` | C | README identifies Weblate-powered app translations; inspected changelog explicitly adds Thai in v1.15.0, Urdu in v1.15.6 and Kurdish/Kurmanji in v1.14.6. These are application translations, not merely translated repository documentation; exhaustive language coverage is not claimed. | [R14-S1](<#r14-s1>), [R14-S4](<#r14-s4>) |
| **Image conversion**<br>`editing.format_conversion` | C | Convert/export exposes format, quality and width/height controls; v1.15.9 supports a single target dimension across mixed aspect ratios and removes BMP output. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Export dimension control**<br>`editing.resize` | C | Export controls width/height and supports mixed-aspect-ratio conversions by one target dimension. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Rotation and flip**<br>`editing.rotate_flip` | C | Clockwise/counterclockwise rotation and horizontal flip are explicit actions. | [R14-S5](<#r14-s5>) |
| **Burst pattern handling**<br>`library.burst_stacking` | C | Collection has configurable burst patterns; v1.15.6 adds Realme pattern recognition. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **GeoTIFF overlay**<br>`formats.geotiff` | C | Detects GeoTIFF and exposes Show as map overlay rather than merely treating georeferenced TIFF as an ordinary thumbnail. | [R14-S1](<#r14-s1>), [R14-S5](<#r14-s5>) |
| **Motion Photo inspection/actions**<br>`formats.motion_photos` | C | Detects Motion Photos and exposes still conversion, separate video opening and image-only/video-only sharing; rotation attempts to rotate the video component too. | [R14-S1](<#r14-s1>), [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Multipage TIFF**<br>`formats.multipage_tiff` | C | README specifically identifies multipage TIFF as supported media. | [R14-S1](<#r14-s1>) |
| **SVG display**<br>`formats.svg` | C | README explicitly supports SVG and v1.15.9 improves malformed SVG rendering. | [R14-S1](<#r14-s1>), [R14-S4](<#r14-s4>) |
| **Map browsing**<br>`geo.map` | C | Maps integrate with album/tag/location navigation. Google Maps depends on Google Mobile Services and is excluded from Libre; base-layer options include Humanitarian OSM and Stamen Watercolor. | [R14-S1](<#r14-s1>), [R14-S2](<#r14-s2>) |
| **Network reverse geocoding**<br>`geo.online_geocoding` | C | README explicitly attributes INTERNET permission to map viewing and reverse geocoding; offline geocoding is not claimed. | [R14-S1](<#r14-s1>) |
| **Map paths**<br>`geo.track_overlay` | C | v1.14.6 adds showing paths on the map; the changelog does not specify every track-import format for this overlay. | [R14-S4](<#r14-s4>) |
| **Android launcher, viewer and search integration**<br>`integration.android_components` | C | Provides launcher shortcuts and global search handling and can act as a media viewer for other Android apps; widget, picker and screensaver capabilities are recorded separately. | [R14-S1](<#r14-s1>) |
| **Android media picker**<br>`integration.android_picker` | C | README explicitly says Aves can serve as a media picker for Android applications, independently of opening media as a viewer; no cloud-provider or document-picker scope is inferred. | [R14-S1](<#r14-s1>) |
| **Clipboard and external application actions**<br>`integration.external_actions` | C | UI actions include copy to clipboard, open-with, set-as and opening coordinates in a map app; sharing and printing are recorded separately. | [R14-S5](<#r14-s5>) |
| **Android home-screen widgets**<br>`integration.home_widgets` | C | README explicitly lists widgets among Aves' Android integrations. Widget layout, refresh frequency and parity across Android/Android TV are not specified by this source. | [R14-S1](<#r14-s1>) |
| **Print media action**<br>`integration.print` | C | The Android media-action strings explicitly include Print. Printer compatibility, print-layout controls and platform-specific print-service behavior were not established by the inspected source. | [R14-S5](<#r14-s5>) |
| **Android screensaver integration**<br>`integration.screensaver` | C | README lists a screen saver among the application's Android integrations, alongside Android TV support. This establishes a screensaver function, not desktop wallpaper scheduling or a separate casting protocol. | [R14-S1](<#r14-s1>) |
| **Pattern-based rename**<br>`library.bulk_rename` | C | Multi-item rename offers a naming pattern, inserted counter/hash/name fields and a preview. | [R14-S5](<#r14-s5>) |
| **Local device media access**<br>`library.existing_folders` | C | Accesses/manages existing local photos/videos; Android 11+ uses MediaStore preferentially and requires Media Management permission for edits. | [R14-S1](<#r14-s1>), [R14-S3](<#r14-s3>), [R14-S4](<#r14-s4>) |
| **Local file relocation**<br>`library.move_copy` | C | Changelog documents moving files from app-media directories and rename/move handling on SD cards; these are ordinary file operations, not a catalogue-only action. | [R14-S4](<#r14-s4>) |
| **Opt-in crash diagnostics**<br>`maintenance.diagnostics` | O | Play version can send anonymous error/diagnostic data to Firebase Crashlytics with consent; Izzy and Libre omit this capability. | [R14-S2](<#r14-s2>), [R14-S3](<#r14-s3>) |
| **Automatic settings export**<br>`maintenance.settings_export` | C | v1.14.6 introduces automatic settings export; subsequent releases improve export failure feedback and storage-access handling. | [R14-S4](<#r14-s4>) |
| **Title and description editing**<br>`metadata.comments` | C | Info provides Edit title &amp; description; this establishes the edit affordance, not universal file-format write compatibility. | [R14-S5](<#r14-s5>) |
| **C2PA content credentials**<br>`metadata.content_credentials` | C | v1.15.9 displays credentials, overlays validity icons and filters unknown/invalid/valid/trusted states; removal of JPEG JUMBF credential metadata is supported. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Capture date correction**<br>`metadata.date_fix` | C | Set a custom date, shift timestamps, extract from filenames or copy another date field; v1.15.0 explicitly saves assigned undated-item dates to metadata. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Detailed embedded metadata explorer**<br>`metadata.exif_read` | C | Info displays embedded metadata including distinct Exif SubIFD sections; changelog notes handling large GIF XMP and metadata capture dates. | [R14-S1](<#r14-s1>), [R14-S4](<#r14-s4>) |
| **Export metadata**<br>`metadata.export` | C | Info exposes an Export metadata action; the exact serialization and sidecar interoperability are not established here. | [R14-S5](<#r14-s5>) |
| **Favorites**<br>`metadata.favorites` | C | Add/remove favorites actions and favorite filtering are exposed. | [R14-S5](<#r14-s5>) |
| **Location editing**<br>`metadata.gps_write` | C | Editor offers latitude/longitude, map selection, custom coordinates and removal of location. | [R14-S5](<#r14-s5>) |
| **GPX-based geotagging**<br>`metadata.gpx_sync` | C | Location editor includes Import GPX and time-shift controls for associating locations with timestamps. | [R14-S5](<#r14-s5>) |
| **Optional metadata on conversion**<br>`metadata.preserve_export` | C | Export dialog offers Write metadata along with format, dimension and quality controls. | [R14-S5](<#r14-s5>) |
| **Editable ratings**<br>`metadata.ratings` | C | Info offers a rating editor and collection badges; precise embedding formats are not established by the strings. | [R14-S5](<#r14-s5>) |
| **Selective metadata removal**<br>`metadata.strip` | C | Removal actions include all metadata or selected categories/location/JUMBF. UI warns removing Motion Photo XMP can prevent embedded video playback. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Editable tags and groups**<br>`metadata.tags` | C | Tag editing offers recent tags and country/state/place placeholders; tags and groups can be renamed directly. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Locked app-private vaults**<br>`privacy.app_private_vault` | C | Vaults support pattern/PIN/password and biometric unlock, with optional lock when the screen turns off. Warning states app uninstall/data-clear loses vault items; encryption at rest is not established by these sources. | [R14-S1](<#r14-s1>), [R14-S5](<#r14-s5>) |
| **Local photo management**<br>`privacy.no_upload_required` | C | Terms describe management of local media and state the developer never accesses photos/videos; map and opt-in diagnostics traffic are separate exceptions. | [R14-S3](<#r14-s3>), [R14-S1](<#r14-s1>) |
| **Recycle bin and restore**<br>`safety.app_recovery` | C | UI confirms moving items to the recycle bin and offers Restore; changelog addresses recovery when the original directory is inaccessible. It is not treated as a durable operation journal. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Special-media classification**<br>`search.file_type` | C | Filters distinguish images/videos, RAW, animations, Motion Photos, panoramas, slow motion, 360 video and GeoTIFF. | [R14-S1](<#r14-s1>), [R14-S5](<#r14-s5>) |
| **Country/state/place browsing**<br>`search.location` | C | Search facets cover countries, states, places and coordinates. Recent releases add state-level Brazil/Canada display and coordinate-center copying. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Metadata and missing-value facets**<br>`search.metadata` | C | Search includes metadata, dates and formats; filters identify undated, untitled, untagged, unrated and unlocated media, favorites and rejected ratings. | [R14-S5](<#r14-s5>) |
| **Rating filters**<br>`search.ratings` | C | Search contains ratings including unrated/rejected states; sorting by rating is also offered. | [R14-S5](<#r14-s5>) |
| **Tag and group navigation**<br>`search.tags` | C | Tags are searchable/navigable; tag/group renaming is documented and album/country/tag text filters accept slash-wrapped regular expressions. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Share media to other apps**<br>`sharing.system_share` | C | Android viewer exposes Share plus image-only and video-only sharing actions for supported compound media. These are app sharing affordances, not hosted public links or automatic publication to a social network. | [R14-S5](<#r14-s5>) |
| **Date ordering**<br>`sort.capture_date` | C | Date sorting is exposed; changelog specifically addresses mixed files with/without metadata dates. | [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>) |
| **Size ordering**<br>`sort.file_size` | C | Sort-by-size is an explicit user-interface option. | [R14-S5](<#r14-s5>) |
| **Name and path ordering**<br>`sort.filename` | C | Sort options include name, path and album plus item title. | [R14-S5](<#r14-s5>) |
| **Random collection order**<br>`sort.random` | C | Random sorting is added in v1.15.9. | [R14-S4](<#r14-s4>) |
| **Duration ordering**<br>`sort.video_duration` | C | Sort-by-duration is an explicit option, separate from video playback controls. | [R14-S5](<#r14-s5>) |

## Limitations and evidence gaps

- **explicit:** Vault media is lost if app data is cleared or the app uninstalled. No encryption guarantee follows merely from biometric/PIN access controls. ([R14-S5](<#r14-s5>))
- **explicit:** Google Maps requires Google Mobile Services and is unavailable in Libre; online map/geocoding access remains distinct from local gallery privacy. ([R14-S1](<#r14-s1>), [R14-S2](<#r14-s2>))
- **explicit:** BMP conversion and OSM Liberty map layer were removed in documented releases. ([R14-S4](<#r14-s4>))
- **coverage-gap:** Exact/perceptual duplicates, face recognition, cloud backup, multi-user sharing and universal RAW decoding/write-format coverage are not established in the inspected sources. ([R14-S1](<#r14-s1>), [R14-S4](<#r14-s4>), [R14-S5](<#r14-s5>))
- **Coverage gap:** No broad standalone end-user manual found; current interface text supplies medium-confidence detail where implementation was not traced.
- **Coverage gap:** Historical changelog outside the cited recent range was not exhaustively read; no unsupported legacy feature claims are imported.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R14-S1

[README](<https://github.com/deckerst/aves/blob/17a25dae9837d5a27d328b9c7d12b2a0f76b4c26/README.md>)
- Kind/ref: readme; 17a25dae9837d5a27d328b9c7d12b2a0f76b4c26
- Sections inspected: Entire README, features and permission table
- Establishes: Local gallery purpose, broad formats, geographic discovery and Android integrations.

### R14-S2

[App versions comparison](<https://github.com/deckerst/aves/wiki/App-Versions>)
- Kind/ref: manual; live-docs (page edited 2026-10-22)
- Sections inspected: Complete comparison and map-layer footnotes, read as raw wiki Markdown
- Establishes: Play/Izzy/Libre map, diagnostics and distribution differences.

### R14-S3

[Terms and privacy policy](<https://github.com/deckerst/aves/blob/17a25dae9837d5a27d328b9c7d12b2a0f76b4c26/assets/terms.md>)
- Kind/ref: manual; 17a25dae9837d5a27d328b9c7d12b2a0f76b4c26
- Sections inspected: Entire policy
- Establishes: Local media, consent-based diagnostics and inability to restore deleted unbacked-up originals.

### R14-S4

[Changelog](<https://github.com/deckerst/aves/blob/17a25dae9837d5a27d328b9c7d12b2a0f76b4c26/CHANGELOG.md>)
- Kind/ref: release; 17a25dae9837d5a27d328b9c7d12b2a0f76b4c26
- Sections inspected: Unreleased through complete v1.14.6 sections; beginning of v1.14.5
- Establishes: C2PA, calendar layout, map paths, slow-motion control, media permission changes and removed capabilities.

### R14-S5

[English user-interface actions and help](<https://github.com/deckerst/aves/blob/17a25dae9837d5a27d328b9c7d12b2a0f76b4c26/lib/l10n/app_en.arb>)
- Kind/ref: code; 17a25dae9837d5a27d328b9c7d12b2a0f76b4c26
- Sections inspected: Complete matching action, metadata editing, export, filter/search, sorting, stats, slideshow, vault and video settings key groups
- Establishes: Concrete user-facing actions, configurable behaviors and vault data-loss warning; labels establish UI affordances, not uninspected implementation guarantees.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
