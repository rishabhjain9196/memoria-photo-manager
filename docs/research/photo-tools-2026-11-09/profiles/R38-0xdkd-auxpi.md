# R38 — 0xDkd/auxpi

[Repository](<https://github.com/0xDkd/auxpi>) · 2,697 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Go/Vue image-hosting gateway that routes uploads among local and third-party hosts and offers stable dispatch links, administration and local backup of remotely hosted images.

**Deployment:** Self-hosted Go server with web UI and MySQL; Documented Linux VPS installation; Source build targets Linux, macOS and Windows; these are server deployments, not native gallery clients

**Storage:** MySQL tracks users, providers, image URLs/deletion tokens/local paths and dispatch records. Local uploads use upload-date folders and random names; remote adapters store images on external hosts. Optional synchronization downloads remote images into local backup records.

**Privacy/network behavior:** Remote-provider uploads disclose image bytes to chosen hosts and dispatch can replicate them elsewhere. Local storage can avoid those uploads when chosen. User/IP records, authentication and upload restrictions exist, but no encrypted media/private-album model is established. Demo moderation statement is not proof of available local AI.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 2.3.9 (2019-06-01T08:28:56Z)
**Repository pushed at:** 2025-06-12T16:23:11Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [7144707f10fe](<https://github.com/0xDkd/auxpi/commit/7144707f10fec0a7eb426d9fb1cb362271a16925>).
**Product lineage:** 0xDkd/auxpi.

## Maturity and availability caveats

- Frozen dev commit 7144707f10fec0a7eb426d9fb1cb362271a16925; latest release 2.3.9 (2019-06-01), despite later repository pushes.
- README and code retain prior aimerforreimu/AUXPI identity and dated external provider endpoints. Provider availability was not tested and should not be assumed current.
- README explicitly describes a learning-stage project and warns of bugs; source shows unfinished hooks/TODOs.
- No demo logins, uploads or installation scripts were executed.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Content moderation**<br>`ai.sensitive_content_detection` | ? | README says the public demo has strict image moderation, but inspected CheckImage hook is empty and shared upload pipeline does not establish a configured classifier. Not counted as working core AI. | [R38-S1](<#r38-s1>), [R38-S10](<#r38-s10>), [R38-S13](<#r38-s13>) |
| **Image and usage dashboard**<br>`analytics.library_statistics` | C | Reports include images by provider, last-seven-day all/local image counts, recent registrations and API information, rendered as dashboard charts. | [R38-S1](<#r38-s1>), [R38-S6](<#r38-s6>), [R38-S9](<#r38-s9>) |
| **Paged image and backup lists**<br>`browse.pagination` | C | Admin lists image/dispatch/backup records with page/limit, provider filtering and ascending/descending ID order. | [R38-S3](<#r38-s3>), [R38-S6](<#r38-s6>), [R38-S9](<#r38-s9>) |
| **Internationalized interface**<br>`deployment.localization` | R | README lists internationalization as unchecked TODO, not currently completed multilingual support. | [R38-S1](<#r38-s1>) |
| **Self-hosted image hosting server**<br>`deployment.selfhosted` | C | Web upload/admin application with Go backend, Vue frontend and MySQL; README offers VPS/manual deployment and cross-platform server builds. | [R38-S1](<#r38-s1>) |
| **Web image hosting and administration**<br>`deployment.web` | C | README explicitly documents web image upload, a Vue-driven frontend and administrator dashboard. Linux/macOS/Windows build targets are for the server, not native desktop gallery clients. | [R38-S1](<#r38-s1>) |
| **Provider-selecting upload API**<br>`integration.api` | C | V1 multipart API accepts image, optional/configured token and apiSelect; returns image name/URL and provider deletion data, with explicit disabled/auth/empty/size errors documented. | [R38-S1](<#r38-s1>), [R38-S4](<#r38-s4>), [R38-S10](<#r38-s10>) |
| **Automatic API documentation**<br>`integration.generated_api_docs` | R | README unchecked roadmap item; manually written V1 API instructions already exist. | [R38-S1](<#r38-s1>) |
| **GitHub and Gitee image storage**<br>`integration.git_repository_storage` | O | Both adapters are registered and eligible as dispatch root stores, alongside local/Flickr/Imgur; service setup/credentials remain external. | [R38-S5](<#r38-s5>), [R38-S12](<#r38-s12>) |
| **Multiple external image-host adapters**<br>`integration.hosting_services` | O | Registered adapters include Sogou, Sina, SMMS, Upload.cc, Flickr, Imgur, Alibaba/JD/Juejin and others; these are legacy external integrations, not verified currently functioning services. | [R38-S5](<#r38-s5>), [R38-S12](<#r38-s12>) |
| **Ranked redispatch and root fallback**<br>`integration.provider_failover` | C | Dispatch checks target availability and attempts another ranked host, falling back to root when destinations are exhausted. Source contains TODO failure handling, so this is designed behavior rather than proven reliable failover. | [R38-S3](<#r38-s3>) |
| **Enable, reorder and weight providers**<br>`integration.provider_management` | C | Admin menu drag-order controls enabled providers; provider records separately hold homepage rank and dispatch weight plus configuration updates. | [R38-S1](<#r38-s1>), [R38-S5](<#r38-s5>), [R38-S6](<#r38-s6>) |
| **Delete image and local-backup records**<br>`library.bulk_delete` | C | Admin accepts ID lists; model deletes associated local paths and database rows. Inspected delete path does not establish revocation of every third-party hosted copy. | [R38-S6](<#r38-s6>), [R38-S8](<#r38-s8>), [R38-S9](<#r38-s9>) |
| **Web image uploads**<br>`library.import_copy` | C | Browser upload sends supported images to chosen enabled provider; upload size is configurable and source checks PNG/JPG/JPEG/GIF/BMP suffix/MIME combinations. | [R38-S1](<#r38-s1>), [R38-S4](<#r38-s4>), [R38-S10](<#r38-s10>) |
| **Download hosted images into local backups**<br>`library.remote_backup` | C | Admin-selected remote URLs are concurrently downloaded to server files and linked backup records; source uses a task lock and reports progress/completion or a 60-second inactivity timeout. | [R38-S6](<#r38-s6>), [R38-S8](<#r38-s8>) |
| **Date-partitioned local storage**<br>`library.upload_date_storage` | C | Local adapter uses current upload year/month/day directories and a random 16-character basename with retained extension; not EXIF capture-date organization. | [R38-S7](<#r38-s7>) |
| **Clear all server caches**<br>`maintenance.cache_reset` | C | Admin action calls ClearAll; group-selective cache clearing remains a TODO. | [R38-S6](<#r38-s6>) |
| **Admin logs and task events**<br>`maintenance.diagnostics` | C | Paged logs and synchronization progress/completion messages expose operational status. These logs are not rollback/crash-recovery file journals. | [R38-S6](<#r38-s6>), [R38-S8](<#r38-s8>) |
| **IP-based upload blocking**<br>`maintenance.ip_rate_limits` | O | Configurable enabled middleware tracks attempts/time, temporary block period and threshold for persistent blocks; release 2.3.9 includes IP-block fixes. | [R38-S2](<#r38-s2>), [R38-S11](<#r38-s11>) |
| **Asynchronous dispatch and synchronization**<br>`performance.background_jobs` | C | Goroutines perform secondary host upload and multi-image local synchronization; no durable queue/checkpoint recovery is established. | [R38-S3](<#r38-s3>), [R38-S8](<#r38-s8>) |
| **Cache dispatch targets**<br>`performance.redirect_cache` | C | Dispatch stores URL targets with a 3600 cache duration and redirects directly on cache hits; release notes identify Redis cache fixes. | [R38-S2](<#r38-s2>), [R38-S3](<#r38-s3>) |
| **Scheduled task execution**<br>`performance.scheduled_tasks` | R | README lists scheduled task dispatch as an unchecked roadmap item; asynchronous immediate work is separate. | [R38-S1](<#r38-s1>) |
| **Local image storage option**<br>`privacy.no_upload_required` | C | Enabled Local adapter writes image bytes to configured server filesystem and returns a server URL; use of remote dispatch/providers is a separate choice. | [R38-S7](<#r38-s7>), [R38-S12](<#r38-s12>) |
| **Configurable upload size and type restrictions**<br>`safety.upload_limits` | C | Server enforces configured maximum size and allowed filename/MIME suffix combinations; this is not evidence of full decoding, malware scan or content-safety recognition. | [R38-S4](<#r38-s4>), [R38-S10](<#r38-s10>) |
| **Stable redirect URLs over changing hosts**<br>`sharing.dispatch_links` | C | V2 uploads to selected root, creates a dispatch/hash URL, starts secondary upload asynchronously and serves cached/provider redirects. Stable URL can outlive a provider target change. | [R38-S1](<#r38-s1>), [R38-S3](<#r38-s3>) |
| **User accounts and administration**<br>`sharing.multiuser` | C | README marks user system complete; admin API lists/deletes users and associates image records with uploading users. | [R38-S1](<#r38-s1>), [R38-S6](<#r38-s6>), [R38-S9](<#r38-s9>) |
| **Per-provider account requirements**<br>`sharing.provider_access_levels` | C | Provider Auth setting distinguishes guest, any signed-in user and administrator-only use; this is upload-provider access, not password-protected photo albums. | [R38-S5](<#r38-s5>) |

## Limitations and evidence gaps

- **coverage-gap:** Latest release is from 2019 and many adapters use old third-party endpoints. No assertion is made that any external host still accepts uploads or retains files indefinitely. ([R38-S1](<#r38-s1>), [R38-S2](<#r38-s2>), [R38-S5](<#r38-s5>), [R38-S12](<#r38-s12>))
- **explicit:** Provider descriptions themselves mention anti-hotlinking, moderation/cleanup, geographic reachability and unstable response formats; remote services control availability. ([R38-S5](<#r38-s5>))
- **coverage-gap:** Application deletion removes catalogue/local files in inspected source but does not establish removal of all remote replicas; dispatch and sharing are not privacy-preserving cloud storage. ([R38-S3](<#r38-s3>), [R38-S8](<#r38-s8>), [R38-S9](<#r38-s9>))
- **coverage-gap:** README demo moderation statement is not backed by a functioning inspected moderation implementation. ([R38-S1](<#r38-s1>), [R38-S10](<#r38-s10>), [R38-S13](<#r38-s13>))
- **coverage-gap:** No EXIF organization, face recognition, similarity deduplication, photo albums, encrypted vault, durable job resume or recoverable trash was established. ([R38-S1](<#r38-s1>), [R38-S6](<#r38-s6>), [R38-S9](<#r38-s9>))
- **explicit:** README one-click installation explicitly warns it installs nginx/MySQL and expects a clean server; it was not run. ([R38-S1](<#r38-s1>))
- **Coverage gap:** Primary documentation is sparse beyond README/API examples; source provides most detail.
- **Coverage gap:** External provider operability and moderation availability remain unresolved.
- **Coverage gap:** No security audit or live behavior validation was performed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R38-S1

[AUXPI README](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/README.md>)
- Kind/ref: readme; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete README: features, API, installation, screenshots captions, TODO
- Establishes: Web/API hosting, weighted distribution, users, administrator dashboard and roadmap.

### R38-S2

[2.3.9 release](<https://github.com/0xDkd/auxpi/releases/tag/2.3.9>)
- Kind/ref: release; 2.3.9
- Sections inspected: Complete release note
- Establishes: Shell update, Redis/store-cache fixes and IP-blocking fixes.

### R38-S3

[Dispatch controller](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/controllers/api/v2/dispatch.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Root upload, stable dispatch links, async secondary upload, redirect caching and source fallback intent.

### R38-S4

[Upload endpoint](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/controllers/api/v1/upload.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Selected provider, configurable size bounds and image-type checks.

### R38-S5

[Storage registry](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/models/stores.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Provider list, rank/weight/auth controls and warnings about provider restrictions.

### R38-S6

[Administration controller](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/controllers/api/v1/admin.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file across two reads
- Establishes: Paged image lists, bulk delete/sync, reports, users, configuration and cache clearing.

### R38-S7

[Local storage adapter](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/server/Local.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Configurable directory/URL and upload-date/random-name storage.

### R38-S8

[Remote image backup synchronization](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/models/sync.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Concurrent remote downloads, local backup records, progress notifications and timeout.

### R38-S9

[Image persistence and deletion](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/models/images.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file across two reads
- Establishes: Image/user/provider associations, reports and deletion scope.

### R38-S10

[Shared upload processing](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/controllers/base.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Default/provider selection, header/suffix validation and URL/token response.

### R38-S11

[Upload IP-limit middleware](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/middleware/limit.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Configurable IP attempts, temporary/permanent blocking and cached counters.

### R38-S12

[Uploader registration](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/server/index.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Uploader types, complete root/general registration and client construction
- Establishes: Actual registered local/external adapters and restricted root choices.

### R38-S13

[Moderation hook](<https://github.com/0xDkd/auxpi/blob/7144707f10fec0a7eb426d9fb1cb362271a16925/tools/checkPorn.go>)
- Kind/ref: code; 7144707f10fec0a7eb426d9fb1cb362271a16925
- Sections inspected: Complete file
- Establishes: Empty content-check stub contrasts with README demo moderation claim.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
