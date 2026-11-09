# Photo and video tools: 50-repository feature study

## Coverage and deliverables

**50/50 repositories individually researched.** 617 primary-source records (617 distinct URLs), 2,657 source-backed findings, and 889 normalized feature definitions (844 with documented support in at least one repository).

| Deliverable | Purpose |
|---|---|
| [Full feature catalogue](FEATURES.md) | Every normalized feature, ranked common-to-unique, with all matching repository names and availability statuses. |
| [Feature frequency / decision CSV](feature-frequency.csv) | Counts, complete repository lists and blank decision/priority/notes columns for your selections. |
| [50-repository feature matrix](feature-matrix.csv) | One row per feature, one column per repository; status-aware comparisons. |
| [Within-category frequencies](category-frequency.csv) | Compare desktop, server, mobile, utility and cleanup peers rather than mixing their different goals. |
| [Repository inventory](repositories.csv) | Frozen stars, categories, licenses, release metadata and profile links. |
| [Evidence ledger](evidence.csv) | Every finding mapped to normalized features and inspected primary sources. |
| [Sources](sources.csv) | Source URLs, references and sections inspected. |
| [Coverage audit](coverage.csv) | All 50 completion records and documentation gaps. |
| [Candidate audit](candidate-audit.csv) | Discovery candidates and selection/exclusion decisions. |
| [Structured research data](research-data.json) | Raw profiles, frozen metadata, taxonomy and normalization rules. |
| [Methodology](METHODOLOGY.md) | Search queries, selection rules, counting semantics, validation and limits. |
| [Normalization audit](normalization-audit.csv) | Explicit synonym merges and non-feature exclusions. |

## How to read the counts

- **C** core, **O** optional module/configuration, **P** plugin, **$** paid: documented support, counted once per repository.
- **R** roadmap, **?** unclear, **N** explicitly unsupported: retained as evidence but not counted as present.
- Empty matrix cells mean **not established**, not 'no'. Do not interpret undocumented safeguards as absent safeguards.
- Counts are **documented-evidence lower bounds**, not proof of actual prevalence. Routine features may be underdocumented, and granular variants are naturally rarer.
- Generic file hashing is not video playback; face detection is not face recognition; self-hosting is not E2EE or air-gapped operation.
- Legacy/fork lineages can inflate repository frequencies. Family counts provide a second view; they do not prove independent implementations.
- Status-specific counts may overlap for documented variants; total support still counts each repository once.
- A popular feature may be irrelevant to a local desktop app. A rare safety feature may be more valuable than a common sharing feature.

## Selection method

Photo/video collection managers, end-user galleries, photo-library organization utilities, and duplicate-file cleanup tools. Desktop, web/server, CLI and mobile are eligible. Legacy repositories are included and labelled. General-purpose editors, single-image viewers without substantive collection organization, SDKs/components, AI generators, backup/download-only tools, generic CMS/file hosting, and release-only binary repositories are excluded.

Highest live GitHub star counts among the explicitly eligible repositories in the documented discovery pool; not an authoritative ranking of every project on GitHub.

Frozen metadata: **2026-11-09T14:33:57.893756+00:00**. Explicitly eligible candidates: **71**. Selected cutoff: **1,456 stars**. Broad discovery included English descriptions/topics, Chinese album/image-hosting terms and known-project checks.

The panel includes collection-oriented import/metadata utilities and full image-hosting galleries. It excludes RAW/general editors, SDKs/lightbox components, pure downloaders, generic CMS/file sharing and binary-only release repositories. Distinct legacy/current repositories are intentionally retained where relevant, and labelled by lineage.

### Category mix

| Category | Repositories |
|---|---:|
| cleanup | 7 |
| gallery-mobile | 7 |
| gallery-sharing | 15 |
| library-cloud-client | 1 |
| library-desktop | 3 |
| library-server | 11 |
| library-utility | 6 |

## Most broadly documented features

