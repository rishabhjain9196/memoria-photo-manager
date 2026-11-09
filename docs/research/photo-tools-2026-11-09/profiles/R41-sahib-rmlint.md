# R41 — sahib/rmlint

[Repository](<https://github.com/sahib/rmlint>) · 2,467 stars at the frozen snapshot · cleanup · Not archived

**Purpose:** Unix-oriented exact-content duplicate and filesystem-lint scanner that emits reviewable action scripts, with optional byte comparison, tree deduplication, caches, reflink operations and a Shredder GUI.

**Deployment:** Linux CLI and distribution packages; Source builds on other Unices including FreeBSD, Darwin and Solaris; Linux is primary target; Optional Python/GTK Shredder desktop frontend

**Storage:** Traverses existing files directly. Normal scanning emits shell/JSON reports without deleting media. Optional caches write checksums/timestamps into filesystem extended attributes; replay consumes saved JSON. Separate generated scripts or standalone --dedupe perform changes.

**Privacy/network behavior:** Local filesystem analysis does not require hosted media services. Hash caches, JSON reports and scripts contain paths and other file metadata. Custom handlers can invoke external tools, so privacy depends on those configured commands.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v2.11.0 (2026-11-01T23:52:28Z)
**Repository pushed at:** 2026-11-03T17:49:46Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [fd20430ef830](<https://github.com/sahib/rmlint/commit/fd20430ef830eab25b5726df8498a04d9a4b804f>).
**Product lineage:** sahib/rmlint.

## Maturity and availability caveats

- Frozen master fd20430ef830eab25b5726df8498a04d9a4b804f; latest release v2.11.0 dated 2026-11-01.
- Tutorial marks duplicate-tree merging experimental and GUI documentation warns it is still developing; old GUI dependency text is superseded by v2.11.0's Python 3.12/GTK 3.22 minimums.
- Tutorial and manpage contain some differing historical defaults; precise current option semantics below follow pinned manpage and v2.11.0 notes rather than generic examples.
- Performance descriptions are project claims, not benchmarks run here.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Duplicate distribution chart**<br>`analytics.storage_distribution` | O | GUI charts duplicate distribution across scanned directories and shows a running affected-byte count during script execution. | [R41-S4](<#r41-s4>) |
| **Live GUI scan results**<br>`browse.live_scan_tree` | O | Shredder streams CLI JSON into a tree while scanning and allows editing keep/delete decisions after scan. | [R41-S4](<#r41-s4>) |
| **Find broken symbolic links**<br>`cleanup.invalid_symlinks` | C | badlinks identifies symbolic links without valid targets. | [R41-S1](<#r41-s1>), [R41-S5](<#r41-s5>) |
| **Find unstripped binaries**<br>`cleanup.debug_symbols` | C | Optional lint type identifies binaries retaining debug symbols; it is not enabled by default. | [R41-S5](<#r41-s5>) |
| **Find empty files**<br>`cleanup.empty_files` | C | Dedicated selectable empty-file lint type, independently configurable from duplicate content matching. | [R41-S1](<#r41-s1>), [R41-S5](<#r41-s5>) |
| **Find nested empty directories**<br>`cleanup.empty_folders` | C | Finds empty directories including nested empty trees. | [R41-S5](<#r41-s5>) |
| **Find invalid owner/group IDs**<br>`cleanup.invalid_ownership` | C | badids identifies files with unresolved UID/GID ownership. | [R41-S1](<#r41-s1>), [R41-S5](<#r41-s5>) |
| **Linux distribution packages**<br>`deployment.linux` | C | Linux is the primary target and README points to distribution packages; other Unices compile with some optimizations unavailable. | [R41-S1](<#r41-s1>) |
| **Localized runtime interface messages**<br>`deployment.localization` | C | Gettext catalogues translate runtime/CLI messages and LANG selects the locale when compiled translation support is installed. v2.11.0 adds Japanese; inspected Japanese messages include help/errors and command-option diagnostics. This evidence establishes terminal-interface localization, not completeness of every Shredder GUI translation. | [R41-S6](<#r41-s6>), [R41-S7](<#r41-s7>), [R41-S8](<#r41-s8>) |
| **Shredder GTK frontend**<br>`deployment.optional_gui` | O | rmlint --gui launches separately installed GUI dependencies; 2.11.0 requires Python 3.12/GTK 3.22 for the GUI. | [R41-S4](<#r41-s4>), [R41-S5](<#r41-s5>), [R41-S6](<#r41-s6>) |
| **Paranoid byte comparison**<br>`duplicates.byte_compare` | C | --paranoid or --algorithm=paranoid compares file bytes rather than relying on digest equality. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Review and dry-run action plans**<br>`duplicates.dry_run` | C | Normal scan does not delete files; scripts can be inspected/edited first, Python output provides dry run, and GUI explicitly distinguishes dry versus destructive execution. | [R41-S2](<#r41-s2>), [R41-S4](<#r41-s4>), [R41-S5](<#r41-s5>) |
| **Configurable content hashing**<br>`duplicates.exact_hash` | C | Default BLAKE2b content matching with alternative BLAKE3, SHA, MD5, Highway, Metro, Murmur and xxHash variants. 64-bit hashes are explicitly discouraged for duplicate safety. | [R41-S5](<#r41-s5>), [R41-S6](<#r41-s6>) |
| **Composable input selection**<br>`duplicates.exclude_paths` | C | Use find or another selector to pipe paths, including NUL-separated paths, rather than a built-in arbitrary include/exclude regex engine. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Handle existing hardlink aliases**<br>`duplicates.existing_hardlink_policy` | C | Default considers hardlinks; --keep-hardlinked preserves aliases of the original, while --no-hardlinked considers only the highest-ranked member and ignores other aliases. | [R41-S5](<#r41-s5>) |
| **Whole duplicate directory trees**<br>`duplicates.folders` | C | --merge-directories aggregates matching file content into duplicate trees. Default equality disregards names/layout and empty-file contents; --honour-dir-layout requires matching relative layout. Marked experimental in tutorial. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Hardlink action plans**<br>`duplicates.hardlinks` | C | Generated scripts can replace duplicates with hardlinks; they require same filesystem and can fall back to symlinks when configured. | [R41-S5](<#r41-s5>) |
| **Extended-attribute checksum cache**<br>`duplicates.hash_cache` | C | Separate read/write/clear xattr controls cache checksum and timestamp; requires filesystem support and write access for writes, and relies on mtime to invalidate stale values. Cross-endian portability depends on algorithm. | [R41-S5](<#r41-s5>), [R41-S6](<#r41-s6>) |
| **Ordered original-selection policies**<br>`duplicates.keeper_selection` | C | Rank by root order, mtime, basename/path alphabetic order, depth, basename length, path/name regex and inner/outer hardlink counts. Criteria chain provides deterministic tie-breaks; default is pOma. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Ordered action fallbacks**<br>`duplicates.link_fallback_chain` | C | Configure comma-separated handlers; smart link tries clone, reflink, hardlink then symlink. Default script handler is permanent remove, not trash. | [R41-S5](<#r41-s5>) |
| **Incremental mtime and tolerance filters**<br>`duplicates.modified_time_bounds` | C | Scan files newer than a timestamp or updated stamp file, retaining size siblings as comparison candidates. Separate mtime-window requires content-equal files to lie within a time window, which can transitively chain groups. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Name and relative-path match constraints**<br>`duplicates.name_constraints` | C | Require same/different basename, extension, extensionless name, parent directory or relative path in addition to content matching; optional case-insensitivity is ASCII-only, not fuzzy-image/name matching. | [R41-S5](<#r41-s5>) |
| **Explicit byte-range comparison**<br>`duplicates.partial_content` | C | Clamp start/end by byte offset, percentage or factor to compare part of each file, e.g. excluding a fixed header. Results are partial-content matches, not exact whole-file duplicates. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Tagged original roots and protected copies**<br>`duplicates.reference_folders` | C | Paths after // are preferred, but preference alone does not protect every tagged copy. --keep-all-tagged protects all, and --must-match-tagged limits candidates to groups represented in those roots. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Reflink/extent deduplication**<br>`duplicates.reflinks` | C | Supports reflink copy or kernel-verified FIDEDUPERANGE clone on capable filesystems. Standalone --dedupe checks equality, shares extents and preserves destination metadata; optional readonly mode targets Btrfs snapshots with root. | [R41-S3](<#r41-s3>), [R41-S5](<#r41-s5>) |
| **Merge and replay prior scans**<br>`duplicates.replay_reports` | C | Replay saved JSON to change ranking/filter/output or merge previous runs without rehashing. It does not discover new paths and ignores entries whose mtime changed; hashing/traversal options no longer apply. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Multiple report and action formats**<br>`duplicates.report_export` | C | Emit JSON including optional linewise records, CSV, shell/Python scripts, fdupes-compatible blocks, unique paths, timestamps and summaries; multiple outputs can coexist. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Size-bounded duplicate scan**<br>`duplicates.size_bounds` | C | Configure inclusive min/max sizes with decimal/binary units; empty files are separate lint by default. 2.11 adds a directory st_size lower-bound flag useful for Ceph rbytes. | [R41-S5](<#r41-s5>), [R41-S6](<#r41-s6>) |
| **Symbolic-link action plans**<br>`duplicates.symlinks` | C | Script handlers can replace duplicates with links to the selected original. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Traversal boundaries and link handling**<br>`duplicates.traversal_controls` | C | Limit depth, mount crossing, hidden files and permission eligibility; follow symlinks, ignore them or compare their target strings. Loop detection is documented when following links. | [R41-S5](<#r41-s5>) |
| **Unique-file inventory and complete hashes**<br>`duplicates.unique_inventory` | C | Unique-path formatter emits nonduplicate paths; --hash-unmatched completes hashes for same-size nonduplicates, while --hash-uniques hashes every traversed file, including unique sizes. | [R41-S5](<#r41-s5>), [R41-S6](<#r41-s6>) |
| **Noninteractive filesystem CLI**<br>`integration.cli` | C | Scan file/directory arguments or stdin; normal execution produces reports/scripts rather than interactively deleting files. | [R41-S1](<#r41-s1>), [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Custom duplicate handlers**<br>`integration.custom_action_commands` | O | Shell handlers receive duplicate and original paths; generated Python scripts can be customized for specialized actions. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Scriptable file/tree equality check**<br>`integration.file_equality` | C | --equal returns status indicating whether multiple files or directory contents match and accepts paranoid mode; directory layout is not automatically part of equality. | [R41-S5](<#r41-s5>) |
| **Standalone parallel hash utility**<br>`integration.hash_utility` | C | --hash operates like a multithreaded checksum tool over paths or stdin using supported hash algorithms. | [R41-S5](<#r41-s5>) |
| **Analyze files in place**<br>`library.existing_folders` | C | No media import/catalogue copying is required; scans supplied filesystem paths. | [R41-S5](<#r41-s5>) |
| **Multi-root scans**<br>`library.multiple_roots` | C | Scan several file/directory roots in a run and rank their relative importance. | [R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>) |
| **Inspect physical sharing**<br>`maintenance.reflink_diagnostics` | C | --is-reflink distinguishes reflinks, hardlinks, identical paths, different devices, symlinks, unavailable extent information and inline extents through exit statuses. | [R41-S5](<#r41-s5>), [R41-S6](<#r41-s6>) |
| **Rotational-disk extent ordering**<br>`performance.disk_seek_optimization` | C | Optional FIEMAP reads physical file extents to optimize disk access; disabled automatically where unavailable. | [R41-S3](<#r41-s3>), [R41-S5](<#r41-s5>) |
| **Bound hashing/comparison memory**<br>`performance.hash_memory_limit` | C | --limit-mem caps memory for hashing/paranoid comparison, not total process RSS; path/index and other overhead remain. | [R41-S5](<#r41-s5>) |
| **Parallel traversal and hashing**<br>`performance.parallel_scan` | C | Configurable worker count defaults to 16; setting it to one does not make the entire program single-threaded. | [R41-S5](<#r41-s5>) |
| **Script confirmation and GUI recheck**<br>`safety.confirmation` | C | Generated shell script prompts before proceeding unless bypassed; GUI guide says files are rechecked before deletion and presents editable keep/delete marks. | [R41-S2](<#r41-s2>), [R41-S4](<#r41-s4>) |
| **External trash integration**<br>`safety.os_trash` | P | Tutorial shows a custom handler invoking separately installed trash-cli; OS trash is not the normal built-in remove handler. | [R41-S2](<#r41-s2>), [R41-S3](<#r41-s3>) |
| **GUI structured result filters**<br>`search.duplicate_results` | O | Filter path text plus size ranges, mtime and twin count; generate scripts for all results or only visible results. | [R41-S4](<#r41-s4>) |

## Limitations and evidence gaps

- **explicit:** Translation guide calls internationalization rudimentary; Japanese catalogue header says its AI-assisted translation has not been reviewed by the submitter. Localization coverage/linguistic quality was not runtime-tested. ([R41-S7](<#r41-s7>), [R41-S8](<#r41-s8>))
- **explicit:** Normal scan is non-destructive, but generated scripts default to permanent removal and standalone --dedupe changes storage extents. Review plus independent backup is recommended; scripts/replay are not an undo journal. ([R41-S2](<#r41-s2>), [R41-S3](<#r41-s3>), [R41-S5](<#r41-s5>))
- **explicit:** Do not change scanned trees while directory merging or its removal scripts run. Tree mode consumes extra memory, defers output, ignores layout by default and cannot combine with sh:clone; sh:link is suggested instead. ([R41-S2](<#r41-s2>), [R41-S5](<#r41-s5>))
- **explicit:** mtime-based xattr caches can become unsafe if contents change without timestamp changes. Clamped ranges intentionally identify only partial duplicates. Weak hash choices increase collision risk. ([R41-S5](<#r41-s5>))
- **explicit:** Reflinks require supported filesystems/kernel features; hardlinks cannot span filesystems. 2.11 generally skips files under 4 KiB for cloning because they may use inline extents. ([R41-S5](<#r41-s5>), [R41-S6](<#r41-s6>))
- **coverage-gap:** No inspected evidence establishes perceptual photo/video similarity, photo thumbnails, face recognition, media playback, EXIF catalogue editing, a recoverable operation journal or crash-safe transactional cleanup. ([R41-S1](<#r41-s1>), [R41-S2](<#r41-s2>), [R41-S4](<#r41-s4>), [R41-S5](<#r41-s5>))
- **Coverage gap:** No runtime filesystem/codec tests; performance figures in cautions were not adopted as our benchmarks.
- **Coverage gap:** Historical tutorial defaults may differ from the current manpage/release; profile follows the latter for exact options.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R41-S1

[rmlint README](<https://github.com/sahib/rmlint/blob/fd20430ef830eab25b5726df8498a04d9a4b804f/README.rst>)
- Kind/ref: readme; fd20430ef830eab25b5726df8498a04d9a4b804f
- Sections inspected: Complete README
- Establishes: Lint types, local CLI scope, platforms and documentation.

### R41-S2

[Gentle guide](<https://github.com/sahib/rmlint/blob/fd20430ef830eab25b5726df8498a04d9a4b804f/docs/tutorial.rst>)
- Kind/ref: manual; fd20430ef830eab25b5726df8498a04d9a4b804f
- Sections inspected: Complete tutorial
- Establishes: Filtering, outputs, keeper policies, script handling, tree semantics, replay and caching.

### R41-S3

[Cautions and robust duplicate handling](<https://github.com/sahib/rmlint/blob/fd20430ef830eab25b5726df8498a04d9a4b804f/docs/cautions.rst>)
- Kind/ref: manual; fd20430ef830eab25b5726df8498a04d9a4b804f
- Sections inspected: Complete cautions document
- Establishes: Backups, false positives, path aliases, hash collisions, links, seek/memory tradeoffs.

### R41-S4

[Shredder GUI guide](<https://github.com/sahib/rmlint/blob/fd20430ef830eab25b5726df8498a04d9a4b804f/docs/gui.rst>)
- Kind/ref: manual; fd20430ef830eab25b5726df8498a04d9a4b804f
- Sections inspected: Complete GUI guide
- Establishes: Location selection, live tree, distribution charts, filters, editable scripts and dry run.

### R41-S5

[rmlint command reference](<https://github.com/sahib/rmlint/blob/fd20430ef830eab25b5726df8498a04d9a4b804f/docs/rmlint.1.rst>)
- Kind/ref: manual; fd20430ef830eab25b5726df8498a04d9a4b804f
- Sections inspected: Synopsis/description; all options, formatters and standalone commands through --is-reflink
- Establishes: Exact matching/filter/cache semantics, action handlers, memory/thread controls and special modes.

### R41-S6

[2.11.0 Evolving Echidna](<https://github.com/sahib/rmlint/releases/tag/v2.11.0>)
- Kind/ref: release; v2.11.0
- Sections inspected: Complete release notes
- Establishes: New hash variants/full-hash modes, FreeBSD cache, replay/tree fixes and current dependency/CLI changes.

### R41-S7

[Runtime translation guide](<https://github.com/sahib/rmlint/blob/fd20430ef830eab25b5726df8498a04d9a4b804f/docs/translators.rst>)
- Kind/ref: manual; fd20430ef830eab25b5726df8498a04d9a4b804f
- Sections inspected: Complete page
- Establishes: Gettext message catalogues, locale selection with LANG and translation compilation.

### R41-S8

[Japanese runtime messages](<https://github.com/sahib/rmlint/blob/fd20430ef830eab25b5726df8498a04d9a4b804f/po/ja.po>)
- Kind/ref: code; fd20430ef830eab25b5726df8498a04d9a4b804f
- Sections inspected: Catalogue header and initial directory/CLI/help/option/error translation entries
- Establishes: Actual localized terminal interface messages; header explicitly identifies unreviewed AI-assisted translation.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
