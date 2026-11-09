# Features: most common to most unique

Corpus: **50 repositories**, 47 product-lineage groups. Frozen stars: 2026-11-09T14:33:57.893756+00:00.

Ranked by the number of repositories with documented current support (core, optional, plugin or paid), then core support. A repository counts once per feature even if it has several implementations. **Blank/undocumented is not absence.** Frequencies are not quality scores or implementation priorities.

Codes: **C** core · **O** optional module/configuration · **P** plugin/integration · **$** paid · **R** roadmap (excluded from support count) · **?** unclear · **N** explicitly unsupported.

[Editable frequency / decision CSV](<feature-frequency.csv>) · [Full 50-column matrix](<feature-matrix.csv>) · [Evidence ledger](<evidence.csv>)

## Common: 25–50 repositories

### 1. Translated / localized application interface — 30/50

`deployment.localization` · Domain: **deployment** · Core: **30** · Product-lineage groups: **29**

Application UI is offered in multiple languages. Translated README files and multilingual semantic search do not establish this capability.

- **Core (30):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Roadmap (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 18/50.

### 2. End-user web interface — 29/50

`deployment.web` · Domain: **deployment** · Core: **28** · Product-lineage groups: **27**

End-user web interface

- **Core (28):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [guardian/grid](<profiles/R49-guardian-grid.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Plugin/integration (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Explicitly unsupported (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 20/50.

### 3. Self-hosted deployment — 27/50

`deployment.selfhosted` · Domain: **deployment** · Core: **26** · Product-lineage groups: **25**

Self-hosted deployment

- **Core (26):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [guardian/grid](<profiles/R49-guardian-grid.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 23/50.

### 4. Read/display EXIF — 25/50

`metadata.exif_read` · Domain: **metadata** · Core: **25** · Product-lineage groups: **23**

Read/display EXIF

- **Core (25):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 25/50.

### 5. Collection thumbnail grid — 25/50

`browse.grid` · Domain: **browse** · Core: **24** · Product-lineage groups: **24**

Collection thumbnail grid

- **Core (24):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 25/50.

## Widespread: 10–24 repositories

### 6. Thumbnail caching — 24/50

`performance.thumbnail_cache` · Domain: **performance** · Core: **23** · Product-lineage groups: **21**

Thumbnail caching

- **Core (23):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Optional (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 26/50.

### 7. Index/browse original files in existing directories without mandatory re-import copies — 22/50

`library.existing_folders` · Domain: **library** · Core: **21** · Product-lineage groups: **20**

Index/browse original files in existing directories without mandatory re-import copies

- **Core (21):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Roadmap (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Explicitly unsupported (2):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 25/50.

### 8. Documented Docker deployment — 22/50

`deployment.docker` · Domain: **deployment** · Core: **18** · Product-lineage groups: **20**

Documented Docker deployment

- **Core (18):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Plugin/integration (3):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Roadmap (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 27/50.

### 9. Documented API — 21/50

`integration.api` · Domain: **integration** · Core: **19** · Product-lineage groups: **20**

Documented API

- **Core (19):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [guardian/grid](<profiles/R49-guardian-grid.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (2):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Explicitly unsupported (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 28/50.

### 10. Shareable public links — 21/50

`sharing.public_links` · Domain: **sharing** · Core: **19** · Product-lineage groups: **19**

Shareable public links

- **Core (19):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Roadmap (1):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 28/50.

### 11. Favorites — 20/50

`metadata.favorites` · Domain: **metadata** · Core: **19** · Product-lineage groups: **17**

Favorites

- **Core (19):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 30/50.

### 12. Multiple user accounts — 20/50

`sharing.multiuser` · Domain: **sharing** · Core: **18** · Product-lineage groups: **19**

Multiple user accounts

- **Core (18):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (2):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Explicitly unsupported (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 29/50.

### 13. Search filenames/paths — 19/50

`search.filename_path` · Domain: **search** · Core: **18** · Product-lineage groups: **18**

Search filenames/paths

- **Core (18):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [guardian/grid](<profiles/R49-guardian-grid.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Roadmap (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 30/50.

### 14. Play/preview video, not only hash video bytes — 19/50

`browse.video_playback` · Domain: **browse** · Core: **17** · Product-lineage groups: **18**

Play/preview video, not only hash video bytes

- **Core (17):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Optional (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Roadmap (2):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Unclear (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Explicitly unsupported (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 27/50.

### 15. Command-line interface — 19/50

`integration.cli` · Domain: **integration** · Core: **17** · Product-lineage groups: **19**

Command-line interface

- **Core (17):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Plugin/integration (2):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Roadmap (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 29/50.

### 16. HEIC/HEIF support — 19/50

`formats.heic` · Domain: **formats** · Core: **15** · Product-lineage groups: **19**

HEIC/HEIF support

- **Core (15):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Optional (4):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 31/50.

### 17. Download/export original media — 18/50

`library.export_originals` · Domain: **library** · Core: **18** · Product-lineage groups: **17**

Download/export original media

- **Core (18):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 32/50.

### 18. File/media type filtering — 18/50

`search.file_type` · Domain: **search** · Core: **18** · Product-lineage groups: **17**

File/media type filtering

- **Core (18):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 32/50.

### 19. Chronological/date-grouped browsing — 17/50

`browse.timeline` · Domain: **browse** · Core: **17** · Product-lineage groups: **15**

Chronological/date-grouped browsing

- **Core (17):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 33/50.

### 20. Descriptions/comments/captions — 17/50

`metadata.comments` · Domain: **metadata** · Core: **17** · Product-lineage groups: **17**

Descriptions/comments/captions

- **Core (17):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 33/50.

### 21. Assign/manage tags or keywords — 17/50

`metadata.tags` · Domain: **metadata** · Core: **17** · Product-lineage groups: **16**

Assign/manage tags or keywords

- **Core (17):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 33/50.

### 22. Tag/keyword search — 17/50

`search.tags` · Domain: **search** · Core: **17** · Product-lineage groups: **17**

Tag/keyword search

- **Core (17):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 33/50.

### 23. User-created virtual albums/collections — 17/50

`albums.manual` · Domain: **albums** · Core: **16** · Product-lineage groups: **15**

User-created virtual albums/collections

- **Core (16):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Plugin/integration (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 33/50.

### 24. Skip/deduplicate already imported assets — 17/50

`library.deduplicate_import` · Domain: **library** · Core: **16** · Product-lineage groups: **16**

Skip/deduplicate already imported assets

- **Core (16):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 33/50.

### 25. Image zoom/pan — 17/50

`browse.zoom` · Domain: **browse** · Core: **15** · Product-lineage groups: **16**

Image zoom/pan

- **Core (15):** [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 33/50.

### 26. Exact duplicate detection using content hashes — 16/50

`duplicates.exact_hash` · Domain: **duplicates** · Core: **16** · Product-lineage groups: **15**

Exact duplicate detection using content hashes

- **Core (16):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 34/50.

### 27. Roles/access permissions — 16/50

`sharing.roles` · Domain: **sharing** · Core: **14** · Product-lineage groups: **15**

Roles/access permissions

- **Core (14):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Optional (2):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Unclear (1):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 33/50.

### 28. Plot media on a map — 16/50

`geo.map` · Domain: **geo** · Core: **13** · Product-lineage groups: **15**

Plot media on a map

- **Core (13):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (3):** [photoview/photoview](<profiles/R11-photoview-photoview.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Unclear (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 33/50.

### 29. One library/catalogue can cover multiple filesystem roots — 15/50

`library.multiple_roots` · Domain: **library** · Core: **15** · Product-lineage groups: **15**

One library/catalogue can cover multiple filesystem roots

- **Core (15):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Roadmap (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 34/50.

### 30. Explicit confirmation/review before destructive actions — 15/50

`safety.confirmation` · Domain: **safety** · Core: **15** · Product-lineage groups: **14**

Explicit confirmation/review before destructive actions

- **Core (15):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 35/50.

### 31. Decode/preview RAW photos — 15/50

`formats.raw` · Domain: **formats** · Core: **14** · Product-lineage groups: **14**

Decode/preview RAW photos

- **Core (14):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 35/50.

### 32. Android client/application — 15/50

`deployment.android` · Domain: **deployment** · Core: **11** · Product-lineage groups: **14**

Android client/application

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Plugin/integration (4):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 35/50.

### 33. Full-screen media viewer — 14/50

`browse.fullscreen` · Domain: **browse** · Core: **14** · Product-lineage groups: **12**

Full-screen media viewer

- **Core (14):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 36/50.

### 34. Slideshow — 14/50

`browse.slideshow` · Domain: **browse** · Core: **14** · Product-lineage groups: **13**

Slideshow

- **Core (14):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Roadmap (1):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 35/50.

### 35. Move/copy files through the app — 14/50

`library.move_copy` · Domain: **library** · Core: **14** · Product-lineage groups: **13**

Move/copy files through the app

- **Core (14):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 36/50.

### 36. Explicit paged results — 14/50

`browse.pagination` · Domain: **browse** · Core: **13** · Product-lineage groups: **14**

Explicit paged results

- **Core (13):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [guardian/grid](<profiles/R49-guardian-grid.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 36/50.

### 37. Search/filter technical or descriptive metadata — 14/50

`search.metadata` · Domain: **search** · Core: **13** · Product-lineage groups: **14**

Search/filter technical or descriptive metadata

- **Core (13):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Optional (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Roadmap (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 35/50.

### 38. Native Linux application distribution — 13/50

`deployment.linux` · Domain: **deployment** · Core: **13** · Product-lineage groups: **13**

Native Linux application distribution

- **Core (13):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 37/50.

### 39. Managed copy/import workflow — 13/50

`library.import_copy` · Domain: **library** · Core: **13** · Product-lineage groups: **13**

Managed copy/import workflow

- **Core (13):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 37/50.

### 40. Incremental rescan/reuse of existing index — 13/50

`library.incremental_scan` · Domain: **library** · Core: **13** · Product-lineage groups: **13**

Incremental rescan/reuse of existing index

- **Core (13):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 37/50.

### 41. Edit/correct capture timestamps — 13/50

`metadata.date_fix` · Domain: **metadata** · Core: **13** · Product-lineage groups: **12**

Edit/correct capture timestamps

- **Core (13):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Roadmap (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 36/50.

### 42. Manage originals without mandatory third-party upload — 13/50

`privacy.no_upload_required` · Domain: **privacy** · Core: **13** · Product-lineage groups: **13**

Manage originals without mandatory third-party upload

- **Core (13):** [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 37/50.

### 43. Application-managed trash/recovery area — 13/50

`safety.app_recovery` · Domain: **safety** · Core: **13** · Product-lineage groups: **12**

Application-managed trash/recovery area

- **Core (13):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 37/50.

### 44. Date-range filtering — 13/50

`search.date_range` · Domain: **search** · Core: **13** · Product-lineage groups: **13**

Date-range filtering

- **Core (13):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [guardian/grid](<profiles/R49-guardian-grid.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 37/50.

### 45. Crop — 13/50

`editing.crop` · Domain: **editing** · Core: **12** · Product-lineage groups: **12**

Crop

- **Core (12):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 37/50.

### 46. Rotate/flip — 13/50

`editing.rotate_flip` · Domain: **editing** · Core: **12** · Product-lineage groups: **12**

Rotate/flip

- **Core (12):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Roadmap (1):** [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 36/50.

### 47. AVIF support — 13/50

`formats.avif` · Domain: **formats** · Core: **12** · Product-lineage groups: **12**

AVIF support

- **Core (12):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Optional (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 37/50.

### 48. Organize/import into date-based folders — 13/50

`library.auto_date_folders` · Domain: **library** · Core: **12** · Product-lineage groups: **13**

Organize/import into date-based folders

- **Core (12):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Optional (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 37/50.

### 49. Password-protected shares — 13/50

`sharing.password_links` · Domain: **sharing** · Core: **11** · Product-lineage groups: **12**

Password-protected shares

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Roadmap (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Explicitly unsupported (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 35/50.

### 50. Documented local/on-device inference — 13/50

`ai.local_inference` · Domain: **ai** · Core: **9** · Product-lineage groups: **12**

Documented local/on-device inference

- **Core (9):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (4):** [ente/ente](<profiles/R04-ente-ente.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Unclear (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 36/50.

### 51. Back up/export application catalogue — 12/50

`safety.catalogue_backup` · Domain: **safety** · Core: **12** · Product-lineage groups: **12**

Back up/export application catalogue

- **Core (12):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 38/50.

### 52. Native Windows application distribution (not merely Docker on Windows) — 12/50

`deployment.windows` · Domain: **deployment** · Core: **11** · Product-lineage groups: **12**

Native Windows application distribution (not merely Docker on Windows)

- **Core (11):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Plugin/integration (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 38/50.

### 53. Choose the duplicate copy to retain — 12/50

`duplicates.keeper_selection` · Domain: **duplicates** · Core: **11** · Product-lineage groups: **12**

Choose the duplicate copy to retain

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 38/50.

### 54. Resize — 12/50

`editing.resize` · Domain: **editing** · Core: **11** · Product-lineage groups: **11**

Resize

- **Core (11):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 38/50.

### 55. Animated image support — 12/50

`formats.animated` · Domain: **formats** · Core: **11** · Product-lineage groups: **11**

Animated image support

- **Core (11):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Optional (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 38/50.

### 56. SVG preview — 12/50

`formats.svg` · Domain: **formats** · Core: **11** · Product-lineage groups: **11**

SVG preview

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Paid (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 38/50.

### 57. Native macOS application distribution — 12/50

`deployment.macos` · Domain: **deployment** · Core: **10** · Product-lineage groups: **12**

Native macOS application distribution

- **Core (10):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Plugin/integration (2):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 38/50.

### 58. Guest/public uploads — 12/50

`sharing.guest_upload` · Domain: **sharing** · Core: **10** · Product-lineage groups: **12**

Guest/public uploads

- **Core (10):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 38/50.

### 59. Dark theme — 11/50

`browse.dark_theme` · Domain: **browse** · Core: **11** · Product-lineage groups: **11**

Dark theme

- **Core (11):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 39/50.

### 60. Apple Live Photos paired assets — 11/50

`formats.live_photos` · Domain: **formats** · Core: **11** · Product-lineage groups: **11**

Apple Live Photos paired assets

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 39/50.

### 61. Selectively clear derived versus personal data — 11/50

`maintenance.selective_reset` · Domain: **maintenance** · Core: **11** · Product-lineage groups: **11**

Selectively clear derived versus personal data

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 39/50.

### 62. Batch metadata editing — 11/50

`metadata.batch_edit` · Domain: **metadata** · Core: **11** · Product-lineage groups: **11**

Batch metadata editing

- **Core (11):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 39/50.

### 63. Read IPTC — 11/50

`metadata.iptc_read` · Domain: **metadata** · Core: **11** · Product-lineage groups: **10**

Read IPTC

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 39/50.

### 64. Read XMP — 11/50

`metadata.xmp_read` · Domain: **metadata** · Core: **11** · Product-lineage groups: **11**

Read XMP

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 39/50.

### 65. Parallel scanning/hashing/analysis — 11/50

`performance.parallel_scan` · Domain: **performance** · Core: **11** · Product-lineage groups: **11**

Parallel scanning/hashing/analysis

- **Core (11):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 39/50.

### 66. Resume interrupted scan/import/tasks — 11/50

`performance.resume` · Domain: **performance** · Core: **11** · Product-lineage groups: **11**

Resume interrupted scan/import/tasks

- **Core (11):** [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 39/50.

### 67. Collision handling/no silent overwrite — 11/50

`safety.no_overwrite` · Domain: **safety** · Core: **11** · Product-lineage groups: **11**

Collision handling/no silent overwrite

- **Core (11):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 39/50.

### 68. JPEG XL support — 11/50

`formats.jpegxl` · Domain: **formats** · Core: **10** · Product-lineage groups: **11**

JPEG XL support

- **Core (10):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Optional (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Unclear (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 38/50.

### 69. Library totals/statistics — 11/50

`analytics.library_statistics` · Domain: **analytics** · Core: **9** · Product-lineage groups: **10**

Library totals/statistics

- **Core (9):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 39/50.

### 70. Background work queue — 11/50

`performance.background_jobs` · Domain: **performance** · Core: **9** · Product-lineage groups: **10**

Background work queue

- **Core (9):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Optional (2):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 39/50.

### 71. Object-storage integration — 11/50

`integration.object_storage` · Domain: **integration** · Core: **1** · Product-lineage groups: **11**

Object-storage integration

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Optional (10):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 38/50.

### 72. Documented keyboard navigation/shortcuts — 10/50

`browse.keyboard` · Domain: **browse** · Core: **10** · Product-lineage groups: **10**

Documented keyboard navigation/shortcuts

- **Core (10):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 40/50.

### 73. Media format conversion — 10/50

`editing.format_conversion` · Domain: **editing** · Core: **10** · Product-lineage groups: **10**

Media format conversion

- **Core (10):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 40/50.

### 74. Motion Photo support — 10/50

`formats.motion_photos` · Domain: **formats** · Core: **10** · Product-lineage groups: **10**

Motion Photo support

- **Core (10):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 40/50.

### 75. Multi-file / batch media upload — 10/50

`library.batch_upload` · Domain: **library** · Core: **10** · Product-lineage groups: **10**

Upload multiple media files as a batch through supported clients. Drag-and-drop, clipboard, URL and parallel-transfer details vary.

- **Core (10):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 40/50.

### 76. Library file/folder exclusion rules — 10/50

`library.exclude_folders` · Domain: **library** · Core: **10** · Product-lineage groups: **10**

Exclude files, folders or matching paths from library discovery/scanning/views. Retroactive behavior, marker files and pattern syntax vary; privacy vaults are separate.

- **Core (10):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 40/50.

### 77. Documented offline core operation (state exceptions) — 10/50

`privacy.offline_use` · Domain: **privacy** · Core: **9** · Product-lineage groups: **10**

Documented offline core operation (state exceptions)

- **Core (9):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Optional (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 40/50.

### 78. Use operating-system recycle bin/trash — 10/50

`safety.os_trash` · Domain: **safety** · Core: **9** · Product-lineage groups: **10**

Use operating-system recycle bin/trash

- **Core (9):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Plugin/integration (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 40/50.

### 79. Detect face regions — 10/50

`ai.face_detection` · Domain: **ai** · Core: **8** · Product-lineage groups: **9**

Detect face regions

- **Core (8):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (2):** [ente/ente](<profiles/R04-ente-ente.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Unclear (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 39/50.

### 80. Transcode/compress videos — 10/50

`editing.video_transcode` · Domain: **editing** · Core: **8** · Product-lineage groups: **10**

Transcode/compress videos

- **Core (8):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Optional (2):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 40/50.

### 81. Merge/split/reject/correct face groups — 10/50

`ai.face_corrections` · Domain: **ai** · Core: **7** · Product-lineage groups: **9**

Merge/split/reject/correct face groups

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (2):** [ente/ente](<profiles/R04-ente-ente.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Unclear (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 39/50.

### 82. Manually name identified people — 10/50

`ai.face_naming` · Domain: **ai** · Core: **7** · Product-lineage groups: **9**

Manually name identified people

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (2):** [ente/ente](<profiles/R04-ente-ente.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 40/50.

### 83. Recognize/match identities across faces — 10/50

`ai.face_recognition` · Domain: **ai** · Core: **7** · Product-lineage groups: **9**

Recognize/match identities across faces

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (2):** [ente/ente](<profiles/R04-ente-ente.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Roadmap (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Unclear (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 38/50.

## Selective: 3–9 repositories

### 84. Exclude directories/files/patterns — 9/50

`duplicates.exclude_paths` · Domain: **duplicates** · Core: **9** · Product-lineage groups: **9**

Exclude directories/files/patterns

- **Core (9):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 41/50.

### 85. Treat RAW+JPEG companions as linked/stacked assets — 9/50

`formats.raw_jpeg_pairs` · Domain: **formats** · Core: **9** · Product-lineage groups: **9**

Treat RAW+JPEG companions as linked/stacked assets

- **Core (9):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 41/50.

### 86. Location/GPS filtering — 9/50

`search.location` · Domain: **search** · Core: **9** · Product-lineage groups: **8**

Location/GPS filtering

- **Core (9):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 41/50.

### 87. Diagnostic/performance reporting — 9/50

`maintenance.diagnostics` · Domain: **maintenance** · Core: **8** · Product-lineage groups: **8**

Diagnostic/performance reporting

- **Core (8):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Optional (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 41/50.

### 88. Search/filter by identified people — 9/50

`search.people` · Domain: **search** · Core: **8** · Product-lineage groups: **8**

Search/filter by identified people

- **Core (8):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 41/50.

### 89. Automatically group similar faces — 9/50

`ai.face_clustering` · Domain: **ai** · Core: **7** · Product-lineage groups: **8**

Automatically group similar faces

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Optional (2):** [ente/ente](<profiles/R04-ente-ente.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Unclear (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 40/50.

### 90. Automatic content/scene/object tags — 9/50

`ai.auto_tags` · Domain: **ai** · Core: **6** · Product-lineage groups: **8**

Automatic content/scene/object tags

- **Core (6):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Plugin/integration (2):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Unclear (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 40/50.

### 91. Plugin/extension system — 9/50

`integration.plugins` · Domain: **integration** · Core: **4** · Product-lineage groups: **9**

Plugin/extension system

- **Core (4):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Optional (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Plugin/integration (4):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 41/50.

### 92. Map folders to albums — 8/50

`albums.folder_mapping` · Domain: **albums** · Core: **8** · Product-lineage groups: **8**

Map folders to albums

- **Core (8):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 42/50.

### 93. Touch/mobile-responsive interactions — 8/50

`browse.touch` · Domain: **browse** · Core: **8** · Product-lineage groups: **7**

Touch/mobile-responsive interactions

- **Core (8):** [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 42/50.

### 94. Preserve or reflect source folder hierarchy — 8/50

`library.folder_structure` · Domain: **library** · Core: **8** · Product-lineage groups: **8**

Preserve or reflect source folder hierarchy

- **Core (8):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 42/50.

### 95. Star ratings or equivalent numeric ratings — 8/50

`metadata.ratings` · Domain: **metadata** · Core: **8** · Product-lineage groups: **8**

Star ratings or equivalent numeric ratings

- **Core (8):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 42/50.

### 96. Remove sensitive/EXIF metadata — 8/50

`metadata.strip` · Domain: **metadata** · Core: **8** · Product-lineage groups: **8**

Remove sensitive/EXIF metadata

- **Core (8):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 42/50.

### 97. Non-destructive editing or save-as-new-copy — 8/50

`safety.nondestructive_edits` · Domain: **safety** · Core: **8** · Product-lineage groups: **8**

Non-destructive editing or save-as-new-copy

- **Core (8):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 42/50.

### 98. Panorama/360-degree viewing — 8/50

`browse.panorama` · Domain: **browse** · Core: **7** · Product-lineage groups: **8**

Panorama/360-degree viewing

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 41/50.

### 99. Google Photos Takeout import or repair — 8/50

`library.takeout_import` · Domain: **library** · Core: **7** · Product-lineage groups: **8**

Google Photos Takeout import or repair

- **Core (7):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Plugin/integration (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 42/50.

### 100. Write/export metadata sidecars — 8/50

`metadata.sidecar_write` · Domain: **metadata** · Core: **7** · Product-lineage groups: **8**

Write/export metadata sidecars

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Optional (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 42/50.

### 101. Explicit read-only source/library mode — 8/50

`safety.read_only_originals` · Domain: **safety** · Core: **7** · Product-lineage groups: **8**

Explicit read-only source/library mode

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Optional (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 42/50.

### 102. Watermark — 8/50

`editing.watermark` · Domain: **editing** · Core: **6** · Product-lineage groups: **7**

Watermark

- **Core (6):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 42/50.

### 103. Expiring shares — 8/50

`sharing.expiring_links` · Domain: **sharing** · Core: **6** · Product-lineage groups: **8**

Expiring shares

- **Core (6):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 42/50.

### 104. Natural-language semantic media search — 8/50

`search.semantic_text` · Domain: **search** · Core: **3** · Product-lineage groups: **8**

Natural-language semantic media search

- **Core (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Optional (5):** [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 42/50.

### 105. Folder/tree navigation — 7/50

`browse.folders` · Domain: **browse** · Core: **7** · Product-lineage groups: **6**

Folder/tree navigation

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 43/50.

### 106. Skip/keep all copies of a duplicate group — 7/50

`duplicates.keep_all` · Domain: **duplicates** · Core: **7** · Product-lineage groups: **7**

Skip/keep all copies of a duplicate group

- **Core (7):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 43/50.

### 107. Import media from remote URLs — 7/50

`library.url_import` · Domain: **library** · Core: **7** · Product-lineage groups: **6**

Fetch media from direct remote URLs into managed storage or a collection. Webpage scraping and cloud-account import are separate capabilities.

- **Core (7):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 43/50.

### 108. Cooperative task cancellation — 7/50

`performance.cancel` · Domain: **performance** · Core: **7** · Product-lineage groups: **7**

Cooperative task cancellation

- **Core (7):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 43/50.

### 109. Boolean/structured query syntax — 7/50

`search.boolean` · Domain: **search** · Core: **7** · Product-lineage groups: **7**

Boolean/structured query syntax

- **Core (7):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 43/50.

### 110. Sort by capture date — 7/50

`sort.capture_date` · Domain: **sort** · Core: **7** · Product-lineage groups: **6**

Sort by capture date

- **Core (7):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 43/50.

### 111. Cache hashes/results for later scans — 7/50

`duplicates.hash_cache` · Domain: **duplicates** · Core: **6** · Product-lineage groups: **7**

Cache hashes/results for later scans

- **Core (6):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Optional (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 43/50.

### 112. Perceptually similar image detection — 7/50

`duplicates.similar_images` · Domain: **duplicates** · Core: **6** · Product-lineage groups: **7**

Perceptually similar image detection

- **Core (6):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 43/50.

### 113. Search by image/visual similarity — 7/50

`search.similar_image` · Domain: **search** · Core: **5** · Product-lineage groups: **6**

Search by image/visual similarity

- **Core (5):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (2):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 43/50.

### 114. Background/event notifications — 7/50

`maintenance.notifications` · Domain: **maintenance** · Core: **4** · Product-lineage groups: **7**

Background/event notifications

- **Core (4):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [ente/ente](<profiles/R04-ente-ente.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Optional (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 43/50.

### 115. Write metadata into original/media files — 7/50

`metadata.embedded_write` · Domain: **metadata** · Core: **3** · Product-lineage groups: **7**

Write metadata into original/media files

- **Core (3):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Optional (3):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Roadmap (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Explicitly unsupported (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 41/50.

### 116. Import/sync from external cloud media providers — 7/50

`library.cloud_import` · Domain: **library** · Core: **2** · Product-lineage groups: **6**

Import/sync from external cloud media providers

- **Core (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Optional (5):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Explicitly unsupported (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 42/50.

### 117. Portable/no-install executable distribution — 6/50

`deployment.portable` · Domain: **deployment** · Core: **6** · Product-lineage groups: **6**

Portable/no-install executable distribution

- **Core (6):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 44/50.

### 118. Preview/dry-run actions without executing — 6/50

`duplicates.dry_run` · Domain: **duplicates** · Core: **6** · Product-lineage groups: **6**

Preview/dry-run actions without executing

- **Core (6):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 44/50.

### 119. Export duplicate reports/plans — 6/50

`duplicates.report_export` · Domain: **duplicates** · Core: **6** · Product-lineage groups: **6**

Export duplicate reports/plans

- **Core (6):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 44/50.

### 120. Restrict duplicate scan by size — 6/50

`duplicates.size_bounds` · Domain: **duplicates** · Core: **6** · Product-lineage groups: **6**

Restrict duplicate scan by size

- **Core (6):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 44/50.

### 121. Assign/edit GPS coordinates — 6/50

`metadata.gps_write` · Domain: **metadata** · Core: **6** · Product-lineage groups: **6**

Assign/edit GPS coordinates

- **Core (6):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Roadmap (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Explicitly unsupported (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 42/50.

### 122. Rating/pick filtering — 6/50

`search.ratings` · Domain: **search** · Core: **6** · Product-lineage groups: **6**

Rating/pick filtering

- **Core (6):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 44/50.

### 123. Sort by file size — 6/50

`sort.file_size` · Domain: **sort** · Core: **6** · Product-lineage groups: **6**

Sort by file size

- **Core (6):** [deckerst/aves](<profiles/R14-deckerst-aves.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 44/50.

### 124. Sort by filename/path — 6/50

`sort.filename` · Domain: **sort** · Core: **6** · Product-lineage groups: **6**

Sort by filename/path

- **Core (6):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 44/50.

### 125. iOS client/application — 6/50

`deployment.ios` · Domain: **deployment** · Core: **5** · Product-lineage groups: **6**

iOS client/application

- **Core (5):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Roadmap (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 43/50.

### 126. Batch filename renaming — 6/50

`library.bulk_rename` · Domain: **library** · Core: **5** · Product-lineage groups: **6**

Batch filename renaming

- **Core (5):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 44/50.

### 127. Collaborative/shared album contributions — 6/50

`sharing.collaborative_albums` · Domain: **sharing** · Core: **5** · Product-lineage groups: **6**

Collaborative/shared album contributions

- **Core (5):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 44/50.

### 128. Automatic filesystem change monitoring — 6/50

`library.filesystem_watch` · Domain: **library** · Core: **3** · Product-lineage groups: **6**

Automatic filesystem change monitoring

- **Core (3):** [ente/ente](<profiles/R04-ente-ente.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Optional (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Plugin/integration (1):** [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 44/50.

### 129. Online place/geocoding service — 6/50

`geo.online_geocoding` · Domain: **geo** · Core: **2** · Product-lineage groups: **5**

Online place/geocoding service

- **Core (2):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Optional (4):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>), [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 44/50.

### 130. Hardware-accelerated video encoding — 6/50

`editing.hardware_encoding` · Domain: **editing** · Core: **1** · Product-lineage groups: **6**

Hardware-accelerated video encoding

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Optional (5):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [photoview/photoview](<profiles/R11-photoview-photoview.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 44/50.

### 131. Automated media-content moderation — 6/50

`ai.content_moderation` · Domain: **ai** · Core: **0** · Product-lineage groups: **6**

Automated safety/content classification and moderation of media, often using an optional external service. Local-only NSFW detection and manual sensitive labels remain separate.

- **Optional (6):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Explicitly unsupported (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 43/50.

### 132. Remote/cloud inference integration — 6/50

`ai.remote_inference` · Domain: **ai** · Core: **0** · Product-lineage groups: **6**

Remote/cloud inference integration

- **Optional (5):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Plugin/integration (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Explicitly unsupported (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 43/50.

### 133. Location/trip albums — 5/50

`albums.locations` · Domain: **albums** · Core: **5** · Product-lineage groups: **4**

Location/trip albums

- **Core (5):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 45/50.

### 134. Protected/reference directories or keeper locations — 5/50

`duplicates.reference_folders` · Domain: **duplicates** · Core: **5** · Product-lineage groups: **5**

Protected/reference directories or keeper locations

- **Core (5):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 45/50.

### 135. Color/exposure/basic adjustments — 5/50

`editing.adjustments` · Domain: **editing** · Core: **5** · Product-lineage groups: **5**

Color/exposure/basic adjustments

- **Core (5):** [ente/ente](<profiles/R04-ente-ente.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 45/50.

### 136. Home-screen photo/album widgets — 5/50

`integration.home_widgets` · Domain: **integration** · Core: **5** · Product-lineage groups: **4**

Provide configurable home-screen widgets showing photos, folders, albums, people or memories; exact widget types vary.

- **Core (5):** [ente/ente](<profiles/R04-ente-ente.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 45/50.

### 137. Upload into a managed library — 5/50

`library.managed_upload` · Domain: **library** · Core: **5** · Product-lineage groups: **5**

Upload into a managed library. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (5):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 45/50.

### 138. Separate user-selectable libraries/catalogues, not merely multiple users or folders — 5/50

`library.multiple_libraries` · Domain: **library** · Core: **5** · Product-lineage groups: **5**

Separate user-selectable libraries/catalogues, not merely multiple users or folders

- **Core (5):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 45/50.

### 139. Rename selected file — 5/50

`library.rename` · Domain: **library** · Core: **5** · Product-lineage groups: **5**

Rename selected file. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (5):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 45/50.

### 140. Hierarchical/relational tags — 5/50

`metadata.hierarchical_tags` · Domain: **metadata** · Core: **5** · Product-lineage groups: **5**

Hierarchical/relational tags

- **Core (5):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 45/50.

### 141. Hidden folder/album visibility controls — 5/50

`privacy.hidden_folders` · Domain: **privacy** · Core: **5** · Product-lineage groups: **4**

Hide/unhide filesystem-backed media folders/albums using application state or media-scan markers. This is not an encryption guarantee.

- **Core (5):** [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 45/50.

### 142. Undo file-changing actions — 5/50

`safety.undo` · Domain: **safety** · Core: **5** · Product-lineage groups: **5**

Undo file-changing actions

- **Core (5):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 45/50.

### 143. Rule-based dynamic albums — 5/50

`albums.smart` · Domain: **albums** · Core: **4** · Product-lineage groups: **4**

Rule-based dynamic albums

- **Core (4):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 45/50.

### 144. Thumbnail/side-by-side duplicate review — 5/50

`duplicates.visual_review` · Domain: **duplicates** · Core: **4** · Product-lineage groups: **5**

Thumbnail/side-by-side duplicate review

- **Core (4):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Roadmap (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 44/50.

### 145. Audio playback — 5/50

`browse.audio_playback` · Domain: **browse** · Core: **3** · Product-lineage groups: **5**

Audio playback

- **Core (3):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Optional (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 45/50.

### 146. Cluster map markers — 5/50

`geo.clustering` · Domain: **geo** · Core: **3** · Product-lineage groups: **5**

Cluster map markers

- **Core (3):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Optional (2):** [photoview/photoview](<profiles/R11-photoview-photoview.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 45/50.

### 147. Offline reverse geocoding/place lookup — 5/50

`geo.offline_geocoding` · Domain: **geo** · Core: **3** · Product-lineage groups: **5**

Offline reverse geocoding/place lookup

- **Core (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Optional (2):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 45/50.

### 148. Mobile camera-roll backup/upload — 5/50

`library.mobile_backup` · Domain: **library** · Core: **2** · Product-lineage groups: **5**

Mobile camera-roll backup/upload

- **Core (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>)
- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (2):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Roadmap (2):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 43/50.

### 149. WebDAV integration — 5/50

`integration.webdav` · Domain: **integration** · Core: **1** · Product-lineage groups: **5**

WebDAV integration

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Optional (4):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Unclear (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 44/50.

### 150. Publish/export to external social/photo services — 5/50

`sharing.social_export` · Domain: **sharing** · Core: **1** · Product-lineage groups: **5**

Publish/export to external social/photo services

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Optional (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Plugin/integration (3):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 45/50.

### 151. OpenID Connect single sign-on — 5/50

`integration.oidc` · Domain: **integration** · Core: **0** · Product-lineage groups: **5**

Authenticate with an OIDC identity provider; identity linking, role synchronization and platform support vary.

- **Optional (5):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 45/50.

### 152. GPU-accelerated ML — 5/50

`performance.gpu_ml` · Domain: **performance** · Core: **0** · Product-lineage groups: **5**

GPU-accelerated ML

- **Optional (5):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 45/50.

### 153. Nested albums/collections — 4/50

`albums.nested` · Domain: **albums** · Core: **4** · Product-lineage groups: **4**

Nested albums/collections

- **Core (4):** [photoview/photoview](<profiles/R11-photoview-photoview.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Roadmap (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Explicitly unsupported (2):** [ente/ente](<profiles/R04-ente-ente.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 43/50.

### 154. On-this-day / past-years memories — 4/50

`browse.memories` · Domain: **browse** · Core: **4** · Product-lineage groups: **4**

Resurface media from corresponding dates or past years. Curated notifications, widgets and filters vary by repository.

- **Core (4):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 46/50.

### 155. Virtualized/lazy visible-row rendering, not merely image caching — 4/50

`browse.virtualization` · Domain: **browse** · Core: **4** · Product-lineage groups: **4**

Virtualized/lazy visible-row rendering, not merely image caching

- **Core (4):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 46/50.

### 156. Recognize existing hard links during duplicate scans — 4/50

`duplicates.existing_hardlink_policy` · Domain: **duplicates** · Core: **4** · Product-lineage groups: **4**

Account for multiple paths referring to the same underlying file and control or document whether they count as duplicates. This does not imply creating hard links.

- **Core (4):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 46/50.

### 157. Replace duplicate files with hard links — 4/50

`duplicates.hardlinks` · Domain: **duplicates** · Core: **4** · Product-lineage groups: **4**

Replace duplicate files with hard links

- **Core (4):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 46/50.

### 158. Attribute-based possible-duplicate detection — 4/50

`duplicates.metadata_candidates` · Domain: **duplicates** · Core: **4** · Product-lineage groups: **4**

Identify candidate duplicates using names, sizes, dates or dimensions without claiming content equality. Available attributes and false-positive risks vary.

- **Core (4):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 46/50.

### 159. Replace duplicates with symbolic links — 4/50

`duplicates.symlinks` · Domain: **duplicates** · Core: **4** · Product-lineage groups: **4**

Replace duplicates with symbolic links

- **Core (4):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 46/50.

### 160. Photo collage/layout generation — 4/50

`editing.collage` · Domain: **editing** · Core: **4** · Product-lineage groups: **4**

Photo collage/layout generation

- **Core (4):** [ente/ente](<profiles/R04-ente-ente.md>), [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Unclear (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 45/50.

### 161. Image compression / encoder-quality controls — 4/50

`editing.image_compression` · Domain: **editing** · Core: **4** · Product-lineage groups: **4**

Reduce image output size or configure encoder quality. Algorithms, targets, metadata handling and animation limits vary.

- **Core (4):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 46/50.

### 162. Rule-based burst-photo grouping — 4/50

`library.burst_stacking` · Domain: **library** · Core: **4** · Product-lineage groups: **4**

Group related burst shots using supported metadata, filename patterns, timing or other rules. This does not imply automatic best-shot scoring.

- **Core (4):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [simulot/immich-go](<profiles/R08-simulot-immich-go.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 46/50.

### 163. Reset/rebuild cache/index — 4/50

`maintenance.cache_reset` · Domain: **maintenance** · Core: **4** · Product-lineage groups: **4**

Reset/rebuild cache/index

- **Core (4):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 46/50.

### 164. Dimensions/resolution filtering — 4/50

`search.dimensions` · Domain: **search** · Core: **4** · Product-lineage groups: **4**

Dimensions/resolution filtering

- **Core (4):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 46/50.

### 165. File-size filtering — 4/50

`search.file_size` · Domain: **search** · Core: **4** · Product-lineage groups: **4**

File-size filtering

- **Core (4):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 46/50.

### 166. Basic library/album/media text search — 4/50

`search.library_text` · Domain: **search** · Core: **4** · Product-lineage groups: **4**

Text search over documented library entities; arbitrary metadata, Boolean, OCR or semantic search are not implied.

- **Core (4):** [photoview/photoview](<profiles/R11-photoview-photoview.md>), [electerious/Lychee](<profiles/R12-electerious-lychee.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 46/50.

### 167. Capacity and file restrictions — 4/50

`sharing.upload_quotas` · Domain: **sharing** · Core: **4** · Product-lineage groups: **4**

Capacity and file restrictions. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (4):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 46/50.

### 168. Text recognition in images — 4/50

`ai.ocr` · Domain: **ai** · Core: **3** · Product-lineage groups: **4**

Text recognition in images

- **Core (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Optional (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Unclear (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 45/50.

### 169. Albums/collections organized by people — 4/50

`albums.people` · Domain: **albums** · Core: **3** · Product-lineage groups: **4**

Albums/collections organized by people

- **Core (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Plugin/integration (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 46/50.

### 170. Folder/type storage-size distributions — 4/50

`analytics.storage_distribution` · Domain: **analytics** · Core: **3** · Product-lineage groups: **4**

Folder/type storage-size distributions

- **Core (3):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Optional (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 46/50.

### 171. Preserve metadata during export/conversion — 4/50

`metadata.preserve_export` · Domain: **metadata** · Core: **3** · Product-lineage groups: **4**

Preserve metadata during export/conversion

- **Core (3):** [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Optional (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 46/50.

### 172. Chunked large-file uploads — 4/50

`performance.chunked_upload` · Domain: **performance** · Core: **3** · Product-lineage groups: **4**

Transfer files in chunks and assemble/finalize them at the destination. Chunking alone does not establish restart-resume semantics.

- **Core (3):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 46/50.

### 173. Per-account storage capacity quotas — 4/50

`sharing.storage_quotas` · Domain: **sharing** · Core: **3** · Product-lineage groups: **4**

Set/enforce total account storage allocations. Per-file size, upload frequency and concurrent-transfer limits are separate.

- **Core (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 46/50.

### 174. Visitor gallery for selected directories — 4/50

`sharing.public_gallery` · Domain: **sharing** · Core: **2** · Product-lineage groups: **4**

Visitor gallery for selected directories. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Optional (2):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 46/50.

### 175. Time-bucket photo counts/charts — 3/50

`analytics.timeline_counts` · Domain: **analytics** · Core: **3** · Product-lineage groups: **3**

Time-bucket photo counts/charts

- **Core (3):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [guardian/grid](<profiles/R49-guardian-grid.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 47/50.

### 176. Side-by-side/comparison/culling viewer — 3/50

`browse.compare` · Domain: **browse** · Core: **3** · Product-lineage groups: **3**

Side-by-side/comparison/culling viewer

- **Core (3):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 47/50.

### 177. Custom colors, themes and controls — 3/50

`browse.theme_customization` · Domain: **browse** · Core: **3** · Product-lineage groups: **3**

Custom colors, themes and controls. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (3):** [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 47/50.

### 178. Find empty directories — 3/50

`cleanup.empty_folders` · Domain: **cleanup** · Core: **3** · Product-lineage groups: **3**

Find empty directories

- **Core (3):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 47/50.

### 179. Detect whole duplicate folders/trees — 3/50

`duplicates.folders` · Domain: **duplicates** · Core: **3** · Product-lineage groups: **3**

Detect whole duplicate folders/trees

- **Core (3):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 47/50.

### 180. Draw, annotate or add text/stickers to images — 3/50

`editing.annotations` · Domain: **editing** · Core: **3** · Product-lineage groups: **3**

Add drawn or composited annotations to image pixels; this is distinct from searchable metadata captions.

- **Core (3):** [ente/ente](<profiles/R04-ente-ente.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>), [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 47/50.

### 181. HDR photo decoding/display — 3/50

`formats.hdr` · Domain: **formats** · Core: **3** · Product-lineage groups: **3**

Decode or display supported HDR photos, including Ultra HDR/gain-map variants; device and format constraints are preserved in repository evidence.

- **Core (3):** [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 47/50.

### 182. Keep companion sidecars/assets together during operations — 3/50

`formats.sidecar_pairs` · Domain: **formats** · Core: **3** · Product-lineage groups: **3**

Keep companion sidecars/assets together during operations

- **Core (3):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 47/50.

### 183. Display route/track overlays — 3/50

`geo.track_overlay` · Domain: **geo** · Core: **3** · Product-lineage groups: **3**

Display route/track overlays

- **Core (3):** [deckerst/aves](<profiles/R14-deckerst-aves.md>), [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 47/50.

### 184. Set desktop wallpaper — 3/50

`integration.wallpaper` · Domain: **integration** · Core: **3** · Product-lineage groups: **2**

Set desktop wallpaper. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (3):** [julyx10/lap](<profiles/R19-julyx10-lap.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>)
- **Not established by this research:** 47/50.

### 185. Archive media out of the main timeline — 3/50

`library.archive` · Domain: **library** · Core: **3** · Product-lineage groups: **3**

Declutter the main timeline without deleting originals. Filesystem archive-folder moves, inbox culling workflows and social-post archives remain distinct.

- **Core (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 47/50.

### 186. Local application access lock — 3/50

`privacy.app_lock` · Domain: **privacy** · Core: **3** · Product-lineage groups: **2**

Gate application or media access with a PIN, password or device authentication. Access locks alone do not imply encrypted files.

- **Core (3):** [ente/ente](<profiles/R04-ente-ente.md>), [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>)
- **Not established by this research:** 47/50.

### 187. Account two-factor authentication — 3/50

`privacy.two_factor_auth` · Domain: **privacy** · Core: **3** · Product-lineage groups: **3**

Require a second authentication factor for the media service account. Supported factors and recovery policies vary; authenticator products are not inventoried as photo features.

- **Core (3):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 47/50.

### 188. Persistent checksum/bit-rot/integrity verification — 3/50

`safety.integrity_check` · Domain: **safety** · Core: **3** · Product-lineage groups: **3**

Persistent checksum/bit-rot/integrity verification

- **Core (3):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 47/50.

### 189. Saved reusable searches — 3/50

`search.saved_queries` · Domain: **search** · Core: **3** · Product-lineage groups: **3**

Saved reusable searches

- **Core (3):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>), [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 47/50.

### 190. Free device space after verified backup — 3/50

`cleanup.backed_up_device_copies` · Domain: **cleanup** · Core: **2** · Product-lineage groups: **3**

Remove backed-up device copies while retaining the library/server originals; selection, retention and verification policies are repository-specific.

- **Core (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [ente/ente](<profiles/R04-ente-ente.md>)
- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 47/50.

### 191. Trim/split/join video — 3/50

`editing.video_trim_join` · Domain: **editing** · Core: **2** · Product-lineage groups: **3**

Trim/split/join video

- **Core (2):** [ente/ente](<profiles/R04-ente-ente.md>), [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Optional (1):** [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>)
- **Not established by this research:** 47/50.

### 192. Edit catalogue/display filenames — 3/50

`metadata.display_name_edit` · Domain: **metadata** · Core: **2** · Product-lineage groups: **3**

Change displayed or recorded media names. Physical filesystem/object-key renaming is not implied unless separately documented.

- **Core (2):** [ente/ente](<profiles/R04-ente-ente.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 47/50.

### 193. Color-based search/filter — 3/50

`search.colors` · Domain: **search** · Core: **2** · Product-lineage groups: **3**

Color-based search/filter

- **Core (2):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 47/50.

### 194. Comments and reactions on shared media/albums — 3/50

`sharing.comments_reactions` · Domain: **sharing** · Core: **2** · Product-lineage groups: **3**

Allow comments, likes or reactions associated with shared media or albums. Audience, encryption, moderation and per-item scope vary.

- **Core (2):** [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 47/50.

### 195. Generated natural-language captions — 3/50

`ai.captioning` · Domain: **ai** · Core: **1** · Product-lineage groups: **3**

Generated natural-language captions

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Optional (2):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Unclear (2):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 45/50.

### 196. Perceptually/frame/audio similar video detection — 3/50

`duplicates.similar_videos` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **3**

Perceptually/frame/audio similar video detection

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Optional (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Plugin/integration (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 47/50.

### 197. Multilingual semantic queries — 3/50

`search.multilingual_semantic` · Domain: **search** · Core: **1** · Product-lineage groups: **3**

Semantic media search accepts multiple query languages, sometimes through an optional model. This is separate from UI translation.

- **Core (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Optional (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 47/50.

### 198. Short share/image URLs — 3/50

`sharing.short_urls` · Domain: **sharing** · Core: **1** · Product-lineage groups: **3**

Generate short URLs natively or via a configured shortener. Shortening is not an access-control/privacy mechanism.

- **Core (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Optional (2):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 47/50.

### 199. Configurable catalogue database backend — 3/50

`storage.database_choices` · Domain: **storage** · Core: **1** · Product-lineage groups: **3**

Document support for alternative database engines; maturity and migration constraints vary by engine and repository.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Optional (2):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Not established by this research:** 47/50.

### 200. Managed hosting/cloud service option — 3/50

`deployment.managed_cloud` · Domain: **deployment** · Core: **0** · Product-lineage groups: **3**

A documented hosted alternative to operating the software yourself, directly or through a partner. Pricing, provider duties and edition entitlements vary.

- **Optional (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Paid (2):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 47/50.

### 201. Optional FTP transfer settings — 3/50

`integration.ftp_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **3**

Optional FTP transfer settings. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Optional (3):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 47/50.

## Rare: 1–2 repositories

### 202. Mark missed faces manually — 2/50

`ai.manual_face_regions` · Domain: **ai** · Core: **2** · Product-lineage groups: **2**

Mark missed faces manually. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Roadmap (1):** [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 47/50.

### 203. Automatic event albums — 2/50

`albums.events` · Domain: **albums** · Core: **2** · Product-lineage groups: **1**

Automatic event albums

- **Core (2):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 48/50.

### 204. People co-occurrence graph — 2/50

`analytics.people_cooccurrence_graph` · Domain: **analytics** · Core: **2** · Product-lineage groups: **1**

Compute or expose graph relationships for people appearing in photos together. API data and interactive visualization availability differ; this does not establish real-world social relationships.

- **Core (2):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 48/50.

### 205. Hidden-tag archive filtering — 2/50

`browse.hidden_items` · Domain: **browse** · Core: **2** · Product-lineage groups: **2**

Hidden-tag archive filtering. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 48/50.

### 206. Public square and image details — 2/50

`browse.public_gallery` · Domain: **browse** · Core: **2** · Product-lineage groups: **2**

Public square and image details. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 48/50.

### 207. Manually stack related media — 2/50

`browse.stacks` · Domain: **browse** · Core: **2** · Product-lineage groups: **2**

Group related assets into stacks, retain members and expose a cover/stack view. Automatic burst heuristics are a separate feature.

- **Core (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 48/50.

### 208. Find empty files — 2/50

`cleanup.empty_files` · Domain: **cleanup** · Core: **2** · Product-lineage groups: **2**

Find empty files

- **Core (2):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 48/50.

### 209. Find broken or invalid symbolic links — 2/50

`cleanup.invalid_symlinks` · Domain: **cleanup** · Core: **2** · Product-lineage groups: **2**

Identify links whose targets are missing or otherwise invalid; some implementations also detect cycles.

- **Core (2):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 48/50.

### 210. Find largest files — 2/50

`cleanup.large_files` · Domain: **cleanup** · Core: **2** · Product-lineage groups: **2**

Find largest files

- **Core (2):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 48/50.

### 211. Find temporary/cache/junk files — 2/50

`cleanup.temporary_junk` · Domain: **cleanup** · Core: **2** · Product-lineage groups: **2**

Find temporary/cache/junk files

- **Core (2):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 48/50.

### 212. Duplicate/similar music/audio detection — 2/50

`duplicates.audio` · Domain: **duplicates** · Core: **2** · Product-lineage groups: **2**

Duplicate/similar music/audio detection

- **Core (2):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>)
- **Not established by this research:** 48/50.

### 213. Explicit byte comparison to verify equality — 2/50

`duplicates.byte_compare` · Domain: **duplicates** · Core: **2** · Product-lineage groups: **2**

Explicit byte comparison to verify equality

- **Core (2):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Explicitly unsupported (2):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 46/50.

### 214. Preserve metadata when deduplicating — 2/50

`duplicates.metadata_merge` · Domain: **duplicates** · Core: **2** · Product-lineage groups: **2**

Preserve metadata when deduplicating. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 48/50.

### 215. Copy-on-write/reflink deduplication — 2/50

`duplicates.reflinks` · Domain: **duplicates** · Core: **2** · Product-lineage groups: **2**

Copy-on-write/reflink deduplication

- **Core (2):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>), [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 48/50.

### 216. Persist reviewed/ignored duplicate decisions across runs — 2/50

`duplicates.remember_decisions` · Domain: **duplicates** · Core: **2** · Product-lineage groups: **2**

Persist reviewed/ignored duplicate decisions across runs

- **Core (2):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 48/50.

### 217. Creative-project file previews — 2/50

`formats.project_previews` · Domain: **formats** · Core: **2** · Product-lineage groups: **2**

Preview supported creative-project formats, often using flattened or embedded previews. Supported formats and full-view versus thumbnail-only behavior differ.

- **Core (2):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 48/50.

### 218. Web image formats — 2/50

`formats.web_images` · Domain: **formats** · Core: **2** · Product-lineage groups: **2**

Web image formats. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 48/50.

### 219. System viewer/editor/picker integration — 2/50

`integration.android_picker` · Domain: **integration** · Core: **2** · Product-lineage groups: **2**

Manifest registers PICK/GET_CONTENT for image/video, VIEW, photo EDIT/CROP and camera review intents.

- **Core (2):** [deckerst/aves](<profiles/R14-deckerst-aves.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>)
- **Not established by this research:** 48/50.

### 220. Android printing — 2/50

`integration.print` · Domain: **integration** · Core: **2** · Product-lineage groups: **2**

PrintHelper renders the selected bitmap with fit-to-page scaling and reports failures.

- **Core (2):** [deckerst/aves](<profiles/R14-deckerst-aves.md>), [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 48/50.

### 221. Persistent batch-action selection baskets — 2/50

`library.selection_baskets` · Domain: **library** · Core: **2** · Product-lineage groups: **2**

Collect media across browsing/search into a reusable working selection for later batch operations or export.

- **Core (2):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>), [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 48/50.

### 222. Rule-driven object names and folders — 2/50

`library.upload_naming_templates` · Domain: **library** · Core: **2** · Product-lineage groups: **2**

Rule-driven object names and folders. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 48/50.

### 223. Upload logs and IP location — 2/50

`maintenance.upload_audit` · Domain: **maintenance** · Core: **2** · Product-lineage groups: **2**

Upload logs and IP location. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 48/50.

### 224. Read/search generative-image prompt metadata — 2/50

`metadata.ai_prompt` · Domain: **metadata** · Core: **2** · Product-lineage groups: **2**

Read/search generative-image prompt metadata

- **Core (2):** [julyx10/lap](<profiles/R19-julyx10-lap.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 48/50.

### 225. Edit catalogue-only location coordinates — 2/50

`metadata.catalogue_geotag` · Domain: **metadata** · Core: **2** · Product-lineage groups: **2**

Add or correct locations in application metadata without establishing embedded EXIF GPS write-back.

- **Core (2):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>), [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 48/50.

### 226. Set filesystem timestamps from photo dates — 2/50

`metadata.filesystem_date_fix` · Domain: **metadata** · Core: **2** · Product-lineage groups: **2**

Set filesystem dates using photo metadata or supported fallback rules, on originals or exported copies as documented. This is separate from changing embedded capture dates.

- **Core (2):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>), [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 48/50.

### 227. Import metadata from sidecars — 2/50

`metadata.sidecar_import` · Domain: **metadata** · Core: **2** · Product-lineage groups: **2**

Read or restore metadata from supported sidecar files or export-state records. Formats, target fields and external-tool dependencies vary.

- **Core (2):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>), [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 48/50.

### 228. Browse processed assets before an ongoing scan completes — 2/50

`performance.live_browsing` · Domain: **performance** · Core: **2** · Product-lineage groups: **2**

Browse processed assets before an ongoing scan completes

- **Core (2):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>), [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>)
- **Not established by this research:** 48/50.

### 229. Progress and elapsed time — 2/50

`performance.progress_reporting` · Domain: **performance** · Core: **2** · Product-lineage groups: **2**

Progress and elapsed time. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 48/50.

### 230. Hidden media section — 2/50

`privacy.hidden_media` · Domain: **privacy** · Core: **2** · Product-lineage groups: **2**

Hide selected media from ordinary collection views and expose a separate hidden area. Authentication and encryption guarantees differ and must be checked in the repository evidence.

- **Core (2):** [ente/ente](<profiles/R04-ente-ente.md>), [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 48/50.

### 231. Recheck changed files before cleanup actions — 2/50

`safety.changed_file_guards` · Domain: **safety** · Core: **2** · Product-lineage groups: **2**

Validate reviewed files before destructive/cleanup actions and skip or reject stale targets. Exact checks and overrides vary.

- **Core (2):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>), [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 48/50.

### 232. Uploader deletion links — 2/50

`sharing.deletion_capability_links` · Domain: **sharing** · Core: **2** · Product-lineage groups: **2**

Uploader deletion links. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 48/50.

### 233. Copy URL, Markdown, HTML or BBCode — 2/50

`sharing.embed_codes` · Domain: **sharing** · Core: **2** · Product-lineage groups: **2**

Copy URL, Markdown, HTML or BBCode. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>), [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 48/50.

### 234. IP allow/block controls — 2/50

`sharing.ip_access_control` · Domain: **sharing** · Core: **2** · Product-lineage groups: **2**

IP allow/block controls. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>), [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 48/50.

### 235. Share a resized version — 2/50

`sharing.resized_copy` · Domain: **sharing** · Core: **2** · Product-lineage groups: **2**

Share a resized version. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (2):** [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>), [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 48/50.

### 236. Share a viewed image — 2/50

`sharing.system_share` · Domain: **sharing** · Core: **2** · Product-lineage groups: **2**

SwiftUI ShareLink exports the displayed image with the search text used as its share preview; original-byte or EXIF preservation is not established.

- **Core (2):** [deckerst/aves](<profiles/R14-deckerst-aves.md>), [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 48/50.

### 237. Random collection order — 2/50

`sort.random` · Domain: **sort** · Core: **2** · Product-lineage groups: **2**

Random sorting is added in v1.15.9.

- **Core (2):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>), [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 48/50.

### 238. Document previews and PDF reader — 2/50

`browse.document_preview` · Domain: **browse** · Core: **1** · Product-lineage groups: **2**

Configured PDF/SVG/EPS/TIFF/PSD/AI types can have generated previews; v15 adds an inline PDF reader. Other office formats may be downloadable only with generic icons. Cloud premium formats require Team+.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Optional (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 48/50.

### 239. Environment-driven site customization — 2/50

`deployment.site_branding` · Domain: **deployment** · Core: **1** · Product-lineage groups: **2**

Environment-driven site customization. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 48/50.

### 240. Cast photos/albums/video to another screen — 2/50

`integration.cast` · Domain: **integration** · Core: **1** · Product-lineage groups: **2**

Cast supported media or album slideshows to a receiving screen. Protocol, client-platform, networking and video support vary.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Optional (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 48/50.

### 241. Time-limited hosted-file lifecycle — 2/50

`library.file_expiry` · Domain: **library** · Core: **1** · Product-lineage groups: **2**

Time-limited hosted-file lifecycle. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 48/50.

### 242. Scheduled library scans/indexing — 2/50

`library.scheduled_indexing` · Domain: **library** · Core: **1** · Product-lineage groups: **2**

Configure recurring or delayed library scans/indexing. Frequency, concurrency and trigger behavior vary.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Optional (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 48/50.

### 243. Extract/display image color palettes — 2/50

`metadata.color_palette` · Domain: **metadata** · Core: **1** · Product-lineage groups: **2**

Extract or display dominant image colors/a palette. Color-based search and pixel-color editing are not implied.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 48/50.

### 244. Custom typed field templates — 2/50

`metadata.custom_fields` · Domain: **metadata** · Core: **1** · Product-lineage groups: **2**

Custom typed field templates. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 48/50.

### 245. Import existing face/person metadata — 2/50

`metadata.face_region_import` · Domain: **metadata** · Core: **1** · Product-lineage groups: **2**

Reuse person names or face regions from supported embedded or sidecar metadata. This is distinct from newly detecting faces with ML.

- **Core (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Optional (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 48/50.

### 246. At-rest/library/vault encryption — 2/50

`privacy.at_rest_encryption` · Domain: **privacy** · Core: **1** · Product-lineage groups: **2**

At-rest/library/vault encryption

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Plugin/integration (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 48/50.

### 247. Control or disable telemetry — 2/50

`privacy.telemetry_control` · Domain: **privacy** · Core: **1** · Product-lineage groups: **2**

Provide an explicit telemetry setting or opt-out. Presence of an opt-out does not mean telemetry is disabled by default.

- **Core (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 48/50.

### 248. Search recognized text in images — 2/50

`search.ocr` · Domain: **search** · Core: **1** · Product-lineage groups: **2**

Search recognized text in images

- **Core (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Optional (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Roadmap (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Explicitly unsupported (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 46/50.

### 249. Require login to browse the gallery — 2/50

`sharing.private_site` · Domain: **sharing** · Core: **1** · Product-lineage groups: **2**

Restrict ordinary gallery/site viewing to authenticated users; per-share account policies are separate.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Optional (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Not established by this research:** 48/50.

### 250. HLS video streaming — 2/50

`browse.hls_streaming` · Domain: **browse** · Core: **0** · Product-lineage groups: **2**

Optional HLS requires FFmpeg and defaults off; configurable bitrate governs generated streams.

- **Optional (2):** [ente/ente](<profiles/R04-ente-ente.md>), [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 48/50.

### 251. Configurable map provider or base style — 2/50

`geo.custom_map_provider` · Domain: **geo** · Core: **0** · Product-lineage groups: **2**

Select/configure a map tile provider or style URL. This alone does not establish offline maps or offline geocoding.

- **Optional (2):** [immich-app/immich](<profiles/R01-immich-app-immich.md>), [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 48/50.

### 252. External image-hosting service adapters — 2/50

`integration.hosting_services` · Domain: **integration** · Core: **0** · Product-lineage groups: **2**

Integrate external image-hosting services for uploading and, in some cases, management/deletion. Legacy service adapters are not a guarantee of current provider availability.

- **Optional (2):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>), [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 48/50.

### 253. SFTP storage integration — 2/50

`integration.sftp_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **2**

Use SFTP destinations for supported media upload/storage/management operations; capabilities and connection configuration vary.

- **Optional (2):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>), [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 48/50.

### 254. ShareX capture/upload client — 2/50

`integration.sharex` · Domain: **integration** · Core: **0** · Product-lineage groups: **2**

ShareX capture/upload client. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Plugin/integration (2):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>), [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 48/50.

### 255. Custom-domain album links — 2/50

`sharing.custom_domains` · Domain: **sharing** · Core: **0** · Product-lineage groups: **2**

Custom-domain album links. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Optional (2):** [ente/ente](<profiles/R04-ente-ente.md>), [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 48/50.

### 256. Screenshot/document categories — 1/50

`ai.document_classification` · Domain: **ai** · Core: **1** · Product-lineage groups: **1**

Screenshots are detected on scan; document inference combines OCR and content labels, so OCR is needed for automatic documents. Manual/bulk category corrections persist across rescans and support undo.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 257. Read Apple-generated captions — 1/50

`ai.read_existing_captions` · Domain: **ai** · Core: **1** · Product-lineage groups: **1**

PhotoInfo exposes mediaanalysisd metadata and an AI caption when one exists; OSXPhotos is reading existing analysis, not generating captions itself.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 258. Expose Apple's hidden classification labels — 1/50

`ai.read_existing_labels` · Domain: **ai** · Core: **1** · Product-lineage groups: **1**

Read normalized labels produced by Photos image categorization and use them in queries or export keyword templates; labels originate from Photos, not a new OSXPhotos classifier.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 259. Read stored aesthetic/curation scores — 1/50

`ai.read_existing_scores` · Domain: **ai** · Core: **1** · Product-lineage groups: **1**

Photos 5+ ScoreInfo exposes overall, composition, blur/focus, noise and other existing scores; the author explicitly has not fully decoded their semantics. Not claimed as newly computed culling or best-shot inference.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 260. Artistic style classifier — 1/50

`ai.style_classification` · Domain: **ai** · Core: **1** · Product-lineage groups: **1**

Classifies style labels such as geometric, minimalist and noir, distinct from literal object labels.

- **Core (1):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 49/50.

### 261. Sample video frames for people — 1/50

`ai.video_faces` · Domain: **ai** · Core: **1** · Product-lineage groups: **1**

Up to eight frames from 5%–95%, at most one/second, consolidate matching identities using largest face. Faces retain timestamp for seek-to-person; clips under two seconds use first frame only.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 262. Many-to-many album collections — 1/50

`albums.collections` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Private labels such as Travel/Family group an album into several collections; deleting a collection preserves albums/photos. Not a nested filesystem hierarchy.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 263. Automatic thing and scene albums — 1/50

`albums.content_categories` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Places365 attributes and categories each generate owner-scoped AlbumThing collections with representative cover photos.

- **Core (1):** [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 49/50.

### 264. Choose album cover — 1/50

`albums.cover_selection` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

API assigns a selected cover photo or resets the album cover.

- **Core (1):** [photoview/photoview](<profiles/R11-photoview-photoview.md>)
- **Not established by this research:** 49/50.

### 265. Custom album slugs with redirects — 1/50

`albums.custom_urls` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Self-hosted titles generate slugs; numeric links redirect to current slug and historical slugs temporarily redirect. Renaming title alone keeps URL; editing/clearing frees the old slug for reassignment.

- **Core (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 266. Portable album file copies — 1/50

`albums.duplicate_copy` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

duplicate-copy materializes files per album, trading substantially more space for portability across systems.

- **Core (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 267. Star-driven album covers — 1/50

`albums.favorite_cover_selection` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

FAQ says covers are selected automatically from starred photos and upload order; starring an image influences the album thumbnail.

- **Core (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 268. Space-saving album links — 1/50

`albums.filesystem_links` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Default album strategy creates Windows .lnk shortcuts or Unix symlinks to originals using relative target paths; failed link creation falls back to materializing a file.

- **Core (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 269. Display-only album merging — 1/50

`albums.folder_merge_views` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Merge same-name albums across volumes or fold subfolders/parent subfolders into one view, with unmerge; no file movement or renaming occurs.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 270. Ignore album-only assets — 1/50

`albums.ignore_mode` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

nothing mode keeps year-folder photos without albums; documentation explicitly warns this omits Archive/Trash assets outside year folders.

- **Core (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 271. Cross-folder media-type albums — 1/50

`albums.media_type_collections` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Virtual Photos/Videos/GIF/RAW albums cover all folders and can be shown/hidden as a Library section.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 272. Lock album membership — 1/50

`albums.membership_lock` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

API-enforced lock blocks adding/removing photos including uploads, but not editing/deleting underlying photos, renaming/sharing album or deleting album.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 273. Scheduled photo habits — 1/50

`albums.photo_rituals` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Mobile rituals link an owned album to weekdays/reminders and track capture-date-based scheduled-day streaks. Ritual camera supports up to 20 photos/session, not video; ritual settings stay local although the album syncs.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 274. Pinned albums — 1/50

`albums.pin` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Pin/unpin updates local album settings and re-sorts the grid.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 275. Album pins, groups and sections — 1/50

`albums.presentation_groups` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Pin albums, choose covers, create collapsible named groups and override automatic Common/Apps/Other sections; deleting a group does not remove folders.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 276. Reconstruct album memberships — 1/50

`albums.takeout_reconstruction` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Groups identical exported instances across year/album folders and merges their album associations before output.

- **Core (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 277. AI Things and caption hashtag albums — 1/50

`albums.things` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Object/scene classifications form Things albums separate from user tags; caption hashtags remain visible independent of selected tagging model.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 278. Uncategorized catch-all — 1/50

`albums.uncategorized_safety` · Domain: **albums** · Core: **1** · Product-lineage groups: **1**

Removing the last album membership or watched-folder file retains the asset in Uncategorized. Cleaning removes only entries also present in an album the user owns.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 279. Snapshot JSON/Markdown reports — 1/50

`analytics.analysis_export` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Exports current-directory analysis with depth 1–6, optional full paths, configurable entry limits and separate remainder/omission accounting; never silently rescans. Reports are evidence, not importable state or deletion authority.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 280. Locally computed annual Rewind — 1/50

`analytics.annual_rewind` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

1.6.0 shows per-user busiest day/month and most photographed people/places from Dec 20–Jan 6, computed on own server and admin-disableable.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 281. Duplicate summary and quick estimate — 1/50

`analytics.duplicate_summary` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

--summarize reports duplicate information; --quicksummary skips the slower byte-verification phase and must not be treated as fully verified equality.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 282. Face-cluster scatter visualization — 1/50

`analytics.face_embedding_plot` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Projected embeddings coloured by identity, hover thumbnails, click-to-photo and per-person highlights assist correction.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 283. Per-image viewing statistics — 1/50

`analytics.image_views` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Detail page displays stored view count and discovery offers a views category.

- **Core (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 284. Interactive place hierarchy — 1/50

`analytics.place_tree` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Country/region/town tree with horizontal/vertical/radial layouts, counts, collapse, pan and zoom.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 285. Print/digital usage tracking — 1/50

`analytics.publication_usage` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Usage records connect images to articles/editorial systems or print issue/page/layout/publication details, with pending/published/removed state resolution.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 286. Explicit incomplete-scan reporting — 1/50

`analytics.scan_coverage` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Reports omissions by permissions, read errors, exclusions, link/mount boundaries and unknown causes; unreadable is distinguished from measured empty directories.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 287. Supplier usage/quota API — 1/50

`analytics.supplier_quotas` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Current API exposes supplier usage, image usage and quota-count/quota-for-image endpoints for contractual accounting.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 288. Visits and activity reporting — 1/50

`analytics.usage_history` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Official overview describes day/month/year visit graphs, activity search and upload/edit/delete logs. These are audit analytics, not rollback-capable file journals.

- **Core (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 289. Place, Things and people word clouds — 1/50

`analytics.word_clouds` · Domain: **analytics** · Core: **1** · Product-lineage groups: **1**

Top 100 terms sized by frequency, clickable to search their photos.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 290. Wide-screen side-by-side browsing — 1/50

`browse.adaptive_split_view` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Wide windows open viewer beside timeline with current grid item outlined; smaller windows use fullscreen paging.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 291. Customizable photo management table — 1/50

`browse.admin_table` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Admin table supports sorting/filtering, persistent visible-column choice, upload-date sorting and Shift-click range selection.

- **Core (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 292. Album feed and frame display — 1/50

`browse.album_feed` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Flow page presents albums as a feed with access control and configurable base album; separate frame-display module is included free. Compact/extensively customized flow cards are SE.

- **Core (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 293. Browse actual remote assets — 1/50

`browse.cloud_files` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Cloud manager selects account/bucket/repository/root and lists objects uploaded from any device, unlike machine-local gallery history.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 294. Open unsupported viewers externally — 1/50

`browse.external_open` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Any managed file can be launched with the OS default application; import support alone does not imply internal rendering.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 295. Image histogram display — 1/50

`browse.histogram` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

README photo-browsing feature list explicitly includes histograms.

- **Core (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 296. Browser-native media and PDF previews — 1/50

`browse.inline_file_preview` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Images, video, audio and PDF are served for inline browser opening rather than forced download; browser format support still applies.

- **Core (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 297. Lazy image loading — 1/50

`browse.lazy_images` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

README says photos load when visible; this is image lazy loading, not evidence that DOM rows are virtualized.

- **Core (1):** [photoview/photoview](<profiles/R11-photoview-photoview.md>)
- **Not established by this research:** 49/50.

### 298. Folder-local dated Markdown stories — 1/50

`browse.markdown_stories` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Displays .md files near gallery/map; pg-date comments attach sections to dates, enabling narrative photo presentation.

- **Core (1):** [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 49/50.

### 299. Query-driven photo-frame mode — 1/50

`browse.photo_frame_links` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Generates a looping display link for a directory or search, suitable for kiosk apps; recurring-date queries can produce anniversary frames.

- **Core (1):** [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 49/50.

### 300. Random public-image browsing — 1/50

`browse.random` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Enable random public-image fetching independently of Explore and guest Explore.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 301. Viewer rotation — 1/50

`browse.rotate_view` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Single-media menu sends ±90 or 180-degree rotations to the image fragment; persistent original-file rotation is not established by this inspected handler.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 302. Slow-motion range control — 1/50

`browse.slow_motion_control` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

v1.14.6 adds detection/filtering of slow-motion clips and range control in the player.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 303. Chronological social feeds — 1/50

`browse.social_timelines` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Home shows followed accounts, Public shows local users and Network shows remote unmoderated content; these are chronological post feeds, not capture-date photo-library timelines.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 304. Multiple search and downloader pages — 1/50

`browse.tabs` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Create search/special/downloader pages from keyboard chooser, close via middle click and organize subscription landing pages into pages-of-pages.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 305. Group thumbnails by namespace/rating — 1/50

`browse.tag_collections` · Domain: **browse** · Core: **1** · Product-lineage groups: **1**

Collect-by combines results into groups according to selected tag namespaces or rating services, independent of file folders.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 306. Built-in camera — 1/50

`capture.camera` · Domain: **capture** · Core: **1** · Product-lineage groups: **1**

Take photographs inside the app with advanced scene and white-balance modes and front/rear camera selection.

- **Core (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 49/50.

### 307. Automatic and manual camera controls — 1/50

`capture.manual_controls` · Domain: **capture** · Core: **1** · Product-lineage groups: **1**

Official application description explicitly documents automatic and manual camera control; device-specific support is not enumerated.

- **Core (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 49/50.

### 308. Local model and download cache discovery — 1/50

`cleanup.ai_model_cache` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Surfaces large local AI models, cached downloads and temporary transfers as reclaimable-space candidates, not as photo-analysis models.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 309. Detect file extension/content mismatches — 1/50

`cleanup.bad_extensions` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Detect file extension/content mismatches

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 310. Detect problematic filenames — 1/50

`cleanup.bad_names` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Detect problematic filenames

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 311. Detect unreadable/corrupt media — 1/50

`cleanup.broken_media` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Detect unreadable/corrupt media

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 312. Owner-approved deletion suggestions — 1/50

`cleanup.collaborative_delete_suggestions` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

On mobile, album owners/admins remove others' selected photos from the album and send a deletion suggestion; actual photo owners accept/delete or reject/keep in their queue.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 313. Find unstripped binaries — 1/50

`cleanup.debug_symbols` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Optional lint type identifies binaries retaining debug symbols; it is not enabled by default.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 314. Prune an export mirror — 1/50

`cleanup.export_mirror` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

--cleanup deletes files not in the current export set, including unrelated user files unless protected by .osxphotos_keep/keep rules; dotfiles are excluded. Explicit dry run is recommended.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 315. Find invalid owner/group IDs — 1/50

`cleanup.invalid_ownership` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

badids identifies files with unresolved UID/GID ownership.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 316. Find and recover orphan candidates — 1/50

`cleanup.orphaned_library_files` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Compare UUID-named files in originals/renders/derivatives/shared scopes against catalogue IDs including trash and burst members. List candidates or copy them to a destination with collision-safe names; not automatic deletion.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 317. Rebuildable development-project cleanup — 1/50

`cleanup.project_artifacts` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Finds dependencies, caches and build directories across Node.js, Rust, Gradle, Swift, Python, .NET, Godot and CMake projects.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 318. Separate history removal and remote deletion — 1/50

`cleanup.remote_deletion` · Domain: **cleanup** · Core: **1** · Product-lineage groups: **1**

Delete from Cloud toggle decides whether gallery removal also deletes destination files. Adapters need stored uploader IDs, credentials and remote metadata; failed remote operations are reported.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 319. Heuristic review queue — 1/50

`culling.quality_review` · Domain: **culling** · Core: **1** · Product-lineage groups: **1**

Review score uses known date/GPS, resolution, non-screenshot classification and favorite/edit/approval; low scores are withheld until approved unless disabled. Not blur/aesthetic scoring; manual says 1–5 while filter reference permits 1–7.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 320. Pages and Workers runtimes — 1/50

`deployment.cloudflare` · Domain: **deployment** · Core: **1** · Product-lineage groups: **1**

Cloudflare Pages and Workers run the shared engine with KV/D1 persistence; Workers deployment via GitHub Actions supports secret-typed variables.

- **Core (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 321. Cloudflare Pages hosting — 1/50

`deployment.cloudflare_pages` · Domain: **deployment** · Core: **1** · Product-lineage groups: **1**

Deploy through Git integration or Wrangler Pages; a free pages.dev hostname and custom domains are documented. This is a Pages Functions project, not a directly deployable Worker entry point.

- **Core (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 322. FreeBSD executable distribution — 1/50

`deployment.freebsd` · Domain: **deployment** · Core: **1** · Product-lineage groups: **1**

Documented FreeBSD application/CLI executables. This does not imply a native desktop GUI.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 323. Documented Kubernetes deployment manifests — 1/50

`deployment.kubernetes` · Domain: **deployment** · Core: **1** · Product-lineage groups: **1**

Project-provided/documented Kubernetes manifests or deployment instructions; operational scalability is not independently benchmarked.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 324. macOS source execution — 1/50

`deployment.macos_source` · Domain: **deployment** · Core: **1** · Product-lineage groups: **1**

Current guide says source installation is the only macOS option; discontinued Intel .app is not claimed as a current native binary distribution.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 325. Installable responsive PWA — 1/50

`deployment.pwa` · Domain: **deployment** · Core: **1** · Product-lineage groups: **1**

Browser app can be installed on phone/tablet/desktop home screen; this does not establish a native mobile background-backup service.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 326. Documented Unraid installation — 1/50

`deployment.unraid` · Domain: **deployment** · Core: **1** · Product-lineage groups: **1**

An explicit Unraid installation option and guide, not an inference from generic Docker support.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 327. Review AI-added groups — 1/50

`duplicates.ai_result_filter` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

An AI filter retains groups containing an AI-only accepted member along with its comparison context; it is not an AI-only rescan.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 328. Rule-driven duplicate resolution — 1/50

`duplicates.auto_resolution` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Rules combine pair searches, ordered comparisons and actions. Semi-automatic queues require approve/deny; fully automatic rules can delete and merge without per-pair approval.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 329. Noninteractive and immediate deletion — 1/50

`duplicates.automatic_deletion` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--delete --noprompt retains the first ordered member and removes others. --immediate deletes as matches arrive without collecting groups and implies no prompt.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 330. EXIF timestamp candidate matching — 1/50

`duplicates.capture_timestamp` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

A separate scan treats matching DateTimeOriginal tags as duplicate candidates; modified images retaining the timestamp can be false positives.

- **Core (1):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>)
- **Not established by this research:** 49/50.

### 331. Classic algorithm and threshold controls — 1/50

`duplicates.configurable_similarity` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Choose grayscale percentage-difference or pHash, or combine both so either match qualifies. Controls include hash-difference threshold, minimum similarity and required fraction of matching sampled pHash frames.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 332. Match only across independent trees — 1/50

`duplicates.cross_root_isolation` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--isolate counts matching content within one root as one replica, distinguishing cross-tree backups from repeated paths inside a tree; removal can retain/drop a root's matching files together.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 333. Compare against prior/missing files — 1/50

`duplicates.database_comparison` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Settings can scan against the entire database and include non-existing files; tombstone mode also enables missing-file comparison.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 334. Defer verification until deletion — 1/50

`duplicates.deferred_verification` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--deferconfirmation postpones byte-level equality checks in interactive mode until immediately before deletion.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 335. Delete redundant files — 1/50

`duplicates.delete_files` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

remove permanently removes selected redundant entries using the separately reviewed report and keeper policies.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 336. Remember deleted content — 1/50

`duplicates.deleted_content_memory` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Optional RememberDeletedContent retains fingerprints when the last copy is deleted, so re-downloaded content can be recognized; database cleanup becomes tombstone-aware. This is not a general reviewed-pair ignore list.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 337. Duration candidate constraints — 1/50

`duplicates.duration_tolerance` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Configure percentage duration tolerance with minimum/maximum seconds bounds; with percentage disabled, seconds-only tolerance is supported. Maximum sampled duration is also configurable.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 338. Ordered or reordered filename fields — 1/50

`duplicates.fielded_names` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Dash-separated fields are compared individually; an order-independent mode can match artist/title reversed between files, with each field used once.

- **Core (1):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>)
- **Not established by this research:** 49/50.

### 339. Single-filesystem matching — 1/50

`duplicates.filesystem_boundary` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--one-fs skips nested mount points and cross-filesystem symlinks and avoids matching across devices/filesystems.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 340. Dupes-only review mode — 1/50

`duplicates.flat_results` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Hide reference rows to sort all duplicate files independently by columns, combine with relative values, and mark batches such as extension or bitrate differences.

- **Core (1):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>)
- **Not established by this research:** 49/50.

### 341. Same/different-folder matching — 1/50

`duplicates.folder_relationship` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

FolderMatchMode permits unrestricted, same-folder-only or different-folder-only matching with configurable same-folder depth.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 342. Optional symlink traversal — 1/50

`duplicates.follow_symlinks` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--symlinks follows symlinked directories; manual warns that keeping a link while deleting its target can lose the usable file.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 343. Fuzzy/similar filename matching — 1/50

`duplicates.fuzzy_names` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Fuzzy/similar filename matching

- **Core (1):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>)
- **Not established by this research:** 49/50.

### 344. Rotated and mirrored duplicate matching — 1/50

`duplicates.geometric_invariance` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Optional comparison setting adds mirror/flip and 90-degree rotation variants; changed invariance/hash/filter parameters create distinct cached signatures.

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 345. Ordered action fallbacks — 1/50

`duplicates.link_fallback_chain` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Configure comma-separated handlers; smart link tries clone, reflink, hardlink then symlink. Default script handler is permanent remove, not trash.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 346. Collapse presumed duplicate timeline entries — 1/50

`duplicates.metadata_collapse` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

De-duplicate identical files setting collapses matching AUID entries and retains hidden copies for bulk actions. Missing AUID is derived from MD5(timestamp plus file size), not file bytes; this is presentation deduplication, not verified exact-content cleanup.

- **Core (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 49/50.

### 347. Metadata-aware automated comparisons — 1/50

`duplicates.metadata_preservation_checks` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Rule comparators can protect EXIF/XMP/IPTC/human-readable/software metadata and ICC presence; they check presence flags, not equality or richness of contents.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 348. Incremental mtime and tolerance filters — 1/50

`duplicates.modified_time_bounds` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Scan files newer than a timestamp or updated stamp file, retaining size siblings as comparison candidates. Separate mtime-window requires content-equal files to lie within a time window, which can transitively chain groups.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 349. Move redundant copies — 1/50

`duplicates.move_aside` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

move sends selected redundant files to a target directory instead of deleting or linking them; this is not described as an OS trash integration.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 350. Name and relative-path match constraints — 1/50

`duplicates.name_constraints` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Require same/different basename, extension, extensionless name, parent directory or relative path in addition to content matching; optional case-insensitivity is ASCII-only, not fuzzy-image/name matching.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 351. Deterministic output and keeper ordering — 1/50

`duplicates.order_policy` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Order by modification time (default), status-change time or filename, with reversal; changelog documents ctime tie-breaking for mtime.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 352. Explicit byte-range comparison — 1/50

`duplicates.partial_content` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Clamp start/end by byte offset, percentage or factor to compare part of each file, e.g. excluding a fixed header. Results are partial-content matches, not exact whole-file duplicates.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 353. Optional partial-hash-only matching — 1/50

`duplicates.partial_hash_only` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--skip-content-hash bypasses whole-file hashing, with explicit false-positive warnings and advice to enlarge prefix/suffix samples. This mode is not safe exact-content verification.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 354. Path and regex-based review selection — 1/50

`duplicates.path_selection` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Select/deselect by substring, prefix, suffix, exact path or PCRE2 expression; clear or invert selections within affected sets before tagging them.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 355. Require matching ownership and permissions — 1/50

`duplicates.permission_match` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--permissions prevents files with different owner, group or permission bits from being considered duplicates.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 356. Exact decoded-pixel matches — 1/50

`duplicates.pixel_identity` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Distinguishes same-resolution/pixel-content matches even when metadata or file encoding differs; pixel hashes can be regenerated independently.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 357. Independent queries for pair sides — 1/50

`duplicates.query_scoped_pairs` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Require one side, both sides or different searches per side, plus maximum Hamming distance and require/exclude pixel matches; mixed-pair or full-group review modes.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 358. Hide resolved groups safely — 1/50

`duplicates.remaining_copy_filter` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Can hide groups with at most one remaining existing member; files on disconnected drives still count as offline rather than deleted.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 359. Explicitly allow removal of every copy in a group — 1/50

`duplicates.remove_all` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Explicitly allow removal of every copy in a group

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Explicitly unsupported (3):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>), [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>), [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 46/50.

### 360. Merge and replay prior scans — 1/50

`duplicates.replay_reports` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Replay saved JSON to change ranking/filter/output or merge previous runs without rehashing. It does not discover new paths and ignores entries whose mtime changed; hashing/traversal options no longer apply.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 361. Unique and under/over-replicated files — 1/50

`duplicates.replication_counts` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Can report unique files or groups below/above a chosen replication factor, rather than only pairs of duplicates.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 362. Similarity and selected-group filters — 1/50

`duplicates.result_similarity_filter` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Result filters support minimum/maximum similarity and groups with checked items.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 363. Scoped and library-wide duplicate review — 1/50

`duplicates.review_cleanup` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Duplicate scans can target a collection or selection; library-wide cleanup reports reclaimable space and bulk removes chosen copies. Sources do not specify hash versus perceptual equality.

- **Core (1):** [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 49/50.

### 364. Persist pending/resolved review records — 1/50

`duplicates.review_status` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Filter pending/resolved/type, delete group records individually/in bulk or clear pending groups before detection. Looser reruns exclude photos already in visual groups, so groups must be cleared to reconsider them.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 365. Cross-resolution and rotated picture matches — 1/50

`duplicates.rotation_dimension_tolerance` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Preferences can permit differing dimensions and rotations in the same picture duplicate group and allow mixed file extensions.

- **Core (1):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>)
- **Not established by this research:** 49/50.

### 366. Control recursion per directory argument — 1/50

`duplicates.selective_recursion` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

--recurse traverses all supplied roots; --recurse: traverses only roots positioned after that option, permitting mixed shallow/deep scans.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 367. Stored original-content fingerprints — 1/50

`duplicates.stored_fingerprint` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Expose Photos' stored hash of original file for cross-library matching, distinct from the metadata-based duplicates property.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 368. Traversal boundaries and link handling — 1/50

`duplicates.traversal_controls` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Limit depth, mount crossing, hidden files and permission eligibility; follow symlinks, ignore them or compare their target strings. Loop detection is documented when following links.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 369. Unique-file inventory and complete hashes — 1/50

`duplicates.unique_inventory` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Unique-path formatter emits nonduplicate paths; --hash-unmatched completes hashes for same-size nonduplicates, while --hash-uniques hashes every traversed file, including unique sizes.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 370. Video audio-fingerprint matching — 1/50

`duplicates.video_audio_fingerprints` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Separate audio comparison mode uses similarity, shorter/longer duration ratio, minimum duration and maximum audio difference; Krokiet manual says this mode itself does not require ffmpeg, unlike visual hashing/thumbnails.

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 371. Flip/background matching controls — 1/50

`duplicates.visual_transform_controls` · Domain: **duplicates** · Core: **1** · Product-lineage groups: **1**

Core settings expose horizontal-flip comparison and ignoring black/white pixels, distinct from optional neural transformed-copy detection.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 372. Drawing and filters — 1/50

`editing.draw_filters` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

README explicitly includes drawing and image filters in the basic editor; no professional RAW processing is implied.

- **Core (1):** [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>)
- **Not established by this research:** 49/50.

### 373. Resolution/format export dialog — 1/50

`editing.export_renditions` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Admins/Users export originals, full-size previews, resized JPEGs or playable video renditions with per-download retry; Viewers/Guests/Visitors may download but not use Export.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 374. Composition photo filters — 1/50

`editing.filters` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Help describes choosing a filter in media options, labels it experimental and explicitly says filters are not federated.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 375. Background Insta360 dewarping — 1/50

`editing.fisheye_dewarp` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

INSV/INSP/fisheye DNG become equirectangular derivatives using known camera FOV or configured fallback; dual-lens video/proxy files stack and originals stay unchanged.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 376. HDR-to-SDR previews and playback — 1/50

`editing.hdr_tonemap` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

HDR phone video is tone-mapped during thumbnail/conversion paths; HDR badges and probe/rebuild job repair older previews.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 377. Layered photo compositing — 1/50

`editing.layers` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Up to sixteen JPEG/PNG image layers, locked base, reorder/duplicate/hide/lock, transforms, five blend modes, opacity, clipping and erase/paint masks; output flattens visible layers and missing source media can be relinked on recovery.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 378. Extract motion clips or selected frames — 1/50

`editing.motion_extract` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Save embedded motion as a separate video or use frame picker for stills without changing source. Editing its still creates a separate image copy.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 379. Three-level image-processing inheritance — 1/50

`editing.processing_scopes` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Named configuration overrides provider overrides global defaults, including explicit disabled switches. Effective settings show value sources and can revert to inherited values.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 380. RAW sensor development controls — 1/50

`editing.raw_development` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

White-balance presets/custom temp/tint; exposure/tone; sharpening; Linear/VNG/PPG/AHD/DCB demosaic; denoise and half resolution; sRGB/AdobeRGB/Wide/ProPhoto output; clip/blend/rebuild highlights. TIFF 8/16 export only holds development, not additional crop/markup/look edits.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 381. Per-clip video picture changes — 1/50

`editing.video_adjustments` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Transform/crop Fit/Fill/Crop, scale/rotation/position/horizontal flip/background plus per-clip light/color/curves and opacity.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 382. Voice-over and multitrack audio — 1/50

`editing.video_audio_mixing` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Import audio, record local voice-over or extract clip sound; mix gain/pan/fades/mute/solo/master limiter, channel routing/mono downmix, sidechain ducking and three-band EQ/high-pass.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 383. Video framing and orientation — 1/50

`editing.video_crop_rotate` · Domain: **editing** · Core: **1** · Product-lineage groups: **1**

Mobile crops freely or to 1:1, 9:16, 16:9, 3:4 or 4:3 and rotates in 90-degree steps, accounting for original orientation.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 384. AAE edit round-trip — 1/50

`formats.adjustment_sidecars` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Export AAE adjustment files and re-import with original/edited companions to preserve non-destructive edits when Photos naming conventions match; unmatched edits become separate assets.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 385. Configured non-image uploads — 1/50

`formats.arbitrary_uploads` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Add extensions such as MP4, PDF or MP3 and disable image-only mode to upload other types. This does not establish a video/audio playback library.

- **Core (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 386. Archive/eBook covers — 1/50

`formats.archive_ebook_previews` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

ZIP/RAR/7z/Tar variants show first archive image; EPUB shows cover and comic-book archives use cover/first page.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 387. Burst companion preservation — 1/50

`formats.burst_groups` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Default export includes burst photos unless skipped; macOS 11+ import groups burst members, unlike older versions. Missing iCloud bursts remain a documented limitation.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 388. Content-based filetype detection and override — 1/50

`formats.content_detection` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Detects type by inspecting content rather than trusting extension/MIME; users can force a type from context menu.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 389. Document content extraction — 1/50

`formats.document_text_extraction` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Readers handle UTF-8 text/Markdown, DOCX-style documents, PDF, Excel/CSV and PowerPoint text. Plain text is capped at 3,000 characters and PDF at its first three pages; legacy .doc/.ppt are routed through libraries primarily intended for modern formats, so successful legacy parsing is not guaranteed.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 390. Document/archive cataloguing — 1/50

`formats.documents_archives` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Can import PDF/Office/ebook/archive formats with differing previews; PDF thumbnails except encrypted PDFs and CBZ identification do not imply internal document reading.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 391. Font and plaintext previews — 1/50

`formats.font_text_previews` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Font formats show Aa/alphanumeric samples; plaintext previews render only first 256 bytes. Full text/syntax highlighting remain planned.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 392. GeoTIFF overlay — 1/50

`formats.geotiff` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Detects GeoTIFF and exposes Show as map overlay rather than merely treating georeferenced TIFF as an ordinary thumbnail.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 393. Ultra HDR thumbnail metadata — 1/50

`formats.hdr_thumbnails` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Desktop v1.7.30 preserves HDR gain maps in Ultra HDR JPEG thumbnails generated on Linux/Windows; this is narrower than a universal HDR rendering guarantee.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 394. Manage HEIC+JPEG companions — 1/50

`formats.heic_jpeg_pairs` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Offers separate, keep-HEIC, keep-JPEG and either-cover stacking modes based on matching basenames; this is not by itself proof of Live Photo video pairing.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 395. Raster image analysis — 1/50

`formats.image_content_analysis` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

README lists PNG/JPEG/GIF/BMP; source additionally classifies TIFF as an image. This is analysis eligibility, not documented animated playback or RAW decoding.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 396. Broad image/video original backup — 1/50

`formats.media_backup` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Accepts image/* and video/* originals up to 10 GB, without upload compression; backup eligibility does not guarantee every client can thumbnail/play the format.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 397. Multipage TIFF — 1/50

`formats.multipage_tiff` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

README specifically identifies multipage TIFF as supported media.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 398. TIFF original and previews — 1/50

`formats.tiff` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

Uploads original TIFF and creates mandatory JPEG thumbnails plus optional optimized PNG; layered TIFF handling picks the extracted first image/layer for the preview rather than providing a complete multipage viewer.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 399. WebP and icon image hosting — 1/50

`formats.webp_ico` · Domain: **formats** · Core: **1** · Product-lineage groups: **1**

README explicitly names WebP and ICO in addition to common image formats.

- **Core (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 49/50.

### 400. Open media location on a map — 1/50

`geo.external_map` · Domain: **geo** · Core: **1** · Product-lineage groups: **1**

UI exposes Show on map and an unknown-location state. An integrated offline basemap or geocoder is not established.

- **Core (1):** [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>)
- **Not established by this research:** 49/50.

### 401. Interactive 3D Earth view — 1/50

`geo.globe_view` · Domain: **geo** · Core: **1** · Product-lineage groups: **1**

Places can switch to a globe that rotates, zooms and tilts; the guide says it works with all map styles and can combine with terrain mode. Paid satellite/terrain map services remain a separate capability.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 402. Reuse previously resolved places — 1/50

`geo.location_cache` · Domain: **geo** · Core: **1** · Product-lineage groups: **1**

Location lookup caches results in JSON and reuses a nearby cached location within a requested 3 km radius, reducing repeated lookups but potentially coarsening naming.

- **Core (1):** [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 49/50.

### 403. Private named circular places — 1/50

`geo.private_places` · Domain: **geo** · Core: **1** · Product-lineage groups: **1**

Define up to 100 places of 25 m–2 km radius with live photo counts; smaller overlapping circle wins. Names dynamically group photos/search and can title events, but never leave owner via sharing/write-back.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 404. Custom radius-defined places — 1/50

`geo.radius_location_tags` · Domain: **geo** · Core: **1** · Product-lineage groups: **1**

Create labels such as Home/Office by choosing a center and radius; the app groups matching photos locally, with encrypted location labels.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 405. Lossy GPX compression — 1/50

`geo.track_simplification` · Domain: **geo** · Core: **1** · Product-lineage groups: **1**

On-demand/scheduled compression removes too-close or near-collinear points using distance, temporal spacing and deviation thresholds.

- **Core (1):** [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 49/50.

### 406. Album launcher shortcuts — 1/50

`integration.album_shortcuts` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Selected album paths can be sent to a shortcut-creation helper from the album menu.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 407. Widgets, picker and screensaver — 1/50

`integration.android_components` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Provides widgets, launcher shortcuts, screensaver and global search handling, and can act as media viewer/picker for other Android apps.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 408. Accept external Android edit requests — 1/50

`integration.android_editor` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Current editor accepts JPEG/PNG/video edit intents and returns the saved copy to caller while also retaining it in ReFra output folders.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 409. Share, open, edit and use-as handoffs — 1/50

`integration.android_intents` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Android choosers receive file URIs with read permission for sharing, external editing/viewing and attach/use-as actions.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 410. Share selected media to apps — 1/50

`integration.android_share` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Single and multiple selections route through Android media-sharing helpers; not a hosted public-link service.

- **Core (1):** [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>)
- **Not established by this research:** 49/50.

### 411. Atom syndication — 1/50

`integration.atom_feeds` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Federation configuration independently enables Atom feeds by default.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 412. Share, print and external apps — 1/50

`integration.external_actions` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

UI actions include share, print, copy to clipboard, open-with, set-as and opening coordinates in a map app.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 413. Multiple external applications — 1/50

`integration.external_editor` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Configure multiple external apps and a default; opening more than 100 files requires confirmation.

- **Core (1):** [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 49/50.

### 414. Scriptable file/tree equality check — 1/50

`integration.file_equality` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

--equal returns status indicating whether multiple files or directory contents match and accepts paranoid mode; directory layout is not automatically part of equality.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 415. Standalone parallel hash utility — 1/50

`integration.hash_utility` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

--hash operates like a multithreaded checksum tool over paths or stdin using supported hash algorithms.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 416. Prompted or scripted operation — 1/50

`integration.interactive_cli` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Interactive mode prompts for folders/date division/album strategy; explicit input/output/album switches support headless NAS use and automation, with --help argument documentation.

- **Core (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 417. Local filesystem upload destination — 1/50

`integration.local_storage` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Built-in local destination supports upload, destination-file deletion and file management. Core release notes describe writing to a temporary file before replacing the local destination to reduce incomplete output after interruption.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 418. Permission-aware MCP library tools — 1/50

`integration.mcp` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

October release adds search/browse and metadata/format/command lookups, enabled for eligible roles with per-account/global disable options; external assistants can access authorized library information.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 419. OAuth app authorization — 1/50

`integration.oauth_apps` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Release adds authorization-code app/remote-MCP connections; PHOTOPRISM_OAUTH_APPS=none can block external app authorization.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 420. Named expiring API keys — 1/50

`integration.personal_api_keys` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Keys have optional expiry, are displayed once and can be revoked; docs warn they permit uploads on the user's behalf.

- **Core (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 421. Ranked redispatch and root fallback — 1/50

`integration.provider_failover` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Dispatch checks target availability and attempts another ranked host, falling back to root when destinations are exhausted. Source contains TODO failure handling, so this is designed behavior rather than proven reliable failover.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 422. Enable, reorder and weight providers — 1/50

`integration.provider_management` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Admin menu drag-order controls enabled providers; provider records separately hold homepage rank and dispatch weight plus configuration updates.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 423. QR actions inside photos — 1/50

`integration.qr_detection` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Mobile detects multiple QR codes on-device and offers open/copy/share plus supported UPI payment actions; scanning alone does not upload QR contents.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 424. Random image endpoint links — 1/50

`integration.random_photo_url` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Creates a URL serving a random photo, useful for external wallpaper/photo-frame applications and subject to user rights.

- **Core (1):** [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 49/50.

### 425. Embeddable scanning core — 1/50

`integration.rust_library` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

UI-independent czkawka_core exposes scan configuration, typed results and shared functionality for other applications.

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 426. Persist scan configurations — 1/50

`integration.scan_presets` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Ten user presets save roots, filters and tool parameters, plus a reserved command-line-path slot; custom selection rules are separately persisted.

- **Core (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 427. Android screensaver integration — 1/50

`integration.screensaver` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

README lists a screen saver among the application's Android integrations, alongside Android TV support. This establishes a screensaver function, not desktop wallpaper scheduling or a separate casting protocol.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 428. Browser-first setup and settings — 1/50

`integration.setup_wizard` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

Wizard creates an administrator and chooses site/storage; everyday settings persist in database and can be changed without rebuilding containers or editing .env.

- **Core (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 429. Shell completion generation — 1/50

`integration.shell_completion` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

complete prints setup scripts for Bash, Zsh, Fish, Elvish and PowerShell; installation into the shell is manual.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 430. Provider image URL parameters — 1/50

`integration.storage_url_parameters` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

2.1 adds per-strategy image URL parameters; docs recommend provider-side transformation rules for third-party storage to avoid heavy PHP processing.

- **Core (1):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>)
- **Not established by this research:** 49/50.

### 431. Telegram channel storage — 1/50

`integration.telegram_storage` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

A bot token and channel/chat ID route uploads into a channel where the bot is an administrator; source files reside on Telegram.

- **Core (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 432. Adapt to Immich V2/V3 APIs — 1/50

`integration.version_adaptive_api` · Domain: **integration** · Core: **1** · Product-lineage groups: **1**

v0.32.0 detects server version and adapts errors/API behavior; album assets are retrieved through paginated metadata search for large collections.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 433. AI-generated category directories — 1/50

`library.ai_category_folders` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Content analysis produces foldername and filename values used to construct the proposed output hierarchy.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 434. Descriptive output filenames — 1/50

`library.ai_filename_generation` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Generates descriptive names while preserving extensions; sanitizer removes unsuitable words/punctuation, lowercases, separates words with underscores and limits length to 50 characters/five words.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 435. Preserve folder/album hierarchy on export — 1/50

`library.album_export_layout` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

folder_album templates reproduce Photos nested albums; multi-album/multi-keyword templates can export multiple copies and filters can restrict chosen hierarchy branches.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 436. ZIP a folder — 1/50

`library.archive_export` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Gallery exposes folder ZIP creation with progress, cancellation and saved-location feedback.

- **Core (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 49/50.

### 437. Archive outside ordinary timeline — 1/50

`library.archive_folder` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Archive moves photos to .archive at timeline/storage root, which may be mounted to cold storage; this is a filesystem move, not just hiding.

- **Core (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 49/50.

### 438. Previewed bulk record URL replacement — 1/50

`library.batch_url_edit` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Select/filter records, inspect pattern-based before/after matches and final plan before applying. This edits history only, not remote filenames or published Markdown documents.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 439. Delete image and local-backup records — 1/50

`library.bulk_delete` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Admin accepts ID lists; model deletes associated local paths and database rows. Inspected delete path does not establish revocation of every third-party hosted copy.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 440. Automatic clipboard image uploads — 1/50

`library.clipboard_monitor` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Optional monitoring uploads newly copied images automatically, including temporary screenshots; docs warn about online destination exposure.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 441. Clipboard image upload — 1/50

`library.clipboard_upload` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Ctrl+V workflow sends base64 image content; parse endpoint validates MIME before storing it.

- **Core (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 442. Compare two Photos libraries — 1/50

`library.compare_catalogues` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Compare identifies assets unique to each catalogue and same/different pairs, accepts custom signature functions/templates, outputs CSV/TSV/JSON and offers nonzero-difference exit status.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 443. Continuous one-way local backup — 1/50

`library.continuous_export` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Desktop continuous export downloads new items while running; CLI repeated/scheduled exports incrementally update a disk or mounted NAS. Local edits do not upload back.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 444. Delete a photo from results — 1/50

`library.delete_asset` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Viewer delegates deletion to the photo asset and removes its search embedding. The inspected viewer does not establish a separate application trash or operation journal.

- **Core (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 49/50.

### 445. Derivative provenance ingestion — 1/50

`library.derivative_ingestion` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Loader exposes enqueueDerivativeImage with derivativeOfMediaIds, preserving an explicit relationship to source assets.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 446. Synchronize server directory trees — 1/50

`library.directory_sync` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Free comparison lists directory-tree import and optional removal of catalogue photos/albums no longer present in source directories; these are potentially destructive sync choices, not a read-only guarantee.

- **Core (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 447. Media download variants — 1/50

`library.download_variants` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Media exposes a list of downloadable file versions with role/title, URL, dimensions and file size; exact variants depend on processing.

- **Core (1):** [photoview/photoview](<profiles/R11-photoview-photoview.md>)
- **Not established by this research:** 49/50.

### 448. Reuse existing duplicate in target albums — 1/50

`library.duplicate_album_reuse` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

--dup-albums adds an existing matched asset to the albums skipped import would have created, preserving folder-to-album organization without extra copies.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 449. Export edited versions separately — 1/50

`library.export_edited` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Defaults to original and edited versions with a configurable edited suffix; can skip edits or export only edited when one exists.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 450. Metadata-driven exported names — 1/50

`library.export_filename_templates` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Directory/filename templates support defaults, nested conditionals, multi-valued fields and filters; use title, date, place, album, keyword or original name without renaming Photos originals.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 451. Export derivative previews — 1/50

`library.export_previews` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

API exposes ordered preview paths and optional preview export/suffix, including derivative stills/video previews when available.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 452. Optional hardlink export — 1/50

`library.hardlink_export` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Exporter supports creating hardlinks instead of copies. These share the underlying file and are not an independent backup.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 453. Hard-linked output views — 1/50

`library.hardlink_organization` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

All three planning modes currently assign hardlink, and execution calls os.link. Original filenames remain; output is not an independent backup and cross-filesystem creation can fail.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 454. Import iCloud exports — 1/50

`library.icloud_export_import` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Reads iCloud export CSV metadata for dates and organization; optional --memories turns memories into albums. This is export ingestion, not documented live iCloud synchronization.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 455. Size, dimensions and deleted-file import policies — 1/50

`library.import_filters` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Import options include min/max size, resolution and whether to reimport previously deleted files; optional pre-import tagging parses filenames/folders.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 456. Inbox-to-archive curation — 1/50

`library.inbox_archive` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

New imports enter inbox; archive marks keepers without moving folders. Fast archive/delete filter supports skip/back and commits decisions at completion.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 457. Update an existing export — 1/50

`library.incremental_export` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

SQLite export state enables --update to export only new/changed files. --only-new ignores removed prior exports; --ignore-signature avoids replacing externally edited output merely because file size/mtime differs.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 458. Legacy iPhoto library access — 1/50

`library.legacy_iphoto` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Limited iPhoto 9.6.1 support includes export/query metadata; v0.78.1 adds iPhoto support to sync --export.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 459. Overlapping local file subsets — 1/50

`library.local_file_domains` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Create separate searchable file-domain lists, add/move membership and intersect with tag domains without duplicating payloads. These are not independent databases or user accounts.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 460. Set or merge metadata across libraries — 1/50

`library.metadata_sync` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Sync matched assets using original filename/fingerprint from another library/database or exported SQLite metadata. Set overwrites chosen fields; merge preserves/combines them, and album sync only adds memberships.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 461. One-way device album synchronization — 1/50

`library.mobile_album_sync` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Creates/merges same-named server albums and backfills existing uploads. Later local deletes/reordering do not propagate; matching already-shared server albums share the newly added media.

- **Core (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 462. Multiple named provider configurations — 1/50

`library.named_upload_profiles` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Maintain multiple accounts/configurations per provider; setting default is separate from saving, and up to six favorites enable quick switching.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 463. Only-new-photo cutoff — 1/50

`library.new_only_backup` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Onboarding new-only mode starts at seven days ago; enabling later uses the current moment. Already queued uploads are not cancelled and manual older uploads still work.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 464. Browse catalogue/thumbnails while source storage is disconnected — 1/50

`library.offline_volumes` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Browse catalogue/thumbnails while source storage is disconnected

- **Core (1):** [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Explicitly unsupported (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 48/50.

### 465. Reconstruct Picasa albums — 1/50

`library.picasa_import` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

from-picasa automatically reads .picasa.ini, and folder ingestion can enable the same album-name processing.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 466. Hide posts in archive — 1/50

`library.post_archive` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Archived posts become unavailable for viewing/interactions and can be unarchived via profile Archives; help warns remote interactions may not be received while archived.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 467. Organize camera RAW, video and audio files — 1/50

`library.raw_audio_video_organization` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

README explicitly includes DNG/NEF and common video/audio alongside JPEG, with media-specific metadata precedence; no built-in playback is implied.

- **Core (1):** [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 49/50.

### 468. Recursive file discovery — 1/50

`library.recursive_file_discovery` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Accepts a directory or single file, recursively collects paths and excludes dot-prefixed filenames; hidden directory traversal is not explicitly excluded by os.walk.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 469. Duplicate-upload acceptance control — 1/50

`library.reject_duplicate_uploads` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Enable or disable accepting duplicate uploads; inspected settings alone do not establish perceptual matching or a general duplicate-review interface.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 470. Configurable related-image grouping — 1/50

`library.related_file_stacks` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Optional sequential-name, same-second/position and Unique Image/XMP Instance ID grouping; choose primary preview or unstack nonprimary image. Changing rules does not auto-unstack old groups.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 471. Portable library root — 1/50

`library.relative_path_portability` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Relative entry paths allow moving the whole content/data folder together, including external drives or differently mounted NAS paths.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 472. Repair moved/unlinked entries — 1/50

`library.relink_entries` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Tool finds missing entries, searches/relinks or removes only catalogue records after confirmation. README says matching uses filenames, ignores ambiguous matches and cannot relink renamed files.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 473. Download hosted images into local backups — 1/50

`library.remote_backup` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Admin-selected remote URLs are concurrently downloaded to server files and linked backup records; source uses a task lock and reports progress/completion or a 60-second inactivity timeout.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 474. Organize existing server assets — 1/50

`library.retroactive_stacking` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

stack operates on existing Immich assets without uploading media, using the same burst/pair/scanner rules and an optional timezone override.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 475. Epson FastFoto front/back grouping — 1/50

`library.scanner_stacking` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Groups original, _a corrected and _b reverse-side scans with corrected image as stack cover.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 476. Automated import/export folders — 1/50

`library.scheduled_import_export` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Configured folders run on schedules, importing tags/URLs/notes via sidecars and exporting selected files with naming patterns/metadata.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 477. Second upload destination — 1/50

`library.secondary_upload` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Can reuse primary processed bytes or independently process original input using secondary settings. Errors are separate and identical configuration can be skipped; not a backfill of earlier uploads.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 478. Recursive server-directory import — 1/50

`library.server_import` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Import accepts a chosen server directory, recurses into subdirectories and creates albums named from folders with an Import prefix; reserved Lychee derivative directories are excluded.

- **Core (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 479. Immich-to-Immich transfer — 1/50

`library.server_migration` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Source and destination have separate server/API credentials and timeout/TLS settings; filters include dates, archived/trash state, favorites and minimum rating.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 480. Sidecar-sensitive RAW previews — 1/50

`library.sidecar_change_detection` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

For non-web-compatible photos, discovers filename.ext.xmp, stores its hash and regenerates JPEG preview/thumbnail when sidecar changes or disappears. This establishes sidecar change detection, not a general XMP field reader/writer or searchable sidecar metadata.

- **Core (1):** [photoview/photoview](<profiles/R11-photoview-photoview.md>)
- **Not established by this research:** 49/50.

### 481. Filter Google-generated extra images — 1/50

`library.skip_edited_extras` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

--skip-extras removes recognized edited/effects/smile/mix suffix variants in several languages, with Unicode normalization for macOS names.

- **Core (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 482. Manage multiple storage schemes — 1/50

`library.storage_schemes` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Dashboard adds/edits/selects local, S3 and OpenList schemes. Changing active scheme affects new uploads only; this is not multiple independent user-selectable catalogues.

- **Core (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 483. Search existing Apple Photos library — 1/50

`library.system_photo_library` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Search controller opens the system user-library smart album and references PHAsset identifiers without importing originals into a second managed store.

- **Core (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 49/50.

### 484. Selective Takeout import — 1/50

`library.takeout_selection` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Archived and partner photos default to included; trashed, unmatched and untitled-album inclusion are separate switches. Can select an album and group partner photos into a named album.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 485. Scan named files or subtrees — 1/50

`library.targeted_scan` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

API accepts up to 1000 changed paths and separately 1000 removed paths; validates library scope and detects move-out/move-in without losing personal edits.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 486. Extension-based organization — 1/50

`library.type_folders` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Type mode separates image_files, text_files with plain-text/document/PDF/spreadsheet/ebook subcategories, and others; this does not imply semantic ebook understanding.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 487. Date-partitioned local storage — 1/50

`library.upload_date_storage` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Local adapter uses current upload year/month/day directories and a random 16-character basename with retained extension; not EXIF capture-date organization.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 488. Upload filename policies — 1/50

`library.upload_naming` · Domain: **library** · Core: **1** · Product-lineage groups: **1**

Choose original name, randomized name, original-plus-random or encoded ID naming; original-name collisions are randomized.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 489. Startup database migrations — 1/50

`maintenance.automatic_migrations` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Migrations run automatically; current runtime image has no shell/package manager, and older manual in-container migration instructions no longer apply.

- **Core (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 490. Deployment self-check — 1/50

`maintenance.configuration_diagnostics` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Homepage identifies missing environment variables or bindings and tells operators where to configure them before the first upload.

- **Core (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 491. Incremental local index compaction — 1/50

`maintenance.index_compaction` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Appends new embeddings and records deleted IDs, migrates the older archive format and compacts after a journal exceeds five million bytes or tombstones exist.

- **Core (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 49/50.

### 492. Selected-photo and template inspection — 1/50

`maintenance.interactive_inspection` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

CLI provides inspect, UUID, show, REPL and interactive template commands for exploring selected Photos items and developing repeatable workflows.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 493. Delete associated pin media — 1/50

`maintenance.media_cleanup` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Deleting a pin triggers deletion of its image record; example settings enable image-file auto-deletion. This is cleanup, not recoverable trash.

- **Core (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Not established by this research:** 49/50.

### 494. Reconcile missing and orphaned files — 1/50

`maintenance.media_recovery` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Queue missing-file checks/redownload from known URLs, export hashes/tags/URLs for recovery, and move orphaned payloads to a review location for deletion/reimport.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 495. Online incremental and cross-version updates — 1/50

`maintenance.online_upgrade` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

README lists both upgrade modes as implemented; this is historical functionality and does not imply continued upstream updates.

- **Core (1):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>)
- **Not established by this research:** 49/50.

### 496. Silent text logging — 1/50

`maintenance.operation_log` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Silent mode appends messages and operation successes/failures to operation_log.txt; it is not a transactional journal or undo mechanism.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 497. Structured action reports — 1/50

`maintenance.operation_reports` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Export/import/sync/push-exif reports support CSV/JSON/SQLite outcomes including new/updated/skipped/missing/errors; import/sync can append reports. These logs are not crash-recovery journals.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 498. Conservative app-data health cleanup — 1/50

`maintenance.orphan_data_cleanup` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

Daily/on-library-change or manual cleanup removes orphaned extracted data/memberships/edit backups, preserving cloud cache rows and user definitions such as people/collections/vaults.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 499. Inspect physical sharing — 1/50

`maintenance.reflink_diagnostics` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

--is-reflink distinguishes reflinks, hardlinks, identical paths, different devices, symlinks, unavailable extent information and inline extents through exit statuses.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 500. Automatic settings export — 1/50

`maintenance.settings_export` · Domain: **maintenance** · Core: **1** · Product-lineage groups: **1**

v1.14.6 introduces automatic settings export; subsequent releases improve export failure feedback and storage-access handling.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 501. Per-media alternative descriptions — 1/50

`metadata.accessibility_descriptions` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Help documents media descriptions for visually impaired users, federated where supported. Help labels the composing UI experimental; current config sets an alt-text length limit of 1,000.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 502. Bookmark public images — 1/50

`metadata.bookmarks` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Users save public images for later access; distinguished from changing ownership or copying originals.

- **Core (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 503. Site image categories — 1/50

`metadata.categories` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Categories classify images and create category listings with name, URL key and description.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 504. C2PA content credentials — 1/50

`metadata.content_credentials` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

v1.15.9 displays credentials, overlays validity icons and filters unknown/invalid/valid/trusted states; removal of JPEG JUMBF credential metadata is supported.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 505. Crop requester and timestamp — 1/50

`metadata.crop_provenance` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Each generated crop records authenticated identity, request time and specification. This is derivative provenance, not a durable crash-recovery file-action journal.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 506. Picks and rejects — 1/50

`metadata.culling_flags` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Local catalogue preserves culling states including Picks and Rejects, separate from file-embedded metadata.

- **Core (1):** [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 49/50.

### 507. Configurable metadata/date precedence — 1/50

`metadata.date_rules` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Ordered rules choose XMP/EXIF/video/GPS/Takeout/name times, use recorded or GPS/default timezone and can be reapplied without rewriting originals or overriding manually set dates.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 508. Configurable EXIF handling — 1/50

`metadata.exif_handling` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Site controls image EXIF handling and whether users can choose their own handling setting; no broad EXIF-write editor is inferred.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 509. Export metadata — 1/50

`metadata.export` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Info exposes an Export metadata action; the exact serialization and sidecar interoperability are not established here.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 510. Selective metadata export — 1/50

`metadata.export_privacy_selection` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Exporter options control inclusion of location/persons, replacement/merging of keywords and generated metadata; this does not automatically remove every pre-existing embedded field.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 511. Portable named MWG face regions — 1/50

`metadata.face_regions` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Imports XMP RegionInfo faces/names and merges overlapping detections; optional face-write switch plus metadata-write mode exports normalized regions/names with rotation handling.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 512. Export/import favorites — 1/50

`metadata.favorite_paths_transfer` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Settings expose favorite path import/export; export selects a .txt destination and confirms overwriting an existing file. This is not a full database/photo backup.

- **Core (1):** [FossifyOrg/Gallery](<profiles/R22-fossifyorg-gallery.md>)
- **Not established by this research:** 49/50.

### 513. Infer missing dates from filenames — 1/50

`metadata.filename_date_fallback` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

If EXIF timestamp is unavailable, the model tries fuzzy date parsing of the filename and assigns UTC; this is inference, not a confirmed capture time.

- **Core (1):** [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 49/50.

### 514. Finder tags/comments and Spotlight attributes — 1/50

`metadata.finder_attributes` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Write keywords to Finder tags and template-driven author/comment/copyright/description/headline attributes without altering image bytes.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 515. Folder-derived tags — 1/50

`metadata.folder_tags` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Auto-generates tags from directory structure; Eagle integration can also map folders to tags.

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 516. Convert folder hierarchy to tag inheritance — 1/50

`metadata.folders_to_tags` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Macro previews a hierarchy for confirmation, creates a tag per folder, applies to entries and assigns parent-folder tags as parents; v9.6.4 fixes this workflow.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 517. Fujifilm film recipes — 1/50

`metadata.fujifilm_recipes` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Displays extracted Fujifilm film-simulation settings.

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 518. Geotag from GPX/tracks — 1/50

`metadata.gpx_sync` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Geotag from GPX/tracks

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 519. Hosting metadata display and editing — 1/50

`metadata.hosting_fields` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Shows upload time, size and source IP; supports editing display filename/type and renaming File ID. These are hosting fields, not EXIF/IPTC editing.

- **Core (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 520. Infer import dates from names/directories — 1/50

`metadata.import_date_parsing` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Parse strptime-like filename or folder patterns and supply timezone overrides; missing components fall back to Photos' date behavior. Direct named-timezone writes carry an undocumented-database risk.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 521. Adjust Photos added/imported date — 1/50

`metadata.import_timestamp_edit` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Set date-added independently or copy capture date to added date, useful for removing old scans from Recents without changing their capture timestamp.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 522. Built-in broader label categories — 1/50

`metadata.label_categories` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Generated labels belong to searchable broader groups such as vehicle; category grouping is not user-editable hierarchy.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 523. Time-nearest photo GPS propagation — 1/50

`metadata.nearest_photo_geotag` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Find the nearest geotagged photo within a configurable ±time window (default one hour) and copy its location; assumes correct capture times and offers dry run.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 524. Read Photos person/face records — 1/50

`metadata.people_read` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Expose names, face/person objects and region metadata from Apple's catalogue. This is not an independent face-recognition engine.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 525. Batch metadata refresh — 1/50

`metadata.refresh` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Refresh file info rereads selected files together; unchanged cloud-only OneDrive/macOS dataless entries are detected without forcing downloads.

- **Core (1):** [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 49/50.

### 526. Named XMP region overlay — 1/50

`metadata.region_overlay` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Region boxes/labels can appear over placeholders and remain aligned while zooming; affected photos switch to a DOM viewer. This consumes existing regions, not automatic face detection.

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 527. Creator, copyright and licence metadata — 1/50

`metadata.rights` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Reads/displays creator/copyright and fixed Creative Commons/all-rights/public-domain licence choices, with supported write-back. Licence-bearing public photos expose relevant rights regardless of other detail switches.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 528. Retain source and known URLs — 1/50

`metadata.source_urls` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Known URLs stay attached to content hashes, support downloader skip/refetch decisions and can be exported or used for recovery.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 529. Aliases and contextual names — 1/50

`metadata.tag_aliases_disambiguation` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Aliases/shorthand are searchable; marked parent tags add their name or shorthand in display parentheses to distinguish same-named tags without changing base identity.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 530. Export hash-to-tag archives — 1/50

`metadata.tag_archive` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Tag migration can export a Hydrus Tag Archive of queried hash-to-tag mappings independently of media bytes.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 531. Tag-driven inspector categories — 1/50

`metadata.tag_categories` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Category tags group inheriting tags in inspector, including multiple categories. Per-tag exclusions control category display; v9.6.4 release confirms the feature.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 532. Custom tag palettes — 1/50

`metadata.tag_colors` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Built-in and user-defined namespaced palettes set primary/secondary text/border colors on tags; not an independently established media color-label rating system.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 533. Handle Takeout sidecar naming anomalies — 1/50

`metadata.takeout_json_matching` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Matches photoTakenTime JSON through direct names, Google truncation, moved bracket suffixes, known edited suffixes and extension removal; last-resort aggressive suffix/digit removal is explicitly described as potentially dangerous in the pipeline.

- **Core (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 534. Technical image detail display — 1/50

`metadata.technical_details` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Image page lists dimensions, MIME, extension, upload time, file size and view count; EXIF capture metadata editing is not established.

- **Core (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 535. Image tone analysis — 1/50

`metadata.tone_analysis` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Pipeline computes tone information and stores it in manifest records; this is not documented object tagging or semantic search.

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 536. Editorial licensing and restrictions — 1/50

`metadata.usage_rights` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Displays/edits usage categories, agency suppliers, publications/creators and required restriction text; unknown rights are explicit and some categories force restrictions.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 537. Video technical metadata — 1/50

`metadata.video_read` · Domain: **metadata** · Core: **1** · Product-lineage groups: **1**

Displays dimensions, duration, codec, frame rate, bitrate, color profile and audio information.

- **Core (1):** [photoview/photoview](<profiles/R11-photoview-photoview.md>)
- **Not established by this research:** 49/50.

### 538. Administrative image moderation — 1/50

`moderation.admin_visibility` · Domain: **moderation** · Core: **1** · Product-lineage groups: **1**

Administrators manage image content/visibility, users, storage and settings; stored settings override corresponding environment variables.

- **Core (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 539. Scheduled and throttled AI work — 1/50

`performance.ai_schedule` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Set a processing time window and CPU throttling to limit intensive face/object jobs on shared NAS hardware.

- **Core (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 540. Context-aware download throttling — 1/50

`performance.bandwidth_limits` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Global, domain/subdomain and downloader/subscription/watcher contexts all must permit each request; review usage and customize limits, with conservative defaults.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 541. Cached filesystem statistics — 1/50

`performance.cached_file_counts` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

2.8.7 caches/iterates square file counts, general file counting and version checks to avoid recursive full-directory scans on every request; not a measured benchmark.

- **Core (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 542. Storage balancing and upload failover — 1/50

`performance.channel_failover` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Manage multiple channel configurations, configure load balancing and automatically retry through another available channel after upload failure.

- **Core (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 543. Bound still-image conversion time — 1/50

`performance.conversion_timeout` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Still/document/RAW conversion defaults to ten-minute timeout; -1 disables it. Video uses a separate timeout disabled by default.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 544. Periodic scan database saves — 1/50

`performance.database_checkpoints` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Automatic checkpoint interval defaults to five minutes; zero disables interval saves but retains phase-boundary saves. This is not a file-operation undo journal.

- **Core (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 545. Defer high-resolution loading — 1/50

`performance.deferred_fullsize` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Viewer can delay full-size image loading until zoom, and automatic media refresh can be disabled for large libraries according to its setting help.

- **Core (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 49/50.

### 546. Rotational-disk extent ordering — 1/50

`performance.disk_seek_optimization` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Optional FIEMAP reads physical file extents to optimize disk access; disabled automatically where unavailable.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 547. Trade precomputed storage for on-demand CPU — 1/50

`performance.dynamic_previews` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Independent static/dynamic size limits and Dynamic Previews reduce disk use at cost of latency/CPU; smaller/lower-quality analysis thumbnails can impair recognition.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 548. Optional gallery auto-refresh — 1/50

`performance.gallery_polling` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

AutoUpdate polls for new photos/videos at configurable interval, default 60 seconds when enabled; not a filesystem event watcher.

- **Core (1):** [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 49/50.

### 549. GPU-accelerated embedding search — 1/50

`performance.gpu_similarity` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Metal/MPSGraph multiplies normalized Float16 embeddings using persistent buffers and a cached graph; the controller provides CPU cosine-similarity fallback when GPU search is unavailable.

- **Core (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 49/50.

### 550. Bound hashing/comparison memory — 1/50

`performance.hash_memory_limit` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

--limit-mem caps memory for hashing/paranoid comparison, not total process RSS; path/index and other overhead remain.

- **Core (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 551. Prefetch adjacent viewing assets — 1/50

`performance.image_prefetch` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Changelog documents preloading large photos then preferring medium images for prefetch, plus album caching and saved scroll positions.

- **Core (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 552. Linux-specific I/O optimization — 1/50

`performance.linux_io_optimization` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Orders accesses by physical placement and uses page-cache drop-behind on Linux; documentation says these optimizations are unavailable on other platforms.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 553. Speed versus validity/quality controls — 1/50

`performance.loading_policy` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Settings expose file-loading priority choices including speed, compromise and avoiding invalid files, plus high-quality deep-zoom rendering.

- **Core (1):** [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>)
- **Not established by this research:** 49/50.

### 554. Compressed paths for large trees — 1/50

`performance.low_memory_paths` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

README attributes low memory use on millions of paths to prefix-compressed representations; this is a project claim, not a measured result here.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 555. Concurrent thumbnail generation — 1/50

`performance.parallel_thumbnails` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Thumbnail workers default to CPU count minus one with configurable concurrency cap; this is derivative processing, not a claim of parallel scanning or perceptual matching.

- **Core (1):** [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 49/50.

### 556. Pause server processing during import — 1/50

`performance.pause_server_jobs` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

--pause-immich-jobs defaults true to reduce thumbnail/other server workload during a bulk upload, requiring appropriate server permissions.

- **Core (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 49/50.

### 557. Continue past failed photos — 1/50

`performance.per_item_failure_isolation` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Per-photo errors mark an item failed and continue, while fatal errors terminate nonzero; logs/TUI report counts.

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 558. Cache dispatch targets — 1/50

`performance.redirect_cache` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Dispatch stores URL targets with a 3600 cache duration and redirects directly on cache hits; release notes identify Redis cache fixes.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 559. Retain tool results during navigation — 1/50

`performance.retained_page_state` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

1.2.3 scans uninstall/startup/privacy pages on first opening and preserves results, scroll position and category choices on page switches.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 560. Retry unreliable exports — 1/50

`performance.retry` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

--retry sets export retry attempts for failures such as intermittent NAS connections.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 561. Off-thread tiled decoding — 1/50

`performance.tiled_rendering` · Domain: **performance** · Core: **1** · Product-lineage groups: **1**

Large photos decode in a worker and stream tiles to the GPU instead of decoding entirely on the main UI thread.

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 562. Hotlink and file-access controls — 1/50

`privacy.access_rules` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Allowed source domains, file/IP allow/block lists and whitelist-only access can restrict public delivery; CDN caches may delay enforcement.

- **Core (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 563. Locked app-private vaults — 1/50

`privacy.app_private_vault` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Vaults support pattern/PIN/password and biometric unlock, with optional lock when the screen turns off. Warning states app uninstall/data-clear loses vault items; encryption at rest is not established by these sources.

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 564. Password and fingerprint gates — 1/50

`privacy.authentication_gates` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Configure password checks for hidden content/deletion and fingerprint unlock when Android M+ and hardware support it; password checks compare a stored SHA-256 hash.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 565. Password-protected backup archive — 1/50

`privacy.backup_encryption` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Optional archive password protects exported vault media, which is decrypted inside archive; vault custom credentials are included only with protected archives. Without archive password restored vault uses device lock.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 566. Block app-content screen capture — 1/50

`privacy.capture_protection` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

General Settings Secure Mode blocks screenshots, screen recordings and the recent-apps preview. It protects display/capture surfaces rather than encrypting ordinary files; vault encryption remains a separate feature.

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 567. Temporary account deactivation — 1/50

`privacy.disable_account` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Disabling hides profile, photos, comments and likes until login reactivates the account; permanent deletion is separate and may have an admin-configured grace period.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 568. End-to-end encryption — 1/50

`privacy.e2ee` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

End-to-end encryption

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 569. Local-first sanitized error reports — 1/50

`privacy.error_reporting_control` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

1.6.0 retains at most 30 reports for 30 days locally, deduplicating repeats; admin may opt into maintainers or own Sentry/GlitchTip. Reports rebuilt from allowlisted fields remove paths/names/URLs/identifiers.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 570. Authenticated-exit handoff viewer — 1/50

`privacy.guest_view` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Mobile guest view restricts browsing to one item/selection/album, hides edit/share/delete/info/navigation and requires configured device authentication to exit.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 571. IP upload blocking — 1/50

`privacy.ip_blocklist` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Administrator-configurable IP blacklist is explicitly documented.

- **Core (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 49/50.

### 572. Manual NSFW display controls — 1/50

`privacy.nsfw_display_controls` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Hide or blur manually flagged NSFW content in listings, control inclusion in random results and lock user flag changes. This is not automatic moderation.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 573. PIN-locked assets — 1/50

`privacy.pin_locked_folder` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Locked Folder hides assets until session unlock; access initially lasts 15 minutes and can extend with activity. While unlocked, locked assets may appear in search/utilities; Lock/sign-out revokes access.

- **Core (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 574. Hide identities without hiding pictures — 1/50

`privacy.private_people` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Private/hidden people withhold names/regions from viewers/guests/visitors and remove names from generated titles after maintenance; pictures remain visible, so this is not redaction/encryption.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 575. User-held recovery key — 1/50

`privacy.recovery_key` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

A 24-word key recovers access after password loss; absent password, signed-in recovery route/key or preconfigured trusted contact, support cannot decrypt Photos data.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 576. Hide app-switcher content — 1/50

`privacy.screen_content_protection` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

Mobile Hide content obscures app-switcher views and disables screenshots on Android; no claim of general screen-recording prevention is made.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 577. Password hashing and configurable sessions — 1/50

`privacy.session_security` · Domain: **privacy** · Core: **1** · Product-lineage groups: **1**

PBKDF2 with legacy password migration, HttpOnly sessions, isolated admin/user login and configurable age. HTTPS-only Secure cookies are configurable and disabled by default.

- **Core (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 578. Account activity history — 1/50

`safety.account_activity_log` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Security help recommends reviewing Account Log for suspicious activity. This is account history, not a durable pre-operation crash-recovery file journal.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 579. Atomic report publication — 1/50

`safety.atomic_report_export` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Analysis export flushes and syncs a sibling temporary file before atomic publication; failed writes preserve the previous report destination. This is report safety, not copied-photo verification.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 580. No automatic cross-device destructive sync — 1/50

`safety.backup_deletion_separation` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Native-device deletion does not delete backup, and cloud deletion does not silently erase the device original. Ente remembers uploaded files to avoid automatically re-uploading deliberately deleted cloud copies.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 581. Non-writing builder inspection — 1/50

`safety.builder_dry_run` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

--dry-run performs processing but does not save manifests, clean thumbnails or run plugin side effects; --key-regex limits inspection to matched storage keys.

- **Core (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 582. Companion-aware move rollback — 1/50

`safety.companion_operation_rollback` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

If one file of a photo cannot move, previously moved companion files are put back; rename also retains old names on failure. Docs establish per-photo rollback, not a durable crash-recovery journal.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 583. Rehash unchanged-timestamp files — 1/50

`safety.content_change_check` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Check file contents rereads every byte to detect replacements retaining old mtime, then reimports/reindexes changes with appropriate personal-data preservation. It is not documented as bit-rot recovery or copy verification.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 584. Verify copied/exported output content — 1/50

`safety.copy_verification` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Verify copied/exported output content

- **Core (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 585. Preserve corrupt catalogue — 1/50

`safety.corruption_preservation` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Detects per-library corruption and prompts a library switch while preserving the original database instead of silently rebuilding it.

- **Core (1):** [julyx10/lap](<profiles/R19-julyx10-lap.md>)
- **Not established by this research:** 49/50.

### 586. Reset original capture timestamp — 1/50

`safety.date_reset` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Timewarp --reset restores original recorded date/time/timezone only on macOS 13+ and only where Photos stored those original values.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 587. Log deletion choices — 1/50

`safety.deletion_choice_log` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

--log writes file-deletion choices to a chosen logfile; documentation does not describe rollback or saved file contents.

- **Core (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 588. Preview imports, exports and edits — 1/50

`safety.dry_run` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Export/import/batch/sync/geotag/push-exif support dry-run paths; import also validates/render-checks templates and checks already-imported versus not-imported files without importing.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 589. Keep locally exported deleted copies — 1/50

`safety.export_trash_retention` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Cloud deletion moves exported files into an export Trash folder; subsequently emptying cloud Trash does not automatically delete those local copies.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 590. Timestamped checksum-cache backups — 1/50

`safety.hash_database_backup` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Storage implementation provides timestamped copies of existing hash.json; this is backup of small integrity metadata, not copies of all media.

- **Core (1):** [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 49/50.

### 591. Hosted database backup and restore checks — 1/50

`safety.hosted_catalogue_backup` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Specification describes HA Postgres, six-hour snapshots, daily portable dumps, encrypted locked cross-provider copies and daily restore testing with alerts. These are service operational claims, not tested here.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 592. Provider-level deletion protection — 1/50

`safety.hosted_retention_lock` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Hosted Wasabi replica uses compliance hold plus a 21-day release buffer; cleanup occurs later after customer permanent deletion. This does not promise user restoration after Trash expires.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 593. User keyword filters — 1/50

`safety.keyword_filters` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Current configuration supports custom content filters with bounded keywords, scan length, regex size and creation/update rates; default limits include 20 filters and 10 keywords per filter.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 594. Preview proposed directory tree — 1/50

`safety.organization_preview` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Shows the proposed hierarchy before executing operations and offers another organization mode when the proposal is rejected; execute_operations also has an explicit non-mutating dry_run path.

- **Core (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 595. Accurate batch-delete outcomes — 1/50

`safety.partial_failure_reporting` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Bulk deletion reports complete success, partial failure or total failure and returns failed paths instead of always claiming success.

- **Core (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 596. Explicit permanent cleanup — 1/50

`safety.permanent_delete` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Duplicate and disk-analysis deletion directly remove selected files, report removed/already-absent/failed outcomes and reconcile scan caches. Analysis stops a batch on possible partial mutation or lost authority.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 597. Mobile read-only/kid mode — 1/50

`safety.read_only_client` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Read-only app mode permits timeline viewing while preventing accidental device photo deletion; not an encrypted vault.

- **Core (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 598. Replica restoration endpoint — 1/50

`safety.replica_restore` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Loader exposes images/restore calling restoreFromReplica; exact operator workflow/backup completeness remains unverified.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 599. Mute/block/report controls — 1/50

`safety.social_moderation` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Accounts can be muted/blocked from feeds; direct messages can be reported or deleted. Config bounds user mutes/blocks/domain blocks.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 600. Startup storage health checks — 1/50

`safety.storage_mount_checks` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Read/write marker checks validate expected storage mounts and permissions; failed checks normally prevent server startup.

- **Core (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 601. Scoped synchronization rollback snapshots — 1/50

`safety.sync_recovery_snapshots` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Sync snapshots allow local rollback on failure with retention, size display, export/deletion and active-use protection. Cannot restore deleted remote objects; not general file-operation undo.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 602. Preview synchronization — 1/50

`safety.sync_simulation` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Simulation-only mode reports prospective filesystem/database synchronization without applying changes; distinct from a general undo journal.

- **Core (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 603. Protect originals during transforms — 1/50

`safety.transform_copy` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

$IN transformations use a temporary copy by default; --no-copy deliberately permits the external command to modify the original and is warned as data-loss-prone.

- **Core (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 604. Photos Legacy recovery — 1/50

`safety.trusted_contact_recovery` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Previously accepted Ente trusted contacts can request recovery with a 7/14/30-day owner veto period, then change account password; configured from Photos mobile and applicable to photo succession.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 605. Unmounted/mass-missing protection — 1/50

`safety.unavailable_library_guard` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Missing-file detection checks whole result before changes, refuses apparently unmounted roots or configured excessive missing count and avoids flagging photos after unreadable-subfolder scans.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 606. Recover result saving without reupload — 1/50

`safety.upload_finalization_recovery` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Records remote completion separately from gallery/success-script finalization. Retrying original task uses persisted finalization data and API finalizationId rather than uploading again.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 607. Configurable upload size and type restrictions — 1/50

`safety.upload_limits` · Domain: **safety** · Core: **1** · Product-lineage groups: **1**

Server enforces configured maximum size and allowed filename/MIME suffix combinations; this is not evidence of full decoding, malware scan or content-safety recognition.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 608. Find boards by name — 1/50

`search.board_name` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Board search uses name; autocomplete and owner-name filters help select boards.

- **Core (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Not established by this research:** 49/50.

### 609. Share/bookmark filter URLs — 1/50

`search.bookmarkable_filters` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Active filters live in page address, appear as removable chips and preserve words/media when cleared; this is URL persistence rather than a saved-query catalogue.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 610. Human-readable date filtering — 1/50

`search.calendar_terms` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Parses month names/abbreviations, day ordinals and years into capture-date constraints; when a month lacks a year, selects the current or most recent applicable year.

- **Core (1):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 49/50.

### 611. Find missing/edited/cloud/deleted assets — 1/50

`search.catalogue_states` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Query missing originals, referenced versus managed, iCloud-managed/synced, hidden, favorite, edited/external-edit, in/no album, deleted and missing descriptive metadata states.

- **Core (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 612. Independent file and tag domains — 1/50

`search.domain_scoping` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Choose local/trash/known-file domain and specific tag service, including union of several file domains; current/pending tags can be searched separately.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 613. Full-text partial phrase search — 1/50

`search.full_text` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

README explicitly supports full-text multi-phrase, partial-word retrieval; exact filename/path tokenization is not specified in the inspected feature section.

- **Core (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 614. Refine the open directory or search result — 1/50

`search.local_result_filters` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Feature manual describes a local filter panel that further narrows the current directory or search results, distinct from submitting the full structured query language.

- **Core (1):** [bpatrik/pigallery2](<profiles/R42-bpatrik-pigallery2.md>)
- **Not established by this research:** 49/50.

### 615. Filter pins by owner or board — 1/50

`search.owner_board_filters` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

API supports submitter username and board ID filters and lists pins/boards newest-first by ID.

- **Core (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Not established by this research:** 49/50.

### 616. Search by downstream usage — 1/50

`search.publication_usage` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Nested usages constraints include status, platform, section, publication, orderedBy and content references; request filters also cover usage and syndication status.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 617. Adjust result set size — 1/50

`search.result_count` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Settings exposes a persisted 10–1000 result slider in increments of ten; actual results are bounded by indexed library size.

- **Core (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 49/50.

### 618. Channel and access-status filters — 1/50

`search.storage_access` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Filter by storage channel and access state in addition to name/directory/tag/type.

- **Core (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 619. Administrative record filters — 1/50

`search.storage_owner_moderation` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Admins can filter by storage source, username/user type, own-versus-all and violation flag, with ascending/descending order selection.

- **Core (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 49/50.

### 620. Find untagged entries — 1/50

`search.untagged` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

special:untagged finds entries without tags. special:empty availability conflicts across docs and is not included in this present claim.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 621. Find uploads by ID or IP — 1/50

`search.upload_identifiers` · Domain: **search** · Core: **1** · Product-lineage groups: **1**

Management can query numeric ID, 16-character image ID or uploading IP, and filter suspicious/adult-classified records.

- **Core (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 622. Photo and album sharing to users — 1/50

`sharing.account_shares` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Despite stale README roadmap, pinned backend has share/unshare handlers for photos and user albums plus shared-to/from-me routes; original access checks recognize these memberships.

- **Core (1):** [hooram/ownphotos](<profiles/R37-hooram-ownphotos.md>)
- **Not established by this research:** 49/50.

### 623. Signup and profile controls — 1/50

`sharing.account_verification` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Configure email confirmation, minimum user age, profile-avatar/background size limits and whether users may delete their own content.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 624. Shared social activity feed — 1/50

`sharing.activity_feed` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Mobile Feed aggregates likes/comments/replies from shared albums; it is social history, not an operation-recovery journal.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 625. Embed albums and publish RSS — 1/50

`sharing.album_embedding` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Edition table marks album embedding and RSS feeds as free modules.

- **Core (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 626. Require accounts to view shares — 1/50

`sharing.authenticated_share_policy` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Instance settings separately require sign-in for media shares or collection shares; anonymous access to public routes is independently configurable.

- **Core (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 627. Enable/disable replies per post — 1/50

`sharing.comment_controls` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Post menu can enable or disable comments/replies from desktop or mobile browser.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 628. Copy generated image links — 1/50

`sharing.copy_links` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Upload UI offers copying and one-click link copying; API returns computed links and storage paths.

- **Core (1):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>)
- **Not established by this research:** 49/50.

### 629. Private-message interface — 1/50

`sharing.direct_messages` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Direct supports photos/videos, text, feed posts, profiles, hashtags and locations; unsolicited messages may enter a filtered inbox. Help says direct media does not appear on hashtag/location pages or share onward through Pixelfed to other sites.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 630. Stable redirect URLs over changing hosts — 1/50

`sharing.dispatch_links` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

V2 uploads to selected root, creates a dispatch/hash URL, starts secondary upload asynchronously and serves cached/provider redirects. Stable URL can outlive a provider target change.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 631. Hide public download controls — 1/50

`sharing.download_button_control` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Owners can hide download buttons, but recipients can still copy via browser/tools/screenshots and metadata is not stripped. This is not DRM or guaranteed original-file protection.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 632. Album download visibility control — 1/50

`sharing.download_permissions` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Public albums can be configured downloadable or not; no claim is made that this prevents saving images already displayed.

- **Core (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 633. Encrypted album-scoped discussions — 1/50

`sharing.encrypted_comments_reactions` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Shared albums/public links support comments, quoted replies, likes and anonymous display names. Same photo has separate threads per album; owners/admins moderate. Comments cap at 500 characters and do not apply to unshared private albums.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 634. Expiring hosted images — 1/50

`sharing.expiring_uploads` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Enable expirable uploads that are removed after a selected date and configure automatic guest-upload deletion. This deletes hosted content, not merely a share token.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 635. Subscribe to hashtag feeds — 1/50

`sharing.follow_hashtags` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Following a hashtag adds its photos/videos to feed; help gives follow limits of 20/hour and 100/day.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 636. Read-only whole-library sharing — 1/50

`sharing.library_share` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Share ongoing own photos with another account and independently opt into location/people/camera/captions/originals; recipient may mix them into timeline but cannot edit or add to own albums.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 637. Link audience device cap — 1/50

`sharing.link_device_limits` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Limits unique IP+User-Agent combinations, not actual physical devices; already admitted combinations retain access after the cap is reached. Free plans have a ten-device cap.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 638. Masonry, grouped and Trip layouts — 1/50

`sharing.link_layouts` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Public viewers support proportional masonry, date groups or map/timeline Trip layout; Trip currently redirects custom-domain links to albums.ente.com.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 639. Multiple reusable link formats — 1/50

`sharing.link_templates` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Copy Markdown/HTML/URL/UBB/custom links individually or in batches; gallery supports url/name/extension placeholders, cloud per-bucket templates also object path/directory.

- **Core (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 640. Account mentions — 1/50

`sharing.mentions` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Help documents tagging/mentioning up to five profiles in a post or comment; no automatic face recognition is implied.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 641. Per-share detail and original controls — 1/50

`sharing.metadata_controls` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Public date/location/camera/caption/face-name switches default off. Original public delivery requires all five; otherwise metadata-free copies are served. Whole-library originals independently override embedded privacy expectations.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 642. Restore moderation-quarantined images — 1/50

`sharing.moderation_restore` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Administrative suspic_reimg action restores files from the suspect-image area independently of the ordinary recycle area.

- **Core (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 643. Multi-image/video posts — 1/50

`sharing.multi_media_posts` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Composer accepts several media files together or individually; per-post count is instance-configured (default max_album_length is four).

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 644. Proxy-mediated original protection — 1/50

`sharing.original_proxy_protection` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Group can enable original protection, withholding direct links and serving processed/cached responses through PHP with configurable image cache lifetime; not encryption.

- **Core (1):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>)
- **Not established by this research:** 49/50.

### 645. One-way partner library sharing — 1/50

`sharing.partner_library` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Grant broad asset/metadata/download/resharing access with optional per-partner timeline inclusion. Person data and favorites are not shared; both parties must grant separately for reciprocity.

- **Core (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 646. Approval-gated person sharing — 1/50

`sharing.person_share` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Only manually labelled person photos count; existing labels initially approve, later labels await review. Inferred/unknown faces do not auto-share; metadata switches start off and originals are withheld.

- **Core (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 647. Approved-follower visibility — 1/50

`sharing.private_accounts` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Private Account setting limits photo/video visibility to approved followers and prompts about existing followers/new requests; not an encryption feature.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 648. Embeddable profiles and posts — 1/50

`sharing.profile_post_embeds` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Current instance configuration separately enables profile and post embeds by default; exact embed UI is not established by the unfinished help page.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 649. Per-provider account requirements — 1/50

`sharing.provider_access_levels` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Provider Auth setting distinguishes guest, any signed-in user and administrator-only use; this is upload-provider access, not password-protected photo albums.

- **Core (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 650. QR codes for direct image links — 1/50

`sharing.qr_links` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

README lists generating a QR code from an image's direct link.

- **Core (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 49/50.

### 651. Configurable gallery reactions — 1/50

`sharing.reactions` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

v1.2 release adds controls to disable gallery reactions; precise reaction types are not stated in inspected note.

- **Core (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 652. Instance registration policies — 1/50

`sharing.registration_policy` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Config controls open registration, email verification, maximum accounts and invites; curated registration and user invitations are optional modes.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 653. Scoped device credentials — 1/50

`sharing.scoped_app_passwords` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

App passwords support WebDAV-only scope; even Full Access app credentials cannot change account password or manage users.

- **Core (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 654. Manually mark sensitive albums — 1/50

`sharing.sensitive_albums` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Free sensitive-album module and is_nsfw album field allow manual content marking; no automatic classifier is implied.

- **Core (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 655. Unified share management — 1/50

`sharing.share_inventory` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

/shares lists owned image and collection shares; filters type, expired/has/no-expiry and password protection, with free-text underlying-name search.

- **Core (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 656. Social preview metadata — 1/50

`sharing.social_cards` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Shared images, but explicitly not albums, support Twitter Cards and Open Graph; historical Twitter domain approval instructions are not current service guarantees.

- **Core (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 657. Partner syndication API — 1/50

`sharing.syndication` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Media API exposes per-partner image syndication and search can filter syndication status; downstream commercial integrations are deployment-specific.

- **Core (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 658. Unlisted publishing — 1/50

`sharing.unlisted_posts` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Unlisted posts do not appear in public timelines, as explicitly documented in timeline help.

- **Core (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 659. Upload history — 1/50

`sharing.upload_history` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Dedicated history offers latest/last-first ordering and clear-history confirmation; clearing history is not documented as deleting provider copies.

- **Core (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 49/50.

### 660. Multi-window upload limits — 1/50

`sharing.upload_rate_limits` · Domain: **sharing** · Core: **1** · Product-lineage groups: **1**

Configurable minute/hour/day/week/month counts apply to a logged-in user or anonymous uploader IP, based on recent image records.

- **Core (1):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>)
- **Not established by this research:** 49/50.

### 661. Configurable album/photo sorting — 1/50

`sort.catalogue_fields` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

sortingAlbums and sortingPhotos store SQL ordering fragments; some settings require direct database editing rather than a UI option.

- **Core (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 662. Sort by catalogue addition date — 1/50

`sort.entry_added` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

Results can be ordered by when the file entry was added to the library, explicitly distinct from file creation, modification or photo capture time.

- **Core (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 663. MIME sorting — 1/50

`sort.media_type` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

Type sorting compares media MIME strings.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 664. Modification-date sorting — 1/50

`sort.modified_date` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

Date comparator uses getDateModified, even though a menu identifier contains date_taken; not claimed as EXIF capture-date sorting.

- **Core (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 665. Tag-namespace ordering — 1/50

`sort.namespace` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

Configure namespace-based sorting and collection rules; limit semantics differ from simple metadata sorts.

- **Core (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 666. Date ordering — 1/50

`sort.upload_date` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

Album/search listing routes support date sorting and ascending/descending order; EXIF capture-date semantics are not established.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 667. Sort by video duration — 1/50

`sort.video_duration` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

Sort by video duration

- **Core (1):** [deckerst/aves](<profiles/R14-deckerst-aves.md>)
- **Not established by this research:** 49/50.

### 668. Popularity ordering — 1/50

`sort.view_count` · Domain: **sort** · Core: **1** · Product-lineage groups: **1**

Album/search listings support view-count sorting.

- **Core (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 669. Group-based storage routing — 1/50

`storage.distribution_groups` · Domain: **storage** · Core: **1** · Product-lineage groups: **1**

Distribution groups associate group name, storage-key ID, user type and compression flag; default group cannot be deleted.

- **Core (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 49/50.

### 670. Three-provider hosted replicas — 1/50

`storage.hosted_replication` · Domain: **storage** · Core: **1** · Product-lineage groups: **1**

Hosted specification describes two hot encrypted copies in Amsterdam/Frankfurt and one cold copy in Paris across Backblaze/Wasabi/Scaleway; self-hosters must design their own redundancy.

- **Core (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 671. Browser and system trace cleanup — 1/50

`system.activity_trace_cleanup` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Clears selected browsing history, searches, cookies, recent items and clipboard traces; this is an OS/application administration tool, not photo-metadata privacy or secure disk erasure.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 672. Shrink supported application installations — 1/50

`system.application_optimization` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Deep Cleanup overview documents application optimization to reduce supported application size without affecting normal use; exact eligible apps and transformations are not specified there. This is not photo compression.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 673. Uninstall applications and remnants — 1/50

`system.application_uninstall` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Uninstalls applications and reviews associated caches/settings/leftovers, treating potential personal files cautiously. AI manual warns vendor uninstallers control their own final scope.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 674. Windows file-oriented menu actions — 1/50

`system.context_menu_extensions` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Add copy-path/name/image-dimensions, terminal-here, desktop shortcuts and system-tool shortcuts.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 675. Windows Explorer menu management — 1/50

`system.context_menu_management` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Since 1.2.3, browse by app/menu location, disable/restore/remove entries, configure file types, switch supported Windows 11/classic styles and optionally restart Explorer.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 676. Common system repair actions — 1/50

`system.maintenance` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Documented maintenance targets missing search results, incorrect icons, sound and network issues; available operations depend on platform.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 677. Resource-heavy app and memory management — 1/50

`system.memory_management` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Find and quit resource-heavy applications and free memory manually or automatically; performance improvements are project claims.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 678. Cleanup and change history — 1/50

`system.operation_history` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Records completed cleanup/system changes, reclaimed space and failures. Duplicate deletion appends history after execution; this is not an undo-capable transactional operation journal.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 679. Live resource and hardware metrics — 1/50

`system.resource_monitor` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

CPU/GPU/memory/network/disk trends; supported devices also expose temperature, power, battery and disk-health information, with menu/taskbar/tray/floating displays. These are whole-computer metrics, not photo-library analytics.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 680. Disable and re-enable startup entries — 1/50

`system.startup_management` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Manage startup registrations to reduce login/background load, with ability to turn entries back on.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 681. Built-in system settings optimization — 1/50

`system.validated_optimization` · Domain: **system** · Core: **1** · Product-lineage groups: **1**

Only built-in validated settings are accepted; no arbitrary commands/scripts/registry paths. Values are reread after changes and high-impact, elevated or restart-required actions are flagged.

- **Core (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 682. Optional item-level AI explanations — 1/50

`ai.cleanup_explanations` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

Explains cleanup, privacy, startup, settings, maintenance, large/duplicate files and uninstall candidates on explicit request. Does not select items, change risk classification, execute commands or authorize cleanup.

- **Optional (1):** [harry0703/MangoDisk](<profiles/R15-harry0703-mangodisk.md>)
- **Not established by this research:** 49/50.

### 683. Custom zero-shot vocabulary — 1/50

`ai.custom_tag_vocabulary` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

Admin custom_tags.txt adds words or word=description with multiple prompt descriptions separated by \|; at most two custom/five total labels, no model retraining, and old photos need retagging.

- **Optional (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 684. Legacy ModerateContent integration — 1/50

`ai.legacy_moderation_provider` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

Existing ModerateContent keys remain usable only for old Telegraph-hosted files; new registrations are closed and Telegram Bot API files cannot be reviewed by this provider.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 685. Per-model execution policy — 1/50

`ai.model_scheduling` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

vision.yml supports auto/manual/on-index/newly-indexed/on-demand/on-schedule/always/never modes; on-index limited to built-in local models to avoid blocking ingestion.

- **Optional (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 686. Moderation model discovery and fallback — 1/50

`ai.moderation_model_fallback` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

Override the vision model or use a built-in fallback chain. Optional Cloudflare account credentials discover active vision models, exclude retired ones and cache the catalogue for six hours.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 687. Optional private-content classification — 1/50

`ai.nsfw_detection` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

NSFW detector can mark potentially objectionable images private; docs call it only partly reliable and older indexed images need rescan.

- **Optional (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 688. Separate nsfwjs moderation service — 1/50

`ai.selfhosted_moderation` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

Can deploy an nsfwjs REST container or compatible endpoint returning Drawing/Hentai/Neutral/Porn/Sexy probabilities; this is a separate service, not in-process local inference.

- **Optional (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 689. Interactive subject segmentation — 1/50

`ai.subject_cutout` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

Model-backed long-press or editor Cutout/Remove background uses include/exclude points with undo/redo/refinement; copy/share/save transparent PNG while keeping original.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 690. Background automatic upload tagging — 1/50

`ai.upload_tagging` · Domain: **ai** · Core: **0** · Product-lineage groups: **1**

Live documentation describes opt-in post-upload tagging of originals on supported channels, excluding External and images over 20 MiB. Disabled by default; upload response does not wait. Presence in frozen v2.7.8 is not established by its notes.

- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 691. People-driven auto-add albums — 1/50

`albums.auto_add_people` · Domain: **albums** · Core: **0** · Product-lineage groups: **1**

Mobile config adds existing/new owned uploads containing selected named people after local face indexing, including editable collaborative albums; Favorites/Uncategorized are excluded and disabling ML pauses updates.

- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 692. User-owned reusable selections — 1/50

`albums.personal_collections` · Domain: **albums** · Core: **0** · Product-lineage groups: **1**

User Collections lets logged-in users maintain unlimited selections separate from albums; admins search/edit/export collections as CSV. Cloud Enterprise+.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 693. Custom semantic collections — 1/50

`albums.semantic_categories` · Domain: **albums** · Core: **0** · Product-lineage groups: **1**

Define categories with text description, optional example photos and Broad/Balanced/Strict/Exact preference; preview matches, pin/set cover and optionally exclude videos. Categories classify locally but do not imply embedded tag writing.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 694. Optional analytics scripts — 1/50

`analytics.custom_scripts` · Domain: **analytics** · Core: **0** · Product-lineage groups: **1**

Dashboard accepts custom tracking scripts in head/body; operators control the added privacy implications.

- **Optional (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 695. Report storage usage per user — 1/50

`analytics.user_storage_usage` · Domain: **analytics** · Core: **0** · Product-lineage groups: **1**

Edition matrix separately lists per-user space usage for SE; reporting consumed storage is distinct from enforcing the account-capacity quota.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 696. Show tags on album view — 1/50

`browse.album_tag_display` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

Edition comparison gates displaying tags directly on the album view to SE, despite free tag assignment, listing and tag-album creation.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 697. Encrypted video streaming beta — 1/50

`browse.encrypted_hls` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

Optional stream generation creates 720p H.264 at 2 Mbps in encrypted HLS with encrypted playlist, enabling seeking without downloading whole originals. Stream storage is quota-exempt only during beta.

- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 698. Customize album feed cards — 1/50

`browse.flow_card_customization` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

SE separately provides compact Flow cards and extensive card customization; the basic access-controlled feed is free.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 699. Live GUI scan results — 1/50

`browse.live_scan_tree` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

Shredder streams CLI JSON into a tree while scanning and allows editing keep/delete decisions after scan.

- **Optional (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 700. Person growth timelines — 1/50

`browse.person_memory_lane` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

Mobile Memory Lane requires at least two years with four eligible person photos per year; known ages below three, hidden items and ignored faces are excluded. Timelines include age/year captions and public-link presentation.

- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 701. Selectable OCR overlay — 1/50

`browse.text_selection` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

Own-photo viewer T action overlays recognized text for mouse selection/copy; requires OCR results.

- **Optional (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 702. Custom timeline formats — 1/50

`browse.timeline_customization` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

SE comparison separately gates custom timeline granularity, formatting and per-album timeline customization.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 703. Video timeline hover previews — 1/50

`browse.video_storyboards` · Domain: **browse** · Core: **0** · Product-lineage groups: **1**

go-vod generates thumbnail sprites/VTT storyboards for video hover previews, cached persistently with keyframes.

- **Optional (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 49/50.

### 704. Optional capture-time geotagging — 1/50

`capture.geotagging` · Domain: **capture** · Core: **0** · Product-lineage groups: **1**

Camera introduction says geotagging starts disabled, requires location permission and records location in saved files when enabled.

- **Optional (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 49/50.

### 705. Voice-launched camera — 1/50

`capture.voice_trigger` · Domain: **capture** · Core: **0** · Product-lineage groups: **1**

README describes Google voice actions for taking a picture and selecting front/rear cameras; requires the external voice-assistant integration.

- **Optional (1):** [fossasia/phimpme-android](<profiles/R40-fossasia-phimpme-android.md>)
- **Not established by this research:** 49/50.

### 706. Resumable mass deletion utility — 1/50

`cleanup.bulk_delete_script` · Domain: **cleanup** · Core: **0** · Product-lineage groups: **1**

Administrator script consumes image IDs and Internal API credentials, records last processed ID and separate success/error lists. Documentation explicitly says no mass-deletion UI; logs are not an atomic pre-operation journal.

- **Optional (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 707. Quick or full video validation — 1/50

`cleanup.video_validation` · Domain: **cleanup** · Core: **0** · Product-lineage groups: **1**

Off-by-default ffprobe header checks and slow ffmpeg full-decode checks require external ffmpeg; videos are otherwise not checked by Broken Files.

- **Optional (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 708. Commercial Pro+ hosting business tools — 1/50

`commerce.hosting_plans` · Domain: **commerce** · Core: **0** · Product-lineage groups: **1**

Current paid-edition documentation advertises plans, orders, tickets, feedback, announcements, coupons and Alipay/WeChat payments. These belong to separate Pro+, not demonstrated open-source repository functionality.

- **Paid (1):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>)
- **Not established by this research:** 49/50.

### 709. Desktop companion client — 1/50

`deployment.desktop_client` · Domain: **deployment** · Core: **0** · Product-lineage groups: **1**

A documented separate desktop companion for the media service. Exact operating-system and release availability require their own evidence.

- **Plugin/integration (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 710. Quick interface-language selector — 1/50

`deployment.language_switcher` · Domain: **deployment** · Core: **0** · Product-lineage groups: **1**

Language Switch adds a flag selector for one-click switching among enabled gallery languages; base per-user language preference works without this convenience plugin.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 711. Shredder GTK frontend — 1/50

`deployment.optional_gui` · Domain: **deployment** · Core: **0** · Product-lineage groups: **1**

rmlint --gui launches separately installed GUI dependencies; 2.11.0 requires Python 3.12/GTK 3.22 for the GUI.

- **Optional (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 712. Paid packaged App Store distribution — 1/50

`deployment.paid_app_store` · Domain: **deployment** · Core: **0** · Product-lineage groups: **1**

In-app privacy guide describes paying for the application instead of a free app with network-dependent in-app purchases; this does not change the MIT source licence.

- **Paid (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 49/50.

### 713. Paid Play Store channel — 1/50

`deployment.play_store` · Domain: **deployment** · Core: **0** · Product-lineage groups: **1**

README says Play price supports the project and automatic Play updates; no separate paid functional tier is documented.

- **Paid (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 714. Separate media hostname — 1/50

`deployment.separate_media_domain` · Domain: **deployment** · Core: **0** · Product-lineage groups: **1**

Bind an image domain directly to the image root to hide /i/ in returned paths; it must differ from the site domain for this mode.

- **Optional (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 715. White-label gallery branding — 1/50

`deployment.white_label` · Domain: **deployment** · Core: **0** · Product-lineage groups: **1**

SE v7 can remove Lychee branding; free users can separately hide SE promotional calls to action without obtaining white-label entitlement.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 716. Clip duration/audio/visual thresholds — 1/50

`duplicates.audio_clip_thresholds` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **1**

Audio clip mode defaults to minimum 10% clip/source duration, 80% audio similarity and 85% frame confirmation; the confirmation requirement is independently configurable.

- **Optional (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 717. Audio-based partial video detection — 1/50

`duplicates.audio_partial_clips` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **1**

A second phase uses chroma fingerprints and sliding-window Hamming similarity to find shorter clips within longer sources, reports a Clip Offset and defaults to visual confirmation at the offset. Both files need audio.

- **Optional (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 718. Neural transformed-copy detection — 1/50

`duplicates.neural_transformed_videos` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **1**

DINOv2 embeddings via ONNX add matches for cropped, mirrored, zoomed, letterboxed or heavily edited copies; classic results remain authoritative and are never hidden by enabling AI. Default threshold is 94%.

- **Optional (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 719. External preprocessing before matching — 1/50

`duplicates.preprocess_matching` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **1**

--transform invokes an external program per file, with pipe or $IN/$OUT support. Documentation demonstrates stripping EXIF with exiv2 before matching, not perceptual image matching.

- **Optional (1):** [pkolaczk/fclones](<profiles/R34-pkolaczk-fclones.md>)
- **Not established by this research:** 49/50.

### 720. Silent/retimed clip matching — 1/50

`duplicates.visual_partial_clips` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **1**

Independent AI partial-detection switch compares dense keyframes by a consistent time offset; at least four hits must agree, default frame threshold 89%. Works without audio, including muted/re-dubbed clips.

- **Optional (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 721. Blur a person's faces in copies — 1/50

`editing.face_blur` · Domain: **editing** · Core: **0** · Product-lineage groups: **1**

Blur everywhere creates new copies of photos containing the selected person; face models also enable local blur/mosaic editor tools.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 722. Advanced SDK filters and adjustments — 1/50

`editing.proprietary_adjustments` · Domain: **editing** · Core: **0** · Product-lineage groups: **1**

Proprietary build conditionally includes IMG.LY advanced editor. UI defines exposure, highlights, shadows, clarity, gamma, colour, blur-focus, overlays, text and sticker controls; these must not be attributed to every FOSS build.

- **Optional (1):** [SimpleMobileTools/Simple-Gallery](<profiles/R20-simplemobiletools-simple-gallery.md>)
- **Not established by this research:** 49/50.

### 723. Single/batch TinyPNG compression — 1/50

`editing.remote_compression` · Domain: **editing** · Core: **0** · Product-lineage groups: **1**

README lists batch compression; configured TinyPNG processing accepts JPEG/PNG, skips previously compressed records and overwrites the local original with downloaded output. Multiple configured API keys can be selected.

- **Optional (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 724. Detect static video borders — 1/50

`editing.video_auto_crop` · Domain: **editing** · Core: **0** · Product-lineage groups: **1**

ffmpeg-backed optimization detects black bars or static edge content using thresholds/sample limits and applies the proposed crop to selected files.

- **Optional (1):** [qarmin/czkawka](<profiles/R03-qarmin-czkawka.md>)
- **Not established by this research:** 49/50.

### 725. Multiple formats per image — 1/50

`formats.alternate_downloads` · Domain: **formats** · Core: **0** · Product-lineage groups: **1**

enable_formats plus format_ext associates files such as CR2, CMYK JPEG or ZIP in pwg_format with one image. Cloud offers this from Enterprise; storing RAW companions does not prove RAW decoding.

- **Optional (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 726. Double-sided image pairs — 1/50

`formats.front_back_pairs` · Domain: **formats** · Core: **0** · Product-lineage groups: **1**

Back2Front links a reverse-side photo to a front ID, can hide the back from album listings and exposes See back in the viewer.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 727. Satellite/terrain and enhanced location service — 1/50

`geo.premium_maps` · Domain: **geo** · Core: **0** · Product-lineage groups: **1**

Essentials/Plus provide additional MapTiler satellite/outdoor/3D styles and enhanced geocoding; standard hosted vector map remains free. Globe viewer works across styles.

- **Paid (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 728. Custom map and geocoder endpoints — 1/50

`geo.selfhosted_services` · Domain: **geo** · Core: **0** · Product-lineage groups: **1**

Custom MapLibre Style JSON can reference self-hosted tiles/fonts/sprites with browser CORS; Nominatim URL can target a self-hosted service/proxy. This is not a bundled offline basemap or geocoder.

- **Optional (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 729. Online static-map provider support — 1/50

`geo.static_map` · Domain: **geo** · Core: **0** · Product-lineage groups: **1**

Static-map URLs embed image coordinates for Google, Mapbox streets/dark/light or Tyler/Stamen; this is not an offline basemap or full-library map.

- **Optional (1):** [UnevenSoftware/LeafPic](<profiles/R31-unevensoftware-leafpic.md>)
- **Not established by this research:** 49/50.

### 730. Billing and plan enforcement — 1/50

`integration.billing_quotas` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Backend includes Creem integration, tenant plans/overrides and request-level usage/quota enforcement. Specific hosted paid-only feature entitlements are not enumerated in inspected docs.

- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 731. Chrome/Firefox capture extensions — 1/50

`integration.browser_extensions` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Official docs link a separately maintained browser-pinry extension and browser stores for adding web content.

- **Plugin/integration (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Not established by this research:** 49/50.

### 732. Static-resource CDN and analytics hooks — 1/50

`integration.cdn_analytics` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Configure a pull-CDN URL for local static resources and analytics HTML in all views; neither is a claim of external original-image storage.

- **Optional (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 733. Separate image-serving CDN URLs — 1/50

`integration.cdn_urls` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Remote storage can provide a separate CDN read base URL; R2 S3 upload endpoint must not be confused with its public image domain.

- **Optional (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 734. Central OAuth gateway — 1/50

`integration.central_oauth` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Optional SaaS architecture uses a single OAuth callback domain that routes provider responses to per-tenant sessions.

- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 735. External comments — 1/50

`integration.comment_services` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Configure Disqus or arbitrary HTML/JavaScript comments on image views; not a native comments-store claim.

- **Optional (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 736. Configuration sync through Git/WebDAV — 1/50

`integration.configuration_sync` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Upload/download common settings, management settings or all configs using selected private Git/WebDAV target; direction can overwrite current defaults and contains credentials.

- **Optional (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 737. Custom duplicate handlers — 1/50

`integration.custom_action_commands` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Shell handlers receive duplicate and original paths; generated Python scripts can be customized for specialized actions.

- **Optional (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 738. Eagle library publication — 1/50

`integration.eagle` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Eagle 4 source publishes an existing Eagle library with folder/tag filters and folder-to-tag mapping.

- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 739. Markdown editor integrations — 1/50

`integration.editor_upload` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Typora &gt;=1.6 selects PicList directly; older Typora uses PicGo(app). Obsidian requires Image Auto Upload plugin and VS Code uses VS-PicList extension.

- **Plugin/integration (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 740. Custom external comparison commands — 1/50

`integration.external_tools` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Configure a command with duplicate and reference path placeholders; results can also open in the default application or reveal their containing directory.

- **Optional (1):** [arsenetar/dupeguru](<profiles/R06-arsenetar-dupeguru.md>)
- **Not established by this research:** 49/50.

### 741. Image handoff to Lens-like apps — 1/50

`integration.external_visual_search` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Separate Visual search shares current image/video frame with chosen installed app, can convert unsupported formats and needs explicit vault-item allowance because temporary decrypted data is exposed.

- **Plugin/integration (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 742. LAN photo/video casting — 1/50

`integration.fcast` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

FCast-compatible receiver required, discovered by mDNS or entered manually at default port 46899; remote pause/seek/speed controls depend on receiver codec support. No Chromecast protocol is involved.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 743. Previewed cross-device history sync — 1/50

`integration.gallery_sync` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Plans additions/updates/deletions/conflicts and supports local, remote or both conflict choices with exported summary; transfers records, never all cloud objects.

- **Optional (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 744. Derived-asset Git synchronization — 1/50

`integration.git_asset_sync` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Bundled opt-in plugin reuses manifest/thumbnails from a Git repository and optionally commits/pushes changes; push needs a token and Git on PATH.

- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 745. GitHub and Gitee image storage — 1/50

`integration.git_repository_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Both adapters are registered and eligible as dispatch root stores, alongside local/Flickr/Imgur; service setup/credentials remain external.

- **Optional (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 746. GitHub-backed originals — 1/50

`integration.github_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

GitHub storage is documented for small galleries/demos with about 1 GB recommended repository size, not unlimited archival scale.

- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 747. Hugging Face dataset storage — 1/50

`integration.huggingface_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Configured token and dataset repository support private repositories and LFS-based large-file uploads.

- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 748. Managed JavaScript lifecycle scripts — 1/50

`integration.lifecycle_scripts` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Scripts run at startup/shutdown, preprocess/transform/upload/success/gallery removal or manually; advanced uploader stage can set result URLs. Access includes filesystem/network and local .env values; no separate Node runtime required for scripting.

- **Optional (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 749. Telegram and Discord payload channels — 1/50

`integration.messaging_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Store payloads through configured bots/channels, with optional proxy URLs and Discord Nitro setting; not private local disk storage.

- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 750. Ordered ingest processors — 1/50

`integration.metadata_processors` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

ImageProcessor/MetadataCleaner interfaces enable configured Scala pipelines for agency detection, license assignment, credits and house-style normalization; custom implementations require integration, not a generic AI model.

- **Plugin/integration (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 751. Optional GitHub administrator login — 1/50

`integration.oauth` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Email/password is established at setup; GitHub OAuth requires configured client credentials and returned email matching an existing administrator, not arbitrary GitHub-user admin access.

- **Optional (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 752. OpenList storage integration — 1/50

`integration.openlist` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Uses OpenList API token/root and configurable upload/delete/metadata endpoints; remote permissions and expiring download URLs affect accessibility.

- **Optional (1):** [HoshinoSuzumi/chronoframe](<profiles/R43-hoshinosuzumi-chronoframe.md>)
- **Not established by this research:** 49/50.

### 753. PicGo web-uploader plugin — 1/50

`integration.picgo` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Separate PicGo web-uploader plugin maps image/token fields and the response URL after enabling API upload.

- **Plugin/integration (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 754. Companion Android configuration transfer — 1/50

`integration.pichoro` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

PicHoro imports uploader configuration by QR code; codes can expose destination credentials and should be transferred privately.

- **Plugin/integration (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 755. External-editor popup uploader — 1/50

`integration.popup_uploader` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Embed PUP JavaScript in another site to upload without leaving its editor and automatically insert URL/HTML/BBCode/Markdown; supports named forum vendors, custom selectors, styles and dynamic editors.

- **Plugin/integration (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 756. Post-export commands and import functions — 1/50

`integration.postprocessing_hooks` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Export executes template-based commands by output category; import can call configured Python post-functions, and timewarp accepts a custom timestamp function. External scripts are user-controlled executable integrations.

- **Optional (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 757. Pro external storage and MySQL — 1/50

`integration.pro_external_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

README advertises multiple external storage backends, MySQL, no advertising and professional support in separate ImgURL Pro; these are not verified free-source features.

- **Paid (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 758. Embed hosted videos — 1/50

`integration.remote_video_embed` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Embedded Videos imports URLs or embed code from YouTube/Vimeo/Dailymotion and others, with optional title/tag extraction and player settings; playback depends on those external services.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 759. Organization-specific rights sources — 1/50

`integration.rights_providers` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Includes Guardian hardcoded and runtime-configured providers for photographer/illustrator lists and Creative Commons options; additional sources can implement the provider trait.

- **Optional (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 760. Photo RSS feed extension — 1/50

`integration.rss_plugin` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

README lists lychee-rss as a separate feed-generating extension.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 761. SMB/CIFS image storage — 1/50

`integration.smb_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Configured network share credentials store originals and transformed caches in automatically created slink/images and slink/cache directories.

- **Optional (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 762. Optional spam/CAPTCHA services — 1/50

`integration.spam_services` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Legacy docs configure Akismet, StopForumSpam and reCAPTCHA thresholds; provider availability was not tested.

- **Optional (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 763. Jekyll album embedding extension — 1/50

`integration.static_site_embed` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

README lists a separate Jekyll Liquid tag for embedding Lychee albums in generated sites; no current Jekyll-version compatibility was established.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 764. Reuse Synology thumbnails — 1/50

`integration.synology_thumbnails` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

SYNO_THUMBS uses Synology @eaDir layout so existing DSM thumbnails are reused and newly created ones can be used by Photo Station.

- **Optional (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 765. Peer-assisted video distribution — 1/50

`integration.video_p2p` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Optional P2P video requires HLS plus FFmpeg and defaults off; config identifies an external WebTorrent tracker and Google STUN server.

- **Optional (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 766. Use a WebDAV storage provider — 1/50

`integration.webdav_backend` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Configure service URL, optional credentials/custom headers/public HTTP URL and automatic parent-directory creation.

- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 767. Sell downloads and prints — 1/50

`integration.webshop` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

Pro addon above SE supplies pricing, size/license choices, basket/order administration, managed download links and Mollie/PayPal/offline payments. Print support does not integrate with printing services.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 768. WeChat mini-program — 1/50

`integration.wechat` · Domain: **integration** · Core: **0** · Product-lineage groups: **1**

README explicitly limits the mini-program to paid Core and says it cannot currently connect to the open-source edition.

- **Paid (1):** [Hello-hao/Tbed](<profiles/R50-hello-hao-tbed.md>)
- **Not established by this research:** 49/50.

### 769. Scheduled listing sync and optional deletion propagation — 1/50

`library.cloud_sync` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

15-minute to daily approximate Android schedules, Wi-Fi-only auto sync, unrestricted manual sync and cold-start sync; opt-in remote deletions remove only app-downloaded copies, not arbitrary local originals.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 770. Download selected rendition size — 1/50

`library.download_size_choice` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Download by Size adds size selection to the download action using configured derivatives.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 771. External folder synchronization — 1/50

`library.folder_sync_plugin` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

README lists lycheesync as a separate extension for syncing an existing photo directory; this does not remove core managed-storage limitations.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 772. Instagram export import — 1/50

`library.instagram_import` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Imports Instagram JSON ZIP data including photos, captions and hashtags. Current dedicated config defaults to 1,000 posts, permits video/WebP, excludes archived posts and supports administrator/account-age/follower eligibility restrictions.

- **Optional (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 773. Android/iOS upload companions — 1/50

`library.mobile_upload` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Separate mobile apps send photos to the server; cited overview establishes upload, not unrestricted automatic background camera-roll backup.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 774. Offline browsing of cached remote previews — 1/50

`library.offline_cloud_previews` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Force offline uses only cache; account pinning downloads thumbnails/previews with partial-progress/retry status, and per-account/auto-only cache clears retain accounts/listings.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 775. Replace existing server media — 1/50

`library.replace_existing_asset` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Replace existing server media. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Unclear (1):** [simulot/immich-go](<profiles/R08-simulot-immich-go.md>)
- **Not established by this research:** 48/50.

### 776. Manage Immich albums — 1/50

`library.server_album_management` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

5.2.2 populates shared/v3 albums and allows owned-album rename/share/delete/member removal. Same-account Copy adds membership; Move is explicitly unsupported because albums are not folders.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 777. SSH photo-upload companion — 1/50

`library.ssh_upload_plugin` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

README lists the separate lycheeupload extension for uploading photos to Lychee via SSH. This is an advertised companion capability, not a built-in upload transport or independently tested extension.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 778. Adaptive repeating gallery queries — 1/50

`library.subscription_sync` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Subscriptions detect new URLs, adapt interval to source velocity, stop dead queries and publish to grouped landing pages; they do not reliably backfill old gaps.

- **Optional (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 779. Imageboard-thread watcher — 1/50

`library.thread_watcher` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Installed watcher definitions repeatedly check a thread, adapt to incoming frequency and stop at inactivity/404; not filesystem watching.

- **Optional (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 780. Uploader/admin/token separation — 1/50

`library.uploader_directory_separation` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

Separate upload-user, administrator and token-ID directories; the public square excludes those separated uploads and lists guest uploads only.

- **Optional (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 781. Gallery, URL and simple-page downloading — 1/50

`library.web_download` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

User-installed downloader definitions parse gallery searches, file/post URLs or simple page links; fresh installs contain no downloaders. Tags/notes can accompany files.

- **Optional (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 782. Toshiba FlashAir import extension — 1/50

`library.wifi_sd_import` · Domain: **library** · Core: **0** · Product-lineage groups: **1**

README lists lychee-FlashAir for importing photos from a Toshiba FlashAir WiFi SD card. Hardware/network setup and current extension compatibility were not separately verified.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 783. Regenerate missing medium derivatives — 1/50

`maintenance.generate_missing_medium` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **1**

README lists lychee-create-medium for generating missing medium-size photos; this is an external maintenance extension, not built-in image editing.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 784. IP-based upload blocking — 1/50

`maintenance.ip_rate_limits` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **1**

Configurable enabled middleware tracks attempts/time, temporary block period and threshold for persistent blocks; release 2.3.9 includes IP-block fixes.

- **Optional (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 785. Record-only administrative deletion — 1/50

`maintenance.record_removal` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **1**

Delete removes the dashboard record, not the Telegram/Telegraph original; later access can recreate a record. Blocking access uses the blacklist instead.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 786. Manage cached signatures — 1/50

`maintenance.signature_cache_controls` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **1**

Cache supports readonly, orphan pruning, clearing and vacuuming. Maintenance can run without directory arguments and still takes effect with readonly; operation order is clear, prune, update, vacuum.

- **Optional (1):** [adrianlopezroche/fdupes](<profiles/R32-adrianlopezroche-fdupes.md>)
- **Not established by this research:** 49/50.

### 787. Optional fork auto-updates — 1/50

`maintenance.upstream_sync` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **1**

An enabled GitHub Actions upstream-sync workflow updates the fork hourly, after which connected Pages deployment can rebuild.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 788. Strip metadata from derivatives — 1/50

`metadata.derivative_strip` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Imagick path removes metadata from medium images and thumbnails; this does not establish stripping metadata from downloadable originals.

- **Optional (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 789. Custom searchable metadata schema — 1/50

`metadata.domain_schema` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Configuration defines collapsible domain sections with string/integer/datetime/select fields, controlled vocabularies, validation and searchable aliases without modifying application code.

- **Optional (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 790. Optional EXIF database storage — 1/50

`metadata.exif_catalogue` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

MEDIA_EXIF_DATABASE defaults false; enabling stores EXIF in the database, without proving an end-user EXIF editing interface.

- **Optional (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 791. Compare/pull/push EXIF dates — 1/50

`metadata.exif_time_reconcile` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

With ExifTool compare Photos versus embedded timestamps, collect mismatches in an album, pull metadata into Photos or push it into originals; missing EXIF can fall back to file time.

- **Optional (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 792. Runtime metadata editing — 1/50

`metadata.live_cms` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Backend CMS edits titles/tags/descriptions and enabled state in PostgreSQL, with fresh data on refetch/page load without a builder run; tenant admins can also upload.

- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 793. Localized EXIF presentation — 1/50

`metadata.localized_exif_display` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Exif View translates displayed EXIF values into the gallery language; it does not rewrite the photo's underlying metadata into a different language.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 794. Language-specific titles and descriptions — 1/50

`metadata.multilingual_descriptions` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Extended Descriptions provides manually authored photo/album title and description variants selected by visitor language, with default/all-language fallbacks. This is separate from translating UI and is not automatic machine translation.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 795. Cost and allowed-use summaries — 1/50

`metadata.rights_cost_summary` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Configured UI can show payable, all-use, news/sport eligibility and supplier markers, based on deployment-specific rights rules rather than generic image availability.

- **Optional (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 796. License and expiry workflows — 1/50

`metadata.rights_expiry` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Copyrights defines selectable rights; Expiry Date can leave, archive or delete expiring files and notify downloaders/admins before/on expiry. Expiry Date is Cloud Enterprise+.

- **Plugin/integration (1):** [Piwigo/Piwigo](<profiles/R23-piwigo-piwigo.md>)
- **Not established by this research:** 49/50.

### 797. Metadata-template rights preview — 1/50

`metadata.rights_templates` · Domain: **metadata** · Core: **0** · Product-lineage groups: **1**

Configured templates preview their replacement usage-rights category in a locked editor and allow applying or cancelling without prematurely changing existing rights.

- **Optional (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 798. Selectable cache drivers — 1/50

`performance.cache_backends` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

README lists file cache by default plus configurable Memcached, Redis, DynamoDB and relational database alternatives.

- **Optional (1):** [lsky-org/lsky-pro](<profiles/R17-lsky-org-lsky-pro.md>)
- **Not established by this research:** 49/50.

### 799. Configurable/bounded thumbnail/cache limits — 1/50

`performance.cache_limits` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Configurable/bounded thumbnail/cache limits

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 800. CDN caching and purge integration — 1/50

`performance.cdn_cache` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Cloudflare delivery caches public responses and avoids Range fragments; configured Cloudflare API credentials can purge cached content after deletion/access changes.

- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 801. Reuse encrypted indexes across devices — 1/50

`performance.encrypted_ml_sync` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Index on desktop, sync encrypted results to mobile and disable mobile local indexing to reduce memory load. Concurrent clients avoid duplicate indexing but documentation says this does not accelerate the overall job.

- **Optional (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 802. Local or RAM export-state database — 1/50

`performance.export_database_location` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Place export state on a faster local disk or use RAM then flush on completion; RAM mode can improve NAS workloads but loses progress if interrupted.

- **Optional (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 803. External and distributed transcoding — 1/50

`performance.multiple_transcoders` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Deploy separate go-vod containers/hosts and list several addresses for load distribution with per-client sticky routing; supports external/object storage with documented setup.

- **Optional (1):** [pulsejet/memories](<profiles/R25-pulsejet-memories.md>)
- **Not established by this research:** 49/50.

### 804. Optional native FFmpeg bindings — 1/50

`performance.native_ffmpeg` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Can call FFmpeg functions natively for claimed speed improvement; requires compatible FFmpeg 8.x shared libraries rather than master builds.

- **Optional (1):** [0x90d/videoduplicatefinder](<profiles/R24-0x90d-videoduplicatefinder.md>)
- **Not established by this research:** 49/50.

### 805. Threaded export integration — 1/50

`performance.parallel_export_api` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

API documents concurrent export using threads on Python 3.11+; PhotosDB cannot be pickled for multiprocessing. This is an API/example capability, not a claimed default CLI speedup.

- **Optional (1):** [RhetTbull/osxphotos](<profiles/R21-rhettbull-osxphotos.md>)
- **Not established by this research:** 49/50.

### 806. Shared in-flight query cache — 1/50

`performance.query_embedding_cache` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

AI-search controller caches normalized query embeddings/futures so simultaneous equivalent queries share a remote call; zero-length polling skips Bedrock/KNN work.

- **Optional (1):** [guardian/grid](<profiles/R49-guardian-grid.md>)
- **Not established by this research:** 49/50.

### 807. Remote thumbnail publication — 1/50

`performance.remote_thumbnail_storage` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Bundled opt-in thumbnail-storage plugin uploads derivatives to default/secondary storage, rewrites URLs, deduplicates uploads per run and falls back to local URLs on upload failure.

- **Optional (1):** [Afilmory/afilmory](<profiles/R39-afilmory-afilmory.md>)
- **Not established by this research:** 49/50.

### 808. Optional fast directory scanner — 1/50

`performance.ripgrep_scan` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Installed ripgrep replaces wcmatch scanning for speed and Git-style glob parity; docs warn fallback pattern behavior can differ.

- **Optional (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 809. Separate API and processing workers — 1/50

`performance.split_workers` · Domain: **performance** · Core: **0** · Product-lineage groups: **1**

Include/exclude worker settings let containers isolate web/API work from background processing and distribute resources.

- **Optional (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 810. Encrypted provider-key storage — 1/50

`privacy.ai_key_encryption` · Domain: **privacy** · Core: **0** · Product-lineage groups: **1**

AI_CONFIG_SECRET encrypts saved API keys; operator must keep a separate backup because secret loss/change makes keys unreadable. This does not encrypt hosted images end-to-end.

- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 811. Webroot access-control extension — 1/50

`privacy.original_access_plugin` · Domain: **privacy** · Core: **0** · Product-lineage groups: **1**

README describes lychee-webroot as a separate extension controlling photo accessibility and keeping Lychee files hidden. Its existence must not be interpreted as default core original-file protection.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 812. Delayed repository account anonymisation — 1/50

`privacy.repository_anonymisation` · Domain: **privacy** · Core: **0** · Product-lineage groups: **1**

Repository content attribution is reassigned to a null account after default 90 days, configurable by operator; does not eliminate IP/content inference or malicious-server risks.

- **Optional (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 813. Protected original-image links — 1/50

`privacy.source_link_protection` · Domain: **privacy** · Core: **0** · Product-lineage groups: **1**

Configurable source protection uses keyed links; 2.8.7 changes token/key handling and invalidates old links. FAQ warns web-server image caching can cause 404 behavior.

- **Optional (1):** [icret/EasyImages2.0](<profiles/R26-icret-easyimages2-0.md>)
- **Not established by this research:** 49/50.

### 814. Uploader IP recording and optional lookup — 1/50

`privacy.upload_ip_geolocation` · Domain: **privacy** · Core: **0** · Product-lineage groups: **1**

Optional custom API receives upload IP and selected JSON fields populate UploadAddress. This is uploader network geolocation, not photo GPS mapping.

- **Optional (1):** [MarSeventh/CloudFlare-ImgBed](<profiles/R10-marseventh-cloudflare-imgbed.md>)
- **Not established by this research:** 49/50.

### 815. Optional low-disk operation guard — 1/50

`safety.free_space_guard` · Domain: **safety** · Core: **0** · Product-lineage groups: **1**

Can pause index/import/upload below configured free-space percentage with 100 MB floor; disabled by default because network/FUSE/container probes may be unreliable.

- **Optional (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 816. Restricted child accounts — 1/50

`safety.parental_controls` · Domain: **safety** · Core: **0** · Product-lineage groups: **1**

When administrators enable the feature, parents create linked child accounts and choose posting, commenting, liking/sharing and federation permissions; configured child-count limits apply.

- **Optional (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 817. GUI structured result filters — 1/50

`search.duplicate_results` · Domain: **search** · Core: **0** · Product-lineage groups: **1**

Filter path text plus size ranges, mtime and twin count; generate scripts for all results or only visible results.

- **Optional (1):** [sahib/rmlint](<profiles/R41-sahib-rmlint.md>)
- **Not established by this research:** 49/50.

### 818. Delegate search to connected server — 1/50

`search.server_semantics` · Domain: **search** · Core: **0** · Product-lineage groups: **1**

Cloud smart-search setting lets capable servers, currently Immich, answer queries; separate provider-type switches download thumbnails for local indexing, including NAS providers without their own AI.

- **Optional (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 819. Web account/session administration — 1/50

`sharing.account_admin_ui` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Plus adds UI for accounts/sessions; account deletion disables/signs out but retains account record and uploaded pictures. CLI remains in all editions.

- **Paid (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 820. Follower/account migration — 1/50

`sharing.account_migration` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Migration uses account aliases and compatible Pixelfed/Mastodon migration extensions. Post migration is documented for Pixelfed v0.11.9+ only when server-enabled; completion can take hours.

- **Optional (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 821. Internal user administration notes — 1/50

`sharing.admin_notes` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

SE provides an admin note for each user; the user manual distinguishes this internal note from the user's public/profile description.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 822. Human-readable album-name redirect plugin — 1/50

`sharing.album_name_redirect` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

README lists lychee-redirect as a separate extension that redirects an album name to a Lychee album, rather than a core routing guarantee.

- **Plugin/integration (1):** [electerious/Lychee](<profiles/R12-electerious-lychee.md>)
- **Not established by this research:** 49/50.

### 823. Referer allowlist — 1/50

`sharing.anti_hotlinking` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

ALLOWED_REFERERS accepts exact and wildcard-subdomain hosts. Other referring sites receive 403, but absent referers and the host's own domain remain allowed; this is not private-link authentication.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 824. File allow/block lists — 1/50

`sharing.blacklist_whitelist` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

KV records can be blacklisted to block loading or whitelisted to bypass moderation; whitelist-only mode requires approval before serving.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 825. Custom comment embedding — 1/50

`sharing.comment_embed` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Image view includes a comment.html file if present; this is an integration hook, not evidence of a built-in comment database.

- **Optional (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 826. Gallery contact form — 1/50

`sharing.contact_form` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Official edition matrix lists contact form as an SE-only v7 module.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 827. Optional administrative authentication — 1/50

`sharing.dashboard_authentication` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

BASIC_USER and BASIC_PASS enable dashboard login. Cloudflare Access is an alternative, with both /admin and /api/manage/* requiring protection.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 828. Automatic future-album sharing — 1/50

`sharing.family_library_auto_share` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Within family sharing, select owned albums in bulk and optionally share newly created albums automatically; shared capacity alone never grants content access.

- **Paid (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 829. Paid family capacity sharing — 1/50

`sharing.family_storage` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Paid subscriber plus five members share one plan while content stays private by default; admin can set individual storage limits.

- **Paid (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 830. Federated sharing such as ActivityPub — 1/50

`sharing.federation` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Federated sharing such as ActivityPub

- **Optional (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 831. Federated follower/block synchronization — 1/50

`sharing.follower_block_sync` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Configured federation supports signed follower-collection synchronization for followers-only delivery and block-list synchronization with cooldown/page limits.

- **Optional (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 832. Delegate group administration — 1/50

`sharing.group_administration` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Edition comparison explicitly lists group administrators for delegated group management as an SE capability, distinct from granting full-system administrator status.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 833. Share albums through group permissions — 1/50

`sharing.group_sharing` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

SE supports group sharing and per-album group access rights. AccessPermission can target a user group so album grants apply to its members; this is separate from free individual cross-user sharing.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 834. Multiple system administrators — 1/50

`sharing.multiple_administrators` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Edition matrix lists multi-admin support as SE; the user model's may_administrate permission grants full system administration, unlike a delegated group role.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 835. User and Viewer roles — 1/50

`sharing.premium_roles` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Essentials/Plus add editable-library User without global settings and read-only Viewer excluding private/archive and uploads/indexing.

- **Paid (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 836. Provider-signed temporary links — 1/50

`sharing.presigned_urls` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Cloud workflows support private temporary signed addresses and batch copying; expiration and accessibility depend on provider, not a PicList hosted share database.

- **Optional (1):** [Kuingsmile/PicList](<profiles/R27-kuingsmile-piclist.md>)
- **Not established by this research:** 49/50.

### 837. Per-provider registration/approval overrides — 1/50

`sharing.provider_registration_policy` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

OIDC providers can inherit/allow/block registration and inherit/require/auto-approve new accounts independently of global signup policy; existing users are unaffected.

- **Optional (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 838. Self-run file/tag repository server — 1/50

`sharing.repository_server` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Bundled separate server can host multiple services with registration tokens, accounts, uploader/downloader/admin permissions and server backups; designed for delayed sync, not live LAN browsing.

- **Optional (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 839. AES-secured image links — 1/50

`sharing.secured_image_links` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

SE offers secured image URLs; this is link protection, not evidence of encrypted-at-rest media or end-to-end encryption.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 840. Optional shared tag repositories — 1/50

`sharing.tag_repository` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Sync all repository hash/tag metadata into a local cache; uploads are explicitly queued/pended and removals may require janitor petitions. Supports multiple repos.

- **Optional (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 841. Uncapped paid link audiences — 1/50

`sharing.unlimited_link_devices` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

Paid plans can create public links without the free tier's ten-device limit.

- **Paid (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

### 842. Separate upload authentication — 1/50

`sharing.upload_authentication` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

UPLOAD_BASIC_USER and UPLOAD_BASIC_PASS protect both browser and multipart API uploads independently of dashboard credentials.

- **Optional (1):** [cf-pages/Telegraph-Image](<profiles/R16-cf-pages-telegraph-image.md>)
- **Not established by this research:** 49/50.

### 843. Manage user-group memberships — 1/50

`sharing.user_groups` · Domain: **sharing** · Core: **0** · Product-lineage groups: **1**

SE includes named user groups for team/client/family access management; a user can belong to multiple groups and membership records carry a group role.

- **Paid (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 844. Paid hosted capacity — 1/50

`storage.paid_cloud_capacity` · Domain: **storage** · Core: **0** · Product-lineage groups: **1**

README describes Photos as a paid service with a 10 GB free allocation; additional hosted capacity requires a subscription, separate from self-hosting.

- **Paid (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.

## Roadmap, unclear or unsupported only: zero confirmed-support repositories

### 845. Model selection in CLI — 0/50

`ai.cli_model_selection` · Domain: **ai** · Core: **0** · Product-lineage groups: **0**

Changing models through the CLI is an unchecked roadmap item; current model identifiers are fixed in initialization source.

- **Roadmap (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 846. Conversational Copilot mode — 0/50

`ai.conversational_organization` · Domain: **ai** · Core: **0** · Product-lineage groups: **0**

Roadmap proposes telling AI how to organize and rename files through conversation.

- **Roadmap (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 847. Alternative face model quality tiers — 0/50

`ai.face_quality_tiers` · Domain: **ai** · Core: **0** · Product-lineage groups: **0**

Fast and Accurate face-grouping tiers are explicitly Coming soon; Standard is the available tier.

- **Roadmap (1):** [IacobIonut01/ReFra](<profiles/R33-iacobionut01-refra.md>)
- **Not established by this research:** 49/50.

### 848. Full-video facial scanning — 0/50

`ai.full_video_face_scan` · Domain: **ai** · Core: **0** · Product-lineage groups: **0**

FAQ limits current video face recognition to a generated thumbnail and mentions possible future whole-video scanning.

- **Roadmap (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 849. Sensitive-content detection — 0/50

`ai.sensitive_content_detection` · Domain: **ai** · Core: **0** · Product-lineage groups: **0**

Sensitive-content detection. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Roadmap (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Unclear (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 48/50.

### 850. Custom album photo ordering — 0/50

`albums.manual_order` · Domain: **albums** · Core: **0** · Product-lineage groups: **0**

Custom album photo ordering. Exact behavior, limits, editions and platforms are specified in the per-repository evidence.

- **Roadmap (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Explicitly unsupported (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 48/50.

### 851. Opt-in versus automatic feed strategy — 0/50

`browse.flow_strategy` · Domain: **browse** · Core: **0** · Product-lineage groups: **0**

Edition table explicitly labels custom Flow inclusion strategy Soon and SE rather than an already available core feature.

- **Roadmap (1):** [LycheeOrg/Lychee](<profiles/R18-lycheeorg-lychee.md>)
- **Not established by this research:** 49/50.

### 852. Unreleased Android client source preview — 0/50

`deployment.android_source_preview` · Domain: **deployment** · Core: **0** · Product-lineage groups: **0**

An Android client exists as a development/source preview without an established production package. Such roadmap/preview findings are not counted as released client support.

- **Roadmap (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 853. Taskbar drag-and-drop album edits — 0/50

`deployment.legacy_taskbar_gui` · Domain: **deployment** · Core: **0** · Product-lineage groups: **0**

GUI guide describes dragging Finder photos to create an album that writes EXIF and moves files, but calls the GUI unfinished and uses obsolete build tooling; manifest has no current release.

- **Unclear (1):** [jmathai/elodie](<profiles/R48-jmathai-elodie.md>)
- **Not established by this research:** 49/50.

### 854. New Nuxt web UI — 0/50

`deployment.nuxt_ui` · Domain: **deployment** · Core: **0** · Product-lineage groups: **0**

v0.15.2 notes continued refactoring toward a new Nuxt interface, not a completed shipped replacement.

- **Roadmap (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 855. Standalone desktop executables — 0/50

`deployment.standalone_executables` · Domain: **deployment** · Core: **0** · Product-lineage groups: **0**

macOS/Linux/Windows executables are planned; currently documented installation requires Python, Conda and SDK dependencies.

- **Roadmap (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 856. Image deduplication — 0/50

`duplicates.cleanup` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **0**

README explicitly lists image de-duplication as in progress; existing visual-similarity search is not counted as duplicate cleanup.

- **Roadmap (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 857. Duplicate detection — 0/50

`duplicates.content_detection` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **0**

Checking file duplication remains on the roadmap. Current processed-path and destination-name sets are not duplicate-content detection.

- **Roadmap (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 858. Legacy dupeGuru metadata mirroring — 0/50

`duplicates.external_result_mirroring` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **0**

Tools page describes loading dupeGuru result files and mirroring entry fields before deleting elsewhere, but current roadmap marks Fix Duplicate Files a regression still to restore; not a current built-in scanner.

- **Unclear (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 859. Rich alternate categorization — 0/50

`duplicates.rich_alternate_labels` · Domain: **duplicates** · Core: **0** · Product-lineage groups: **0**

Basic alternate relationships exist, but ordered WIP/recolour labels and richer presentation are explicitly future work; large alternate sets currently scale poorly.

- **Roadmap (1):** [hydrusnetwork/hydrus](<profiles/R30-hydrusnetwork-hydrus.md>)
- **Not established by this research:** 49/50.

### 860. General non-destructive photo edits — 0/50

`editing.nondestructive_photo_editor` · Domain: **editing** · Core: **0** · Product-lineage groups: **0**

README places cropping and colour adjustments in planned/in-progress enhancements, separate from existing lossless metadata and export processing.

- **Roadmap (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 861. Audio, video and ebook understanding — 0/50

`formats.additional_ai_inputs` · Domain: **formats** · Core: **0** · Product-lineage groups: **0**

Semantic support for ebooks, audio and video is listed as future work; extension-only ebook placement is already present in type mode.

- **Roadmap (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 862. Location display deliberately omitted — 0/50

`geo.location_display` · Domain: **geo** · Core: **0** · Product-lineage groups: **0**

The in-app privacy guide explicitly says photos do not show location information because the developer avoids its network requirement.

- **Explicitly unsupported (1):** [mazzzystar/Queryable](<profiles/R35-mazzzystar-queryable.md>)
- **Not established by this research:** 49/50.

### 863. Event-driven automation macros — 0/50

`integration.event_macros` · Domain: **integration** · Core: **0** · Product-lineage groups: **0**

Versioned TOML macros with add/refresh triggers and tag/field actions are planned; implemented Folders to Tags is a narrower tool.

- **Roadmap (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 864. Free-edition external storage roadmap — 0/50

`integration.external_storage` · Domain: **integration** · Core: **0** · Product-lineage groups: **0**

Free README leaves external storage unchecked and free navigation only activates localhost. Pro's advertised support is separately classified.

- **Roadmap (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 865. Automatic API documentation — 0/50

`integration.generated_api_docs` · Domain: **integration** · Core: **0** · Product-lineage groups: **0**

README unchecked roadmap item; manually written V1 API instructions already exist.

- **Roadmap (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 866. Mobile Cast — 0/50

`integration.mobile_cast` · Domain: **integration** · Core: **0** · Product-lineage groups: **0**

Cast manual explicitly reserves Android/iOS support for future development.

- **Roadmap (1):** [immich-app/immich](<profiles/R01-immich-app-immich.md>)
- **Not established by this research:** 49/50.

### 867. Source-preview mobile share target — 0/50

`integration.mobile_share_target` · Domain: **integration** · Core: **0** · Product-lineage groups: **0**

Implemented Android development-build share target accepts images from other apps, not Expo Go; iOS share extension explicitly still being finalized.

- **Roadmap (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 868. Social-network login — 0/50

`integration.social_login` · Domain: **integration** · Core: **0** · Product-lineage groups: **0**

Explicitly removed from this Free fork; inherited social-signup settings must not be counted.

- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 869. Automatic exposure-bracket detection — 0/50

`library.automatic_bracket_stacks` · Domain: **library** · Core: **0** · Product-lineage groups: **0**

Detailed guide explicitly says Bracket is a reserved type not currently created; no bracket detection exists and Create stack always makes Manual, despite broader README wording.

- **Explicitly unsupported (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 870. Bulk content importing — 0/50

`library.bulk_server_import` · Domain: **library** · Core: **0** · Product-lineage groups: **0**

Release README explicitly removes bulk content import, distinct from ordinary parallel browser uploads.

- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 871. Automatic desktop-to-server synchronization — 0/50

`library.desktop_writeback_sync` · Domain: **library** · Core: **0** · Product-lineage groups: **0**

Current workflow requires manually copying/rclone-syncing edits back; automatic return synchronization is explicitly future work.

- **Roadmap (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 872. Interactive Takeout ZIP extraction — 0/50

`library.direct_zip_extraction` · Domain: **library** · Core: **0** · Product-lineage groups: **0**

Current README and commented-out CLI blocks explicitly disable interactive unzipping; users must unzip and merge beforehand despite stale help text suggesting auto-extraction.

- **Explicitly unsupported (1):** [TheLastGimbus/GooglePhotosTakeoutHelper](<profiles/R13-thelastgimbus-googlephotostakeouthelper.md>)
- **Not established by this research:** 49/50.

### 873. Johnny Decimal organization — 0/50

`library.johnny_decimal` · Domain: **library** · Core: **0** · Product-lineage groups: **0**

Implementing established organization schemes such as Johnny Decimal is an unchecked roadmap item.

- **Roadmap (1):** [QiuYannnn/Local-File-Organizer](<profiles/R29-qiuyannnn-local-file-organizer.md>)
- **Not established by this research:** 49/50.

### 874. Manually select preferred edit — 0/50

`library.preferred_version` · Domain: **library** · Core: **0** · Product-lineage groups: **0**

Current grouping chooses the inferred latest edit; manually preferring an older edit is described as upcoming.

- **Roadmap (1):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 49/50.

### 875. Archive arbitrary webpage content — 0/50

`library.webpage_archive` · Domain: **library** · Core: **0** · Product-lineage groups: **0**

README mentions webpages but model/API evidence establishes image URL, referrer and description rather than a full HTML capture/archive pipeline.

- **Unclear (1):** [pinry/pinry](<profiles/R28-pinry-pinry.md>)
- **Not established by this research:** 49/50.

### 876. Source-preview local reminders — 0/50

`maintenance.mobile_memories_notifications` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **0**

Unreleased mobile app schedules on-this-day notifications locally two weeks ahead without push service; they stop if not reopened/synced within two weeks.

- **Roadmap (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 877. Online updating availability — 0/50

`maintenance.online_update` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **0**

README marks online update unfinished, but source navigation exposes a version-upgrade page. Its completeness was not established; not counted as present.

- **Unclear (1):** [helloxz/imgurl](<profiles/R46-helloxz-imgurl.md>)
- **Not established by this research:** 49/50.

### 878. User audit reporting — 0/50

`maintenance.user_audit_reports` · Domain: **maintenance** · Core: **0** · Product-lineage groups: **0**

User IDs are associated with some operations, but the roles manual explicitly says audit reporting will come in a future release.

- **Roadmap (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 879. Composition relationships and overrides — 0/50

`metadata.component_tags` · Domain: **metadata** · Core: **0** · Product-lineage groups: **0**

HAS/component relationships and tag overrides are planned, distinct from implemented parent inheritance.

- **Roadmap (1):** [TagStudioDev/TagStudio](<profiles/R07-tagstudiodev-tagstudio.md>)
- **Not established by this research:** 49/50.

### 880. Scheduled task execution — 0/50

`performance.scheduled_tasks` · Domain: **performance** · Core: **0** · Product-lineage groups: **0**

README lists scheduled task dispatch as an unchecked roadmap item; asynchronous immediate work is separate.

- **Roadmap (1):** [0xDkd/auxpi](<profiles/R38-0xdkd-auxpi.md>)
- **Not established by this research:** 49/50.

### 881. Official source-preview offline editing — 0/50

`privacy.mobile_offline_mirror` · Domain: **privacy** · Core: **0** · Product-lineage groups: **0**

Unreleased mobile app mirrors metadata/grid thumbnails and queues favourite/hide/trash/rating/caption/album edits; full originals still need network unless already on device, and resync rebuilds disposable mirror.

- **Roadmap (1):** [LibrePhotos/librephotos](<profiles/R05-librephotos-librephotos.md>)
- **Not established by this research:** 49/50.

### 882. Automatic tagged-person YAML backup — 0/50

`safety.people_yaml_backup` · Domain: **safety** · Core: **0** · Product-lineage groups: **0**

People manual lists automatic YAML backup of tagged people as upcoming; general metadata sidecars must not be assumed to fully back up face identities.

- **Roadmap (1):** [photoprism/photoprism](<profiles/R02-photoprism-photoprism.md>)
- **Not established by this research:** 49/50.

### 883. Alamy stock-service upload — 0/50

`sharing.alamy_export` · Domain: **sharing** · Core: **0** · Product-lineage groups: **0**

README roadmap names selection/upload to Alamy; not established as available.

- **Roadmap (1):** [Webreaper/Damselfly](<profiles/R45-webreaper-damselfly.md>)
- **Not established by this research:** 49/50.

### 884. Built-in brute-force/rate protection — 0/50

`sharing.builtin_rate_limiting` · Domain: **sharing** · Core: **0** · Product-lineage groups: **0**

Security guide explicitly says built-in rate limiting and brute-force protection are absent and recommends a reverse proxy for them.

- **Explicitly unsupported (1):** [andrii-kryvoviaz/slink](<profiles/R47-andrii-kryvoviaz-slink.md>)
- **Not established by this research:** 49/50.

### 885. Account/library management UI — 0/50

`sharing.management_ui` · Domain: **sharing** · Core: **0** · Product-lineage groups: **0**

User/library guide states management UI is yet to be developed and directs administrators to CLI provisioning.

- **Roadmap (1):** [photonixapp/photonix](<profiles/R44-photonixapp-photonix.md>)
- **Not established by this research:** 49/50.

### 886. Moderation — 0/50

`sharing.moderation` · Domain: **sharing** · Core: **0** · Product-lineage groups: **0**

Explicitly removed from Free; inherited manual sections for upload approval/ModerateContent do not establish available moderation.

- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 887. Likes and followers — 0/50

`sharing.social_graph` · Domain: **sharing** · Core: **0** · Product-lineage groups: **0**

Explicitly removed from this fork.

- **Explicitly unsupported (1):** [rodber/chevereto-free](<profiles/R36-rodber-chevereto-free.md>)
- **Not established by this research:** 49/50.

### 888. Stories availability — 0/50

`sharing.stories` · Domain: **sharing** · Core: **0** · Product-lineage groups: **0**

An off-by-default STORIES_ENABLED flag exists, but built-in Stories help is unfinished; inspected evidence does not establish lifecycle/privacy semantics or current shipped UI.

- **Unclear (1):** [pixelfed/pixelfed](<profiles/R09-pixelfed-pixelfed.md>)
- **Not established by this research:** 49/50.

### 889. Automatic cross-provider failover — 0/50

`storage.automatic_disaster_failover` · Domain: **storage** · Core: **0** · Product-lineage groups: **0**

Reliability document describes manually tested secondary-storage/database recovery and lists fully automatic failover as future work; primary DB active/passive failover is already distinct.

- **Roadmap (1):** [ente/ente](<profiles/R04-ente-ente.md>)
- **Not established by this research:** 49/50.
