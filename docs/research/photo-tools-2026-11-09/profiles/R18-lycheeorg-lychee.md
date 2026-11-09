# R18 — LycheeOrg/Lychee

[Repository](<https://github.com/LycheeOrg/Lychee>) · 4,328 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Self-hosted multiuser photo gallery with albums, fine-grained sharing, server import/sync and optional processing services; free, Supporter and Pro capabilities differ substantially.

**Deployment:** Self-hosted PHP web application; Recommended Docker deployment with optional separate workers; Prebuilt releases or source installation

**Storage:** Database catalogue plus original files and configurable generated size variants; default images disk is local public/uploads, with configurable S3 storage. RAW conversion preserves the native source alongside display JPEG where supported. Current docs describe opt-in embedded metadata changes, so originals are not unconditionally immutable.

**Privacy/network behavior:** Can use an operator-controlled server; self-hosting is not E2EE. Album access, download and full-original grants are distinct. Default storage configuration includes public visibility, so generic architecture prose claiming all originals are outside web root is not a guarantee. Optional face processing uses a separate self-hosted service with read-only shared photos and local embeddings, but downloads models initially; map/offsite-import and license services introduce external dependencies.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v7.13.0 (2026-11-09T01:16:04Z)
**Repository pushed at:** 2026-11-08T22:50:23Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [ba1e7ef62b03](<https://github.com/LycheeOrg/Lychee/commit/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d>).
**Product lineage:** Lychee.

## Maturity and availability caveats

- Frozen commit ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d and latest release v7.13.0 (2026-11-09).
- Current source/docs mix v7 and gated v8 development. Release notes explicitly label some additions v8. This inventory distinguishes implemented documented baseline from ambiguous upcoming modules.
- Supporter Edition unlocks paid capabilities; Pro adds webshop functionality. Same MIT source license does not make all runtime edition gates free.
- Facial recognition marketing, comparison table and how-to disagree on timing and edition: card says Free, table says Soon v8, how-to says SE settings. Face functionality is therefore recorded unclear rather than assumed released/free.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **DBSCAN face grouping**<br>`ai.face_clustering` | ? | How-to describes DBSCAN cosine-distance grouping of stored embeddings, noise labels and reviewable clusters; shares unresolved v8/edition availability. | [R18-S3](<#r18-s3>), [R18-S8](<#r18-s8>) |
| **Face assignment and maintenance**<br>`ai.face_corrections` | ? | Documented workflows assign/merge people, destroy dismissed faces/embeddings, reset failed/stuck scans and synchronize embedding stores. Four permission modes range from public to restricted. | [R18-S8](<#r18-s8>) |
| **Optional sidecar face detection**<br>`ai.face_detection` | ? | Concrete setup guide describes Python sidecar, queue worker, detection/size/blur thresholds and bounding-box overlays, but live table marks Soon v8 and edition claims conflict. Not counted as generally released. | [R18-S3](<#r18-s3>), [R18-S8](<#r18-s8>), [R18-S12](<#r18-s12>) |
| **Person matching and selfie claim**<br>`ai.face_recognition` | ? | How-to describes person profiles, similarity thresholds and selfie-based profile claims. Requires configured sidecar/model; exact current released entitlement remains contradictory. | [R18-S3](<#r18-s3>), [R18-S8](<#r18-s8>) |
| **Self-hosted face inference architecture**<br>`ai.local_inference` | ? | Configured face service reads a shared read-only photo volume, stores SQLite/pgvector embeddings and downloads a model initially; publication/edition ambiguity remains, and this is not fully air-gapped setup. | [R18-S3](<#r18-s3>), [R18-S8](<#r18-s8>) |
| **Sensitive-content detection**<br>`ai.sensitive_content_detection` | R | Comparison table explicitly labels sensitive-content detection Soon v8 and SE-only; existing manual sensitive-album flagging is separate. | [R18-S3](<#r18-s3>) |
| **Multi-album photo organization**<br>`albums.manual` | C | A photo can belong to multiple regular albums without duplicating files; album title, description, cover, header, sorting and layout can be customized. | [R18-S3](<#r18-s3>), [R18-S4](<#r18-s4>), [R18-S5](<#r18-s5>) |
| **On This Day collection**<br>`browse.memories` | C | Built-in smart collection selects capture dates matching today's month/day in earlier years, subject to permissions. | [R18-S4](<#r18-s4>) |
| **Nested album trees**<br>`albums.nested` | C | Regular albums contain photos and child albums with subtree operations; tag and system smart albums are flat. | [R18-S4](<#r18-s4>) |
| **Tag-driven and system smart albums**<br>`albums.smart` | C | User-defined tag albums dynamically match tag combinations and are shareable; system albums include Recent, Highlighted, Public, Unsorted and On This Day. Arbitrary custom system-smart queries are not supported by this model. | [R18-S4](<#r18-s4>) |
| **Library and usage analytics**<br>`analytics.library_statistics` | $ | SE adds installation/library/photo/album statistics including downloads and shares; API v3 Insights also has an SE gate. | [R18-S3](<#r18-s3>), [R18-S12](<#r18-s12>) |
| **Report storage usage per user**<br>`analytics.user_storage_usage` | $ | Edition matrix separately lists per-user space usage for SE; reporting consumed storage is distinct from enforcing the account-capacity quota. | [R18-S3](<#r18-s3>) |
| **Album feed and frame display**<br>`browse.album_feed` | C | Flow page presents albums as a feed with access control and configurable base album; separate frame-display module is included free. Compact/extensively customized flow cards are SE. | [R18-S3](<#r18-s3>) |
| **Show tags on album view**<br>`browse.album_tag_display` | $ | Edition comparison gates displaying tags directly on the album view to SE, despite free tag assignment, listing and tag-album creation. | [R18-S3](<#r18-s3>) |
| **Dark and light themes**<br>`browse.dark_theme` | C | Both themes and multilingual UI are free edition features. | [R18-S3](<#r18-s3>) |
| **Customize album feed cards**<br>`browse.flow_card_customization` | $ | SE separately provides compact Flow cards and extensive card customization; the basic access-controlled feed is free. | [R18-S3](<#r18-s3>) |
| **Opt-in versus automatic feed strategy**<br>`browse.flow_strategy` | R | Edition table explicitly labels custom Flow inclusion strategy Soon and SE rather than an already available core feature. | [R18-S3](<#r18-s3>) |
| **Fullscreen viewing**<br>`browse.fullscreen` | C | Official overview documents full-screen images and forward/backward keyboard navigation. | [R18-S2](<#r18-s2>) |
| **Configurable gallery layouts**<br>`browse.grid` | C | Justified, masonry and square layouts, album cover/header controls and customizable album thumbnail aspect ratio are free. | [R18-S3](<#r18-s3>) |
| **Independent album/photo paging**<br>`browse.pagination` | C | Configurable 1–1000 item pages, defaults 30 albums/100 photos; choose infinite scroll, load-more or page navigation independently. Infinite scroll retains loaded pages and grows memory usage. | [R18-S9](<#r18-s9>) |
| **Photo and album slideshows**<br>`browse.slideshow` | C | Free edition includes photo slideshow and album previous/next slideshow. | [R18-S3](<#r18-s3>) |
| **Timeline with direct date access**<br>`browse.timeline` | C | Free standalone and album timeline views respect access control and offer date navigation; custom granularity/format are SE-only. | [R18-S3](<#r18-s3>) |
| **Custom timeline formats**<br>`browse.timeline_customization` | $ | SE comparison separately gates custom timeline granularity, formatting and per-album timeline customization. | [R18-S3](<#r18-s3>) |
| **Docker server deployment**<br>`deployment.docker` | C | README recommends published Docker images and Compose, including persistent uploads/settings-related storage and an optional separate background worker. This packages the web server, not a native desktop client. | [R18-S1](<#r18-s1>) |
| **Multilingual interface**<br>`deployment.localization` | C | Official edition comparison explicitly includes multiple supported UI languages in both Free and SE. Its footnote warns that some languages remain untranslated, so complete translation coverage is not assumed. | [R18-S3](<#r18-s3>) |
| **Self-hosted web gallery**<br>`deployment.selfhosted` | C | Runs on the user's PHP server or supplied Docker images; current README requires PHP 8.4+ for source deployment and distinguishes latest stable from edge. | [R18-S1](<#r18-s1>) |
| **Browser gallery and administration**<br>`deployment.web` | C | Lychee runs on a server/web space and lets users upload, manage, view and share photos from a browser; no native desktop gallery is implied. | [R18-S1](<#r18-s1>), [R18-S2](<#r18-s2>) |
| **White-label gallery branding**<br>`deployment.white_label` | $ | SE v7 can remove Lychee branding; free users can separately hide SE promotional calls to action without obtaining white-label entitlement. | [R18-S3](<#r18-s3>) |
| **Content-checksum duplicate tools**<br>`duplicates.exact_hash` | C | Edition table includes hash deduplication and administration duplicate finding. Current/original checksum tracking is documented; contradictory algorithm descriptions are not resolved into a specific algorithm claim. | [R18-S3](<#r18-s3>), [R18-S5](<#r18-s5>), [R18-S7](<#r18-s7>) |
| **Choose derivative encodings**<br>`editing.format_conversion` | C | Current processing settings offer original/JPEG/WebP/JXL variants, with codec dependencies for optional formats. Quality 0 requests lossless WebP/JXL; changing settings only affects new variants until old ones are regenerated. | [R18-S7](<#r18-s7>) |
| **Automatic orientation and rotation**<br>`editing.rotate_flip` | C | Free import auto-rotation is listed and edit grant includes photo rotation; no claim of a general nondestructive editor. | [R18-S3](<#r18-s3>), [R18-S6](<#r18-s6>) |
| **Custom image watermarks**<br>`editing.watermark` | $ | SE supports watermark images with adjustable scaling, placement and opacity. | [R18-S3](<#r18-s3>) |
| **HEIC/HEIF conversion with original retention**<br>`formats.heic` | O | Current dual-variant pipeline lists HEIC/HEIF among Imagick-convertible source formats and retains native originals where conversion succeeds. | [R18-S7](<#r18-s7>) |
| **JPEG XL import and derivatives**<br>`formats.jpegxl` | O | Requires Imagick/ImageMagick built with libjxl; accepts signatures and can write JXL variants. GD cannot handle it and unsupported browsers have no image fallback. | [R18-S7](<#r18-s7>) |
| **Apple Live Photo pairing**<br>`formats.live_photos` | C | Photo records associate still and video using content ID/checksum/path for motion viewing. v8 hover playback is version-specific rather than baseline UI. | [R18-S5](<#r18-s5>) |
| **Google Motion Photo extraction**<br>`formats.motion_photos` | C | Current photo reference supports legacy MicroVideoOffset and Motion Photo 1.0/Ultra HDR embedded clips, plus artisan extraction for prior still-only imports; v8 grid badges/hover behavior is separately identified. | [R18-S5](<#r18-s5>) |
| **Preserve RAW and generate JPEG displays**<br>`formats.raw` | O | Imagick pipeline converts supported camera RAW/PSD sources to a JPEG display original and retains untouched RAW; conversion failure keeps source as-is with limited preview. RAW downloads have a separate default-off setting. | [R18-S5](<#r18-s5>), [R18-S7](<#r18-s7>) |
| **GPS map viewing**<br>`geo.map` | C | Free GPS localization and map module plot media; no offline basemap or offline geocoder was established. | [R18-S3](<#r18-s3>), [R18-S5](<#r18-s5>) |
| **Album GPS/GPX tracks**<br>`geo.track_overlay` | C | Regular albums can attach multiple GPS/GPX tracks displayed on the map; this does not establish automatic GPX-based geotag writing. | [R18-S4](<#r18-s4>) |
| **Documented API and import CLI**<br>`integration.api` | C | API documentation and CLI import are free; current repository has v2 and newer v3 routes, with v8-specific gates on some endpoints. | [R18-S3](<#r18-s3>), [R18-S12](<#r18-s12>) |
| **Configurable S3 storage**<br>`integration.object_storage` | O | S3 disk supports bucket, endpoint, region, root and path-style configuration; default image disk is local. Metadata write-back currently skips non-local variants. | [R18-S7](<#r18-s7>), [R18-S10](<#r18-s10>) |
| **Sell downloads and prints**<br>`integration.webshop` | $ | Pro addon above SE supplies pricing, size/license choices, basket/order administration, managed download links and Mollie/PayPal/offline payments. Print support does not integrate with printing services. | [R18-S3](<#r18-s3>) |
| **Import renaming rules**<br>`library.bulk_rename` | $ | Edition comparison specifically gates renaming rules on import/upload to SE; free UI retitling is a different operation. | [R18-S3](<#r18-s3>) |
| **Duplicate-aware importing**<br>`library.deduplicate_import` | C | Free edition lists fast filename/title duplicate checks and separate content-hash duplicate detection. These are distinct matching modes; visual similarity is not established. | [R18-S3](<#r18-s3>) |
| **Synchronize server directory trees**<br>`library.directory_sync` | C | Free comparison lists directory-tree import and optional removal of catalogue photos/albums no longer present in source directories; these are potentially destructive sync choices, not a read-only guarantee. | [R18-S3](<#r18-s3>) |
| **Original and album ZIP download**<br>`library.export_originals` | C | Photo/album ZIP downloads are free but subject to download/full-photo grants; preserved RAW export additionally needs raw_download_enabled. | [R18-S3](<#r18-s3>), [R18-S6](<#r18-s6>), [R18-S7](<#r18-s7>) |
| **Browser and server imports**<br>`library.import_copy` | C | Upload from a local computer or import server files through web UI/CLI; chunked upload and full directory-tree import are listed in the free edition. | [R18-S2](<#r18-s2>), [R18-S3](<#r18-s3>) |
| **Import remote image sources**<br>`library.url_import` | C | Official overview lists URL and Dropbox sources; provider-specific current authentication restrictions were not established. | [R18-S2](<#r18-s2>) |
| **Diagnostics and maintenance tools**<br>`maintenance.diagnostics` | C | Free logs, diagnostic checks, maintenance settings and CLI derivative regeneration are documented; optional JXL and face services expose health/configuration diagnostics. | [R18-S3](<#r18-s3>), [R18-S7](<#r18-s7>), [R18-S8](<#r18-s8>) |
| **Batch descriptive editing**<br>`metadata.batch_edit` | C | Desktop-like multi-selection and editing tags/metadata for selected photos are documented; baseline edits change catalogue data. | [R18-S2](<#r18-s2>), [R18-S5](<#r18-s5>), [R18-S7](<#r18-s7>) |
| **Extract dominant colors**<br>`metadata.color_palette` | $ | SE gates dominant color-palette extraction; photo model describes five stored colors. Search/theming use cases in architecture prose do not independently prove a complete color-search UI. | [R18-S3](<#r18-s3>), [R18-S5](<#r18-s5>) |
| **Opt-in metadata write-back**<br>`metadata.embedded_write` | O | Current reference documents disabled-by-default ExifTool queue jobs writing title/description/tags across EXIF/IPTC/XMP and owner's rating into original and preserved RAW files. Local disks only; S3 is skipped. Separate checksum-refresh option defaults on. | [R18-S7](<#r18-s7>) |
| **EXIF extraction and display**<br>`metadata.exif_read` | C | Extracts camera/lens/exposure, GPS/orientation and capture timestamps; display can hide sensitive metadata and manual catalogue values can override extracted values. | [R18-S2](<#r18-s2>), [R18-S5](<#r18-s5>), [R18-S7](<#r18-s7>) |
| **Personal favourites**<br>`metadata.favorites` | $ | Personal favourites are specifically SE in the edition table and are separate from free photo highlighting/smart albums. | [R18-S3](<#r18-s3>), [R18-S4](<#r18-s4>) |
| **IPTC metadata support**<br>`metadata.iptc_read` | C | Official overview explicitly supports/display IPTC; processing guide states default metadata access is read-only rather than writing user changes into files. | [R18-S2](<#r18-s2>), [R18-S7](<#r18-s7>) |
| **One-to-five-star ratings**<br>`metadata.ratings` | C | Edition comparison marks numeric photo ratings as a free v7 capability; optional embedded writing exports the owner's rating only. | [R18-S3](<#r18-s3>), [R18-S7](<#r18-s7>) |
| **Tags and highlighted photos**<br>`metadata.tags` | C | Assign tags singly/in bulk and globally rename, merge or delete tags; highlighted photos feed a built-in smart album. | [R18-S2](<#r18-s2>), [R18-S3](<#r18-s3>), [R18-S4](<#r18-s4>) |
| **Read embedded XMP**<br>`metadata.xmp_read` | C | Processing reference identifies EXIF/IPTC/XMP as read metadata sources; external sidecar matching is not established here. | [R18-S7](<#r18-s7>) |
| **Asynchronous processing workers**<br>`performance.background_jobs` | O | Free worker mode uses a separately running queue worker/container for processing; face scans and metadata-embedding jobs rely on queues. | [R18-S1](<#r18-s1>), [R18-S3](<#r18-s3>), [R18-S7](<#r18-s7>), [R18-S8](<#r18-s8>) |
| **Multiple display derivatives**<br>`performance.thumbnail_cache` | C | Generates medium/small/thumb and high-DPI variants plus low-quality placeholders; dimensions/quality are configurable and original access is separately permissioned. | [R18-S5](<#r18-s5>), [R18-S7](<#r18-s7>) |
| **Basic gallery search**<br>`search.metadata` | C | Free feature table and overview establish basic photo searching; arbitrary technical-field query syntax is not established. | [R18-S2](<#r18-s2>), [R18-S3](<#r18-s3>) |
| **Tag browsing and autocomplete**<br>`search.tags` | C | Tag listings and autocomplete accompany global tag rename/merge/delete management and dynamic tag albums. | [R18-S3](<#r18-s3>), [R18-S4](<#r18-s4>) |
| **Internal user administration notes**<br>`sharing.admin_notes` | $ | SE provides an admin note for each user; the user manual distinguishes this internal note from the user's public/profile description. | [R18-S3](<#r18-s3>), [R18-S13](<#r18-s13>) |
| **Embed albums and publish RSS**<br>`sharing.album_embedding` | C | Edition table marks album embedding and RSS feeds as free modules. | [R18-S3](<#r18-s3>) |
| **Granted album contributions**<br>`sharing.collaborative_albums` | C | Upload and edit grants let selected authenticated users contribute or edit without permission to change sharing; upload moderation is available in v7. | [R18-S3](<#r18-s3>), [R18-S6](<#r18-s6>) |
| **Gallery contact form**<br>`sharing.contact_form` | $ | Official edition matrix lists contact form as an SE-only v7 module. | [R18-S3](<#r18-s3>) |
| **Delegate group administration**<br>`sharing.group_administration` | $ | Edition comparison explicitly lists group administrators for delegated group management as an SE capability, distinct from granting full-system administrator status. | [R18-S3](<#r18-s3>) |
| **Share albums through group permissions**<br>`sharing.group_sharing` | $ | SE supports group sharing and per-album group access rights. AccessPermission can target a user group so album grants apply to its members; this is separate from free individual cross-user sharing. | [R18-S3](<#r18-s3>), [R18-S6](<#r18-s6>), [R18-S13](<#r18-s13>) |
| **Anonymous uploads**<br>`sharing.guest_upload` | $ | Public-link upload grants require SE; public shares never grant edit, move or delete. | [R18-S3](<#r18-s3>), [R18-S6](<#r18-s6>) |
| **Multiple system administrators**<br>`sharing.multiple_administrators` | $ | Edition matrix lists multi-admin support as SE; the user model's may_administrate permission grants full system administration, unlike a delegated group role. | [R18-S3](<#r18-s3>), [R18-S13](<#r18-s13>) |
| **Accounts, registration and invitations**<br>`sharing.multiuser` | C | Unlimited users, registration, invite links, cross-user sharing, per-user trust level and WebAuthn/OAuth login are listed free. | [R18-S3](<#r18-s3>) |
| **Password-protected albums**<br>`sharing.password_links` | C | Album passwords are checked even for explicitly permitted users and unlocking persists for the session. | [R18-S2](<#r18-s2>), [R18-S6](<#r18-s6>) |
| **Public and unlisted albums**<br>`sharing.public_links` | C | Albums/photos can be public; link-required albums are not listed and require knowledge of the URL. Owners/admins alone control visibility/sharing. | [R18-S2](<#r18-s2>), [R18-S6](<#r18-s6>) |
| **Separate per-album action grants**<br>`sharing.roles` | C | View, full-original, download, upload, edit, move and delete rights are separate. Destination albums require edit; ownership-changing actions are constrained. Detailed grant section says permissions must be explicitly propagated to children, although a later legacy paragraph contradicts it. | [R18-S6](<#r18-s6>) |
| **AES-secured image links**<br>`sharing.secured_image_links` | $ | SE offers secured image URLs; this is link protection, not evidence of encrypted-at-rest media or end-to-end encryption. | [R18-S3](<#r18-s3>) |
| **Manually mark sensitive albums**<br>`sharing.sensitive_albums` | C | Free sensitive-album module and is_nsfw album field allow manual content marking; no automatic classifier is implied. | [R18-S3](<#r18-s3>), [R18-S4](<#r18-s4>) |
| **Total per-user storage capacity quotas**<br>`sharing.storage_quotas` | $ | SE's per-user upload quota is explicitly defined by the user manual as quota_kb, a storage limit in kilobytes tracking total photo storage for each user; further uploads are blocked when that quota is exceeded. This is account-capacity enforcement, not a per-upload file-size or file-count limit. | [R18-S3](<#r18-s3>), [R18-S13](<#r18-s13>) |
| **Manage user-group memberships**<br>`sharing.user_groups` | $ | SE includes named user groups for team/client/family access management; a user can belong to multiple groups and membership records carry a group role. | [R18-S3](<#r18-s3>), [R18-S13](<#r18-s13>) |

## Limitations and evidence gaps

- **coverage-gap:** Face recognition release/edition documentation conflicts: Free card, Soon-v8 table and SE-only setup settings. Face subfeatures remain unclear pending an authoritative release/entitlement statement. ([R18-S3](<#r18-s3>), [R18-S8](<#r18-s8>), [R18-S11](<#r18-s11>), [R18-S12](<#r18-s12>))
- **explicit:** Permission document's detailed current grants say no automatic child inheritance, while a later paragraph says permissions flow to children. The detailed rule is described but conflict is not hidden. ([R18-S6](<#r18-s6>))
- **explicit:** Metadata embedding changes file bytes and affects duplicate matching against untouched backups; default off, ExifTool required, local disks only. ([R18-S7](<#r18-s7>))
- **explicit:** JPEG XL requires codec-enabled Imagick and compatible browsers; no browser fallback. RAW conversion can fail gracefully and RAW downloads default disabled. ([R18-S7](<#r18-s7>))
- **coverage-gap:** Architecture prose contradicts source on storage privacy defaults and differs on hash algorithm. Actual filesystem config uses a public uploads root/visibility by default; no universal private-original or persistent bit-rot verification guarantee is asserted. ([R18-S5](<#r18-s5>), [R18-S7](<#r18-s7>), [R18-S10](<#r18-s10>))
- **coverage-gap:** No durable file undo journal, app trash/recovery guarantee, offline basemap or end-to-end media encryption was established. ([R18-S3](<#r18-s3>), [R18-S6](<#r18-s6>), [R18-S7](<#r18-s7>))
- **Coverage gap:** v8 feature gates and facial-recognition edition/timing conflict are unresolved.
- **Coverage gap:** No exhaustive audit of 350+ individual settings; major user workflows, paid boundaries and relevant constraints were inspected.
- **Coverage gap:** No assertion of unverified security, encryption or offline-map guarantees.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R18-S1

[Lychee README](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/README.md>)
- Kind/ref: readme; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Purpose; edition; upgrade; complete installation sections
- Establishes: Server deployment, current PHP requirements and worker-oriented Docker setup.

### R18-S2

[Official feature overview](<https://lycheeorg.dev/>)
- Kind/ref: official-site; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Upload/manage/share/view, EXIF/IPTC and external import claims.

### R18-S3

[Edition comparison](<https://lycheeorg.dev/get-supporter-edition/>)
- Kind/ref: official-site; live-docs inspected 2026-11-09
- Sections inspected: Complete comparison and FAQ; raw HTML checkmark columns inspected
- Establishes: Free/SE/Pro boundaries, feature list and explicitly upcoming v8 functions.

### R18-S4

[Album concepts](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/docs/specs/1-concepts/albums.md>)
- Kind/ref: manual; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Complete document
- Establishes: Regular/tag/system smart albums, many-album membership, tracks and layout controls.

### R18-S5

[Photo concepts](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/docs/specs/1-concepts/photos.md>)
- Kind/ref: manual; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Complete document
- Establishes: Metadata, Live/Motion Photo associations, variants and permissions; includes claims refined by newer processing docs.

### R18-S6

[Access permissions](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/docs/specs/1-concepts/permissions.md>)
- Kind/ref: manual; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Complete document
- Establishes: Separate grants, sharing ownership, public upload gates and conflicting inheritance passages.

### R18-S7

[Image processing reference](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/docs/specs/3-reference/image-processing.md>)
- Kind/ref: manual; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Complete document
- Establishes: RAW preservation, JPEG XL requirements, derivative formats and opt-in metadata write-back.

### R18-S8

[Configure facial recognition](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/docs/specs/2-how-to/configure-facial-recognition.md>)
- Kind/ref: manual; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Overview through setup, environment, permissions, scanning, clustering, maintenance and authentication troubleshooting
- Establishes: Concrete sidecar setup and face workflows, with unresolved version/edition availability.

### R18-S9

[Configure pagination](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/docs/specs/2-how-to/configure-pagination.md>)
- Kind/ref: manual; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Overview; all page-size and UI-mode settings; infinite-scroll threshold descriptions
- Establishes: Paged, load-more and infinite-scroll behavior and memory caveat.

### R18-S10

[Filesystem configuration](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/config/filesystems.php>)
- Kind/ref: code; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Complete file
- Establishes: Actual local/public upload defaults, S3 configuration and private job staging disks.

### R18-S11

[v7.13.0 release notes](<https://github.com/LycheeOrg/Lychee/releases/tag/v7.13.0>)
- Kind/ref: release; v7.13.0
- Sections inspected: Complete release note
- Establishes: Stable release includes explicitly labelled v8 development changes.

### R18-S12

[API v3 routes](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/routes/api_v3.php>)
- Kind/ref: code; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Album listing feature-gate comments; Insights; People/Faces routes
- Establishes: Source confirms v8-gated album surface and face routes without proving general release availability.

### R18-S13

[Users, storage quotas and groups](<https://github.com/LycheeOrg/Lychee/blob/ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d/docs/specs/1-concepts/users.md>)
- Kind/ref: manual; ba1e7ef62b037fd29a3d6b8a52e1eae903c53d0d
- Sections inspected: Complete document; specifically User Attributes Quota, User Capabilities Storage Quota, group membership and access permissions
- Establishes: quota_kb is a per-user total photo-storage limit in kilobytes, with uploads blocked when exceeded; also defines multiple group memberships and group-targeted album permissions.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
