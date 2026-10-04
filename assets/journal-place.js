/* Venue story layout: real story photo first; place illustration later. */
(() => {
  'use strict';
  if (!document.body.classList.contains('journal-place')) return;
  if (document.querySelector('.journal-place-hero')) return;

  const head = document.querySelector('.journal-place-head');
  const jumps = document.querySelector('.journal-jumps');
  const cover = document.querySelector('.journal-place-cover');
  if (!head || !jumps || !cover) return;

  const coverFigure = cover.querySelector(':scope > .journal-photo');
  const familyFigure = document.querySelector('.journal-family-photo');
  const originalFamilySection = familyFigure?.closest('.journal-family-chapter') || null;

  // Prefer the family's actual story photograph. If this page only has one photo,
  // that photograph becomes the lead.
  const leadFigure = familyFigure || coverFigure;
  if (!leadFigure) return;

  const hero = document.createElement('section');
  hero.className = 'wrap journal-place-hero';
  head.before(hero);
  head.classList.remove('wrap');
  hero.append(head, leadFigure);
  leadFigure.classList.add('journal-hero-photo');
  leadFigure.querySelector('img')?.setAttribute('fetchpriority','high');
  leadFigure.querySelector('img')?.removeAttribute('loading');

  // When a separate venue illustration had been leading the page, keep it —
  // but move it into a later "field sketch" chapter instead of letting it outrank
  // the family's own photograph.
  if (familyFigure && coverFigure && coverFigure !== familyFigure) {
    const source = coverFigure.querySelector('img')?.getAttribute('src') || '';
    const isIllustration = coverFigure.dataset.mediaKind === 'illustration' || /\/(?:venue-illustrations|sketches)\//.test(source);
    coverFigure.classList.add(isIllustration ? 'journal-location-sketch' : 'journal-location-photo');
    const sketchChapter = document.createElement('section');
    sketchChapter.className = 'wrap journal-sketch-chapter';
    sketchChapter.innerHTML = isIllustration
      ? '<div class="journal-sketch-copy"><p class="eyebrow">Field sketch</p><h2>The place, before the practical details.</h2><p>An illustrated impression of the setting. Use the official information below for current entrances, routes and facilities.</p></div>'
      : '<div class="journal-sketch-copy"><p class="eyebrow">From the family camera roll</p><h2>A little more of our day.</h2></div>';
    sketchChapter.append(coverFigure);
    jumps.after(sketchChapter);
    if (originalFamilySection && !originalFamilySection.querySelector('.journal-photo')) {
      originalFamilySection.remove();
    }
  }

  cover.classList.add('journal-place-cover--story-only');

  // A small editorial cue gives the opening prose its own chapter after the utilities.
  if (!cover.querySelector('.journal-story-label')) {
    const label = document.createElement('p');
    label.className = 'eyebrow journal-story-label';
    label.textContent = 'The little story';
    cover.querySelector('.journal-place-opening')?.prepend(label);
  }
})();