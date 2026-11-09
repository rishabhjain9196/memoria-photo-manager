# R39 — Afilmory/afilmory

[Repository](<https://github.com/Afilmory/afilmory>) · 2,670 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Photographer-oriented published gallery with a GPU/HDR viewer, storage-adapter build pipeline and optional database-backed multi-tenant CMS.

**Deployment:** Self-hosted web gallery and builder CLI; Docker deployment documented through official companion repository; Optional backend/SaaS mode with PostgreSQL and Redis; Native iOS 18+ companion, distributed via TestFlight link

**Storage:** Static mode builds a JSON manifest and JPEG thumbnails from configured originals, retaining URLs into S3-compatible/B2/GitHub/local/Eagle storage. Backend mode stores photo metadata in PostgreSQL and injects a tenant-specific live manifest; originals remain in configured object/file storage. Optional plugins publish derived assets separately.

**Privacy/network behavior:** Gallery publication and remote storage are explicit design choices, not end-to-end encrypted personal backup. A local provider avoids mandatory cloud storage; maps, external providers, Git synchronization, hosted SaaS, OAuth and push notifications introduce deployment-dependent network services.

**License metadata:** NOASSERTION. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** No GitHub release returned
**Repository pushed at:** 2026-11-03T09:02:23Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [cdeada392f4b](<https://github.com/Afilmory/afilmory/commit/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1>).
**Product lineage:** Afilmory/afilmory.

## Maturity and availability caveats

- Pinned cdeada392f4bcdc9e8ddaceb61eed6051f93caa1; manifest has no tagged release. Inventory describes pinned main documentation/source, not a released binary guarantee.
- README describes multi-size thumbnails, but detailed pipeline documents one 600px JPEG per photo; generation behavior is recorded at the more specific level.
- License is ANL v1.0: MIT library code and AGPL project code with UI attribution. SaaS guide additionally says commercial rights are not granted, in tension with the root license's no-additional-restrictions wording; commercial adopters need clarification rather than assuming ordinary permissive licensing.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Responsive masonry layout**<br>`browse.grid` | C | Masonry layout adapts gallery presentation to screen size. | [R39-S1](<#r39-s1>) |
| **Mobile touch viewer**<br>`browse.touch` | C | Pinch and double-tap controls accompany a responsive gallery, with native iOS browsing also available. | [R39-S1](<#r39-s1>) |
| **GPU image navigation**<br>`browse.zoom` | C | WebGPU-first viewer falls back to WebGL without navigator.gpu; supports zoom/pan/pinch and double-tap cycling among fit, fill and 100%. | [R39-S1](<#r39-s1>) |
| **iOS gallery companion**<br>`deployment.ios` | C | Native Swift/UIKit client for iOS 18+ browses galleries and supports push notifications; README links TestFlight, not a claimed camera-roll backup feature. | [R39-S1](<#r39-s1>) |
| **Localized gallery interface**<br>`deployment.localization` | C | README's application Core Capabilities explicitly lists English, Simplified Chinese, Traditional Chinese with Hong Kong/Taiwan variants, Japanese and Korean internationalization. This is UI language support, not AI query-language support; native iOS language parity is not established by that statement. | [R39-S1](<#r39-s1>) |
| **Self-hosting**<br>`deployment.selfhosted` | C | Manual builder/web deployment and an official companion Docker guide are documented; a managed hosted service is an alternative, not required. | [R39-S1](<#r39-s1>) |
| **Published web gallery**<br>`deployment.web` | C | Gallery SPA can use a generated static manifest or an SSR host that injects manifest and SEO/OpenGraph data. | [R39-S1](<#r39-s1>), [R39-S2](<#r39-s2>) |
| **HDR gain-map display**<br>`formats.hdr` | C | Detects JPEG gain maps including Apple HDR photos and composites HDR on compatible high-dynamic-range displays. | [R39-S1](<#r39-s1>), [R39-S2](<#r39-s2>) |
| **HEIC/HEIF ingestion**<br>`formats.heic` | C | Build pipeline converts HEIC/HEIF to JPEG and applies EXIF orientation; README also lists TIFF/BMP conversion. | [R39-S1](<#r39-s1>), [R39-S2](<#r39-s2>) |
| **Paired iPhone Live Photos**<br>`formats.live_photos` | C | Lists storage objects before image filtering to identify paired videos and enables playback; detection is configurable. | [R39-S1](<#r39-s1>), [R39-S2](<#r39-s2>), [R39-S8](<#r39-s8>) |
| **Embedded Motion Photos**<br>`formats.motion_photos` | C | Pipeline detects embedded Motion Photo video or a paired Live Photo, never both for the same item. | [R39-S2](<#r39-s2>) |
| **MapLibre geographic gallery**<br>`geo.map` | C | Interactive map uses GPS coordinates; site configuration exposes map style/projection. Offline basemap availability is not established. | [R39-S1](<#r39-s1>) |
| **Billing and plan enforcement**<br>`integration.billing_quotas` | O | Backend includes Creem integration, tenant plans/overrides and request-level usage/quota enforcement. Specific hosted paid-only feature entitlements are not enumerated in inspected docs. | [R39-S7](<#r39-s7>) |
| **Central OAuth gateway**<br>`integration.central_oauth` | O | Optional SaaS architecture uses a single OAuth callback domain that routes provider responses to per-tenant sessions. | [R39-S7](<#r39-s7>) |
| **Builder command interface**<br>`integration.cli` | C | CLI supports configuration display, plain logs versus TUI, incremental/rebuild modes and nonzero error exits. | [R39-S6](<#r39-s6>) |
| **Eagle library publication**<br>`integration.eagle` | O | Eagle 4 source publishes an existing Eagle library with folder/tag filters and folder-to-tag mapping. | [R39-S5](<#r39-s5>) |
| **Derived-asset Git synchronization**<br>`integration.git_asset_sync` | O | Bundled opt-in plugin reuses manifest/thumbnails from a Git repository and optionally commits/pushes changes; push needs a token and Git on PATH. | [R39-S3](<#r39-s3>) |
| **GitHub-backed originals**<br>`integration.github_storage` | O | GitHub storage is documented for small galleries/demos with about 1 GB recommended repository size, not unlimited archival scale. | [R39-S5](<#r39-s5>) |
| **Object storage adapters**<br>`integration.object_storage` | O | Providers support S3-compatible services, B2, Aliyun OSS and Tencent COS, with provider-specific domains/CDN configuration. | [R39-S1](<#r39-s1>), [R39-S5](<#r39-s5>) |
| **Builder lifecycle plugins**<br>`integration.plugins` | C | Hooks before/after builds, processing and manifest save permit custom logic and storage rewriting; custom StorageProvider implementations can add backends. | [R39-S1](<#r39-s1>), [R39-S3](<#r39-s3>) |
| **Local filesystem source**<br>`library.existing_folders` | O | Local provider publishes files on the same host without an external storage dependency; configure basePath and baseUrl. | [R39-S5](<#r39-s5>), [R39-S8](<#r39-s8>) |
| **Incremental storage synchronization**<br>`library.incremental_scan` | C | New objects are processed; LastModified changes rebuild metadata; missing thumbnails regenerate; unchanged manifest/thumbnails are reused and orphaned thumbnails are cleaned after source deletion. | [R39-S2](<#r39-s2>) |
| **Selective rebuild controls**<br>`maintenance.selective_reset` | C | --force rebuilds all; --force-manifest refreshes metadata while retaining valid thumbnails; --force-thumbnails regenerates thumbnail derivatives. | [R39-S6](<#r39-s6>) |
| **Photographic EXIF display**<br>`metadata.exif_read` | C | ExifTool extracts camera/lens, focal length, aperture, ISO, GPS and other exposure metadata for viewer and manifest display. | [R39-S1](<#r39-s1>), [R39-S2](<#r39-s2>) |
| **Folder-derived tags**<br>`metadata.folder_tags` | C | Auto-generates tags from directory structure; Eagle integration can also map folders to tags. | [R39-S1](<#r39-s1>), [R39-S5](<#r39-s5>) |
| **Fujifilm film recipes**<br>`metadata.fujifilm_recipes` | C | Displays extracted Fujifilm film-simulation settings. | [R39-S1](<#r39-s1>), [R39-S2](<#r39-s2>) |
| **Runtime metadata editing**<br>`metadata.live_cms` | O | Backend CMS edits titles/tags/descriptions and enabled state in PostgreSQL, with fresh data on refetch/page load without a builder run; tenant admins can also upload. | [R39-S4](<#r39-s4>) |
| **Named XMP region overlay**<br>`metadata.region_overlay` | C | Region boxes/labels can appear over placeholders and remain aligned while zooming; affected photos switch to a DOM viewer. This consumes existing regions, not automatic face detection. | [R39-S2](<#r39-s2>) |
| **Image tone analysis**<br>`metadata.tone_analysis` | C | Pipeline computes tone information and stores it in manifest records; this is not documented object tagging or semantic search. | [R39-S2](<#r39-s2>) |
| **Embedded keywords and regions**<br>`metadata.xmp_read` | C | Extracts XMP keywords/regions into manifest arrays and merges keywords into gallery tags; missing arrays trigger incremental backfill. | [R39-S2](<#r39-s2>), [R39-S8](<#r39-s8>) |
| **Parallel build workers**<br>`performance.parallel_scan` | C | Worker/cluster modes and per-worker/download concurrency are configurable. Tasks begin largest-first to reduce tail latency; cluster mode needs sufficient queued work. | [R39-S2](<#r39-s2>), [R39-S6](<#r39-s6>), [R39-S8](<#r39-s8>) |
| **Continue past failed photos**<br>`performance.per_item_failure_isolation` | C | Per-photo errors mark an item failed and continue, while fatal errors terminate nonzero; logs/TUI report counts. | [R39-S2](<#r39-s2>), [R39-S6](<#r39-s6>) |
| **Remote thumbnail publication**<br>`performance.remote_thumbnail_storage` | O | Bundled opt-in thumbnail-storage plugin uploads derivatives to default/secondary storage, rewrites URLs, deduplicates uploads per run and falls back to local URLs on upload failure. | [R39-S3](<#r39-s3>) |
| **Thumbnail and ThumbHash derivatives**<br>`performance.thumbnail_cache` | C | Detailed pipeline writes one 600px quality-100 JPEG thumbnail per photo and ThumbHash placeholders; derivatives are reused independently of manifest refreshes. | [R39-S2](<#r39-s2>) |
| **Off-thread tiled decoding**<br>`performance.tiled_rendering` | C | Large photos decode in a worker and stream tiles to the GPU instead of decoding entirely on the main UI thread. | [R39-S1](<#r39-s1>) |
| **Non-writing builder inspection**<br>`safety.builder_dry_run` | C | --dry-run performs processing but does not save manifests, clean thumbnails or run plugin side effects; --key-regex limits inspection to matched storage keys. | [R39-S6](<#r39-s6>) |
| **Tag-driven gallery filtering**<br>`search.tags` | C | Pipeline documents merging embedded keywords into existing tags for tag-driven UI; Eagle provider additionally filters by folders and tags. | [R39-S2](<#r39-s2>), [R39-S5](<#r39-s5>) |
| **Visitor comments and reactions**<br>`sharing.comments_reactions` | O | README explicitly limits visitor comments/reactions to backend-powered galleries, rather than static-only deployments. | [R39-S1](<#r39-s1>) |
| **Verified tenant domains**<br>`sharing.custom_domains` | O | Backend accepts per-tenant custom domains after DNS CNAME/TXT verification as well as ordinary tenant subdomains. | [R39-S7](<#r39-s7>) |
| **Multi-tenant hosted galleries**<br>`sharing.multiuser` | O | One backend serves isolated tenant workspaces resolved by slug/domain, each with storage and plan configuration. | [R39-S4](<#r39-s4>), [R39-S7](<#r39-s7>) |
| **Tenant roles and superadmin**<br>`sharing.roles` | O | Tenant roles gate edits and a superadmin manages tenants, content, suspensions/bans and plan overrides. | [R39-S4](<#r39-s4>), [R39-S7](<#r39-s7>) |
| **Social share and rich previews**<br>`sharing.social_export` | C | Supports image sharing with dynamic OpenGraph images/SEO metadata and embedding through a public SDK. | [R39-S1](<#r39-s1>) |

## Limitations and evidence gaps

- **explicit:** Region overlay alignment assumes embedded coordinates correspond to the EXIF-rotated image and currently switches those photos from GPU to DOM rendering. ([R39-S2](<#r39-s2>))
- **explicit:** Backend caching must not share injected tenant data across tenants; authenticated responses need short TTLs or cache bypass. ([R39-S4](<#r39-s4>))
- **explicit:** GitHub provider is recommended for small collections, and moving providers requires rebuilding/migrating manifest and thumbnail references. ([R39-S4](<#r39-s4>), [R39-S5](<#r39-s5>))
- **coverage-gap:** Root license and SaaS commercial-rights wording are inconsistent; exact paid hosted feature gates and commercial permission need clarification. ([R39-S7](<#r39-s7>), [R39-S9](<#r39-s9>))
- **coverage-gap:** Face recognition, semantic search, duplicate cleanup, recoverable trash, mobile backup, private album access rules and E2EE are not established by these sources. XMP face-region display must not be conflated with inference. ([R39-S1](<#r39-s1>), [R39-S2](<#r39-s2>), [R39-S4](<#r39-s4>))
- **Coverage gap:** No tagged release exists in manifest; sources are pinned main.
- **Coverage gap:** Commercial-rights wording and hosted plan entitlements unresolved; performance/renderer behavior was not executed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R39-S1

[README](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/README.md>)
- Kind/ref: readme; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire README
- Establishes: Gallery/viewer, formats, storage integrations, iOS client and static/backend deployment.

### R39-S2

[Processing flow](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/apps/docs/contents/builder/pipeline.mdx>)
- Kind/ref: manual; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire page
- Establishes: Incremental rules, EXIF/XMP, region overlays, derived outputs and failure handling.

### R39-S3

[Built-in builder plugins](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/apps/docs/contents/builder/built-ins.mdx>)
- Kind/ref: manual; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire page
- Establishes: Opt-in Git-derived-asset synchronization and thumbnail storage plugins.

### R39-S4

[CMS and live updates](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/apps/docs/contents/saas/cms.mdx>)
- Kind/ref: manual; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire page
- Establishes: Backend upload/edit workflow, tenant roles and cache-isolation caveats.

### R39-S5

[Storage providers](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/apps/docs/contents/storage/providers/index.mdx>)
- Kind/ref: manual; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire page
- Establishes: Cloud/local/GitHub/Eagle options, provider limitations and recommendations.

### R39-S6

[Builder CLI and run modes](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/apps/docs/contents/builder/cli.mdx>)
- Kind/ref: manual; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire page
- Establishes: Dry-run subsets, selective rebuilds, concurrency and exit semantics.

### R39-S7

[SaaS mode](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/apps/docs/contents/saas/index.mdx>)
- Kind/ref: manual; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire page
- Establishes: Optional multi-tenant domains, auth, billing enforcement and licensing caveat.

### R39-S8

[Default builder configuration](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/builder.config.default.ts>)
- Kind/ref: code; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Entire file
- Establishes: Actual storage/exclusion/concurrency and XMP configuration defaults.

### R39-S9

[Attribution Network License v1.0](<https://github.com/Afilmory/afilmory/blob/cdeada392f4bcdc9e8ddaceb61eed6051f93caa1/LICENSE>)
- Kind/ref: manual; cdeada392f4bcdc9e8ddaceb61eed6051f93caa1
- Sections inspected: Sections 1–7 including MIT and attribution terms; standard AGPL appendix not used as feature evidence
- Establishes: Dual-track file classification and attribution obligations.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
