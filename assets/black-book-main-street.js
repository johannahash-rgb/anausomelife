/* Keep category browsing and filtered results predictable. */
(() => {
  'use strict';
  const page = document.querySelector('.black-book-page');
  const form = page?.querySelector('.directory-controls');
  if (!form) return;
  function syncLayout() {
    const {q, kind, relationship, sort} = form.elements;
    const filtered = q.value.trim() || kind.value || relationship.value || sort.value !== 'featured';
    page.dataset.directoryMode = filtered ? 'results' : 'browse';
  }
  ['input', 'change', 'reset'].forEach(type => {
    form.addEventListener(type, () => queueMicrotask(syncLayout));
  });
  if (document.readyState === 'complete') syncLayout();
  else document.addEventListener('DOMContentLoaded', syncLayout);
  page.querySelectorAll('.book-categories a').forEach(link => {
    link.addEventListener('click', () => {
      const section = document.getElementById(link.hash.slice(1));
      if (section?.hidden) form.reset();
      page.querySelectorAll('.book-categories a').forEach(item => {
        item.removeAttribute('aria-current');
        if (item === link) item.setAttribute('aria-current', 'location');
      });
    });
  });
  const detail = page.querySelector('.book-lightbox');
  if (detail && typeof detail.showModal === 'function') {
    page.querySelectorAll('[data-look-closer]').forEach(link => {
      link.addEventListener('click', event => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        const source = link.closest('figure').querySelector('img');
        const image = detail.querySelector('img');
        image.src = link.href;
        image.alt = source.alt;
        detail.showModal();
      });
    });
  }
})();
