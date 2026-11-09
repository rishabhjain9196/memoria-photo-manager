# R04 — ente/ente

[Repository](<https://github.com/ente/ente>) · 30,012 stars at the frozen snapshot · library-cloud-client · Not archived

**Purpose:** Ente Photos combines end-to-end-encrypted backup and sharing with cross-platform clients, optional on-device AI and a mobile account-free local gallery. Auth and Locker product features are excluded.

**Deployment:** iOS and Android Photos apps, including alternative Android distributions; Native macOS/Windows/Linux Photos desktop clients; Photos and public-album web applications; Photos CLI; Self-hosted Museum/server and web applications with Docker Compose

**Storage:** Cloud mode preserves uploaded originals and stores encrypted metadata, album membership and derived indexes separately. Reused assets have logical album references, not OS symlinks. Desktop/CLI export creates album folders plus Takeout-style JSON sidecars and can duplicate one asset across multiple exported albums. Mobile gallery mode reads device media without an account. Self-hosting requires configured database and object storage.

**Privacy/network behavior:** Originals, descriptive metadata, face/search indexes and shared interactions are encrypted before server storage; ML queries/inference run on-device. Public-link keys reside in the URL fragment, so anyone receiving the link can decrypt its contents and metadata. Password links add server access control, not new encryption. Map tiles/model provisioning/backup/sharing need network services; local gallery and already-indexed search have offline operation. Hosted replication policies do not automatically apply to self-hosting.

**License metadata:** AGPL-3.0. Individual modules, models and editions may have additional terms; this is not a license audit.

**Latest GitHub release at snapshot:** locker-v1.0.12 (2026-11-09T08:15:10Z)
**Repository pushed at:** 2026-11-09T08:16:42Z (not proof of meaningful maintenance).
**Pinned default-branch commit:** [52b907b57018](<https://github.com/ente/ente/commit/52b907b57018958468615f4036851c196291012f>).
**Product lineage:** ente/ente.

## Maturity and availability caveats

- Scope is Ente Photos plus shared account/server capabilities applicable to Photos. GitHub stars are for the entire ente/ente monorepo, not Photos alone.
- Pinned 52b907b57018958468615f4036851c196291012f. Manifest latest release locker-v1.0.12 belongs to another product and is not used as a Photos version.
- Inspected Photos changelog records mobile v1.3.69/v1.3.68 in November 2026 and desktop v1.7.31 in October 2026; pinned documentation may be ahead of individual client packages.
- Hosted service offers 10 GB free storage per README, with paid capacity/family benefits; self-hosting is distinct. Video streaming is explicitly beta.
- Several guides simplify desktop face management as view-only, while the detailed face guide documents naming/merging and merge-history undo. Fine-grained incorrect-face editing remains mobile-only; this distinction is retained.

## Complete researched feature inventory

Status: C = core; O = optional configuration/module; P = plugin; $ = paid; R = roadmap; ? = unclear; N = explicitly unsupported. Roadmap/unclear/unsupported do not count as present.

| Feature | Status | Evidence-backed detail | Sources |
|---|---|---|---|
| **Automatic person groups**<br>`ai.face_clustering` | O | Automatically groups similar faces after indexing. Mobile mixed-group re-evaluation applies stricter settings for difficult cases such as babies. | [R04-S6](<#r04-s6>) |
| **Merge, de-merge and reject faces**<br>`ai.face_corrections` | O | Mobile supports de-merge, Not this person, ignored-group restore and cover selection; desktop has naming/merge-history undo/ignore but not individual incorrect-face editing or cover selection. | [R04-S6](<#r04-s6>) |
| **Local face detection**<br>`ai.face_detection` | O | Opt-in analysis detects face regions as the first stage of recognizing people; web does not support this feature. | [R04-S6](<#r04-s6>) |
| **Named people**<br>`ai.face_naming` | O | Mobile/desktop assign names to groups and make them searchable; selecting an existing named identity merges groups. | [R04-S6](<#r04-s6>) |
| **Cross-photo identity matching**<br>`ai.face_recognition` | O | Face groups find all photos containing the same people across albums; identity naming and corrective operations remain local and encrypted on sync. | [R04-S6](<#r04-s6>), [R04-S7](<#r04-s7>) |
| **Optional client-side ML**<br>`ai.local_inference` | O | Face and semantic indexing runs on mobile/desktop. Signed-in mode indexes backed-up media only, whereas signed-out gallery mode can index permitted local files. | [R04-S7](<#r04-s7>), [R04-S15](<#r04-s15>) |
| **On-demand text selection**<br>`ai.ocr` | C | Mobile long-press recognizes/copies text in photos/Live Photos using on-device OCR. Android downloads models on first use; supported languages vary, and Trash/guest views and video are excluded. | [R04-S11](<#r04-s11>) |
| **People-driven auto-add albums**<br>`albums.auto_add_people` | O | Mobile config adds existing/new owned uploads containing selected named people after local face indexing, including editable collaborative albums; Favorites/Uncategorized are excluded and disabling ML pauses updates. | [R04-S21](<#r04-s21>) |
| **Flat folder-to-album mapping**<br>`albums.folder_mapping` | C | Upload/watch chooses one flattened album or separate albums named by leaf folders. Equal leaf names can merge into one album and empty folders are ignored. | [R04-S3](<#r04-s3>), [R04-S4](<#r04-s4>) |
| **Virtual cloud albums**<br>`albums.manual` | C | Signed-in users create albums with covers/descriptions and reuse one original across albums through references; local account-free mode does not provide Ente albums. | [R04-S3](<#r04-s3>), [R04-S9](<#r04-s9>), [R04-S15](<#r04-s15>) |
| **Manual drag ordering**<br>`albums.manual_order` | N | FAQ explicitly says photos/videos cannot currently be dragged into a custom album order; available Sort by options must be used instead. | [R04-S3](<#r04-s3>) |
| **Nested albums**<br>`albums.nested` | N | FAQ explicitly states albums are flat and cannot be nested, even when uploaded folders are nested. | [R04-S3](<#r04-s3>) |
| **Scheduled photo habits**<br>`albums.photo_rituals` | C | Mobile rituals link an owned album to weekdays/reminders and track capture-date-based scheduled-day streaks. Ritual camera supports up to 20 photos/session, not video; ritual settings stay local although the album syncs. | [R04-S26](<#r04-s26>) |
| **Uncategorized catch-all**<br>`albums.uncategorized_safety` | C | Removing the last album membership or watched-folder file retains the asset in Uncategorized. Cleaning removes only entries also present in an album the user owns. | [R04-S3](<#r04-s3>) |
| **Encrypted video streaming beta**<br>`browse.encrypted_hls` | O | Optional stream generation creates 720p H.264 at 2 Mbps in encrypted HLS with encrypted playlist, enabling seeking without downloading whole originals. Stream storage is quota-exempt only during beta. | [R04-S2](<#r04-s2>) |
| **Photo/video viewer**<br>`browse.fullscreen` | C | Local and signed-in mobile modes provide a full-screen photo/video viewer with swiping and pinch zoom. | [R04-S15](<#r04-s15>) |
| **Square and proportional layouts**<br>`browse.grid` | C | Mobile gallery chooses square tiles or original-proportion mosaic; pinch adjusts density and crosses into mosaic without modifying images. | [R04-S3](<#r04-s3>), [R04-S23](<#r04-s23>) |
| **HLS video streaming beta**<br>`browse.hls_streaming` | O | Optional beta streaming generates 720p H.264 at 2 Mbps with an HLS playlist so mobile and web/desktop clients can begin playback and seek without first downloading the complete original. A stream must have been generated; unsupported or failed streams can fall back to original-file playback/download. Streams are encrypted and quota-exempt only during beta. | [R04-S2](<#r04-s2>) |
| **Desktop/web shortcuts**<br>`browse.keyboard` | C | Search focus, range/additive/select-all selection and delete shortcuts are documented; slideshow uses arrows and Space. | [R04-S2](<#r04-s2>), [R04-S3](<#r04-s3>) |
| **On-this-day and curated memories**<br>`browse.memories` | C | Mobile memories/widgets show On This Day, Past Years and smart curated moments; notifications can exclude a person by hiding them from memories. | [R04-S2](<#r04-s2>), [R04-S15](<#r04-s15>) |
| **Person growth timelines**<br>`browse.person_memory_lane` | O | Mobile Memory Lane requires at least two years with four eligible person photos per year; known ages below three, hidden items and ignored faces are excluded. Timelines include age/year captions and public-link presentation. | [R04-S20](<#r04-s20>) |
| **Album slideshows**<br>`browse.slideshow` | C | Mobile and desktop play photos/Live Photos, not videos, with 5-second through 10-minute intervals, ordered/shuffled playback and black/blurred backgrounds. Mobile can combine albums; desktop plays one album. | [R04-S3](<#r04-s3>) |
| **Capture-date timeline**<br>`browse.timeline` | C | Device gallery presents photos chronologically; cloud metadata date selection uses embedded metadata, Takeout sidecar, filename inference then upload-time fallback. | [R04-S15](<#r04-s15>), [R04-S5](<#r04-s5>) |
| **Original video playback**<br>`browse.video_playback` | C | Clients view videos, but browser-unsupported codecs may require original-file download instead of streaming. | [R04-S4](<#r04-s4>), [R04-S15](<#r04-s15>) |
| **Pinch zoom and swiping**<br>`browse.zoom` | C | Gallery-mode comparison explicitly includes pinch-to-zoom and swiping between media; collage framing also uses pinch/drag. | [R04-S15](<#r04-s15>), [R04-S17](<#r04-s17>) |
| **Free device space after backup**<br>`cleanup.backed_up_device_copies` | C | Shows reclaimable size and removes backed-up local copies after confirmation, retaining Ente originals; the automated action covers all backed-up items rather than an arbitrary selective subset. | [R04-S3](<#r04-s3>), [R04-S4](<#r04-s4>) |
| **Owner-approved deletion suggestions**<br>`cleanup.collaborative_delete_suggestions` | C | On mobile, album owners/admins remove others' selected photos from the album and send a deletion suggestion; actual photo owners accept/delete or reject/keep in their queue. | [R04-S19](<#r04-s19>) |
| **Android Photos client**<br>`deployment.android` | C | Photos app supports Android and alternative distribution channels including F-Droid, with local gallery and encrypted backup modes. | [R04-S1](<#r04-s1>), [R04-S15](<#r04-s15>) |
| **Docker Compose setup**<br>`deployment.docker` | C | Quickstart provisions containers; documented minimum is one CPU core and 1 GB RAM. Production configuration/backup is the operator's responsibility. | [R04-S16](<#r04-s16>) |
| **iOS Photos client**<br>`deployment.ios` | C | iOS app supports gallery/backup, editors and local AI, subject to mobile permission/background constraints. | [R04-S1](<#r04-s1>), [R04-S4](<#r04-s4>), [R04-S15](<#r04-s15>) |
| **Linux desktop Photos**<br>`deployment.linux` | C | Native Photos desktop release supports Linux, including documented RAW-preview improvements and export/ML workflows. | [R04-S1](<#r04-s1>), [R04-S23](<#r04-s23>) |
| **Translated Photos interface**<br>`deployment.localization` | C | Photos mobile v1.3.66 explicitly adds Korean UI language support and updates translations across sharing, account recovery, cleanup and onboarding; v1.3.67 restores missing translations. This is interface localization, separate from Magic Search query-language support; equal language coverage across clients is not asserted. | [R04-S23](<#r04-s23>) |
| **macOS desktop Photos**<br>`deployment.macos` | C | Desktop Photos supports local AI/watch/export and macOS device-authentication app lock. | [R04-S1](<#r04-s1>), [R04-S27](<#r04-s27>) |
| **Self-hosted Photos backend**<br>`deployment.selfhosted` | C | Open-source production server can be deployed with configurable endpoints/buckets, Photos web and a separate public Albums application; clients can connect to it. | [R04-S16](<#r04-s16>) |
| **Photos and album web clients**<br>`deployment.web` | C | Web client supports uploads, basic search, metadata and sharing; public album viewers do not need an account. Web ML/face recognition is not available. | [R04-S1](<#r04-s1>), [R04-S7](<#r04-s7>), [R04-S8](<#r04-s8>) |
| **Windows desktop Photos**<br>`deployment.windows` | C | Native desktop client supports watch folders, local AI and continuous export; it is not the independent Auth client. | [R04-S1](<#r04-s1>), [R04-S2](<#r04-s2>), [R04-S4](<#r04-s4>) |
| **Exact duplicate cleanup**<br>`duplicates.exact_hash` | C | Manual mobile/desktop cleanup recognizes content hashes and retains one underlying file with references in each album; independently generated thumbnails can differ without changing identity. | [R04-S3](<#r04-s3>), [R04-S4](<#r04-s4>), [R04-S9](<#r04-s9>) |
| **Similar-image keeper defaults**<br>`duplicates.keeper_selection` | O | Review can override deletion choices. Favorites are never auto-selected; other files favor the largest size, with filename as tie-breaker, not resolution or EXIF completeness. | [R04-S3](<#r04-s3>) |
| **Mobile near-image cleanup**<br>`duplicates.similar_images` | O | ML Similar images groups visually related but nonidentical photos for mobile review; desktop lacks this dedicated cleanup feature. | [R04-S3](<#r04-s3>) |
| **Review similar groups before removal**<br>`duplicates.visual_review` | O | Mobile Similar images requires reviewing groups and confirming which copies to keep/delete; logical album references help avoid removing every representation of a scene from albums. | [R04-S3](<#r04-s3>) |
| **Filters and color adjustments**<br>`editing.adjustments` | C | Mobile editor offers filters, brightness/contrast/saturation/exposure/hue/temperature/tint/fade. Recent changelog explicitly removes Sharpness and Luminance. | [R04-S5](<#r04-s5>), [R04-S23](<#r04-s23>) |
| **Draw, text and stickers**<br>`editing.annotations` | C | Mobile editor draws and layers text/stickers with font/color/background/alignment controls and per-object edit/duplicate/delete; text becomes image pixels rather than searchable caption metadata. | [R04-S5](<#r04-s5>) |
| **Two-to-six-photo mobile collages**<br>`editing.collage` | C | Choose layouts, swap tiles by long-press/tap, pinch/drag framing and save to device gallery; no videos or web/desktop creation. | [R04-S17](<#r04-s17>) |
| **Photo crop and straighten**<br>`editing.crop` | C | Mobile editor crops and straightens arbitrary tilts; saved result is a separate copy. | [R04-S5](<#r04-s5>), [R04-S23](<#r04-s23>) |
| **Native accelerated video export**<br>`editing.hardware_encoding` | C | Native export uses hardware acceleration where supported; software FFmpeg fallback runs when native export fails. | [R04-S12](<#r04-s12>) |
| **Rotate/flip photos**<br>`editing.rotate_flip` | C | JPEG-only rotation/flip edits avoid re-encoding; other edits may re-encode. Originals remain untouched. | [R04-S5](<#r04-s5>) |
| **Video framing and orientation**<br>`editing.video_crop_rotate` | C | Mobile crops freely or to 1:1, 9:16, 16:9, 3:4 or 4:3 and rotates in 90-degree steps, accounting for original orientation. | [R04-S12](<#r04-s12>) |
| **New-copy MP4 export**<br>`editing.video_transcode` | C | Native AVFoundation/Media3 export produces H.264 MP4, with FFmpeg H.264/AAC fallback; iOS simple trims can use passthrough. New copy preserves date/location/album membership where available. | [R04-S12](<#r04-s12>) |
| **Trim single videos**<br>`editing.video_trim_join` | C | Mobile editor sets start/end with preview and a one-second minimum; this documents trimming only, not joining. Each export is a finalized new file, not a saved edit recipe. | [R04-S12](<#r04-s12>) |
| **Ultra HDR thumbnail metadata**<br>`formats.hdr_thumbnails` | C | Desktop v1.7.30 preserves HDR gain maps in Ultra HDR JPEG thumbnails generated on Linux/Windows; this is narrower than a universal HDR rendering guarantee. | [R04-S23](<#r04-s23>) |
| **JPEG XL preview availability**<br>`formats.jpegxl` | ? | FAQ explicitly says JPEG XL may upload while lacking a thumbnail/preview; reliable viewing across clients is not established. | [R04-S4](<#r04-s4>) |
| **Live Photos viewing and utilities**<br>`formats.live_photos` | C | Live Photos participate in album slideshows and photo OCR; differing video-frame thumbnail extraction does not affect exact duplicate identity. | [R04-S3](<#r04-s3>), [R04-S4](<#r04-s4>), [R04-S11](<#r04-s11>) |
| **Broad image/video original backup**<br>`formats.media_backup` | C | Accepts image/* and video/* originals up to 10 GB, without upload compression; backup eligibility does not guarantee every client can thumbnail/play the format. | [R04-S4](<#r04-s4>) |
| **Limited RAW previews and backup**<br>`formats.raw` | C | Backup FAQ explicitly calls RAW support limited; desktop v1.7.30 improves RAF/ORF/PEF/NRW/SRW previews on Linux/Windows. Universal camera compatibility is not claimed. | [R04-S4](<#r04-s4>), [R04-S23](<#r04-s23>) |
| **Photo/album map**<br>`geo.map` | C | View all GPS-tagged media or one album on the map across clients; location search is local and coordinates encrypted. Desktop changelog explicitly references OpenStreetMap tile loading. | [R04-S10](<#r04-s10>), [R04-S23](<#r04-s23>) |
| **Custom radius-defined places**<br>`geo.radius_location_tags` | C | Create labels such as Home/Office by choosing a center and radius; the app groups matching photos locally, with encrypted location labels. | [R04-S10](<#r04-s10>) |
| **Public third-party Photos API**<br>`integration.api` | N | Advanced FAQ explicitly says there is no public third-party API and directs automation users to CLI; open server source is not equivalent to a supported public API. | [R04-S2](<#r04-s2>) |
| **Encrypted-album slideshow casting**<br>`integration.cast` | C | Cast sends an album slideshow to Chromecast or any Internet-connected screen using PIN pairing; multiple sessions can be managed. It does not mirror the photo currently scrolled on the phone. | [R04-S2](<#r04-s2>) |
| **Photos export CLI**<br>`integration.cli` | C | CLI exports selected albums or individual files and supports scheduled local/NAS backups; restarting export resumes. It is not a two-way filesystem sync tool. | [R04-S2](<#r04-s2>) |
| **Mobile memories/album/people widgets**<br>`integration.home_widgets` | C | iOS/Android widgets show configured albums, memories or ML-selected people, usually refresh about every 15 minutes and require account features for album/people widgets. | [R04-S2](<#r04-s2>), [R04-S15](<#r04-s15>) |
| **QR actions inside photos**<br>`integration.qr_detection` | C | Mobile detects multiple QR codes on-device and offers open/copy/share plus supported UPI payment actions; scanning alone does not upload QR contents. | [R04-S22](<#r04-s22>) |
| **Timeline decluttering archive**<br>`library.archive` | C | Archive removes items from home timeline/memories while retaining search and album visibility; no extra authentication is required. | [R04-S3](<#r04-s3>) |
| **Continuous one-way local backup**<br>`library.continuous_export` | C | Desktop continuous export downloads new items while running; CLI repeated/scheduled exports incrementally update a disk or mounted NAS. Local edits do not upload back. | [R04-S2](<#r04-s2>) |
| **Skip existing uploads**<br>`library.deduplicate_import` | C | Same-album duplicates skip; cross-album matches add logical references without re-upload. Mobile uses content hash; web/desktop require matching hash and filename. | [R04-S9](<#r04-s9>) |
| **Browse device folders in place**<br>`library.existing_folders` | C | Mobile gallery mode reads native Camera/Screenshots/other device albums without an import copy; cloud mode is a separate backup workflow. | [R04-S15](<#r04-s15>) |
| **Original-quality export**<br>`library.export_originals` | C | Desktop/CLI export preserves original file bytes and album folders; files in several albums appear in each exported folder, potentially increasing local space. | [R04-S2](<#r04-s2>), [R04-S5](<#r04-s5>) |
| **Desktop watched folders**<br>`library.filesystem_watch` | C | Monitors additions/deletions while the desktop client runs; new files upload and local deletions move cloud membership to Uncategorized instead of permanent removal. Edits to already-uploaded files are not tracked. | [R04-S4](<#r04-s4>) |
| **Selective background mobile backup**<br>`library.mobile_backup` | C | Selected device folders/albums back up originals without compression, use Wi-Fi by default with a cellular override, resume interrupted uploads and map into Ente albums. | [R04-S4](<#r04-s4>) |
| **Multiple watched directories**<br>`library.multiple_roots` | C | Multiple desktop watch folders have independent album-mapping choices and sync concurrently; these are roots feeding one account, not separate catalogues. | [R04-S4](<#r04-s4>) |
| **Only-new-photo cutoff**<br>`library.new_only_backup` | C | Onboarding new-only mode starts at seven days ago; enabling later uses the current moment. Already queued uploads are not cancelled and manual older uploads still work. | [R04-S4](<#r04-s4>) |
| **Google Takeout metadata import**<br>`library.takeout_import` | C | Matches media with Takeout JSON dates/location/captions. Extract all archive parts into one parent while preserving album subfolders; reimporting skipped assets does not repair their stored dates. | [R04-S5](<#r04-s5>) |
| **Shared updates and memories reminders**<br>`maintenance.notifications` | C | Mobile notifications cover shared additions, memories and tagged-person birthdays. Categories are configurable; birthday reminders occur on the day, not earlier. | [R04-S2](<#r04-s2>) |
| **Batch date/location editing**<br>`metadata.batch_edit` | C | Desktop supports bulk creation-time changes; mobile/web/desktop allow location edits on multi-selection. | [R04-S5](<#r04-s5>) |
| **Non-embedded coordinate corrections**<br>`metadata.catalogue_geotag` | C | Add or drag map coordinates for photos lacking/wrong locations. Values belong to Ente's separate metadata and do not strip/replace GPS inside the original or phone-library copy. | [R04-S5](<#r04-s5>) |
| **Encrypted descriptive captions**<br>`metadata.comments` | C | Edit searchable descriptions in the info panel on mobile/web/desktop; values sync encrypted and are separate from originals. | [R04-S5](<#r04-s5>) |
| **Correct capture timestamps**<br>`metadata.date_fix` | C | Desktop bulk Edit/Fix time can use original/digitized/metadata EXIF dates, parsed filename or custom time. Corrections sync but never rewrite original EXIF. | [R04-S5](<#r04-s5>) |
| **Full EXIF inspection**<br>`metadata.exif_read` | C | Reads capture time/camera/GPS for import and exposes View all EXIF on mobile/web/desktop; not every raw field is searchable. | [R04-S5](<#r04-s5>) |
| **Signed-in favorites**<br>`metadata.favorites` | C | Favorites are account-backed organization, used by widgets and protected by similar-image auto-selection; unavailable in account-free gallery mode. | [R04-S2](<#r04-s2>), [R04-S3](<#r04-s3>), [R04-S15](<#r04-s15>) |
| **IPTC import**<br>`metadata.iptc_read` | C | Imports embedded IPTC alongside other standards, including date information; original bytes remain preserved. | [R04-S5](<#r04-s5>) |
| **Rename without rewriting originals**<br>`metadata.display_name_edit` | C | Filename edits in the info panel are stored separately and synced; original filename is preserved. | [R04-S5](<#r04-s5>) |
| **Original metadata preserved on export**<br>`metadata.preserve_export` | C | Original downloads retain embedded metadata verbatim; Ente/Takeout corrections travel as JSON sidecars, not rewritten EXIF. Edited copies preserve selected camera/date/location fields but not necessarily all metadata. | [R04-S5](<#r04-s5>) |
| **Takeout-style export sidecars**<br>`metadata.sidecar_write` | C | Exports edits into metadata/filename.ext.json with canonical photoTakenTime, description and geoData; originals remain unchanged. Legacy creationTime field is deprecated. | [R04-S5](<#r04-s5>) |
| **XMP import**<br>`metadata.xmp_read` | C | Reads embedded XMP for metadata/date extraction without implying arbitrary XMP sidecar editing. | [R04-S5](<#r04-s5>) |
| **Reuse encrypted indexes across devices**<br>`performance.encrypted_ml_sync` | O | Index on desktop, sync encrypted results to mobile and disable mobile local indexing to reduce memory load. Concurrent clients avoid duplicate indexing but documentation says this does not accelerate the overall job. | [R04-S7](<#r04-s7>) |
| **Resume uploads and exports**<br>`performance.resume` | C | Interrupted backup resumes with connectivity and repeated CLI export continues previous work; retained encrypted upload staging can temporarily increase device storage. | [R04-S2](<#r04-s2>), [R04-S4](<#r04-s4>) |
| **Local app lock**<br>`privacy.app_lock` | C | Mobile/desktop offer PIN/password locks, configurable immediate-to-30-minute background autolock and device authentication; desktop device lock is macOS-only. | [R04-S27](<#r04-s27>) |
| **End-to-end-encrypted Photos**<br>`privacy.e2ee` | C | Encrypts original media and metadata on the client; security FAQ identifies XChaCha20/XSalsa20, Poly1305 and Argon2id. Server operators do not receive plaintext library data or encryption keys. | [R04-S1](<#r04-s1>), [R04-S24](<#r04-s24>) |
| **Authenticated-exit handoff viewer**<br>`privacy.guest_view` | C | Mobile guest view restricts browsing to one item/selection/album, hides edit/share/delete/info/navigation and requires configured device authentication to exit. | [R04-S25](<#r04-s25>) |
| **Authenticated hidden section**<br>`privacy.hidden_media` | C | Hide removes owned media from ordinary timeline/albums/search and requires device authentication for Hidden; a still-local copy may remain visible in On device views. | [R04-S3](<#r04-s3>) |
| **Account-free local mobile gallery**<br>`privacy.no_upload_required` | C | Gallery mode on iOS/Android browses device photos/videos and runs optional local face/semantic analysis without uploading; desktop does not have this mode. | [R04-S15](<#r04-s15>), [R04-S7](<#r04-s7>) |
| **Offline local/indexed use**<br>`privacy.offline_use` | C | Device media and already-indexed face/Magic Search work offline; remote originals must first download, and account sharing/backups/maps are separate network-dependent functions. | [R04-S3](<#r04-s3>), [R04-S6](<#r04-s6>), [R04-S7](<#r04-s7>), [R04-S15](<#r04-s15>), [R04-S23](<#r04-s23>) |
| **User-held recovery key**<br>`privacy.recovery_key` | C | A 24-word key recovers access after password loss; absent password, signed-in recovery route/key or preconfigured trusted contact, support cannot decrypt Photos data. | [R04-S24](<#r04-s24>) |
| **Hide app-switcher content**<br>`privacy.screen_content_protection` | C | Mobile Hide content obscures app-switcher views and disables screenshots on Android; no claim of general screen-recording prevention is made. | [R04-S27](<#r04-s27>) |
| **Photos account second factor**<br>`privacy.two_factor_auth` | C | Shared account supports TOTP or WebAuthn passkeys as a second factor; adding passkeys replaces configured TOTP, rather than making Photos passwordless. This does not inventory Ente Auth's authenticator features. | [R04-S28](<#r04-s28>) |
| **Thirty-day cloud Trash**<br>`safety.app_recovery` | C | Deleted Ente assets remain recoverable for 30 days and count toward quota until purged. Bulk restore targets a chosen album, not each previous membership; permanent deletion is unrecoverable. | [R04-S3](<#r04-s3>) |
| **No automatic cross-device destructive sync**<br>`safety.backup_deletion_separation` | C | Native-device deletion does not delete backup, and cloud deletion does not silently erase the device original. Ente remembers uploaded files to avoid automatically re-uploading deliberately deleted cloud copies. | [R04-S4](<#r04-s4>) |
| **Review before cleanup/deletion**<br>`safety.confirmation` | C | Cloud deletion, empty Trash and device-space cleanup require confirmation; duplicate cleanup reviews results and reclaimable-space information first. | [R04-S3](<#r04-s3>) |
| **Keep locally exported deleted copies**<br>`safety.export_trash_retention` | C | Cloud deletion moves exported files into an export Trash folder; subsequently emptying cloud Trash does not automatically delete those local copies. | [R04-S4](<#r04-s4>) |
| **Hosted database backup and restore checks**<br>`safety.hosted_catalogue_backup` | C | Specification describes HA Postgres, six-hour snapshots, daily portable dumps, encrypted locked cross-provider copies and daily restore testing with alerts. These are service operational claims, not tested here. | [R04-S30](<#r04-s30>) |
| **Provider-level deletion protection**<br>`safety.hosted_retention_lock` | C | Hosted Wasabi replica uses compliance hold plus a 21-day release buffer; cleanup occurs later after customer permanent deletion. This does not promise user restoration after Trash expires. | [R04-S30](<#r04-s30>) |
| **Save edited copies**<br>`safety.nondestructive_edits` | C | Photo/video edits leave original files unchanged and save new finalized copies. Edited dimensions/format or secondary metadata can change; not a reversible development-history stack. | [R04-S5](<#r04-s5>), [R04-S12](<#r04-s12>) |
| **Android device trash integration**<br>`safety.os_trash` | C | On Android 11+, deleting local gallery items through Ente uses Android system trash and exposes a Device recovery tab even for unbacked media; system retention is distinct from Ente's 30 days. | [R04-S3](<#r04-s3>) |
| **Photos Legacy recovery**<br>`safety.trusted_contact_recovery` | C | Previously accepted Ente trusted contacts can request recovery with a 7/14/30-day owner veto period, then change account password; configured from Photos mobile and applicable to photo succession. | [R04-S13](<#r04-s13>), [R04-S24](<#r04-s24>) |
| **Date-constrained discovery**<br>`search.date_range` | C | Magic Search documentation combines semantic results with date filters and specific time periods; web supports basic date search. | [R04-S7](<#r04-s7>), [R04-S29](<#r04-s29>) |
| **Filename search**<br>`search.filename_path` | C | Web/basic search includes filename alongside date, description and album; no semantic model is required for these fields. | [R04-S7](<#r04-s7>) |
| **Private location discovery**<br>`search.location` | C | Search location tags and geographic areas locally; Magic Search can be narrowed to a tagged place. | [R04-S10](<#r04-s10>), [R04-S29](<#r04-s29>) |
| **Parsed metadata and caption search**<br>`search.metadata` | C | Only fields parsed at import are searchable; raw EXIF can still be displayed separately. Captions/descriptions are searchable and encrypted. | [R04-S5](<#r04-s5>), [R04-S7](<#r04-s7>) |
| **Library-wide recognized-text search**<br>`search.ocr` | N | OCR guide explicitly states Detect Text builds no searchable library index; occasional CLIP matches to prominent text are not dedicated OCR search. | [R04-S11](<#r04-s11>) |
| **Person-name search**<br>`search.people` | O | Named identities can be searched across albums using the local face index; no unencrypted face data or search queries need reach the service. | [R04-S6](<#r04-s6>) |
| **On-device CLIP Magic Search**<br>`search.semantic_text` | O | Opt-in local CLIP matches natural-language objects/scenes/colors/activities and relationships; combine with dates, people, albums or locations. English typically works best; not available in the web client. | [R04-S7](<#r04-s7>), [R04-S29](<#r04-s29>) |
| **Shared social activity feed**<br>`sharing.activity_feed` | C | Mobile Feed aggregates likes/comments/replies from shared albums; it is social history, not an operation-recovery journal. | [R04-S18](<#r04-s18>) |
| **Authenticated collaborative albums**<br>`sharing.collaborative_albums` | C | Email-invited participants add photos/videos. Each uploader pays their own quota, and their contributions leave the shared album if they leave while remaining in their account. | [R04-S19](<#r04-s19>) |
| **Shared-album comments and likes**<br>`sharing.comments_reactions` | C | Mobile, web and desktop support commenting, quoted replies and likes on shared photos/videos; public-link visitors can participate anonymously when enabled. Owners/admins moderate comments, each album keeps a separate thread for the same photo, and comments are limited to 500 characters. Unshared private albums do not support these interactions; comment and like data remain end-to-end encrypted. | [R04-S18](<#r04-s18>) |
| **Custom-domain album links**<br>`sharing.custom_domains` | O | Public links can use an owner-controlled domain; Trip and app-reopen/join flows have documented custom-domain limitations. | [R04-S8](<#r04-s8>) |
| **Hide public download controls**<br>`sharing.download_button_control` | C | Owners can hide download buttons, but recipients can still copy via browser/tools/screenshots and metadata is not stripped. This is not DRM or guaranteed original-file protection. | [R04-S8](<#r04-s8>) |
| **Encrypted album-scoped discussions**<br>`sharing.encrypted_comments_reactions` | C | Shared albums/public links support comments, quoted replies, likes and anonymous display names. Same photo has separate threads per album; owners/admins moderate. Comments cap at 500 characters and do not apply to unshared private albums. | [R04-S18](<#r04-s18>) |
| **Expiring links**<br>`sharing.expiring_links` | C | Choose preset/custom expiry and later extend/change it; expired or removed links stop granting access. | [R04-S8](<#r04-s8>) |
| **Automatic future-album sharing**<br>`sharing.family_library_auto_share` | $ | Within family sharing, select owned albums in bulk and optionally share newly created albums automatically; shared capacity alone never grants content access. | [R04-S14](<#r04-s14>) |
| **Paid family capacity sharing**<br>`sharing.family_storage` | $ | Paid subscriber plus five members share one plan while content stays private by default; admin can set individual storage limits. | [R04-S14](<#r04-s14>) |
| **Account-free collect links**<br>`sharing.guest_upload` | C | Anyone with the enabled link can view/add through a browser; collected files count to the owner's quota and guests cannot delete uploads. Current guide says contributor attribution is unavailable. | [R04-S8](<#r04-s8>), [R04-S19](<#r04-s19>) |
| **Link audience device cap**<br>`sharing.link_device_limits` | C | Limits unique IP+User-Agent combinations, not actual physical devices; already admitted combinations retain access after the cap is reached. Free plans have a ten-device cap. | [R04-S8](<#r04-s8>) |
| **Masonry, grouped and Trip layouts**<br>`sharing.link_layouts` | C | Public viewers support proportional masonry, date groups or map/timeline Trip layout; Trip currently redirects custom-domain links to albums.ente.com. | [R04-S8](<#r04-s8>) |
| **Separate accounts with sharing**<br>`sharing.multiuser` | C | Each user has their own account/storage; invited collaborators share selected albums. Multiple accounts are not counted as selectable libraries. | [R04-S19](<#r04-s19>), [R04-S14](<#r04-s14>) |
| **Password access control**<br>`sharing.password_links` | C | Optional link password gates server access to encrypted content but does not re-encrypt it or change the embedded link key. | [R04-S8](<#r04-s8>) |
| **Encrypted public/quick album links**<br>`sharing.public_links` | C | Share an album or selected items without requiring recipients' accounts. Quick links create a backing album, can become ordinary albums and can be revoked without deleting photos. | [R04-S8](<#r04-s8>) |
| **Viewer/collaborator/admin/owner roles**<br>`sharing.roles` | C | Viewer views/downloads/comments, collaborator adds/removes own uploads, admin manages members/removes membership and suggests deletion; only owner manages links/deletes album and nobody permanently deletes others' assets. | [R04-S19](<#r04-s19>) |
| **Uncapped paid link audiences**<br>`sharing.unlimited_link_devices` | $ | Paid plans can create public links without the free tier's ten-device limit. | [R04-S8](<#r04-s8>) |
| **Automatic cross-provider failover**<br>`storage.automatic_disaster_failover` | R | Reliability document describes manually tested secondary-storage/database recovery and lists fully automatic failover as future work; primary DB active/passive failover is already distinct. | [R04-S30](<#r04-s30>) |
| **Three-provider hosted replicas**<br>`storage.hosted_replication` | C | Hosted specification describes two hot encrypted copies in Amsterdam/Frankfurt and one cold copy in Paris across Backblaze/Wasabi/Scaleway; self-hosters must design their own redundancy. | [R04-S30](<#r04-s30>) |
| **Paid hosted capacity**<br>`storage.paid_cloud_capacity` | $ | README describes Photos as a paid service with a 10 GB free allocation; additional hosted capacity requires a subscription, separate from self-hosting. | [R04-S1](<#r04-s1>) |

## Limitations and evidence gaps

- **explicit:** This profile excludes independent Auth token-management and Locker document features; monorepo stars and latest Locker release are not attributed solely to Photos. ([R04-S1](<#r04-s1>))
- **explicit:** No nested albums/custom drag ordering or general two-way sync. Watch folders do not update previously uploaded file edits, NAS watch imports are not officially supported and exports must not target an upload-watched directory. ([R04-S2](<#r04-s2>), [R04-S3](<#r04-s3>), [R04-S4](<#r04-s4>))
- **explicit:** Account-free local gallery is mobile-only and lacks cloud albums/favorites/hide/archive/sharing. Signing in discards local gallery ML indexes and limits subsequent indexing to backed-up assets. ([R04-S7](<#r04-s7>), [R04-S15](<#r04-s15>))
- **explicit:** Web lacks face/Magic Search; desktop lacks fine-grained face correction, mobile Similar images cleanup, collage and video editor. On-demand OCR does not create searchable text across the library. ([R04-S3](<#r04-s3>), [R04-S6](<#r04-s6>), [R04-S7](<#r04-s7>), [R04-S11](<#r04-s11>), [R04-S12](<#r04-s12>), [R04-S17](<#r04-s17>))
- **explicit:** 10 GB per-file limit; RAW preview support is limited and uploaded formats may not display. Apple Portrait's separate editable depth/adjustment payload is not preserved like a full Apple Photos asset. ([R04-S4](<#r04-s4>), [R04-S5](<#r04-s5>))
- **explicit:** Public recipients can decrypt metadata including GPS. Hiding download buttons or editing the catalogue location neither prevents copying nor removes original embedded coordinates; password links are access control, not additional encryption. ([R04-S5](<#r04-s5>), [R04-S8](<#r04-s8>))
- **explicit:** Ente's symlink wording means logical album references, not filesystem link replacement. Exported multi-album files may consume repeated disk space and metadata edits require JSON-aware destination tools. ([R04-S2](<#r04-s2>), [R04-S5](<#r04-s5>), [R04-S9](<#r04-s9>))
- **explicit:** Hosted retention locks and restore checks do not make user-deleted data recoverable after the documented recovery windows, and do not establish a durable per-file-operation journal for client actions. ([R04-S3](<#r04-s3>), [R04-S30](<#r04-s30>))
- **coverage-gap:** Offline basemaps, user-configurable integrity scrubbing, general tagging/rating writeback, full RAW development and a crash-recovery file-operation journal are not established by inspected sources. ([R04-S5](<#r04-s5>), [R04-S10](<#r04-s10>), [R04-S30](<#r04-s30>))
- **explicit:** Some documentation overstates hiding download controls in the collaboration page; the dedicated public-link guide explicitly disclaims preventing copies and is treated as controlling evidence. ([R04-S8](<#r04-s8>), [R04-S19](<#r04-s19>))
- **Coverage gap:** No application execution or independent cryptographic/performance verification; hosted durability is reported as documented design.
- **Coverage gap:** Selected backup/security FAQ sections were read in full as listed, rather than every troubleshooting question; feature-specific guides and current Photos release entries cover the feature inventory.
- **Coverage gap:** Legacy Auth/Locker functionality excluded; client-version/platform asymmetries and a few internally simplified documentation statements are explicitly qualified.

## Coverage

Outcome: **complete**.
Areas checked: ingestion, browsing/search, metadata, duplicates/cleanup, AI/people, maps/time, sharing, safety/privacy, performance/storage, deployment/integrations.

## Inspected primary sources

### R04-S1

[Monorepo README, Photos scope](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/README.md>)
- Kind/ref: readme; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Complete README read; only platform and Ente Photos claims used
- Establishes: Encrypted Photos service, clients, free/paid hosting and monorepo/product boundaries.

### R04-S2

[Advanced features FAQ](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/faq/advanced-features.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire FAQ
- Establishes: CLI/desktop export, streaming beta, casting, widgets, shortcuts and API limits.

### R04-S3

[Albums and organization FAQ](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/faq/albums-and-organization.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire FAQ
- Establishes: Flat albums, gallery/slideshows, hide/archive, exact/similar cleanup, deletion and recovery semantics.

### R04-S4

[Backup and sync FAQ](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/faq/backup-and-sync.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Mobile Backup through duplicate-handling; complete Desktop Backup section; export-trash, File Support &amp; Upload Limits and Deduplication sections
- Establishes: Backup-first semantics, multiple watched folders, rename/edit constraints, upload sizes and format limitations.

### R04-S5

[Metadata and editing FAQ](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/faq/metadata-and-editing.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire FAQ
- Establishes: EXIF/IPTC/XMP/Takeout import, image editing, separate metadata edits, JSON export and sharing privacy.

### R04-S6

[Face recognition](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/search-and-discovery/face-recognition.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Detection, grouping, naming/corrections, platform limits, encrypted sync and offline operation.

### R04-S7

[Machine learning](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/search-and-discovery/machine-learning.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Opt-in local processing, signed-in versus gallery-mode scope and encrypted shared indexes.

### R04-S8

[Public and quick links](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/sharing-and-collaboration/public-links.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Layouts, link keys, password/expiry/device/download controls, guest uploads and plan distinctions.

### R04-S9

[Duplicate detection during backup](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/backup-and-sync/duplicate-detection.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Hash versus hash-and-filename import identity and logical album references.

### R04-S10

[Map and location tags](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/search-and-discovery/map-and-location.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Map scope, private location search and radius-defined custom places.

### R04-S11

[Detect Text OCR](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/utilities/detect-text.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: On-demand mobile OCR, model download and explicit absence of library-wide OCR search.

### R04-S12

[Mobile video editor](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/utilities/video-editor.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Trim/crop/rotate, native/fallback encoding, new-copy semantics and limitations.

### R04-S13

[Photos Legacy trusted contacts](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/account/legacy/index.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Photos account succession/recovery with configurable waiting period and veto.

### R04-S14

[Photos family plans](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/account/family-plans.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Paid shared capacity, private accounts, six-person limit, quotas and library sharing.

### R04-S15

[Account-free gallery mode](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/getting-started/gallery-mode.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Local mobile gallery/AI capabilities and signed-in-only organization features.

### R04-S16

[Self-hosting quickstart](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/self-hosting/index.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide; Photos and shared infrastructure only
- Establishes: Docker setup, Photos/public-album apps, server endpoints and configuration boundary.

### R04-S17

[Mobile collage](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/utilities/collage.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Two-to-six photo layouts, swapping, framing and device export.

### R04-S18

[Shared comments and likes](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/sharing-and-collaboration/comments-and-likes.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Encrypted album-scoped discussions, anonymous participants, moderation and activity feed.

### R04-S19

[Collaboration and collection](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/sharing-and-collaboration/collaboration.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Role-specific rights, storage ownership, guest collections and deletion suggestions.

### R04-S20

[Memory Lane](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/search-and-discovery/memory-lane.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Person-year timelines, eligibility thresholds and public presentation.

### R04-S21

[Auto-add people to albums](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/albums-and-organization/auto-add-people.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Named-person rules and ownership/platform constraints on automatic album population.

### R04-S22

[QR codes in photos](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/utilities/qr-codes-in-photos.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: On-device QR detection and per-code copy/open/share/payment actions.

### R04-S23

[Photos changelog](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/changelog.md>)
- Kind/ref: release; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Complete entries mobile v1.3.69, v1.3.68, v1.3.67, v1.3.66 and desktop v1.7.31/v1.7.30
- Establishes: Current Photos release-specific viewer/editor, RAW, HDR-thumbnail and reliability changes.

### R04-S24

[Photos security and privacy FAQ](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/faq/security-and-privacy.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Data Encryption and Storage; account recovery/recovery-key questions through using the key
- Establishes: Encryption primitives, replication location and irrecoverability without credentials or configured recovery.

### R04-S25

[Guest view](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/utilities/guest-view.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Restricted handoff viewer and authenticated exit.

### R04-S26

[Photo rituals](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/utilities/rituals.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Scheduled photo habits, capture-date streaks and local-only ritual state.

### R04-S27

[Photos app lock](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/account/app-lock.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: PIN/password/device lock, timing and screen-content protection.

### R04-S28

[Shared account passkeys applicable to Photos](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/account/passkeys.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide, excluding any independent authenticator product functionality
- Establishes: Passkeys as second factor, TOTP replacement and recovery-key path.

### R04-S29

[Magic Search](<https://github.com/ente/ente/blob/52b907b57018958468615f4036851c196291012f/docs/docs/photos/features/search-and-discovery/magic-search.md>)
- Kind/ref: manual; 52b907b57018958468615f4036851c196291012f
- Sections inspected: Entire guide
- Establishes: Local CLIP search, combinations with metadata facets, language/accuracy limits.

### R04-S30

[Reliability and replication](<https://ente.com/reliability/>)
- Kind/ref: official-site; live-docs
- Sections inspected: Entire specification including current replication, backup restore verification and future work
- Establishes: Hosted three-provider storage, retention locks, DB snapshots/dumps and explicitly not-yet-automatic failover.

---
[All 50 repositories](<../README.md>) · [Common-to-unique feature catalogue](<../FEATURES.md>)
