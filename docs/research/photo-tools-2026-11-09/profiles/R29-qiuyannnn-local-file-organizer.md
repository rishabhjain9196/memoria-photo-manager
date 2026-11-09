# R29 — QiuYannnn/Local-File-Organizer

[Repository](<https://github.com/QiuYannnn/Local-File-Organizer>) · 3,370 stars at the frozen snapshot · library-utility · Not archived

**Purpose:** Interactive local AI organizer that proposes content-derived names and category directories, then creates hard-linked views of files; not a photo catalogue or duplicate finder.

**Deployment:** Python 3.12/Conda CLI on Windows, macOS and Linux; Nexa SDK with downloaded Llama 3.2 and LLaVA models

**Storage:** Recursively reads existing files. Current operation generation creates hard links in the selected output tree, rather than independent copies or moves. Original paths remain; linked paths share underlying data. Text operation logs are optional.

**Privacy/network behavior:** Inference is local through Nexa SDK, without an AI API. Initial models/dependencies require downloads; main.py also invokes NLTK downloads at startup. The README's offline statement is therefore conditional on provisioning, not a guarantee of zero network access.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** new_version (2024-10-01T00:41:20Z)
**Repository pushed at:** 2024-10-21T22:20:55Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a19559942a35](<https://github.com/QiuYannnn/Local-File-Organizer/commit/a19559942a35d98e9d2168fa58f288d9ea294bc6>).
**Product lineage:** QiuYannnn/Local-File-Organizer.

## Maturity and availability caveats

- Manifest pins a19559942a35d98e9d2168fa58f288d9ea294bc6; latest release new_version (v0.0.2), 2024-10-01; last repository push 2024-10-21.
- README references multiprocessing, but the inspected main workflow explicitly processes image and text groups sequentially; no parallel-inference claim is made here.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Content descriptions for naming**<br>`ai.captioning` | C | Text summaries and image descriptions drive suggested category folder names and filenames; not a persistent searchable caption catalogue. | [R29-S1](<#r29-s1>) |
| **Model selection in CLI**<br>`ai.cli_model_selection` | R | Changing models through the CLI is an unchecked roadmap item; current model identifiers are fixed in initialization source. | [R29-S1](<#r29-s1>), [R29-S2](<#r29-s2>) |
| **Conversational Copilot mode**<br>`ai.conversational_organization` | R | Roadmap proposes telling AI how to organize and rename files through conversation. | [R29-S1](<#r29-s1>) |
| **Local text and vision inference**<br>`ai.local_inference` | C | Content mode initializes quantized Llama3.2-3B-Instruct q3_K_M and llava-v1.6-vicuna-7b q4_0 through Nexa; these models run on the user's machine. | [R29-S1](<#r29-s1>), [R29-S2](<#r29-s2>) |
| **Docker distribution**<br>`deployment.docker` | R | Dockerfile is explicitly unchecked in the roadmap. | [R29-S1](<#r29-s1>) |
| **Standalone desktop executables**<br>`deployment.standalone_executables` | R | macOS/Linux/Windows executables are planned; currently documented installation requires Python, Conda and SDK dependencies. | [R29-S1](<#r29-s1>) |
| **Duplicate detection**<br>`duplicates.content_detection` | R | Checking file duplication remains on the roadmap. Current processed-path and destination-name sets are not duplicate-content detection. | [R29-S1](<#r29-s1>), [R29-S4](<#r29-s4>) |
| **Audio, video and ebook understanding**<br>`formats.additional_ai_inputs` | R | Semantic support for ebooks, audio and video is listed as future work; extension-only ebook placement is already present in type mode. | [R29-S1](<#r29-s1>), [R29-S4](<#r29-s4>) |
| **Document content extraction**<br>`formats.document_text_extraction` | C | Readers handle UTF-8 text/Markdown, DOCX-style documents, PDF, Excel/CSV and PowerPoint text. Plain text is capped at 3,000 characters and PDF at its first three pages; legacy .doc/.ppt are routed through libraries primarily intended for modern formats, so successful legacy parsing is not guaranteed. | [R29-S3](<#r29-s3>) |
| **Raster image analysis**<br>`formats.image_content_analysis` | C | README lists PNG/JPEG/GIF/BMP; source additionally classifies TIFF as an image. This is analysis eligibility, not documented animated playback or RAW decoding. | [R29-S1](<#r29-s1>), [R29-S3](<#r29-s3>) |
| **Interactive organization CLI**<br>`integration.cli` | C | Prompts for input/output paths and content, date or type organization; can retry a different mode or process another directory within the same session. | [R29-S2](<#r29-s2>), [R29-S5](<#r29-s5>) |
| **AI-generated category directories**<br>`library.ai_category_folders` | C | Content analysis produces foldername and filename values used to construct the proposed output hierarchy. | [R29-S1](<#r29-s1>), [R29-S4](<#r29-s4>) |
| **Descriptive output filenames**<br>`library.ai_filename_generation` | C | Generates descriptive names while preserving extensions; sanitizer removes unsuitable words/punctuation, lowercases, separates words with underscores and limits length to 50 characters/five words. | [R29-S4](<#r29-s4>) |
| **Modification-date folders**<br>`library.auto_date_folders` | C | Date mode creates year/month-name directories using filesystem modification time, not EXIF capture dates, and retains existing filenames. | [R29-S4](<#r29-s4>) |
| **Hard-linked output views**<br>`library.hardlink_organization` | C | All three planning modes currently assign hardlink, and execution calls os.link. Original filenames remain; output is not an independent backup and cross-filesystem creation can fail. | [R29-S4](<#r29-s4>) |
| **Johnny Decimal organization**<br>`library.johnny_decimal` | R | Implementing established organization schemes such as Johnny Decimal is an unchecked roadmap item. | [R29-S1](<#r29-s1>) |
| **Recursive file discovery**<br>`library.recursive_file_discovery` | C | Accepts a directory or single file, recursively collects paths and excludes dot-prefixed filenames; hidden directory traversal is not explicitly excluded by os.walk. | [R29-S3](<#r29-s3>) |
| **Extension-based organization**<br>`library.type_folders` | C | Type mode separates image_files, text_files with plain-text/document/PDF/spreadsheet/ebook subcategories, and others; this does not imply semantic ebook understanding. | [R29-S4](<#r29-s4>) |
| **Silent text logging**<br>`maintenance.operation_log` | C | Silent mode appends messages and operation successes/failures to operation_log.txt; it is not a transactional journal or undo mechanism. | [R29-S2](<#r29-s2>), [R29-S4](<#r29-s4>) |
| **Optional GPU-enabled SDK**<br>`performance.gpu_ml` | O | Installation documents a Metal build for macOS and links to Nexa CUDA/AMD support; CPU installation is also provided. | [R29-S1](<#r29-s1>) |
| **Progress and elapsed time**<br>`performance.progress_reporting` | C | CLI reports path-load time and execution uses a progress bar with elapsed time and per-operation advancement. | [R29-S2](<#r29-s2>), [R29-S4](<#r29-s4>), [R29-S5](<#r29-s5>) |
| **No mandatory content upload**<br>`privacy.no_upload_required` | C | The documented content-analysis workflow uses local models and requires no hosted AI API. | [R29-S1](<#r29-s1>), [R29-S2](<#r29-s2>) |
| **Provisioned local processing**<br>`privacy.offline_use` | C | README documents processing without Internet once models are set up; startup calls NLTK download and missing Nexa models are downloaded, so completely disconnected first-run setup is not established. | [R29-S1](<#r29-s1>), [R29-S2](<#r29-s2>) |
| **Confirmation before linking**<br>`safety.confirmation` | C | Output creation and execute_operations occur only after a yes/no confirmation in the main workflow. | [R29-S2](<#r29-s2>) |
| **Limited collision protection**<br>`safety.no_overwrite` | C | Content mode adds numeric suffixes for repeated proposed destinations in the current batch. Existing destinations cause os.link errors logged per operation rather than overwrite; date/type modes do not disambiguate duplicate basenames. | [R29-S4](<#r29-s4>) |
| **Preview proposed directory tree**<br>`safety.organization_preview` | C | Shows the proposed hierarchy before executing operations and offers another organization mode when the proposal is rejected; execute_operations also has an explicit non-mutating dry_run path. | [R29-S2](<#r29-s2>), [R29-S4](<#r29-s4>), [R29-S5](<#r29-s5>) |

## Limitations and evidence gaps

- **coverage-gap:** Translated or user-selectable UI languages are not established in the inspected README and interactive CLI source; this is a documentation gap, not an assertion that localization is unsupported. ([R29-S1](<#r29-s1>), [R29-S2](<#r29-s2>))
- **explicit:** Hard links share content and require filesystem support; editing a linked output can affect the original. Code logs link failures and has no documented copy fallback or rollback. ([R29-S4](<#r29-s4>))
- **explicit:** Offline inference does not imply zero-network startup: NLTK resources and missing model weights are downloaded. ([R29-S2](<#r29-s2>))
- **explicit:** Only limited document text is sampled; PDF reader extracts text rather than performing demonstrated OCR. Imported pytesseract alone does not establish an OCR feature. ([R29-S3](<#r29-s3>))
- **coverage-gap:** Gallery browsing, EXIF editing, face recognition, maps, album sharing, catalogue search and recoverable trash are not established in the inspected documentation/source. ([R29-S1](<#r29-s1>), [R29-S2](<#r29-s2>), [R29-S4](<#r29-s4>))
- **Coverage gap:** No separate user manual exists in the inspected tree; README, release and three complete implementation files establish the limited CLI scope.
- **Coverage gap:** Model accuracy and platform execution were not tested.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R29-S1

[README](<https://github.com/QiuYannnn/Local-File-Organizer/blob/a19559942a35d98e9d2168fa58f288d9ea294bc6/README.md>)
- Kind/ref: readme; a19559942a35d98e9d2168fa58f288d9ea294bc6
- Sections inspected: Entire README, particularly updates, roadmap, supported types, prerequisites and notes
- Establishes: Purpose, local models, supported formats, deployment and explicitly unfinished capabilities.

### R29-S2

[Interactive workflow](<https://github.com/QiuYannnn/Local-File-Organizer/blob/a19559942a35d98e9d2168fa58f288d9ea294bc6/main.py>)
- Kind/ref: code; a19559942a35d98e9d2168fa58f288d9ea294bc6
- Sections inspected: Entire file: initialization, mode selection, simulation, confirmation and repeated sessions
- Establishes: Model download behavior, actual CLI flow, dry preview and logging.

### R29-S3

[File readers and enumeration](<https://github.com/QiuYannnn/Local-File-Organizer/blob/a19559942a35d98e9d2168fa58f288d9ea294bc6/file_utils.py>)
- Kind/ref: code; a19559942a35d98e9d2168fa58f288d9ea294bc6
- Sections inspected: Entire file
- Establishes: Recursive enumeration and concrete content-extraction limits.

### R29-S4

[Operation planning and execution](<https://github.com/QiuYannnn/Local-File-Organizer/blob/a19559942a35d98e9d2168fa58f288d9ea294bc6/data_processing_common.py>)
- Kind/ref: code; a19559942a35d98e9d2168fa58f288d9ea294bc6
- Sections inspected: Entire file
- Establishes: Date/type categorization, filename sanitization, collision handling and hard-link semantics.

### R29-S5

[Version 0.0.2 release](<https://github.com/QiuYannnn/Local-File-Organizer/releases/tag/new_version>)
- Kind/ref: release; new_version
- Sections inspected: Complete release body
- Establishes: Released dry preview, silent logging, new formats and three organization modes.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
