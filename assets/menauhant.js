(() => {
  'use strict';
  const links = Array.from(document.querySelectorAll('[data-beach-photo]'));
  const dialog = document.getElementById('beach-lightbox');
  if (!dialog || typeof dialog.showModal !== 'function' || !links.length) return;
  const photo = dialog.querySelector('img');
  const caption = dialog.querySelector('[data-photo-caption]');
  const count = dialog.querySelector('[data-photo-count]');
  let index = 0;
  let opener = null;
  function show(next) {
    index = (next + links.length) % links.length;
    const link = links[index];
    const original = link.querySelector('img');
    photo.src = link.href;
    photo.alt = original.alt;
    caption.textContent = link.closest('figure').querySelector('figcaption').textContent;
    count.textContent = `${index + 1} of ${links.length}`;
  }
  links.forEach((link, i) => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault(); opener = link; show(i); dialog.showModal();
  }));
  dialog.querySelector('[data-photo-prev]').addEventListener('click', () => show(index - 1));
  dialog.querySelector('[data-photo-next]').addEventListener('click', () => show(index + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') { event.preventDefault(); show(index - 1); }
    if (event.key === 'ArrowRight') { event.preventDefault(); show(index + 1); }
  });
  dialog.addEventListener('close', () => { if (opener) opener.focus(); });
  const films = Array.from(document.querySelectorAll('.beach-film-grid video'));
  films.forEach(film => film.addEventListener('play', () => films.forEach(other => { if (other !== film) other.pause(); })));
})();
