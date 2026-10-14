# Library visual browsing

Owner requested the approved illustrated brand treatment on `library.html` on 14 October 2026.

- Six labeled topic links use their own transparent miniatures in `assets/library-watercolors/`, distinct from all top-navigation imagery. The set is recorded in `docs/library-watercolors-provenance-2026-10-14.json`: armchair, walking boots, family tree, photo stack, pencils and celebration cake. The owner explicitly rejected repeating top-navigation artwork in this row even where destinations overlap.
- Twelve reading-list images reuse material already published in their matching articles. The explicit mapping and factual/illustrated alternative text are in `tools/apply_library_design.py`; no third-party downloads or family-photo alterations were made. New topic art is original generated illustration, not documentary imagery.
- Family-photo permissions and provenance remain in the existing autumn, family-field-notes, journal, Margaritas, Wicked Tulips and My Small World records. Artwork remains distinguishable from family photographs.
- Display the full frame with `object-fit: contain`. Preserve native colors, transparency and image bytes; no masks, tinting, shadows or synthetic crops.
- `tools/build_magazine.py` calls the library decorator for the main catalog. For surgical updates after other catalog edits, run `python tools/apply_library_design.py`. The decorator is idempotent and preserves catalog text and order.
- The existing form remains the search/filter source of truth. Topic links work as ordinary topic-page links without JavaScript, and become in-page filters with JavaScript. Current-topic state updates after filtering, reset and history navigation.

Validation: all 110 existing entries, text and order retained; all added media resolves; JavaScript/Python syntax, editorial-reference audit and strict internal-link audit pass. The reference audit has its usual limited scope and is not comprehensive rights clearance. Existing missing-social-image notices are unrelated to this layout update.
