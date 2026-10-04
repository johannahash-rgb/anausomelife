/* Curated downloadable picture-card library. Existing site images only; no AI. */
(() => {
  'use strict';

  const entries = [
    {category:'everyday',label:'water',image:'/assets/card-studio/water.webp',description:'A clear glass of drinking water.'},
    {category:'everyday',label:'quiet break',image:'/assets/card-studio/break.webp',description:'A white armchair with a navy striped cushion.'},
    {category:'everyday',label:'apple',image:'/assets/card-studio/apple.webp',description:'A whole red apple.'},
    {category:'everyday',label:'toilet',image:'/assets/card-studio/toilet.webp',description:'A white toilet.'},
    {category:'everyday',label:'coat',image:'/assets/card-studio/coat.webp',description:'A navy quilted coat.'},
    {category:'everyday',label:'car',image:'/assets/card-studio/car.webp',description:'A navy family car.'},

    {category:'outings',label:'The Book Barn',place:'Niantic, Connecticut',image:'/assets/book-barn-ct-clean.jpg',page:'/favorite-places-book-barn-niantic.html'},
    {category:'outings',label:'Codman Community Farms',place:'Lincoln, Massachusetts',image:'/assets/editorial/farm-meadow.webp',page:'/favorite-places-codman-community-farms.html'},
    {category:'outings',label:'deCordova Sculpture Park',place:'Lincoln, Massachusetts',image:'/assets/editorial/main-street.webp',page:'/favorite-places-decordova.html'},
    {category:'outings',label:'Drumlin Farm',place:'Lincoln, Massachusetts',image:'/assets/editorial/farm-meadow.webp',page:'/favorite-places-drumlin-farm.html'},
    {category:'outings',label:'Gilsland Farm',place:'Falmouth, Maine',image:'/assets/editorial/farm-meadow.webp',page:'/favorite-places-gilsland-farm.html'},
    {category:'outings',label:'Misty Harbor',place:'Wells, Maine',image:'/assets/editorial/autumn-table.webp',page:'/favorite-places-misty-harbor-wells.html'},
    {category:'outings',label:'Pineland Farms',place:'New Gloucester, Maine',image:'/assets/editorial/farm-meadow.webp',page:'/favorite-places-pineland-farms.html'},
    {category:'outings',label:'Quiero Cafe',place:'Portland, Maine',image:'/assets/editorial/main-street.webp',page:'/favorite-places-quiero-cafe-portland.html'},
    {category:'outings',label:'Scarborough State Beach',place:'Narragansett, Rhode Island',image:'/assets/editorial/coastal-walk.webp',page:'/favorite-places-scarborough-state-beach.html'},
    {category:'outings',label:'Sherman’s Book Shop',place:'Freeport, Maine',image:'/assets/editorial/main-street.webp',page:'/favorite-places-shermans-freeport.html'},
    {category:'outings',label:'Watch Hill + Napatree',place:'Westerly, Rhode Island',image:'/assets/editorial/coastal-walk.webp',page:'/favorite-places-watch-hill-napatree.html'},
    {category:'outings',label:'Wells Beach',place:'Wells, Maine',image:'/assets/venue-illustrations/wells-beach-winter-illustration.webp',page:'/favorite-places-wells-beach.html'},
    {category:'outings',label:'Wilson Farm',place:'Lexington, Massachusetts',image:'/assets/editorial/main-street.webp',page:'/favorite-places-wilson-farm.html'},
    {category:'outings',label:'Wolfe’s Neck Center',place:'Freeport, Maine',image:'/assets/editorial/farm-meadow.webp',page:'/favorite-places-wolfes-neck.html'},
    {category:'outings',label:'York + the Nubble',place:'York, Maine',image:'/assets/york-maine-clean.jpg',page:'/favorite-places-york-nubble.html'},

    {category:'stories',label:'apple picking',image:'/assets/orchard-afternoon-clean.jpg',page:'/apple-orchard-afternoon.html',description:'A family apple-orchard afternoon.'},
    {category:'stories',label:'coffee',image:'/assets/editorial/autumn-table.webp',page:'/eight-oclock-colombian-peaks-field-note.html',description:'A warm New England coffee still life.'},
    {category:'stories',label:'small outing',image:'/assets/family-outings/lexington-ice-cream-family.webp',page:'/small-outings-count.html',description:'A family outing.'},
    {category:'stories',label:'swimming',image:'/assets/venue-illustrations/indoor-pool-illustration.webp',page:'/older-teen-swim-guide.html',description:'An indoor swimming pool.'}
  ];

  const root = document.querySelector('[data-picture-card-library]');
  if (!root || !window.AALPictureCard) return;

  const grid = root.querySelector('[data-card-grid]');
  const count = root.querySelector('[data-card-count]');
  const filters = [...root.querySelectorAll('[data-card-filter]')];
  let current = 'all';

  function render() {
    const shown = current === 'all' ? entries : entries.filter(entry => entry.category === current);
    grid.replaceChildren();
    count.textContent = `${shown.length} ready-made ${shown.length === 1 ? 'card' : 'cards'}`;

    for (const entry of shown) {
      const item = document.createElement('article');
      item.className = 'download-card-tile';

      const figure = document.createElement('figure');
      const img = document.createElement('img');
      img.src = entry.image;
      img.alt = entry.description || '';
      img.loading = 'lazy';
      img.decoding = 'async';
      const figcaption = document.createElement('figcaption');
      const strong = document.createElement('strong');
      strong.textContent = entry.label;
      figcaption.append(strong);
      if (entry.place) {
        const small = document.createElement('small');
        small.textContent = entry.place;
        figcaption.append(small);
      }
      figure.append(img, figcaption);

      const actions = document.createElement('div');
      actions.className = 'download-card-actions';
      const download = document.createElement('button');
      download.type = 'button';
      download.className = 'button';
      download.textContent = 'Download PNG';
      const status = document.createElement('span');
      status.className = 'download-card-status';
      status.setAttribute('role', 'status');
      status.setAttribute('aria-live', 'polite');
      actions.append(download);

      if (entry.page) {
        const story = document.createElement('a');
        story.className = 'button secondary';
        story.href = entry.page;
        story.textContent = entry.category === 'outings' ? 'Open place' : 'Open story';
        actions.append(story);
      }
      actions.append(status);
      item.append(figure, actions);
      grid.append(item);

      download.addEventListener('click', async () => {
        download.disabled = true;
        status.textContent = 'Preparing…';
        try {
          await window.AALPictureCard.download({
            image: entry.image,
            label: entry.label,
            place: entry.place || '',
            description: entry.description || entry.label
          });
          status.textContent = 'Ready.';
        } catch (_) {
          status.textContent = 'Could not prepare this card.';
        } finally {
          download.disabled = false;
        }
      });
    }
  }

  filters.forEach(button => button.addEventListener('click', () => {
    current = button.dataset.cardFilter;
    filters.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    render();
  }));

  render();
})();
