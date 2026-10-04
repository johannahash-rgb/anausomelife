/* Adds a deterministic downloadable picture card to eligible An AUsome Life stories. */
(() => {
  'use strict';
  if (window.__AAL_ARTICLE_PICTURE_CARD__) return;
  window.__AAL_ARTICLE_PICTURE_CARD__ = true;

  const start = () => {
    if (!window.AALPictureCard) return;
    if (document.body.classList.contains('picture-card-page') || document.body.classList.contains('picture-card-library-page')) return;
    if (document.querySelector('[data-aal-article-picture-card]')) return;

    const main = document.querySelector('main');
    const h1 = main?.querySelector('h1');
    if (!main || !h1) return;

    const selectors = [
      '.favorite-cover img',
      '.favorite-hero-art img',
      '.hero figure img',
      '.notebook-story-cover img',
      '.coffee-hero figure img',
      '.coffee-hero img',
      '.journal-place-hero img',
      '.field-note-hero img',
      '.er-family-photo img',
      'article > figure img',
      'article figure img',
      'main section figure img'
    ];
    let hero = null;
    for (const selector of selectors) {
      const candidate = main.querySelector(selector);
      if (candidate) { hero = candidate; break; }
    }
    if (!hero) return;

    const imageUrl = new URL(hero.currentSrc || hero.getAttribute('src') || '', location.href);
    if (!imageUrl.href || imageUrl.origin !== location.origin) return;

    const exact = document.querySelector('meta[name="aal-picture-card-label"]')?.content?.trim();
    const heading = h1.textContent.replace(/\s+/g, ' ').trim();
    const isPlace = document.body.classList.contains('favorite-place-page') || document.body.classList.contains('favorite-page');
    let label = exact || heading;
    if (!exact && isPlace && label.includes(':')) label = label.split(':')[0].trim();
    if (!exact && !isPlace && label.length > 34) {
      const firstClause = label.split(/[,;:—–]/)[0].trim();
      if (firstClause.length >= 4) label = firstClause;
    }
    if (!label) return;

    const place = document.querySelector('meta[name="aal-picture-card-place"]')?.content?.trim()
      || main.querySelector('.favorite-place-name')?.textContent?.replace(/\s+/g, ' ').trim()
      || (isPlace ? main.querySelector('.hero .lede')?.textContent?.replace(/\s+/g, ' ').trim() : '')
      || '';
    const description = hero.getAttribute('alt')?.trim() || heading;

    const style = document.createElement('style');
    style.textContent = `
      .aal-article-card-box{margin:18px 0 8px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
      .aal-article-card-button{appearance:none;border:1px solid #173c4c;background:#fffdf8;color:#173c4c;min-height:44px;padding:10px 15px;font:700 .88rem/1.2 Arial,Helvetica,sans-serif;cursor:pointer}
      .aal-article-card-button:hover{background:#eef2ef}.aal-article-card-button:disabled{opacity:.62;cursor:wait}
      .aal-article-card-note{font:400 .76rem/1.4 Arial,Helvetica,sans-serif;color:#52656c}
      .aal-article-card-status{flex-basis:100%;font:400 .78rem/1.4 Arial,Helvetica,sans-serif;color:#52656c;margin:0}
      @media print{.aal-article-card-box{display:none!important}}
    `;
    document.head.append(style);

    const box = document.createElement('div');
    box.className = 'aal-article-card-box';
    box.dataset.aalArticlePictureCard = '';
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'aal-article-card-button';
    button.textContent = 'Download picture card';
    const note = document.createElement('span');
    note.className = 'aal-article-card-note';
    note.textContent = 'Uses this page’s existing picture · no AI';
    const status = document.createElement('p');
    status.className = 'aal-article-card-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    box.append(button, note, status);

    const actionRow = h1.closest('section,article')?.querySelector('.actions');
    if (actionRow) actionRow.insertAdjacentElement('afterend', box);
    else {
      const header = h1.closest('header');
      if (header) header.append(box);
      else h1.insertAdjacentElement('afterend', box);
    }

    button.addEventListener('click', async () => {
      button.disabled = true;
      status.textContent = 'Preparing your PNG…';
      try {
        await window.AALPictureCard.download({
          image: imageUrl.href,
          label,
          place,
          description
        });
        status.textContent = 'Picture card ready.';
      } catch (_) {
        status.textContent = 'We could not prepare this card in your browser. Try the ready-made card library instead.';
      } finally {
        button.disabled = false;
      }
    });
  };

  if (window.AALPictureCard) {
    start();
  } else {
    const script = document.createElement('script');
    script.src = '/assets/picture-card-download.js?v=20261004-static1';
    script.defer = true;
    script.onload = start;
    document.head.append(script);
  }
})();
