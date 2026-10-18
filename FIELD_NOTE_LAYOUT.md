# An AUsome Life — Favorite Place / Field Note Layout

## The opening sequence
Every place story should answer two questions immediately:
1. **Where are we?**
2. **Why did this moment matter enough to save?**

For new brand/place/product stories, the dek should also identify the useful thing readers can take away: a free board, practical guide or specific firsthand insight. Give social metadata a complete place/product name, location where relevant, and that benefit. Preserve the editorial headline rather than repeating a marketing heading through the page.

### Desktop
**Split hero**
- Left: place eyebrow, title, dek, 1 short lived-in line if needed.
- Right: the **real story photograph from the visit**.
- The real photo outranks illustration, map, logo or utility navigation.

### Mobile
1. Eyebrow
2. Title
3. Dek
4. **Real story photograph immediately**
5. Utility grid

No visitor should have to scroll past the whole practical interface before encountering the actual story.

---

## Utility grid
Immediately after the hero:
- The little story
- The simple plan
- Getting there
- Access & facilities
- Hours & links
- Print the guide

The utilities are useful, but they are **supporting cast**, not the opening scene.

---

## Visual chapter after utilities
Use a location-specific field sketch / watercolor / ink drawing.

### Source rule
The sketch should be inspired by:
- our own family camera-roll / Google Photos from the visit whenever available;
- otherwise a properly licensed/current location reference.

Do **not** use a generic “New England” illustration and imply that it depicts the venue.

### What to sketch
Prefer the place itself:
- storefront;
- alley or approach;
- harbor edge;
- farm building;
- hotel exterior or lobby geometry;
- pool room;
- trailhead;
- distinctive architecture or landscape.

People do not need to appear. The sketch is about **place memory and wayfinding**, not portraiture.

### Style
- loose ink + watercolor / editorial field sketch;
- recognizable but not photorealistic;
- restrained cream, forest, navy, brick, weathered wood;
- no fake logo recreation;
- no cartoon disability cues;
- no tourist-poster caricature.

The family photograph carries the human story. The sketch gives the location atmosphere.

---

## Story rhythm
After the utility grid and sketch:
- 2–4 short story paragraphs;
- “Start with this” practical note;
- at-a-glance facts;
- simple plan;
- arrival/map;
- access & facilities;
- supporting real photographs;
- source links;
- printable guide.

Aim for a visual/editorial change of scene every 2–3 mobile screens.

---

## Editorial voice
Specific, lived-in, lightly dry.

Good:
> A single scoop can be the whole outing. Nobody gets a medal for adding an unnecessary second stop.

Good:
> The photograph tells you why we remember the place. The field notes tell you whether the visit might actually work.

Avoid:
- generic “making memories” language;
- inspiration framing;
- therapy-copy;
- fake regional quaintness;
- long access disclaimers before the actual story.

---

## Image hierarchy
1. **Our real story photo**
2. Location-specific sketch
3. Supporting family/location photos
4. Map / practical diagram
5. Generic editorial illustration only when it is clearly labeled as such

Never lead a family-tested place story with generic art when a meaningful real photograph exists.

---

## Useful communication downloads

Create a purpose-made choice board or short visual plan when it helps someone participate in the outing. This section follows the current `AGENTS.md` owner direction and replaces the older instruction to turn every hero into a downloadable card. **Do not add automatic family-photo or decorative-venue-art communication cards.**

Use reviewed, recognizable objects with plain labels, enough white space and a clear task. Match the person's likely choices; preserve refusal, alternatives and useful words such as “help,” “break” and “all done.” Keep the person's usual communication system available. Use familiar labels such as “coffee,” “swimming” or the actual place name, rather than an editorial headline.

Keep factual family photographs separate from functional communication art. Label generic or generated objects accurately, and check any menu or product names against an official source. A visual choice does not guarantee current availability, appearance or ingredients. Do not imply that a board created after a visit was used during it.

The download should work as a practical resource on its own, with readable images, labels, credit, useful source link and appropriate disclosure. A board is not a mini advertisement. These are picture communication resources, not official PECS® materials or the PECS® teaching protocol.

Add broadly useful resources to the appropriate picture-card collection and story pathways, using the maintained library conventions. Keep the main resource's ordinary download link available without JavaScript.

---

## A compact sharing section

Every new comparable place, outing or product story needs a reviewed sharing package. Place one authored `.aal-story-share` section after the story and practical information, before related reading. Keep the main benefit and primary action visible. Put optional graphics, captions, image descriptions and exact-file reuse terms in an accessible native disclosure.

The package should contain:

- A story-specific caption with the real reader benefit, canonical link and An AUsome Life credit; a short Story caption with its destination link.
- Reviewed social graphics when their intended sharing rights are cleared. Use a simple feed composition and a tall Story composition with actual dimensions, readable text and full image proportions. A resource preview must not pretend to be the entire usable board.
- Plain download links, meaningful image alt text, and copyable descriptions. The useful text and links remain present without JavaScript; optional copy and native-share buttons are progressively enhanced.
- Permission that applies only to the named, reviewed files and use. Other photographs, illustrations and archive content keep their existing terms.
- Any disclosure required for the shared material to remain accurate by itself. Keep generic-object art distinct from actual product evidence and independent resources distinct from a brand's official materials.

Use `data-share-summary`, `[data-share-caption]` and the existing `assets/story-share.js` enhancement contract described in `docs/brand-repost-publishing.md`. Register the authored page and its reviewed provenance in `docs/story-sharing-approvals.json`; downloadable graphics must match the exact permitted files, hashes and dimensions in that provenance. Do not create a second generated sharing section or hide the only caption/download path behind JavaScript.

Check both the reader's mobile layout and the isolated social assets. Verify link previews and run `python tools/check_story_sharing.py` before publication. The checker reviews packages that exist; the editorial publication review must still confirm that every new comparable story has its own package. Existing archive stories retain the generic link-sharing fallback until individually reviewed.
