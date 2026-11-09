# R44 — photonixapp/photonix

[Repository](<https://github.com/photonixapp/photonix>) · 1,955 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Self-hosted, tag-centric photo server with local object/style/color/face analysis and photo-version grouping; several sharing/mobile/video ambitions remain explicitly future work.

**Deployment:** Docker Compose server with browser UI; Android/iPhone companion clients requiring a server; Documented image-analysis benchmarks include Raspberry Pi 4

**Storage:** Mounts existing photo directories; database, thumbnails and derived caches are stored separately. PostgreSQL stores catalogue/users/tags; Redis provides locking and service state. Multiple private/shared libraries can coexist.

**Privacy/network behavior:** Photo analysis executes on the self-hosted server rather than external image-classification APIs; country/city lookup uses bundled geographic datasets. Browser access and server authentication do not imply E2EE or an offline map basemap. Operator must back up originals/catalogue.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v0.24.0 (2021-11-18T22:14:31Z)
**Repository pushed at:** 2026-10-28T23:01:42Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [7d2674f0ebf7](<https://github.com/photonixapp/photonix/commit/7d2674f0ebf7851788748d6000e72f082d3c7248>).
**Product lineage:** photonixapp/photonix.

## Maturity and availability caveats

- Repository pinned 7d2674f0ebf7851788748d6000e72f082d3c7248, pushed 2026-10-28; latest tagged release remains v0.24.0 dated 2021-11-18.
- README explicitly describes pre-1.0, incomplete development with potentially broken parts; do not infer abandonment from release age or production readiness from recent commits.
- Official website combines available features with future-tense proposals; these are separated below. Documentation repository is pinned independently to 104cd498c2ca906576ccc0e4a84632e7de7834ff.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Object content tags**<br>`ai.auto_tags` | C | Object classifier runs within Photonix, stores bounding boxes and uses detected area as a significance signal; models are not a hosted Google API. | [R44-S2](<#r44-s2>) |
| **Unknown-person groups**<br>`ai.face_clustering` | C | Unmatched faces form conservatively grouped Unknown person tags during import. Annoy nearest-neighbor indexes rebuild at five-minute intervals when needed, with direct comparison for newly added faces. | [R44-S4](<#r44-s4>) |
| **Approve/reject/edit face labels**<br>`ai.face_corrections` | C | UI shows bounding boxes and supports approval, rejection and editing automatic face tags; documentation describes merging groups as the preferred correction path. | [R44-S4](<#r44-s4>) |
| **MTCNN facial regions**<br>`ai.face_detection` | C | MTCNN detects face boxes and landmarks, creating initially unknown location-specific face tags. | [R44-S4](<#r44-s4>) |
| **Rename face groups**<br>`ai.face_naming` | C | Users label automatically grouped unknown people with names, allowing personalized recognition without training a full new face model. | [R44-S2](<#r44-s2>), [R44-S4](<#r44-s4>) |
| **FaceNet identity matching**<br>`ai.face_recognition` | C | Aligned face crops generate 128-value FaceNet embeddings; Euclidean similarity thresholds match identities across images. | [R44-S4](<#r44-s4>) |
| **Server-local classifiers**<br>`ai.local_inference` | C | Object/face/style/color and location analysis run inside the deployment; configuration enables/disables individual classifiers to manage CPU/RAM. | [R44-S2](<#r44-s2>), [R44-S4](<#r44-s4>), [R44-S5](<#r44-s5>) |
| **Artistic style classifier**<br>`ai.style_classification` | C | Classifies style labels such as geometric, minimalist and noir, distinct from literal object labels. | [R44-S2](<#r44-s2>) |
| **Full-screen photo viewer**<br>`browse.fullscreen` | C | Viewer exposes camera/time metadata and analysis results by scrolling, including colors, objects and map location. | [R44-S2](<#r44-s2>) |
| **Presentation and multi-screen slideshow**<br>`browse.slideshow` | R | Official site describes phone-controlled TV/client presentations as future work, not an available feature. | [R44-S2](<#r44-s2>) |
| **Video support**<br>`browse.video_playback` | R | Official site explicitly says limited video-file support is intended soon; current documented scope focuses on photography. | [R44-S2](<#r44-s2>) |
| **Android companion**<br>`deployment.android` | C | Official site links a Google Play client providing access to an existing server; it is not a standalone gallery or currently documented backup client. | [R44-S2](<#r44-s2>) |
| **Compose deployment**<br>`deployment.docker` | C | Prebuilt application image is configured with PostgreSQL/Redis and mounted photos; data persists outside containers. | [R44-S1](<#r44-s1>), [R44-S5](<#r44-s5>) |
| **iPhone companion**<br>`deployment.ios` | C | Official site links an App Store client requiring a Photonix server. | [R44-S2](<#r44-s2>) |
| **Self-hosted photo server**<br>`deployment.selfhosted` | C | Runs on a home/server host and exposes a browser interface to authenticated devices; Docker Compose is the recommended setup. | [R44-S1](<#r44-s1>) |
| **Browser photo interface**<br>`deployment.web` | C | Web-based filtering and full-screen viewing work from logged-in desktop/tablet/mobile devices. | [R44-S1](<#r44-s1>), [R44-S2](<#r44-s2>) |
| **Version-aware RAW/edit grouping**<br>`formats.raw_jpeg_pairs` | C | Compares timestamps and other metadata to group camera RAW, camera JPEG and edited versions; latest inferred edit becomes the preview while other versions remain accessible. This is not exact hash deduplication. | [R44-S2](<#r44-s2>) |
| **Photo location map**<br>`geo.map` | C | Official feature overview documents viewing geographic location on a map; no offline tile-cache guarantee is inferred from offline geocoding. | [R44-S2](<#r44-s2>) |
| **Bundled country/city lookup**<br>`geo.offline_geocoding` | C | Uses World Borders polygons and GeoNames top-1000 cities locally with no API calls; returns nearest city only within 10 km. Coarse coastlines may miss beach locations. | [R44-S4](<#r44-s4>) |
| **Administrative commands**<br>`integration.cli` | C | create_library and create_user management commands provision additional accounts/library access; initial setup may use createsuperuser. | [R44-S1](<#r44-s1>), [R44-S3](<#r44-s3>) |
| **Existing photo directories**<br>`library.existing_folders` | C | Mount existing photo storage instead of copying into a proprietary container; database/thumbnails remain separate from originals. | [R44-S1](<#r44-s1>) |
| **Live directory monitoring**<br>`library.filesystem_watch` | C | Recursive inotify watches respond to completed writes, added files, directory additions, moves/renames and deletions. Per-LibraryPath watch_for_changes settings enable/disable watches. | [R44-S6](<#r44-s6>) |
| **Automatic camera-roll uploads**<br>`library.mobile_backup` | R | Official mobile-app section explicitly says automatic camera-roll uploading is a feature to come; present apps provide server access. | [R44-S2](<#r44-s2>) |
| **Private and shared libraries**<br>`library.multiple_libraries` | C | Multiple libraries coexist in one installation and users switch through the account menu; CLI assigns accounts to libraries. | [R44-S3](<#r44-s3>) |
| **Manually select preferred edit**<br>`library.preferred_version` | R | Current grouping chooses the inferred latest edit; manually preferring an older edit is described as upcoming. | [R44-S2](<#r44-s2>) |
| **Camera-derived metadata**<br>`metadata.exif_read` | C | Uses aperture, shutter speed, GPS and capture date/time as searchable information; source adds camera, lens, ISO and focal-length constraints. | [R44-S2](<#r44-s2>), [R44-S7](<#r44-s7>) |
| **User and generated tags**<br>`metadata.tags` | C | User-assigned concepts coexist with camera-derived and automatically classified tags; multiple tags per photo enable combined filtering. | [R44-S2](<#r44-s2>) |
| **Deferred classifier queues**<br>`performance.background_jobs` | C | Disabling an analysis type stops processing but newly imported photos remain queued and are analyzed when it is re-enabled. | [R44-S5](<#r44-s5>) |
| **Separate thumbnail/cache storage**<br>`performance.thumbnail_cache` | C | Thumbnails and cache data are outside the originals' directory; v0.24.0 addresses corrupt-image thumbnail crashes. | [R44-S1](<#r44-s1>), [R44-S8](<#r44-s8>) |
| **Self-controlled image processing**<br>`privacy.no_upload_required` | C | Mounted originals and local classifiers avoid mandatory third-party image upload; operating a remotely accessible server remains the user's responsibility. | [R44-S1](<#r44-s1>), [R44-S2](<#r44-s2>), [R44-S4](<#r44-s4>) |
| **Human-readable date filtering**<br>`search.calendar_terms` | C | Parses month names/abbreviations, day ordinals and years into capture-date constraints; when a month lacks a year, selects the current or most recent applicable year. | [R44-S7](<#r44-s7>) |
| **Weighted color discovery**<br>`search.colors` | C | A fixed color palette is compared with a 32x32 resampled image using weighted HSV distance; results retain sufficiently significant color proportions. | [R44-S2](<#r44-s2>), [R44-S4](<#r44-s4>) |
| **Technical shooting filters**<br>`search.metadata` | C | Supports camera/lens IDs, aperture/ISO/focal-length ranges, exposure values, flash and metering/drive/shooting modes. | [R44-S7](<#r44-s7>) |
| **Rating-range search**<br>`search.ratings` | C | rating filters apply an inclusive star-rating range; this proves filtering, not the location or format of rating writes. | [R44-S7](<#r44-s7>) |
| **Tag query filtering**<br>`search.tags` | C | Queries resolve tag IDs or case-insensitive tag-name substrings; multiple filters are applied to the photo queryset. | [R44-S7](<#r44-s7>) |
| **Account/library management UI**<br>`sharing.management_ui` | R | User/library guide states management UI is yet to be developed and directs administrators to CLI provisioning. | [R44-S3](<#r44-s3>) |
| **Multiple accounts**<br>`sharing.multiuser` | C | Separate usernames/passwords support private user libraries and administrator-configured shared libraries. | [R44-S3](<#r44-s3>) |
| **External photo/album sharing**<br>`sharing.public_links` | R | Sharing-online section asks users to wait until the feature is fully ready; it must not be counted as existing public-link sharing. | [R44-S2](<#r44-s2>) |
| **Fine-grained library roles**<br>`sharing.roles` | ? | Website discusses read-only/read-write roles and invitations in future tense; inspected current user guide establishes membership but not all UI/permission workflows. | [R44-S2](<#r44-s2>), [R44-S3](<#r44-s3>) |

## Limitations and evidence gaps

- **coverage-gap:** The inspected official feature overview, configuration guide and repository documentation do not establish translated UI or a language selector; locale-related tree discovery found no positive evidence, which is not proof of absence. ([R44-S1](<#r44-s1>), [R44-S2](<#r44-s2>), [R44-S5](<#r44-s5>))
- **explicit:** README explicitly warns that the project is not feature-complete for 1.0 and requires operator-managed backups. ([R44-S1](<#r44-s1>))
- **explicit:** Offline geocoding only considers a coarse country map and 1,000 major cities within 10 km; it is not complete street/address geocoding. ([R44-S4](<#r44-s4>))
- **explicit:** Available mobile apps require a server and do not establish camera-roll backup. Public sharing, presentations and video support are future-tense on the official site. ([R44-S2](<#r44-s2>))
- **coverage-gap:** Exact content dedupe, destructive cleanup safety, metadata writeback/sidecars, end-to-end encryption and a guaranteed offline map are not established. Version grouping must not be recast as exact duplicate detection. ([R44-S1](<#r44-s1>), [R44-S2](<#r44-s2>), [R44-S4](<#r44-s4>))
- **Coverage gap:** Official website has old/future-tense sections; planned and unclear entries are not treated as shipped functionality.
- **Coverage gap:** No runtime verification of recently changed master against the 2021 stable tag.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R44-S1

[README](<https://github.com/photonixapp/photonix/blob/7d2674f0ebf7851788748d6000e72f082d3c7248/README.md>)
- Kind/ref: readme; 7d2674f0ebf7851788748d6000e72f082d3c7248
- Sections inspected: Complete README
- Establishes: Deployment, in-place directories, separate catalogue storage and pre-1.0 warning.

### R44-S2

[Official feature overview](<https://photonix.org/>)
- Kind/ref: official-site; live-docs
- Sections inspected: All Main Features sections, excluding testimonial claims
- Establishes: Available tagging/viewing/version grouping and explicitly future sharing/mobile/video features.

### R44-S3

[Users and libraries](<https://github.com/photonixapp/photonix-website/blob/104cd498c2ca906576ccc0e4a84632e7de7834ff/docs/users_libraries.md>)
- Kind/ref: manual; 104cd498c2ca906576ccc0e4a84632e7de7834ff
- Sections inspected: Entire page
- Establishes: Private/shared libraries and CLI provisioning versus planned management UI.

### R44-S4

[Image analysis](<https://github.com/photonixapp/photonix-website/blob/104cd498c2ca906576ccc0e4a84632e7de7834ff/docs/developer/image_analysis.md>)
- Kind/ref: manual; 104cd498c2ca906576ccc0e4a84632e7de7834ff
- Sections inspected: Entire page
- Establishes: Color histogram, offline geocoding and detailed face detection/recognition/clustering pipeline.

### R44-S5

[Configuration](<https://github.com/photonixapp/photonix-website/blob/104cd498c2ca906576ccc0e4a84632e7de7834ff/docs/configuration.md>)
- Kind/ref: manual; 104cd498c2ca906576ccc0e4a84632e7de7834ff
- Sections inspected: Entire page
- Establishes: Per-classifier enable/disable, queued analysis, environment settings and claimed Pi benchmark costs.

### R44-S6

[Photo directory watcher](<https://github.com/photonixapp/photonix/blob/7d2674f0ebf7851788748d6000e72f082d3c7248/photonix/photos/management/commands/watch_photos.py>)
- Kind/ref: code; 7d2674f0ebf7851788748d6000e72f082d3c7248
- Sections inspected: Entire file
- Establishes: Per-path local inotify watches and handling additions/changes/moves/deletions.

### R44-S7

[Photo query filtering](<https://github.com/photonixapp/photonix/blob/7d2674f0ebf7851788748d6000e72f082d3c7248/photonix/photos/utils/filter_photos.py>)
- Kind/ref: code; 7d2674f0ebf7851788748d6000e72f082d3c7248
- Sections inspected: Entire file
- Establishes: Actual camera/lens/exposure/rating/tag/date filter semantics.

### R44-S8

[v0.24.0](<https://github.com/photonixapp/photonix/releases/tag/v0.24.0>)
- Kind/ref: release; v0.24.0
- Sections inspected: Complete release body
- Establishes: Dependency updates and corrupt-image thumbnail failure fix.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
