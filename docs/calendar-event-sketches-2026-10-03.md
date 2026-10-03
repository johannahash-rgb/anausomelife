# Event illustrations · 3 October 2026

The public calendar has 36 distinct dated-event illustrations, plus a separate annual watchlist illustration. Every dated record has an original composition, including repeated sessions of the same program and venue. Artwork is keyed by event ID, not shared program name.

## Origin and publication basis

All 37 artworks were newly generated for this site using OpenAI's built-in image-generation tool from original event-inspired subject prompts. No third-party photographs, logos, copied characters, production costumes or family photographs were supplied or reused. Each image was visually reviewed and converted to a 720 × 480 WebP while retaining its full composition. Illustrations are conceptual still lifes or scenes, not documentary photographs, access maps or representations of a venue's confirmed exhibits. The owner requested that process labels not appear on the cards; the image alternatives describe their subjects. Provenance remains recorded here and in the data manifest. Nothing presents these sketches as documentary photography. This provenance record is not a guarantee of complete legal clearance.

`data/event-illustrations.json` maintains the exact event-ID-to-asset mapping, descriptive alternative text and display dimensions. The artwork is stored under `assets/event-sketches/`. Publication assets are optimized 720-pixel WebPs; images load lazily. Every new dated record requires its own reviewed artwork and manifest entry. The calendar remains usable if the illustration manifest cannot load.

## UI

Native labeled month and date controls, original navy line icons, labeled controls with at least 44-pixel targets, visible keyboard focus, reduced-motion support, and responsive art placement. The month grid uses each dated event’s art and returns keyboard focus to the chosen full listing. A regional Event map view is integrated alongside the list and month views, with an accessible matching venue list. A pre-existing state-index selector pointing inside the wrong container was corrected.

No event dates, source evidence, booking details, accessibility claims, or editorial calendar entries were changed.

## Verification

JavaScript syntax checked. All illustration regression tests passed. A DOM harness verified every active listing has one image, all seven state controls render, three month choices populate, combined month/state/search filters work, and the no-results state appears. The existing refresh suite passes 21 tests; its seed test refers to an already-missing `data/curated-events.json` in the repository. The focused HTML media/rights check passes, with its documented scope limitations. Live browser checks are recorded in the release report after deployment.
