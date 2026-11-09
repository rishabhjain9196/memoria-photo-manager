# R35 — mazzzystar/Queryable

[Repository](<https://github.com/mazzzystar/Queryable>) · 2,993 stars at the frozen snapshot · gallery-mobile · Not archived

**Purpose:** On-device semantic and image-to-image search over an Apple Photos library, rather than a general-purpose photo catalogue.

**Deployment:** iPhone and iPad, iOS 18 or later; App Store application; Buildable Swift/Core ML source; model bundles downloaded separately for development

**Storage:** Originals remain in the Apple Photos library. Asset IDs and 512-dimensional image embeddings are stored in the application's Documents directory using a binary main file, incremental append journal and deletion tombstones. This journal concerns the search index, not reversible file operations.

**Privacy/network behavior:** Image/text inference and similarity search execute on-device. Photo requests disable network access during indexing; users can explicitly enable downloading full-resolution iCloud photos in the viewer. Optional sharing and feedback links leave the offline workflow. No encryption guarantee is established.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** No GitHub release returned
**Repository pushed at:** 2026-10-31T05:51:59Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [19825faac5d1](<https://github.com/mazzzystar/Queryable/commit/19825faac5d1ea6da7a65fc4d6255ce785a09e2c>).
**Product lineage:** mazzzystar/Queryable.

## Maturity and availability caveats

- Frozen manifest commit 19825faac5d1ea6da7a65fc4d6255ce785a09e2c on main; manifest contains no GitHub release.
- Current README uses MobileCLIP S2, superseding the earlier OpenAI CLIP model. Older linked articles and model-export notebooks describe the legacy implementation.
- The settings help describes paid App Store distribution; the repository itself is MIT-licensed. Android PicQuery and macOS Searchable are separate projects, not native distributions of this repository.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Bundled on-device image and text encoders**<br>`ai.local_inference` | C | MobileCLIP S2 encoders run through Core ML locally; model files are bundled in the installed app rather than retrieved for each search. | [R35-S1](<#r35-s1>), [R35-S2](<#r35-s2>), [R35-S5](<#r35-s5>) |
| **Ranked photo result collection**<br>`browse.grid` | C | Displays a prominent best match followed by the remaining photo collection and opens individual results in the photo viewer. | [R35-S7](<#r35-s7>) |
| **Zoom result photos**<br>`browse.zoom` | C | Viewer wraps the image in a scroll view with 1×–20× zoom and displays the asset creation timestamp. | [R35-S6](<#r35-s6>) |
| **iPhone and iPad app**<br>`deployment.ios` | C | Current README specifies iPhone/iPad on iOS 18 or later; source builds require separate MobileCLIP S2 model bundles. | [R35-S1](<#r35-s1>) |
| **Five-language interface resources**<br>`deployment.localization` | C | Application target includes English, German, French, Italian and Spanish resources. Inspected German/French strings translate search/index progress, gestures, settings and privacy help, not only example search queries. Some retain older help wording, so complete current-UI translation parity is not guaranteed. | [R35-S9](<#r35-s9>), [R35-S10](<#r35-s10>), [R35-S11](<#r35-s11>), [R35-S5](<#r35-s5>), [R35-S7](<#r35-s7>) |
| **Paid packaged App Store distribution**<br>`deployment.paid_app_store` | $ | In-app privacy guide describes paying for the application instead of a free app with network-dependent in-app purchases; this does not change the MIT source licence. | [R35-S5](<#r35-s5>), [R35-S1](<#r35-s1>) |
| **Location display deliberately omitted**<br>`geo.location_display` | N | The in-app privacy guide explicitly says photos do not show location information because the developer avoids its network requirement. | [R35-S5](<#r35-s5>) |
| **Opt-in iCloud original retrieval**<br>`library.cloud_import` | O | A cloud-download button for a lower-quality asset enables network access and requests its maximum-size image. Offline operation remains available if declined. | [R35-S6](<#r35-s6>), [R35-S5](<#r35-s5>) |
| **Delete a photo from results**<br>`library.delete_asset` | C | Viewer delegates deletion to the photo asset and removes its search embedding. The inspected viewer does not establish a separate application trash or operation journal. | [R35-S6](<#r35-s6>), [R35-S2](<#r35-s2>) |
| **Index only newly seen photo IDs**<br>`library.incremental_scan` | C | Compares current asset IDs with saved embeddings and offers an Update index action for new photos. Collection observation does not itself imply automatic embedding generation. | [R35-S2](<#r35-s2>), [R35-S7](<#r35-s7>), [R35-S8](<#r35-s8>) |
| **Search existing Apple Photos library**<br>`library.system_photo_library` | C | Search controller opens the system user-library smart album and references PHAsset identifiers without importing originals into a second managed store. | [R35-S2](<#r35-s2>), [R35-S8](<#r35-s8>) |
| **Incremental local index compaction**<br>`maintenance.index_compaction` | C | Appends new embeddings and records deleted IDs, migrates the older archive format and compacts after a journal exceeds five million bytes or tombstones exist. | [R35-S3](<#r35-s3>) |
| **Toggle Apple Photos favourite**<br>`metadata.favorites` | C | Viewer invokes the asset favourite update; this UI is conditional on the saved network-permission flag in the inspected implementation. | [R35-S6](<#r35-s6>) |
| **GPU-accelerated embedding search**<br>`performance.gpu_similarity` | C | Metal/MPSGraph multiplies normalized Float16 embeddings using persistent buffers and a cached graph; the controller provides CPU cosine-similarity fallback when GPU search is unavailable. | [R35-S2](<#r35-s2>), [R35-S4](<#r35-s4>) |
| **Batched on-device indexing**<br>`performance.parallel_scan` | C | Fetches images concurrently in batches of 32, performs batch Core ML prediction and falls back to single-image encoding if a batch fails. | [R35-S2](<#r35-s2>) |
| **Persist partial indexing progress**<br>`performance.resume` | C | Saves embeddings every 5,000 accumulated results, at completion and on caught indexing errors; later indexing skips already persisted IDs. Unsaved work may need repetition. | [R35-S2](<#r35-s2>), [R35-S3](<#r35-s3>) |
| **No mandatory photo upload**<br>`privacy.no_upload_required` | C | README says photos are not uploaded for search; inference and persisted vectors remain on-device. User-invoked sharing is separate. | [R35-S1](<#r35-s1>), [R35-S3](<#r35-s3>), [R35-S6](<#r35-s6>) |
| **Offline indexing and search**<br>`privacy.offline_use` | C | Indexing forcibly disables network photo requests and the guide describes airplane-mode use. iCloud-only originals may remain low-resolution until a user permits download. | [R35-S2](<#r35-s2>), [R35-S5](<#r35-s5>), [R35-S6](<#r35-s6>) |
| **Multiple query languages**<br>`search.multilingual_semantic` | C | In-app guide lists English, French, German, Spanish and Italian input and explicitly says English works best; comparative accuracy is not independently verified. | [R35-S5](<#r35-s5>) |
| **Adjust result set size**<br>`search.result_count` | C | Settings exposes a persisted 10–1000 result slider in increments of ten; actual results are bounded by indexed library size. | [R35-S5](<#r35-s5>), [R35-S2](<#r35-s2>) |
| **Natural-language photo retrieval**<br>`search.semantic_text` | C | Encodes a text description and ranks saved image vectors by similarity; default top result count is 120 rather than an exact-keyword matching guarantee. | [R35-S1](<#r35-s1>), [R35-S2](<#r35-s2>) |
| **Search with an existing photo**<br>`search.similar_image` | C | Swipe upward in a photo viewer to compare its stored embedding against the library and display similar photos; this is semantic similarity, not exact duplicate identification. | [R35-S2](<#r35-s2>), [R35-S6](<#r35-s6>) |
| **Share a viewed image**<br>`sharing.system_share` | C | SwiftUI ShareLink exports the displayed image with the search text used as its share preview; original-byte or EXIF preservation is not established. | [R35-S6](<#r35-s6>) |

## Limitations and evidence gaps

- **explicit:** Indexing is a prerequisite; new photos may require manually updating the index. This is not a full background cloud library sync. ([R35-S7](<#r35-s7>), [R35-S2](<#r35-s2>))
- **explicit:** iCloud-only photos may be shown at lower quality until network download is authorised; offline operation does not guarantee offline availability of every original. ([R35-S6](<#r35-s6>))
- **explicit:** Settings warns of device-specific Core ML crashes or abnormal results. No accuracy or large-library benchmark was performed here. ([R35-S5](<#r35-s5>))
- **coverage-gap:** Exact duplicate cleanup, face identity recognition, OCR, folder management, metadata editing, video playback and recovery guarantees are not established by the inspected sources. ([R35-S1](<#r35-s1>), [R35-S2](<#r35-s2>), [R35-S6](<#r35-s6>))
- **coverage-gap:** App Store price/version parity with this unreleased branch snapshot is not verified; external Android/macOS projects must not be counted as this repository's shipped clients. ([R35-S1](<#r35-s1>), [R35-S5](<#r35-s5>))
- **Coverage gap:** No GitHub release in frozen manifest; current branch and in-app documentation used.
- **Coverage gap:** Broader DAM and recovery features not established; no equivalence to external sibling products claimed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R35-S1

[Queryable README](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/README.md>)
- Kind/ref: readme; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete README, including operation, MobileCLIP updates, setup and related apps
- Establishes: Purpose, supported iOS platform, offline inference, model migration and separate companion projects.

### R35-S2

[Search and indexing controller](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable/ViewModel/PhotoSearcher.swift>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete file: prepareModelForSearch, fetchUnIndexedPhotos, batchBuildIndex, buildIndex, search, similarPhoto
- Establishes: Incremental indexing, checkpoint persistence, batch inference, image queries and CPU fallback.

### R35-S3

[Embedding persistence](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable/Model/EmbeddingStore.swift>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete binary storage, migration, tombstone and compaction implementation
- Establishes: Local persistent index format and incremental save semantics.

### R35-S4

[GPU similarity search](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable/Model/GPUSimilaritySearch.swift>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete file
- Establishes: Metal/MPSGraph normalized Float16 matrix search and cached GPU buffers.

### R35-S5

[Settings and in-app guide](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable/View/ConfigPageViews/ConfigView.swift>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete settings and help text
- Establishes: Result-count control, language guidance, privacy exceptions, distribution and limitations.

### R35-S6

[Photo viewer](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable/View/PhotoResult/PhotoView.swift>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete viewer, actions, cloud download and zoom implementation
- Establishes: Similarity gesture, sharing, favourites, deletion and iCloud handling.

### R35-S7

[Search results and indexing guide](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable/View/SearchResultsView.swift>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete results, first-use and update-index views
- Establishes: Top result plus collection, progress states and manual refresh instructions.

### R35-S8

[Apple Photos collection adapter](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable/PhotoHelper/PhotoCollection.swift>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete loading and PHPhotoLibraryChangeObserver implementation
- Establishes: Existing system library access and collection change observation.

### R35-S9

[German interface translations](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/de.lproj/Localizable.strings>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete string resource
- Establishes: Actual German translations for search/index states, viewer gestures, settings and privacy help.

### R35-S10

[French interface translations](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/fr.lproj/Localizable.strings>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Complete string resource
- Establishes: Actual French UI/help translations distinct from natural-language model input support.

### R35-S11

[Application localization packaging](<https://github.com/mazzzystar/Queryable/blob/19825faac5d1ea6da7a65fc4d6255ce785a09e2c/Queryable/Queryable.xcodeproj/project.pbxproj>)
- Kind/ref: code; 19825faac5d1ea6da7a65fc4d6255ce785a09e2c
- Sections inspected: Known regions, localization file/group references, PBXVariantGroup and Resources build phase
- Establishes: English, German, French, Italian and Spanish string resources are included in application target.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
