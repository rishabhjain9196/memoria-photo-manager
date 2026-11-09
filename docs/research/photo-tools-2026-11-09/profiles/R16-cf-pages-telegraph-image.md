# R16 — cf-pages/Telegraph-Image

[Repository](<https://github.com/cf-pages/Telegraph-Image>) · 4,707 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Cloudflare Pages file host with Telegram or optional R2 storage, public upload links and an optional KV-backed administration interface; not a private local photo catalogue.

**Deployment:** Cloudflare Pages with file-based Functions; Git-connected or Wrangler Pages deployment; Browser upload and optional administration UI

**Storage:** Default uploads are sent through a Telegram bot to a channel. Optional R2 stores new uploads in a bound bucket. Optional Cloudflare KV holds file metadata, moderation decisions and short-link mappings. Provider-specific IDs keep existing links readable after changing providers.

**Privacy/network behavior:** Cloudflare handles requests and Telegram normally stores file content; R2 and Workers AI are optional Cloudflare services. Upload and dashboard authentication are disabled unless configured. Remote telemetry is opt-out. Dashboard libraries load from jsDelivr. No end-to-end encryption claim is established.

**License metadata:** CC0-1.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** No GitHub release returned
**Repository pushed at:** 2026-07-27T03:57:46Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [ef69018df196](<https://github.com/cf-pages/Telegraph-Image/commit/ef69018df1967708ec026a671e3976f5524ff490>).
**Product lineage:** cf-pages/Telegraph-Image.

## Maturity and availability caveats

- Frozen main commit ef69018df1967708ec026a671e3976f5524ff490; manifest has no release.
- Original Telegraph upload API is closed: deployments must configure Telegram or R2 instead.
- The July 2026 README includes substantial storage, moderation, upload and interface changes; older Telegraph deployment guides are not equivalent.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Workers AI image review**<br>`ai.content_moderation` | O | AI binding plus KV enables remote vision moderation; verdicts are cached per file. Adult-content classifications redirect to a block page. Review failures are explicitly fail-open. | [R16-S1](<#r16-s1>) |
| **Legacy ModerateContent integration**<br>`ai.legacy_moderation_provider` | O | Existing ModerateContent keys remain usable only for old Telegraph-hosted files; new registrations are closed and Telegram Bot API files cannot be reviewed by this provider. | [R16-S1](<#r16-s1>) |
| **Moderation model discovery and fallback**<br>`ai.moderation_model_fallback` | O | Override the vision model or use a built-in fallback chain. Optional Cloudflare account credentials discover active vision models, exclude retired ones and cache the catalogue for six hours. | [R16-S1](<#r16-s1>) |
| **Recorded file total**<br>`analytics.library_statistics` | O | KV-backed administration displays total recorded images and each item's list/moderation state. | [R16-S1](<#r16-s1>) |
| **Administrative grid and waterfall views**<br>`browse.grid` | O | Binding img_url KV enables dashboard grid/waterfall layouts, online image preview and batch record selection. | [R16-S1](<#r16-s1>) |
| **Browser-native media and PDF previews**<br>`browse.inline_file_preview` | C | Images, video, audio and PDF are served for inline browser opening rather than forced download; browser format support still applies. | [R16-S1](<#r16-s1>) |
| **Cursor-paginated dashboard**<br>`browse.pagination` | O | KV listing supports cursor/load-more and a limit defaulting to 100 and capped at 1000; internal short-link/cache keys are excluded from returned file keys. | [R16-S1](<#r16-s1>), [R16-S3](<#r16-s3>) |
| **Administrative preview zoom and rotation**<br>`browse.zoom` | O | Dashboard preview allows zooming in/out and viewer rotation; documentation does not establish rewriting the original image. | [R16-S1](<#r16-s1>) |
| **Cloudflare Pages hosting**<br>`deployment.cloudflare_pages` | C | Deploy through Git integration or Wrangler Pages; a free pages.dev hostname and custom domains are documented. This is a Pages Functions project, not a directly deployable Worker entry point. | [R16-S1](<#r16-s1>) |
| **Environment-driven site customization**<br>`deployment.site_branding` | O | Configure site/header name, title, background and hiding the dashboard entry via GET /api/config; hiding the entry does not make /admin inaccessible. | [R16-S1](<#r16-s1>) |
| **Browser upload interface**<br>`deployment.web` | C | Cloudflare Pages serves the upload homepage; current homepage is dependency-free, while the older Nuxt page remains separately accessible. | [R16-S1](<#r16-s1>) |
| **Multipart upload API**<br>`integration.api` | C | POST /upload accepts multipart file and returns a JSON array containing src. It works with configurable upload clients such as PicGo. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>) |
| **Alternative Cloudflare R2 storage**<br>`integration.object_storage` | O | An img_r2 bucket and STORAGE_PROVIDER=r2 redirect new uploads to R2. Self-describing provider IDs preserve access to old Telegram and R2 files across switches. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>) |
| **Telegram channel storage**<br>`integration.telegram_storage` | C | A bot token and channel/chat ID route uploads into a channel where the bot is an administrator; source files reside on Telegram. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>) |
| **Batch drag-and-drop and clipboard uploads**<br>`library.batch_upload` | C | Upload multiple files by selection, drag-and-drop or paste, with per-file progress. | [R16-S1](<#r16-s1>) |
| **Deployment self-check**<br>`maintenance.configuration_diagnostics` | C | Homepage identifies missing environment variables or bindings and tells operators where to configure them before the first upload. | [R16-S1](<#r16-s1>) |
| **Record-only administrative deletion**<br>`maintenance.record_removal` | O | Delete removes the dashboard record, not the Telegram/Telegraph original; later access can recreate a record. Blocking access uses the blacklist instead. | [R16-S1](<#r16-s1>) |
| **Optional fork auto-updates**<br>`maintenance.upstream_sync` | O | An enabled GitHub Actions upstream-sync workflow updates the fork hourly, after which connected Pages deployment can rebuild. | [R16-S1](<#r16-s1>) |
| **Dashboard rename**<br>`metadata.display_name_edit` | O | Administration supports renaming listed files; July 2026 notes record a fix to this workflow. Physical Telegram object renaming is not established. | [R16-S1](<#r16-s1>) |
| **Telemetry opt-out**<br>`privacy.telemetry_control` | O | disable_telemetry disables documented remote telemetry; file-serving middleware and upload handler otherwise call telemetry functions. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>), [R16-S4](<#r16-s4>) |
| **Dashboard prefix search**<br>`search.filename_path` | O | README describes server-side filename-prefix search; list endpoint passes the supplied prefix to KV rather than providing full-text catalogue search. | [R16-S1](<#r16-s1>), [R16-S3](<#r16-s3>) |
| **Referer allowlist**<br>`sharing.anti_hotlinking` | O | ALLOWED_REFERERS accepts exact and wildcard-subdomain hosts. Other referring sites receive 403, but absent referers and the host's own domain remain allowed; this is not private-link authentication. | [R16-S1](<#r16-s1>) |
| **File allow/block lists**<br>`sharing.blacklist_whitelist` | O | KV records can be blacklisted to block loading or whitelisted to bypass moderation; whitelist-only mode requires approval before serving. | [R16-S1](<#r16-s1>) |
| **Optional administrative authentication**<br>`sharing.dashboard_authentication` | O | BASIC_USER and BASIC_PASS enable dashboard login. Cloudflare Access is an alternative, with both /admin and /api/manage/* requiring protection. | [R16-S1](<#r16-s1>) |
| **Public uploads by default**<br>`sharing.guest_upload` | C | Anonymous uploads remain enabled unless both upload Basic Auth variables are configured. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>) |
| **Direct file links and embed formats**<br>`sharing.public_links` | C | Upload returns a /file path; interface copies URL, Markdown, BBCode or HTML links. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>) |
| **Persistent configurable short links**<br>`sharing.short_urls` | O | KV plus ENABLE_SHORT_URLS allocates short IDs of 4–16 characters, default six. Old long URLs continue to resolve. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>) |
| **Separate upload authentication**<br>`sharing.upload_authentication` | O | UPLOAD_BASIC_USER and UPLOAD_BASIC_PASS protect both browser and multipart API uploads independently of dashboard credentials. | [R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>) |

## Limitations and evidence gaps

- **coverage-gap:** Focused interface-localization review found no explicit translated-UI capability in inspected primary feature/configuration documentation. English/Chinese README editions are not evidence of a language-switchable application; localization remains undocumented here. ([R16-S1](<#r16-s1>))
- **explicit:** Telegram uploads may accept approximately 50 MB, but Bot API getFile can serve only up to 20 MB: 20 MB is the documented practical file limit. Roughly 20 messages/minute/channel also constrains throughput. R2 avoids these Telegram limits, not all service quotas. ([R16-S1](<#r16-s1>))
- **explicit:** README's unlimited-image claim is qualified by Cloudflare request/KV/R2/AI quotas. It quotes 100,000 free Function requests/day, KV 1,000 writes/deletes/lists and 100,000 reads/day; these are project-documented quotas, not independently verified current pricing. ([R16-S1](<#r16-s1>))
- **explicit:** Dashboard login and upload protection default off. Record deletion is not erasure of hosted content. Moderation is fail-open and referer protection allows clients without a referer. ([R16-S1](<#r16-s1>))
- **explicit:** Environment/binding changes require redeployment. The dashboard can render blank when jsDelivr is unreachable. Regional Cloudflare performance is not guaranteed. ([R16-S1](<#r16-s1>))
- **coverage-gap:** No inspected evidence establishes EXIF catalogue search, albums/people recognition, duplicate detection, local offline operation, encrypted storage or recoverable file-deletion history. ([R16-S1](<#r16-s1>), [R16-S2](<#r16-s2>), [R16-S3](<#r16-s3>))
- **Coverage gap:** No standalone manual or release exists in the frozen manifest; comprehensive README feature/configuration/update sections and source were inspected.
- **Coverage gap:** No evidence for local-catalogue, deduplication, EXIF-management or encrypted-vault capabilities.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R16-S1

[Telegraph-Image README](<https://github.com/cf-pages/Telegraph-Image/blob/ef69018df1967708ec026a671e3976f5524ff490/README.md>)
- Kind/ref: readme; ef69018df1967708ec026a671e3976f5524ff490
- Sections inspected: Complete README: configuration, features, optional features, API, quotas, FAQ and update log
- Establishes: Deployment, user workflows, optional services, privacy defaults and concrete hosting limits.

### R16-S2

[Upload request handler](<https://github.com/cf-pages/Telegraph-Image/blob/ef69018df1967708ec026a671e3976f5524ff490/functions/upload.js>)
- Kind/ref: code; ef69018df1967708ec026a671e3976f5524ff490
- Sections inspected: Complete onRequestPost implementation
- Establishes: Authentication, provider dispatch, KV metadata and short-link allocation.

### R16-S3

[Administration listing API](<https://github.com/cf-pages/Telegraph-Image/blob/ef69018df1967708ec026a671e3976f5524ff490/functions/api/manage/list.js>)
- Kind/ref: code; ef69018df1967708ec026a671e3976f5524ff490
- Sections inspected: Complete onRequest implementation
- Establishes: Cursor pagination, prefix filtering, page limits and hidden internal bookkeeping keys.

### R16-S4

[File route middleware](<https://github.com/cf-pages/Telegraph-Image/blob/ef69018df1967708ec026a671e3976f5524ff490/functions/file/_middleware.js>)
- Kind/ref: code; ef69018df1967708ec026a671e3976f5524ff490
- Sections inspected: Complete file
- Establishes: File-serving routes attach error handling and telemetry middleware.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
