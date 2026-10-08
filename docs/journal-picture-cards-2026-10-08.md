# Journal sketches and picture cards

Requested scope: every existing blog receives relevant picture communication cards and a lovely subject-appropriate sketch, with its cards available in the existing collection. The work preserves the GitHub Pages host and original photographs.

## Coverage

53 narrative/related place-article URLs receive an explicit four-card selection. This includes all 15 current journal posts, the family notebook, the illustrated Little Adventures story, and 36 place-article URLs (including maintained legacy aliases). See data/journal-picture-cards.json for the exact selection. Existing suitable sketches remain. Thirteen narrative pages receive new or reused subject-specific sketches.

## Artwork provenance

Nine original editorial sketches in assets/journal-sketches/ were commissioned with OpenAI image generation for this update: tulips, orchard, table-flowers, roses-fidget, snowshoes, lake, easter, groceries-flowers, pumpkin-corn. No family photographs or third-party images were provided to generate them; they are conceptual subject studies. They were visually reviewed as complete original images. These are not venue photographs, route diagrams or factual representations of entrances/facilities. Public captions say Original editorial illustration. The lake caption explicitly distinguishes the generic Maine-inspired landscape from a map of the visit.

The dedicated assets/card-collection/tulip-farm.png is a separate original commissioned generic communication illustration, visually reviewed, depicting tulip rows and a farm barn. It was created as a picture-communication subject, not extracted from a story, family photograph or decorative venue artwork. The existing tulip card is retained. Catalog IDs are unique; total is 279.

Reused approved editorial work: assets/rancatores-scaffold/rancatores-cup-cone-v1.webp on the ice-cream-choice story and Small Outings; assets/ellis-coastal/wells-wave-study.webp on Energy. Both were inspected visually before reuse. Existing coffee, Margaritas and Fiber Connect sketches are preserved. Existing provenance for these assets continues to apply.

The owner commissioned the new original artwork for the public website, individual card downloads and printable sets. No external proprietary AAC/PECS symbols, third-party photos, logos or character art were copied. This records intended use, not a claim of exclusivity, complete legal clearance, clinical validation or official PECS affiliation.

## Functionality and preservation

Curated card previews are static HTML; labels and library links work without scripts. PNG export uses the explicit catalog subject, never an article hero. Edit/print links pass approved catalog IDs to the existing local-only collection. Incoming IDs are allowlisted against the catalog; unknown/duplicate IDs are ignored. No upload, external generation endpoint, credentials or persistent visitor storage is added.

Existing 278-card downloadable PDF/ZIP archives remain at their original URLs and are explicitly labeled original starter packs. New additions can be downloaded individually or included in the current browser print set. Category PDFs are labeled original category PDFs rather than claiming to contain future additions.

The six-story content source and generator include the same cards/sketches as current HTML. A dedicated manifest and validation script guard coverage and asset references. Legacy retired automatic-photo card code stays retired. Original family photo references and bytes remain unchanged.

## Verification

Run tools/check_journal_picture_cards.py, tools/check_editorial_rights.py, Node syntax checks, and the existing public-site audit before deployment. These source/reference checks are not a full accessibility audit or substitute for interactive browser testing. The executor available for this change has no shell/browser; GitHub Pages CI performs the scripted checks, and public-page extraction verifies the deployed HTML/assets. Record the actual results in the task report.
