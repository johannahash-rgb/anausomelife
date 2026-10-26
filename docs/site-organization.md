# Site organization, 26 October 2026

The public edition has five shared chapters: Journal; Places & days out; Picture cards & tools; Home & finds; Family & support. Every reader page has the same static header, illustrated Explore all menu, breadcrumb, search entry and grouped footer. The complete library and site map include every indexable canonical destination, including generated follow/reviews pages in the published artifact. Redirects and aliases remain available but are not duplicated in the index.

## Editing the organization

- `data/site-structure.json` owns chapter labels, destinations, descriptions and existing illustrated navigation assets.
- `data/journal-taxonomy.json` owns journal membership, multiple formats and multiple topics. Register each new journal story here. Keep the pinned first three stories in the required order; new stories follow them.
- `data/caregiver-taxonomy.json` owns support resources, multiple roles and multiple needs. An empty role list means the resource applies to every role. It does not mean unclassified. Specific roles remain explicit arrays and may overlap when the content supports it.
- `data/library.json` retains authored summaries/art and legacy editorial topic mappings. `data/page-directory.json` is generated from the complete public HTML inventory and is the full library's data source.
- `.github/scripts/collection_browse.py` generates static journal/support cards and topic links on individual articles. `.github/scripts/site_experience.py` owns the common shell, start page, site map, breadcrumbs and contextual contents links.
- `assets/collection-browse.js` progressively enhances the static collections. Search stays visible; native, initially closed “Filter stories/guides” disclosures contain the optional kind/role, sorting and topic controls. Active choices and a clear action stay visible outside the disclosure. Multiple selected topics are intersected; the interface explains that each result matches every selected topic. Kind/role is an independent filter. Queries are shareable and browser Back restores prior filters. All links remain available without JavaScript. Journal cards lead with photography, headline and summary; the repeated category shortcut row and card tag lists are intentionally omitted. Searchable category labels remain in card data.

Do not hand-edit a generated header or collection card. Edit its source configuration or the article itself and regenerate. Keep the original story body, photography, IDs, permissions and disclosures. Do not reintroduce retired AI family portrait art or place the media kit in the top navigation. The open-book Journal miniature has provenance in `journal-navigation-art-2026-10-26.json`.

## Build

After article generators, apply the standing photography/headline maintenance scripts. Generate the shared experience and refresh metadata/index:

```sh
python .github/scripts/site_experience.py --root .
python .github/scripts/enrich_social_meta.py --root .
python tools/build_site_index.py
python tests/test_site_experience.py
```

The GitHub Pages and preview workflows run the experience generator after `prepare_curated_edition.py` and `reader_growth.py`, then enrich social metadata and rebuild search from that finished artifact. Keep this order so generated pages receive the same shell and join the full library. Do not migrate hosting.

## Validation record

The refactor preserved every pre-existing `main` section ID, the journal's pinned order and the current Wayne Newton press entry. Static graph checks cover canonical membership, shared header/footer uniqueness, unique IDs, linked taxonomy, menu destinations, anchors and artwork. Browser checks cover desktop, 390px/320px layouts, search, native menus, multi-topic journal and role/need filtering, and keyboard dismissal/focus return. This is scoped quality assurance, not a claim of a complete accessibility audit.

The original outbound audit attempted 1,174 URLs. Confirmed HEAD 404s were retried with GET; false positives were preserved. Fourteen genuinely expired links were updated to official current program/policy pages. Past event dates remain historical and carry an explanatory note. See `ux-external-link-review-2026-10-26.json`. Network restrictions/rate limiting prevent a guarantee that every external destination is reachable for every reader.

The required publication checks pass. Full legacy unittest discovery also exposes three pre-existing failures, reproduced in the untouched base checkout: an outdated calendar replacement manifest expectation, a Shelburne note expecting the literal word “slopes,” and absent `data/curated-events.json` in refresh-events tests. These were outside the navigation changes and are not represented as passing.

## Homepage continuation, 26 October 2026

The maintained `content/home-entrance.html` now leads with one family photograph and the Menauhant reflection, followed by three practical starting points, three distinct journal photographs, a family introduction and a short community/partnership section. The scoped `assets/homepage.css` retains complete photographic frames and switches the story grid to one column on phones. Secondary homepage search uses a native disclosure and a standard GET form to the library; the shared header search stays available.

`.github/scripts/build_homepage.py` installs that fragment into `index.html`, attaches exactly one scoped stylesheet, and removes the retired dynamic homepage replacement script. The public-edition preparation calls it before the other page transforms, so subsequent builds preserve this entrance. All previous fragment IDs are retained, including legacy press bookmarks. The journal's pinned stories and the shared navigation remain unchanged.

Validation: required publication checks passed; full-frame images loaded in the desktop preview; 390px and 320px framed browser checks showed no horizontal page overflow; mobile homepage search for Maine reached the filtered library. Internal link/asset, publication metadata, and repeat-build checks also passed. This does not represent a complete accessibility audit.
