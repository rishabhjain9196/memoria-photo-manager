# R10 — MarSeventh/CloudFlare-ImgBed

[Repository](<https://github.com/MarSeventh/CloudFlare-ImgBed>) · 6,883 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Image and general-file hosting frontend/backend with selectable external storage channels, public delivery, admin management and optional AI tagging.

**Deployment:** Cloudflare Pages; Cloudflare Workers; Self-hosted Docker/Node.js/Hono service; Responsive web UI; separate ecosystem desktop/browser/blog clients

**Storage:** Metadata is decoupled from payloads: KV/D1 in Cloudflare deployments or SQLite/local data directory in Docker; payload channels include Telegram, Discord, R2, S3-compatible services, Hugging Face datasets and WebDAV. Direct links and CDN routes can bypass application-layer lifecycle controls.

**Privacy/network behavior:** Self-hosting the service does not make storage or AI local. Files may be sent to selected providers; moderation and IP geolocation may contact additional services. Telemetry documentation warns that access links and domains may reach developers. AI keys are encrypted with an operator-managed secret, not media E2EE. Ordinary file reads usually need no authentication.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v2.7.8 (2026-10-25T14:07:54Z)
**Repository pushed at:** 2026-11-03T02:45:16Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [85636c5bc739](<https://github.com/MarSeventh/CloudFlare-ImgBed/commit/85636c5bc7393e80e0fe229a8f73538ad5c65ee4>).
**Product lineage:** MarSeventh/CloudFlare-ImgBed.

## Maturity and availability caveats

- Frozen main commit 85636c5bc7393e80e0fe229a8f73538ad5c65ee4; release v2.7.8 dated 2026-10-25.
- Official live documentation inspected 2026-11-09 may be ahead of the pinned release, notably automatic AI tagging and file-expiry settings; those are explicitly labelled live-doc capabilities below.
- Evolved from Telegraph-Image. Web frontend Sanyue-ImgHub and desktop Satellite are separate repositories; ecosystem integrations are not bundled core features.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **AI tag suggestions**<br>`ai.auto_tags` | O | v2.7.8 provides manually invoked single/batch tag recognition with selectable suggestions, progress, cancellation of future work and failed-item retries, without needing stored thumbnails. | [R10-S2](<#r10-s2>) |
| **Configurable image-capable providers**<br>`ai.remote_inference` | O | OpenAI-compatible chat endpoints, up to 8 providers/16 models, configurable prompts/language/preferred vocabulary and structured output; text connection test does not prove image capability. | [R10-S4](<#r10-s4>) |
| **Background automatic upload tagging**<br>`ai.upload_tagging` | O | Live documentation describes opt-in post-upload tagging of originals on supported channels, excluding External and images over 20 MiB. Disabled by default; upload response does not wait. Presence in frozen v2.7.8 is not established by its notes. | [R10-S4](<#r10-s4>) |
| **Channel storage and upload statistics**<br>`analytics.storage_distribution` | C | Counts, storage usage, channel distribution and date/channel upload trends, with capacity thresholds for R2/S3/WebDAV. | [R10-S3](<#r10-s3>) |
| **Audio preview player**<br>`browse.audio_playback` | C | File Details provides a compact audio player and skeleton preview states; other file types fall back to an information row. | [R10-S2](<#r10-s2>) |
| **Light/dark and branding controls**<br>`browse.dark_theme` | C | Theme switching, custom title/logo/icon/footer/link prefix and solid, fixed, rotating or Bing backgrounds are configurable; Bing is an external request option. | [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>) |
| **Directory organization**<br>`browse.folders` | C | Create directories and navigate a visual directory tree; search can retain folders or recursively expand results, with preference saved. | [R10-S3](<#r10-s3>), [R10-S2](<#r10-s2>) |
| **Card and list file management**<br>`browse.grid` | C | Visual card/list views with rubber-band selection and batch operations in user-selected order. | [R10-S3](<#r10-s3>) |
| **Paged large-file listings**<br>`browse.pagination` | C | File management uses paginated loading and mobile swipe pagination; this is not a claim of virtualized rows. | [R10-S3](<#r10-s3>) |
| **Video detail previews**<br>`browse.video_playback` | C | Release describes video preview loading/orientation handling in File Details; codec coverage is not exhaustively specified. | [R10-S2](<#r10-s2>) |
| **Pages and Workers runtimes**<br>`deployment.cloudflare` | C | Cloudflare Pages and Workers run the shared engine with KV/D1 persistence; Workers deployment via GitHub Actions supports secret-typed variables. | [R10-S1](<#r10-s1>), [R10-S2](<#r10-s2>) |
| **Separate Satellite desktop companion**<br>`deployment.desktop_client` | P | README explicitly links MarSeventh/satellite as the project's desktop client, separately from the hosting server and web frontend. The inspected README does not establish exact supported desktop OSes or release parity, so no Windows/macOS/Linux availability is inferred. | [R10-S1](<#r10-s1>) |
| **Docker with SQLite**<br>`deployment.docker` | C | Node.js/Hono Docker deployment uses SQLite and a persistent local data directory for service data. | [R10-S3](<#r10-s3>) |
| **Chinese and English interface**<br>`deployment.localization` | C | Official feature/configuration guides document dynamic Chinese/English UI switching, persisted language preference, configurable default language and synchronized component-library locale; this is UI translation, not AI tag-language selection. | [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>) |
| **Operator-managed hosting**<br>`deployment.selfhosted` | C | Deploy the serverless service to one's Cloudflare account or self-host the Docker service; external storage providers remain separately configured. | [R10-S1](<#r10-s1>), [R10-S3](<#r10-s3>) |
| **Responsive hosting dashboard**<br>`deployment.web` | C | Web upload/admin/public-gallery interfaces support desktop and mobile layouts, Chinese/English switching and stored language preference. | [R10-S3](<#r10-s3>) |
| **URL-based centre crop**<br>`editing.crop` | O | With both dimensions and fit=cover, delivery resizes and centre-crops. It is not an interactive photo editor and requires image processing enabled. | [R10-S6](<#r10-s6>) |
| **Convert uploads to WebP**<br>`editing.format_conversion` | C | Can convert images in-browser before uploading and displays conversion/size-reduction badges; animated GIF/WebP/APNG skip conversion. | [R10-S4](<#r10-s4>), [R10-S2](<#r10-s2>) |
| **Browser-side image compression**<br>`editing.image_compression` | C | Optional upload optimization has configurable 1–20 MB trigger threshold and target size from 0.5 MB to that threshold; release excludes animated files to preserve animation. | [R10-S4](<#r10-s4>), [R10-S2](<#r10-s2>) |
| **Delivery-time image sizing**<br>`editing.resize` | O | Read API accepts dimensions 1–4096, bounded aspect-preserving resize without enlargement, exact centre crop with cover or stretching with squeeze; admin can restrict allowed sizes. | [R10-S6](<#r10-s6>) |
| **Preserve animated uploads**<br>`formats.animated` | C | v2.7.8 skips local compression, WebP conversion and Telegram server-side compression for animated GIF, WebP and APNG. | [R10-S2](<#r10-s2>) |
| **Hosting REST API**<br>`integration.api` | C | Upload/read/delete/batch-delete/list/random-image/token endpoints with CORS; reads support HEAD and channel-dependent byte ranges, but not Range combined with resizing. | [R10-S3](<#r10-s3>), [R10-S6](<#r10-s6>) |
| **Hugging Face dataset storage**<br>`integration.huggingface_storage` | O | Configured token and dataset repository support private repositories and LFS-based large-file uploads. | [R10-S4](<#r10-s4>) |
| **Telegram and Discord payload channels**<br>`integration.messaging_storage` | O | Store payloads through configured bots/channels, with optional proxy URLs and Discord Nitro setting; not private local disk storage. | [R10-S4](<#r10-s4>) |
| **R2 and S3-compatible backends**<br>`integration.object_storage` | O | Configure R2 bindings or S3 endpoint, credentials, bucket, optional region/path-style/CDN and custom User-Agent; quota/cost varies by provider. | [R10-S4](<#r10-s4>), [R10-S2](<#r10-s2>) |
| **External upload/client ecosystem**<br>`integration.plugins` | P | README links browser, WordPress/Typecho/Obsidian/OpenList integrations; feature guide names PicGo. The separately named Satellite desktop client has its own deployment finding rather than being inferred from API availability. | [R10-S1](<#r10-s1>), [R10-S3](<#r10-s3>) |
| **Expose a WebDAV filesystem**<br>`integration.webdav` | O | Enable /dav with separate credentials and destination channel for PROPFIND/GET/PUT/DELETE/OPTIONS/MKCOL. Feature overview also lists MOVE, while dedicated method table omits it; MOVE compatibility needs verification. | [R10-S5](<#r10-s5>), [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>) |
| **Use a WebDAV storage provider**<br>`integration.webdav_backend` | O | Configure service URL, optional credentials/custom headers/public HTTP URL and automatic parent-directory creation. | [R10-S4](<#r10-s4>) |
| **Multiple upload entry methods**<br>`library.batch_upload` | C | Click, drag/drop, clipboard files or URLs and batch upload with live progress and retry. | [R10-S3](<#r10-s3>) |
| **Download hosted files**<br>`library.export_originals` | C | File Details and batch management offer downloads; untransformed Read API returns original file content. | [R10-S2](<#r10-s2>), [R10-S6](<#r10-s6>) |
| **Time-limited hosted-file lifecycle**<br>`library.file_expiry` | O | Live docs describe future-upload expiry presets up to 3650 days, optional uploader choice and scheduled/manual cleanup. Application access stops on expiry, while underlying public links/caches can persist; release parity is unverified. | [R10-S4](<#r10-s4>) |
| **Recursive folder upload**<br>`library.folder_structure` | C | Uploading folders preserves their relative directory structure; upload directory picker supports suggestions/completion. | [R10-S3](<#r10-s3>) |
| **Batch file organization**<br>`library.move_copy` | C | Move files among directories with a visual destination picker; batch copy actions primarily concern generated links, so payload-copy semantics are not assumed. | [R10-S3](<#r10-s3>), [R10-S2](<#r10-s2>) |
| **Batched index rebuilding**<br>`maintenance.cache_reset` | C | Admin can rebuild the file index in batches to avoid runtime CPU limits. | [R10-S3](<#r10-s3>) |
| **Hosting metadata display and editing**<br>`metadata.hosting_fields` | C | Shows upload time, size and source IP; supports editing display filename/type and renaming File ID. These are hosting fields, not EXIF/IPTC editing. | [R10-S3](<#r10-s3>) |
| **Single and bulk tag editing**<br>`metadata.tags` | C | Autocomplete and common tags assist editing; multiple selected files can receive tags, preserving existing ones when AI suggestions are added. | [R10-S3](<#r10-s3>), [R10-S2](<#r10-s2>) |
| **External or self-hosted content moderation**<br>`ai.content_moderation` | O | Supports moderatecontent.com API or separately deployed nsfwjs service; moderatecontent free registration is noted unavailable. | [R10-S4](<#r10-s4>) |
| **CDN caching and purge integration**<br>`performance.cdn_cache` | O | Cloudflare delivery caches public responses and avoids Range fragments; configured Cloudflare API credentials can purge cached content after deletion/access changes. | [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>) |
| **Storage balancing and upload failover**<br>`performance.channel_failover` | C | Manage multiple channel configurations, configure load balancing and automatically retry through another available channel after upload failure. | [R10-S1](<#r10-s1>), [R10-S3](<#r10-s3>) |
| **Channel-aware large-file uploads**<br>`performance.chunked_upload` | C | Telegram/R2/S3/Discord support chunking, while Hugging Face uses LFS direct upload. Guide quotes Telegram 20 MB parts and Discord commonly 10/25 MB, subject to provider policy. | [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>) |
| **Hotlink and file-access controls**<br>`privacy.access_rules` | C | Allowed source domains, file/IP allow/block lists and whitelist-only access can restrict public delivery; CDN caches may delay enforcement. | [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>) |
| **Encrypted provider-key storage**<br>`privacy.ai_key_encryption` | O | AI_CONFIG_SECRET encrypts saved API keys; operator must keep a separate backup because secret loss/change makes keys unreadable. This does not encrypt hosted images end-to-end. | [R10-S2](<#r10-s2>), [R10-S4](<#r10-s4>) |
| **Password hashing and configurable sessions**<br>`privacy.session_security` | C | PBKDF2 with legacy password migration, HttpOnly sessions, isolated admin/user login and configurable age. HTTPS-only Secure cookies are configurable and disabled by default. | [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>) |
| **Disable remote telemetry**<br>`privacy.telemetry_control` | C | Admin settings can disable telemetry that may disclose access URLs/domains. v2.7.8 removes remote sampling configuration, not telemetry itself; sampling defaults to 100%. | [R10-S4](<#r10-s4>), [R10-S2](<#r10-s2>) |
| **Uploader IP recording and optional lookup**<br>`privacy.upload_ip_geolocation` | O | Optional custom API receives upload IP and selected JSON fields populate UploadAddress. This is uploader network geolocation, not photo GPS mapping. | [R10-S4](<#r10-s4>) |
| **Batch data backup and restore**<br>`safety.catalogue_backup` | C | Feature guide documents batch file-data backup/restore; whether this includes every remote original rather than hosting records is not specified and must be verified before relying on it. | [R10-S3](<#r10-s3>) |
| **File-type filtering**<br>`search.file_type` | C | Filter listed files by file type, using centralized MIME inference where metadata is missing or generic. | [R10-S3](<#r10-s3>), [R10-S2](<#r10-s2>) |
| **Search names and directories**<br>`search.filename_path` | C | Feature guide lists name and directory search, with recursive expansion configurable in v2.7.8. | [R10-S3](<#r10-s3>), [R10-S2](<#r10-s2>) |
| **Channel and access-status filters**<br>`search.storage_access` | C | Filter by storage channel and access state in addition to name/directory/tag/type. | [R10-S3](<#r10-s3>) |
| **Search file tags**<br>`search.tags` | C | Search/filter by user or AI-applied tags; no semantic embedding search is claimed. | [R10-S3](<#r10-s3>) |
| **Copy URL, Markdown, HTML or BBCode**<br>`sharing.embed_codes` | C | Format preference is independent of content-link preference; choose hosted link or channel-specific Telegram/S3/CDN/WebDAV-public link, with unavailable choices falling back. | [R10-S2](<#r10-s2>) |
| **User and admin management**<br>`sharing.multiuser` | C | Separate admin/user sessions, user upload controls and per-user upload statistics are documented; this does not establish isolated personal photo libraries. | [R10-S3](<#r10-s3>) |
| **Visitor gallery for selected directories**<br>`sharing.public_gallery` | O | Enable unauthenticated browsing only for configured directory roots through /browse paths. | [R10-S4](<#r10-s4>) |
| **Direct hosting links**<br>`sharing.public_links` | C | Ordinary /file paths usually do not require authentication, subject to configured domain/file/moderation rules; links can use custom prefixes. | [R10-S6](<#r10-s6>), [R10-S4](<#r10-s4>) |
| **Scoped API permissions and upload access**<br>`sharing.roles` | C | API tokens independently grant upload/delete/list/manage, can expire and be auto-deleted; web/API uploads use configured authentication codes. | [R10-S3](<#r10-s3>) |

## Limitations and evidence gaps

- **explicit:** External provider limits/costs vary; self-hosting this service is not equivalent to offline originals, E2EE or zero third-party processing. ([R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>))
- **explicit:** Ordinary file links are generally unauthenticated. Moderation/blacklisting/deletion can lag in CDN caches; direct storage links may bypass hosting access restrictions. ([R10-S6](<#r10-s6>), [R10-S4](<#r10-s4>))
- **explicit:** Live expiry docs state Telegram/external-channel cleanup removes only the hosting record, not the remote file. WebDAV-service uploads receive no expiry; public provider URLs remain live until cleanup and cached copies may persist. ([R10-S4](<#r10-s4>))
- **explicit:** Image sizing differs by deployment: JPEG/PNG/WebP everywhere, AVIF Worker/Docker only, GIF resizing Docker only; SVG unsupported. Worker/Docker processing limits originals to 20 MB, and Pages needs enabled Cloudflare transformations plus a custom domain. ([R10-S6](<#r10-s6>), [R10-S4](<#r10-s4>))
- **explicit:** AI supports JPEG/PNG/WebP/AVIF/GIF but not SVG/non-images; manual GIF recognition uses the first decoded frame. Maximum manual batch is 3 with 2 concurrent calls and a 25-second processing deadline; provider format support still applies. ([R10-S4](<#r10-s4>))
- **coverage-gap:** Backup payload completeness, EXIF/IPTC edits, duplicates, face identities and photo semantic search are not established. AI tag recognition is not face recognition or vector search. ([R10-S2](<#r10-s2>), [R10-S3](<#r10-s3>))
- **coverage-gap:** Live docs may exceed frozen release functionality; automatic upload AI/expiry marked medium confidence. MOVE appears in overview but not WebDAV method table. ([R10-S2](<#r10-s2>), [R10-S3](<#r10-s3>), [R10-S4](<#r10-s4>), [R10-S5](<#r10-s5>))
- **Coverage gap:** Live-doc versus v2.7.8 parity unresolved for automatic tagging and expiry.
- **Coverage gap:** Dedicated AI URL returned 404; complete AI configuration section and release notes inspected instead.
- **Coverage gap:** No live provider or integration tests; backup scope and WebDAV MOVE discrepancy remain.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R10-S1

[CloudFlare ImgBed README](<https://github.com/MarSeventh/CloudFlare-ImgBed/blob/85636c5bc7393e80e0fe229a8f73538ad5c65ee4/README.md>)
- Kind/ref: readme; 85636c5bc7393e80e0fe229a8f73538ad5c65ee4
- Sections inspected: Complete README: introduction, architecture, deployment/docs and ecosystem
- Establishes: Runtime/storage architecture and integration boundaries.

### R10-S2

[v2.7.8 release notes](<https://github.com/MarSeventh/CloudFlare-ImgBed/releases/tag/v2.7.8>)
- Kind/ref: release; v2.7.8
- Sections inspected: Complete release notes
- Establishes: Manual AI tags, link controls, previews, animation preservation, telemetry and compatibility fixes.

### R10-S3

[Official feature guide](<https://cfbed.sanyue.de/en/guide/features.html>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Detailed upload, organization, access, API, performance and deployment inventory.

### R10-S4

[Configuration guide](<https://cfbed.sanyue.de/en/deployment/configuration.html>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page including channels, expiry, AI, telemetry, public gallery and environment variables
- Establishes: Provider requirements, privacy disclosures, exact limits and lifecycle caveats.

### R10-S5

[WebDAV service manual](<https://cfbed.sanyue.de/en/api/webdav.html>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Optional /dav endpoint, methods and external-client use.

### R10-S6

[Read API](<https://cfbed.sanyue.de/en/api/file.html>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete page
- Establishes: Public reads, ranges, image transforms, deployment-specific formats and failure handling.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
