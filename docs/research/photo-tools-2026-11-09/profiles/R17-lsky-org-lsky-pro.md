# R17 — lsky-org/lsky-pro

[Repository](<https://github.com/lsky-org/lsky-pro>) · 4,702 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Discontinued open-source multi-user image host with configurable storage strategies, role-based upload policies, watermarking and an upload/management API. Commercial Lsky Pro+ is a separate edition.

**Deployment:** Self-hosted PHP &gt;=8.0.2 application with Imagick and required PHP extensions; MySQL 5.7+, PostgreSQL 9.6+, SQLite 3.8.8+ or SQL Server 2017+ per README

**Storage:** Managed upload objects on a configured storage strategy; database records track owner, album, paths, dimensions, hashes and upload IP. Within one strategy, matching MD5 and SHA-1 reuse the physical object while creating a new record. Processing may rewrite uploads before hashes are computed.

**Privacy/network behavior:** Can use local storage or optional external cloud/network backends. Optional Alibaba/Tencent moderation sends images to providers; NSFW.js uses a configured service endpoint. Public links and original-protection settings are not E2EE; uploads record IP addresses.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 2.1 (2022-08-17T05:37:50Z)
**Repository pushed at:** 2026-02-14T03:51:20Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [38d52c4609eb](<https://github.com/lsky-org/lsky-pro/commit/38d52c4609eb85236b45ac75acac2ced55174953>).
**Product lineage:** lsky-org/lsky-pro.

## Maturity and availability caveats

- Pinned master 38d52c4609eb85236b45ac75acac2ced55174953 explicitly says open-source maintenance, new features and bug fixes have stopped.
- Latest manifest release is 2.1 (2022-08-17); README warns master can include experimental/unreleased features.
- Current docs.lsky.pro explicitly documents paid Pro+ 2.x; its commerce features are not attributed to this open-source repository.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Managed user albums**<br>`albums.manual` | C | API lists/deletes albums and ingestion can assign a valid user-configured default album; no nested/smart album semantics are established. | [R17-S6](<#r17-s6>), [R17-S7](<#r17-s7>) |
| **Waterfall image manager**<br>`browse.grid` | C | README describes waterfall display, context menu, single/multiple selection and rename operations. | [R17-S1](<#r17-s1>) |
| **Paginated image API**<br>`browse.pagination` | C | Authenticated image listing uses pages of 40 and returns dimensions, MIME, extensions, sizes, hashes, timestamps and link fields. | [R17-S8](<#r17-s8>) |
| **Commercial Pro+ hosting business tools**<br>`commerce.hosting_plans` | $ | Current paid-edition documentation advertises plans, orders, tickets, feedback, announcements, coupons and Alipay/WeChat payments. These belong to separate Pro+, not demonstrated open-source repository functionality. | [R17-S9](<#r17-s9>) |
| **Self-hosted image hosting**<br>`deployment.selfhosted` | C | Browser upload/management application deployed on a PHP/Imagick server, not a local photo catalogue. | [R17-S1](<#r17-s1>) |
| **Browser upload and administration interface**<br>`deployment.web` | C | The self-hosted PHP application exposes browser image upload, waterfall management and administrative role/storage settings; this is the discontinued open-source web interface, not a native desktop client or the separate paid Pro+ edition. | [R17-S1](<#r17-s1>), [R17-S3](<#r17-s3>) |
| **Reuse identical stored content**<br>`duplicates.exact_hash` | C | Within a storage strategy, ingestion matches both MD5 and SHA-1 of post-processed upload bytes; matching content reuses path/name and creates only a new database record. No byte verification or visual similarity is claimed. | [R17-S6](<#r17-s6>) |
| **Group-level upload conversion**<br>`editing.format_conversion` | C | Role group selects saved format and quality; store applies processing before hashing, excluding ICO/GIF/SVG from this conversion path. | [R17-S2](<#r17-s2>), [R17-S3](<#r17-s3>), [R17-S6](<#r17-s6>) |
| **Detailed text/image watermarks**<br>`editing.watermark` | C | Supports text or image, tiled positioning, offsets and rotation; text has font/color/size and image has dimensions/opacity. Modes either overwrite stored image or generate dynamically. | [R17-S1](<#r17-s1>), [R17-S2](<#r17-s2>), [R17-S3](<#r17-s3>) |
| **Versioned token upload and management API**<br>`integration.api` | C | API v1 exposes upload, storage strategies and token issuance; authenticated routes list/delete images and albums, revoke tokens and fetch profile. Feature can be globally enabled/disabled. | [R17-S7](<#r17-s7>), [R17-S8](<#r17-s8>) |
| **FTP storage strategy**<br>`integration.ftp_storage` | O | README explicitly lists FTP as a configurable remote storage backend; this is storage integration, not source-folder library synchronization. | [R17-S1](<#r17-s1>) |
| **Cloud/object storage strategies**<br>`integration.object_storage` | O | Strategies support AWS S3, Alibaba OSS, Tencent COS, Qiniu, Upyun and Minio in addition to local files. | [R17-S1](<#r17-s1>) |
| **SFTP storage strategy**<br>`integration.sftp_storage` | O | README explicitly lists SFTP as a configurable remote storage backend; release 2.1 updates its driver extension. | [R17-S1](<#r17-s1>), [R17-S2](<#r17-s2>) |
| **Provider image URL parameters**<br>`integration.storage_url_parameters` | C | 2.1 adds per-strategy image URL parameters; docs recommend provider-side transformation rules for third-party storage to avoid heavy PHP processing. | [R17-S2](<#r17-s2>), [R17-S5](<#r17-s5>) |
| **WebDAV storage backend**<br>`integration.webdav` | O | WebDAV is explicitly a storage strategy, alongside FTP and SFTP; no automatic desktop-library sync is implied. | [R17-S1](<#r17-s1>) |
| **Upload multiple images**<br>`library.batch_upload` | C | README explicitly lists multi-image upload; role-group configuration additionally exposes a concurrent-upload limit. | [R17-S1](<#r17-s1>), [R17-S3](<#r17-s3>) |
| **Managed image-upload inputs**<br>`library.managed_upload` | C | Drag-and-drop and pasted images enter managed storage, with dynamic selection of a storage strategy allowed for the uploader's group. | [R17-S1](<#r17-s1>), [R17-S6](<#r17-s6>) |
| **Rule-driven object names and folders**<br>`library.upload_naming_templates` | C | Naming rules combine year/month/day, timestamp, unique/random tokens, original filename and user ID (zero for guests). These are upload-path rules, not capture-date organization. | [R17-S4](<#r17-s4>) |
| **Online incremental and cross-version updates**<br>`maintenance.online_upgrade` | C | README lists both upgrade modes as implemented; this is historical functionality and does not imply continued upstream updates. | [R17-S1](<#r17-s1>) |
| **Optional image-content moderation**<br>`ai.content_moderation` | O | Group selects Tencent, Alibaba or configured NSFW.js service; can flag unhealthy or delete/reject. NSFW.js threshold is configurable; PSD/ICO/TIF/SVG skip the examined scan path. | [R17-S3](<#r17-s3>), [R17-S6](<#r17-s6>) |
| **Selectable cache drivers**<br>`performance.cache_backends` | O | README lists file cache by default plus configurable Memcached, Redis, DynamoDB and relational database alternatives. | [R17-S1](<#r17-s1>) |
| **Generated thumbnails and processed cache**<br>`performance.thumbnail_cache` | C | Ingestion creates thumbnails; original protection/dynamic watermarking uses cached processed images with configurable TTL and explicit cache clearing. | [R17-S3](<#r17-s3>), [R17-S5](<#r17-s5>), [R17-S6](<#r17-s6>) |
| **Copy generated image links**<br>`sharing.copy_links` | C | Upload UI offers copying and one-click link copying; API returns computed links and storage paths. | [R17-S1](<#r17-s1>), [R17-S8](<#r17-s8>) |
| **Configurable guest uploads**<br>`sharing.guest_upload` | C | Ingestion checks a global allow-guest setting, assigns the guest role group and applies guest upload limits by IP. | [R17-S6](<#r17-s6>) |
| **Registered user accounts**<br>`sharing.multiuser` | C | Upload checks user status, optional verified email, per-user capacity and default album/visibility settings. | [R17-S6](<#r17-s6>) |
| **Proxy-mediated original protection**<br>`sharing.original_proxy_protection` | C | Group can enable original protection, withholding direct links and serving processed/cached responses through PHP with configurable image cache lifetime; not encryption. | [R17-S3](<#r17-s3>), [R17-S5](<#r17-s5>) |
| **Image square and image visibility**<br>`sharing.public_gallery` | C | README lists a public image square; ingestion defaults to private and honors a registered user's default image permission. | [R17-S1](<#r17-s1>), [R17-S6](<#r17-s6>) |
| **Many-to-many groups and storage strategies**<br>`sharing.roles` | C | Each role group can access multiple strategies, and each strategy can serve multiple groups; per-group policies control upload behavior. | [R17-S1](<#r17-s1>), [R17-S3](<#r17-s3>) |
| **Enforced per-account storage capacity**<br>`sharing.storage_quotas` | C | Before accepting an authenticated user's upload, ImageService adds its size in KB to the sum of that user's existing image-record sizes and rejects the upload if the result exceeds the user's capacity. This establishes account-level recorded-storage accounting, not a physical-backend free-space measurement. | [R17-S6](<#r17-s6>) |
| **Per-file and concurrent-upload restrictions**<br>`sharing.upload_quotas` | C | Role group sets permitted extensions, maximum individual file size in KB and concurrent upload count; ingestion rejects unsupported extensions or oversized files. Total account capacity is a separate control. | [R17-S3](<#r17-s3>), [R17-S6](<#r17-s6>) |
| **Multi-window upload limits**<br>`sharing.upload_rate_limits` | C | Configurable minute/hour/day/week/month counts apply to a logged-in user or anonymous uploader IP, based on recent image records. | [R17-S3](<#r17-s3>), [R17-S6](<#r17-s6>) |
| **Multiple relational database engines**<br>`storage.database_choices` | O | README lists MySQL, PostgreSQL, SQLite and SQL Server with explicit minimum versions. | [R17-S1](<#r17-s1>) |

## Limitations and evidence gaps

- **explicit:** Open-source edition explicitly stopped feature development and bug fixes; master may contain unreleased experiments. ([R17-S1](<#r17-s1>))
- **explicit:** Current official documentation is paid Pro+ documentation. Paid commerce features are separated rather than counted as open-source core. ([R17-S9](<#r17-s9>))
- **explicit:** Dynamic watermark/original-protection processing loads cached responses into memory and has high server requirements; PHP upload/post limits also bound uploads. ([R17-S5](<#r17-s5>))
- **explicit:** Upload conversion or overlay watermarking can replace submitted image bytes; no archive-preserving copy workflow is established. Moderation may delete content. ([R17-S6](<#r17-s6>))
- **coverage-gap:** Face recognition, EXIF catalogue editing, maps, existing-folder indexing, trash/undo, expiring/password shares and E2EE were not established by inspected open-source evidence. ([R17-S1](<#r17-s1>), [R17-S3](<#r17-s3>), [R17-S6](<#r17-s6>))
- **Coverage gap:** Current commercial manual cannot establish legacy open-source behavior; used in-repository role help/forms and ingestion/API source instead.
- **Coverage gap:** No runtime deployment or provider integrations tested.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R17-S1

[Open-source README](<https://github.com/lsky-org/lsky-pro/blob/38d52c4609eb85236b45ac75acac2ced55174953/README.md>)
- Kind/ref: readme; 38d52c4609eb85236b45ac75acac2ced55174953
- Sections inspected: Maintenance warning; master/release notice; complete checked feature list; requirements
- Establishes: Storage, databases, upload UI, roles, watermarks, API and stopped maintenance.

### R17-S2

[Release 2.1](<https://github.com/lsky-org/lsky-pro/releases/tag/2.1>)
- Kind/ref: release; 2.1
- Sections inspected: Complete added/changed/fixed release notes
- Establishes: Group quality/format controls, storage URL parameters and watermark modes.

### R17-S3

[Role-group configuration form](<https://github.com/lsky-org/lsky-pro/blob/38d52c4609eb85236b45ac75acac2ced55174953/resources/views/admin/group/edit.blade.php>)
- Kind/ref: code; 38d52c4609eb85236b45ac75acac2ced55174953
- Sections inspected: All form tabs and help text: general, moderation, original protection, watermark
- Establishes: Upload restrictions, moderation services, cache lifetime and detailed watermark controls.

### R17-S4

[Path and filename rule reference](<https://github.com/lsky-org/lsky-pro/blob/38d52c4609eb85236b45ac75acac2ced55174953/resources/views/admin/group/rules.blade.php>)
- Kind/ref: manual; 38d52c4609eb85236b45ac75acac2ced55174953
- Sections inspected: Complete naming token table
- Establishes: Date/time, random identifiers, original filename and user-ID tokens.

### R17-S5

[Group configuration warnings](<https://github.com/lsky-org/lsky-pro/blob/38d52c4609eb85236b45ac75acac2ced55174953/resources/views/admin/group/tips.blade.php>)
- Kind/ref: manual; 38d52c4609eb85236b45acac2ced55174953
- Sections inspected: Complete upload/runtime and dynamic-processing warnings
- Establishes: PHP size ceilings and resource costs of protection/watermarking.

### R17-S6

[Image ingestion service](<https://github.com/lsky-org/lsky-pro/blob/38d52c4609eb85236b45acac2ced55174953/app/Services/ImageService.php>)
- Kind/ref: code; 38d52c4609eb85236b45acac2ced55174953
- Sections inspected: Complete store method (77-275); rateLimiter (368-405); method index
- Establishes: Validation, account/quota checks, transformations, deduplication, moderation and IP storage.

### R17-S7

[Versioned API routes](<https://github.com/lsky-org/lsky-pro/blob/38d52c4609eb85236b45acac2ced55174953/routes/api.php>)
- Kind/ref: code; 38d52c4609eb85236b45acac2ced55174953
- Sections inspected: Complete v1 route definitions
- Establishes: Upload/strategy/token access and authenticated image/album/profile operations.

### R17-S8

[Image API controller](<https://github.com/lsky-org/lsky-pro/blob/38d52c4609eb85236b45acac2ced55174953/app/Http/Controllers/Api/V1/ImageController.php>)
- Kind/ref: code; 38d52c4609eb85236b45acac2ced55174953
- Sections inspected: Complete upload, images and destroy methods
- Establishes: Returned metadata/link fields, 40-item pagination and owner-specific listing/deletion.

### R17-S9

[Current commercial documentation landing page](<https://docs.lsky.pro>)
- Kind/ref: official-site; live-docs inspected 2026-11-09
- Sections inspected: Edition banner; storage, commerce and moderation overview
- Establishes: Explicit paid-edition boundary; paid packages/orders/payment integration are Pro+ claims.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
