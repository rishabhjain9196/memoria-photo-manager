# R37 — hooram/ownphotos

[Repository](<https://github.com/hooram/ownphotos>) · 2,757 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Legacy self-hosted photo catalogue with locally run recognition, date/place/person/event groupings and experimental analytics; development moved to LibrePhotos.

**Deployment:** Docker Compose with separate Django backend, React frontend, reverse proxy, PostgreSQL and Redis

**Storage:** Administrators assign filesystem scan directories per user. Models retain original image paths and database metadata, generate multiple thumbnail sizes and face crops, and serve originals through protected proxy routes. Nextcloud scanning copies remote contents to backend storage.

**Privacy/network behavior:** Photo analysis uses server-local face_recognition and Places365 code; Mapbox reverse geocoding requires an external API key and sends location lookups. Self-hosting is not E2EE. Deployment examples contain placeholder admin credentials and secrets that must be changed.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** No GitHub release returned
**Repository pushed at:** 2022-12-07T23:36:50Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [180de5746468](<https://github.com/hooram/ownphotos/commit/180de5746468ec64b725723e03657dc21317f3a9>).
**Product lineage:** OwnPhotos-LibrePhotos.

## Maturity and availability caveats

- README explicitly labels this the old project for archive only and directs users to LibrePhotos; manifest has no release and last push in 2022.
- Profile is confined to pinned dev 180de5746468ec64b725723e03657dc21317f3a9, not features of current LibrePhotos.
- README describes a very early-stage experiment. Its sharing roadmap is stale relative to implemented backend handlers; code-supported capabilities below do not establish a polished or currently deployable UI.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Automatic scene and content descriptions**<br>`ai.auto_tags` | C | Active Places365 path stores attributes, scene categories and environment words in search_captions and creates thing albums. Densecap is named in README but disabled in the default caption-generation method. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>) |
| **Experimental on-demand im2txt captions**<br>`ai.captioning` | ? | A routed owner-checked handler calls _generate_captions_im2txt, but automatic im2txt and densecap paths are explicitly disabled and deployability/model availability was not established. | [R37-S3](<#r37-s3>), [R37-S4](<#r37-s4>), [R37-S5](<#r37-s5>) |
| **Face-clustering endpoint**<br>`ai.face_clustering` | C | Registered clusterfaces handler invokes cluster_faces for the requesting user; README identifies scikit-learn classification/clustering. No specific clustering accuracy is established. | [R37-S1](<#r37-s1>), [R37-S4](<#r37-s4>), [R37-S5](<#r37-s5>) |
| **Relabel or remove face detections**<br>`ai.face_corrections` | C | Owner-checked handlers relabel selected faces or delete their face records without deleting the parent photograph. | [R37-S5](<#r37-s5>) |
| **Face regions and crops**<br>`ai.face_detection` | C | face_recognition detects locations/encodings on thumbnails and persists face coordinates, encodings and JPEG crops. | [R37-S3](<#r37-s3>) |
| **Manually label people**<br>`ai.face_naming` | C | Selected face IDs can be assigned a person's name; manual labels are marked non-inferred with confidence 1. | [R37-S1](<#r37-s1>), [R37-S5](<#r37-s5>) |
| **Train classifier from labeled faces**<br>`ai.face_recognition` | C | README describes labeling a sample and training a classifier to name remaining faces; training handler queues a per-user task. | [R37-S1](<#r37-s1>), [R37-S5](<#r37-s5>) |
| **Server-local recognition**<br>`ai.local_inference` | C | Photo methods call local face_recognition, Places365 inference and Im2Vec(cuda=False); this establishes local processing paths, not all-service offline operation. | [R37-S3](<#r37-s3>) |
| **Add undetected faces roadmap**<br>`ai.manual_face_regions` | R | Tagging an undetected face is explicitly listed as upcoming, distinct from naming an already detected face. | [R37-S1](<#r37-s1>) |
| **Automatic thing and scene albums**<br>`albums.content_categories` | C | Places365 attributes and categories each generate owner-scoped AlbumThing collections with representative cover photos. | [R37-S3](<#r37-s3>) |
| **Automatic event albums and titles**<br>`albums.events` | C | Queues event generation and title regeneration; title model combines weekday/time, common places and people, with special multi-day and weekend wording. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>), [R37-S5](<#r37-s5>) |
| **Place-level collections**<br>`albums.locations` | C | Mapbox location features create owner-scoped place albums at different geographic levels with up to four selected cover photos. | [R37-S3](<#r37-s3>) |
| **Custom albums**<br>`albums.manual` | C | README supports custom albums; AlbumUser stores owner, photos, cover photos and title independently of the source folders. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>) |
| **Backend count and distribution endpoints**<br>`analytics.library_statistics` | C | Registered handlers expose library counts, monthly/country counts, location timeline/sunburst and search-word-cloud helpers; UI completeness and helper accuracy were not independently verified. | [R37-S4](<#r37-s4>), [R37-S5](<#r37-s5>) |
| **People graph endpoints**<br>`analytics.people_cooccurrence_graph` | C | Backend routes socialgraph and egograph to graph-building helpers, with person_id for ego view; these code paths are more specific than the old README's generic planned graphs. | [R37-S4](<#r37-s4>), [R37-S5](<#r37-s5>) |
| **Hide photos from normal browsing**<br>`browse.hidden_items` | C | Photo has a hidden flag and dedicated hidden-list/hide endpoints; hiding is not evidence of encryption. | [R37-S3](<#r37-s3>), [R37-S4](<#r37-s4>) |
| **Date-grouped browsing**<br>`browse.timeline` | C | README advertises grouped-by-date photos; AlbumDate stores dated and no-date groups and returns descending EXIF time. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>) |
| **Virtualized photo frontend**<br>`browse.virtualization` | C | README explicitly identifies react-virtualized as its frontend optimization; no independent scale benchmark is asserted. | [R37-S1](<#r37-s1>) |
| **Compose deployment**<br>`deployment.docker` | C | Recommended deployment uses host mounts for source photos, protected thumbnails and logs plus a persistent database volume. | [R37-S2](<#r37-s2>) |
| **Self-hosted browser service**<br>`deployment.selfhosted` | C | OwnPhotos runs a backend API and separate browser frontend behind a proxy; Compose includes PostgreSQL and Redis. | [R37-S1](<#r37-s1>), [R37-S2](<#r37-s2>) |
| **Legacy browser photo-library frontend**<br>`deployment.web` | C | OwnPhotos documents a React frontend served separately from its Django REST backend and connected through a proxy. The browser library interface belongs to this archived-lineage experiment, not the current LibrePhotos frontend. | [R37-S1](<#r37-s1>), [R37-S2](<#r37-s2>) |
| **User photo rotation/editing roadmap**<br>`editing.rotate_flip` | R | README lists basic editing such as rotation as longer-term work. Automatic EXIF orientation of thumbnails is implemented but is not a user editing feature. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>) |
| **View photos on a map**<br>`geo.map` | C | Map viewing is listed as implemented; stored GPS coordinates and location-cluster endpoint support geographic browsing. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>), [R37-S5](<#r37-s5>) |
| **Mapbox reverse geocoding**<br>`geo.online_geocoding` | O | Requires a Mapbox API key; returned location feature text is persisted for search and album generation. Historical free-tier numbers in README are not a current pricing guarantee. | [R37-S1](<#r37-s1>), [R37-S2](<#r37-s2>), [R37-S3](<#r37-s3>) |
| **REST and JWT API**<br>`integration.api` | C | Django routes expose library, face, album, job and user operations with JWT obtain/refresh endpoints; this is an application API, not a stable-version guarantee. | [R37-S1](<#r37-s1>), [R37-S4](<#r37-s4>) |
| **Nextcloud directory import**<br>`library.cloud_import` | O | Users configure a Nextcloud endpoint/account and top-level folder, then explicitly scan; README says backend copies that folder's contents, not remote-only indexing. | [R37-S1](<#r37-s1>) |
| **Scan original directories**<br>`library.existing_folders` | C | Library dashboard starts filesystem scanning of an admin-assigned per-user directory; Photo retains image_path and protected-media handler resolves original files. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>), [R37-S5](<#r37-s5>) |
| **EXIF, capture time and GPS extraction**<br>`metadata.exif_read` | C | Extraction saves serializable EXIF, DateTimeOriginal and latitude/longitude with hemisphere signs. | [R37-S3](<#r37-s3>) |
| **Favorite photos**<br>`metadata.favorites` | C | Photo has a favorite field and API registers favorite-list and bulk favorite-edit routes. | [R37-S3](<#r37-s3>), [R37-S4](<#r37-s4>) |
| **Infer missing dates from filenames**<br>`metadata.filename_date_fallback` | C | If EXIF timestamp is unavailable, the model tries fuzzy date parsing of the filename and assigns UTC; this is inference, not a confirmed capture time. | [R37-S3](<#r37-s3>) |
| **Queued analysis and progress records**<br>`performance.background_jobs` | C | Scanning, event generation, title regeneration and face training enqueue asynchronous jobs; LongRunningJob tracks status, times and target/current progress. | [R37-S3](<#r37-s3>), [R37-S5](<#r37-s5>) |
| **Multiple persisted thumbnail variants**<br>`performance.thumbnail_cache` | C | Produces tiny, small, medium and big proportional and square JPEG thumbnails, correcting EXIF orientation, plus face crops in protected media storage. | [R37-S3](<#r37-s3>) |
| **Location text search**<br>`search.location` | C | README lists location search; geocoding appends returned search_text to the photo's searchable location field. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>) |
| **Browse by identified person**<br>`search.people` | C | README explicitly supports viewing photos by people; person model obtains photos through face associations scoped to owner. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>) |
| **Backend image-similarity search**<br>`search.similar_image` | C | Authenticated similar endpoint accepts an existing image hash and calls search_similar_image; Photo stores Im2Vec encodings. Algorithm/ranking and frontend availability were not established; not exact duplicate detection. | [R37-S3](<#r37-s3>), [R37-S4](<#r37-s4>), [R37-S5](<#r37-s5>) |
| **Photo and album sharing to users**<br>`sharing.account_shares` | C | Despite stale README roadmap, pinned backend has share/unshare handlers for photos and user albums plus shared-to/from-me routes; original access checks recognize these memberships. | [R37-S4](<#r37-s4>), [R37-S5](<#r37-s5>) |
| **Per-user libraries**<br>`sharing.multiuser` | C | Admin area manages users and their scan directories; photos and albums carry ownership and manual-album titles are unique per owner. | [R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>) |
| **Public photo access**<br>`sharing.public_links` | C | Owner-checked makepublic operation and media handler permit unauthenticated access to photos explicitly marked public; password/expiry semantics are not documented. | [R37-S5](<#r37-s5>) |
| **Admin-controlled source access**<br>`sharing.roles` | C | Only administrators may set filesystem scan roots, including their own; ordinary users may configure their own Nextcloud source instead. | [R37-S1](<#r37-s1>) |

## Limitations and evidence gaps

- **explicit:** Old project is retained for archive only; README recommends LibrePhotos and warns this code is early-stage experimentation. ([R37-S1](<#r37-s1>))
- **explicit:** Mapbox reverse geocoding requires an external key/service; Nextcloud import copies files and is not in-place remote browsing. ([R37-S1](<#r37-s1>), [R37-S2](<#r37-s2>))
- **coverage-gap:** README sharing/graph roadmap conflicts with later backend implementation. Core labels based on code mean implemented backend paths, not verified frontend release behavior. ([R37-S1](<#r37-s1>), [R37-S4](<#r37-s4>), [R37-S5](<#r37-s5>))
- **explicit:** Natural-language caption generation is disabled in default automatic paths; a separate im2txt endpoint exists but its deployability is not established. ([R37-S3](<#r37-s3>), [R37-S5](<#r37-s5>))
- **coverage-gap:** Hash storage does not establish a duplicate-review or deletion workflow. Trash, sidecar export, video playback, E2EE and current operational compatibility were not established. ([R37-S1](<#r37-s1>), [R37-S3](<#r37-s3>), [R37-S5](<#r37-s5>))
- **Coverage gap:** No dedicated current manual/release exists in the manifest; inspected README setup plus pinned backend/deployment source.
- **Coverage gap:** Legacy frontend repository and runtime behavior not inspected; code-only capabilities are qualified.
- **Coverage gap:** Similarity/graph helper internals were not fully traced.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R37-S1

[OwnPhotos legacy README](<https://github.com/hooram/ownphotos/blob/180de5746468ec64b725723e03657dc21317f3a9/README.md>)
- Kind/ref: readme; 180de5746468ec64b725723e03657dc21317f3a9
- Sections inspected: Archive notice; implemented/upcoming features; dependencies; complete Docker and first-steps instructions
- Establishes: Legacy status, user-facing feature claims, local/Nextcloud scanning and Mapbox dependency.

### R37-S2

[Compose deployment template](<https://github.com/hooram/ownphotos/blob/180de5746468ec64b725723e03657dc21317f3a9/docker-compose.yml.template>)
- Kind/ref: code; 180de5746468ec64b725723e03657dc21317f3a9
- Sections inspected: Complete service definitions, volumes and environment
- Establishes: Separate services, database persistence, original/thumbnail mounts and external geocoding configuration.

### R37-S3

[Photo, face, album and job models](<https://github.com/hooram/ownphotos/blob/180de5746468ec64b725723e03657dc21317f3a9/api/models.py>)
- Kind/ref: code; 180de5746468ec64b725723e03657dc21317f3a9
- Sections inspected: Complete file; Photo extraction/analysis methods, all album models, User and LongRunningJob
- Establishes: EXIF/time fallback, thumbnails, local analysis, disabled caption paths, albums and persistence semantics.

### R37-S4

[Backend API routes](<https://github.com/hooram/ownphotos/blob/180de5746468ec64b725723e03657dc21317f3a9/ownphotos/urls.py>)
- Kind/ref: code; 180de5746468ec64b725723e03657dc21317f3a9
- Sections inspected: Complete registered viewsets and urlpatterns
- Establishes: Exposed sharing, face review, similarity, statistics, scan/job and authentication routes.

### R37-S5

[Sharing, face, analytics, queue and media handlers](<https://github.com/hooram/ownphotos/blob/180de5746468ec64b725723e03657dc21317f3a9/api/views.py>)
- Kind/ref: code; 180de5746468ec64b725723e03657dc21317f3a9
- Sections inspected: 1294-1478; 1545-1597; 1684-1841; 1959-2083; class index
- Establishes: Actual sharing/publicity operations, manual face corrections, queued tasks and original-media access; analytics/similarity handlers delegate to helpers.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
