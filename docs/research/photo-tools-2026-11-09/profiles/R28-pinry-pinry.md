# R28 — pinry/pinry

[Repository](<https://github.com/pinry/pinry>) · 3,432 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Self-hosted visual bookmarking/image-board application centered on tagged pins and public/private boards, not a filesystem photo-library manager.

**Deployment:** Docker images for AMD64, ARMv7 and ARMv8; Self-hosted Django backend and browser frontend; Separate browser extensions and CLI companion

**Storage:** Pins store source URL/referrer, description, owner and tags, referencing server-stored images with standard/thumbnail/square derivatives; boards have many-to-many pin membership. Docker persists SQLite database, media and settings under its mounted data directory, with optional PostgreSQL/MySQL configuration.

**Privacy/network behavior:** Can be self-hosted with global login-only browsing and private pins/boards. Remote-image capture makes server HTTP requests to source sites; profile API includes Gravatar-related data. Owner/privacy checks are application controls, not evidence that static media URLs are encrypted or access-protected.

**License metadata:** BSD-2-Clause. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v2.1.13 (2024-10-03T08:22:43Z)
**Repository pushed at:** 2026-01-05T16:46:25Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [05476b112401](<https://github.com/pinry/pinry/commit/05476b112401cf34a38bfbffc67c37f5f6c3b38f>).
**Product lineage:** pinry/pinry.

## Maturity and availability caveats

- Frozen commit 05476b112401cf34a38bfbffc67c37f5f6c3b38f; latest release v2.1.13 (2024-10-03), a small fix release.
- Plugin system describes itself as a naive released implementation still under development.
- README broadly mentions videos and webpages; inspected ingestion code validates images, so full video playback and arbitrary webpage archiving remain unclear.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Owner-managed boards**<br>`albums.manual` | C | Boards have per-owner unique names and many-to-many pin membership, with pin counts and a cover derived from the first pin. | [R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>) |
| **Tiling visual pin board**<br>`browse.grid` | C | Browser interface presents saved image pins in a skim-friendly tiled board with online preview. | [R28-S1](<#r28-s1>) |
| **Native saved-video playback**<br>`browse.video_playback` | ? | README description includes videos but detailed feature list emphasizes images and URL ingestion explicitly validates image content; playback semantics/formats are not established. | [R28-S1](<#r28-s1>), [R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>) |
| **Multi-architecture Docker distribution**<br>`deployment.docker` | C | Published images cover ARMv7/ARMv8/AMD64 and persist all data via a mounted directory or named volume. | [R28-S1](<#r28-s1>), [R28-S2](<#r28-s2>) |
| **Translated Pinry interface**<br>`deployment.localization` | C | README explicitly lists implemented i18n support for English, Simplified Chinese and French in its application feature checklist. | [R28-S1](<#r28-s1>) |
| **Self-hosted Pinry server**<br>`deployment.selfhosted` | C | Official Docker guide runs a user-controlled server with a persistent data volume, database and local settings; alternate database backends can be configured. | [R28-S1](<#r28-s1>), [R28-S2](<#r28-s2>) |
| **Browser-based image boards**<br>`deployment.web` | C | Pinry's tiled pin/board interface is reached through the running instance's web address; browser extensions are separate capture companions. | [R28-S1](<#r28-s1>), [R28-S2](<#r28-s2>) |
| **Token-authenticated resource API**<br>`integration.api` | C | User profile supplies a token; DRF exposes interactive API plus pin/board creation/editing and image upload. Board add/remove ID lists are capped at ten per update. | [R28-S3](<#r28-s3>), [R28-S8](<#r28-s8>), [R28-S9](<#r28-s9>) |
| **Chrome/Firefox capture extensions**<br>`integration.browser_extensions` | P | Official docs link a separately maintained browser-pinry extension and browser stores for adding web content. | [R28-S1](<#r28-s1>), [R28-S5](<#r28-s5>) |
| **Command-line pin submission**<br>`integration.cli` | P | README links pinry-cli-py companion for adding an image or URL; not a built-in executable in this repository. | [R28-S1](<#r28-s1>) |
| **Choose catalogue database backend**<br>`storage.database_choices` | O | Docker defaults to SQLite for small personal deployments; guide documents switching local settings to PostgreSQL or MySQL. | [R28-S2](<#r28-s2>) |
| **Image-processing lifecycle hooks**<br>`integration.plugins` | O | Configure Python plugin objects in ENABLED_PLUGINS; hooks run before image/thumbnail creation and can modify objects. Documentation offers watermarking as an example, not a ready-made watermark UI. | [R28-S4](<#r28-s4>) |
| **Upload images into pins**<br>`library.import_copy` | C | Image creation endpoint accepts uploaded content; pin creation can reference image_by_id instead of fetching a URL. | [R28-S8](<#r28-s8>), [R28-S9](<#r28-s9>) |
| **Fetch and retain remote images**<br>`library.url_import` | C | Creates pins from image URLs, optionally preserving referrer; server downloads content, verifies it is an image and creates local image/thumbnail records. | [R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>) |
| **Archive arbitrary webpage content**<br>`library.webpage_archive` | ? | README mentions webpages but model/API evidence establishes image URL, referrer and description rather than a full HTML capture/archive pipeline. | [R28-S1](<#r28-s1>), [R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>) |
| **Delete associated pin media**<br>`maintenance.media_cleanup` | C | Deleting a pin triggers deletion of its image record; example settings enable image-file auto-deletion. This is cleanup, not recoverable trash. | [R28-S7](<#r28-s7>), [R28-S11](<#r28-s11>) |
| **Pin descriptions and source references**<br>`metadata.comments` | C | Pins retain description, source URL and referrer in addition to publication time and submitting user. | [R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>) |
| **Shared pin tagging**<br>`metadata.tags` | C | Pins have multiple tags; serializer can create missing tags when assigned. Design distinguishes global tag classification from single-owner boards. | [R28-S6](<#r28-s6>), [R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>) |
| **Pre-generated display images**<br>`performance.thumbnail_cache` | C | Image ingestion generates standard, thumbnail and square derivatives; example sizes are 600-wide, 240-wide and cropped 125-square, configurable by IMAGE_SIZES. | [R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>), [R28-S11](<#r28-s11>) |
| **Disable anonymous browsing**<br>`sharing.private_site` | O | Example configuration has PUBLIC controlling whether pins are viewable without login, separate from per-object private flags. | [R28-S11](<#r28-s11>) |
| **Backup persisted server data**<br>`safety.catalogue_backup` | C | Docker guide instructs copying the mounted data directory containing database, settings and pins; no automatic scheduled backup/restore UI is claimed. | [R28-S2](<#r28-s2>) |
| **Find boards by name**<br>`search.board_name` | C | Board search uses name; autocomplete and owner-name filters help select boards. | [R28-S1](<#r28-s1>), [R28-S8](<#r28-s8>) |
| **Filter pins by owner or board**<br>`search.owner_board_filters` | C | API supports submitter username and board ID filters and lists pins/boards newest-first by ID. | [R28-S8](<#r28-s8>) |
| **Filter pins by tags**<br>`search.tags` | C | README and API expose tag-name pin filtering plus tag autocomplete; no semantic or image similarity search is established. | [R28-S1](<#r28-s1>), [R28-S8](<#r28-s8>) |
| **Multiple accounts and signup control**<br>`sharing.multiuser` | C | Multiuser application with configurable self-registration; Docker guide describes enabling new registrations in persisted local settings. | [R28-S1](<#r28-s1>), [R28-S2](<#r28-s2>), [R28-S11](<#r28-s11>) |
| **Public boards and pins**<br>`sharing.public_links` | C | Public/private booleans exist independently on pins and boards; public boards support sharing by board. This does not establish password/expiry-link support. | [R28-S1](<#r28-s1>), [R28-S6](<#r28-s6>), [R28-S7](<#r28-s7>) |
| **Owner editing and private content**<br>`sharing.roles` | C | Object permission classes allow owner mutations and owner-only access to private pins/boards; list queries filter private records for nonowners and anonymous requests. | [R28-S8](<#r28-s8>), [R28-S9](<#r28-s9>), [R28-S10](<#r28-s10>) |

## Limitations and evidence gaps

- **explicit:** Board design is single-owner, not evidence of collaboratively editable multi-owner albums; private pin and board flags are separate. ([R28-S6](<#r28-s6>), [R28-S7](<#r28-s7>), [R28-S10](<#r28-s10>))
- **explicit:** Remote URL image creation is synchronous in the inspected model (asynchronous processing remains a TODO), and board membership patch lists allow at most ten IDs per list. ([R28-S7](<#r28-s7>), [R28-S9](<#r28-s9>))
- **coverage-gap:** Private record filtering is not proof of protection of direct static-media URLs; no encryption, expiring links or media retention recovery was established. ([R28-S9](<#r28-s9>), [R28-S10](<#r28-s10>), [R28-S11](<#r28-s11>))
- **coverage-gap:** No EXIF/GPS catalogue, duplicate detection, filesystem scan/watch, AI people or video playback implementation was established by the available docs/source. ([R28-S1](<#r28-s1>), [R28-S7](<#r28-s7>), [R28-S8](<#r28-s8>))
- **explicit:** Plugin API is early; available-plugin catalogue is blank/coming soon, so example watermarking should not be treated as a finished feature. ([R28-S4](<#r28-s4>))
- **Coverage gap:** Image-centric implementation does not substantiate all broad README video/webpage wording.
- **Coverage gap:** No native photo-library AI, metadata or duplicate workflows established.
- **Coverage gap:** Static asset authorization was not audited; private flags are not a security guarantee.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R28-S1

[Pinry README](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/README.md>)
- Kind/ref: readme; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete README
- Establishes: Board features, tag/name search, clients, API and Docker platforms.

### R28-S2

[Docker installation and backup](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/docs/src/install-with-docker.md>)
- Kind/ref: manual; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete guide
- Establishes: Persistent data, registration setting, backup and database choices.

### R28-S3

[Token API](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/docs/src/api.md>)
- Kind/ref: manual; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete guide
- Establishes: Profile-issued token and interactive DRF API.

### R28-S4

[Plugin system](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/docs/src/plugin-system.md>)
- Kind/ref: manual; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete guide
- Establishes: Image/thumbnail pre-creation hooks and explicit immaturity of plugin ecosystem.

### R28-S5

[Browser extensions](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/docs/src/extensions.md>)
- Kind/ref: manual; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete document
- Establishes: Separate Chrome and Firefox clients.

### R28-S6

[Boards and tags design](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/docs/src/theories.md>)
- Kind/ref: manual; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete document
- Establishes: Single-user board ownership versus cross-user tag organization.

### R28-S7

[Image, board and pin models](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/core/models.py>)
- Kind/ref: code; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete file
- Establishes: Remote fetch/validation, derivatives, pin descriptions and ownership.

### R28-S8

[API viewsets](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/core/views.py>)
- Kind/ref: code; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete file
- Establishes: Pin/board filters, ordering and autocomplete.

### R28-S9

[Pin/board serializers](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/core/serializers.py>)
- Kind/ref: code; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete file
- Establishes: Uploaded-image versus URL creation, visibility filtering and bounded board membership updates.

### R28-S10

[Object permissions](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/core/permissions.py>)
- Kind/ref: code; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete file
- Establishes: Owner-edit and owner-only-private permission classes.

### R28-S11

[Example runtime settings](<https://github.com/pinry/pinry/blob/05476b112401cf34a38bfbffc67c37f5f6c3b38f/pinry/settings/local_settings.example.py>)
- Kind/ref: code; 05476b112401cf34a38bfbffc67c37f5f6c3b38f
- Sections inspected: Complete file
- Establishes: Registration/public switches, media location, derivative dimensions and auto-deletion setting.

### R28-S12

[v2.1.13 release](<https://github.com/pinry/pinry/releases/tag/v2.1.13>)
- Kind/ref: release; v2.1.13
- Sections inspected: Complete release note
- Establishes: Docker x86 and overflow/documentation fixes.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
