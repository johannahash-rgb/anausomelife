# Reader pathways

The caregiver entry point remains `/family-roles.html`, now titled “Family & caregiver support.” It starts with practical tasks and original family stories, followed by the individual role guides. Existing section IDs are retained.

`.github/scripts/prepare_curated_edition.py` runs `reader_pathways.py` on the publication artifact. The latter adds static breadcrumbs where missing, relevant story/tool cards where a useful next-read section is missing, and consistent links back to the appropriate collection, journal, caregiver hub and search. The existing hand-picked related sections remain intact. The generic “More practical guides” blocks and the role guides’ repetitive recommendations are replaced. Fragment IDs inside replaced navigation remain as anchors. The homepage, redirects, noindex documents and print downloads are excluded; policy pages receive only a breadcrumb.

Card selections and page groups live in `reader_pathways.py`. Add genuine, published stories and existing authorized photographs there; do not infer a visit or substitute generated family imagery. New cards must resolve to real pages and images. Shared `immersion.js` respects the static navigation, and sharing controls appear before onward reading.

The search builder excludes utility/source documents, separates words around line breaks, and keeps one result for identical page text, preferring library addresses. Publication also inserts real whitespace after heading breaks, preserving readable headings when responsive CSS hides the break. Journal pins remain unchanged.

Validation: `python tests/test_reader_pathways.py`, `python tests/test_access_publication.py`, `node tests/test_editorial_sharing.cjs`, then the normal rights, social metadata and strict publication audits. These checks cover routes and preserved controls/anchors, not rendered iPhone/Safari layout.
