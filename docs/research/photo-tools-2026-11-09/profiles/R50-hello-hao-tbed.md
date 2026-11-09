# R50 — Hello-hao/Tbed

[Repository](<https://github.com/Hello-hao/Tbed>) · 1,456 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Multi-user image hosting and share-gallery service with local/cloud storage routing; open-source and paid Core editions must be distinguished.

**Deployment:** Self-hosted web server with separate frontend/backend; Docker Compose; JDK 1.8, MySQL 5.7+ and Redis; Separate Windows/macOS desktop clients usable with both editions; WeChat mini-program restricted to paid Core

**Storage:** Upload payloads go to local storage or a configured object/FTP backend; database records track ownership, names, storage source, quota and gallery membership. Current source also contains WebDAV upload/proxy support. Gallery entries associate image URLs/notes rather than requiring another original copy.

**Privacy/network behavior:** Operator-managed server and storage, not E2EE. External object stores and configured moderation APIs may receive media; URL uploads cause server-side retrieval. Gallery password gates are application controls, not encryption assurances. README lists initial default admin credentials, which operators must replace.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 20240319 (2024-03-19T09:36:21Z)
**Repository pushed at:** 2026-10-09T13:45:24Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [869872211239](<https://github.com/Hello-hao/Tbed/commit/86987221123931366efbf79b9b029180ddcf52e4>).
**Product lineage:** Hello-hao/Tbed.

## Maturity and availability caveats

- Frozen master commit 86987221123931366efbf79b9b029180ddcf52e4; latest open-source release 20240319 is dated 2024-03-19.
- README explicitly calls repository code experimental and recommends supplied compiled packages rather than guaranteeing branch functionality.
- Paid Core contains unspecified extra features; WeChat restriction is explicit despite the introductory all-platform marketing. Current branch WebDAV/chunk endpoints are not automatically attributed to the old release.
- Official documentation URL could not be fetched because of a transport/DNS/TLS failure; primary README, release and substantial source inspected instead.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Create and edit share galleries**<br>`albums.manual` | C | Gallery controller creates a titled set of image references, supports editing membership/title and lists/deletes galleries by user/admin context. | [R50-S3](<#r50-s3>) |
| **Account and site overview**<br>`analytics.library_statistics` | C | Dashboard totals cover own images/galleries/quota usage and, for privileged users, global image/user counts, review and guest-capacity state. | [R50-S7](<#r50-s7>) |
| **Monthly upload/library record charts**<br>`analytics.timeline_counts` | C | Controller builds twelve monthly counts for a selected year, restricted to current user unless admin requests global data; not a capture-time photo timeline guarantee. | [R50-S7](<#r50-s7>) |
| **Personal image gallery and detail cards**<br>`browse.grid` | C | README documents personal album browsing and image-information cards. | [R50-S1](<#r50-s1>) |
| **Paged gallery and image results**<br>`browse.pagination` | C | Album and image queries accept page number/size and return total counts with selected rows. | [R50-S3](<#r50-s3>), [R50-S7](<#r50-s7>) |
| **Docker Compose deployment**<br>`deployment.docker` | C | README provides app/database services, persistent data volumes and separate public frontend/backend addresses. | [R50-S1](<#r50-s1>) |
| **Separate macOS desktop client**<br>`deployment.macos` | P | README explicitly offers a Mac desktop client usable with both editions. This records the separately distributed client, not native execution of the Java server as a gallery; current companion compatibility was not tested. | [R50-S1](<#r50-s1>) |
| **Self-hosted Java service**<br>`deployment.selfhosted` | C | Runtime requirements list JDK 1.8, MySQL 5.7+ and Redis; README recommends compiled integrated packages for deployment. | [R50-S1](<#r50-s1>), [R50-S2](<#r50-s2>) |
| **Web image host and administration**<br>`deployment.web` | C | Separate frontend/backend application for personal photo storage, team image sharing and web/blog image hosting. | [R50-S1](<#r50-s1>) |
| **Separate Windows desktop client**<br>`deployment.windows` | P | README explicitly offers a Windows desktop client downloadable from the project website and usable with both open-source and paid Core servers. This is a separate companion distribution, not the Java server's web UI or proof of its packaged source availability. | [R50-S1](<#r50-s1>) |
| **SVG hosting**<br>`formats.svg` | C | README explicitly lists SVG among accepted image formats; this does not establish raster editing or thumbnail rendering of SVG. | [R50-S1](<#r50-s1>) |
| **WebP and icon image hosting**<br>`formats.webp_ico` | C | README explicitly names WebP and ICO in addition to common image formats. | [R50-S1](<#r50-s1>) |
| **Controllable upload API**<br>`integration.api` | C | README documents site-controlled upload APIs and source exposes web/client routes; account token can be regenerated with immediate effect. | [R50-S1](<#r50-s1>), [R50-S6](<#r50-s6>), [R50-S7](<#r50-s7>) |
| **FTP storage destination**<br>`integration.ftp_storage` | O | FTP is explicitly listed among the open-source edition's storage sources; transport encryption is not specified. | [R50-S1](<#r50-s1>) |
| **Selectable object-storage sources**<br>`integration.object_storage` | O | Open-source list includes Alibaba OSS, UpYun USS, Qiniu KODO, Tencent COS, NetEase NOS and AWS S3 protocol, alongside local storage and FTP. | [R50-S1](<#r50-s1>) |
| **Current-source WebDAV storage adapter**<br>`integration.webdav` | ? | Branch source implements authenticated PUT, MKCOL, DELETE and proxy GET for a configured WebDAV provider, but README/release do not establish packaged open-source availability. | [R50-S8](<#r50-s8>), [R50-S6](<#r50-s6>) |
| **WeChat mini-program**<br>`integration.wechat` | $ | README explicitly limits the mini-program to paid Core and says it cannot currently connect to the open-source edition. | [R50-S1](<#r50-s1>) |
| **Drag/drop, clipboard and batch uploads**<br>`library.batch_upload` | C | Upload images by drag/drop or pasting screenshots with Ctrl+V; supports multiple images and guest/user management. | [R50-S1](<#r50-s1>) |
| **Account duplicate-upload check**<br>`library.deduplicate_import` | C | README lists account-level duplicate checking on upload; upload endpoint accepts optional MD5. Full comparison/verification semantics are not established, so this is not claimed as byte-verified library cleanup. | [R50-S1](<#r50-s1>), [R50-S6](<#r50-s6>) |
| **Temporary image retention**<br>`library.file_expiry` | C | README advertises timed temporary image storage and upload methods accept a day value; cleanup timing, provider removal and cache expiry are not established. | [R50-S1](<#r50-s1>), [R50-S6](<#r50-s6>) |
| **Batch remote-URL upload**<br>`library.url_import` | C | Newline-separated URLs are processed server-side, with a configurable referer, per-guest/user count limit and counts for failures/excess URLs. | [R50-S1](<#r50-s1>), [R50-S6](<#r50-s6>) |
| **Gallery-specific image notes**<br>`metadata.comments` | C | Gallery membership stores per-image notes along with URL/name references; embedded original-file metadata is not modified by the inspected controller. | [R50-S3](<#r50-s3>) |
| **Recorded image-name editing**<br>`metadata.display_name_edit` | C | Rename action changes the recorded idname for a stored image identifier; physical object-key renaming is not established. | [R50-S1](<#r50-s1>), [R50-S7](<#r50-s7>) |
| **Configured image content review**<br>`ai.content_moderation` | O | README describes real-time multithreaded review; configuration requires service API credentials and can enable a selected review provider. No on-device or air-gapped guarantee. | [R50-S1](<#r50-s1>), [R50-S5](<#r50-s5>) |
| **Current-branch chunk upload endpoints**<br>`performance.chunked_upload` | C | Source exposes uploadChunkFile and processFile/merge endpoints for web and client routes; this establishes branch support, not guaranteed 20240319 package parity or restart-resume semantics. | [R50-S6](<#r50-s6>) |
| **IP upload blocking**<br>`privacy.ip_blocklist` | C | Administrator-configurable IP blacklist is explicitly documented. | [R50-S1](<#r50-s1>) |
| **Image-record date-range filter**<br>`search.date_range` | C | Query accepts start/stop times and rejects reversed ranges; whether dates are capture EXIF or upload timestamps is not established here. | [R50-S7](<#r50-s7>) |
| **Image-name search**<br>`search.filename_path` | C | selectPhoto passes a nonempty searchname into the image query; ordinary users are constrained to their own user ID. | [R50-S7](<#r50-s7>) |
| **Administrative record filters**<br>`search.storage_owner_moderation` | C | Admins can filter by storage source, username/user type, own-versus-all and violation flag, with ascending/descending order selection. | [R50-S7](<#r50-s7>) |
| **Customizable embed code**<br>`sharing.embed_codes` | C | One-click copy of image embed links with user-defined code format. | [R50-S1](<#r50-s1>) |
| **Configurable visitor upload capacity**<br>`sharing.guest_upload` | C | Guest uploads can be enabled/disabled and have a shared capacity budget; URL upload count limits distinguish unauthenticated from registered users. | [R50-S7](<#r50-s7>), [R50-S6](<#r50-s6>) |
| **Accounts and guest uploads**<br>`sharing.multiuser` | C | Multiple registered users and visitors have separately configurable upload management; registration/password recovery integrate email service. | [R50-S1](<#r50-s1>) |
| **Optional gallery password**<br>`sharing.password_links` | C | Gallery create/update accepts an optional password of at least three non-space characters and gallery listing checks it; not an E2EE or security-audit claim. | [R50-S3](<#r50-s3>) |
| **Direct links and gallery sharing**<br>`sharing.public_links` | C | README offers direct image links and batch gallery sharing; controller returns generated gallery keys for created collections. | [R50-S1](<#r50-s1>), [R50-S3](<#r50-s3>) |
| **QR codes for direct image links**<br>`sharing.qr_links` | C | README lists generating a QR code from an image's direct link. | [R50-S1](<#r50-s1>) |
| **Per-user quotas and expansion codes**<br>`sharing.storage_quotas` | C | Set available user capacity and bulk-generate account-expansion codes; redeeming a valid code increases the account allocation. | [R50-S1](<#r50-s1>), [R50-S7](<#r50-s7>) |
| **Group-based storage routing**<br>`storage.distribution_groups` | C | Distribution groups associate group name, storage-key ID, user type and compression flag; default group cannot be deleted. | [R50-S1](<#r50-s1>), [R50-S4](<#r50-s4>) |

## Limitations and evidence gaps

- **explicit:** Repository explicitly warns that source is experimental and may not work, and recommends compiled release bundles. Source-only features may differ from the 20240319 package. ([R50-S1](<#r50-s1>), [R50-S2](<#r50-s2>))
- **explicit:** WeChat mini-program is paid-Core-only; desktop clients work with both editions. Other paid capabilities are not enumerated precisely and are not merged into this open-source inventory. ([R50-S1](<#r50-s1>))
- **coverage-gap:** Official manual at doc.hellohao.cn could not be retrieved. Storage-provider operational limits, backup/recovery, exact expiry deletion semantics and metadata preservation remain unverified. ([R50-S1](<#r50-s1>))
- **coverage-gap:** Public description mentions watermarking but inspected open-source README/controller evidence does not establish its implementation or edition; no watermark feature is counted as present. ([R50-S1](<#r50-s1>), [R50-S4](<#r50-s4>))
- **coverage-gap:** No inspected evidence establishes face recognition, semantic search, photo-GPS maps, perceptual duplicates, app trash, byte-verified copies or E2EE. ([R50-S1](<#r50-s1>), [R50-S3](<#r50-s3>), [R50-S7](<#r50-s7>))
- **Coverage gap:** Official external manual unavailable; six targeted source files supplement README and release.
- **Coverage gap:** Open-source/Core split is explicit only where evidenced; watermark and current-source WebDAV distribution unresolved.
- **Coverage gap:** Chinese UI evidence does not establish a multilingual/localized interface selector; focused pinned-tree localization discovery found no positive evidence, so it remains undocumented rather than unsupported.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations, interface localization.

## Inspected primary sources

### R50-S1

[Hellohao open-source image hosting README](<https://github.com/Hello-hao/Tbed/blob/86987221123931366efbf79b9b029180ddcf52e4/README.md>)
- Kind/ref: readme; 86987221123931366efbf79b9b029180ddcf52e4
- Sections inspected: Complete Chinese README, all feature and edition/deployment sections
- Establishes: Open-source capabilities, supported storage, Core distinctions and experimental-code warning.

### R50-S2

[Tbed open-source release 20240319](<https://github.com/Hello-hao/Tbed/releases/tag/20240319>)
- Kind/ref: release; 20240319
- Sections inspected: Complete release notes
- Establishes: Deployment/stability release and integrated versus separate package guidance.

### R50-S3

[Gallery creation and access controller](<https://github.com/Hello-hao/Tbed/blob/86987221123931366efbf79b9b029180ddcf52e4/src/main/java/cn/hellohao/controller/AlbumController.java>)
- Kind/ref: code; 86987221123931366efbf79b9b029180ddcf52e4
- Sections inspected: Complete file
- Establishes: Gallery titles, image notes, optional passwords, pagination and user/admin ownership handling.

### R50-S4

[Storage distribution groups](<https://github.com/Hello-hao/Tbed/blob/86987221123931366efbf79b9b029180ddcf52e4/src/main/java/cn/hellohao/controller/GroupController.java>)
- Kind/ref: code; 86987221123931366efbf79b9b029180ddcf52e4
- Sections inspected: Complete file
- Establishes: Groups associate storage keys, user types and compression settings.

### R50-S5

[Image-review configuration](<https://github.com/Hello-hao/Tbed/blob/86987221123931366efbf79b9b029180ddcf52e4/src/main/java/cn/hellohao/controller/ImageReviewController.java>)
- Kind/ref: code; 86987221123931366efbf79b9b029180ddcf52e4
- Sections inspected: Complete file
- Establishes: Moderation is configured with API credentials, not established as on-device inference.

### R50-S6

[Upload controller](<https://github.com/Hello-hao/Tbed/blob/86987221123931366efbf79b9b029180ddcf52e4/src/main/java/cn/hellohao/controller/IndexController.java>)
- Kind/ref: code; 86987221123931366efbf79b9b029180ddcf52e4
- Sections inspected: Complete uploadChunk, processFile, upimg, upurlimg and WebDAV proxy methods
- Establishes: Chunk endpoints, batch URL imports, optional lifetime/MD5 parameters and guest/user limits.

### R50-S7

[Image management and statistics controller](<https://github.com/Hello-hao/Tbed/blob/86987221123931366efbf79b9b029180ddcf52e4/src/main/java/cn/hellohao/controller/AdminController.java>)
- Kind/ref: code; 86987221123931366efbf79b9b029180ddcf52e4
- Sections inspected: Complete overviewData, SpaceExpansion, setImgFileName, getRecently, updateToken, getChart and selectPhoto methods
- Establishes: Quota, monthly counts, search/filter, image-name edits and token regeneration.

### R50-S8

[Current-branch WebDAV storage adapter](<https://github.com/Hello-hao/Tbed/blob/86987221123931366efbf79b9b029180ddcf52e4/src/main/java/cn/hellohao/service/impl/WebDAVImageupload.java>)
- Kind/ref: code; 86987221123931366efbf79b9b029180ddcf52e4
- Sections inspected: Complete file
- Establishes: Authenticated remote upload, directory creation, deletion and proxy reads; release support not established.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
