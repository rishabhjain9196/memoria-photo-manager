# R49 — guardian/grid

[Repository](<https://github.com/guardian/grid>) · 1,460 stars at the frozen snapshot · library-server · Not archived

**Purpose:** Newsroom image asset-management platform centered on searchable editorial metadata, licensing/restrictions, publication usage and derivative crop distribution, with optional AWS-backed AI search.

**Deployment:** Self-hosted multi-service Scala/Play system with Kahuna browser UI; Elasticsearch plus AWS S3, DynamoDB and messaging infrastructure; Local development uses LocalStack, but AI embedding still calls real AWS services

**Storage:** Uploads originals into managed object storage and generates thumbnail/optimized derivatives. Extracted and edited metadata/search projections live in database/search services; collections and publication usage have separate services. Crop exports are separately stored derivatives with requester/time provenance.

**Privacy/network behavior:** Server-managed organizational asset store, not E2EE. User/machine authentication and API-key tiers gate access. Optional AI sends image/query inputs to AWS Bedrock and stores vectors in AWS services, including when a developer uses LocalStack. Production rights providers and authentication can depend on organization-specific external systems.

**License metadata:** Apache-2.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** No GitHub release returned
**Repository pushed at:** 2026-11-09T11:29:00Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [b874a49bc0ca](<https://github.com/guardian/grid/commit/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa>).
**Product lineage:** guardian/grid.

## Maturity and availability caveats

- Pinned main b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa; manifest has no latest tagged release.
- Documentation includes legacy ecosystem references and a provider-auth page explicitly marked work-in-progress; current source/tests are used to establish implemented permissions.
- Vision document is aspirational and is not treated as proof of all goals. No throughput/latency benchmarks were run.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **AWS Bedrock embeddings**<br>`ai.remote_inference` | O | Lambda sends images to real Bedrock and stores vectors in S3 Vectors even in LocalStack development; query embedding calls are likewise remote. | [R49-S14](<#r49-s14>), [R49-S15](<#r49-s15>) |
| **Hierarchical collections**<br>`albums.nested` | C | Collections have root/child/grandchild hierarchy. Root creation currently requires the API, not Kahuna UI. | [R49-S4](<#r49-s4>) |
| **Print/digital usage tracking**<br>`analytics.publication_usage` | C | Usage records connect images to articles/editorial systems or print issue/page/layout/publication details, with pending/published/removed state resolution. | [R49-S8](<#r49-s8>) |
| **Supplier usage/quota API**<br>`analytics.supplier_quotas` | C | Current API exposes supplier usage, image usage and quota-count/quota-for-image endpoints for contractual accounting. | [R49-S13](<#r49-s13>) |
| **Date histogram API**<br>`analytics.timeline_counts` | C | Aggregation endpoint computes a date histogram for a chosen field and optional query. | [R49-S13](<#r49-s13>) |
| **Paged search API**<br>`browse.pagination` | C | Search provides offset/length and configurable orderBy; documented defaults are ten results ordered newest upload first. | [R49-S2](<#r49-s2>) |
| **Resumable mass deletion utility**<br>`cleanup.bulk_delete_script` | O | Administrator script consumes image IDs and Internal API credentials, records last processed ID and separate success/error lists. Documentation explicitly says no mass-deletion UI; logs are not an atomic pre-operation journal. | [R49-S16](<#r49-s16>) |
| **Self-hosted service suite**<br>`deployment.selfhosted` | C | Runs separately deployable services with Elasticsearch and AWS infrastructure; local setup provisions LocalStack resources. | [R49-S1](<#r49-s1>), [R49-S17](<#r49-s17>) |
| **Kahuna image management UI**<br>`deployment.web` | C | Browser frontend accesses the microservices via hypermedia APIs; intended for organizational/editorial image workflows. | [R49-S1](<#r49-s1>) |
| **Validated derivative crops**<br>`editing.crop` | C | Cropper verifies source ownership URI, image validity and bounds using oriented dimensions, then generates/stores crop exports separately from originals. | [R49-S12](<#r49-s12>) |
| **Derivative sizes and optimized download**<br>`editing.resize` | C | Crop creation yields master/additional sizings; optimized download API accepts width, height and quality parameters. | [R49-S12](<#r49-s12>), [R49-S13](<#r49-s13>) |
| **TIFF original and previews**<br>`formats.tiff` | C | Uploads original TIFF and creates mandatory JPEG thumbnails plus optional optimized PNG; layered TIFF handling picks the extracted first image/layer for the preview rather than providing a complete multipage viewer. | [R49-S9](<#r49-s9>) |
| **Hypermedia service APIs**<br>`integration.api` | C | APIs cover image ingestion/search, metadata, exports, collections, usage and auth; internal, readonly and syndication machine keys have distinct scopes. | [R49-S1](<#r49-s1>), [R49-S10](<#r49-s10>), [R49-S13](<#r49-s13>) |
| **Ordered ingest processors**<br>`integration.metadata_processors` | P | ImageProcessor/MetadataCleaner interfaces enable configured Scala pipelines for agency detection, license assignment, credits and house-style normalization; custom implementations require integration, not a generic AI model. | [R49-S5](<#r49-s5>) |
| **Managed object storage**<br>`integration.object_storage` | C | Requires S3 buckets and DynamoDB resources; originals and derivative images are server-managed rather than a local folder browser. | [R49-S9](<#r49-s9>), [R49-S17](<#r49-s17>) |
| **Organization-specific rights sources**<br>`integration.rights_providers` | O | Includes Guardian hardcoded and runtime-configured providers for photographer/illustrator lists and Creative Commons options; additional sources can implement the provider trait. | [R49-S6](<#r49-s6>) |
| **Derivative provenance ingestion**<br>`library.derivative_ingestion` | C | Loader exposes enqueueDerivativeImage with derivativeOfMediaIds, preserving an explicit relationship to source assets. | [R49-S18](<#r49-s18>) |
| **Original and crop downloads**<br>`library.export_originals` | C | Media API supplies original-file download and width-specific crop-export downloads; crop links are configurable. | [R49-S12](<#r49-s12>), [R49-S13](<#r49-s13>) |
| **Managed image upload**<br>`library.import_copy` | C | Upload service prepares presigned uploads, accepts images with uploader/identifiers/timestamps/filename and exposes per-image/per-user upload status. | [R49-S18](<#r49-s18>), [R49-S5](<#r49-s5>) |
| **Multi-image metadata editing**<br>`metadata.batch_edit` | C | Selected images show common values or Multiple values; saving applies per-image updates. Opt-in string edit modes support overwrite, prefix or suffix against each existing value. | [R49-S7](<#r49-s7>) |
| **Crop requester and timestamp**<br>`metadata.crop_provenance` | C | Each generated crop records authenticated identity, request time and specification. This is derivative provenance, not a durable crash-recovery file-action journal. | [R49-S12](<#r49-s12>) |
| **Custom searchable metadata schema**<br>`metadata.domain_schema` | O | Configuration defines collapsible domain sections with string/integer/datetime/select fields, controlled vocabularies, validation and searchable aliases without modifying application code. | [R49-S7](<#r49-s7>) |
| **Source IPTC extraction**<br>`metadata.iptc_read` | C | Ingestion extracts IPTC into source metadata and maps key fields into editable/searchable primary metadata. | [R49-S5](<#r49-s5>) |
| **Cost and allowed-use summaries**<br>`metadata.rights_cost_summary` | O | Configured UI can show payable, all-use, news/sport eligibility and supplier markers, based on deployment-specific rights rules rather than generic image availability. | [R49-S11](<#r49-s11>) |
| **Metadata-template rights preview**<br>`metadata.rights_templates` | O | Configured templates preview their replacement usage-rights category in a locked editor and allow applying or cancelling without prematurely changing existing rights. | [R49-S11](<#r49-s11>) |
| **Editorial licensing and restrictions**<br>`metadata.usage_rights` | C | Displays/edits usage categories, agency suppliers, publications/creators and required restriction text; unknown rights are explicit and some categories force restrictions. | [R49-S6](<#r49-s6>), [R49-S11](<#r49-s11>) |
| **Source XMP extraction**<br>`metadata.xmp_read` | C | Ingestion preserves source XMP metadata in the database before configurable classification/cleaning. | [R49-S5](<#r49-s5>) |
| **Queued embedding/backfill**<br>`performance.background_jobs` | O | SQS-fed embedding work supports retries/dead-letter behavior; documented backfill selects unembedded, non-soft-deleted assets. | [R49-S14](<#r49-s14>) |
| **Shared in-flight query cache**<br>`performance.query_embedding_cache` | O | AI-search controller caches normalized query embeddings/futures so simultaneous equivalent queries share a remote call; zero-length polling skips Bedrock/KNN work. | [R49-S15](<#r49-s15>) |
| **Soft deletion and undelete API**<br>`safety.app_recovery` | C | Current routes distinguish soft-deleted metadata, ordinary delete, explicit hard-delete and undelete. Retention period and complete recovery semantics are not documented by these routes. | [R49-S13](<#r49-s13>) |
| **Separate crop derivatives**<br>`safety.nondestructive_edits` | C | Crop exports refer to a source image, have separate asset/download records and can be removed via crop permissions without a source rewrite in the inspected controller. | [R49-S12](<#r49-s12>) |
| **Replica restoration endpoint**<br>`safety.replica_restore` | C | Loader exposes images/restore calling restoreFromReplica; exact operator workflow/backup completeness remains unverified. | [R49-S18](<#r49-s18>) |
| **Structured filters and negation**<br>`search.boolean` | C | Supports field:value, quoted phrases, leading '-' negation, has:/is: conditions, # labels, collection: hierarchy terms and nested usages@field filters. | [R49-S3](<#r49-s3>) |
| **Capture/upload/date range search**<br>`search.date_range` | C | Distinguishes taken, uploaded/date and added dates; supports comparison operators, today/yesterday, multiple date formats and API since/until relative durations. | [R49-S2](<#r49-s2>), [R49-S3](<#r49-s3>) |
| **JPEG/PNG/TIFF filters**<br>`search.file_type` | C | fileType parser normalizes jpg/jpeg and tif/tiff plus png to MIME constraints. | [R49-S3](<#r49-s3>) |
| **Filename field search**<br>`search.filename_path` | C | Query parser explicitly supports filename; this is managed-asset metadata search rather than browsing filesystem paths. | [R49-S3](<#r49-s3>) |
| **Editorial location fields**<br>`search.location` | C | Searches location/city/state/country; the in alias expands across these descriptive fields. This is not a map or reverse-geocoding claim. | [R49-S3](<#r49-s3>) |
| **Editorial field search**<br>`search.metadata` | C | Structured fields include title, description, copyright, credit, supplier reference, source, photographer/byline, category, subject, people-in-image, photoshoot and cropper identity. | [R49-S3](<#r49-s3>) |
| **People-in-image metadata**<br>`search.people` | C | person query aliases peopleInImage metadata; no automatic facial recognition is implied. | [R49-S3](<#r49-s3>) |
| **Search by downstream usage**<br>`search.publication_usage` | C | Nested usages constraints include status, platform, section, publication, orderedBy and content references; request filters also cover usage and syndication status. | [R49-S3](<#r49-s3>), [R49-S15](<#r49-s15>) |
| **Hybrid semantic/text ranking**<br>`search.semantic_text` | O | useAISearch plus enabled server configuration embeds query text through Bedrock and combines vector/text ranking; default vector weight is 0.85 and metadata/usage filters constrain the candidate pool. | [R49-S15](<#r49-s15>), [R49-S14](<#r49-s14>) |
| **Embedding-based image similarity**<br>`search.similar_image` | O | AI similar:imageId uses the accessible source image's Cohere Embed v4 image vector for filtered nearest-neighbor retrieval. Missing vectors yield no results; combining image and text ranking signals is rejected. | [R49-S3](<#r49-s3>), [R49-S15](<#r49-s15>) |
| **Permission-gated editing/actions**<br>`sharing.roles` | C | Rights tests specify edit permission or ownership; crop deletion uses a dedicated permission. Machine API tiers are internal, readonly or syndication-specific. | [R49-S10](<#r49-s10>), [R49-S11](<#r49-s11>), [R49-S12](<#r49-s12>) |
| **Partner syndication API**<br>`sharing.syndication` | C | Media API exposes per-partner image syndication and search can filter syndication status; downstream commercial integrations are deployment-specific. | [R49-S13](<#r49-s13>), [R49-S15](<#r49-s15>) |

## Limitations and evidence gaps

- **coverage-gap:** Translated Kahuna UI or selectable interface languages are not established by the inspected primary documentation/source. Multilingual query characters and a service MessageTranslator are not treated as UI localization evidence. ([R49-S1](<#r49-s1>), [R49-S3](<#r49-s3>), [R49-S11](<#r49-s11>))
- **explicit:** AWS infrastructure is a documented dependency. Optional embedding calls real Bedrock/S3 Vectors even under LocalStack, so this is not guaranteed local/offline AI. ([R49-S14](<#r49-s14>), [R49-S17](<#r49-s17>))
- **explicit:** Collection roots require API creation; mass deletion uses a separate script rather than the UI. ([R49-S4](<#r49-s4>), [R49-S16](<#r49-s16>))
- **explicit:** Domain field removal drops editable/persisted values on updates; changing types may break old values, and aliases can collide with built-in query prefixes. ([R49-S7](<#r49-s7>))
- **explicit:** AI search cannot combine similar-image and textual ranking in one query, requires existing embeddings for image search and uses a configured result limit rather than ordinary unlimited paging. ([R49-S15](<#r49-s15>))
- **coverage-gap:** Mobile backup, local-folder browsing, RAW development, face recognition, geographic maps, duplicate cleanup, E2EE and crash-recovery file journals are not established. person search is metadata, not facial identification. ([R49-S1](<#r49-s1>), [R49-S3](<#r49-s3>), [R49-S5](<#r49-s5>), [R49-S12](<#r49-s12>))
- **Coverage gap:** No tagged release metadata; pinned main mixes active source and some older service docs.
- **Coverage gap:** API-only recovery/quota endpoints are medium-confidence capability evidence; full UI/retention policies not established.
- **Coverage gap:** No runtime execution of source or behavior scenarios.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R49-S1

[README](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/README.md>)
- Kind/ref: readme; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire README
- Establishes: Newsroom purpose, hypermedia APIs, browser UI and infrastructure.

### R49-S2

[Image-search API](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/media-api/README.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire README
- Establishes: Text query, offset/length pagination, ordering and time boundaries.

### R49-S3

[Structured search parser](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/media-api/app/lib/querysyntax/QuerySyntax.scala>)
- Kind/ref: code; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire file
- Establishes: Metadata/usage/date/type/collection filters, negation, labels and field aliases.

### R49-S4

[Collections](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/docs/03-apis/02-collections.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: Nested collection hierarchy and API-only creation of roots.

### R49-S5

[Image-processor pipelines](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/docs/07-extending/02-image-processors.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: Embedded metadata extraction, configurable classification/rights/credit cleaning and extension interfaces.

### R49-S6

[Usage-rights providers](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/docs/07-extending/04-usage-rights.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: Creator/publication/Creative Commons configuration and extensible rights providers.

### R49-S7

[Domain metadata](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/docs/07-extending/05-domain-metadata.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: Configurable editable/searchable schema, bulk edits, aliases and compatibility caveats.

### R49-S8

[Usage API examples](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/usage/api-examples.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: Digital/print publication provenance and pending/published/removed usage status.

### R49-S9

[TIFF import](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/docs/06-objects-of-interest/01-tiffs.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: Original preservation and first-image/layer-derived PNG/JPEG previews.

### R49-S10

[Authentication and API tiers](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/docs/03-apis/01-authentication.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: User federation, signed inner-service calls and internal/readonly/syndication keys.

### R49-S11

[Rights and restrictions behavioral scenarios](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/e2e-tests/features/rights-and-restrictions.feature>)
- Kind/ref: code; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire feature specification
- Establishes: Current user-visible rights summaries, permission gating and template previews; tests inspected, not executed.

### R49-S12

[Crop export controller](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/cropper/app/controllers/CropperController.scala>)
- Kind/ref: code; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire file
- Establishes: Validated derivative creation, export provenance, download links and permission-controlled deletion.

### R49-S13

[Current media API routes](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/media-api/conf/routes>)
- Kind/ref: code; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire routes file
- Establishes: Original/optimized/crop downloads, soft/hard deletion, restoration, quotas and aggregations.

### R49-S14

[Image embedding service](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/image-embedder-lambda/README.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire README
- Establishes: Asynchronous remote embedding, real AWS dependencies, vector storage and backfill.

### R49-S15

[Media API AI-search implementation](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/media-api/app/controllers/MediaApi.scala>)
- Kind/ref: code; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Embedding cache, search parameters, AI mode/filter helpers, text/image ranking and useAISearch dispatch
- Establishes: Actual gated hybrid text/vector and similar-image search with metadata filters and visibility checks.

### R49-S16

[Mass deletion utility](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/scripts/mass-deletion/README.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire README
- Establishes: API-key script with last-ID progress, success and error files; no bulk deletion UI.

### R49-S17

[AWS dependencies](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/docs/01-setup/02-aws-dependencies.md>)
- Kind/ref: manual; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire page
- Establishes: S3/DynamoDB requirements and LocalStack development resources.

### R49-S18

[Image-loader routes](<https://github.com/guardian/grid/blob/b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa/image-loader/conf/routes>)
- Kind/ref: code; b874a49bc0ca091ad5762bf8b09a7ac457cbeaaa
- Sections inspected: Entire file
- Establishes: Upload preparation/status, derivative ingestion and replica restoration endpoints.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
