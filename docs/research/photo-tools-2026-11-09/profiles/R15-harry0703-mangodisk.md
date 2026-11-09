# R15 — harry0703/MangoDisk

[Repository](<https://github.com/harry0703/MangoDisk>) · 5,446 stars at the frozen snapshot · cleanup · Not archived

**Purpose:** Cross-platform disk-space analyzer and safety-oriented cleaner; relevant to photo libraries chiefly for exact duplicate and large-file cleanup, not visual photo organization.

**Deployment:** macOS 12.5+ desktop; 64-bit Windows 10+ desktop; Linux .deb and AppImage, Ubuntu 22.04+ recommended, x64/ARM64; CLI packages for macOS/Windows; Linux CLI built from source

**Storage:** Analyzes existing filesystem roots and retains bounded scan/session indexes, local settings and operation history. Duplicate results use logical file length plus physical-allocation accounting. Cleanup directly deletes selected files; this is not a managed photo library.

**Privacy/network behavior:** Core filesystem scanning is local and read-only until confirmed actions. Optional AI explanations send allowlisted metadata including full paths to an official or custom provider, not file contents. Official AI context/replies are retained for 30 days; custom-provider credentials are stored in plaintext local JSON. This is not a blanket offline/no-telemetry or encryption claim.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v1.2.3 (2026-11-06T00:44:02Z)
**Repository pushed at:** 2026-11-06T09:36:50Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a512f290d63f](<https://github.com/harry0703/MangoDisk/commit/a512f290d63ff7863993b0cb999492070eaefb3b>).
**Product lineage:** harry0703/MangoDisk.

## Maturity and availability caveats

- Frozen main commit a512f290d63ff7863993b0cb999492070eaefb3b; release v1.2.3 dated 2026-11-06.
- README's safety, speed and optimization assertions are project claims, not validation or benchmarks performed for this inventory.
- Platform-specific cleanup and system tools vary; Linux standalone prebuilt CLI is explicitly not yet available.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Optional item-level AI explanations**<br>`ai.cleanup_explanations` | O | Explains cleanup, privacy, startup, settings, maintenance, large/duplicate files and uninstall candidates on explicit request. Does not select items, change risk classification, execute commands or authorize cleanup. | [R15-S7](<#r15-s7>) |
| **Official or custom explanation provider**<br>`ai.remote_inference` | O | Official builds offer a daily free quota; custom OpenAI-compatible endpoints can include local loopback services. Official initial policy is 20/day with 60-second cooldown and 30-day context/reply retention; provider settings and billing remain separate. | [R15-S7](<#r15-s7>) |
| **Snapshot JSON/Markdown reports**<br>`analytics.analysis_export` | C | Exports current-directory analysis with depth 1–6, optional full paths, configurable entry limits and separate remainder/omission accounting; never silently rescans. Reports are evidence, not importable state or deletion authority. | [R15-S8](<#r15-s8>) |
| **Explicit incomplete-scan reporting**<br>`analytics.scan_coverage` | C | Reports omissions by permissions, read errors, exclusions, link/mount boundaries and unknown causes; unreadable is distinguished from measured empty directories. | [R15-S8](<#r15-s8>) |
| **Treemap and sunburst disk analysis**<br>`analytics.storage_distribution` | C | Switch visualization and depth while browsing folder/file lists; Standard measures physical allocated bytes, while Windows Fast uses logical lengths. | [R15-S1](<#r15-s1>), [R15-S8](<#r15-s8>) |
| **Paged duplicate results**<br>`browse.pagination` | C | Complete bounded duplicate results remain in Rust; only an initial page enters the WebView and later pages load on demand using a scan ID. | [R15-S3](<#r15-s3>) |
| **Local model and download cache discovery**<br>`cleanup.ai_model_cache` | C | Surfaces large local AI models, cached downloads and temporary transfers as reclaimable-space candidates, not as photo-analysis models. | [R15-S1](<#r15-s1>) |
| **Large-file discovery**<br>`cleanup.large_files` | C | Finds large installers, video files, archives and other bulky content for review without implying video playback or perceptual-video matching. | [R15-S1](<#r15-s1>) |
| **Rebuildable development-project cleanup**<br>`cleanup.project_artifacts` | C | Finds dependencies, caches and build directories across Node.js, Rust, Gradle, Swift, Python, .NET, Godot and CMake projects. | [R15-S1](<#r15-s1>) |
| **Rule-based deep cleanup**<br>`cleanup.temporary_junk` | C | Scans system/user temporary data, application caches/logs/update packages, browser caches, package managers, IDE/compiler/Xcode data and inactive container build caches. | [R15-S1](<#r15-s1>) |
| **Linux desktop**<br>`deployment.linux` | C | x64/ARM64 .deb and AppImage distributions; Ubuntu 22.04+ recommended and other distro compatibility depends on libraries/desktop. | [R15-S1](<#r15-s1>) |
| **Eleven offline UI locales**<br>`deployment.localization` | C | Runtime registers English, Simplified/Traditional Chinese, Japanese, Korean, Russian, Turkish, Brazilian Portuguese, French, German and Spanish. Bundled message graph permits offline view-language switching; English is fallback and French/Russian have explicit plural rules. | [R15-S9](<#r15-s9>) |
| **macOS desktop**<br>`deployment.macos` | C | DMG and Homebrew Cask distribution for macOS Monterey 12.5 or later. | [R15-S1](<#r15-s1>) |
| **Windows desktop**<br>`deployment.windows` | C | Native Windows installer for 64-bit Windows 10+; WinGet and official download are documented. | [R15-S1](<#r15-s1>) |
| **Content-hash duplicate detection**<br>`duplicates.exact_hash` | C | Groups equal-size files by BLAKE3 content hash after sample filtering. Sample hashes alone do not establish equality; full hashing checks open-file identity/size/time and current path. | [R15-S3](<#r15-s3>) |
| **Duplicate scan exclusions**<br>`duplicates.exclude_paths` | C | Public product scan entry accepts exclusion options alongside typed cleanable/protected roots. | [R15-S3](<#r15-s3>) |
| **Aggregate duplicate directory trees**<br>`duplicates.folders` | C | Builds recursive fingerprints from file sizes/content hashes and child-tree fingerprints, sorting tokens without incorporating filenames. Skips empty trees, unreadable/unknown entries and link-like objects; this is content/tree equivalence, not identical names. | [R15-S6](<#r15-s6>) |
| **Clear a group's deletion selection**<br>`duplicates.keep_all` | C | Toggling an already-selected smart-selection group clears its paths while retaining selections in other groups. | [R15-S5](<#r15-s5>) |
| **Selectable smart keeper rules**<br>`duplicates.keeper_selection` | C | Prefer shortest path by default, shortest filename, oldest modification or newest modification; deterministic tie-breaks handle equal/missing times. Protected copies become keepers automatically. | [R15-S5](<#r15-s5>) |
| **Protected reference roots**<br>`duplicates.reference_folders` | C | Protected locations participate in matching but cannot be deleted. Directories containing protected descendants are also rejected; protection changes deletion authority, not scan coverage. | [R15-S3](<#r15-s3>), [R15-S4](<#r15-s4>) |
| **Deleting every duplicate copy is rejected**<br>`duplicates.remove_all` | N | Both selection utilities and native validation require at least one remaining entry in every affected duplicate group. | [R15-S4](<#r15-s4>), [R15-S5](<#r15-s5>) |
| **Minimum duplicate file size**<br>`duplicates.size_bounds` | C | Duplicate scan APIs accept minimum_bytes to limit eligible files; no maximum-size selector is established here. | [R15-S3](<#r15-s3>) |
| **Scriptable cleanup CLI**<br>`integration.cli` | C | Shared cleanup engine offers scan-only default, --apply, selection policy, --dry-run, JSON output and --no-progress; non-interactive mutation additionally requires --yes. | [R15-S1](<#r15-s1>) |
| **Analyze multiple selected roots**<br>`library.multiple_roots` | C | Duplicate scan takes a vector of filesystem roots, including separately protected descendants; this is scan scope rather than multiple photo catalogues. | [R15-S3](<#r15-s3>) |
| **Cooperative scan cancellation**<br>`performance.cancel` | C | Hashing checks cancellation between reads/samples and recursive directory fingerprinting checks its operation guard; disk analysis also documents cancellation. | [R15-S3](<#r15-s3>), [R15-S6](<#r15-s6>), [R15-S8](<#r15-s8>) |
| **Storage-aware duplicate hashing**<br>`performance.parallel_scan` | C | Concurrency depends on available CPUs and volume scheduling; rotational, removable, network and unknown storage use one hashing worker to limit random-I/O costs. | [R15-S3](<#r15-s3>) |
| **Retain tool results during navigation**<br>`performance.retained_page_state` | C | 1.2.3 scans uninstall/startup/privacy pages on first opening and preserves results, scroll position and category choices on page switches. | [R15-S2](<#r15-s2>) |
| **Atomic report publication**<br>`safety.atomic_report_export` | C | Analysis export flushes and syncs a sibling temporary file before atomic publication; failed writes preserve the previous report destination. This is report safety, not copied-photo verification. | [R15-S8](<#r15-s8>) |
| **Review and native deletion preflight**<br>`safety.confirmation` | C | Native duplicate deletion verifies current-scan membership, expected size/modification and protected roots independently of UI selection; stale/foreign candidates are rejected. | [R15-S1](<#r15-s1>), [R15-S4](<#r15-s4>) |
| **Explicit permanent cleanup**<br>`safety.permanent_delete` | C | Duplicate and disk-analysis deletion directly remove selected files, report removed/already-absent/failed outcomes and reconcile scan caches. Analysis stops a batch on possible partial mutation or lost authority. | [R15-S3](<#r15-s3>), [R15-S8](<#r15-s8>) |
| **Read-only scan phase**<br>`safety.read_only_originals` | C | Default scans do not modify files. Cleanup, uninstall and system changes require explicit review/confirmation; this is not an immutable library mode once actions are approved. | [R15-S1](<#r15-s1>) |
| **Browser and system trace cleanup**<br>`system.activity_trace_cleanup` | C | Clears selected browsing history, searches, cookies, recent items and clipboard traces; this is an OS/application administration tool, not photo-metadata privacy or secure disk erasure. | [R15-S1](<#r15-s1>) |
| **Shrink supported application installations**<br>`system.application_optimization` | C | Deep Cleanup overview documents application optimization to reduce supported application size without affecting normal use; exact eligible apps and transformations are not specified there. This is not photo compression. | [R15-S1](<#r15-s1>) |
| **Uninstall applications and remnants**<br>`system.application_uninstall` | C | Uninstalls applications and reviews associated caches/settings/leftovers, treating potential personal files cautiously. AI manual warns vendor uninstallers control their own final scope. | [R15-S1](<#r15-s1>), [R15-S7](<#r15-s7>) |
| **Windows file-oriented menu actions**<br>`system.context_menu_extensions` | C | Add copy-path/name/image-dimensions, terminal-here, desktop shortcuts and system-tool shortcuts. | [R15-S2](<#r15-s2>) |
| **Windows Explorer menu management**<br>`system.context_menu_management` | C | Since 1.2.3, browse by app/menu location, disable/restore/remove entries, configure file types, switch supported Windows 11/classic styles and optionally restart Explorer. | [R15-S2](<#r15-s2>) |
| **Common system repair actions**<br>`system.maintenance` | C | Documented maintenance targets missing search results, incorrect icons, sound and network issues; available operations depend on platform. | [R15-S1](<#r15-s1>) |
| **Resource-heavy app and memory management**<br>`system.memory_management` | C | Find and quit resource-heavy applications and free memory manually or automatically; performance improvements are project claims. | [R15-S1](<#r15-s1>) |
| **Cleanup and change history**<br>`system.operation_history` | C | Records completed cleanup/system changes, reclaimed space and failures. Duplicate deletion appends history after execution; this is not an undo-capable transactional operation journal. | [R15-S1](<#r15-s1>), [R15-S3](<#r15-s3>) |
| **Live resource and hardware metrics**<br>`system.resource_monitor` | C | CPU/GPU/memory/network/disk trends; supported devices also expose temperature, power, battery and disk-health information, with menu/taskbar/tray/floating displays. These are whole-computer metrics, not photo-library analytics. | [R15-S1](<#r15-s1>) |
| **Disable and re-enable startup entries**<br>`system.startup_management` | C | Manage startup registrations to reduce login/background load, with ability to turn entries back on. | [R15-S1](<#r15-s1>) |
| **Built-in system settings optimization**<br>`system.validated_optimization` | C | Only built-in validated settings are accepted; no arbitrary commands/scripts/registry paths. Values are reread after changes and high-impact, elevated or restart-required actions are flagged. | [R15-S1](<#r15-s1>) |

## Limitations and evidence gaps

- **explicit:** Cleanup, permanent deletion and uninstall may not be reversible; keep independent backups. Operation History is not proof of undo or OS-trash recovery. ([R15-S1](<#r15-s1>), [R15-S3](<#r15-s3>))
- **explicit:** Exact equality does not prove different application paths are interchangeable. AI explanations are advisory and cannot authorize deletion. ([R15-S7](<#r15-s7>))
- **explicit:** AI metadata can include full paths and installation identity; official service retains context/replies 30 days. Custom credentials are plaintext in local ai.json, and custom HTTP endpoints do not encrypt keys or requests. ([R15-S7](<#r15-s7>))
- **explicit:** Reports use retained scan data with limits and omission accounting, not an unrestricted fresh filesystem inventory. Windows Fast reports logical bytes, which can differ substantially from actual sparse/compressed disk usage. ([R15-S8](<#r15-s8>))
- **coverage-gap:** Source inspection establishes hash matching, not byte-by-byte pair verification, perceptual image/video matching, hardlink replacement or a photo-viewing catalogue. ([R15-S3](<#r15-s3>), [R15-S6](<#r15-s6>))
- **explicit:** Linux prebuilt standalone CLI is not yet provided; build from source is documented. ([R15-S1](<#r15-s1>))
- **Coverage gap:** No photo-specific EXIF/face/map/editor features established; scope is filesystem/system management.
- **Coverage gap:** No independent performance or safety validation performed and no public code executed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R15-S1

[MangoDisk README](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/README.md>)
- Kind/ref: readme; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete README including all feature groups, safety, desktop platforms and CLI
- Establishes: Cleanup/system capabilities, deployment and mandatory review boundaries.

### R15-S2

[MangoDisk 1.2.3](<https://github.com/harry0703/MangoDisk/releases/tag/v1.2.3>)
- Kind/ref: release; v1.2.3
- Sections inspected: Complete English and Chinese release notes
- Establishes: Windows context menus, scan-state preservation and analysis export improvements.

### R15-S3

[Duplicate scan and deletion service](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/src-tauri/crates/mangodisk-core/src/storage/duplicates/service.rs>)
- Kind/ref: code; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete public scan entry points, permanent deletion method, protection/group construction, worker scheduling and sample/full hashing functions
- Establishes: BLAKE3 equality, configurable roots/exclusions, paged results, storage-aware concurrency and permanent deletion.

### R15-S4

[Duplicate deletion authority](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/src-tauri/crates/mangodisk-core/src/storage/duplicates/session.rs>)
- Kind/ref: code; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete validate_permanent_delete_candidates function
- Establishes: Current-scan binding, keep-one enforcement, changed-item rejection and protected roots.

### R15-S5

[Duplicate smart selection](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/src/lib/utils/storage/duplicate-file-selection.ts>)
- Kind/ref: code; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete file
- Establishes: Shortest-path/name and modification-time keeper policies and group deselection.

### R15-S6

[Content-based directory aggregation](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/src-tauri/crates/mangodisk-core/src/storage/duplicates/directory_aggregation.rs>)
- Kind/ref: code; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete fingerprint_known_directory, fingerprint_tokens, file_token and directory_token functions
- Establishes: Whole-tree content fingerprints, omitted filenames and conservative rejection rules.

### R15-S7

[Optional AI explanations](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/src-tauri/crates/mangodisk-core/src/ai/README.md>)
- Kind/ref: manual; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete document: boundaries, provider contract, storage, request limits and feedback
- Establishes: Precise AI data disclosure, retention, local credentials, quotas and non-execution boundaries.

### R15-S8

[Analysis snapshots and scan metrics](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/src-tauri/crates/mangodisk-core/src/storage/analysis/README.md>)
- Kind/ref: manual; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete document
- Establishes: Allocated/logical size modes, bounded report exports, omissions, privileges and batch-delete safeguards.

### R15-S9

[Runtime interface localization](<https://github.com/harry0703/MangoDisk/blob/a512f290d63ff7863993b0cb999492070eaefb3b/src/i18n.ts>)
- Kind/ref: code; a512f290d63ff7863993b0cb999492070eaefb3b
- Sections inspected: Complete file
- Establishes: Eleven registered UI locale message resources, offline switching and plural handling.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
