# R22 — FossifyOrg/Gallery

[Repository](<https://github.com/FossifyOrg/Gallery>) · 3,904 stars at the frozen snapshot · gallery-mobile · Not archived

**Purpose:** Android local photo/video gallery with folder-oriented browsing, media playback, basic editing, privacy controls and a recoverable app recycle bin.

**Deployment:** Android app distributed through Google Play, F-Droid, IzzyOnDroid and GitHub releases

**Storage:** Browses device media and folders rather than requiring cloud import. Android MediaStore/scoped-storage permissions affect access; app keeps cached media, favorites/settings and an app-managed recycle bin. Saved edits can target a new file or overwrite with confirmation.

**Privacy/network behavior:** README advertises no ads and user-controlled EXIF removal and PIN/pattern/fingerprint access protection. Hidden folders use .nomedia and exclusions affect only this app; neither is encryption. FAQ says clearing app data resets the password without removing media, so app lock must not be represented as an encrypted vault.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 1.14.2 (2026-11-07T16:09:55Z)
**Repository pushed at:** 2026-11-07T16:09:55Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [268836024246](<https://github.com/FossifyOrg/Gallery/commit/2688360242468f1d591eddf23740c879616bb828>).
**Product lineage:** Simple-Gallery-Fossify.

## Maturity and availability caveats

- Manifest release 1.14.2 (2026-11-07), pinned main 2688360242468f1d591eddf23740c879616bb828; release notes are translation updates.
- Some retained strings mention Pro/advanced editor and older Android limitations; they are not evidence of a current paid edition. Current behavior is qualified with permission-dependent paths.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Folder navigation and pinning**<br>`browse.folders` | C | Folder or all-content views, grouped direct subfolders, pinned/default folders and custom drag order are documented. | [R22-S2](<#r22-s2>), [R22-S4](<#r22-s4>) |
| **Configurable fullscreen viewing**<br>`browse.fullscreen` | C | Options include hidden system UI, black background, brightness, keep-screen-on, extended details and configurable bottom actions. | [R22-S2](<#r22-s2>) |
| **Configurable thumbnails and list view**<br>`browse.grid` | C | Grid/list layout with configurable column count, horizontal/vertical scrolling, square/rounded thumbnails, spacing, filenames and folder counts. | [R22-S2](<#r22-s2>), [R22-S5](<#r22-s5>) |
| **Mixed-media slideshows**<br>`browse.slideshow` | C | Choose interval, photos/videos/GIF inclusion, random or reverse order, loop and none/fade/slide animation. | [R22-S2](<#r22-s2>) |
| **Custom colors, themes and controls**<br>`browse.theme_customization` | C | Dynamic Material themes and custom themes, launcher colors, bottom action visibility and thumbnail styling are documented. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>), [R22-S3](<#r22-s3>) |
| **Date-grouped media**<br>`browse.timeline` | C | Group by capture date or last modification daily/monthly; also by folder, media type or extension. Grouping and sorting are independent. | [R22-S2](<#r22-s2>) |
| **Touch navigation and media gestures**<br>`browse.touch` | C | Side taps change media, down gesture closes viewer, vertical gestures adjust photo brightness or video volume/brightness, and video supports horizontal seeking. | [R22-S2](<#r22-s2>) |
| **Built-in or external video player**<br>`browse.video_playback` | C | Select in-app/default player; autoplay, looping, remembered position, playback speed, seek gestures and durations are exposed. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>), [R22-S5](<#r22-s5>) |
| **Deep and gesture zoom**<br>`browse.zoom` | C | Settings offer deep zoom/highest quality, one-finger zoom, two-double-tap 1:1 zoom and video double-tap zoom. | [R22-S2](<#r22-s2>) |
| **Native Android gallery**<br>`deployment.android` | C | Distributed through Android stores/repos and GitHub; registers as image/video viewer, picker and editor. | [R22-S1](<#r22-s1>), [R22-S3](<#r22-s3>) |
| **Translated Android interface**<br>`deployment.localization` | C | Release 1.14.2 explicitly updates translations, and the Android app manifest enables right-to-left layout support. The inspected sources establish localized UI but do not provide a verified complete language/completeness matrix. | [R22-S9](<#r22-s9>), [R22-S3](<#r22-s3>) |
| **Crop with aspect ratios**<br>`editing.crop` | C | Basic editor crops by dragging corners and supports fixed/free/custom aspect ratios. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>) |
| **Drawing and filters**<br>`editing.draw_filters` | C | README explicitly includes drawing and image filters in the basic editor; no professional RAW processing is implied. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>) |
| **Single/batch resizing**<br>`editing.resize` | C | Resize dimensions with aspect-ratio lock or batch scale factor between 10% and 90%; settings also advertise sharing a resized version. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>) |
| **Rotate and flip**<br>`editing.rotate_flip` | C | Editor offers horizontal/vertical flips; media selection routes support 90/180/270-degree rotations. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>), [R22-S6](<#r22-s6>) |
| **Animated GIF browsing**<br>`formats.animated` | C | GIF filter, animated thumbnails and GIF inclusion in slideshows are user options. | [R22-S2](<#r22-s2>) |
| **AVIF images**<br>`formats.avif` | C | AVIF is explicitly listed among supported formats. | [R22-S1](<#r22-s1>) |
| **JPEG XL images**<br>`formats.jpegxl` | C | README explicitly supports JPEG XL and manifest registers .jxl content handling. | [R22-S1](<#r22-s1>), [R22-S3](<#r22-s3>) |
| **RAW image viewing**<br>`formats.raw` | C | README lists RAW and UI has a RAW filter; camera-specific decoding coverage is not enumerated. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>) |
| **SVG viewing/filter**<br>`formats.svg` | C | SVG is listed in README and filter UI. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>) |
| **Ultra HDR rendering option**<br>`formats.hdr` | C | In-app setting explicitly enables showing Ultra HDR photos in HDR; device/version support is not fully specified by this source. | [R22-S2](<#r22-s2>) |
| **System viewer/editor/picker integration**<br>`integration.android_picker` | C | Manifest registers PICK/GET_CONTENT for image/video, VIEW, photo EDIT/CROP and camera review intents. | [R22-S3](<#r22-s3>) |
| **Share selected media to apps**<br>`integration.android_share` | C | Single and multiple selections route through Android media-sharing helpers; not a hosted public-link service. | [R22-S6](<#r22-s6>) |
| **Configurable home-screen folder widget**<br>`integration.home_widgets` | C | Widget settings select the displayed folder and whether to show its name; manifest registers the widget configuration activity and app-widget provider. | [R22-S2](<#r22-s2>), [R22-S3](<#r22-s3>) |
| **Set device wallpaper**<br>`integration.wallpaper` | C | Set a photo as home-screen, lock-screen or both wallpapers, with aspect-ratio controls; manifest registers wallpaper activities and SET_WALLPAPER permission. | [R22-S2](<#r22-s2>), [R22-S3](<#r22-s3>) |
| **Single and multiple file rename**<br>`library.bulk_rename` | C | One selected item uses RenameItemDialog; multiple items use RenameDialog. Android 11 SD/OTG root rename needs all-files access. | [R22-S6](<#r22-s6>) |
| **Browse existing device media**<br>`library.existing_folders` | C | Reads device folders/MediaStore with manual inclusion for missing folders; permissions and Android version restrict hidden/path access. | [R22-S2](<#r22-s2>), [R22-S3](<#r22-s3>) |
| **Copy/move selected media**<br>`library.move_copy` | C | Invokes file destination workflow, rescans source/destination, fixes date values and updates favorite paths on moves; moving directly from recycle-bin paths is blocked. | [R22-S6](<#r22-s6>) |
| **Repair Date Taken values**<br>`metadata.date_fix` | C | Selected-media action repairs Date Taken used for ordering, especially after copying; source calls fixDateTaken rather than establishing arbitrary EXIF timestamp editing. | [R22-S2](<#r22-s2>), [R22-S6](<#r22-s6>) |
| **Export/import favorites**<br>`metadata.favorite_paths_transfer` | C | Settings expose favorite path import/export; export selects a .txt destination and confirms overwriting an existing file. This is not a full database/photo backup. | [R22-S2](<#r22-s2>), [R22-S8](<#r22-s8>) |
| **Favorites across paths**<br>`metadata.favorites` | C | Batch add/remove favorites, display favorite marks and maintain favorite paths after moving files. | [R22-S2](<#r22-s2>), [R22-S6](<#r22-s6>) |
| **Remove EXIF metadata**<br>`metadata.strip` | C | README explicitly offers stripping sensitive EXIF including GPS and camera details; exact field-by-field scope is not documented. | [R22-S1](<#r22-s1>) |
| **Cached results before refresh**<br>`performance.live_browsing` | C | Search loads cached media into its adapter before starting asynchronous media fetch and stops the current fetch when destroyed/replaced. | [R22-S5](<#r22-s5>) |
| **Local image cache**<br>`performance.thumbnail_cache` | C | FAQ documents up to 250 MB app cache for quicker image loading, separately from recycle-bin storage. | [R22-S2](<#r22-s2>) |
| **PIN/pattern/fingerprint access protection**<br>`privacy.app_lock` | C | README advertises locking media or app; FAQ permits reset via reinstall/clear data without media removal, so not an encrypted vault guarantee. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>) |
| **Hide versus exclude folders**<br>`privacy.hidden_folders` | C | Hide recursively creates .nomedia affecting other galleries; Exclude hides only within Fossify. Included folders override recursive exclusions; Android permissions can restrict both. | [R22-S2](<#r22-s2>) |
| **App recycle bin**<br>`safety.app_recovery` | C | Deleted photos/videos can be restored. FAQ says bin contents count toward app storage and automatically expire after 30 days; deletion can explicitly bypass bin. | [R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>), [R22-S5](<#r22-s5>), [R22-S6](<#r22-s6>) |
| **Deletion review and optional password**<br>`safety.confirmation` | C | Delete dialog shows item count/size and bin-versus-permanent action; user can remember skip-confirmation or bypass bin. Password-protected deletion is a separate path. | [R22-S6](<#r22-s6>) |
| **Save-as collision confirmation**<br>`safety.no_overwrite` | C | SaveAsDialog calls ensureWritablePath with confirmOverwrite=true; favorite-text export also explicitly prompts on collision. | [R22-S7](<#r22-s7>), [R22-S8](<#r22-s8>) |
| **Save edited output separately**<br>`safety.nondestructive_edits` | C | Save-as dialog chooses directory, basename and extension, optionally adds _1, validates names and asks before overwrite. Also exposes overwrite-original option, so edits are not universally nondestructive. | [R22-S2](<#r22-s2>), [R22-S7](<#r22-s7>) |
| **Media category filters**<br>`search.file_type` | C | Filters include images, videos, GIFs, RAW, SVG and portraits. | [R22-S2](<#r22-s2>) |
| **Cross-folder filename search**<br>`search.filename_path` | C | SearchActivity performs case-insensitive name containment across fetched visible media and prioritizes names starting with the query; not semantic or metadata search. | [R22-S5](<#r22-s5>) |
| **Capture/modification date sort**<br>`sort.capture_date` | C | Sort by Date Taken or last modified independently of grouping, with ascending/descending and folder-specific settings. | [R22-S4](<#r22-s4>) |
| **Sort by file size**<br>`sort.file_size` | C | Size ordering appears alongside filename, dates, random, folder count and custom folder order. | [R22-S4](<#r22-s4>) |
| **Name/path sorting with numeric option**<br>`sort.filename` | C | Sort by name or full path, optionally numeric/natural value, ascending/descending; preferences can be global or per-folder. | [R22-S4](<#r22-s4>) |

## Limitations and evidence gaps

- **explicit:** Android 11+ scoped storage limits hidden files/folders and some rename/include actions; all-files/media-management permissions enable broader operation, and some system folders cannot be hidden. ([R22-S2](<#r22-s2>), [R22-S3](<#r22-s3>), [R22-S6](<#r22-s6>))
- **explicit:** App password can be reset by clearing app data/reinstalling without removing media; .nomedia hiding and in-app exclusion are not encryption. ([R22-S2](<#r22-s2>))
- **explicit:** Recycle-bin items auto-delete after 30 days and may be bypassed; save/edit operations can overwrite originals with confirmation. ([R22-S2](<#r22-s2>), [R22-S6](<#r22-s6>), [R22-S7](<#r22-s7>))
- **coverage-gap:** AI recognition, duplicate matching, embedded map/offline tiles, cloud backup, durable operation journal and encrypted vault were not established. A Show on map label alone does not establish an integrated map. ([R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>))
- **coverage-gap:** Format support depends on actual media/device capability; README's broad format claims are not a tested codec matrix. Retained Pro strings do not establish paid functionality. ([R22-S1](<#r22-s1>), [R22-S2](<#r22-s2>))
- **Coverage gap:** Used in-app FAQ/settings as primary manual; source-backed settings-only capabilities carry limited device guarantees.
- **Coverage gap:** No merged-manifest/network audit or device tests; no absolute air-gap claim.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R22-S1

[Gallery README](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/README.md>)
- Kind/ref: readme; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Complete privacy, editing, protection, recovery, formats and customization overview
- Establishes: Core app scope and explicit feature claims.

### R22-S2

[In-app settings and complete FAQ](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/app/src/main/res/values/strings.xml>)
- Kind/ref: manual; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Complete English strings including filter/hide/include/editor/slideshow/settings and FAQ sections
- Establishes: User-facing documentation of grouping, playback, permissions, cache, recycle-bin retention and locks.

### R22-S3

[Android integration and permissions](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/app/src/main/AndroidManifest.xml>)
- Kind/ref: code; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Complete manifest; media permissions, viewer/editor/picker intents, wallpaper and widget components
- Establishes: Device access and integration surfaces; not a merged-dependency/network audit.

### R22-S4

[Sorting controls](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/app/src/main/kotlin/org/fossify/gallery/dialogs/ChangeSortingDialog.kt>)
- Kind/ref: code; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Complete class
- Establishes: Name/path/size/date/count/random/custom sorting and per-folder preferences.

### R22-S5

[Search and delete workflow](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/app/src/main/kotlin/org/fossify/gallery/activities/SearchActivity.kt>)
- Kind/ref: code; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Complete class
- Establishes: Case-insensitive filename search, cached/background loading, list/grid and recycle-bin path.

### R22-S6

[Selected-media operations](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/app/src/main/kotlin/org/fossify/gallery/adapters/MediaAdapter.kt>)
- Kind/ref: code; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Action routing/index; properties/rename 278-322; hide/favorite/restore/share 366-416; move/copy 451-496; date-fix/delete 523-619
- Establishes: Batch rename/copy/move, favorites, share, permissions and destructive confirmation.

### R22-S7

[Save-as dialog](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/app/src/main/kotlin/org/fossify/gallery/dialogs/SaveAsDialog.kt>)
- Kind/ref: code; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Complete class
- Establishes: Destination/name selection, validation and explicit overwrite confirmation.

### R22-S8

[Favorite paths export](<https://github.com/FossifyOrg/Gallery/blob/2688360242468f1d591eddf23740c879616bb828/app/src/main/kotlin/org/fossify/gallery/dialogs/ExportFavoritesDialog.kt>)
- Kind/ref: code; 2688360242468f1d591eddf23740c879616bb828
- Sections inspected: Complete class
- Establishes: Text export destination and overwrite handling, complemented by import/export UI labels.

### R22-S9

[Release 1.14.2](<https://github.com/FossifyOrg/Gallery/releases/tag/1.14.2>)
- Kind/ref: release; 1.14.2
- Sections inspected: Complete release note
- Establishes: Translation update in manifest's latest release.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
