# Methodology and limitations

## Agreed scope

Photo/video collection managers, end-user galleries, photo-library organization utilities, and duplicate-file cleanup tools. Desktop, web/server, CLI and mobile are eligible. Legacy repositories are included and labelled. General-purpose editors, single-image viewers without substantive collection organization, SDKs/components, AI generators, backup/download-only tools, generic CMS/file hosting, and release-only binary repositories are excluded.

The user chose management/cleanup rather than the broader editor/transcoder workflow, allowed legacy repositories, and authorized parallel individual research. No private application code, photo library or diagnostic data was used as input to public searches.

## Discovery and ranking

Discovery pool: **1,559** unique repository names. Explicitly eligible candidates: **71**. Final panel: **50**, ranked by live GitHub `stargazerCount`.

GitHub searches used stars-descending ordering. Eligible candidates were subsequently queried directly for live stars, default-branch commit, license metadata, archive/fork status and latest GitHub release. The resulting snapshot is frozen in `research-data.json`; later star changes do not silently change the panel.

| Search query | Result cap |
|---|---:|
| `photo in:name,description` | 100 |
| `gallery in:name,description` | 100 |
| `duplicate in:name,description` | 100 |
| `media management in:description` | 100 |
| `image organizer in:description` | 60 |
| `deduplication in:name,description` | 100 |
| `topic:photo-gallery` | 100 |
| `topic:photo-management` | 100 |
| `photo manager in:description` | 100 |
| `duplicate finder in:description` | 100 |
| `photo library in:description` | 100 |
| `image browser in:description` | 100 |
| `topic:photo-organizer` | 100 |
| `photo management in:description` | 100 |
| `image management in:description` | 100 |
| `image hosting in:description` | 100 |
| `相册 in:name,description` | 80 |
| `图床 in:name,description` | 60 |

- Explicit checks for known photo-library and cleanup projects whose names/descriptions did not match keyword searches.
- meichthys/foss_photo_libraries used only to discover candidate names; its comparison cells were not used as feature evidence.
- Live GitHub GraphQL metadata for every explicitly eligible candidate before selecting the highest-starred 50.

### Discovery limits

- Search results are capped and depend on names, descriptions, topics and indexing; this is not an exhaustive GitHub census.
- Eligibility requires editorial judgement. The report states the exact scope and publishes selected/eligible-below-cutoff/excluded candidate records.
- Unselected discovery candidates were descriptively screened, not subjected to the individual deep feature analysis required of all selected repositories.
- Stars of monorepositories and archived/fork-lineage repositories are not directly comparable measures of current product adoption.

## Individual analysis

Every selected repository was assigned an individual profile. Researchers inspected primary readmes, manuals/feature documentation, releases and relevant source files. Large projects received deeper feature-specific inspection; thin documentation is called out rather than filled with assumptions. Profiles identify source sections, constraints and edition/runtime dependencies.

The final profiles contain **617 source records**, referencing **617 distinct URLs**. A record means an inspected source in a repository-specific context, not a separately installed application or an independent empirical benchmark.

## Normalization and counting

A shared vocabulary established precise meanings before research. Additional feature IDs were preserved and reviewed for aliases; meaningful implementation differences were not merged merely because their names were similar.

- Repository support = at least one core, optional, plugin or paid finding for that feature.
- A repository is counted once per feature, even if it has several implementations or editions.
- Status-specific counts can overlap when multiple variants are documented; do not sum them to obtain total support.
- Roadmap, unclear and explicit unsupported findings remain visible, but do not count as support.
- Blank matrix cells mean no finding was established. They are not verified negative answers.
- Support counts are evidence-backed lower bounds, not measurements of actual market-wide prevalence. Routine features can be underdocumented; narrowly specified advanced variants naturally look rarer.
- Family counts collapse labelled legacy/current lineages as a sensitivity check, not as proof of independent implementation.
- Frequencies are descriptive. Server/community features can be common yet irrelevant to Memoria; rare safety features can be essential.
- CSV text that could be interpreted as a spreadsheet formula is prefixed with an apostrophe; the unmodified evidence remains in the JSON.

