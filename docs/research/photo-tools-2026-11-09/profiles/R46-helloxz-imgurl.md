# R46 — helloxz/imgurl

[Repository](<https://github.com/helloxz/imgurl>) · 1,753 stars at the frozen snapshot · gallery-sharing · Archived

**Purpose:** Legacy PHP/SQLite image host with guest uploads, direct/embed links, thumbnails, public discovery and optional externally processed compression/moderation.

**Deployment:** Self-hosted PHP web application; PHP &gt;=5.6 with PDO_SQLite, GD2, ImageMagick, fileinfo and pathinfo as documented

**Storage:** Local files and thumbnails are placed under year/month image directories; SQLite records retain upload and image details. Image identifiers use a 16-character slice of an MD5 digest. Deletion directly removes database records, originals and thumbnails.

**Privacy/network behavior:** Local hosting is available but guest content is surfaced through discovery and public file URLs. Upload records store IP/user agent. Optional TinyPNG sends image bytes externally; ModerateContent receives a retrievable image URL. Authentication does not imply private albums or encryption.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v2.31 (2019-09-02T11:49:51Z)
**Repository pushed at:** 2022-02-18T02:43:47Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [b1f1b930e586](<https://github.com/helloxz/imgurl/commit/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58>).
**Product lineage:** helloxz/imgurl.

## Maturity and availability caveats

- Manifest identifies archived/discontinued repository and directs new deployments to Zpic; frozen master b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58.
- Latest manifest release v2.31 is dated 2019-09-02; source was last pushed in 2022.
- README advertises a separate ImgURL Pro edition. Its storage/MySQL/support claims are not attributed to this free repository.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Optional external content review**<br>`ai.content_moderation` | O | ModerateContent classifies a public image URL and stores the rating; already classified images are skipped, and batch helper selects up to five unknown entries. This is not local inference or face recognition. | [R46-S1](<#r46-s1>), [R46-S3](<#r46-s3>) |
| **Per-image viewing statistics**<br>`analytics.image_views` | C | Detail page displays stored view count and discovery offers a views category. | [R46-S6](<#r46-s6>), [R46-S7](<#r46-s7>) |
| **Paged gallery and administration**<br>`browse.pagination` | C | Uses 16-image pages; public discovery caps the pagination count at 160 entries, while management has its own filters and count. | [R46-S5](<#r46-s5>), [R46-S6](<#r46-s6>) |
| **Public discovery categories**<br>`browse.public_gallery` | C | Discovery controller provides all, GIF, views and large-image categories; category query semantics beyond those labels are not inferred. | [R46-S6](<#r46-s6>) |
| **Local PHP/SQLite hosting**<br>`deployment.selfhosted` | C | Host the site on a PHP server using SQLite 3 rather than the separate Pro edition's MySQL option. | [R46-S1](<#r46-s1>) |
| **Web upload and administration**<br>`deployment.web` | C | Browser upload, image detail, discovery and authenticated management pages are built in. | [R46-S1](<#r46-s1>), [R46-S5](<#r46-s5>), [R46-S6](<#r46-s6>), [R46-S7](<#r46-s7>) |
| **Image cropping**<br>`editing.crop` | C | README explicitly lists image cropping alongside automatic thumbnail generation; crop variants and metadata preservation are not specified there. | [R46-S1](<#r46-s1>) |
| **Single/batch TinyPNG compression**<br>`editing.remote_compression` | O | README lists batch compression; configured TinyPNG processing accepts JPEG/PNG, skips previously compressed records and overwrites the local original with downloaded output. Multiple configured API keys can be selected. | [R46-S1](<#r46-s1>), [R46-S3](<#r46-s3>) |
| **Web image upload formats**<br>`formats.web_images` | C | Multipart allowlist includes GIF, JPG/JPEG, PNG, BMP and WebP. This evidence does not establish RAW or video playback. | [R46-S2](<#r46-s2>) |
| **Upload and gallery JSON APIs**<br>`integration.api` | C | Multipart upload returns IDs, paths, URL, thumbnail, dimensions and for newly inserted files a deletion URL; discovery API serializes gallery records. | [R46-S2](<#r46-s2>), [R46-S11](<#r46-s11>) |
| **Free-edition external storage roadmap**<br>`integration.external_storage` | R | Free README leaves external storage unchecked and free navigation only activates localhost. Pro's advertised support is separately classified. | [R46-S1](<#r46-s1>), [R46-S9](<#r46-s9>) |
| **Pro external storage and MySQL**<br>`integration.pro_external_storage` | $ | README advertises multiple external storage backends, MySQL, no advertising and professional support in separate ImgURL Pro; these are not verified free-source features. | [R46-S1](<#r46-s1>) |
| **Year/month upload layout**<br>`library.auto_date_folders` | C | Original and thumbnail paths are created below imgs/YYYY/MM using generated digest-derived filenames. | [R46-S2](<#r46-s2>) |
| **Batch and drag-and-drop upload**<br>`library.batch_upload` | C | README lists multi-image selection and drag-and-drop as current features. | [R46-S1](<#r46-s1>) |
| **Clipboard image upload**<br>`library.clipboard_upload` | C | Ctrl+V workflow sends base64 image content; parse endpoint validates MIME before storing it. | [R46-S1](<#r46-s1>), [R46-S2](<#r46-s2>) |
| **Hash-derived duplicate upload handling**<br>`library.deduplicate_import` | C | Uses a truncated MD5 as image ID. URL/paste duplicates are rejected; multipart upload reuses the known record ID after writing/renaming the upload, so this is not guaranteed disk-level deduplication. | [R46-S2](<#r46-s2>) |
| **Remote URL image import**<br>`library.url_import` | C | Logged-in users can fetch supported image URLs; URL handler checks an image extension and rejects an already known digest-derived ID. | [R46-S2](<#r46-s2>) |
| **Online updating availability**<br>`maintenance.online_update` | ? | README marks online update unfinished, but source navigation exposes a version-upgrade page. Its completeness was not established; not counted as present. | [R46-S1](<#r46-s1>), [R46-S9](<#r46-s9>) |
| **Upload provenance records**<br>`maintenance.upload_audit` | C | Stores uploader IP, user agent, date, admin/visitor type, original client filename and moderation status. | [R46-S2](<#r46-s2>) |
| **Technical image detail display**<br>`metadata.technical_details` | C | Image page lists dimensions, MIME, extension, upload time, file size and view count; EXIF capture metadata editing is not established. | [R46-S7](<#r46-s7>) |
| **Generated preview images**<br>`performance.thumbnail_cache` | C | Upload creates a 290×175 thumbnail where appropriate; small images can use the original URL instead. | [R46-S2](<#r46-s2>) |
| **Upload-date administration filter**<br>`search.date_range` | C | Management accepts a start/end date and applies it to upload timestamps, separately for all, administrator or visitor records—not EXIF capture dates. | [R46-S5](<#r46-s5>) |
| **Find uploads by ID or IP**<br>`search.upload_identifiers` | C | Management can query numeric ID, 16-character image ID or uploading IP, and filter suspicious/adult-classified records. | [R46-S5](<#r46-s5>) |
| **Custom comment embedding**<br>`sharing.comment_embed` | O | Image view includes a comment.html file if present; this is an integration hook, not evidence of a built-in comment database. | [R46-S7](<#r46-s7>) |
| **Delete by private token link**<br>`sharing.deletion_capability_links` | C | A valid deletion token authorizes removal without logging in; separate ID-based deletion requires login and both remove original, thumbnail and database entries. | [R46-S2](<#r46-s2>), [R46-S4](<#r46-s4>) |
| **Guest upload switch**<br>`sharing.guest_upload` | C | Admin settings enable/disable visitor uploads; uploads distinguish administrator versus visitor records. | [R46-S2](<#r46-s2>), [R46-S8](<#r46-s8>) |
| **Direct and embed link output**<br>`sharing.public_links` | C | UI/API can return URL, HTML, Markdown and BBCode; detail view exposes copy controls and direct download. | [R46-S2](<#r46-s2>), [R46-S7](<#r46-s7>) |
| **Visitor daily quota and maximum size**<br>`sharing.upload_quotas` | C | Configure guest daily upload count and backend file-size limit; upload constructor checks visitor IP quota. v2.31 fixes the size-setting bug. | [R46-S2](<#r46-s2>), [R46-S8](<#r46-s8>), [R46-S10](<#r46-s10>) |

## Limitations and evidence gaps

- **coverage-gap:** Focused localization review found no explicit multiple-language UI in the inspected README or image-host views/controllers. Framework language helpers are not evidence that the ImgURL user interface itself is localized. ([R46-S1](<#r46-s1>), [R46-S7](<#r46-s7>), [R46-S8](<#r46-s8>), [R46-S9](<#r46-s9>))
- **explicit:** WebP uploads explicitly record width/height as zero in the inspected handler; URL import's extension switch is narrower than multipart's WebP-capable allowlist. ([R46-S2](<#r46-s2>))
- **explicit:** Compression overwrites originals and deletion unlinks original/thumbnail files directly; no recycle/recovery layer is present in those inspected operations. ([R46-S3](<#r46-s3>), [R46-S4](<#r46-s4>))
- **explicit:** Digest-derived ID reuse is not proof of byte equality, and multipart duplicate detection occurs after files have been written; storage deduplication guarantees cannot be inferred. ([R46-S2](<#r46-s2>))
- **explicit:** Free external storage remains a roadmap checkbox, not the paid edition's available integration. Public discovery exposes only a bounded navigation window, not a complete large-library catalogue. ([R46-S1](<#r46-s1>), [R46-S6](<#r46-s6>), [R46-S9](<#r46-s9>))
- **coverage-gap:** No inspected evidence establishes face/semantic search, EXIF editing, maps, collaborative albums, private per-user libraries, encrypted storage or reversible operation history. ([R46-S1](<#r46-s1>), [R46-S2](<#r46-s2>), [R46-S5](<#r46-s5>), [R46-S7](<#r46-s7>))
- **Coverage gap:** No dedicated pinned manual exists in the source tree; multiple complete implementation files replace reliance on old external documentation.
- **Coverage gap:** Paid Pro announcement is documented separately, not audited as an available free feature.
- **Coverage gap:** External service availability and legacy PHP deployment compatibility were not runtime-tested.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R46-S1

[ImgURL README](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/README.md>)
- Kind/ref: readme; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete README including feature checklist and Pro announcement
- Establishes: Free scope, dependencies, upload workflows, planned items and separate paid edition.

### R46-S2

[Upload controller](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/controllers/Upload.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete controller: config, localhost, URL, paste, response and token methods
- Establishes: Storage layout, format limits, hash-derived IDs, API responses, logging and guest constraints.

### R46-S3

[Compression and moderation controller](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/controllers/Deal.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete controller, especially compress, identify and identify_more
- Establishes: Third-party processing, JPEG/PNG limits, result state and original replacement.

### R46-S4

[Deletion controller](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/controllers/Del.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete id/token deletion methods
- Establishes: Authenticated deletion or possession of deletion token; direct disk/database removal.

### R46-S5

[Administration controller](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/controllers/Manage.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete images and imginfo methods
- Establishes: Admin/guest/moderation filters, ID/IP/date search and pagination.

### R46-S6

[Public discovery controller](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/controllers/Found.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete controller
- Establishes: Public all/GIF/views/large categories, page size and capped navigation count.

### R46-S7

[Image detail page](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/views/user/img.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete view
- Establishes: Download, embed formats, technical metadata, view counts and optional comment insertion.

### R46-S8

[Upload quota settings](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/views/admin/uplimit.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete settings form
- Establishes: Guest switch, daily count and file size.

### R46-S9

[Administrative navigation](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/views/admin/left.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete navigation
- Establishes: Local storage is active; external storage entries are commented out; upgrade navigation exists.

### R46-S10

[v2.31 release](<https://github.com/helloxz/imgurl/releases/tag/v2.31>)
- Kind/ref: release; v2.31
- Sections inspected: Complete two-item release notes
- Establishes: Menu improvements and corrected upload-size setting.

### R46-S11

[Discovery API](<https://github.com/helloxz/imgurl/blob/b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58/application/controllers/Api.php>)
- Kind/ref: code; b1f1b930e5860c2c1ce8e6d0e425b0ca79491d58
- Sections inspected: Complete found method
- Establishes: JSON gallery-data endpoint with cross-origin access.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
