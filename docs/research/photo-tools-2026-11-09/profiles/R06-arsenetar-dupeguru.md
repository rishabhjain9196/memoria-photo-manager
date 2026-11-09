# R06 — arsenetar/dupeguru

[Repository](<https://github.com/arsenetar/dupeguru>) · 7,954 stars at the frozen snapshot · cleanup · Not archived

**Purpose:** Local cross-platform duplicate-file reviewer with distinct exact-content, fuzzy-name, music-tag and perceptual-picture scan modes and protected keeper selection.

**Deployment:** Windows installer and portable ZIP; macOS desktop application; Linux desktop packages/source

**Storage:** Scans user-selected existing folders in place. Picture analysis is cached in a local database; preferences, logs and other user state are stored in platform-specific application directories. Move/copy/delete operate on original files rather than an imported photo library.

**Privacy/network behavior:** Documented workflows analyze local files without a hosted media account or mandatory upload. External applications can be invoked explicitly. The inspected material is not a formal network-privacy audit.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 4.3.1 (2022-07-09T00:31:52Z)
**Repository pushed at:** 2026-09-07T16:29:13Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [db097a030150](<https://github.com/arsenetar/dupeguru/commit/db097a030150b3d4ea9f492b85e7e4e4bcb3f789>).
**Product lineage:** arsenetar/dupeguru.

## Maturity and availability caveats

- Frozen master db097a030150b3d4ea9f492b85e7e4e4bcb3f789 is newer than latest manifest release 4.3.1 (2022-07-09).
- README requests help maintaining macOS/Linux packaging and keeping documentation current; manuals contain legacy OS/edition terminology.
- Release 4.3.1 fixes a serious standard-content false-duplicate bug present since 4.2.0 and recommends upgrading affected versions.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Reference-versus-duplicate details**<br>`browse.compare` | C | Details panel compares selected file and reference metadata; numeric Delta Values show relative differences and differing text is highlighted. This evidence establishes metadata comparison, not a thumbnail comparison claim. | [R06-S4](<#r06-s4>) |
| **Keyboard batch marking**<br>`browse.keyboard` | C | Shift/Control/Command selection and Space toggle selected duplicate marks; marked and selected states remain distinct. | [R06-S4](<#r06-s4>) |
| **Linux desktop**<br>`deployment.linux` | C | Debian/RPM binaries, Arch packaging and Ubuntu PPA are documented; binary Python compatibility is release-specific. | [R06-S8](<#r06-s8>) |
| **Selectable translated desktop interface**<br>`deployment.localization` | C | General Interface preferences populate a language selector from supported locales, fall back to English for an unknown preference and require restart after changing language. French translations explicitly cover menus, duplicate-review labels and deletion dialogs; release 4.3.1 also updates Italian translations. | [R06-S9](<#r06-s9>), [R06-S10](<#r06-s10>), [R06-S8](<#r06-s8>) |
| **macOS desktop**<br>`deployment.macos` | C | 4.3.1 notes Intel/M1 compatibility and signing without a paid developer subscription. | [R06-S8](<#r06-s8>) |
| **Portable Windows distribution**<br>`deployment.portable` | C | ZIP distribution is offered alongside the Windows installer. | [R06-S8](<#r06-s8>) |
| **Windows desktop**<br>`deployment.windows` | C | Release supplies installers and portable ZIPs; 4.3.1 packages require Windows 7 or later. | [R06-S1](<#r06-s1>), [R06-S8](<#r06-s8>) |
| **Music-tag duplicate matching**<br>`duplicates.audio` | C | Music mode compares chosen tags such as artist/title as separate fields and displays audio metadata columns. This is not a claim of acoustic fingerprinting. | [R06-S2](<#r06-s2>), [R06-S5](<#r06-s5>) |
| **EXIF timestamp candidate matching**<br>`duplicates.capture_timestamp` | C | A separate scan treats matching DateTimeOriginal tags as duplicate candidates; modified images retaining the timestamp can be false positives. | [R06-S2](<#r06-s2>) |
| **Exact content duplicate scan**<br>`duplicates.exact_hash` | C | Standard Contents groups by file size, drops unique-size files and compares MD5 digests. This is hash-based equality, not documented full byte-for-byte verification. | [R06-S2](<#r06-s2>) |
| **Excluded directory states**<br>`duplicates.exclude_paths` | C | Exclude roots or individual subfolders from scanning with inherited per-folder state. | [R06-S5](<#r06-s5>) |
| **Ordered or reordered filename fields**<br>`duplicates.fielded_names` | C | Dash-separated fields are compared individually; an order-independent mode can match artist/title reversed between files, with each field used once. | [R06-S2](<#r06-s2>) |
| **Dupes-only review mode**<br>`duplicates.flat_results` | C | Hide reference rows to sort all duplicate files independently by columns, combine with relative values, and mark batches such as extension or bitrate differences. | [R06-S4](<#r06-s4>), [R06-S7](<#r06-s7>) |
| **Recursive duplicate folder detection**<br>`duplicates.folders` | C | Folder Contents compares contained file contents recursively and returns the largest matching folders instead of redundantly listing their matching subfolders. | [R06-S2](<#r06-s2>) |
| **Word-based filename similarity**<br>`duplicates.fuzzy_names` | C | Normalize case/punctuation and compare shared words against filter hardness; optional character-weighting and approximate-word matching increase flexibility, time and false positives. | [R06-S2](<#r06-s2>), [R06-S3](<#r06-s3>) |
| **Replace deletions with hard links**<br>`duplicates.hardlinks` | C | Deletion options can link removed paths to reference files; manual documents macOS/Linux support and Windows version/admin-privilege caveats. | [R06-S4](<#r06-s4>) |
| **Cached picture analysis**<br>`duplicates.hash_cache` | C | Time-consuming 15×15 picture-analysis results are cached in a database. The release also refers to a standard-content hashing cache bug fix. | [R06-S2](<#r06-s2>), [R06-S8](<#r06-s8>) |
| **Ignore existing inode aliases**<br>`duplicates.existing_hardlink_policy` | C | macOS/Linux preference excludes duplicate candidates already referring to the same inode. | [R06-S3](<#r06-s3>) |
| **Discard candidates without changing files**<br>`duplicates.keep_all` | C | Remove selected/marked candidates from results or leave them unmarked; removing result rows does not touch their files. | [R06-S4](<#r06-s4>) |
| **Manual and rule-driven keeper selection**<br>`duplicates.keeper_selection` | C | Defaults to a protected reference or largest file; manually promote a duplicate or apply ordered size/folder/filename and other prioritization criteria with tie-breakers. | [R06-S4](<#r06-s4>), [R06-S6](<#r06-s6>) |
| **Protected reference directories**<br>`duplicates.reference_folders` | C | Reference-state folders cannot contribute deletable duplicates. States inherit to subfolders unless overridden, and protected references cannot be demoted. | [R06-S4](<#r06-s4>), [R06-S5](<#r06-s5>) |
| **Persistent ignored match pairs**<br>`duplicates.remember_decisions` | C | Add Selected to Ignore List suppresses that duplicate/reference pair in future scans, not the file globally; the same file may match a different reference. Ignore list can be cleared. | [R06-S4](<#r06-s4>) |
| **Delete every group member**<br>`duplicates.remove_all` | N | Group references cannot be marked, ensuring at least one group member remains; reference-folder members are additionally protected. | [R06-S4](<#r06-s4>), [R06-S7](<#r06-s7>) |
| **XHTML result export**<br>`duplicates.report_export` | C | Exports current result columns into an XHTML report and opens it in the browser. | [R06-S4](<#r06-s4>) |
| **Cross-resolution and rotated picture matches**<br>`duplicates.rotation_dimension_tolerance` | C | Preferences can permit differing dimensions and rotations in the same picture duplicate group and allow mixed file extensions. | [R06-S3](<#r06-s3>) |
| **Perceptual picture matching**<br>`duplicates.similar_images` | C | Picture Contents averages RGB values over a 15×15 grid and compares corresponding cells against a configurable threshold; 100 applies an additional exact-picture constraint, while 99 permits small differences. | [R06-S2](<#r06-s2>) |
| **Replace deletions with symbolic links**<br>`duplicates.symlinks` | C | Alternative link replacement uses symlinks, with the explicit caveat that moving/deleting their reference target breaks them. | [R06-S4](<#r06-s4>) |
| **Custom external comparison commands**<br>`integration.external_tools` | O | Configure a command with duplicate and reference path placeholders; results can also open in the default application or reveal their containing directory. | [R06-S3](<#r06-s3>), [R06-S4](<#r06-s4>) |
| **Scan originals in place**<br>`library.existing_folders` | C | Add existing folders to the scan list; no managed photo import is required. | [R06-S5](<#r06-s5>) |
| **Move or copy marked candidates**<br>`library.move_copy` | C | Destination layout can be flat or recreate relative/absolute source paths; source folders can be removed after becoming empty. | [R06-S3](<#r06-s3>), [R06-S4](<#r06-s4>) |
| **Multi-folder scans**<br>`library.multiple_roots` | C | Add multiple recent/new folders or drag directories into the selection list before a single scan. | [R06-S5](<#r06-s5>) |
| **Rename selected file**<br>`library.rename` | C | Action menu prompts for a new filename; a batch naming-template system is not established by this action. | [R06-S4](<#r06-s4>) |
| **Multi-core picture comparison**<br>`performance.parallel_scan` | C | Picture matching is documented as utilizing multiple cores, while still requiring quadratic pair comparisons; no benchmark was performed. | [R06-S2](<#r06-s2>) |
| **Review and deletion options**<br>`safety.confirmation` | C | Scanning first produces reviewable groups; deletion presents options. Groups discard ambiguous non-transitive matches rather than overlapping candidates that might delete distinct files. | [R06-S4](<#r06-s4>), [R06-S7](<#r06-s7>) |
| **Collision-safe copy/move names**<br>`safety.no_overwrite` | C | Copy/move naming conflicts prepend a number instead of silently overwriting the destination filename. | [R06-S3](<#r06-s3>) |
| **Trash by default**<br>`safety.os_trash` | C | Send Marked to Trash uses the OS trash; a separate direct-delete option bypasses it for cases such as incompatible NAS deletion. | [R06-S4](<#r06-s4>), [R06-S7](<#r06-s7>) |
| **Post-scan wildcard or regex filtering**<br>`search.filename_path` | C | Case-insensitive filter searches complete paths using simple text plus wildcard or regular expressions. Nonmatching members remain visible but cannot be marked through the filtered view. | [R06-S3](<#r06-s3>), [R06-S4](<#r06-s4>) |

## Limitations and evidence gaps

- **explicit:** Picture comparisons are quadratic and CPU-intensive. Similar-word matching increases false positives; EXIF timestamp identity alone can match edited variants. These candidate modes need review. ([R06-S2](<#r06-s2>), [R06-S7](<#r06-s7>))
- **explicit:** MD5 content matching is not cryptographic proof against deliberately forged files, and no byte-by-byte verification is established in the inspected scan manual. ([R06-S2](<#r06-s2>))
- **explicit:** 4.2.0–4.3.0 standard-content scans could falsely identify nonduplicates when hashing cache errors occurred; 4.3.1 adds error handling and guards for nonempty files without digests. ([R06-S8](<#r06-s8>))
- **explicit:** All-copy removal is intentionally disallowed. Link and trash behavior depends on platform and filesystem; direct delete bypasses recoverable OS trash. ([R06-S4](<#r06-s4>), [R06-S7](<#r06-s7>))
- **coverage-gap:** The inspected manuals do not establish photo-library albums, face recognition, maps, video similarity, an operation journal, encrypted storage or a general media playback engine. ([R06-S2](<#r06-s2>), [R06-S4](<#r06-s4>), [R06-S5](<#r06-s5>))
- **Coverage gap:** No claim of current GUI visual-thumbnail comparison from the inspected metadata-details manual.
- **Coverage gap:** Some platform details in pinned help are historical; release-specific packaging is distinguished.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R06-S1

[dupeGuru README](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/README.md>)
- Kind/ref: readme; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Complete README
- Establishes: Platform scope, GUI architecture and maintenance/documentation needs.

### R06-S2

[Scanning process manual](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/help/en/scan.rst>)
- Kind/ref: manual; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Complete manual: words, fields, contents, folders, picture blocks and EXIF
- Establishes: Precise matching algorithms, cache behavior and false-positive/performance caveats.

### R06-S3

[Preferences manual](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/help/en/preferences.rst>)
- Kind/ref: manual; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Complete manual
- Establishes: Scan tolerances, rotation/dimension matching, filesystem behavior and custom commands.

### R06-S4

[Results and deletion manual](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/help/en/results.rst>)
- Kind/ref: manual; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Complete manual
- Establishes: Keeper protection, review, filters, exports, ignore lists, links and destructive actions.

### R06-S5

[Folder selection manual](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/help/en/folders.rst>)
- Kind/ref: manual; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Complete manual
- Establishes: Standard/music/picture modes, multiple folder selection and inherited directory states.

### R06-S6

[Re-prioritization manual](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/help/en/reprioritize.rst>)
- Kind/ref: manual; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Complete manual
- Establishes: Ordered keeper criteria and tie-breaking.

### R06-S7

[FAQ](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/help/en/faq.rst>)
- Kind/ref: manual; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Complete FAQ
- Establishes: Non-transitive match handling, post-scan workflows, performance and local user files.

### R06-S8

[Release 4.3.1](<https://github.com/arsenetar/dupeguru/releases/tag/4.3.1>)
- Kind/ref: release; 4.3.1
- Sections inspected: Complete release notes
- Establishes: False-duplicate bug fix, release signatures and platform packaging constraints.

### R06-S9

[Interface language preference](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/qt/preferences_dialog.py>)
- Kind/ref: code; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: supportedLanguages initialization; language selector construction; language preference load/save and restart notice
- Establishes: Selectable UI languages, English fallback and restart requirement.

### R06-S10

[French Qt UI translations](<https://github.com/arsenetar/dupeguru/blob/db097a030150b3d4ea9f492b85e7e4e4bcb3f789/locale/fr/LC_MESSAGES/ui.po>)
- Kind/ref: code; db097a030150b3d4ea9f492b85e7e4e4bcb3f789
- Sections inspected: Catalogue header and complete Quit/Options/Ignore List/cache/deletion/link/details translation entries at file start
- Establishes: Actual translated desktop actions/dialogs rather than only help documentation.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
