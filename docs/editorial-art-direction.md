# Editorial art direction

Owner-approved reference: the original Margaritas Waltham jukebox watercolor, approved 4 October 2026. The Ellis Island pedicab study is the companion reference for pen detail, natural proportions and organic edges.

## Composition and shapes

- Use original ink-and-watercolor illustrations with softly irregular transparent edges that sit naturally on the cream page.
- Keep the subject's full shape. Do not crop the artwork to fill a fixed card, add rounded masks, stretch it, tint it or add a synthetic drop shadow.
- Let each piece have a purpose: a distinctive place, an object from the story or a useful moment. Avoid repeated generic decorative imagery.
- Lead with one clear composition, then use quieter supporting art. Avoid scattering multiple copies of the same image through a page.
- Use fine rules, open space and aligned text for structure. Keep headings outside busy artwork.

## Color and type

- Reuse the existing cream, navy-ink and pine-green theme variables. Retain recognizable subject colors, such as the jukebox's pink glow, as controlled accents.
- Use the established Georgia editorial headings and prose, with the existing sans-serif navigation and functional controls.
- Captions use the same modest italic serif treatment and readable contrast. Keep disclosure wording truthful and concise.
- Keep paragraph measure and section spacing comfortable on mobile; artwork must scale without clipping or horizontal overflow.

## Photos and truthful illustration

- Original family photographs remain photographs, with original pixels and proportions. Place them alongside the story with factual captions.
- Generated artwork is clearly distinguishable from documentary photography. An illustration cannot establish a venue's actual entrance, route, facilities or access.
- Record the source and intended use of each new asset in a provenance file. Keep internal art-direction notes out of public copy.

## Shared implementation

`assets/global-nav.js` loads `assets/editorial-art-direction.css` for editorial article pages. It marks only figures whose image alternative explicitly describes a sketch, illustration or watercolor, or which use the approved artwork class. The shared layer preserves existing geometry and controls; it normalizes artwork edges, image fitting and caption styling.

The Margaritas page also includes the stylesheet directly for the no-JavaScript path. Its original photos retain their separate photo classes. New or revised article templates should include this shared stylesheet directly after their page styles.

Review each newly generated piece for composition and recognizability before publication. Check the finished page at a narrow and wide viewport when browser verification is available. Confirm that headings remain unique and photo bytes unchanged when adjusting layout.