| Feature | Supported repos | Core | Lineages |
|---|---:|---:|---:|
| [Translated / localized application interface](<FEATURES.md>) (`deployment.localization`) | 30/50 | 30 | 29 |
| [End-user web interface](<FEATURES.md>) (`deployment.web`) | 29/50 | 28 | 27 |
| [Self-hosted deployment](<FEATURES.md>) (`deployment.selfhosted`) | 27/50 | 26 | 25 |
| [Read/display EXIF](<FEATURES.md>) (`metadata.exif_read`) | 25/50 | 25 | 23 |
| [Collection thumbnail grid](<FEATURES.md>) (`browse.grid`) | 25/50 | 24 | 24 |
| [Thumbnail caching](<FEATURES.md>) (`performance.thumbnail_cache`) | 24/50 | 23 | 21 |
| [Index/browse original files in existing directories without mandatory re-import copies](<FEATURES.md>) (`library.existing_folders`) | 22/50 | 21 | 20 |
| [Documented Docker deployment](<FEATURES.md>) (`deployment.docker`) | 22/50 | 18 | 20 |
| [Documented API](<FEATURES.md>) (`integration.api`) | 21/50 | 19 | 20 |
| [Shareable public links](<FEATURES.md>) (`sharing.public_links`) | 21/50 | 19 | 19 |
| [Favorites](<FEATURES.md>) (`metadata.favorites`) | 20/50 | 19 | 17 |
| [Multiple user accounts](<FEATURES.md>) (`sharing.multiuser`) | 20/50 | 18 | 19 |
| [Search filenames/paths](<FEATURES.md>) (`search.filename_path`) | 19/50 | 18 | 18 |
| [Play/preview video, not only hash video bytes](<FEATURES.md>) (`browse.video_playback`) | 19/50 | 17 | 18 |
| [Command-line interface](<FEATURES.md>) (`integration.cli`) | 19/50 | 17 | 19 |
| [HEIC/HEIF support](<FEATURES.md>) (`formats.heic`) | 19/50 | 15 | 19 |
| [Download/export original media](<FEATURES.md>) (`library.export_originals`) | 18/50 | 18 | 17 |
| [File/media type filtering](<FEATURES.md>) (`search.file_type`) | 18/50 | 18 | 17 |
| [Chronological/date-grouped browsing](<FEATURES.md>) (`browse.timeline`) | 17/50 | 17 | 15 |
| [Descriptions/comments/captions](<FEATURES.md>) (`metadata.comments`) | 17/50 | 17 | 17 |
| [Assign/manage tags or keywords](<FEATURES.md>) (`metadata.tags`) | 17/50 | 17 | 16 |
| [Tag/keyword search](<FEATURES.md>) (`search.tags`) | 17/50 | 17 | 17 |
| [User-created virtual albums/collections](<FEATURES.md>) (`albums.manual`) | 17/50 | 16 | 15 |
| [Skip/deduplicate already imported assets](<FEATURES.md>) (`library.deduplicate_import`) | 17/50 | 16 | 16 |
| [Image zoom/pan](<FEATURES.md>) (`browse.zoom`) | 17/50 | 15 | 16 |

## Rare capabilities worth inspecting

These are uncommon **in this documented panel**, not claims of global uniqueness.

| Feature | Supporting repositories |
|---|---|
| People co-occurrence graph (`analytics.people_cooccurrence_graph`) | [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>) |
| Preserve metadata when deduplicating (`duplicates.metadata_merge`) | [immich-app/immich](<profiles/R01-immich-app-immich.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>) |
| Copy-on-write/reflink deduplication (`duplicates.reflinks`) | [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>) |
| Persist reviewed/ignored duplicate decisions across runs (`duplicates.remember_decisions`) | [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>) |
| Persistent batch-action selection baskets (`library.selection_baskets`) | [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>) |
| Custom typed field templates (`metadata.custom_fields`) | [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>) |
| Import existing face/person metadata (`metadata.face_region_import`) | [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>) |
| Interactive 3D Earth view (`geo.globe_view`) | [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>) |
| Browse catalogue/thumbnails while source storage is disconnected (`library.offline_volumes`) | [julyx10/lap](<profiles/R19-julyx10-lap.md>) |
| C2PA content credentials (`metadata.content_credentials`) | [deckerst/aves](<profiles/R14-deckerst-aves.md>) |
| Fujifilm film recipes (`metadata.fujifilm_recipes`) | [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>) |
| Time-nearest photo GPS propagation (`metadata.nearest_photo_geotag`) | [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>) |
| Companion-aware move rollback (`safety.companion_operation_rollback`) | [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>) |
| Scoped synchronization rollback snapshots (`safety.sync_recovery_snapshots`) | [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>) |
| Photos Legacy recovery (`safety.trusted_contact_recovery`) | [ente/ente](<profiles/R04-ente-ente.md>) |
| Unmounted/mass-missing protection (`safety.unavailable_library_guard`) | [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>) |
| Interactive subject segmentation (`ai.subject_cutout`) | [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>) |
| Detect static video borders (`editing.video_auto_crop`) | [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>) |
| Double-sided image pairs (`formats.front_back_pairs`) | [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>) |
| Reuse encrypted indexes across devices (`performance.encrypted_ml_sync`) | [ente/ente](<profiles/R04-ente-ente.md>) |

This is a curated preview of distinctive concepts, not every rare row. The full catalogue includes all observed granular capabilities and their evidence gaps.

## All 50 repository profiles

