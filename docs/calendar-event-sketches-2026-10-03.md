# Event illustrations · 3 October 2026

The public calendar now has 24 distinct program illustrations covering all 36 dated records, plus a separate annual watchlist illustration. Repeat dates of the same named program at the same venue share the same art. Different programs or venues do not share art.

## Origin and publication basis

All 25 artworks were newly generated for this site using OpenAI's built-in image-generation tool from original event-inspired subject prompts. No third-party photographs, logos, copied characters, production costumes or family photographs were supplied or reused. Each image was visually reviewed and converted to a 720 × 480 WebP while retaining its full composition. Illustrations are conceptual still lifes or scenes, not documentary photographs, access maps or representations of a venue's confirmed exhibits. Visible card captions and the calendar introduction disclose their AI origin and conceptual purpose. This provenance record is not a guarantee of complete legal clearance.

`data/event-illustrations.json` maintains the exact program/venue-to-asset mapping, descriptive alternative text and display dimensions. The artwork is stored under `assets/event-sketches/`. Publication assets total approximately 2.9 MB; images load lazily. New programs require their own reviewed artwork and manifest entry. The calendar remains usable if the illustration manifest cannot load.

## UI

Native labeled month and date controls, original navy line icons, labeled controls with at least 44-pixel targets, visible keyboard focus, reduced-motion support, and responsive art placement. The month grid uses the same event-specific art and returns keyboard focus to the chosen full listing. A pre-existing state-index selector pointing inside the wrong container was corrected.

No event dates, source evidence, booking details, accessibility claims, or editorial calendar entries were changed.

## Verification

JavaScript syntax checked. All seven illustration regression tests passed. A DOM harness verified every active listing has one image, all seven state controls render, three month choices populate, combined month/state/search filters work, and the no-results state appears. The existing refresh suite passes 21 tests; its seed test refers to an already-missing `data/curated-events.json` in the repository. The focused HTML media/rights check passes, with its documented scope limitations. Live browser checks are recorded in the release report after deployment.
