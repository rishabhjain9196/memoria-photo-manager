# R34 — pkolaczk/fclones

[Repository](<https://github.com/pkolaczk/fclones>) · 2,994 stars at the frozen snapshot · cleanup · Not archived

**Purpose:** High-throughput file-content deduplication CLI with inspectable reports, replica-count policies and filesystem-aware linking/deduplication; not a visual photo manager.

**Deployment:** Native command-line executable on Linux, macOS and Windows; Linux Snap, Homebrew, release binaries and Rust source distribution; Separate fclones-gui project, not part of this inventory

**Storage:** Reads arbitrary existing files in place; optional persistent hash database in the user's OS cache directory. Reports separate discovery from deletion/move/link/reflink actions.

**Privacy/network behavior:** Documented filesystem-local pipeline; external preprocessing commands are optional and have their own behavior. No cloud account or upload is required by the documented workflow.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v0.35.0 (2025-03-03T09:52:10Z)
**Repository pushed at:** 2025-03-03T09:50:02Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a74f90d293e0](<https://github.com/pkolaczk/fclones/commit/a74f90d293e05856d19a4c0ac2b29b46ef16cf23>).
**Product lineage:** pkolaczk/fclones.

## Maturity and availability caveats

- Pinned a74f90d293e05856d19a4c0ac2b29b46ef16cf23; latest release v0.35.0, 2025-03-03.
- README says Linux is best supported and some optimizations are Linux-only. Published benchmarks concern older releases/hardware and were not reproduced.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Bytewise verification**<br>`duplicates.byte_compare` | N | Algorithm documentation explicitly says no byte-by-byte file comparison is performed; identity relies on size and hashes. | [R34-S1](<#r34-s1>) |
| **Match only across independent trees**<br>`duplicates.cross_root_isolation` | C | --isolate counts matching content within one root as one replica, distinguishing cross-tree backups from repeated paths inside a tree; removal can retain/drop a root's matching files together. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Delete redundant files**<br>`duplicates.delete_files` | C | remove permanently removes selected redundant entries using the separately reviewed report and keeper policies. | [R34-S1](<#r34-s1>) |
| **Non-mutating action preview**<br>`duplicates.dry_run` | C | --dry-run emits planned filesystem operations instead of executing them; output can be redirected with the CLI output option. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Content-hash duplicate groups**<br>`duplicates.exact_hash` | C | Groups by length, file identity, prefix hash, suffix hash and finally whole-content hash. Default MetroHash128 can be replaced by xxhash3, BLAKE3, SHA-256/512 or SHA3-256/512. | [R34-S1](<#r34-s1>) |
| **Glob/regex inclusion and exclusion**<br>`duplicates.exclude_paths` | C | Filename/path patterns, excluded paths, case-insensitive mode and Perl-compatible regex alternatives constrain scans. Hidden files and .gitignore/.fdignore matches are skipped unless overridden. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Single-filesystem matching**<br>`duplicates.filesystem_boundary` | C | --one-fs skips nested mount points and cross-filesystem symlinks and avoids matching across devices/filesystems. | [R34-S2](<#r34-s2>) |
| **Hard-link replacement**<br>`duplicates.hardlinks` | C | link defaults to replacing redundant copies with hard links to retained content. | [R34-S1](<#r34-s1>) |
| **Persistent reusable hash cache**<br>`duplicates.hash_cache` | C | --cache stores hashes with identity, size and timestamps; unchanged files reuse hashes even after typical renames/moves. Metadata-stable modifications can make the cache stale. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Keeper and replica policies**<br>`duplicates.keeper_selection` | C | Default report order preserves earlier entries; priorities can instead select removal by creation/modification/access time, Unix status-change time or nesting depth. At least one retained replica is required by the action CLI. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Existing-link accounting**<br>`duplicates.existing_hardlink_policy` | C | Normally counts multiple links to the same underlying file only once. Flags independently control following/reporting symbolic links, matching links and isolated-root replica semantics. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Move redundant copies**<br>`duplicates.move_aside` | C | move sends selected redundant files to a target directory instead of deleting or linking them; this is not described as an OS trash integration. | [R34-S1](<#r34-s1>) |
| **Optional partial-hash-only matching**<br>`duplicates.partial_hash_only` | C | --skip-content-hash bypasses whole-file hashing, with explicit false-positive warnings and advice to enlarge prefix/suffix samples. This mode is not safe exact-content verification. | [R34-S2](<#r34-s2>) |
| **External preprocessing before matching**<br>`duplicates.preprocess_matching` | O | --transform invokes an external program per file, with pipe or $IN/$OUT support. Documentation demonstrates stripping EXIF with exiv2 before matching, not perceptual image matching. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Protected file/path patterns**<br>`duplicates.reference_folders` | C | --keep-name and --keep-path prevent matching entries being removed; action --name/--path restrict the eligible deletion set. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Filesystem-native copy-on-write dedupe**<br>`duplicates.reflinks` | C | dedupe shares underlying file data without removing filenames on supported filesystems. This feature is explicitly unavailable on Windows. | [R34-S1](<#r34-s1>) |
| **Unique and under/over-replicated files**<br>`duplicates.replication_counts` | C | Can report unique files or groups below/above a chosen replication factor, rather than only pairs of duplicates. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Reviewable machine-readable reports**<br>`duplicates.report_export` | C | Exports default text with hashes/sizes, fdupes-compatible text, CSV or JSON. Removal tools accept default and JSON reports, allowing manual editing before action. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Minimum/maximum size**<br>`duplicates.size_bounds` | C | Inclusive byte-size bounds accept decimal/binary units; minimum defaults to one byte. | [R34-S2](<#r34-s2>) |
| **Symbolic-link replacement**<br>`duplicates.symlinks` | C | link --soft replaces redundant files with symbolic links; link-following/matching combinations require care to avoid leaving dangling references. | [R34-S1](<#r34-s1>) |
| **Composable command-line workflow**<br>`integration.cli` | C | group emits reports; remove, move, link and dedupe consume previous discovery results. Input paths can come from arguments or stdin for composition with tools such as find. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Shell completion generation**<br>`integration.shell_completion` | C | complete prints setup scripts for Bash, Zsh, Fish, Elvish and PowerShell; installation into the shell is manual. | [R34-S1](<#r34-s1>), [R34-S3](<#r34-s3>) |
| **Multiple scan roots**<br>`library.multiple_roots` | C | One invocation accepts multiple files/directories and recursively scans directories with a configurable depth limit. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Linux-specific I/O optimization**<br>`performance.linux_io_optimization` | C | Orders accesses by physical placement and uses page-cache drop-behind on Linux; documentation says these optimizations are unavailable on other platforms. | [R34-S1](<#r34-s1>) |
| **Compressed paths for large trees**<br>`performance.low_memory_paths` | C | README attributes low memory use on millions of paths to prefix-compressed representations; this is a project claim, not a measured result here. | [R34-S1](<#r34-s1>) |
| **Storage-adaptive parallel processing**<br>`performance.parallel_scan` | C | Parallel directory traversal and staged hashing use separate per-device random/sequential pools, automatically tuned for HDD/SSD/removable/unknown devices and overridable with --threads. | [R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>) |
| **Terminal-aware progress**<br>`performance.progress_reporting` | C | Reports scan/grouping progress; v0.35.0 limits default progress output to terminal stderr for cleaner redirected workflows. | [R34-S1](<#r34-s1>), [R34-S3](<#r34-s3>) |
| **Reuse interrupted hashing work**<br>`performance.resume` | C | README recommends persistent caching to resume large jobs quickly after interruption; it is hash reuse rather than a transactional deletion journal. | [R34-S1](<#r34-s1>) |
| **Filesystem-local operation**<br>`privacy.no_upload_required` | C | Documented core workflow reads local/mounted paths and writes local reports/actions; no hosted service is required. | [R34-S1](<#r34-s1>) |
| **Changed-file action guards**<br>`safety.changed_file_guards` | C | Actions check sizes against the report unless disabled, lock files unless --no-lock is selected and can skip whole groups if any file changed after --modified-before. Transformed reports automatically disable size checks. | [R34-S2](<#r34-s2>) |
| **Protect originals during transforms**<br>`safety.transform_copy` | C | $IN transformations use a temporary copy by default; --no-copy deliberately permits the external command to modify the original and is warned as data-loss-prone. | [R34-S2](<#r34-s2>) |

## Limitations and evidence gaps

- **coverage-gap:** Translated command-line help/output or a selectable UI language is not established by the inspected manual and CLI definitions; localization is left undocumented rather than marked unsupported. ([R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>))
- **explicit:** No bytewise comparison is performed; skipping full-content hashes further weakens duplicate certainty. ([R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>))
- **explicit:** Reflink deduplication is unsupported on Windows; physical-placement and cache-drop optimizations are Linux-only. ([R34-S1](<#r34-s1>))
- **explicit:** Combining --match-links with --symbolic-links can delete the only regular file and leave orphan symlinks. Cached hashes can be stale when changes preserve recorded metadata. ([R34-S1](<#r34-s1>))
- **coverage-gap:** Photo display, perceptual near-duplicate detection, face/EXIF catalogue search, albums, maps and recoverable trash are not documented; arbitrary-file support must not be interpreted as media playback. ([R34-S1](<#r34-s1>), [R34-S2](<#r34-s2>))
- **Coverage gap:** No standalone photo-oriented manual; the extensive README is the primary user manual, supplemented by CLI declarations and release notes.
- **Coverage gap:** No runtime/platform validation or benchmark reproduction.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R34-S1

[README and command manual](<https://github.com/pkolaczk/fclones/blob/a74f90d293e05856d19a4c0ac2b29b46ef16cf23/README.md>)
- Kind/ref: readme; a74f90d293e05856d19a4c0ac2b29b46ef16cf23
- Sections inspected: Complete README including features, usage, links, preprocessing, algorithm, tuning and benchmarks
- Establishes: Detailed discovery/actions manual, hash semantics, caching and platform restrictions.

### R34-S2

[CLI configuration and help](<https://github.com/pkolaczk/fclones/blob/a74f90d293e05856d19a4c0ac2b29b46ef16cf23/fclones/src/config.rs>)
- Kind/ref: code; a74f90d293e05856d19a4c0ac2b29b46ef16cf23
- Sections inspected: OutputFormat, complete GroupConfig and DedupeConfig, Priority and beginning of Command
- Establishes: Precise filtering, hash bypass warnings, date guards, locking and keeper constraints.

### R34-S3

[v0.35.0 release](<https://github.com/pkolaczk/fclones/releases/tag/v0.35.0>)
- Kind/ref: release; v0.35.0
- Sections inspected: Complete release body
- Establishes: Shell completions and terminal-sensitive progress reporting.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
