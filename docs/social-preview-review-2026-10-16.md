# Editorial social-preview review — 16 October 2026

## Result

- Baseline: main `3ee9a8dfd6266eaee8b50e28a3c68ccdcb9e5a41`; latest pre-change audit run [38835972886](https://github.com/johannahash-rgb/anausomelife/actions/runs/38835972886).
- Integrated concurrent main commit `85a7823abf36e8af764a069f3f171e2ce0535734` (journal headline spacing and mobile story layout) before publication; its page body and new stylesheet are preserved.
- Source audit: **119 → 17 missing-social-image findings**, a reduction of 102 (85.7%), across the same 191 HTML pages. No other source-audit issues were found.
- **144 pages** now have reviewed static metadata: 102 previously missing images and 42 existing previews completed or improved, using **71 distinct existing images**.
- The journal, library, travel and New England sections, product/household guides, coffee review, all ten topic pages, brand contact/press pages, and the canonical media landing page are covered. Existing media subpages are redirects to the canonical media room and are intentionally not given competing previews.
- 110 large-image cards and 34 summary cards. Compact cards are used for portrait/square originals; actual file dimensions are recorded instead of inventing 1200×630 dimensions. Platforms control their own final crop and layout.
- Original photo/illustration bytes and all article bodies are unchanged. There are no new AI images, third-party photo downloads, synthetic family stand-ins, or generic fallback assignments.

## Important baseline distinction

The original repository audit examined source HTML. Deployment already ran a heuristic enrichment script: the live journal had an orchard photograph even though its repository file lacked `og:image`. A reproduced baseline publish pass filled 121 pages, including 26 fallback assignments, and reported zero missing-social-image findings; it used page-order scoring and a shared AI-created coastal fallback. Consequently, the 119 findings were not evidence of 119 blank live previews.

This change makes selections explicit in both source and deployment. It removes automatic fallback filling. The 17 pending pages therefore remain intentionally without an image on the published artifact as well; the old publication-only presence count was artificially satisfied by guessed imagery. Do not present 119 → 17 as a before/after count of blank previews on social platforms.

## Image decisions

- Journal: the real Dairy Joy picnic-table family photograph; library: real Book Barn browsing; travel: the real Rangeley waterfront; New England: the lakeside family-and-dog photograph.
- Product and practical guides keep their subject-specific objects and illustrations. The coffee review uses its own coffee-and-keys study, explicitly described as illustration rather than an exact branded product photograph.
- Florida travel now uses the original evening-flight photograph. My Small World replaces the site emblem with its own shop illustration. Generic farm/coast images on Great Brook Farm and Marginal Way are replaced with their existing subject studies.
- Existing story-specific family photos retain their identity. The Wicked Tulips preview uses the existing smaller full-frame portrait rather than the 5248-pixel file, keeping it inside the configured platform bounds.
- Related section indexes, route aliases and practical guides can intentionally share a relevant image; unrelated stories never receive a single site-wide fallback. The registry records each page explicitly.
- Existing illustration provenance and original-photo permissions are linked in the selection registry. This is editorial link-preview reuse on the owner’s site, not a blanket grant for brand downloads, advertising or republication. Original illustration labels are retained in alternative text; illustrations do not establish a venue’s actual appearance or access.

## Validation

- All 71 distinct live HTTPS image URLs returned HTTP 200 with the expected content type, dimensions and exact SHA-256 bytes.
- Every selected image was visually inspected; every selected file fully decodes and stays under 5 MB and 4096 pixels per side. No SVG, logo fallback, broken asset or unreviewed external host is selected.
- Metadata checks verify one value per property, absolute HTTPS image/canonical URLs, matching Open Graph and Twitter images and alternative descriptions, correct MIME type/dimensions, sensible card type, and bounded Twitter title/description lengths.
- Six new regression tests pass: duplicate/empty tags and escaping, redirect/noindex protection, invalid assets/dimensions/MIME/hash, truncated-image decoding, no unknown-page fallback, and all reviewed source pages plus idempotence.
- Existing calendar filter, editorial sharing, accessibility publication and journal-picture-card checks pass. Calendar artwork mappings remain fixed.
- A complete local publish simulation ran the existing milk-photo/card build, editorial-rights reference check, search refresh, public-file exclusions, curated-edition preparation, reviewed metadata application and strict site audit. The final artifact has 17 missing-social-image warnings and no broken-path or other audit findings.
- The editorial-rights script is a reference/retired-media check, not comprehensive license clearance. Its source-tree missing milk-image warnings disappear after the existing deployment-generated images are built.
- The two retained milk-story previews decode correctly at 1200×630 in the generated artifact. Their existing template remains separate from the reviewed-original registry.
- No platform-specific Facebook/X/LinkedIn composer was tested or cache-purged. Metadata correctness and HTTP reachability do not guarantee immediate refresh of previously cached cards.

## Maintenance

After changing or regenerating an editorial page, run:

```sh
python .github/scripts/enrich_social_meta.py --root .
python .github/scripts/enrich_social_meta.py --root . --check
python -m unittest discover -s tests -p 'test_social_metadata.py'
python .github/scripts/site_audit.py --root . --external-limit 0 --strict
```

Add new selections to `docs/social-preview-selections.json` after reviewing the image, its permission basis and its relation to the page. Update the recorded hash/dimensions only after reviewing changed image bytes. Never replace an image merely to make the missing-image count zero. CI enforces the reviewed selections; the general audit continues to list unselected gaps. Internal selection/provenance records stay out of the GitHub Pages artifact.

## Still pending: 17 source image gaps

- `accessibility.html`
- `calendar.html`
- `communication-card-generator.html`
- `communication-notes.html`
- `disclosure.html`
- `family-agreements.html`
- `family-planning-toolkit.html`
- `family-roles.html`
- `kid-fun.html`
- `language.html`
- `links.html`
- `little-adventures.html`
- `paternal-football-card.html`
- `picture-card-library.html`
- `privacy.html`
- `resources.html`
- `visit-story.html`

These utility, planning and specialist-tool pages need an appropriate deliberately chosen cover. They were not filled with the old generic coastal fallback.

## Existing asset issues and retained generated cards

- `favorite-places-wilson-farm.html` — Existing hero JPEG fails full image decoding; alternative JPEG detail assets also fail. Retain existing article but obtain a clean original for a dependable preview.
- `a-love-letter-to-buying-nothing.html` — Existing .jpg is a two-frame MPO with EXIF rotation. Existing preview retained pending a standard JPEG export that preserves the photographed artwork and orientation.
- `new-england-sharing-directory.html` — Uses the same rotated MPO photograph as the Buy Nothing story; standard JPEG export still needed.
- `little-things-that-help.html` — Existing 1200×630 photo card is built during deployment; retained and separately validated in the publishable artifact.
- `the-little-fixes.html` — Uses the same existing deployment-built 1200×630 photo card; retained and separately validated in the publishable artifact.

## Exact page-to-image selections

All URLs use `https://anausomelife.com`. Image dimensions below are the original encoded file dimensions. Full descriptions, hashes and provenance references are in the JSON registry.

| Page | Selected image | Dimensions | Card |
| --- | --- | --- | --- |
| `aac-outing-note.html` | `/assets/destination-guides/communication-outing-note-20261004.webp` | 1536×1024 | summary_large_image |
| `about.html` | `/assets/family-outings/wells-beach-family.webp` | 1350×1800 | summary |
| `ai-ice-cream-choice-board-rancatores-lexington.html` | `/assets/rancs-ai-choice-board/family-photo.jpg` | 635×820 | summary |
| `apple-orchard-afternoon.html` | `/assets/family-notes/doe-orchards-family.webp` | 675×900 | summary |
| `at-home.html` | `/assets/long-guide-studies/wet-weather-entryway.webp` | 1536×1024 | summary_large_image |
| `autumn-simple-joys-james-ruby.html` | `/assets/family-notes/james-ruby-autumn.jpeg` | 1152×1536 | summary |
| `berlin-farms-easter-field-note.html` | `/assets/berlin-farms-easter/white-fences.jpeg` | 1536×1152 | summary_large_image |
| `blog.html` | `/assets/dairy-joy-october/grandpa-steve-james-ruby.jpeg` | 1536×1152 | summary_large_image |
| `caregiver-handover-guide.html` | `/assets/catalog-advice.webp` | 640×640 | summary |
| `carolines-cart-new-england.html` | `/assets/family-notes/wegmans-carolines-cart.webp` | 709×975 | summary |
| `contact.html` | `/assets/family-outings/fort-mcclary-waterfront.webp` | 1800×1350 | summary_large_image |
| `coparent-role.html` | `/assets/long-guide-studies/household-instruction-cards.webp` | 1536×1024 | summary_large_image |
| `eight-oclock-colombian-peaks-field-note.html` | `/assets/ellis-misc/coffee-before-keys-v1.webp` | 1536×1024 | summary_large_image |
| `energy-is-an-access-resource.html` | `/assets/family-outings/wells-beach-family.webp` | 1350×1800 | summary |
| `extended-family-role.html` | `/assets/long-guide-studies/an-invitation-with-useful-details.webp` | 1536×1024 | summary_large_image |
| `family-command-center-guide.html` | `/assets/long-guide-studies/organize-school-paperwork.webp` | 1536×1024 | summary_large_image |
| `family-notebook.html` | `/assets/orchard-afternoon-clean.jpg` | 800×620 | summary |
| `family-wardrobe.html` | `/assets/catalog-style.webp` | 640×640 | summary |
| `favorite-places-book-barn-niantic.html` | `/assets/book-barn-ct-clean.jpg` | 800×584 | summary_large_image |
| `favorite-places-codman-community-farms.html` | `/assets/ellis-place-guides/codman-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places-decordova.html` | `/assets/ellis-place-guides/decordova-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places-drumlin-farm.html` | `/assets/ellis-place-guides/drumlin-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places-gilsland-farm.html` | `/assets/ellis-place-guides/gilsland-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places-lifetime-burlington.html` | `/assets/venue-illustrations/indoor-pool-illustration.webp` | 1200×800 | summary_large_image |
| `favorite-places-misty-harbor-wells.html` | `/assets/family-outings/wells-beach-family.webp` | 1350×1800 | summary |
| `favorite-places-pineland-farms.html` | `/assets/ellis-place-guides/pineland-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places-quiero-cafe-portland.html` | `/assets/ellis-place-guides/kittery-picnic-study.webp` | 1448×1086 | summary_large_image |
| `favorite-places-rancatores-lexington.html` | `/assets/venue-illustrations/rancatores-lexington-original-study-v2.webp` | 1200×800 | summary_large_image |
| `favorite-places-rococo-kennebunk.html` | `/assets/rancatores-scaffold/rancatores-cup-cone-v1.webp` | 1448×1086 | summary_large_image |
| `favorite-places-scarborough-state-beach.html` | `/assets/ellis-coastal/wells-wave-study.webp` | 1448×1086 | summary_large_image |
| `favorite-places-shermans-freeport.html` | `/assets/long-guide-studies/library-pass-day-trip.webp` | 1536×1024 | summary_large_image |
| `favorite-places-watch-hill-napatree.html` | `/assets/ellis-coastal/wells-wave-study.webp` | 1448×1086 | summary_large_image |
| `favorite-places-wells-beach.html` | `/assets/family-outings/wells-beach-family.webp` | 1350×1800 | summary |
| `favorite-places-wolfes-neck.html` | `/assets/ellis-place-guides/wolfes-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places-york-nubble.html` | `/assets/york-maine-clean.jpg` | 800×584 | summary_large_image |
| `favorite-places.html` | `/assets/venue-illustrations/frog-pond-carousel-illustration.webp` | 1200×800 | summary_large_image |
| `favorite-places/book-barn-niantic.html` | `/assets/book-barn-ct-clean.jpg` | 800×584 | summary_large_image |
| `favorite-places/boston-common-frog-pond.html` | `/assets/venue-illustrations/frog-pond-carousel-illustration.webp` | 1200×800 | summary_large_image |
| `favorite-places/codman-community-farms.html` | `/assets/ellis-place-guides/codman-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places/decordova-sculpture-park.html` | `/assets/ellis-place-guides/decordova-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places/drumlin-farm.html` | `/assets/ellis-place-guides/drumlin-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places/gilsland-farm.html` | `/assets/ellis-place-guides/gilsland-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places/great-brook-farm.html` | `/assets/ellis-place-guides/wolfes-cover.webp` | 1536×1024 | summary_large_image |
| `favorite-places/kittery-food-mart-fort-mcclary.html` | `/assets/family-outings/fort-mcclary-waterfront.webp` | 1800×1350 | summary_large_image |
| `favorite-places/lacascias-burlington.html` | `/assets/destination-illustrations/bakery-deli-still-life-20261004.webp` | 1536×1024 | summary_large_image |
| `favorite-places/llbean-freeport.html` | `/assets/family-outings/llbean-freeport-games.webp` | 1350×1800 | summary |
| `favorite-places/marginal-way-ogunquit.html` | `/assets/ellis-coastal/wells-wave-study.webp` | 1448×1086 | summary_large_image |
| `favorite-places/minute-man-battle-road.html` | `/assets/ellis-place-guides/decordova-light.webp` | 1448×1086 | summary_large_image |
| `favorite-places/misty-harbor-resort.html` | `/assets/family-outings/wells-beach-family.webp` | 1350×1800 | summary |
| `favorite-places/new-england-aquarium.html` | `/assets/destination-illustrations/aquarium-sea-life-editorial-20261004.webp` | 1536×1024 | summary_large_image |
| `favorite-places/nubble-lighthouse.html` | `/assets/york-maine-clean.jpg` | 800×584 | summary_large_image |
| `favorite-places/walden-pond.html` | `/assets/ellis-place-guides/drumlin-pond.webp` | 1448×1086 | summary_large_image |
| `favorite-places/wegmans-burlington.html` | `/assets/family-notes/wegmans-carolines-cart.webp` | 709×975 | summary |
| `favorite-places/wildwood-park-burlington.html` | `/assets/ellis-place-guides/decordova-light.webp` | 1448×1086 | summary_large_image |
| `fiber-connect-disney-field-note.html` | `/assets/fiber-connect-disney/evening-flight.jpeg` | 1536×1152 | summary_large_image |
| `field-notes.html` | `/assets/long-guide-studies/offline-outing-folder.webp` | 1536×1024 | summary_large_image |
| `flowers-fidgets-and-clutter.html` | `/assets/family-notes/flowers-fidgets-clutter.webp` | 1152×1536 | summary |
| `food-away-from-home-guide.html` | `/assets/family-outings/lexington-ice-cream-family.webp` | 1350×1800 | summary |
| `fort-taber-snowshoes-field-note.html` | `/assets/family-notes/fort-taber-snowshoe-family.webp` | 864×866 | summary |
| `frerichs-farm-halloween-field-note.html` | `/assets/frerichs-farm-halloween/skeleton-glasses.webp` | 960×1280 | summary |
| `gifts-worth-giving.html` | `/assets/gift-kit-illustration.webp` | 1536×1024 | summary_large_image |
| `grandparent-role.html` | `/assets/long-guide-studies/a-photo-box-with-a-story.webp` | 1536×1024 | summary_large_image |
| `guides/a-better-hair-appointment.html` | `/assets/long-guide-studies/a-better-hair-appointment.webp` | 1536×1024 | summary_large_image |
| `guides/a-photo-box-with-a-story.html` | `/assets/long-guide-studies/a-photo-box-with-a-story.webp` | 1536×1024 | summary_large_image |
| `guides/an-invitation-with-useful-details.html` | `/assets/long-guide-studies/an-invitation-with-useful-details.webp` | 1536×1024 | summary_large_image |
| `guides/ask-for-meeting-access.html` | `/assets/long-guide-studies/ask-for-meeting-access.webp` | 1536×1024 | summary_large_image |
| `guides/choose-a-special-education-advocate.html` | `/assets/long-guide-studies/choose-a-special-education-advocate.webp` | 1536×1024 | summary_large_image |
| `guides/easter-at-ocean-house.html` | `/assets/long-guide-studies/easter-at-ocean-house.webp` | 1536×1024 | summary_large_image |
| `guides/gifts-without-a-performance.html` | `/assets/long-guide-studies/gifts-without-a-performance.webp` | 1536×1024 | summary_large_image |
| `guides/holiday-meal-two-timetables.html` | `/assets/long-guide-studies/holiday-meal-two-timetables.webp` | 1536×1024 | summary_large_image |
| `guides/household-instruction-cards.html` | `/assets/long-guide-studies/household-instruction-cards.webp` | 1536×1024 | summary_large_image |
| `guides/iep-meeting-follow-up.html` | `/assets/long-guide-studies/iep-meeting-follow-up.webp` | 1536×1024 | summary_large_image |
| `guides/keep-the-student-in-the-conversation.html` | `/assets/long-guide-studies/keep-the-student-in-the-conversation.webp` | 1536×1024 | summary_large_image |
| `guides/library-pass-day-trip.html` | `/assets/long-guide-studies/library-pass-day-trip.webp` | 1536×1024 | summary_large_image |
| `guides/offline-outing-folder.html` | `/assets/long-guide-studies/offline-outing-folder.webp` | 1536×1024 | summary_large_image |
| `guides/one-page-parent-agenda.html` | `/assets/long-guide-studies/iep-meeting-follow-up.webp` | 1536×1024 | summary_large_image |
| `guides/one-week-tech-trial.html` | `/assets/long-guide-studies/one-week-tech-trial.webp` | 1536×1024 | summary_large_image |
| `guides/organize-school-paperwork.html` | `/assets/long-guide-studies/organize-school-paperwork.webp` | 1536×1024 | summary_large_image |
| `guides/prepare-for-an-iep-meeting.html` | `/assets/long-guide-studies/organize-school-paperwork.webp` | 1536×1024 | summary_large_image |
| `guides/reading-a-trail-access-sign.html` | `/assets/long-guide-studies/reading-a-trail-access-sign.webp` | 1536×1024 | summary_large_image |
| `guides/scan-it-on-your-phone.html` | `/assets/long-guide-studies/scan-it-on-your-phone.webp` | 1536×1024 | summary_large_image |
| `guides/school-emails-clear-requests.html` | `/assets/long-guide-studies/iep-meeting-follow-up.webp` | 1536×1024 | summary_large_image |
| `guides/small-weekend-beauty-bag.html` | `/assets/long-guide-studies/small-weekend-beauty-bag.webp` | 1536×1024 | summary_large_image |
| `guides/the-access-call-before-you-go.html` | `/assets/long-guide-studies/ask-for-meeting-access.webp` | 1536×1024 | summary_large_image |
| `guides/the-grocery-list-handoff.html` | `/assets/long-guide-studies/the-grocery-list-handoff.webp` | 1536×1024 | summary_large_image |
| `guides/the-pedicure-menu.html` | `/assets/long-guide-studies/small-weekend-beauty-bag.webp` | 1536×1024 | summary_large_image |
| `guides/virtual-iep-meeting-opening.html` | `/assets/long-guide-studies/ask-for-meeting-access.webp` | 1536×1024 | summary_large_image |
| `guides/wet-weather-entryway.html` | `/assets/long-guide-studies/wet-weather-entryway.webp` | 1536×1024 | summary_large_image |
| `guides/when-the-family-plan-is-too-much.html` | `/assets/long-guide-studies/an-invitation-with-useful-details.webp` | 1536×1024 | summary_large_image |
| `guides/working-with-an-advocate.html` | `/assets/long-guide-studies/choose-a-special-education-advocate.webp` | 1536×1024 | summary_large_image |
| `hotel-pool-checklist.html` | `/assets/destination-guides/hotel-pool-planning-20261004.webp` | 1536×1024 | summary_large_image |
| `household-reset.html` | `/assets/long-guide-studies/household-instruction-cards.webp` | 1536×1024 | summary_large_image |
| `how-we-choose.html` | `/assets/long-guide-studies/one-week-tech-trial.webp` | 1536×1024 | summary_large_image |
| `index.html` | `/assets/rangeley-grandparents/autumn-waterfront.jpeg` | 1536×1152 | summary_large_image |
| `last-minute-gift-kit.html` | `/assets/gift-kit-illustration.webp` | 1536×1024 | summary_large_image |
| `last-minute-guests-pantry-kit.html` | `/assets/catalog-hosting.webp` | 640×640 | summary |
| `library.html` | `/assets/book-barn-ct-clean.jpg` | 800×584 | summary_large_image |
| `little-black-book.html` | `/assets/main-street/outfitter-interior.webp` | 1536×1024 | summary_large_image |
| `margaritas-waltham-field-note.html` | `/assets/margaritas-waltham/jukebox-watercolor-v1.png` | 1536×1024 | summary_large_image |
| `maternal-role.html` | `/assets/long-guide-studies/holiday-meal-two-timetables.webp` | 1536×1024 | summary_large_image |
| `media/index.html` | `/assets/family-outings/fort-mcclary-waterfront.webp` | 1800×1350 | summary_large_image |
| `media/launch.html` | `/assets/family-outings/fort-mcclary-waterfront.webp` | 1800×1350 | summary_large_image |
| `multimodal-communication.html` | `/assets/destination-guides/communication-outing-note-20261004.webp` | 1536×1024 | summary_large_image |
| `my-small-world-autism-friendly-welcome.html` | `/assets/my-small-world/welcome-shop.webp` | 1536×1024 | summary_large_image |
| `new-england-weekends.html` | `/assets/york-maine-clean.jpg` | 800×584 | summary_large_image |
| `new-england.html` | `/assets/rangeley-grandparents/lakeside-pause.jpeg` | 1536×1152 | summary_large_image |
| `october-ice-cream-dairy-joy-weston.html` | `/assets/dairy-joy-october/grandpa-steve-james-ruby.jpeg` | 1536×1152 | summary_large_image |
| `older-teen-edit.html` | `/assets/long-guide-studies/keep-the-student-in-the-conversation.webp` | 1536×1024 | summary_large_image |
| `older-teen-swim-guide.html` | `/assets/venue-illustrations/indoor-pool-illustration.webp` | 1200×800 | summary_large_image |
| `outings.html` | `/assets/orchard-afternoon-clean.jpg` | 800×620 | summary |
| `paternal-role.html` | `/assets/long-guide-studies/library-pass-day-trip.webp` | 1536×1024 | summary_large_image |
| `photo-day-prep.html` | `/assets/catalog-style.webp` | 640×640 | summary |
| `photo-gifts-from-your-camera-roll.html` | `/assets/gift-kit-illustration.webp` | 1536×1024 | summary_large_image |
| `pool-weekend-kit.html` | `/assets/destination-guides/pool-bag-ready-20261004.webp` | 1536×1024 | summary_large_image |
| `press.html` | `/assets/family-outings/fort-mcclary-waterfront.webp` | 1800×1350 | summary_large_image |
| `product-guides.html` | `/assets/long-guide-studies/one-week-tech-trial.webp` | 1536×1024 | summary_large_image |
| `profoundly-awesome.html` | `/assets/catalog-family.webp` | 640×640 | summary |
| `quiet-break-plan.html` | `/assets/catalog-quiet-kit.webp` | 640×640 | summary |
| `rainy-day-outing-plan.html` | `/assets/book-barn-ct-clean.jpg` | 800×584 | summary_large_image |
| `rangeley-grandparents-field-note.html` | `/assets/rangeley-grandparents/autumn-waterfront.jpeg` | 1536×1152 | summary_large_image |
| `respite-partner-role.html` | `/assets/destination-guides/communication-outing-note-20261004.webp` | 1536×1024 | summary_large_image |
| `sensory-clothing-checklist.html` | `/assets/catalog-style.webp` | 640×640 | summary |
| `series.html` | `/assets/long-guide-studies/library-pass-day-trip.webp` | 1536×1024 | summary_large_image |
| `shorter-visit-plan.html` | `/assets/catalog-outings.webp` | 640×640 | summary |
| `sibling-role.html` | `/assets/long-guide-studies/ask-for-meeting-access.webp` | 1536×1024 | summary_large_image |
| `small-outings-count.html` | `/assets/family-outings/lexington-ice-cream-family.webp` | 1350×1800 | summary |
| `start-here.html` | `/assets/family-outings/fort-mcclary-waterfront.webp` | 1800×1350 | summary_large_image |
| `support-professional-role.html` | `/assets/long-guide-studies/iep-meeting-follow-up.webp` | 1536×1024 | summary_large_image |
| `thank-you-for-sharing-an-ausome-life.html` | `/assets/dairy-joy-october/grandpa-steve-james-ruby.jpeg` | 1536×1152 | summary_large_image |
| `things-weve-bought.html` | `/assets/catalog-hosting.webp` | 640×640 | summary |
| `topics/advice.html` | `/assets/long-guide-studies/ask-for-meeting-access.webp` | 1536×1024 | summary_large_image |
| `topics/advocacy.html` | `/assets/long-guide-studies/organize-school-paperwork.webp` | 1536×1024 | summary_large_image |
| `topics/beauty.html` | `/assets/long-guide-studies/small-weekend-beauty-bag.webp` | 1536×1024 | summary_large_image |
| `topics/brands.html` | `/assets/main-street/outfitter-interior.webp` | 1536×1024 | summary_large_image |
| `topics/family.html` | `/assets/family-notes/doe-orchards-family.webp` | 675×900 | summary |
| `topics/holidays.html` | `/assets/long-guide-studies/gifts-without-a-performance.webp` | 1536×1024 | summary_large_image |
| `topics/home.html` | `/assets/long-guide-studies/household-instruction-cards.webp` | 1536×1024 | summary_large_image |
| `topics/outings.html` | `/assets/orchard-afternoon-clean.jpg` | 800×620 | summary |
| `topics/stories.html` | `/assets/family-notes/james-ruby-autumn.jpeg` | 1152×1536 | summary |
| `topics/style.html` | `/assets/catalog-style.webp` | 640×640 | summary |
| `travel.html` | `/assets/rangeley-grandparents/autumn-waterfront.jpeg` | 1536×1152 | summary_large_image |
| `von-trapp-family-field-note.html` | `/assets/family-notes/von-trapp-table.webp` | 1152×1536 | summary |
| `wegmans-carolines-cart-field-note.html` | `/assets/family-notes/wegmans-carolines-cart.webp` | 709×975 | summary |
| `wicked-tulips-family-field-note.html` | `/assets/family-notes/wicked-tulips-portrait.webp` | 960×836 | summary |

## Metadata reference

- [Open Graph protocol](https://ogp.me/) — image URL, structured dimensions/MIME and meaningful image description.
