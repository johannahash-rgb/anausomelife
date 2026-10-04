/* An AUsome Life — rotating homepage notebook + stable A/B test. */
(() => {
  'use strict';
  const root = document.querySelector('.home-welcome');
  if (!root) return;

  const analytics = (name, params) => {
    if (window.AALAnalytics) window.AALAnalytics.track(name, params);
    else (window.__AAL_PENDING_EVENTS__ ||= []).push({ name, params });
  };

  // Stable 50/50 hero experiment. A visitor keeps the same version.
  const experimentId = 'home_hero_v1';
  const storageKey = 'aal_exp_' + experimentId;
  let variant = 'A';
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
    if (saved && (saved.variant === 'A' || saved.variant === 'B')) variant = saved.variant;
    else {
      const random = crypto?.getRandomValues ? crypto.getRandomValues(new Uint32Array(1))[0] / 4294967296 : Math.random();
      variant = random < .5 ? 'A' : 'B';
      localStorage.setItem(storageKey, JSON.stringify({ variant, assigned: Date.now() }));
    }
  } catch (_) {}

  document.documentElement.dataset.homeHeroVariant = variant;
  const copy = root.querySelector('.home-welcome-copy');
  const eyebrow = copy?.querySelector('.eyebrow');
  const title = copy?.querySelector('h1');
  const dek = copy?.querySelector('.home-welcome-dek');
  const body = copy?.querySelector(':scope > p:not(.eyebrow):not(.home-welcome-dek):not(.home-signoff)');
  const primary = copy?.querySelector('.home-actions .button');
  const secondary = copy?.querySelector('.home-actions .home-text-link');

  if (variant === 'B' && eyebrow && title && dek && body && primary && secondary) {
    eyebrow.textContent = 'A family field guide for New England life';
    title.innerHTML = 'Beautiful days.<br>Useful details.';
    dek.innerHTML = 'The lovely part and the practical part,<br>kept together.';
    body.textContent = 'Find places worth going, familiar comforts, useful products and small plans that make the day easier to carry. Accessibility belongs in the details, not at the expense of a whole interesting life.';
    primary.href = '/start-here.html';
    primary.textContent = 'Start with the field guide';
    secondary.href = '/calendar.html';
    secondary.textContent = 'See what’s coming up →';
  }

  [primary, secondary].forEach((el, index) => {
    if (!el) return;
    el.dataset.aalTrack = 'home_hero_' + (index === 0 ? 'primary' : 'secondary');
    el.addEventListener('click', () => analytics('experiment_click', {
      experiment_id: experimentId,
      variant_id: variant,
      element_id: index === 0 ? 'primary_cta' : 'secondary_cta'
    }));
  });
  analytics('experiment_impression', { experiment_id: experimentId, variant_id: variant });

  // Rotating family notebook. Existing content remains valid without JavaScript.
  const stage = root.querySelector('.home-photo-arrangement');
  const figure = stage?.querySelector('.home-main-photo');
  const image = figure?.querySelector('img');
  const caption = figure?.querySelector('figcaption');
  const note = stage?.querySelector('.home-photo-footnote');
  const label = note?.querySelector('span');
  const noteCopy = note?.querySelector('p');
  const noteLink = note?.querySelector('a');
  if (!stage || !figure || !image || !caption || !label || !noteCopy || !noteLink) return;

  stage.setAttribute('role', 'region');
  stage.setAttribute('aria-label', 'Rotating family notebook');
  stage.dataset.homeRotator = 'true';

  const items = [
    {
      src:'/assets/book-barn-ct-clean.jpg',
      alt:'A family photograph of a child browsing the outdoor bookshelves at the Book Barn in Niantic.',
      caption:'A little browsing at the Book Barn, Niantic · family photograph',
      label:'THE FAMILY NOTEBOOK',
      copy:'One good stop. A little room around it.',
      href:'/favorite-places/book-barn-niantic.html',
      link:'Open the Book Barn field guide →'
    },
    {
      src:'/assets/aquarium-visit.webp',
      alt:'A teenager watching the trout pond at the L.L.Bean flagship in Freeport.',
      caption:'The trout pond at L.L.Bean, Freeport · family photograph',
      label:'UP THE COAST',
      copy:'A flagship, a pond and time enough to wander.',
      href:'/favorite-places/llbean-freeport.html',
      link:'Open the Freeport field guide →'
    },
    {
      src:'/assets/family-outings/lexington-ice-cream-family.webp',
      alt:'Two family members together with an ice-cream cone in Lexington.',
      caption:'A familiar scoop in Lexington · family photograph',
      label:'THE EASY LOCAL STOP',
      copy:'Ice cream. A little time. A known way home.',
      href:'/favorite-places-rancatores-lexington.html',
      link:'Read the Lexington story →'
    },
    {
      src:'/assets/family-outings/fort-mcclary-waterfront.webp',
      alt:'Two adults together at the Fort McClary waterfront in Maine.',
      caption:'Waterfront time at Fort McClary, Maine · family photograph',
      label:'A MAINE FIELD NOTE',
      copy:'Lunch, a harbor view and no need to hurry.',
      href:'/favorite-places/kittery-food-mart-fort-mcclary.html',
      link:'Open the Fort McClary field guide →'
    }
  ];

  let index = 0;
  let timer = null;
  let paused = false;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const controls = document.createElement('div');
  controls.className = 'home-rotator-controls';
  controls.innerHTML = '<button type="button" data-rotator-prev aria-label="Previous family note">←</button><button type="button" data-rotator-pause aria-pressed="false">Pause</button><span data-rotator-count aria-live="polite">1 of ' + items.length + '</span><button type="button" data-rotator-next aria-label="Next family note">→</button>';
  stage.append(controls);

  const count = controls.querySelector('[data-rotator-count]');
  const pauseButton = controls.querySelector('[data-rotator-pause]');

  function render(nextIndex, source = 'auto') {
    index = (nextIndex + items.length) % items.length;
    const item = items[index];
    stage.classList.add('is-changing');
    const apply = () => {
      image.src = item.src;
      image.alt = item.alt;
      caption.textContent = item.caption;
      label.textContent = item.label;
      noteCopy.textContent = item.copy;
      noteLink.href = item.href;
      noteLink.textContent = item.link;
      noteLink.dataset.aalTrack = 'home_rotator_story';
      count.textContent = (index + 1) + ' of ' + items.length;
      stage.classList.remove('is-changing');
      analytics('home_rotator_impression', {
        item_index: index + 1,
        item_href: item.href,
        change_source: source
      });
    };
    if (reduced) apply(); else setTimeout(apply, 180);
  }

  function start() {
    if (reduced || paused) return;
    clearInterval(timer);
    timer = setInterval(() => render(index + 1, 'auto'), 9000);
  }
  function setPaused(value) {
    paused = value;
    pauseButton.setAttribute('aria-pressed', String(paused));
    pauseButton.textContent = paused ? 'Play' : 'Pause';
    clearInterval(timer);
    if (!paused) start();
  }

  controls.querySelector('[data-rotator-prev]').addEventListener('click', () => { render(index - 1, 'previous'); start(); });
  controls.querySelector('[data-rotator-next]').addEventListener('click', () => { render(index + 1, 'next'); start(); });
  pauseButton.addEventListener('click', () => setPaused(!paused));
  noteLink.addEventListener('click', () => analytics('home_rotator_click', { item_index:index + 1, item_href:items[index].href }));
  stage.addEventListener('mouseenter', () => clearInterval(timer));
  stage.addEventListener('mouseleave', start);
  stage.addEventListener('focusin', () => clearInterval(timer));
  stage.addEventListener('focusout', event => { if (!stage.contains(event.relatedTarget)) start(); });

  analytics('home_rotator_impression', { item_index: 1, item_href: items[0].href, change_source:'initial' });
  if (reduced) setPaused(true); else start();
})();