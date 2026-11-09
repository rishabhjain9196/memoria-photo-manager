# R47 — andrii-kryvoviaz/slink

[Repository](<https://github.com/andrii-kryvoviaz/slink>) · 1,620 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Self-hosted image-upload and sharing platform centered on individually controlled image/collection links, hierarchical tags and configurable storage/authentication.

**Deployment:** Self-hosted Docker/container web application with Symfony backend and SvelteKit frontend

**Storage:** Managed uploads with local storage by default, optionally SMB or S3-compatible storage. Local/SMB use separate images and cache directories; S3 stores image objects at bucket root and transformed variants under cache. HEIC/TIFF uploads are converted to JPEG rather than preserved in their original format.

**Privacy/network behavior:** Private-by-default share records with publication/password/expiry gates, not E2EE. UI Copy Link publishes immediately and collections auto-publish on creation; guest uploads are public. EXIF stripping defaults on. Remote storage and OIDC are optional external dependencies. Documentation recommends proxy HTTPS/rate limiting and non-root containers.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v1.14.6 (2026-11-06T23:30:21Z)
**Repository pushed at:** 2026-11-06T23:15:23Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [aefc97065c20](<https://github.com/andrii-kryvoviaz/slink/commit/aefc97065c20c543299d23b7315551c979705378>).
**Product lineage:** andrii-kryvoviaz/slink.

## Maturity and availability caveats

- Manifest release v1.14.6 (2026-11-06); README pinned to aefc97065c20c543299d23b7315551c979705378.
- Official live documentation inspected 2026-11-09 can be ahead of the pinned release; detailed controls are labeled as documented, not runtime-verified.
- New share model migrates legacy links automatically except customized transformation links, which require recreation.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Shareable collections**<br>`albums.manual` | C | Group images into a collection and share via one link; collection shares auto-publish upon creation, unlike API-created image shares. | [R47-S1](<#r47-s1>), [R47-S5](<#r47-s5>) |
| **Administrative statistics**<br>`analytics.library_statistics` | C | Admin dashboard provides statistics/analytics and storage-consumption metrics; documentation does not substantiate throughput benchmarks. | [R47-S1](<#r47-s1>), [R47-S6](<#r47-s6>) |
| **Light and dark interface modes**<br>`browse.dark_theme` | C | README explicitly supports both light and dark application modes; interface translation is inventoried separately under deployment.localization. | [R47-S1](<#r47-s1>) |
| **Upload-history grid and list**<br>`browse.grid` | C | Upload history offers list/grid views of the user's uploads. | [R47-S1](<#r47-s1>) |
| **Container deployment and persistence**<br>`deployment.docker` | C | Environment variables configure Docker/Compose deployments; local images require a host mount at /app/slink/images for persistence. | [R47-S2](<#r47-s2>), [R47-S3](<#r47-s3>) |
| **Nine documented UI languages**<br>`deployment.localization` | C | README and introduction explicitly list English, German, Spanish, French, Italian, Japanese, Polish, Ukrainian and Chinese user interfaces. This is interface localization, not a claim about search-language or model support. | [R47-S1](<#r47-s1>), [R47-S6](<#r47-s6>) |
| **Self-hosted web image host**<br>`deployment.selfhosted` | C | Symfony/SvelteKit server with browser upload, management and sharing; container settings and persistent mounts are documented. | [R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>), [R47-S3](<#r47-s3>) |
| **Browser image-sharing application**<br>`deployment.web` | C | Slink provides its upload, collections, share management and administrative interface through its SvelteKit web frontend backed by Symfony; Docker hosts the service and does not imply native desktop/mobile application builds. | [R47-S1](<#r47-s1>), [R47-S5](<#r47-s5>), [R47-S6](<#r47-s6>) |
| **Upload image compression**<br>`editing.image_compression` | C | JPEG compression quality is configurable from 1 to 100, default 80. | [R47-S2](<#r47-s2>) |
| **Forced output format**<br>`editing.format_conversion` | C | Optional setting converts all uploads to WebP, AVIF or JPEG; animated conversion is separately opt-in and disabled by default. | [R47-S2](<#r47-s2>) |
| **AVIF upload and output**<br>`formats.avif` | C | AVIF is a supported upload format and configurable conversion target. | [R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>) |
| **HEIC ingestion with JPEG conversion**<br>`formats.heic` | C | HEIC and TIFF are accepted but converted to JPG before saving for compatibility. | [R47-S6](<#r47-s6>) |
| **SVG and other image uploads**<br>`formats.svg` | C | Supported list includes SVG, BMP, ICO, PNG, JPEG, WebP and GIF; broad image support is not evidence of video support. | [R47-S6](<#r47-s6>) |
| **External upload API**<br>`integration.api` | C | Bearer-authenticated POST /api/external/upload accepts multipart images and returns URL/metadata; login-protected endpoint exports ShareX config. | [R47-S8](<#r47-s8>) |
| **S3 and compatible providers**<br>`integration.object_storage` | O | Supports AWS or custom endpoint/path-style S3 storage; AWS can use instance IAM role instead of static keys, but role mode is ignored for custom providers. | [R47-S3](<#r47-s3>) |
| **Named expiring API keys**<br>`integration.personal_api_keys` | C | Keys have optional expiry, are displayed once and can be revoked; docs warn they permit uploads on the user's behalf. | [R47-S8](<#r47-s8>) |
| **ShareX uploader configuration**<br>`integration.sharex` | P | Slink generates a .sxcu configuration for the separately installed ShareX client to automate screenshot uploads with an API key. | [R47-S1](<#r47-s1>), [R47-S8](<#r47-s8>) |
| **SMB/CIFS image storage**<br>`integration.smb_storage` | O | Configured network share credentials store originals and transformed caches in automatically created slink/images and slink/cache directories. | [R47-S3](<#r47-s3>) |
| **Parallel multi-file image uploads**<br>`library.batch_upload` | C | README explicitly supports uploading multiple image files in parallel, with progress tracking and error handling for each file. | [R47-S1](<#r47-s1>), [R47-S6](<#r47-s6>) |
| **Upload duplicate detection**<br>`library.deduplicate_import` | C | Detects duplicate images during upload and notifies the user; enabled by default. Inspected docs do not specify hash/perceptual algorithm or a batch cleanup tool. | [R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>), [R47-S6](<#r47-s6>) |
| **Concurrent multi-image upload**<br>`library.managed_upload` | C | Parallel multi-file upload tracks progress and per-file errors; maximum image size is configurable and chunk size defaults to 2 MB within a 1–25 MB range. | [R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>) |
| **Interaction notifications**<br>`maintenance.notifications` | C | Notifies users of interactions with their images; specific delivery channels are not established. | [R47-S1](<#r47-s1>) |
| **Bookmark public images**<br>`metadata.bookmarks` | C | Users save public images for later access; distinguished from changing ownership or copying originals. | [R47-S1](<#r47-s1>) |
| **Discussion on public images**<br>`metadata.comments` | C | Users can leave comments on publicly visible images. | [R47-S1](<#r47-s1>) |
| **Nested tags**<br>`metadata.hierarchical_tags` | C | Hierarchical tag management has a dedicated management page and tag search capabilities. | [R47-S1](<#r47-s1>), [R47-S6](<#r47-s6>) |
| **Strip uploaded EXIF**<br>`metadata.strip` | C | IMAGE_STRIP_EXIF_METADATA defaults true; administrators can override at runtime. No preservation of untouched original metadata is implied. | [R47-S2](<#r47-s2>) |
| **Administrative image moderation**<br>`moderation.admin_visibility` | C | Administrators manage image content/visibility, users, storage and settings; stored settings override corresponding environment variables. | [R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>) |
| **Transformed image cache**<br>`performance.thumbnail_cache` | C | Storage layouts separate uploaded images from transformed/cache objects locally, on SMB and under the S3 cache prefix. | [R47-S3](<#r47-s3>) |
| **Tag-based discovery**<br>`search.tags` | C | README explicitly couples nested tags with search; arbitrary boolean/saved-query semantics are not documented. | [R47-S1](<#r47-s1>) |
| **Require accounts to view shares**<br>`sharing.authenticated_share_policy` | C | Instance settings separately require sign-in for media shares or collection shares; anonymous access to public routes is independently configurable. | [R47-S2](<#r47-s2>) |
| **Built-in brute-force/rate protection**<br>`sharing.builtin_rate_limiting` | N | Security guide explicitly says built-in rate limiting and brute-force protection are absent and recommends a reverse proxy for them. | [R47-S4](<#r47-s4>) |
| **Automatic share expiry**<br>`sharing.expiring_links` | C | Expiry timestamp can be set or cleared; passing it auto-revokes access. | [R47-S5](<#r47-s5>) |
| **Opt-in anonymous uploads**<br>`sharing.guest_upload` | C | Disabled by default and admin-enabled; guests use drag/drop or file selection, uploads are public, and guests cannot edit/delete submitted images. | [R47-S2](<#r47-s2>), [R47-S7](<#r47-s7>) |
| **Accounts and approval**<br>`sharing.multiuser` | C | Email/password registration and login with configurable signup and admin approval; default environment reference requires approval before sign-in. | [R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>) |
| **OIDC identity-provider login**<br>`integration.oidc` | O | Google/Authentik/Keycloak/Authelia/Pocket ID presets or custom OIDC; matches sub then verified email, uses S256 PKCE, and stores client configuration encrypted. | [R47-S9](<#r47-s9>) |
| **Password-gated shares**<br>`sharing.password_links` | C | Each share can set/change/remove a password; stored password is hashed and successful unlock creates a short-lived cookie. | [R47-S5](<#r47-s5>) |
| **Per-provider registration/approval overrides**<br>`sharing.provider_registration_policy` | O | OIDC providers can inherit/allow/block registration and inherit/require/auto-approve new accounts independently of global signup policy; existing users are unaffected. | [R47-S9](<#r47-s9>) |
| **Public Explore view**<br>`sharing.public_gallery` | C | Explore shows images users have made publicly visible; admin may disallow unauthenticated public-route access or force uploads public. | [R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>) |
| **Explicitly published image shares**<br>`sharing.public_links` | C | Programmatically created shares start unpublished; UI Copy Link creates/reuses and publishes atomically. Unpublishing returns 404; holding a URL alone is insufficient if its share is revoked. | [R47-S4](<#r47-s4>), [R47-S5](<#r47-s5>) |
| **Unified share management**<br>`sharing.share_inventory` | C | /shares lists owned image and collection shares; filters type, expired/has/no-expiry and password protection, with free-text underlying-name search. | [R47-S5](<#r47-s5>) |
| **Configurable URL shortening**<br>`sharing.short_urls` | C | Shortening is enabled by default; generated code length defaults to 8 and is clamped between 4 and 32 characters. | [R47-S2](<#r47-s2>) |

## Limitations and evidence gaps

- **explicit:** No built-in rate limiting or brute-force protection; container runs as root by default. Guide recommends reverse proxy HTTPS/rate limiting and non-root configuration. ([R47-S4](<#r47-s4>))
- **explicit:** Guest uploads are public and cannot be edited/deleted by their guest uploader; docs recommend trusted/private environments due to content/moderation risks. ([R47-S7](<#r47-s7>))
- **explicit:** Copy Link publishes image shares immediately and collection shares auto-publish; private-by-default wording does not mean copied links stay inaccessible. ([R47-S5](<#r47-s5>))
- **explicit:** Legacy custom transformation shares are not auto-migrated. HEIC/TIFF are converted before storage, so this is not guaranteed untouched-original archival. ([R47-S5](<#r47-s5>), [R47-S6](<#r47-s6>))
- **coverage-gap:** Deduplication algorithm, photo recognition, full video library, existing-folder scan, trash/undo and E2EE were not established by inspected sources. ([R47-S1](<#r47-s1>), [R47-S2](<#r47-s2>), [R47-S6](<#r47-s6>))
- **Coverage gap:** Live manual may lead manifest release; no runtime validation performed.
- **Coverage gap:** README's upcoming-features link no longer exposed a roadmap in inspected introduction, so no roadmap features were invented.
- **Coverage gap:** Image transform parameter API beyond conversion settings was not established.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R47-S1

[Slink README](<https://github.com/andrii-kryvoviaz/slink/blob/aefc97065c20c543299d23b7315551c979705378/README.md>)
- Kind/ref: readme; aefc97065c20c543299d23b7315551c979705378
- Sections inspected: Complete features, deployment links and scope
- Establishes: Sharing, uploads, organization, authentication, admin and storage inventory.

### R47-S2

[Environment variables](<https://docs.slinkapp.io/configuration/01-environment-variables/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete general, access, processing, sharing, storage, SSL and bootstrap tables
- Establishes: Defaults and runtime overrides, EXIF, dedup, conversion, chunk limits and access policies.

### R47-S3

[Storage providers](<https://docs.slinkapp.io/configuration/02-storage-provider/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete local, SMB, S3-compatible and directory-layout sections
- Establishes: Storage persistence, transformed-object paths, IAM versus static credentials.

### R47-S4

[Security guide](<https://docs.slinkapp.io/security/01-overview/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete overview, share access and container-user notes
- Establishes: No built-in rate/brute-force protection; share-route gates and proxy/container requirements.

### R47-S5

[Share management](<https://docs.slinkapp.io/usage/01-share-management/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete per-share controls, creation, search and migration
- Establishes: Publish/unpublish, password cookies, expiry, creation-time publication and migration exceptions.

### R47-S6

[Introduction and feature catalogue](<https://docs.slinkapp.io/getting-started/01-introduction/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete features and HEIC/TIFF footnote
- Establishes: Organization/social features and exact format conversion caveat.

### R47-S7

[Guest uploads](<https://docs.slinkapp.io/usage/04-guest-upload/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete enabling, behavior and risk notice
- Establishes: Admin opt-in, public visibility and lack of guest edit/delete access.

### R47-S8

[API key management](<https://docs.slinkapp.io/usage/02-api-key-management/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete creation, authentication and endpoint reference
- Establishes: Named expiring/revocable keys, one-time secret display, upload and ShareX configuration.

### R47-S9

[SSO/OIDC providers](<https://docs.slinkapp.io/configuration/03-sso-providers/>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete providers, setup, registration overrides, account matching and SSL/Authelia notes
- Establishes: Verified-email linking, PKCE, encrypted client settings and per-provider enrollment controls.

### R47-S10

[Slink v1.14.6](<https://github.com/andrii-kryvoviaz/slink/releases/tag/v1.14.6>)
- Kind/ref: release; v1.14.6
- Sections inspected: Complete patch notes
- Establishes: Image URL/cache response fix and dependency/runtime updates.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
