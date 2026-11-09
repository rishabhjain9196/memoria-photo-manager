# R32 — adrianlopezroche/fdupes

[Repository](<https://github.com/adrianlopezroche/fdupes>) · 3,035 stars at the frozen snapshot · cleanup · Not archived

**Purpose:** Filesystem duplicate-file CLI with exact-content verification, optional persistent signature caching, and an interactive terminal deletion workflow; not a photo catalogue or perceptual-image matcher.

**Deployment:** Command-line source distribution for Unix-like systems; ncurses screen interface or plain terminal interface

**Storage:** Operates on files in supplied directories without importing them. Optional signature database accelerates subsequent comparisons; deletion logs record choices, not recoverable file contents.

**Privacy/network behavior:** The inspected workflow compares local filesystem bytes and signatures. No upload service is required by that workflow; no encryption guarantee is documented.

**License metadata:** NOASSERTION. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v2.4.0 (2025-03-30T18:24:44Z)
**Repository pushed at:** 2026-04-14T15:53:29Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [a7c1da4c561a](<https://github.com/adrianlopezroche/fdupes/commit/a7c1da4c561a9f37c7f27bf2350404d209c86014>).
**Product lineage:** adrianlopezroche/fdupes.

## Maturity and availability caveats

- Manifest release is v2.4.0, published 2025-03-30; inspected pinned master a7c1da4c561a9f37c7f27bf2350404d209c86014 includes that changelog and may contain subsequent changes.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Duplicate summary and quick estimate**<br>`analytics.duplicate_summary` | C | --summarize reports duplicate information; --quicksummary skips the slower byte-verification phase and must not be treated as fully verified equality. | [R32-S2](<#r32-s2>), [R32-S4](<#r32-s4>) |
| **Keyboard-driven terminal review**<br>`browse.keyboard` | C | Screen mode supports paging, file/group navigation, selected-group jumps, direct goto, keep/delete hotkeys and command help; --plain or unsupported screen builds use line prompts. | [R32-S2](<#r32-s2>), [R32-S3](<#r32-s3>) |
| **Noninteractive and immediate deletion**<br>`duplicates.automatic_deletion` | C | --delete --noprompt retains the first ordered member and removes others. --immediate deletes as matches arrive without collecting groups and implies no prompt. | [R32-S2](<#r32-s2>) |
| **Verify candidate equality byte by byte**<br>`duplicates.byte_compare` | C | Ordinary duplicate detection confirms hashes using a byte-by-byte comparison. Quick summary explicitly bypasses this stage. | [R32-S2](<#r32-s2>) |
| **Defer verification until deletion**<br>`duplicates.deferred_verification` | C | --deferconfirmation postpones byte-level equality checks in interactive mode until immediately before deletion. | [R32-S2](<#r32-s2>) |
| **Size and MD5 matching**<br>`duplicates.exact_hash` | C | Candidate files are compared by size and MD5 signatures before normal final byte comparison; this is byte-content matching, not perceptual similarity. | [R32-S2](<#r32-s2>) |
| **Exclude hidden and empty files**<br>`duplicates.exclude_paths` | C | --nohidden excludes hidden files and --noempty excludes zero-length files; arbitrary scan-time path glob exclusions are not established by this manual. | [R32-S2](<#r32-s2>) |
| **Choose whether existing hard links count**<br>`duplicates.existing_hardlink_policy` | C | Multiple names pointing to the same disk area normally do not count as duplicates; --hardlinks includes them. This option does not create hard links. | [R32-S2](<#r32-s2>) |
| **Optional symlink traversal**<br>`duplicates.follow_symlinks` | C | --symlinks follows symlinked directories; manual warns that keeping a link while deleting its target can lose the usable file. | [R32-S2](<#r32-s2>) |
| **Persistent signature database**<br>`duplicates.hash_cache` | O | --cache reuses signatures between comparisons; manual explicitly says availability depends on the system/build. | [R32-S2](<#r32-s2>), [R32-S4](<#r32-s4>) |
| **Keep an entire group**<br>`duplicates.keep_all` | C | The interactive all command tags every member of the current group for keeping. | [R32-S3](<#r32-s3>) |
| **Interactive keeper selection**<br>`duplicates.keeper_selection` | C | Keep/delete tags can be set for individual files, lists of indices, or selected subsets; prune can process reviewed subsets incrementally. | [R32-S3](<#r32-s3>) |
| **Deterministic output and keeper ordering**<br>`duplicates.order_policy` | C | Order by modification time (default), status-change time or filename, with reversal; changelog documents ctime tie-breaking for mtime. | [R32-S2](<#r32-s2>), [R32-S4](<#r32-s4>) |
| **Path and regex-based review selection**<br>`duplicates.path_selection` | C | Select/deselect by substring, prefix, suffix, exact path or PCRE2 expression; clear or invert selections within affected sets before tagging them. | [R32-S3](<#r32-s3>) |
| **Require matching ownership and permissions**<br>`duplicates.permission_match` | C | --permissions prevents files with different owner, group or permission bits from being considered duplicates. | [R32-S2](<#r32-s2>) |
| **All-copy deletion refused in screen mode**<br>`duplicates.remove_all` | N | Interactive prune refuses groups with every file tagged for deletion; at least one member must be tagged for keeping. | [R32-S3](<#r32-s3>) |
| **Text duplicate-group reports**<br>`duplicates.report_export` | C | Default output separates groups by blank lines; --sameline places a group on one line and escapes spaces/backslashes. Options omit the first member and include size or modification time. | [R32-S1](<#r32-s1>), [R32-S2](<#r32-s2>) |
| **Control recursion per directory argument**<br>`duplicates.selective_recursion` | C | --recurse traverses all supplied roots; --recurse: traverses only roots positioned after that option, permitting mixed shallow/deep scans. | [R32-S2](<#r32-s2>) |
| **Minimum and maximum file sizes**<br>`duplicates.size_bounds` | C | --minsize and --maxsize restrict candidates inclusively using byte counts. | [R32-S2](<#r32-s2>) |
| **Command-line duplicate workflow**<br>`integration.cli` | C | Accepts multiple directory arguments and reports duplicate groups; deletion is a separately requested mode. | [R32-S1](<#r32-s1>), [R32-S2](<#r32-s2>) |
| **Scan files in place**<br>`library.existing_folders` | C | Searches supplied filesystem paths directly, with no managed import or image-format requirement in the matching pipeline. | [R32-S2](<#r32-s2>) |
| **Manage cached signatures**<br>`maintenance.signature_cache_controls` | O | Cache supports readonly, orphan pruning, clearing and vacuuming. Maintenance can run without directory arguments and still takes effect with readonly; operation order is clear, prune, update, vacuum. | [R32-S2](<#r32-s2>) |
| **Review tags before pruning**<br>`safety.confirmation` | C | Interactive mode separates tagging from deletion via DELETE/prune, while plain line prompts remain available; --noprompt and --immediate deliberately bypass review. | [R32-S2](<#r32-s2>), [R32-S3](<#r32-s3>) |
| **Log deletion choices**<br>`safety.deletion_choice_log` | C | --log writes file-deletion choices to a chosen logfile; documentation does not describe rollback or saved file contents. | [R32-S2](<#r32-s2>) |
| **Recheck changed files before removal**<br>`safety.changed_file_guards` | C | Version 2.2.0 documents checking whether files marked duplicate changed during execution before deleting them; this is not a permanent integrity journal. | [R32-S4](<#r32-s4>) |

## Limitations and evidence gaps

- **explicit:** Deleting while traversing symlinks can retain a link but remove its target; specifying a directory repeatedly can make a file appear as its own duplicate. ([R32-S1](<#r32-s1>), [R32-S2](<#r32-s2>))
- **explicit:** Quick summary skips byte-level confirmation. Cache and screen-mode availability vary by build/system. ([R32-S2](<#r32-s2>))
- **coverage-gap:** Inspected documents do not establish trash/undo, perceptual matching, image previews, metadata editing, hard-link replacement, or scan-time arbitrary path exclusion; --hardlinks only changes treatment of existing hard links. ([R32-S2](<#r32-s2>), [R32-S3](<#r32-s3>))
- **Coverage gap:** Photo-specific capabilities are not documented; this profile intentionally inventories the duplicate CLI rather than inferring a media manager.
- **Coverage gap:** No runtime or platform compatibility tests were performed.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R32-S1

[README](<https://github.com/adrianlopezroche/fdupes/blob/a7c1da4c561a9f37c7f27bf2350404d209c86014/README.md>)
- Kind/ref: readme; a7c1da4c561a9f37c7f27bf2350404d209c86014
- Sections inspected: Introduction; complete Usage and deletion caveats
- Establishes: CLI option overview, output format and dangerous symlink/repeated-directory cases.

### R32-S2

[fdupes command manual](<https://github.com/adrianlopezroche/fdupes/blob/a7c1da4c561a9f37c7f27bf2350404d209c86014/fdupes.1>)
- Kind/ref: manual; a7c1da4c561a9f37c7f27bf2350404d209c86014
- Sections inspected: Description; all Options; Notes; Examples; Caveats
- Establishes: Size/MD5/byte-comparison pipeline, caching controls, recursion, ordering and delete behavior.

### R32-S3

[Interactive mode reference](<https://github.com/adrianlopezroche/fdupes/blob/a7c1da4c561a9f37c7f27bf2350404d209c86014/fdupes-help.7>)
- Kind/ref: manual; a7c1da4c561a9f37c7f27bf2350404d209c86014
- Sections inspected: Complete interactive reference, including selection, tagging, pruning and regex syntax
- Establishes: Keyboard navigation, path/PCRE selection, keep/delete tags and refusal to delete every copy.

### R32-S4

[Version history](<https://github.com/adrianlopezroche/fdupes/blob/a7c1da4c561a9f37c7f27bf2350404d209c86014/CHANGES>)
- Kind/ref: release; a7c1da4c561a9f37c7f27bf2350404d209c86014
- Sections inspected: Complete changelog, especially 2.4.0, 2.3.0 and 2.2.0
- Establishes: Quick summary, persistent cache and pre-deletion file-change checks.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
