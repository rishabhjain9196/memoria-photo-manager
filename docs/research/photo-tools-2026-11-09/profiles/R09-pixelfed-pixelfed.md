# R09 — pixelfed/pixelfed

[Repository](<https://github.com/pixelfed/pixelfed>) · 7,141 stars at the frozen snapshot · gallery-sharing · Not archived

**Purpose:** Federated photo/video social publishing server with chronological feeds, media posts, account controls and configurable federation/import features; not a private local photo catalogue.

**Deployment:** Self-hosted PHP web application; Docker Compose recommended since September 2026; MySQL 8+ or MariaDB 11+ supported; PostgreSQL 14+ best-effort/not recommended; Browser/mobile-browser clients and OAuth/API integrations

**Storage:** Uploaded post media and account/post records are managed on the instance; optional object storage supports S3-compatible services and remote-media caches. Upload resizing/optimization means it should not be assumed to preserve archival originals.

**Privacy/network behavior:** Instance operators host content and federation distributes eligible posts to other servers. Private accounts constrain visibility to approved followers but are not E2EE. Optional push gateway and video P2P tracker/STUN are additional external services. Hosting choices and administrator configuration materially affect privacy and availability.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** v0.15.2 (2026-10-21T23:43:09Z)
**Repository pushed at:** 2026-11-09T12:23:06Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [6e924653ae94](<https://github.com/pixelfed/pixelfed/commit/6e924653ae94aa7a5b7e188e7912eb8fd88f2948>).
**Product lineage:** pixelfed/pixelfed.

## Maturity and availability caveats

- Pinned dev 6e924653ae94aa7a5b7e188e7912eb8fd88f2948; latest release v0.15.2, 2026-10-21, includes PHP/CA updates and urges backups before upgrade.
- Current development may differ from the stable release; built-in help contains legacy experimental labels and several unfinished pages. Configuration defaults are not promises about any particular instance.
- New Nuxt web UI is described as ongoing work in release notes, not a completed replacement.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **HLS video streaming**<br>`browse.hls_streaming` | O | Optional HLS requires FFmpeg and defaults off; configurable bitrate governs generated streams. | [R09-S11](<#r09-s11>) |
| **Chronological social feeds**<br>`browse.social_timelines` | C | Home shows followed accounts, Public shows local users and Network shows remote unmoderated content; these are chronological post feeds, not capture-date photo-library timelines. | [R09-S3](<#r09-s3>) |
| **Maintained Docker deployment**<br>`deployment.docker` | C | README recommends maintained Docker images/Compose; stable release documents image rebuild and database migration workflow. | [R09-S1](<#r09-s1>), [R09-S14](<#r09-s14>) |
| **Selectable translated web interface**<br>`deployment.localization` | C | Language chooser loads the locale manifest, displays language/native names and changes the user's VueI18n locale through the language API. Listed choices include Arabic, French, German, Japanese and Chinese variants; French navigation strings are verified. Some chooser text remains English, so full translation completeness is not claimed. | [R09-S15](<#r09-s15>), [R09-S16](<#r09-s16>), [R09-S17](<#r09-s17>) |
| **New Nuxt web UI**<br>`deployment.nuxt_ui` | R | v0.15.2 notes continued refactoring toward a new Nuxt interface, not a completed shipped replacement. | [R09-S14](<#r09-s14>) |
| **Independent social instance**<br>`deployment.selfhosted` | C | Operators run their own PHP/database instance, with Docker Compose now recommended and conventional installation still supported. | [R09-S1](<#r09-s1>) |
| **Desktop/mobile browser UI**<br>`deployment.web` | C | Help provides distinct desktop and mobile-browser post-composition entry points. | [R09-S2](<#r09-s2>) |
| **Composition photo filters**<br>`editing.filters` | C | Help describes choosing a filter in media options, labels it experimental and explicitly says filters are not federated. | [R09-S2](<#r09-s2>) |
| **Upload resizing and optimization**<br>`editing.resize` | C | Image optimization/resizing defaults on with configurable quality (80 default); upload file-size/account quotas are also configurable. | [R09-S12](<#r09-s12>) |
| **Video optimization**<br>`editing.video_transcode` | C | Configuration documents video upload resizing/optimization enabled by default; accepted video MIME types remain instance-dependent. | [R09-S12](<#r09-s12>), [R09-S2](<#r09-s2>) |
| **Developer API and OAuth**<br>`integration.api` | C | README links official API documentation; config enables OAuth and application registration with rate limits, while personal access tokens are separately optional. | [R09-S1](<#r09-s1>), [R09-S9](<#r09-s9>), [R09-S12](<#r09-s12>) |
| **Atom syndication**<br>`integration.atom_feeds` | C | Federation configuration independently enables Atom feeds by default. | [R09-S10](<#r09-s10>) |
| **Cloud/object media storage**<br>`integration.object_storage` | O | Can store uploaded media on S3/Spaces/Rackspace-compatible backends and separately opt into caching remote federation media there; local media may be deleted after cloud upload. | [R09-S11](<#r09-s11>), [R09-S12](<#r09-s12>) |
| **Peer-assisted video distribution**<br>`integration.video_p2p` | O | Optional P2P video requires HLS plus FFmpeg and defaults off; config identifies an external WebTorrent tracker and Google STUN server. | [R09-S11](<#r09-s11>) |
| **Instagram export import**<br>`library.instagram_import` | O | Imports Instagram JSON ZIP data including photos, captions and hashtags. Current dedicated config defaults to 1,000 posts, permits video/WebP, excludes archived posts and supports administrator/account-age/follower eligibility restrictions. | [R09-S5](<#r09-s5>), [R09-S13](<#r09-s13>) |
| **Hide posts in archive**<br>`library.post_archive` | C | Archived posts become unavailable for viewing/interactions and can be unarchived via profile Archives; help warns remote interactions may not be received while archived. | [R09-S2](<#r09-s2>) |
| **Optional push gateway**<br>`maintenance.notifications` | O | Instance config supports the push.pixelfed.net gateway with an API key; notification garbage collection has separate configurable retention. | [R09-S9](<#r09-s9>) |
| **Per-media alternative descriptions**<br>`metadata.accessibility_descriptions` | C | Help documents media descriptions for visually impaired users, federated where supported. Help labels the composing UI experimental; current config sets an alt-text length limit of 1,000. | [R09-S2](<#r09-s2>), [R09-S12](<#r09-s12>) |
| **Post captions**<br>`metadata.comments` | C | Optional captions are attached during composition; maximum length is configured by the instance (500 default), rather than embedded IPTC writeback. | [R09-S2](<#r09-s2>), [R09-S12](<#r09-s12>) |
| **Optional EXIF database storage**<br>`metadata.exif_catalogue` | O | MEDIA_EXIF_DATABASE defaults false; enabling stores EXIF in the database, without proving an end-user EXIF editing interface. | [R09-S11](<#r09-s11>) |
| **Hashtag labeling**<br>`metadata.tags` | C | Hashtags in captions/comments link to topic pages; help documents up to 30 hashtags per post/comment and public-post discoverability. | [R09-S4](<#r09-s4>) |
| **Temporary account deactivation**<br>`privacy.disable_account` | C | Disabling hides profile, photos, comments and likes until login reactivates the account; permanent deletion is separate and may have an admin-configured grace period. | [R09-S6](<#r09-s6>), [R09-S12](<#r09-s12>) |
| **Two-factor authentication**<br>`privacy.two_factor_auth` | C | Profile security help explicitly directs users to enable 2FA in security settings. | [R09-S6](<#r09-s6>) |
| **Account activity history**<br>`safety.account_activity_log` | C | Security help recommends reviewing Account Log for suspicious activity. This is account history, not a durable pre-operation crash-recovery file journal. | [R09-S6](<#r09-s6>) |
| **User keyword filters**<br>`safety.keyword_filters` | C | Current configuration supports custom content filters with bounded keywords, scan length, regex size and creation/update rates; default limits include 20 filters and 10 keywords per filter. | [R09-S9](<#r09-s9>) |
| **Restricted child accounts**<br>`safety.parental_controls` | O | When administrators enable the feature, parents create linked child accounts and choose posting, commenting, liking/sharing and federation permissions; configured child-count limits apply. | [R09-S8](<#r09-s8>), [R09-S9](<#r09-s9>) |
| **Mute/block/report controls**<br>`safety.social_moderation` | C | Accounts can be muted/blocked from feeds; direct messages can be reported or deleted. Config bounds user mutes/blocks/domain blocks. | [R09-S3](<#r09-s3>), [R09-S7](<#r09-s7>), [R09-S9](<#r09-s9>) |
| **Hashtag search**<br>`search.tags` | C | Search bar locates hashtags; public tagged posts can appear in discovery/search pages. | [R09-S4](<#r09-s4>) |
| **Follower/account migration**<br>`sharing.account_migration` | O | Migration uses account aliases and compatible Pixelfed/Mastodon migration extensions. Post migration is documented for Pixelfed v0.11.9+ only when server-enabled; completion can take hours. | [R09-S6](<#r09-s6>), [R09-S10](<#r09-s10>) |
| **Enable/disable replies per post**<br>`sharing.comment_controls` | C | Post menu can enable or disable comments/replies from desktop or mobile browser. | [R09-S2](<#r09-s2>) |
| **Private-message interface**<br>`sharing.direct_messages` | C | Direct supports photos/videos, text, feed posts, profiles, hashtags and locations; unsolicited messages may enter a filtered inbox. Help says direct media does not appear on hashtag/location pages or share onward through Pixelfed to other sites. | [R09-S7](<#r09-s7>) |
| **ActivityPub federation**<br>`sharing.federation` | O | Instance-configured ActivityPub supports inbox/outbox/shared inbox and remote follows; network timeline can show other servers' content. The config flag defaults off, so federation depends on deployment. | [R09-S1](<#r09-s1>), [R09-S3](<#r09-s3>), [R09-S10](<#r09-s10>) |
| **Subscribe to hashtag feeds**<br>`sharing.follow_hashtags` | C | Following a hashtag adds its photos/videos to feed; help gives follow limits of 20/hour and 100/day. | [R09-S4](<#r09-s4>) |
| **Federated follower/block synchronization**<br>`sharing.follower_block_sync` | O | Configured federation supports signed follower-collection synchronization for followers-only delivery and block-list synchronization with cooldown/page limits. | [R09-S10](<#r09-s10>) |
| **Account mentions**<br>`sharing.mentions` | C | Help documents tagging/mentioning up to five profiles in a post or comment; no automatic face recognition is implied. | [R09-S2](<#r09-s2>) |
| **Multi-image/video posts**<br>`sharing.multi_media_posts` | C | Composer accepts several media files together or individually; per-post count is instance-configured (default max_album_length is four). | [R09-S2](<#r09-s2>), [R09-S12](<#r09-s12>) |
| **Approved-follower visibility**<br>`sharing.private_accounts` | C | Private Account setting limits photo/video visibility to approved followers and prompts about existing followers/new requests; not an encryption feature. | [R09-S6](<#r09-s6>) |
| **Embeddable profiles and posts**<br>`sharing.profile_post_embeds` | C | Current instance configuration separately enables profile and post embeds by default; exact embed UI is not established by the unfinished help page. | [R09-S9](<#r09-s9>) |
| **Instance registration policies**<br>`sharing.registration_policy` | C | Config controls open registration, email verification, maximum accounts and invites; curated registration and user invitations are optional modes. | [R09-S9](<#r09-s9>), [R09-S12](<#r09-s12>) |
| **Stories availability**<br>`sharing.stories` | ? | An off-by-default STORIES_ENABLED flag exists, but built-in Stories help is unfinished; inspected evidence does not establish lifecycle/privacy semantics or current shipped UI. | [R09-S9](<#r09-s9>) |
| **Unlisted publishing**<br>`sharing.unlisted_posts` | C | Unlisted posts do not appear in public timelines, as explicitly documented in timeline help. | [R09-S3](<#r09-s3>) |

## Limitations and evidence gaps

- **explicit:** Username changes are explicitly unsupported in profile help; migration support varies by server/version and does not guarantee every post transfers. ([R09-S6](<#r09-s6>))
- **explicit:** Media formats, quotas, post size, import and federation are administrator-configured. Default MIME list contains JPEG/PNG/GIF even though video composition is documented. ([R09-S2](<#r09-s2>), [R09-S12](<#r09-s12>), [R09-S13](<#r09-s13>))
- **coverage-gap:** Post filters are documented as experimental and not federated. Several help pages are unfinished, so feature completeness cannot be inferred from navigation labels. ([R09-S2](<#r09-s2>), [R09-S9](<#r09-s9>))
- **coverage-gap:** Private visibility and direct messages are not evidence of E2EE. RAW archival handling, exact/perceptual duplicates, face recognition, maps, file-operation rollback and sidecar metadata are not established. ([R09-S1](<#r09-s1>), [R09-S6](<#r09-s6>), [R09-S7](<#r09-s7>), [R09-S12](<#r09-s12>))
- **Coverage gap:** Official features web page returned no substantive body; pinned built-in help, configuration and release notes used instead.
- **Coverage gap:** Some help text appears legacy/experimental; stories and Nuxt replacement are not counted as present core features.
- **Coverage gap:** No live instance testing.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R09-S1

[README](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/README.md>)
- Kind/ref: readme; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Complete README
- Establishes: Federated photo sharing, server requirements, Docker recommendation and API documentation links.

### R09-S2

[Sharing photos and videos help](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/views/site/help/sharing-media.blade.php>)
- Kind/ref: manual; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Complete rendered textual help, with commented unfinished questions excluded
- Establishes: Composition, captions, filters, alt descriptions, comment controls and archive.

### R09-S3

[Timelines help](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/views/site/help/timelines.blade.php>)
- Kind/ref: manual; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire help
- Establishes: Chronological home/public/network feeds, mute/block and unlisted posts.

### R09-S4

[Hashtags help](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/views/site/help/hashtags.blade.php>)
- Kind/ref: manual; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire help
- Establishes: Searchable hashtags, hashtag-follow subscriptions and limits.

### R09-S5

[Instagram import help](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/views/site/help/import.blade.php>)
- Kind/ref: manual; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire help
- Establishes: Instagram JSON archive import and server-dependent eligibility/limits.

### R09-S6

[Profile, privacy and migration help](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/views/site/help/your-profile.blade.php>)
- Kind/ref: manual; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Complete active help text
- Establishes: Private accounts, 2FA, account log, migration and account disabling/deletion.

### R09-S7

[Direct messages help](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/views/site/help/dm.blade.php>)
- Kind/ref: manual; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire help
- Establishes: Message content, filtered inboxes, delete and reporting.

### R09-S8

[Parental controls help](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/views/site/help/parental-controls.blade.php>)
- Kind/ref: manual; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire help
- Establishes: Server-enabled child account controls and per-child federation restrictions.

### R09-S9

[Instance configuration](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/config/instance.php>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire file
- Establishes: Feeds, embeds, content filters, registration, parental controls and push gateway.

### R09-S10

[Federation configuration](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/config/federation.php>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire file
- Establishes: ActivityPub services, follower/block synchronization, feeds and migration.

### R09-S11

[Media configuration](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/config/media.php>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire file
- Establishes: Optional EXIF database, remote/cloud cache and HLS/P2P.

### R09-S12

[Application configuration](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/config/pixelfed.php>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: All configuration entries and descriptive comments
- Establishes: Media/account limits, image/video optimization, cloud storage, OAuth and post composition limits.

### R09-S13

[Import configuration](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/config/import.php>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire file
- Establishes: Current Instagram enablement, video/WebP, post limits and eligibility settings.

### R09-S14

[v0.15.2 release notes](<https://github.com/pixelfed/pixelfed/releases/tag/v0.15.2>)
- Kind/ref: release; v0.15.2
- Sections inspected: Complete release body
- Establishes: Stable build updates, timeline changes, upgrade warnings and ongoing UI rewrite.

### R09-S15

[Interface language chooser](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/resources/assets/components/Language.vue>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire component
- Establishes: User-selectable locale list, language-change API and live VueI18n locale update.

### R09-S16

[UI locale manifest](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/lang/locales.json>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire manifest
- Establishes: Named locale options including native language names and regional variants; listing does not measure translation completeness.

### R09-S17

[French navigation translations](<https://github.com/pixelfed/pixelfed/blob/6e924653ae94aa7a5b7e188e7912eb8fd88f2948/lang/fr-FR/navmenu.php>)
- Kind/ref: code; 6e924653ae94aa7a5b7e188e7912eb8fd88f2948
- Sections inspected: Entire translation file
- Establishes: Actual translated search, navigation, profile, settings, messaging and compose labels.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
