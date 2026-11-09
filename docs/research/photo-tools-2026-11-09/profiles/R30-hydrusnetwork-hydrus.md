# R30 — hydrusnetwork/hydrus

[Repository](<https://github.com/hydrusnetwork/hydrus>) · 3,260 stars at the frozen snapshot · library-desktop · Not archived

**Purpose:** Local, tag-centric media archive with managed content-addressed storage, powerful download automation and unusually detailed duplicate-relationship workflows.

**Deployment:** Windows installer or portable ZIP; Linux built archive or source installation; Official macOS client runs from source; separate third-party Hydra Vista macOS client; Optional bundled file/tag repository server, not a photo web UI; Optional third-party browser UIs such as Hydrus Web/Hydrui and Android clients such as hydit/aether, connected through the enabled Client API

**Storage:** Imports copies into hash-named managed storage using SHA-256 identity; original filenames/folders are not the catalogue model. Settings, tags, ratings, notes, URLs and relationships live in SQLite databases. Media/thumbnails may be distributed over weighted storage locations while the database stays local; local file domains are overlapping database subsets, not independent catalogues.

**Privacy/network behavior:** Default operation is local with no sharing or phone-home according to project documentation. Downloads, tag/file repositories and Client API are explicit network integrations. Repository uploads can reveal identifying content and server operators see connection IPs; transport encryption is not E2EE. Deleting a file retains much of its metadata, and website login credentials are explicitly not securely stored.

**License metadata:** NOASSERTION. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v694a (2026-11-04T21:56:29Z)
**Repository pushed at:** 2026-11-09T04:30:29Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [c78a5cbe76e7](<https://github.com/hydrusnetwork/hydrus/commit/c78a5cbe76e7b77a2f652187e8343907fa7f27ba>).
**Product lineage:** hydrusnetwork/hydrus.

## Maturity and availability caveats

- Frozen master commit c78a5cbe76e7b77a2f652187e8343907fa7f27ba; release v694a dated 2026-11-04.
- Project targets frequent weekly releases and is chiefly solo-maintained; README says public pull requests are closed.
- README/release explicitly urge users of v691 or older to update to v692+ for a disclosed remote-code-execution flaw; this profile is not a security audit.
- macOS Intel application has been discontinued in current installation guide; source remains supported. Older examples still mention the legacy app.
- Advanced alternate categorization and fully headless client operation remain incomplete/planned. Third-party plugins are not maintained or guaranteed by the hydrus author.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **External AI taggers**<br>`ai.auto_tags` | P | API guide links DeepDanbooru and model-based taggers, separate projects not authored/guaranteed by hydrus. No built-in face recognition or semantic photo search is inferred. | [R30-S23](<#r30-s23>) |
| **Audio playback**<br>`browse.audio_playback` | C | MP3/OGG/FLAC/M4A/WAV and others play through available media backend; guide says it is not a typical playlist music manager. | [R30-S17](<#r30-s17>), [R30-S5](<#r30-s5>) |
| **Open unsupported viewers externally**<br>`browse.external_open` | C | Any managed file can be launched with the OS default application; import support alone does not imply internal rendering. | [R30-S1](<#r30-s1>), [R30-S5](<#r30-s5>) |
| **Media viewer and fullscreen toggle**<br>`browse.fullscreen` | C | Double/middle click opens media viewer; F toggles frame/fullscreen and hover panels expose tags, navigation and ratings. | [R30-S5](<#r30-s5>) |
| **Thumbnail collection browser**<br>`browse.grid` | C | Imported thumbnails stream into pages; selections show counts/total size and preview pane, with multi-select context actions. | [R30-S5](<#r30-s5>) |
| **Extensive keyboard curation**<br>`browse.keyboard` | C | Page navigation, F3 tags, F4 ratings, F7 archive, Shift+Delete undelete and configurable duplicate-filter shortcuts. | [R30-S5](<#r30-s5>), [R30-S7](<#r30-s7>), [R30-S9](<#r30-s9>), [R30-S11](<#r30-s11>) |
| **Multiple search and downloader pages**<br>`browse.tabs` | C | Create search/special/downloader pages from keyboard chooser, close via middle click and organize subscription landing pages into pages-of-pages. | [R30-S5](<#r30-s5>), [R30-S15](<#r30-s15>) |
| **Group thumbnails by namespace/rating**<br>`browse.tag_collections` | C | Collect-by combines results into groups according to selected tag namespaces or rating services, independent of file folders. | [R30-S6](<#r30-s6>) |
| **Embedded video playback**<br>`browse.video_playback` | C | mpv embed on compatible Windows/Linux or Qt player; supported containers include MP4/WebM/MKV/AVI/MOV/WMV and others. Wayland/mpv and macOS limitations are explicit. | [R30-S17](<#r30-s17>), [R30-S19](<#r30-s19>) |
| **Wheel zoom and synchronized duplicate comparison**<br>`browse.zoom` | C | Ctrl-wheel zooms normal viewing; duplicate review locks relative zoom and position while switching the compared files. | [R30-S5](<#r30-s5>), [R30-S7](<#r30-s7>) |
| **Third-party Android clients**<br>`deployment.android` | P | Official integration guide explicitly lists hydit and aether as Android clients connecting to hydrus through Client API. These are separate user-created projects, not an official bundled hydrus Android application; current release compatibility was not tested. | [R30-S23](<#r30-s23>) |
| **Linux desktop**<br>`deployment.linux` | C | Ubuntu-built archive and source execution; other distributions may need dependencies or source installation. | [R30-S19](<#r30-s19>) |
| **Third-party Hydra Vista macOS client**<br>`deployment.macos` | P | Client API guide names Hydra Vista (konkrotte/hydravista) as a separate macOS client. This does not revive the discontinued official Intel app or change the official source-only macOS installation guidance; companion availability/compatibility was not live-tested. | [R30-S23](<#r30-s23>), [R30-S19](<#r30-s19>) |
| **macOS source execution**<br>`deployment.macos_source` | C | Current guide says source installation is the only macOS option; discontinued Intel .app is not claimed as a current native binary distribution. | [R30-S19](<#r30-s19>) |
| **Portable application data**<br>`deployment.portable` | C | Default settings, databases, media and subscriptions remain under the install directory; portable archive can move across paths/machines with path adjustments. | [R30-S19](<#r30-s19>), [R30-S20](<#r30-s20>) |
| **Optional file/tag repository server**<br>`deployment.selfhosted` | O | Bundled hydrus_server executable can be hosted on the user's own machine to provide file/tag repository services with accounts. It is not required for local use and does not provide the separately documented third-party browser gallery UI. | [R30-S22](<#r30-s22>) |
| **Third-party browser clients**<br>`deployment.web` | P | The inspected Client API guide explicitly names Hydrus Web (floogulinc/hydrus-web), Hydrui and hyAway as actual web interfaces. These separately installed clients require an enabled API and running hydrus desktop client; the API welcome page and repository server are not counted as a built-in gallery UI. | [R30-S23](<#r30-s23>) |
| **Windows desktop**<br>`deployment.windows` | C | Installer and portable ZIP are documented; current guide warns built releases may no longer run on Windows 10. | [R30-S19](<#r30-s19>) |
| **Rule-driven duplicate resolution**<br>`duplicates.auto_resolution` | C | Rules combine pair searches, ordered comparisons and actions. Semi-automatic queues require approve/deny; fully automatic rules can delete and merge without per-pair approval. | [R30-S8](<#r30-s8>) |
| **Preview duplicate rule effects**<br>`duplicates.dry_run` | C | Preview matched/failed pairs and resulting content updates before saving rules; ambiguous A/B ordering is flagged for better-than rules. | [R30-S8](<#r30-s8>) |
| **SHA-256 file identity**<br>`duplicates.exact_hash` | C | SHA-256 identifies managed files and exact repeats regardless of original filename; no pairwise byte-comparison verification is claimed. | [R30-S18](<#r30-s18>), [R30-S4](<#r30-s4>) |
| **Keep alternatives or equal-quality copies**<br>`duplicates.keep_all` | C | Relationships need not delete either file; same-quality/alternate classifications can retain both when desired. | [R30-S7](<#r30-s7>) |
| **Best-file keeper and quality scoring**<br>`duplicates.keeper_selection` | C | Choose better/same-quality relations and whether to delete the worse file; configurable comparison scores suggest order, while each duplicate group maintains a best-file king. | [R30-S7](<#r30-s7>) |
| **Merge metadata into keeper**<br>`duplicates.metadata_merge` | C | Configure transfer/merge of tags, ratings, archive status, URLs and notes, with defaults or per-action customization; content merges are not fully undoable. | [R30-S7](<#r30-s7>), [R30-S8](<#r30-s8>) |
| **Metadata-aware automated comparisons**<br>`duplicates.metadata_preservation_checks` | C | Rule comparators can protect EXIF/XMP/IPTC/human-readable/software metadata and ICC presence; they check presence flags, not equality or richness of contents. | [R30-S8](<#r30-s8>) |
| **Exact decoded-pixel matches**<br>`duplicates.pixel_identity` | C | Distinguishes same-resolution/pixel-content matches even when metadata or file encoding differs; pixel hashes can be regenerated independently. | [R30-S7](<#r30-s7>), [R30-S24](<#r30-s24>) |
| **Independent queries for pair sides**<br>`duplicates.query_scoped_pairs` | C | Require one side, both sides or different searches per side, plus maximum Hamming distance and require/exclude pixel matches; mixed-pair or full-group review modes. | [R30-S7](<#r30-s7>) |
| **Persist duplicate/alternate/false-positive relations**<br>`duplicates.remember_decisions` | C | Confirmed relationships stop ordinary re-presentation and imply transitive relations; false positives are remembered across runs, without a complete per-decision audit log. | [R30-S7](<#r30-s7>) |
| **Rich alternate categorization**<br>`duplicates.rich_alternate_labels` | R | Basic alternate relationships exist, but ordered WIP/recolour labels and richer presentation are explicitly future work; large alternate sets currently scale poorly. | [R30-S7](<#r30-s7>) |
| **Perceptual duplicate candidates**<br>`duplicates.similar_images` | C | 64-bit pHash with VP-tree Hamming-distance search finds shape-similar still images in the background; adjustable distance trades recall for false positives. | [R30-S7](<#r30-s7>) |
| **External video-deduplication integration**<br>`duplicates.similar_videos` | P | Official docs point to Hydrus Video Deduplicator, which discovers video pairs and queues them through Client API; native still-image pHash is not video matching. | [R30-S7](<#r30-s7>), [R30-S23](<#r30-s23>) |
| **Pair comparison with synchronized view**<br>`duplicates.visual_review` | C | Toggle A/B with locked zoom/position; show filesize/resolution/age/tags, estimated JPEG quality and more expensive visual-comparison statements. | [R30-S7](<#r30-s7>) |
| **Animated images and Ugoira**<br>`formats.animated` | C | GIF/APNG/WebP and HEIC/HEIF/AVIF sequences; Ugoira ZIP can use embedded animation.json or note-provided frame delays, otherwise defaults to 125 ms. | [R30-S17](<#r30-s17>) |
| **AVIF images and sequences**<br>`formats.avif` | C | AVIF stills and AVIF sequences have thumbnails and internal viewing in format matrix. | [R30-S17](<#r30-s17>) |
| **Content-based filetype detection and override**<br>`formats.content_detection` | C | Detects type by inspecting content rather than trusting extension/MIME; users can force a type from context menu. | [R30-S17](<#r30-s17>) |
| **Document/archive cataloguing**<br>`formats.documents_archives` | C | Can import PDF/Office/ebook/archive formats with differing previews; PDF thumbnails except encrypted PDFs and CBZ identification do not imply internal document reading. | [R30-S17](<#r30-s17>) |
| **HEIC/HEIF import and viewing**<br>`formats.heic` | C | Format matrix marks HEIC and HEIF as importable, thumbnail-capable and viewable. | [R30-S17](<#r30-s17>) |
| **JPEG XL images**<br>`formats.jpegxl` | C | JXL is explicitly importable, thumbnail-capable and internally viewable. | [R30-S17](<#r30-s17>) |
| **Creative-project preview support**<br>`formats.project_previews` | C | Krita/OpenRaster/PSD display embedded previews; Clip Studio and Procreate have thumbnails but no direct viewing, and XCF/SAI2 are import-only. | [R30-S17](<#r30-s17>) |
| **SVG thumbnails only**<br>`formats.svg` | C | SVG import and thumbnails are supported; format matrix explicitly says SVG is not directly viewable inside hydrus. | [R30-S17](<#r30-s17>) |
| **Opt-in Client API**<br>`integration.api` | O | Enable a port and per-program access keys; active only while desktop client runs. Default HTTP/local policy can be changed to remote/HTTPS, with operator security responsibilities. | [R30-S23](<#r30-s23>) |
| **Third-party API workflow extensions**<br>`integration.plugins` | P | Official API guide lists Hydrus Companion browser upload/cookie helpers, Hyshare small-gallery sharing, kaimen virtual FUSE search folders and other workflow tools. Separate browser/Android/macOS client deployment is recorded in its own platform findings; these extensions are not bundled core features. | [R30-S23](<#r30-s23>) |
| **Skip exact repeat imports**<br>`library.deduplicate_import` | C | Exact byte-identical repeat files are not stored again; visually similar but byte-different files remain separate for duplicate review. | [R30-S4](<#r30-s4>) |
| **External in-place originals unsupported**<br>`library.existing_folders` | N | FAQ explicitly declines tracking source files in place; after import the original path is never used again. | [R30-S18](<#r30-s18>) |
| **Export stored original bytes**<br>`library.export_originals` | C | Drag/drop, clipboard-copy or explicit export returns managed files; filename patterns can use tags/hash and create subfolders. | [R30-S4](<#r30-s4>) |
| **Managed copy import**<br>`library.import_copy` | C | Drag files/folders or use import dialog; originals stay untouched by default while copied files receive content-addressed managed names. Optional delete-source-after-import must be explicitly enabled. | [R30-S4](<#r30-s4>), [R30-S5](<#r30-s5>) |
| **Size, dimensions and deleted-file import policies**<br>`library.import_filters` | C | Import options include min/max size, resolution and whether to reimport previously deleted files; optional pre-import tagging parses filenames/folders. | [R30-S4](<#r30-s4>) |
| **Inbox-to-archive curation**<br>`library.inbox_archive` | C | New imports enter inbox; archive marks keepers without moving folders. Fast archive/delete filter supports skip/back and commits decisions at completion. | [R30-S5](<#r30-s5>) |
| **Overlapping local file subsets**<br>`library.local_file_domains` | C | Create separate searchable file-domain lists, add/move membership and intersect with tag domains without duplicating payloads. These are not independent databases or user accounts. | [R30-S13](<#r30-s13>) |
| **Independent selectable database instances**<br>`library.multiple_libraries` | C | Create shortcuts using different --db_dir values to run separate catalogues from one install, even concurrently. This is distinct from overlapping file domains within one database. | [R30-S20](<#r30-s20>) |
| **Managed storage across multiple volumes**<br>`library.multiple_roots` | C | Distribute managed media over weighted locations with approximate maximum sizes and separate thumbnail placement; not indexing arbitrary originals in those locations. | [R30-S20](<#r30-s20>) |
| **Missing managed volumes block startup**<br>`library.offline_volumes` | N | Migration guide says all managed file subfolders must be located before the client can boot; it is not an offline-volume catalogue workflow. | [R30-S20](<#r30-s20>) |
| **Automated import/export folders**<br>`library.scheduled_import_export` | C | Configured folders run on schedules, importing tags/URLs/notes via sidecars and exporting selected files with naming patterns/metadata. | [R30-S4](<#r30-s4>), [R30-S12](<#r30-s12>) |
| **Adaptive repeating gallery queries**<br>`library.subscription_sync` | O | Subscriptions detect new URLs, adapt interval to source velocity, stop dead queries and publish to grouped landing pages; they do not reliably backfill old gaps. | [R30-S14](<#r30-s14>), [R30-S15](<#r30-s15>) |
| **Imageboard-thread watcher**<br>`library.thread_watcher` | O | Installed watcher definitions repeatedly check a thread, adapt to incoming frequency and stop at inactivity/404; not filesystem watching. | [R30-S14](<#r30-s14>) |
| **Gallery, URL and simple-page downloading**<br>`library.web_download` | O | User-installed downloader definitions parse gallery searches, file/post URLs or simple page links; fresh installs contain no downloaders. Tags/notes can accompany files. | [R30-S14](<#r30-s14>) |
| **Reconcile missing and orphaned files**<br>`maintenance.media_recovery` | C | Queue missing-file checks/redownload from known URLs, export hashes/tags/URLs for recovery, and move orphaned payloads to a review location for deletion/reimport. | [R30-S21](<#r30-s21>), [R30-S24](<#r30-s24>) |
| **Rebuild derived metadata selectively**<br>`maintenance.selective_reset` | C | Regenerate metadata, thumbnails, supplementary MD5/SHA1/SHA512, pHash, pixel hash, blurhash and embedded-metadata presence flags independently. | [R30-S24](<#r30-s24>) |
| **Display human-readable embedded prompts**<br>`metadata.ai_prompt` | C | Human-readable embedded metadata can include AI prompts and is shown in viewer; search is documented for presence, not natural-language full-prompt search. | [R30-S24](<#r30-s24>) |
| **Bulk tag and rating edits**<br>`metadata.batch_edit` | C | Apply tag edits to selected files and F4 ratings to many thumbnails; viewer tag editor can remain open while navigating and applies immediately. | [R30-S9](<#r30-s9>), [R30-S11](<#r30-s11>) |
| **Named editable notes**<br>`metadata.comments` | C | Downloaders can capture creator comments/text as notes, visible in the viewer; named notes also import/export through sidecars. | [R30-S14](<#r30-s14>), [R30-S12](<#r30-s12>) |
| **View embedded EXIF presence/content**<br>`metadata.exif_read` | C | Maintenance descriptions establish EXIF detection, media-viewer display and system:has exif search. This is not a camera-centric EXIF editing suite. | [R30-S24](<#r30-s24>) |
| **Default favourites rating**<br>`metadata.favorites` | C | New clients include a favourites like/dislike service, functioning as an editable lightweight curation label. | [R30-S11](<#r30-s11>) |
| **Aliases and parent implications**<br>`metadata.hierarchical_tags` | C | Siblings provide reversible tag aliases; parents imply additional tags. Each tag service has its own rules, with configurable cross-service precedence. | [R30-S10](<#r30-s10>) |
| **Embedded IPTC display/presence search**<br>`metadata.iptc_read` | C | Maintenance task and label expose IPTC metadata detection and system:has iptc; detailed field indexing is not claimed. | [R30-S24](<#r30-s24>) |
| **Custom rating services**<br>`metadata.ratings` | C | Like/dislike/unrated, customizable integer-star scales including optional zero, and increment/decrement counters; several services can coexist with configurable shapes/colours. | [R30-S11](<#r30-s11>) |
| **Configurable TXT/JSON sidecar parsing**<br>`metadata.sidecar_import` | C | Import multiple sources into tag/URL/note destinations with filename rules, delimiters, string processing, JSON formulas and live preview; sidecars are not the internal store. | [R30-S12](<#r30-s12>) |
| **TXT/JSON metadata export**<br>`metadata.sidecar_write` | C | Routers export filtered/converted tags, URLs and named notes to TXT or nested JSON; repeated JSON exports update keys rather than replacing unrelated content. | [R30-S12](<#r30-s12>) |
| **Retain source and known URLs**<br>`metadata.source_urls` | C | Known URLs stay attached to content hashes, support downloader skip/refetch decisions and can be exported or used for recovery. | [R30-S14](<#r30-s14>), [R30-S18](<#r30-s18>), [R30-S21](<#r30-s21>) |
| **Export hash-to-tag archives**<br>`metadata.tag_archive` | C | Tag migration can export a Hydrus Tag Archive of queried hash-to-tag mappings independently of media bytes. | [R30-S4](<#r30-s4>) |
| **Private namespaced tags**<br>`metadata.tags` | C | Default my tags/downloader tags remain local; create namespaces such as creator/series/person and customize namespace colours. | [R30-S9](<#r30-s9>), [R30-S10](<#r30-s10>) |
| **Embedded XMP display/presence search**<br>`metadata.xmp_read` | C | XMP presence is detected, viewable and searchable with system:has xmp; arbitrary XMP sidecar import is not established by TXT/JSON routing. | [R30-S24](<#r30-s24>), [R30-S12](<#r30-s12>) |
| **Context-aware download throttling**<br>`performance.bandwidth_limits` | C | Global, domain/subdomain and downloader/subscription/watcher contexts all must permit each request; review usage and customize limits, with conservative defaults. | [R30-S14](<#r30-s14>) |
| **Cancel expensive searches**<br>`performance.cancel` | C | Slow tag/system searches display a stop button; subscriptions expose cancellation and global pause controls. | [R30-S9](<#r30-s9>), [R30-S15](<#r30-s15>) |
| **Pause and resume network queues**<br>`performance.resume` | C | Subscriptions resume where they stopped after cancellation/global pause; normal downloading/import queues can also be paused. | [R30-S15](<#r30-s15>), [R30-S14](<#r30-s14>) |
| **No mandatory media upload**<br>`privacy.no_upload_required` | C | Every upload requires a conscious action according to introduction; the project states it never phones home. | [R30-S3](<#r30-s3>), [R30-S1](<#r30-s1>) |
| **Offline local archive**<br>`privacy.offline_use` | C | Default client connects to no repository and searches local databases; network downloading/sharing is optional. | [R30-S3](<#r30-s3>), [R30-S5](<#r30-s5>) |
| **Delayed repository account anonymisation**<br>`privacy.repository_anonymisation` | O | Repository content attribution is reassigned to a null account after default 90 days, configurable by operator; does not eliminate IP/content inference or malicious-server risks. | [R30-S16](<#r30-s16>) |
| **Searchable application trash**<br>`safety.app_recovery` | C | Deleted media enters a trash domain, can be searched and undeleted, and is automatically permanently removed after configurable time. Files leave local storage only after no local domain retains them. | [R30-S5](<#r30-s5>), [R30-S13](<#r30-s13>) |
| **Integrated backup of normal installations**<br>`safety.catalogue_backup` | C | Set backup location then lock and mirror database/media, copying changes thereafter. Distributed storage disables simple backup and needs a coordinated external backup with client shut down. | [R30-S19](<#r30-s19>) |
| **Scheduled file-content integrity tasks**<br>`safety.integrity_check` | C | Maintenance tasks check expected presence/content to discover corruption or external changes, optionally move bad bytes aside, remove records or enqueue URL redownload; heavier than presence-only checking. | [R30-S24](<#r30-s24>) |
| **OS recycle-bin handoff**<br>`safety.os_trash` | C | Documentation says final physical deletion tries the OS recycle bin by default, providing another possible recovery stage, not a universal guarantee. | [R30-S13](<#r30-s13>) |
| **Immutable managed media bytes**<br>`safety.read_only_originals` | C | Stored originals are expected not to change; editing requires export, external edit and reimport. Metadata remains in catalogue/exports rather than in-place media edits. | [R30-S5](<#r30-s5>) |
| **Undo limited curation actions**<br>`safety.undo` | C | Inbox/archive and trash can be reversed; duplicate filters allow going back before commit. Auto-resolution undo explicitly cannot reverse metadata merges. | [R30-S5](<#r30-s5>), [R30-S7](<#r30-s7>), [R30-S8](<#r30-s8>) |
| **Composable AND, exclusion and OR predicates**<br>`search.boolean` | C | All ordinary predicates must match; leading hyphen excludes tags, Shift builds OR chains and advanced OR accepts system predicates. | [R30-S6](<#r30-s6>) |
| **Dimension predicates**<br>`search.dimensions` | C | Duplicate-rule examples use width and height predicates to exclude tiny images; ordinary predicate searches are reused there. | [R30-S8](<#r30-s8>) |
| **Independent file and tag domains**<br>`search.domain_scoping` | C | Choose local/trash/known-file domain and specific tag service, including union of several file domains; current/pending tags can be searched separately. | [R30-S6](<#r30-s6>), [R30-S13](<#r30-s13>) |
| **File-size restrictions**<br>`search.file_size` | C | Editable filesize predicates can be combined with system:limit to retrieve a bounded largest-file work queue. | [R30-S6](<#r30-s6>) |
| **Media MIME/type predicates**<br>`search.file_type` | C | Filter JPEG/PNG/image/PDF and other types, including separate predicates for each side of a duplicate pair. | [R30-S6](<#r30-s6>), [R30-S7](<#r30-s7>), [R30-S8](<#r30-s8>) |
| **System metadata predicates**<br>`search.metadata` | C | Combine technical metadata, inbox/archive, local/deleted domains and file relationships with tag predicates. | [R30-S5](<#r30-s5>), [R30-S6](<#r30-s6>), [R30-S7](<#r30-s7>) |
| **Search rating services**<br>`search.ratings` | C | system:rating filters like/dislike and configured numeric rating services. | [R30-S11](<#r30-s11>) |
| **Favourite searches**<br>`search.saved_queries` | C | Save common predicate searches with the star control instead of keeping large pages open. | [R30-S6](<#r30-s6>) |
| **Autocomplete namespaced tag search**<br>`search.tags` | C | Tag prefix autocomplete displays counts, resolves aliases and supports wildcard * patterns and namespace-oriented retrieval. | [R30-S6](<#r30-s6>), [R30-S9](<#r30-s9>) |
| **Self-run file/tag repository server**<br>`sharing.repository_server` | O | Bundled separate server can host multiple services with registration tokens, accounts, uploader/downloader/admin permissions and server backups; designed for delayed sync, not live LAN browsing. | [R30-S22](<#r30-s22>) |
| **Optional shared tag repositories**<br>`sharing.tag_repository` | O | Sync all repository hash/tag metadata into a local cache; uploads are explicitly queued/pended and removals may require janitor petitions. Supports multiple repos. | [R30-S10](<#r30-s10>), [R30-S16](<#r30-s16>) |
| **Sort and limit by file size**<br>`sort.file_size` | C | Simple sort such as size/import time is applied before system:limit; complicated tag sorts may instead sort a random limited sample. | [R30-S6](<#r30-s6>) |
| **Tag-namespace ordering**<br>`sort.namespace` | C | Configure namespace-based sorting and collection rules; limit semantics differ from simple metadata sorts. | [R30-S6](<#r30-s6>) |

## Limitations and evidence gaps

- **explicit:** Hydrus copies originals into managed hash storage and will not index them in place. Filename/folder context can be imported as tags but is not preserved as its primary organization. ([R30-S4](<#r30-s4>), [R30-S18](<#r30-s18>))
- **explicit:** Local file domains are overlapping membership lists; independent catalogues require separate database directories. All managed media subfolders must be located before boot, so disconnected-volume browsing is unsupported. ([R30-S13](<#r30-s13>), [R30-S20](<#r30-s20>))
- **explicit:** Large catalogues may contain millions of files, but docs warn that roughly 40,000 files on one page or 150,000 in a session can cause lag; hardware varies. PTR processing is heavy and recommended only with SSD. ([R30-S5](<#r30-s5>), [R30-S10](<#r30-s10>))
- **explicit:** No fully headless client is currently supported; a user-reported offscreen workaround is not an official headless mode. macOS lacks mpv and current packaged .app; Wayland has mpv/UI caveats. ([R30-S18](<#r30-s18>), [R30-S19](<#r30-s19>))
- **explicit:** Store SQLite locally, not on unreliable network locking or live cloud-sync folders. External backup must capture all related databases together while the client is stopped. ([R30-S19](<#r30-s19>), [R30-S20](<#r30-s20>))
- **explicit:** Deleting a file does not erase tags/ratings/notes/URLs and historical records; comprehensive purge is still being developed. Drive encryption must come from the OS/external storage tools, not an asserted built-in vault. ([R30-S18](<#r30-s18>))
- **explicit:** Automatic duplicate rules may delete/merge without review; undo does not undo metadata merge. Pairwise visual confidence is not mathematical identity; detailed relationship history/UI remain incomplete and giant alternate sets scale poorly. ([R30-S7](<#r30-s7>), [R30-S8](<#r30-s8>))
- **explicit:** Downloader credentials are not securely stored; simple login scripts are described as old and fragile. API defaults to HTTP and network services disclose data to configured endpoints. ([R30-S14](<#r30-s14>), [R30-S23](<#r30-s23>))
- **explicit:** Repository synchronization usually propagates on roughly 100,000-second periods, not instant sharing. Subscriptions assume newest-first listings and may miss late-tagged content or historical gaps. ([R30-S22](<#r30-s22>), [R30-S15](<#r30-s15>))
- **coverage-gap:** Native face recognition, GPS photo mapping, RAW camera decoding, general photo editing and a durable per-file-operation crash-recovery journal are not established. External AI/video tools are recorded only as plugins. ([R30-S5](<#r30-s5>), [R30-S17](<#r30-s17>), [R30-S23](<#r30-s23>))
- **Coverage gap:** Third-party integrations not executed or exhaustively inventoried as core features.
- **Coverage gap:** No public code run, benchmark or security audit; older example/UI wording is qualified against current platform and release notes.
- **Coverage gap:** Focused localization/translation documentation search and inspected manuals did not establish translated application UI; arbitrary-language tags and third-party tools are not counted as UI localization.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations, interface localization.

## Inspected primary sources

### R30-S1

[Hydrus README](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/README.md>)
- Kind/ref: readme; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete README
- Establishes: Purpose, privacy defaults, platforms, playback and maintenance/security context.

### R30-S2

[Version 694 release notes](<https://github.com/hydrusnetwork/hydrus/releases/tag/v694a>)
- Kind/ref: release; v694a
- Sections inspected: Complete release note
- Establishes: Current fixes, trash grace period and legacy security update warning.

### R30-S3

[Introduction](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/introduction.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Local managed database and opt-in network services.

### R30-S4

[Importing and exporting](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_importing.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Copy imports, exact dedupe, import restrictions, automated folders, pattern exports and tag archives.

### R30-S5

[Files, viewer and inbox workflow](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_files.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Viewer controls, archive/delete filtering, trash, immutable stored bytes and page-size limits.

### R30-S6

[Searching and sorting](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_searching.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Domains, Boolean predicates, wildcard/autocomplete, saved queries and result-limiting semantics.

### R30-S7

[Filtering duplicates](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/duplicates.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Perceptual/pixel matching, pair review, keepers, remembered relations, metadata merge and video extension.

### R30-S8

[Duplicate auto-resolution](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/advanced_duplicates_auto_resolution.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Rule setup, comparisons, action, preview, semi/full automation, examples and future section
- Establishes: Configurable automation, confidence tests, metadata-preservation predicates and incomplete undo.

### R30-S9

[Tags](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_tags.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Namespaced tags, private services, keyboard editing and query cancellation.

### R30-S10

[Tag services, repositories and relationships](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_more_tags.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Tag-domain isolation, aliases/implications, precedence, shared tag sync and petitions.

### R30-S11

[Ratings](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_ratings.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Like/dislike, configurable numeric scales, counters, bulk editing and rating search.

### R30-S12

[Sidecars](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/advanced_sidecars.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: TXT/JSON metadata routing, parsing previews and tag/URL/note export.

### R30-S13

[Multiple local file domains](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/advanced_multiple_local_file_services.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Overlapping local subsets, domain moves, combined searches and two-stage trash.

### R30-S14

[Downloading](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_downloading.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Downloader types, options, tags/notes, bandwidth and logins; external tools section
- Establishes: Manual/gallery/thread workflows, parser dependency, throttling and credential caveats.

### R30-S15

[Subscriptions](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_subscriptions.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Adaptive polling, resume, limits, publication and query regrouping.

### R30-S16

[Repository privacy](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/privacy.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: HTTPS, generic metadata sync, account attribution, IP/content risks and delayed anonymisation.

### R30-S17

[Supported file types](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/filetypes.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Distinguishes importing, thumbnails and actual playback for each format.

### R30-S18

[FAQ](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/faq.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Filenames/external-files, SQLite, hashes, service isolation, tag backfill, headless and encrypted drives
- Establishes: SHA-256 storage, no in-place library mode, retained metadata and explicit limitations.

### R30-S19

[Installation and backups](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/getting_started_installing.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Downloading/Installing including all platform tabs; complete Backing up and low-space backup sections
- Establishes: Current OS distributions, portable data, database-placement restrictions and backup workflow.

### R30-S20

[Database and storage migration](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/database_migration.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Weighted storage tiers, limits, independent databases, portability and unavailable-volume restrictions.

### R30-S21

[Recovering missing media and records](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/help_my_media_files_are_broke.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Missing-file reconciliation, URL redownload, thumbnail regeneration and orphan export.

### R30-S22

[Running a repository server](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/server.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete document
- Establishes: Separate optional server, service/accounts, sync latency and backups.

### R30-S23

[Client API and user-created tools](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/docs/client_api.md>)
- Kind/ref: manual; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Enabling API and complete third-party tools overview
- Establishes: Explicit enabling/access keys, transport defaults and external web/mobile/AI/video-dedupe integrations.

### R30-S24

[File-maintenance task descriptions](<https://github.com/hydrusnetwork/hydrus/blob/c78a5cbe76e7b77a2f652187e8343907fa7f27ba/hydrus/client/files/ClientFilesMaintenance.py>)
- Kind/ref: code; c78a5cbe76e7b77a2f652187e8343907fa7f27ba
- Sections inspected: Complete task-label and description mappings, regeneration ordering
- Establishes: Content integrity checks, metadata presence/read flags, thumbnail/hash rebuilding and repair variants.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
