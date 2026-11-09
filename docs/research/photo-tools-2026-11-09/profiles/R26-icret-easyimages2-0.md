# R26 — icret/EasyImages2.0

[Repository](<https://github.com/icret/EasyImages2.0>) · 3,802 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Database-free PHP image host for personal or guest uploading, transformations, moderation and server-side file administration rather than a complex multi-user photo library.

**Deployment:** Self-hosted PHP web application; Linux/Nginx recommended; PHP 7.4 minimum; documented supported range 7.4–8.4; Community Docker distribution linked by project

**Storage:** Files normally reside under a configurable image root with year/month/day paths. PHP configuration files, filesystem counts, logs and caches replace a required database. Optional uploader/admin/token directory separation and FTP configuration exist; application recycle and suspect-image areas retain moved files.

**Privacy/network behavior:** Can host original content on one's server, but optional ModerateContent, TinyPNG, FTP, CDN and nsfwjs services change data flow. Default config includes an external Baidu analytics footer. Upload IP logging/geolocation and publicly exposed statistics are configurable. Source-link protection is not media-at-rest encryption.

**License metadata:** GPL-2.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 2.8.7 (2026-10-27T16:26:54Z)
**Repository pushed at:** 2026-10-27T17:28:38Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [5f3e08bb0af5](<https://github.com/icret/EasyImages2.0/commit/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627>).
**Product lineage:** icret/EasyImages2.0.

## Maturity and availability caveats

- Frozen master 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627; manifest latest release 2.8.7 dated 2026-10-27.
- Release 2.8.7 reports major security/stability fixes and deliberately breaks old password hashes, sessions and encrypted deletion/source-protection links; release notes also describe a reissued tag on October 28.
- README explicitly targets personal/guest hosting and says it is unsuitable for complex multi-user scenarios.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Remote ModerateContent review**<br>`ai.content_moderation` | O | Enable configured ModerateContent key and moderation mode to classify uploads. The manual's registration instructions were not validated against current provider availability. | [R26-S4](<#r26-s4>) |
| **Separate nsfwjs moderation service**<br>`ai.selfhosted_moderation` | O | Can deploy an nsfwjs REST container or compatible endpoint returning Drawing/Hentai/Neutral/Porn/Sexy probabilities; this is a separate service, not in-process local inference. | [R26-S4](<#r26-s4>), [R26-S8](<#r26-s8>) |
| **Site and storage statistics**<br>`analytics.library_statistics` | C | Website charts/statistics are documented; optional public API can expose selected daily/monthly file counts, folders and used/free/total storage data. | [R26-S1](<#r26-s1>), [R26-S9](<#r26-s9>), [R26-S10](<#r26-s10>) |
| **Dark appearance option**<br>`browse.dark_theme` | C | Default site configuration exposes dark-mode and theme settings. | [R26-S10](<#r26-s10>) |
| **Public square and image details**<br>`browse.public_gallery` | C | Online gallery/administration and per-image information are documented; optional user/token/admin directory separation changes what appears publicly. | [R26-S1](<#r26-s1>), [R26-S6](<#r26-s6>) |
| **Community Docker deployment**<br>`deployment.docker` | P | Project documentation links DDS-Derek/EasyImage-Docker rather than establishing an official core image. | [R26-S13](<#r26-s13>) |
| **Simplified/Traditional Chinese interface conversion**<br>`deployment.localization` | C | Setting language=1 loads the bundled jquery.s2t script and converts page elements to Traditional Chinese. This is a built-in Chinese-script conversion option; English or a broader translated UI catalogue is not established by this evidence. | [R26-S10](<#r26-s10>), [R26-S15](<#r26-s15>) |
| **Database-free self-hosting**<br>`deployment.selfhosted` | C | PHP application does not require a database; README recommends Linux with Nginx and lists required PHP extensions. | [R26-S1](<#r26-s1>) |
| **Separate media hostname**<br>`deployment.separate_media_domain` | O | Bind an image domain directly to the image root to hide /i/ in returned paths; it must differ from the site domain for this mode. | [R26-S7](<#r26-s7>) |
| **Configurable page and advertising content**<br>`deployment.site_branding` | C | Site title/description, notices, custom code, header/footer advertisements and footer content are configurable. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>) |
| **Responsive browser uploader**<br>`deployment.web` | C | HTML5 desktop/mobile upload UI returns reusable links; README retains legacy-browser fallback language. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>) |
| **Upload format conversion**<br>`editing.format_conversion` | C | Convert uploaded images to a specified format, subject to server image-library support. | [R26-S1](<#r26-s1>), [R26-S14](<#r26-s14>) |
| **Configurable image compression**<br>`editing.image_compression` | C | Set image quality/compression and image-size reduction; configuration also offers a separate TinyPNG service key. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>) |
| **Upload dimension transformation**<br>`editing.resize` | C | Configure target width/height, ratio, crop and quality settings for uploaded image transformations. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>) |
| **Text or image watermark**<br>`editing.watermark` | C | Configure text/image watermark, position, font, size and color. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>) |
| **Configured non-image uploads**<br>`formats.arbitrary_uploads` | C | Add extensions such as MP4, PDF or MP3 and disable image-only mode to upload other types. This does not establish a video/audio playback library. | [R26-S5](<#r26-s5>) |
| **Token upload API**<br>`integration.api` | O | Enable API uploads and POST multipart image plus token. Response includes original filename, URL, thumbnail, deletion link and token ID; optional token-ID filename suffix is documented in 2.8.7. | [R26-S2](<#r26-s2>), [R26-S8](<#r26-s8>), [R26-S12](<#r26-s12>) |
| **Optional FTP transfer settings**<br>`integration.ftp_storage` | O | Configuration includes remote FTP host, port, passive/SSL mode, local-after-transfer deletion and synchronized remote deletion; deletion controller invokes the FTP delete hook. End-to-end transfer behavior was not runtime-tested. | [R26-S10](<#r26-s10>), [R26-S11](<#r26-s11>) |
| **PicGo web-uploader plugin**<br>`integration.picgo` | P | Separate PicGo web-uploader plugin maps image/token fields and the response URL after enabling API upload. | [R26-S12](<#r26-s12>) |
| **Date-based managed storage**<br>`library.auto_date_folders` | C | Default storage root is /i/ with year/month/day folders; configuration warns changing that structure can impair operations. | [R26-S10](<#r26-s10>) |
| **Multi-file drag-and-drop upload**<br>`library.batch_upload` | C | Upload queue supports multiple files and HTML5 drag-and-drop; defaults configure 30 files per upload and 10 MiB per file, adjustable subject to PHP limits. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>), [R26-S14](<#r26-s14>) |
| **Optional chunked uploads**<br>`performance.chunked_upload` | O | chunks configuration enables split uploads; release 2.8.7 fixes large-file chunk merging into the wrong directory. | [R26-S8](<#r26-s8>), [R26-S10](<#r26-s10>) |
| **Uploader/admin/token separation**<br>`library.uploader_directory_separation` | O | Separate upload-user, administrator and token-ID directories; the public square excludes those separated uploads and lists guest uploads only. | [R26-S6](<#r26-s6>), [R26-S10](<#r26-s10>) |
| **Administrative cache refresh**<br>`maintenance.cache_reset` | C | Admin controller supports resetting PHP OPcache when available and deleting cached version information. | [R26-S11](<#r26-s11>) |
| **Upload logs and IP location**<br>`maintenance.upload_audit` | C | Upload logs support uploader IP geolocation; release updates ip2region data and removes password/hash material from login logs. | [R26-S1](<#r26-s1>), [R26-S8](<#r26-s8>) |
| **Configurable EXIF information display**<br>`metadata.exif_read` | C | show_exif_info configuration controls image information display; no embedded-metadata editing workflow is established. | [R26-S10](<#r26-s10>) |
| **Cached filesystem statistics**<br>`performance.cached_file_counts` | C | 2.8.7 caches/iterates square file counts, general file counting and version checks to avoid recursive full-directory scans on every request; not a measured benchmark. | [R26-S8](<#r26-s8>) |
| **Generated thumbnail delivery**<br>`performance.thumbnail_cache` | C | Thumbnail generation has configurable dimensions and is exposed by the upload API; 2.8.7 fixes thumbnail/backend compression behavior. | [R26-S2](<#r26-s2>), [R26-S8](<#r26-s8>), [R26-S10](<#r26-s10>) |
| **Protected original-image links**<br>`privacy.source_link_protection` | O | Configurable source protection uses keyed links; 2.8.7 changes token/key handling and invalidates old links. FAQ warns web-server image caching can cause 404 behavior. | [R26-S8](<#r26-s8>), [R26-S10](<#r26-s10>), [R26-S14](<#r26-s14>) |
| **Recycle area and restoration**<br>`safety.app_recovery` | C | With image_recycl enabled, capability-link deletes move files to recycle storage. Admin supports recycle, restore and permanent deletion, including bulk actions. | [R26-S10](<#r26-s10>), [R26-S11](<#r26-s11>) |
| **Accurate batch-delete outcomes**<br>`safety.partial_failure_reporting` | C | Bulk deletion reports complete success, partial failure or total failure and returns failed paths instead of always claiming success. | [R26-S11](<#r26-s11>) |
| **Uploader deletion links**<br>`sharing.deletion_capability_links` | C | API returns an authorized deletion link usable without admin login. Version 2.8.7 redesigns capability tokens with authenticated encryption and separate delete/hide purposes; this encrypts tokens, not stored pictures. | [R26-S2](<#r26-s2>), [R26-S8](<#r26-s8>), [R26-S11](<#r26-s11>) |
| **Guest or login-only uploads**<br>`sharing.guest_upload` | C | Guest hosting is a primary scenario; mustLogin switches to authenticated-only uploads, with optional daily counts and IP restrictions. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>) |
| **IP allow/block controls**<br>`sharing.ip_access_control` | C | Upload IP blacklists/whitelists are supported; trusted_proxy configuration added with fixes to prevent spoofed forwarding headers bypassing limits. | [R26-S1](<#r26-s1>), [R26-S8](<#r26-s8>) |
| **Restore moderation-quarantined images**<br>`sharing.moderation_restore` | C | Administrative suspic_reimg action restores files from the suspect-image area independently of the ordinary recycle area. | [R26-S11](<#r26-s11>) |
| **Direct and embed links**<br>`sharing.public_links` | C | Return direct URL, Markdown, BBCode and HTML links with copying; API also supplies thumbnail and deletion links. | [R26-S1](<#r26-s1>), [R26-S2](<#r26-s2>) |
| **Administrator and upload-only users**<br>`sharing.roles` | C | Create accounts restricted to uploading while administrative file/configuration operations require admin identity; this is not a full collaborative account system. | [R26-S1](<#r26-s1>), [R26-S11](<#r26-s11>) |
| **Upload size, count and dimension limits**<br>`sharing.upload_quotas` | C | Configure daily uploads, per-upload count/size, allowed extensions and minimum/maximum pixel dimensions. | [R26-S1](<#r26-s1>), [R26-S10](<#r26-s10>) |

## Limitations and evidence gaps

- **explicit:** Not intended for complex multi-user use; uploader roles and directory separation should not be equated with private album permissions. ([R26-S1](<#r26-s1>), [R26-S6](<#r26-s6>))
- **explicit:** 2.8.7 disables file-manager online editing, archive download and remote fetching. Older feature descriptions of those functions are not current capabilities. ([R26-S8](<#r26-s8>))
- **explicit:** Upgrades to 2.8.7 invalidate old passwords, sessions and deletion/source-protection links; required configuration and PHP migration steps are explicit. ([R26-S8](<#r26-s8>))
- **explicit:** Operators must deny web access to credentials/configuration and script execution in upload directories. Nginx/Caddy/Lighttpd do not apply Apache .htaccess protections automatically. ([R26-S3](<#r26-s3>))
- **explicit:** External analytics are present in default footer configuration. Optional external compression/moderation/FTP/CDN integrations preclude assuming entirely offline or third-party-free operation. ([R26-S4](<#r26-s4>), [R26-S10](<#r26-s10>))
- **coverage-gap:** No inspected evidence establishes duplicate discovery, face recognition, semantic search, album taxonomy, metadata writing, encrypted media storage or a durable operation journal. ([R26-S1](<#r26-s1>), [R26-S2](<#r26-s2>), [R26-S10](<#r26-s10>), [R26-S11](<#r26-s11>))
- **Coverage gap:** Backend-management document is mainly a screenshot; substantive capabilities were verified against README, detailed manuals, configuration and deletion source.
- **Coverage gap:** FTP guide is only a short troubleshooting list; FTP integration evidence is configuration plus deletion hooks, not runtime verification.
- **Coverage gap:** External-service availability and current pricing were not independently tested.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R26-S1

[EasyImage README](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/README.md>)
- Kind/ref: readme; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete README
- Establishes: Scope, uploads, transformations, moderation, roles, logs, statistics and requirements.

### R26-S2

[Upload API](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/API.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete API examples and response fields
- Establishes: Token multipart uploads, original name, thumbnail and deletion URL responses.

### R26-S3

[Web server safety configuration](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/安全配置.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete Apache, Nginx and Lighttpd instructions
- Establishes: Configuration-directory protection and prevention of script execution from uploads.

### R26-S4

[Content moderation](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/鉴黄.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete ModerateContent and nsfwjs instructions
- Establishes: External moderation and separately deployed nsfwjs API.

### R26-S5

[Other file formats](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/其他格式.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete document
- Establishes: Extension configuration, non-image mode and dangerous-format warning.

### R26-S6

[Upload separation](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/分离相关.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete document
- Establishes: User/token/admin directories and guest-only public square.

### R26-S7

[Hiding storage-path prefix](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/隐藏存储路径.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete document
- Establishes: Separate media domain rooted at the storage directory.

### R26-S8

[2.8.7 release notes](<https://github.com/icret/EasyImages2.0/releases/tag/2.8.7>)
- Kind/ref: release; 2.8.7; live release text includes reissue note
- Sections inspected: Complete fixes, additions, compatibility and migration notes
- Establishes: Current restrictions, token suffix, cache changes and breaking upgrade requirements.

### R26-S9

[Public statistics API](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/公共查询.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete document
- Establishes: Opt-in public counters and selectable data.

### R26-S10

[Default site configuration](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/config/config.php>)
- Kind/ref: code; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete configuration, especially upload/storage/image/security/statistics keys and footer
- Establishes: Concrete limits, filesystem layout, themes, optional services and external analytics default.

### R26-S11

[Deletion, recycling and restore controller](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/app/del.php>)
- Kind/ref: code; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete controller
- Establishes: Capability-link deletion, admin bulk actions, partial failures, recovery and cache reset.

### R26-S12

[PicGo integration](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/使用PicGo上传.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete instructions
- Establishes: Separate web-uploader plugin and required API/token settings.

### R26-S13

[Third-party deployment guide](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/三方安装指南.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete guide
- Establishes: Official documentation links a community-maintained Docker package.

### R26-S14

[FAQ](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/docs/常见问题.md>)
- Kind/ref: manual; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete FAQ
- Establishes: Subpath support, PHP/image extension dependencies and source-protection caching pitfalls.

### R26-S15

[Chinese interface script conversion](<https://github.com/icret/EasyImages2.0/blob/5f3e08bb0af55b70deddf2ef86fa3535aa5dd627/app/footer.php>)
- Kind/ref: code; 5f3e08bb0af55b70deddf2ef86fa3535aa5dd627
- Sections inspected: Complete conditional language==1 block loading jquery.s2t and applying s2t to page elements
- Establishes: Explicit Simplified-to-Traditional Chinese UI conversion, not a general multilingual catalogue.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
