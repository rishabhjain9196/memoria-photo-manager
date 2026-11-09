# R07 — TagStudioDev/TagStudio

[Repository](<https://github.com/TagStudioDev/TagStudio>) · 7,281 stars at the frozen snapshot · library-desktop · Not archived

**Purpose:** Cross-platform local file catalogue built around relational, inheritable tags and typed metadata fields, layered over an existing directory without mandatory file copies or per-file sidecars.

**Deployment:** Windows, macOS Intel/Apple Silicon and Linux desktop builds; Portable Windows and Linux distributions; official releases on GitHub; Optional FFmpeg for video/audio and ripgrep for faster scanning

**Storage:** One content-root directory per library, including subfolders. A .TagStudio directory holds ts_library.sqlite, thumbnail cache, ignore rules and database backups. Entries store relative paths, so the complete root is portable. Multiple separately opened libraries have independent tags; concurrent users on one library are unsupported.

**Privacy/network behavior:** Local catalogue does not alter source files except explicit operations such as Move to Trash; no cloud upload required. Network/NAS or cloud-mounted folders can be used via the OS. Native cloud and nonlocal LLM integration are explicitly outside the project's scope; this is not encrypted-vault storage.

**License metadata:** GPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v9.6.4 (2026-10-02T19:30:15Z)
**Repository pushed at:** 2026-11-07T20:41:22Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [246f162a70b6](<https://github.com/TagStudioDev/TagStudio/commit/246f162a70b67203ca4d8a425b0ba4c61cf25468>).
**Product lineage:** TagStudioDev/TagStudio.

## Maturity and availability caveats

- Manifest latest release Alpha v9.6.4 (2026-10-02); inspected main 246f162a70b67203ca4d8a425b0ba4c61cf25468.
- README retains v9.5-era statements contradicted by newer manuals/roadmap: custom field templates/names and substring smartcase path search are documented now.
- Roadmap marks Fix Duplicate Files as a regression despite the older macros page describing a dupeGuru import tool; that capability is not counted present.
- v10 denotes intended feature completeness; 9.x does not mean a mature final release.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Native nonlocal LLM integration**<br>`ai.remote_inference` | N | README explicitly rules out built-in ChatGPT/Claude/Gemini/cloud-LLM connections; future external API possibilities do not change present status. | [R07-S1](<#r07-s1>) |
| **Nonexclusive nested entry groups**<br>`albums.nested` | R | Entry groups with nesting, per-group ordering, numbering and custom covers are planned; tags do not establish this album feature. | [R07-S10](<#r07-s10>) |
| **Library information panel**<br>`analytics.library_statistics` | C | Panel shows library statistics and consolidated cleanup/backup access; no exact scale benchmark is claimed. | [R07-S2](<#r07-s2>), [R07-S10](<#r07-s10>) |
| **Audio playback and waveform preview**<br>`browse.audio_playback` | O | FFmpeg enables common audio formats. Thumbnails use cover art or waveform; waveform caching is explicitly not implemented. | [R07-S9](<#r07-s9>), [R07-S10](<#r07-s10>) |
| **PDF and office-document previews**<br>`browse.document_preview` | C | PDF previews render the first page. Apple iWork and OpenDocument documents use embedded thumbnails; PowerPoint support depends on an embedded thumbnail being available. This is preview support, not full document editing or established multipage navigation. | [R07-S9](<#r07-s9>) |
| **Thumbnail grid and inspector**<br>`browse.grid` | C | Grid entries show detailed preview, file statistics, tags and fields in an inspector; roadmap marks infinite scrolling and configurable page size implemented. | [R07-S7](<#r07-s7>), [R07-S10](<#r07-s10>) |
| **Hidden-tag archive filtering**<br>`browse.hidden_items` | C | Is Hidden excludes tagged entries from default searches; Archived carries it by default and a checkbox includes hidden entries. | [R07-S3](<#r07-s3>), [R07-S10](<#r07-s10>) |
| **Tagging and library shortcuts**<br>`browse.keyboard` | C | Shortcuts cover opening/refreshing libraries, creating/managing tags, adding to selected entries and saving backups, with macOS equivalents. | [R07-S1](<#r07-s1>), [R07-S2](<#r07-s2>) |
| **Video thumbnails/player**<br>`browse.video_playback` | O | Requires FFmpeg; thumbnails use a viable middle frame. Player supports play/pause, loop, autoplay, volume/mute and timeline scrubber, not yet fullscreen per roadmap. | [R07-S9](<#r07-s9>), [R07-S10](<#r07-s10>) |
| **Native Linux desktop builds**<br>`deployment.linux` | C | README explicitly lists executable Linux desktop releases; it warns that package-manager distributions are unofficial rather than claiming official support for every package source. | [R07-S1](<#r07-s1>) |
| **Translated desktop interface**<br>`deployment.localization` | C | Roadmap marks interface translations and application language settings implemented; v9.6.4 specifically updates Dutch, French and Hungarian translations. This does not imply the separately planned multilingual tag-name feature. | [R07-S10](<#r07-s10>), [R07-S11](<#r07-s11>) |
| **Native Intel and Apple Silicon macOS builds**<br>`deployment.macos` | C | README explicitly lists macOS desktop builds for both Intel and Apple Silicon, distributed through official GitHub Releases. | [R07-S1](<#r07-s1>) |
| **Portable Windows and Linux releases**<br>`deployment.portable` | C | README explicitly offers self-contained portable Windows and Linux releases intended to be easier to move between locations; macOS portable packaging is not claimed. | [R07-S1](<#r07-s1>) |
| **Native Windows desktop builds**<br>`deployment.windows` | C | README explicitly provides official executable Windows builds from GitHub Releases; these are desktop applications, not a Docker-host or browser-only compatibility claim. | [R07-S1](<#r07-s1>) |
| **Legacy dupeGuru metadata mirroring**<br>`duplicates.external_result_mirroring` | ? | Tools page describes loading dupeGuru result files and mirroring entry fields before deleting elsewhere, but current roadmap marks Fix Duplicate Files a regression still to restore; not a current built-in scanner. | [R07-S8](<#r07-s8>), [R07-S10](<#r07-s10>) |
| **Experimental whole-library collage**<br>`editing.collage` | C | Tools manual describes a working early preview generating all-library collage output under .TagStudio/collages with no customization yet. | [R07-S8](<#r07-s8>) |
| **Animated image playback**<br>`formats.animated` | C | GIF, animated WebP and APNG play in Preview Panel; grid uses cached thumbnails. | [R07-S9](<#r07-s9>) |
| **Archive/eBook covers**<br>`formats.archive_ebook_previews` | C | ZIP/RAR/7z/Tar variants show first archive image; EPUB shows cover and comic-book archives use cover/first page. | [R07-S9](<#r07-s9>) |
| **AVIF previews**<br>`formats.avif` | C | AVIF appears in image support and in FFmpeg video-format listing; no universal animation support is inferred. | [R07-S9](<#r07-s9>) |
| **Font and plaintext previews**<br>`formats.font_text_previews` | C | Font formats show Aa/alphanumeric samples; plaintext previews render only first 256 bytes. Full text/syntax highlighting remain planned. | [R07-S9](<#r07-s9>) |
| **HEIF/HEIC previews**<br>`formats.heic` | C | HEIF and HEIC are explicitly listed in image preview matrix. | [R07-S9](<#r07-s9>) |
| **Static JPEG XL preview**<br>`formats.jpegxl` | C | JXL is listed as supported image preview, but its animation column is explicitly unsupported. | [R07-S9](<#r07-s9>) |
| **Creative-project thumbnail previews**<br>`formats.project_previews` | C | Photoshop PSD previews render a flattened image; Blender, Krita, Clip Studio Paint and other listed creative-project formats use embedded thumbnails, with availability caveats for formats such as Blender and Krita. Blender thumbnails do not establish interactive 3D model rendering. | [R07-S9](<#r07-s9>) |
| **Camera RAW previews**<br>`formats.raw` | C | Matrix lists Canon CRW/CR2/CR3, DNG, Fuji RAF, Nikon NEF/NRW, Olympus ORF, Panasonic RAW/RW2 and Sony ARW. | [R07-S9](<#r07-s9>) |
| **Static vector preview**<br>`formats.svg` | C | SVG thumbnail/preview is supported; animation is explicitly not supported. | [R07-S9](<#r07-s9>) |
| **Separated core library/CLI**<br>`integration.cli` | R | UI-agnostic core and CLI with intended MIT licensing are roadmap work, not a released public API. | [R07-S10](<#r07-s10>) |
| **Event-driven automation macros**<br>`integration.event_macros` | R | Versioned TOML macros with add/refresh triggers and tag/field actions are planned; implemented Folders to Tags is a narrower tool. | [R07-S8](<#r07-s8>), [R07-S10](<#r07-s10>) |
| **Native cloud-service integration**<br>`library.cloud_import` | N | README explicitly rejects native cloud integration; OS-mounted virtual drives are suggested instead. | [R07-S1](<#r07-s1>) |
| **Catalogue files in place**<br>`library.existing_folders` | C | Creates a layer over a chosen directory and its descendants without moving, copying or changing media files. | [R07-S1](<#r07-s1>), [R07-S2](<#r07-s2>) |
| **Gitignore-like scan exclusions**<br>`library.exclude_folders` | C | .ts_ignore supports directory-relative patterns, *, ?, **, ranges, comments and negation. Applies when adding new files, not retroactively; cannot re-include children of an excluded parent. | [R07-S6](<#r07-s6>) |
| **Refresh new/modified files**<br>`library.incremental_scan` | C | Manual Refresh Directories and configurable scan-on-open update the catalogue. README mentions a 10,000-file threshold, while newer manual describes a user toggle; exact threshold behavior is not independently resolved. | [R07-S1](<#r07-s1>), [R07-S2](<#r07-s2>) |
| **Independent selectable libraries**<br>`library.multiple_libraries` | C | Open/Create selects a library root; each library has its own tags, fields, colors and database, not a global tag universe. | [R07-S2](<#r07-s2>) |
| **Multiple roots per library**<br>`library.multiple_roots` | R | Roadmap and library manual explicitly plan multiple content roots and a separately stored data directory; present root must host .TagStudio. | [R07-S2](<#r07-s2>), [R07-S10](<#r07-s10>) |
| **Portable library root**<br>`library.relative_path_portability` | C | Relative entry paths allow moving the whole content/data folder together, including external drives or differently mounted NAS paths. | [R07-S2](<#r07-s2>) |
| **Repair moved/unlinked entries**<br>`library.relink_entries` | C | Tool finds missing entries, searches/relinks or removes only catalogue records after confirmation. README says matching uses filenames, ignores ambiguous matches and cannot relink renamed files. | [R07-S1](<#r07-s1>), [R07-S7](<#r07-s7>), [R07-S8](<#r07-s8>) |
| **Library health/cleanup tools**<br>`maintenance.selective_reset` | C | Library Information provides unlinked repair, remove ignored entries, delete old backups and remove legacy JSON without deleting source media. | [R07-S2](<#r07-s2>), [R07-S7](<#r07-s7>), [R07-S10](<#r07-s10>) |
| **Tag multiple selected entries**<br>`metadata.batch_edit` | C | Add Tags to Selected supports fast keyboard searching/creation and repeated Enter-to-add; unassigned tags are removable in inspector. | [R07-S1](<#r07-s1>) |
| **Text and datetime annotations**<br>`metadata.comments` | C | Single-line/multiline text stores titles, notes or comments; datetime values follow application date format. Values are in the catalogue, not written to media. | [R07-S4](<#r07-s4>), [R07-S7](<#r07-s7>) |
| **Composition relationships and overrides**<br>`metadata.component_tags` | R | HAS/component relationships and tag overrides are planned, distinct from implemented parent inheritance. | [R07-S3](<#r07-s3>), [R07-S10](<#r07-s10>) |
| **Custom typed field templates**<br>`metadata.custom_fields` | C | Create/edit/delete custom templates for text or datetime fields. Template information is copied into an entry; editing the entry does not mutate the template. Newer manual/roadmap supersede README's fixed-name claim. | [R07-S4](<#r07-s4>), [R07-S10](<#r07-s10>) |
| **Customizable Favorite tag**<br>`metadata.favorites` | C | Built-in Favorite and Archived tags inherit Meta Tags; their category/parent behavior can be customized. | [R07-S3](<#r07-s3>) |
| **Convert folder hierarchy to tag inheritance**<br>`metadata.folders_to_tags` | C | Macro previews a hierarchy for confirmation, creates a tag per folder, applies to entries and assigns parent-folder tags as parents; v9.6.4 fixes this workflow. | [R07-S8](<#r07-s8>), [R07-S11](<#r07-s11>) |
| **Multi-parent tag inheritance**<br>`metadata.hierarchical_tags` | C | Tags inherit from multiple parents transitively; searching a parent finds entries assigned descendants without redundantly adding every ancestor to each file. | [R07-S3](<#r07-s3>), [R07-S5](<#r07-s5>) |
| **Aliases and contextual names**<br>`metadata.tag_aliases_disambiguation` | C | Aliases/shorthand are searchable; marked parent tags add their name or shorthand in display parentheses to distinguish same-named tags without changing base identity. | [R07-S3](<#r07-s3>) |
| **Tag-driven inspector categories**<br>`metadata.tag_categories` | C | Category tags group inheriting tags in inspector, including multiple categories. Per-tag exclusions control category display; v9.6.4 release confirms the feature. | [R07-S3](<#r07-s3>), [R07-S11](<#r07-s11>) |
| **Custom tag palettes**<br>`metadata.tag_colors` | C | Built-in and user-defined namespaced palettes set primary/secondary text/border colors on tags; not an independently established media color-label rating system. | [R07-S3](<#r07-s3>) |
| **Rich tag objects**<br>`metadata.tags` | C | Tags have nonunique unrestricted names, shorthand, aliases, colors and relationships rather than just flat text labels. | [R07-S3](<#r07-s3>) |
| **Optional fast directory scanner**<br>`performance.ripgrep_scan` | O | Installed ripgrep replaces wcmatch scanning for speed and Git-style glob parity; docs warn fallback pattern behavior can differ. | [R07-S6](<#r07-s6>) |
| **On-demand cached thumbnails**<br>`performance.thumbnail_cache` | C | Image thumbnails are generated first viewing or after modification and stored in .TagStudio/thumbs; full preview panel does not use them. | [R07-S2](<#r07-s2>), [R07-S9](<#r07-s9>) |
| **Autosave and timestamped database backups**<br>`safety.catalogue_backup` | C | Library autosaves; manual Save Library Backup and automatic migration backups preserve ts_library.sqlite under backups. Original content files are excluded. | [R07-S2](<#r07-s2>) |
| **Explicit move to system trash**<br>`safety.os_trash` | C | README cites Move File(s) to Trash as the exception to otherwise non-modifying cataloguing; no general undo journal is asserted. | [R07-S1](<#r07-s1>) |
| **Boolean and nested queries**<br>`search.boolean` | C | Implicit/explicit AND, OR, NOT and parentheses; quotes or underscore substitution escape multiword names. | [R07-S5](<#r07-s5>) |
| **Extension/media-category filters**<br>`search.file_type` | C | filetype: and mediatype: search extensions or media classes; roadmap marks optional extension-synonym consolidation implemented. | [R07-S1](<#r07-s1>), [R07-S10](<#r07-s10>) |
| **Substring/glob smartcase paths**<br>`search.filename_path` | C | path: searches whole-path substrings by default or optional glob patterns; lowercase is case-insensitive, mixed case is sensitive. No forced case-sensitive all-lowercase query is available. | [R07-S5](<#r07-s5>) |
| **Search custom field contents**<br>`search.metadata` | R | Field search and comparisons of date/duration/size/dimensions are unchecked roadmap tasks and explicitly unavailable in search manual. | [R07-S5](<#r07-s5>), [R07-S10](<#r07-s10>) |
| **OCR search roadmap**<br>`search.ocr` | R | OCR and fuzzy search appear as future low-priority roadmap items, not built-in recognition. | [R07-S10](<#r07-s10>) |
| **Alias-aware inherited tag search**<br>`search.tags` | C | Default search matches tag names, shorthand and aliases including inherited parents; tag: is optional. | [R07-S5](<#r07-s5>) |
| **Find untagged entries**<br>`search.untagged` | C | special:untagged finds entries without tags. special:empty availability conflicts across docs and is not included in this present claim. | [R07-S5](<#r07-s5>) |
| **Sort by catalogue addition date**<br>`sort.entry_added` | C | Results can be ordered by when the file entry was added to the library, explicitly distinct from file creation, modification or photo capture time. | [R07-S10](<#r07-s10>), [R07-S7](<#r07-s7>) |
| **Sort catalogue results by filename**<br>`sort.filename` | C | Roadmap explicitly marks filename result sorting completed in v9.5.2; file creation/modification/capture-date sorting remains unchecked and is not included in this claim. | [R07-S10](<#r07-s10>) |
| **Shuffle result ordering**<br>`sort.random` | C | Random/Shuffle Sort is explicitly checked as implemented in the current search-result sorting roadmap. | [R07-S10](<#r07-s10>) |

## Limitations and evidence gaps

- **explicit:** One library cannot be concurrently accessed by multiple users; multi-root and separately located library data remain planned. ([R07-S2](<#r07-s2>), [R07-S10](<#r07-s10>))
- **explicit:** Backups contain the catalogue SQLite file only, not original media; unlinked entries lose uncached stats and normal thumbnails. ([R07-S2](<#r07-s2>), [R07-S7](<#r07-s7>))
- **explicit:** README's relinker cannot handle renamed files and ignores multiple filename matches; automatic robust relinking remains roadmap work. ([R07-S1](<#r07-s1>), [R07-S10](<#r07-s10>))
- **explicit:** Ignore rules apply to new scans, not existing entries. FFmpeg is required for audio/video; waveform caching, full text preview and 3D rendering are not currently supported. ([R07-S6](<#r07-s6>), [R07-S9](<#r07-s9>))
- **coverage-gap:** Duplicate-tool availability conflicts between older manual and regression roadmap; special:empty is advertised in README but marked unavailable for v9.5.0 in search manual. Neither is asserted currently working. ([R07-S1](<#r07-s1>), [R07-S5](<#r07-s5>), [R07-S8](<#r07-s8>), [R07-S10](<#r07-s10>))
- **coverage-gap:** Face recognition, map browsing, perceptual matching, EXIF/XMP writing and media-content encryption were not established; tags for people/places are not AI recognition/geocoding. ([R07-S1](<#r07-s1>), [R07-S3](<#r07-s3>), [R07-S9](<#r07-s9>), [R07-S10](<#r07-s10>))
- **Coverage gap:** Explicit documentation conflicts retained rather than resolved by assumptions.
- **Coverage gap:** No runtime preview/format tests; roadmap estimates are not release promises.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R07-S1

[TagStudio README](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/README.md>)
- Kind/ref: readme; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete features, usage, installation, goals and FAQ
- Establishes: Core scope, platform support, explicit non-goals and stale relinking/field claims.

### R07-S2

[Libraries](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/libraries.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete library mechanics, migration, refresh, health panel, backup and portability
- Establishes: SQLite storage, autosave, database-only backup, relative paths and multiuser restrictions.

### R07-S3

[Tags](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/tags.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete naming, relationships, appearance, categories, hidden property and examples
- Establishes: Aliases, nonunique names, inheritance, disambiguation, colors and category display.

### R07-S4

[Fields and templates](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/fields.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete template creation/editing and text/datetime types
- Establishes: Custom templates and copy-on-add semantics.

### R07-S5

[Search reference](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/search.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete boolean, tag, field, path, smartcase, glob and special searches
- Establishes: Exact query semantics and field-search/empty-search caveats.

### R07-S6

[Ignoring files/directories](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/ignore.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete syntax and use cases
- Establishes: Scan-time .ts_ignore matching, negation, recursion and optional ripgrep behavior.

### R07-S7

[Entries](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/entries.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete entry storage, inspector, unlinked states and schema explanation
- Establishes: One-to-one files, cached-property limitations and non-destructive entry cleanup.

### R07-S8

[Tools and macros](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/macros.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete unlinked/duplicate/collage/folders-to-tags descriptions
- Establishes: Tools, experimental collage and legacy duplicate-mirroring description.

### R07-S9

[Supported preview matrix](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/preview-support.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete images, RAW, audio/video, documents, archives, eBooks, fonts and text sections
- Establishes: Precise format support and preview/playback/dependency limits.

### R07-S10

[Current versus planned feature checklist](<https://github.com/TagStudioDev/TagStudio/blob/246f162a70b67203ca4d8a425b0ba4c61cf25468/docs/roadmap.md>)
- Kind/ref: manual; 246f162a70b67203ca4d8a425b0ba4c61cf25468
- Sections inspected: Complete roadmap
- Establishes: Availability checks, duplicate regression, planned roots/search/macros/groups and completed custom fields.

### R07-S11

[Alpha v9.6.4 release](<https://github.com/TagStudioDev/TagStudio/releases/tag/v9.6.4>)
- Kind/ref: release; v9.6.4
- Sections inspected: Complete release notes
- Establishes: Per-tag category visibility, tag editor explanations, field-bar options and relink/folders-to-tags fixes.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
