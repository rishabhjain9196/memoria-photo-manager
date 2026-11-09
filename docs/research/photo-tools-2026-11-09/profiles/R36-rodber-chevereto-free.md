# R36 — rodber/chevereto-free

[Repository](<https://github.com/rodber/chevereto-free>) · 2,770 stars at the frozen snapshot · gallery-sharing · Archived

**Purpose:** Archived legacy PHP/MySQL image-sharing site for personal use and small communities; a deliberately reduced fork of Chevereto 3.16.2, not the current Chevereto product.

**Deployment:** Self-hosted PHP 7.4 web application; MySQL 5.7/8 or MariaDB 10; Apache or Nginx with URL rewriting

**Storage:** Local uploads are registered in a relational database, with configurable flat or year/month/day storage and generated thumbnails/medium images. Public IDs are encoded. External-storage references remain in inherited documentation/schema but the release explicitly removes that feature.

**Privacy/network behavior:** Can run as a public community or login-required private site, with album-level owner-only, link-accessible or password-gated content. These access controls and encoded URLs are not encrypted media storage. Optional CDN, spam checking, CAPTCHA, comments or analytics can involve outside services.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** 1.6.2 (2022-01-07T22:02:55Z)
**Repository pushed at:** 2026-11-01T20:16:13Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [ee91365ae837](<https://github.com/rodber/chevereto-free/commit/ee91365ae837c6159e2377dfe74ad97bf6f58382>).
**Product lineage:** Chevereto.

## Maturity and availability caveats

- Frozen 1.6 branch ee91365ae837c6159e2377dfe74ad97bf6f58382; latest release 1.6.2 dated 2022-01-07; repository archived.
- Official status page states there will be no further fixes and advises migration to newer Chevereto. Current README says the projects must not be conflated.
- Critical edition check: release-1.6.2 README explicitly lists removed/missing features. Official legacy docs contain inherited settings for some of these; the explicit release exclusion takes precedence.
- PHP 8 is explicitly unsupported; neither current Chevereto V4 capabilities nor paid successor services are credited to this repository.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **User albums**<br>`albums.manual` | C | Images are organized into owner-associated albums with descriptions, image counts and editing tools. | [R36-S18](<#r36-s18>) |
| **Nested albums**<br>`albums.nested` | N | Listed among later Chevereto changes missing from Free. | [R36-S2](<#r36-s2>) |
| **Listing lightbox viewer**<br>`browse.fullscreen` | C | Optional listing viewer provides full-screen image browsing. | [R36-S6](<#r36-s6>) |
| **Tiled or masonry listings**<br>`browse.grid` | C | Fixed or fluid image listings with device-specific column counts and minimum image count for album exploration. | [R36-S6](<#r36-s6>) |
| **Classic or endless pagination**<br>`browse.pagination` | C | Configure items/page and traditional page navigation or XHR-based endless append; not asserted as DOM virtualization. | [R36-S6](<#r36-s6>) |
| **360-degree viewing**<br>`browse.panorama` | N | Listed among successor features missing from Free. | [R36-S2](<#r36-s2>) |
| **Random public-image browsing**<br>`browse.random` | C | Enable random public-image fetching independently of Explore and guest Explore. | [R36-S4](<#r36-s4>) |
| **Multiple UI languages in Free edition**<br>`deployment.localization` | N | The 1.6.2 edition-scope README explicitly lists Multi-language Support among features removed from Chevereto-Free. Translated upstream resources or successor documentation do not establish this capability in the reduced fork. | [R36-S2](<#r36-s2>) |
| **Self-hosted image sharing**<br>`deployment.selfhosted` | C | Run the legacy PHP/MySQL application on one's own server; PHP 7.4 is required and PHP 8 is not supported. | [R36-S1](<#r36-s1>) |
| **Browser upload and gallery**<br>`deployment.web` | C | Web uploader, public explorer, image viewer and administrative dashboard are part of the legacy application. | [R36-S2](<#r36-s2>), [R36-S5](<#r36-s5>), [R36-S6](<#r36-s6>) |
| **Downscale oversized images**<br>`editing.resize` | C | Maximum pixel dimensions downscale larger uploads; thumbnail dimensions and medium-image fixed width or height are configurable. | [R36-S5](<#r36-s5>) |
| **Image watermarking**<br>`editing.watermark` | C | Configure watermark image, position, relative size, opacity/margins, minimum image dimensions and applicable users/formats. | [R36-S5](<#r36-s5>) |
| **Web image formats**<br>`formats.web_images` | C | Documented upload formats are JPG, PNG, BMP, GIF and WebP; this does not establish RAW/video playback. | [R36-S5](<#r36-s5>) |
| **Single-key upload API v1**<br>`integration.api` | C | API v1 only uploads as guest, accepts file/URL/base64 sources and returns JSON, plain URL or redirect. Per-user attribution requires a custom route override; no dedicated API rate limiter beyond site flood limits. | [R36-S13](<#r36-s13>), [R36-S17](<#r36-s17>) |
| **Static-resource CDN and analytics hooks**<br>`integration.cdn_analytics` | O | Configure a pull-CDN URL for local static resources and analytics HTML in all views; neither is a claim of external original-image storage. | [R36-S10](<#r36-s10>) |
| **CLI API**<br>`integration.cli` | N | Release README explicitly lists CLI API as absent; HTTP upload API is separately available. | [R36-S2](<#r36-s2>), [R36-S17](<#r36-s17>) |
| **External comments**<br>`integration.comment_services` | O | Configure Disqus or arbitrary HTML/JavaScript comments on image views; not a native comments-store claim. | [R36-S10](<#r36-s10>) |
| **External storage servers**<br>`integration.object_storage` | N | 1.6.2 README explicitly removes External Storage Servers despite inherited docs/schema references. | [R36-S2](<#r36-s2>) |
| **External-editor popup uploader**<br>`integration.popup_uploader` | P | Embed PUP JavaScript in another site to upload without leaving its editor and automatically insert URL/HTML/BBCode/Markdown; supports named forum vendors, custom selectors, styles and dynamic editors. | [R36-S14](<#r36-s14>) |
| **ShareX capture/upload client**<br>`integration.sharex` | P | Separate ShareX application has a Chevereto destination or custom uploader using API v1; guest attribution remains the default. | [R36-S15](<#r36-s15>) |
| **Social-network login**<br>`integration.social_login` | N | Explicitly removed from this Free fork; inherited social-signup settings must not be counted. | [R36-S2](<#r36-s2>), [R36-S7](<#r36-s7>) |
| **Optional spam/CAPTCHA services**<br>`integration.spam_services` | O | Legacy docs configure Akismet, StopForumSpam and reCAPTCHA thresholds; provider availability was not tested. | [R36-S10](<#r36-s10>), [R36-S16](<#r36-s16>) |
| **Managed date folders or flat storage**<br>`library.auto_date_folders` | C | Configure nested YYYY/MM/DD or direct layout for future uploads; changing the setting does not relocate existing images. | [R36-S5](<#r36-s5>) |
| **Concurrent browser uploads**<br>`library.batch_upload` | C | Upload UI can be embedded on-page or routed to /upload and uses configurable parallel upload threads. | [R36-S5](<#r36-s5>) |
| **Bulk content importing**<br>`library.bulk_server_import` | N | Release README explicitly removes bulk content import, distinct from ordinary parallel browser uploads. | [R36-S2](<#r36-s2>), [R36-S5](<#r36-s5>) |
| **Duplicate-upload acceptance control**<br>`library.reject_duplicate_uploads` | C | Enable or disable accepting duplicate uploads; inspected settings alone do not establish perceptual matching or a general duplicate-review interface. | [R36-S5](<#r36-s5>) |
| **Upload filename policies**<br>`library.upload_naming` | C | Choose original name, randomized name, original-plus-random or encoded ID naming; original-name collisions are randomized. | [R36-S5](<#r36-s5>) |
| **Remote URL image upload**<br>`library.url_import` | C | URL upload is configurable and API accepts remote source URLs; 1.6.2 specifically fixes its SSRF handling. | [R36-S5](<#r36-s5>), [R36-S17](<#r36-s17>), [R36-S20](<#r36-s20>) |
| **Signup/flood email notifications**<br>`maintenance.notifications` | O | Configured mail can notify operators about signup or detected upload flooding. | [R36-S7](<#r36-s7>), [R36-S11](<#r36-s11>) |
| **Site image categories**<br>`metadata.categories` | C | Categories classify images and create category listings with name, URL key and description. | [R36-S9](<#r36-s9>) |
| **Configurable EXIF handling**<br>`metadata.exif_handling` | C | Site controls image EXIF handling and whether users can choose their own handling setting; no broad EXIF-write editor is inferred. | [R36-S5](<#r36-s5>) |
| **Manual NSFW display controls**<br>`privacy.nsfw_display_controls` | C | Hide or blur manually flagged NSFW content in listings, control inclusion in random results and lock user flag changes. This is not automatic moderation. | [R36-S8](<#r36-s8>), [R36-S2](<#r36-s2>) |
| **Original-name collision handling**<br>`safety.no_overwrite` | C | Documented original-filename upload mode randomizes colliding names rather than reusing the path. | [R36-S5](<#r36-s5>) |
| **Search images, albums and users**<br>`search.library_text` | C | Search route accepts image/album/user categories and query parameters; semantic/face/OCR search is not established. | [R36-S19](<#r36-s19>) |
| **Signup and profile controls**<br>`sharing.account_verification` | C | Configure email confirmation, minimum user age, profile-avatar/background size limits and whether users may delete their own content. | [R36-S7](<#r36-s7>) |
| **Expiring hosted images**<br>`sharing.expiring_uploads` | C | Enable expirable uploads that are removed after a selected date and configure automatic guest-upload deletion. This deletes hosted content, not merely a share token. | [R36-S5](<#r36-s5>) |
| **Guest uploads**<br>`sharing.guest_upload` | C | Enable guest uploading separately from authenticated uploads and apply a separate guest file-size maximum. | [R36-S5](<#r36-s5>) |
| **Expiring IP bans**<br>`sharing.ip_access_control` | C | Ban IPv4/IPv6 addresses or ranges with an optional expiration date. | [R36-S12](<#r36-s12>) |
| **Moderation**<br>`sharing.moderation` | N | Explicitly removed from Free; inherited manual sections for upload approval/ModerateContent do not establish available moderation. | [R36-S2](<#r36-s2>), [R36-S5](<#r36-s5>), [R36-S10](<#r36-s10>) |
| **Community accounts or personal mode**<br>`sharing.multiuser` | C | Site can use community or single-user personal mode; administrators can enable/disable public registration. | [R36-S4](<#r36-s4>), [R36-S7](<#r36-s7>) |
| **Password-gated albums**<br>`sharing.password_links` | C | Album route implements password gates, session password checks and optional CAPTCHA after failed attempts; owners/content managers bypass the gate. | [R36-S18](<#r36-s18>) |
| **Login-required private site**<br>`sharing.private_site` | C | Private website mode requires login and can force owner-only or link-accessible content policy per album. | [R36-S4](<#r36-s4>), [R36-S18](<#r36-s18>) |
| **Image/album links and embed codes**<br>`sharing.public_links` | C | Share viewer URLs and generated embed codes; IDs are encoded per installation and album sharing respects configured privacy. | [R36-S13](<#r36-s13>), [R36-S16](<#r36-s16>), [R36-S18](<#r36-s18>) |
| **Likes and followers**<br>`sharing.social_graph` | N | Explicitly removed from this fork. | [R36-S2](<#r36-s2>) |
| **File size and flood limits**<br>`sharing.upload_quotas` | C | Separate guest/user file-size limits are bounded by PHP settings; flood protection controls minute/hour/day/week/month upload thresholds. | [R36-S5](<#r36-s5>), [R36-S11](<#r36-s11>) |
| **Size ordering**<br>`sort.file_size` | C | Album/search listings support size ordering. | [R36-S18](<#r36-s18>), [R36-S19](<#r36-s19>) |
| **Date ordering**<br>`sort.upload_date` | C | Album/search listing routes support date sorting and ascending/descending order; EXIF capture-date semantics are not established. | [R36-S18](<#r36-s18>), [R36-S19](<#r36-s19>) |
| **Popularity ordering**<br>`sort.view_count` | C | Album/search listings support view-count sorting. | [R36-S18](<#r36-s18>), [R36-S19](<#r36-s19>) |

## Limitations and evidence gaps

- **explicit:** Archived with no future security/bug fixes, and PHP 8 unsupported. Successor Chevereto capabilities and subscriptions must be evaluated separately. ([R36-S1](<#r36-s1>), [R36-S3](<#r36-s3>))
- **explicit:** Official legacy docs overstate this reduced fork in places: social login, external storage and moderation are explicitly removed; release README also excludes banners/multilanguage and later ImageMagick, nested albums, 360 viewing, UI/sharing upgrades and CLI API. ([R36-S2](<#r36-s2>), [R36-S5](<#r36-s5>), [R36-S7](<#r36-s7>), [R36-S10](<#r36-s10>))
- **explicit:** API v1 is a single-key, guest-attributed upload bridge intended for one's own applications, not a full public account/album API. User-targeted upload needs a code override. ([R36-S13](<#r36-s13>), [R36-S17](<#r36-s17>))
- **coverage-gap:** Encoded identifiers and login/password gates are not E2EE or at-rest image encryption. No inspected evidence establishes recoverable deletion, operation journaling, face recognition, RAW processing, video playback or managed local-folder indexing. ([R36-S5](<#r36-s5>), [R36-S16](<#r36-s16>), [R36-S18](<#r36-s18>))
- **Coverage gap:** Legacy docs retain upstream-only settings; explicit release exclusions take precedence, with core album/API/search checked in full source.
- **Coverage gap:** No current successor/paid-service claims or runtime provider compatibility tests are included.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R36-S1

[Current legacy-project README](<https://github.com/rodber/chevereto-free/blob/ee91365ae837c6159e2377dfe74ad97bf6f58382/README.md>)
- Kind/ref: readme; ee91365ae837c6159e2377dfe74ad97bf6f58382
- Sections inspected: Complete README
- Establishes: Supersession, naming boundary and requirements.

### R36-S2

[1.6.2 edition-scope README](<https://github.com/rodber/chevereto-free/blob/1.6.2/README.md>)
- Kind/ref: readme; 1.6.2
- Sections inspected: Complete README, especially About this fork
- Establishes: Fork baseline, intended scale and explicit removed/missing features.

### R36-S3

[Project status](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/get-started/status.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete status page
- Establishes: Archived and unmaintained; no future updates.

### R36-S4

[Website settings](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/website.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: Public/private, personal/community, search/explore/random and branding.

### R36-S5

[Image-upload settings](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/image-upload.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page; removed moderation explicitly excluded using release README
- Establishes: Formats, upload controls, expiry, transforms, naming, EXIF and watermark options.

### R36-S6

[Listing settings](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/listings.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: Pagination/endless loading, lightbox, tiled/masonry layout and responsive columns.

### R36-S7

[User settings](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/users.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page; removed social-login setting excluded
- Establishes: Signups, email verification, deletion permissions, profile media and notifications.

### R36-S8

[Content display settings](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/content.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: Manual NSFW labeling display/blur controls, distinct from removed moderation.

### R36-S9

[Categories](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/categories.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: Site-wide category listings and configurable URL keys.

### R36-S10

[External-service settings](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/external-services.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page; moderation excluded by release scope
- Establishes: Optional spam services, CDN, CAPTCHA, comments and analytics.

### R36-S11

[Flood protection](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/flood-protection.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: Time-window upload limits and optional email alerts.

### R36-S12

[IP bans](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/settings/ip-bans.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: IPv4/IPv6 address/range bans and expiry.

### R36-S13

[API v1 manual](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/api/README.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete API guide and route-override workarounds
- Establishes: Upload-only single-key API, guest attribution and output formats.

### R36-S14

[Popup Upload Plugin](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/features/integrations/pup.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: External-editor upload button, automatic embed insertion and vendor/custom styling.

### R36-S15

[ShareX integration](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/features/integrations/sharex.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: Separate Windows capture client uses upload API.

### R36-S16

[Security reference](<https://github.com/rodber/chevereto-free-docs/blob/507d3b2c275c8372d770886472f7c87f0fd647a1/features/reference/security.md>)
- Kind/ref: manual; 507d3b2c275c8372d770886472f7c87f0fd647a1
- Sections inspected: Complete page
- Establishes: Encoded IDs, password hashing, CSRF, CAPTCHA and invalid-request throttling; not an audit.

### R36-S17

[Free upload API route](<https://github.com/rodber/chevereto-free/blob/ee91365ae837c6159e2377dfe74ad97bf6f58382/app/routes/route.api.php>)
- Kind/ref: code; ee91365ae837c6159e2377dfe74ad97bf6f58382
- Sections inspected: Complete route
- Establishes: Confirms v1 upload-only behavior and file/URL/base64 input.

### R36-S18

[Free album route](<https://github.com/rodber/chevereto-free/blob/ee91365ae837c6159e2377dfe74ad97bf6f58382/app/routes/route.album.php>)
- Kind/ref: code; ee91365ae837c6159e2377dfe74ad97bf6f58382
- Sections inspected: Complete route
- Establishes: Owner/link/password privacy, album editing tools, sorting and sharing.

### R36-S19

[Free search route](<https://github.com/rodber/chevereto-free/blob/ee91365ae837c6159e2377dfe74ad97bf6f58382/app/routes/route.search.php>)
- Kind/ref: code; ee91365ae837c6159e2377dfe74ad97bf6f58382
- Sections inspected: Complete route
- Establishes: Images/albums/users search and list ordering.

### R36-S20

[1.6.2 release](<https://github.com/rodber/chevereto-free/releases/tag/1.6.2>)
- Kind/ref: release; 1.6.2
- Sections inspected: Complete release notes
- Establishes: Remote-URL upload SSRF fix and dependency updates.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