### Semantic boundaries

Byte/hash duplicates versus perceptual similarity; detection versus recognition of faces; local inference versus remote AI; self-hosting versus E2EE; OS trash versus app recovery versus durable operation journaling; any-file hashing versus actual media decoding/playback; metadata display versus embedded/sidecar write-back; live filesystem roots versus disconnected-volume browsing were kept separate.

## Validation

The builder rejects missing repositories, duplicate identities/feature IDs, unresolved source references, invalid status codes and unresolved supported/unsupported conflicts. It refuses to publish partial coverage or unreviewed new definitions. Synthetic self-tests verify per-repository deduplication, roadmap exclusion, lineage counts, missing-evidence rejection and alias-cycle detection. Final CSV dimensions, counts and profile/source links are checked separately.

## What was not done

No large repository clones, application installations, real-library benchmarks, vulnerability audits or license-compliance audits were performed. Documentation can be wrong or ahead of releases; confidence describes evidence clarity, not guaranteed runtime correctness. No claim is made to enumerate every internal code path, every third-party plugin or every capability hidden in undocumented branches.

## Eligible projects below the cutoff

These were not substituted into the panel based on subjective preference; they may still be valuable.

| Repository | Stars at snapshot | Category |
|---|---:|---|
| [photo/frontend](<https://github.com/photo/frontend>) | 1,378 | library-server |
| [zanllp/infinite-image-browsing](<https://github.com/zanllp/infinite-image-browsing>) | 1,369 | library-server |
| [pauldreik/rdfind](<https://github.com/pauldreik/rdfind>) | 1,321 | cleanup |
| [besscroft/PicImpact](<https://github.com/besscroft/PicImpact>) | 1,320 | gallery-sharing |
| [xemle/home-gallery](<https://github.com/xemle/home-gallery>) | 1,213 | library-server |
| [xob0t/Google-Photos-Toolkit](<https://github.com/xob0t/Google-Photos-Toolkit>) | 1,183 | library-utility |
| [fregie/pho](<https://github.com/fregie/pho>) | 1,175 | gallery-sharing |
| [tropy/tropy](<https://github.com/tropy/tropy>) | 1,169 | library-desktop |
| [RupertAvery/DiffusionToolkit](<https://github.com/RupertAvery/DiffusionToolkit>) | 1,022 | library-desktop |
| [chevereto/chevereto](<https://github.com/chevereto/chevereto>) | 1,014 | gallery-sharing |
| [saimn/sigal](<https://github.com/saimn/sigal>) | 949 | gallery-generator |
| [allusion-app/Allusion](<https://github.com/allusion-app/Allusion>) | 909 | library-desktop |
| [thumbsup/thumbsup](<https://github.com/thumbsup/thumbsup>) | 864 | gallery-generator |
| [KDE/digikam](<https://github.com/KDE/digikam>) | 808 | library-desktop |
| [gcui-art/album-ai](<https://github.com/gcui-art/album-ai>) | 793 | library-server |
| [Bitpainter75/FerrumPix](<https://github.com/Bitpainter75/FerrumPix>) | 750 | library-desktop |
| [nextcloud/photos](<https://github.com/nextcloud/photos>) | 725 | library-server |
| [RazgrizHsu/immich-deduper](<https://github.com/RazgrizHsu/immich-deduper>) | 686 | cleanup |
| [SmilyOrg/photofield](<https://github.com/SmilyOrg/photofield>) | 617 | library-server |
| [foldergram/foldergram](<https://github.com/foldergram/foldergram>) | 604 | library-server |
| [snapcrescent/snapcrescent](<https://github.com/snapcrescent/snapcrescent>) | 33 | library-server |

Low GitHub stars are especially misleading for projects primarily hosted elsewhere, including archived mirrors.
