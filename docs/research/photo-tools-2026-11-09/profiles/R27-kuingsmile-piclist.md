# R27 — Kuingsmile/PicList

[Repository](<https://github.com/Kuingsmile/PicList>) · 3,796 stars at the frozen snapshot · library-utility · Not archived

**Purpose:** Desktop uploader and cloud-file manager with local upload history, image processing, multiple destinations, resumable task/finalization workflows and configuration/gallery synchronization; not a conventional photo-library server.

**Deployment:** Windows x64/ARM64 installer and portable packages; macOS Intel/Apple Silicon DMG/ZIP; Linux AppImage, deb, rpm and snap release artifacts; Separate PicList-Core supplies CLI/Docker server; PicHoro is a companion Android client

**Storage:** Electron data directory or portable data folder stores data.json upload settings, manage.json cloud accounts, piclist.db upload-history records, taskQueue.json, finalization recovery data and scripts. Actual objects live at selected local/cloud destinations. Gallery sync moves records, not stored objects; management lists actual remote files.

**Privacy/network behavior:** Can use local storage but normally uploads to explicitly configured services. Credentials can be present in config exports, sync backups and mobile QR codes. Clipboard monitoring can automatically upload screenshots; scripts/plugins have file/network access. Local preview cache is loopback-only, not a public image host.

**License metadata:** MIT. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v3.6.1 (2026-10-14T02:08:58Z)
**Repository pushed at:** 2026-11-05T22:51:30Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [9f302d05e91a](<https://github.com/Kuingsmile/PicList/commit/9f302d05e91aed2c1e34680d3c88147b5b1b8474>).
**Product lineage:** Kuingsmile/PicList.

## Maturity and availability caveats

- Manifest release v3.6.1 (2026-10-14); inspected dev 9f302d05e91aed2c1e34680d3c88147b5b1b8474 and official live manual.
- v3.6.1 explicitly removes the old built-in web upload page/general-purpose web server; local HTTP upload API and preview service remain.
- Uploader, gallery deletion adapter and cloud management support are separate capability sets. Docker/CLI belong to PicList-Core, not this desktop repository.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Audio and text/code previews**<br>`browse.audio_playback` | C | Management preview supports text/code and audio/media where runtime codecs and remote responses allow; unsupported content can be downloaded externally. | [R27-S11](<#r27-s11>) |
| **Browse actual remote assets**<br>`browse.cloud_files` | C | Cloud manager selects account/bucket/repository/root and lists objects uploaded from any device, unlike machine-local gallery history. | [R27-S9](<#r27-s9>) |
| **Gallery/cloud grid and table views**<br>`browse.grid` | C | Thumbnail or row views, adjustable grid size, range selection, selected counts and per-file info. | [R27-S3](<#r27-s3>), [R27-S6](<#r27-s6>), [R27-S9](<#r27-s9>) |
| **Cloud pagination and all-page newest scan**<br>`browse.pagination` | C | First/previous/next/last/jump navigation loads missing pages; + means unknown total. Newest scans all folder pages with cancellation; normal search/sort are page-scoped, and search stays page-scoped after newest scan. | [R27-S9](<#r27-s9>) |
| **Themes and mini/tray UI**<br>`browse.theme_customization` | C | Built-in/custom themes/backgrounds, ThemeHub, mini drag/drop window and tray upload entry points, including Windows tray window in 3.6. | [R27-S1](<#r27-s1>), [R27-S3](<#r27-s3>), [R27-S8](<#r27-s8>) |
| **Cloud media preview**<br>`browse.video_playback` | C | Management media preview/playback depends on platform codecs, server response/range support; uploading arbitrary video files alone does not ensure playback. | [R27-S11](<#r27-s11>) |
| **Image preview zoom/pan**<br>`browse.zoom` | C | Scroll/+/− zoom, drag pan, reset, arrow navigation and Esc/close are documented. | [R27-S11](<#r27-s11>) |
| **Separate history removal and remote deletion**<br>`cleanup.remote_deletion` | C | Delete from Cloud toggle decides whether gallery removal also deletes destination files. Adapters need stored uploader IDs, credentials and remote metadata; failed remote operations are reported. | [R27-S2](<#r27-s2>), [R27-S3](<#r27-s3>), [R27-S6](<#r27-s6>) |
| **Separate PicHoro Android companion**<br>`deployment.android` | P | README identifies PicHoro as the separate Android mobile client, and the sync guide documents transferring configuration to it by QR code. This is a companion project, not an Android build of the PicList Electron desktop application. | [R27-S1](<#r27-s1>), [R27-S7](<#r27-s7>) |
| **Companion Core container**<br>`deployment.docker` | P | Docker runs separately maintained PicList-Core upload server; desktop repo has no Dockerfile/Compose and must not be presented as containerized gallery server. | [R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>) |
| **Linux desktop**<br>`deployment.linux` | C | AppImage, deb, rpm and snap release artifacts; clipboard behavior varies under Linux/WSL/headless sessions. | [R27-S2](<#r27-s2>), [R27-S3](<#r27-s3>), [R27-S8](<#r27-s8>) |
| **Selectable interface language**<br>`deployment.localization` | C | Official configuration guide lets users choose language in System settings; v3.6.1 fixes stale interface text after switching languages. Complete language coverage is not enumerated in these inspected sources. | [R27-S4](<#r27-s4>), [R27-S3](<#r27-s3>) |
| **macOS desktop**<br>`deployment.macos` | C | Intel and Apple Silicon DMG/ZIP releases; menu-bar/main-window behavior documented. | [R27-S2](<#r27-s2>), [R27-S3](<#r27-s3>) |
| **Portable local data directory**<br>`deployment.portable` | C | PORTABLE marker beside executable selects adjacent data directory instead of Electron user-data location. | [R27-S2](<#r27-s2>) |
| **Former built-in web upload UI**<br>`deployment.web` | N | v3.6.1 removes old built-in webpage/web server; HTTP upload API and loopback preview cache are distinct and remain documented. | [R27-S3](<#r27-s3>), [R27-S11](<#r27-s11>) |
| **Windows desktop distributions**<br>`deployment.windows` | C | Release offers x64/ARM64 installers and ZIP/7z portable builds; README also lists winget/Scoop. | [R27-S1](<#r27-s1>), [R27-S3](<#r27-s3>) |
| **Encoder-dependent quality control**<br>`editing.image_compression` | C | Quality presets/slider apply during upload; docs explicitly warn quality percentages are not guaranteed size savings and PNG may not shrink much. | [R27-S5](<#r27-s5>) |
| **Input-specific format conversion**<br>`editing.format_conversion` | C | Preserve source format or choose output with per-input-extension rules. Bypass extensions upload without processing; preview support does not establish encoder availability. | [R27-S3](<#r27-s3>), [R27-S5](<#r27-s5>) |
| **Three-level image-processing inheritance**<br>`editing.processing_scopes` | C | Named configuration overrides provider overrides global defaults, including explicit disabled switches. Effective settings show value sources and can revert to inherited values. | [R27-S5](<#r27-s5>) |
| **Dimension/percentage resize and no enlargement**<br>`editing.resize` | C | Zero dimension preserves proportional sizing; percentage mode takes precedence over fixed dimensions, and small-image enlargement can be disabled. | [R27-S5](<#r27-s5>) |
| **Upload rotation/flipping**<br>`editing.rotate_flip` | C | Processing supports rotation and flips; these and later plugins may change final dimensions. | [R27-S1](<#r27-s1>), [R27-S5](<#r27-s5>) |
| **Text/image/tiled watermarks**<br>`editing.watermark` | C | Text uses local/custom font, size/color/margins/position; image watermark supports scale/opacity/placement and full-image repeated coverage. Missing default-font download can skip watermark. | [R27-S2](<#r27-s2>), [R27-S5](<#r27-s5>) |
| **JPEG XL via PNG preview**<br>`formats.jpegxl` | C | JXL can use generated PNG previews without changing stored original; JXL encoding support is not promised. | [R27-S5](<#r27-s5>), [R27-S11](<#r27-s11>) |
| **SVG gallery preview**<br>`formats.svg` | C | v3.6 adds SVG image previews; non-image gallery entries use extension icons. | [R27-S3](<#r27-s3>), [R27-S11](<#r27-s11>) |
| **Local HTTP upload server**<br>`integration.api` | C | Default endpoint is loopback port 36677/upload, with later port fallback; nonloopback callers need configured key query value, recognized loopback requests receive it automatically. | [R27-S2](<#r27-s2>), [R27-S13](<#r27-s13>) |
| **Separate PicList-Core command-line interface**<br>`integration.cli` | P | PicList-Core supplies the separately usable CLI, including an interactive terminal interface, setup wizard and named upload/configuration choices described in the release notes. The Electron desktop repository is not itself a standalone CLI distribution; Core requires its documented Node.js runtime. | [R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>), [R27-S3](<#r27-s3>) |
| **Configuration sync through Git/WebDAV**<br>`integration.configuration_sync` | O | Upload/download common settings, management settings or all configs using selected private Git/WebDAV target; direction can overwrite current defaults and contains credentials. | [R27-S1](<#r27-s1>), [R27-S7](<#r27-s7>) |
| **Markdown editor integrations**<br>`integration.editor_upload` | P | Typora &gt;=1.6 selects PicList directly; older Typora uses PicGo(app). Obsidian requires Image Auto Upload plugin and VS Code uses VS-PicList extension. | [R27-S1](<#r27-s1>) |
| **Previewed cross-device history sync**<br>`integration.gallery_sync` | O | Plans additions/updates/deletions/conflicts and supports local, remote or both conflict choices with exported summary; transfers records, never all cloud objects. | [R27-S3](<#r27-s3>), [R27-S7](<#r27-s7>) |
| **Repository/image-host adapters**<br>`integration.hosting_services` | O | GitHub, S.EE and Imgur have management/deletion clients; Lsky, Alist and other PicList servers have upload/deletion but no dedicated management client. Huawei OBS deletion depends on corresponding uploader records. | [R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>) |
| **Managed JavaScript lifecycle scripts**<br>`integration.lifecycle_scripts` | O | Scripts run at startup/shutdown, preprocess/transform/upload/success/gallery removal or manually; advanced uploader stage can set result URLs. Access includes filesystem/network and local .env values; no separate Node runtime required for scripting. | [R27-S1](<#r27-s1>), [R27-S12](<#r27-s12>) |
| **Local filesystem upload destination**<br>`integration.local_storage` | C | Built-in local destination supports upload, destination-file deletion and file management. Core release notes describe writing to a temporary file before replacing the local destination to reduce incomplete output after interruption. | [R27-S1](<#r27-s1>), [R27-S3](<#r27-s3>) |
| **Object/cloud storage clients**<br>`integration.object_storage` | O | Upload/deletion/management support includes S3/R2/MinIO, OSS, COS, Qiniu and Upyun; Doge Cloud management uses the S3 client. Requires service credentials. | [R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>) |
| **Companion Android configuration transfer**<br>`integration.pichoro` | P | PicHoro imports uploader configuration by QR code; codes can expose destination credentials and should be transferred privately. | [R27-S1](<#r27-s1>), [R27-S7](<#r27-s7>) |
| **PicGo-compatible plugin ecosystem**<br>`integration.plugins` | P | Many PicGo plugins work, not all. System npm is default; experimental bundled npm avoids separate installation but native plugins can still require build tools. | [R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>), [R27-S3](<#r27-s3>) |
| **SFTP upload and file management**<br>`integration.sftp_storage` | O | Configured SFTP destination supports upload, remote gallery deletion and cloud file management. Core release notes describe temporary-file writes before replacement and recursive folder downloads; network credentials and remote-file metadata are required for relevant operations. | [R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>), [R27-S3](<#r27-s3>) |
| **WebDAV upload and management**<br>`integration.webdav` | O | WebDAV supports upload, remote gallery deletion and cloud management; credentials and serving URLs remain separate from loopback previews. | [R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>), [R27-S11](<#r27-s11>) |
| **Previewed bulk record URL replacement**<br>`library.batch_url_edit` | C | Select/filter records, inspect pattern-based before/after matches and final plan before applying. This edits history only, not remote filenames or published Markdown documents. | [R27-S6](<#r27-s6>) |
| **Cloud regex batch rename**<br>`library.bulk_rename` | C | Cloud batch renaming/moving provides preview, conflict policies and failed-item retry; provider may implement rename via copy-then-delete and require both permissions. | [R27-S1](<#r27-s1>), [R27-S3](<#r27-s3>), [R27-S9](<#r27-s9>) |
| **Automatic clipboard image uploads**<br>`library.clipboard_monitor` | C | Optional monitoring uploads newly copied images automatically, including temporary screenshots; docs warn about online destination exposure. | [R27-S8](<#r27-s8>) |
| **Cloud downloads and folder transfer**<br>`library.export_originals` | C | Downloads selected remote files/folders to chosen local path; transfer list supports pause/resume/cancel and per-item outcomes, with provider-specific paging constraints. | [R27-S3](<#r27-s3>), [R27-S9](<#r27-s9>) |
| **File and clipboard upload**<br>`library.managed_upload` | C | Drag/drop, multi-file selection, clipboard images, absolute paths and file URLs upload to chosen named configuration; arbitrary files depend on provider size/type restrictions. | [R27-S2](<#r27-s2>), [R27-S8](<#r27-s8>) |
| **Multiple named provider configurations**<br>`library.named_upload_profiles` | C | Maintain multiple accounts/configurations per provider; setting default is separate from saving, and up to six favorites enable quick switching. | [R27-S4](<#r27-s4>), [R27-S8](<#r27-s8>) |
| **Second upload destination**<br>`library.secondary_upload` | C | Can reuse primary processed bytes or independently process original input using secondary settings. Errors are separate and identical configuration can be skipped; not a backfill of earlier uploads. | [R27-S8](<#r27-s8>) |
| **Date/hash/path naming templates**<br>`library.upload_naming_templates` | C | Patterns support original basename, date/time/milliseconds, UUID/ULID, random fragments, MD5/SHA-1/SHA-256 and trailing local directories; extension is appended and nested paths depend on provider. | [R27-S5](<#r27-s5>) |
| **Remote URL rehosting**<br>`library.url_import` | C | Downloads one direct HTTP(S) image URL per line and uploads to destination; explicitly not webpage screenshot capture. | [R27-S8](<#r27-s8>) |
| **EXIF removal during processing**<br>`metadata.strip` | C | Release specifically documents EXIF removal compatibility fixes for HEIF; complete preserved/removed field matrix is not established. | [R27-S3](<#r27-s3>) |
| **Paced upload queue**<br>`performance.background_jobs` | C | Queue has pending/completed/failed states, reorder/priority, filename filtering, interval 0.1–99999 seconds, up to 10 auto retries, optional auto-start and pause-on-error. | [R27-S10](<#r27-s10>) |
| **Pause/cancel without undoing delivery**<br>`performance.cancel` | C | Pause lets active file finish; cancel stops relevant pending work but does not remove delivered files. Cloud requests are cancelled when switching folders/accounts to avoid stale results. | [R27-S3](<#r27-s3>), [R27-S10](<#r27-s10>) |
| **Restart-aware queued uploads**<br>`performance.resume` | C | taskQueue.json persists state and identifies interrupted work; resume uses current default destination at execution time and requires original source paths. | [R27-S3](<#r27-s3>), [R27-S10](<#r27-s10>) |
| **Private full-data backup workflow**<br>`safety.catalogue_backup` | C | Documented backup closes app then copies configs, gallery DB, queue/recovery data and scripts; actual destination objects and outside fonts/dependencies need separate backup. | [R27-S7](<#r27-s7>) |
| **Scoped synchronization rollback snapshots**<br>`safety.sync_recovery_snapshots` | C | Sync snapshots allow local rollback on failure with retention, size display, export/deletion and active-use protection. Cannot restore deleted remote objects; not general file-operation undo. | [R27-S3](<#r27-s3>), [R27-S7](<#r27-s7>) |
| **Recover result saving without reupload**<br>`safety.upload_finalization_recovery` | C | Records remote completion separately from gallery/success-script finalization. Retrying original task uses persisted finalization data and API finalizationId rather than uploading again. | [R27-S8](<#r27-s8>), [R27-S10](<#r27-s10>) |
| **Gallery date/provider filtering**<br>`search.date_range` | C | Gallery filter controls narrow records by provider/date and sort order; history defaults newest first. | [R27-S6](<#r27-s6>) |
| **Filename and recorded-URL search**<br>`search.filename_path` | C | Gallery searches partial names or URL domain/path; cloud search scope is current page, not necessarily every remote file. | [R27-S6](<#r27-s6>), [R27-S9](<#r27-s9>) |
| **Multiple reusable link formats**<br>`sharing.link_templates` | C | Copy Markdown/HTML/URL/UBB/custom links individually or in batches; gallery supports url/name/extension placeholders, cloud per-bucket templates also object path/directory. | [R27-S3](<#r27-s3>), [R27-S6](<#r27-s6>), [R27-S8](<#r27-s8>) |
| **Provider-signed temporary links**<br>`sharing.presigned_urls` | O | Cloud workflows support private temporary signed addresses and batch copying; expiration and accessibility depend on provider, not a PicList hosted share database. | [R27-S3](<#r27-s3>), [R27-S9](<#r27-s9>), [R27-S11](<#r27-s11>) |
| **External short-link service**<br>`sharing.short_urls` | O | Long/short URL output is available but shortening requires a configured service; generated names or shortened URLs do not add privacy. | [R27-S6](<#r27-s6>), [R27-S8](<#r27-s8>) |

## Limitations and evidence gaps

- **explicit:** Gallery history, configs and actual objects are independent; gallery sync/snapshots cannot restore deleted remote files or fix already published article links. ([R27-S6](<#r27-s6>), [R27-S7](<#r27-s7>), [R27-S9](<#r27-s9>))
- **explicit:** Queued destination is resolved when each task executes, not pinned on enqueue; changing defaults can redirect later files. ([R27-S8](<#r27-s8>), [R27-S10](<#r27-s10>))
- **explicit:** Cloud search normally covers current page, even after newest-files scans; newest order needs provider timestamps and can require loading all pages. ([R27-S9](<#r27-s9>))
- **explicit:** Provider upload/deletion/management capabilities differ and require their own permissions/settings. Temporary signed/cache URLs are not permanent public article links. ([R27-S1](<#r27-s1>), [R27-S2](<#r27-s2>), [R27-S11](<#r27-s11>))
- **explicit:** Configs, sync exports and QR codes can contain credentials. Scripts access files/network, clipboard monitoring can upload screenshots and default watermark fonts may be fetched online. ([R27-S2](<#r27-s2>), [R27-S7](<#r27-s7>), [R27-S8](<#r27-s8>), [R27-S12](<#r27-s12>))
- **coverage-gap:** Exact/perceptual duplicate cleanup, face recognition, maps, full EXIF catalogue editing and E2EE are not established; hash naming is not duplicate detection. ([R27-S1](<#r27-s1>), [R27-S5](<#r27-s5>), [R27-S6](<#r27-s6>))
- **Coverage gap:** No providers contacted with credentials or user files; throughput/codec support not benchmarked.
- **Coverage gap:** Live manuals may lead release; desktop/Core/mobile scope explicitly separated.
- **Coverage gap:** Encryption options mentioned for configuration sync were not sufficient to establish E2EE media storage.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R27-S1

[PicList README](<https://github.com/Kuingsmile/PicList/blob/9f302d05e91aed2c1e34680d3c88147b5b1b8474/README.md>)
- Kind/ref: readme; 9f302d05e91aed2c1e34680d3c88147b5b1b8474
- Sections inspected: Complete features, platforms, integrations and provider matrix
- Establishes: Desktop scope, processing, sync, plugin ecosystem and provider distinctions.

### R27-S2

[Current FAQ](<https://github.com/Kuingsmile/PicList/blob/9f302d05e91aed2c1e34680d3c88147b5b1b8474/FAQ_EN.md>)
- Kind/ref: manual; 9f302d05e91aed2c1e34680d3c88147b5b1b8474
- Sections inspected: All 15 questions
- Establishes: Separate configs/services, file types, deletion requirements, local server auth, paths, fonts and npm caveats.

### R27-S3

[v3.6.1 release](<https://github.com/Kuingsmile/PicList/releases/tag/v3.6.1>)
- Kind/ref: release; v3.6.1
- Sections inspected: Complete English and Chinese release notes
- Establishes: Sync previews/snapshots, upload finalization recovery, cloud pagination, safety fixes and removed web UI.

### R27-S4

[Configuration](<https://piclist.cn/en/configure>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete upload/management/preferences, paths and credential warnings
- Establishes: Configuration separation and named destinations.

### R27-S5

[Image processing and naming](<https://piclist.cn/en/workflows/processing>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete scope, quality, resize, watermark, naming and bypass workflows
- Establishes: Override precedence, resize priority, hash/date names and external font dependency.

### R27-S6

[Gallery and links](<https://piclist.cn/en/workflows/gallery>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete search, copy templates, URL edits and deletion distinctions
- Establishes: History versus remote files, previewed batch edits and record-only versus cloud delete.

### R27-S7

[Backup and sync](<https://piclist.cn/en/workflows/sync>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete local backups, config sync, gallery plans/snapshots and mobile import
- Establishes: Credential sensitivity and boundaries of record/config recovery.

### R27-S8

[Upload workflows](<https://piclist.cn/en/workflows/uploads>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete files, clipboard, URLs, links, mini/tray, secondary destination and finalization
- Establishes: Input sources, dual-upload processing and result recovery.

### R27-S9

[Cloud storage manager](<https://piclist.cn/en/manage>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete account setup, listing, pagination/newest scan, transfers, renames and batch outcomes
- Establishes: Actual cloud objects, page-scoped search and provider-dependent operations.

### R27-S10

[Upload tasks and recovery](<https://piclist.cn/en/workflows/tasks>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete destination, queue, retries, pause/cancel and finalization recovery
- Establishes: Persisted queue, execution-time destination, retry semantics and local recovery journal.

### R27-S11

[File previews](<https://piclist.cn/en/preview>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete images, text/media and preview/public URL distinctions
- Establishes: Image controls, SVG/JXL, platform playback and local preview service.

### R27-S12

[Script system](<https://piclist.cn/en/script>)
- Kind/ref: manual; live-docs inspected 2026-11-09
- Sections inspected: Complete stage table, API, execution and credential notes
- Establishes: Lifecycle JavaScript and file/network privileges.

### R27-S13

[Main-process API boundaries](<https://github.com/Kuingsmile/PicList/blob/9f302d05e91aed2c1e34680d3c88147b5b1b8474/src/main/apis/README.md>)
- Kind/ref: manual; 9f302d05e91aed2c1e34680d3c88147b5b1b8474
- Sections inspected: Complete directory responsibilities and renderer/interface explanation
- Establishes: Core uploaders, distinct deletion/management adapters, plugin GUI API and separate local HTTP interface.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