| Rank | Repository / individual analysis | Stars | Category | Sources | Findings |
|---:|---|---:|---|---:|---:|
| 1 | [immich-app/immich](<profiles/R01-immich-app-immich.md>) | 118,609 | library-server | 35 | 114 |
| 2 | [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>) | 40,424 | library-server | 35 | 119 |
| 3 | [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>) | 35,004 | cleanup | 4 | 59 |
| 4 | [ente/ente](<profiles/R04-ente-ente.md>) | 30,012 | library-cloud-client | 30 | 130 |
| 5 | [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>) | 8,141 | library-server | 23 | 162 |
| 6 | [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>) | 7,954 | cleanup | 10 | 37 |
| 7 | [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>) | 7,281 | library-desktop | 11 | 61 |
| 8 | [simulot/immich-go](<profiles/R08-simulot-immich-go.md>) | 7,170 | library-utility | 6 | 37 |
| 9 | [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>) | 7,141 | gallery-sharing | 17 | 41 |
| 10 | [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>) | 6,883 | gallery-sharing | 6 | 55 |
| 11 | [photoview/photoview](<profiles/R11-photoview-photoview.md>) | 6,570 | library-server | 17 | 45 |
| 12 | [electerious/Lychee](<profiles/R12-electerious-lychee.md>) | 6,362 | gallery-sharing | 8 | 46 |
| 13 | [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>) | 5,985 | library-utility | 11 | 23 |
| 14 | [deckerst/aves](<profiles/R14-deckerst-aves.md>) | 5,496 | gallery-mobile | 5 | 57 |
| 15 | [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>) | 5,446 | cleanup | 9 | 42 |
| 16 | [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>) | 4,707 | gallery-sharing | 4 | 28 |
| 17 | [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>) | 4,702 | gallery-sharing | 9 | 32 |
| 18 | [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>) | 4,328 | gallery-sharing | 13 | 78 |
| 19 | [julyx10/lap](<profiles/R19-julyx10-lap.md>) | 4,263 | library-desktop | 6 | 68 |
| 20 | [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>) | 4,031 | gallery-mobile | 4 | 42 |
| 21 | [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>) | 3,989 | library-utility | 12 | 76 |
| 22 | [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>) | 3,904 | gallery-mobile | 9 | 45 |
| 23 | [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>) | 3,882 | library-server | 15 | 76 |
| 24 | [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>) | 3,879 | cleanup | 6 | 36 |
| 25 | [pulsejet/memories](<profiles/R25-pulsejet-memories.md>) | 3,875 | library-server | 15 | 78 |
| 26 | [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>) | 3,802 | gallery-sharing | 15 | 38 |
| 27 | [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>) | 3,796 | library-utility | 13 | 58 |
| 28 | [pinry/pinry](<profiles/R28-pinry-pinry.md>) | 3,432 | gallery-sharing | 12 | 27 |
| 29 | [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>) | 3,370 | library-utility | 5 | 26 |
| 30 | [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>) | 3,260 | library-desktop | 24 | 97 |
| 31 | [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>) | 3,260 | gallery-mobile | 18 | 37 |
| 32 | [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>) | 3,035 | cleanup | 4 | 25 |
| 33 | [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>) | 3,006 | gallery-mobile | 49 | 99 |
| 34 | [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>) | 2,994 | cleanup | 3 | 31 |
| 35 | [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>) | 2,993 | gallery-mobile | 11 | 23 |
| 36 | [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>) **ARCHIVED** | 2,770 | gallery-sharing | 20 | 48 |
| 37 | [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>) | 2,757 | library-server | 5 | 39 |
| 38 | [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>) | 2,697 | gallery-sharing | 13 | 27 |
| 39 | [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>) | 2,670 | gallery-sharing | 9 | 42 |
| 40 | [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>) **ARCHIVED** | 2,588 | gallery-mobile | 4 | 38 |
| 41 | [sahib/rmlint](<profiles/R41-sahib-rmlint.md>) | 2,467 | cleanup | 8 | 44 |
| 42 | [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>) | 2,315 | library-server | 9 | 57 |
| 43 | [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>) | 1,975 | gallery-sharing | 6 | 42 |
| 44 | [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>) | 1,955 | library-server | 8 | 39 |
| 45 | [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>) | 1,798 | library-server | 6 | 55 |
| 46 | [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>) **ARCHIVED** | 1,753 | gallery-sharing | 11 | 28 |
| 47 | [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>) | 1,620 | gallery-sharing | 10 | 41 |
| 48 | [jmathai/elodie](<profiles/R48-jmathai-elodie.md>) | 1,506 | library-utility | 8 | 28 |
| 49 | [guardian/grid](<profiles/R49-guardian-grid.md>) | 1,460 | library-server | 18 | 44 |
| 50 | [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>) | 1,456 | gallery-sharing | 8 | 37 |

## Evidence and limits

Each selected repository has a separate profile covering deployment, storage/privacy, documented features, limitations, maturity notes and inspected sources. Source references are attached to every feature claim. README, official manuals, release notes and relevant source files were used; secondary comparisons were discovery aids only.

This is an in-depth **documented-feature inventory**, not proof that every hidden code path or third-party plugin has been discovered. None of the 50 apps was installed, benchmarked on your library or safety-audited here. Performance statements from projects remain their claims. Current-branch docs can be ahead of released builds; profile notes and pinned metadata expose that distinction. Edition/plugin/network dependencies must be reviewed before adoption.
Feature inspiration is distinct from code reuse: application, plugin and model licenses may differ and must be checked before copying code or assets.

### Choosing features for Memoria

Use the decision/priority/notes columns in `feature-frequency.csv`; filter by domain and inspect the linked profiles/evidence before selecting. Separate local-library needs from server/community-hosting features. Keep data-safety, bounded memory, interrupted-work recovery, offline/privacy constraints and clear review/Undo semantics as gates rather than ranking them solely by popularity. No application features were implemented as part of this study.
