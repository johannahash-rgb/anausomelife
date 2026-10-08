/* Optional atmosphere; all directory content and links work without it. */
(() => {
  'use strict';
  const page = document.querySelector('.black-book-page');
  const lights = page?.querySelector('.street-lights');
  if (!lights) return;
  function setLights(on) {
    page.toggleAttribute('data-lamplight', on);
    lights.setAttribute('aria-pressed', String(on));
    lights.textContent = on ? 'Return to daylight' : 'Turn on the lamplight';
  }
  let saved = false;
  try { saved = localStorage.getItem('aal-black-book-lamplight') === 'on'; } catch {}
  setLights(saved);
  lights.hidden = false;
  lights.addEventListener('click', () => {
    const on = !page.hasAttribute('data-lamplight');
    setLights(on);
    try { localStorage.setItem('aal-black-book-lamplight', on ? 'on' : 'off'); } catch {}
  });
  page.querySelectorAll('.street-stops a').forEach(link => {
    link.addEventListener('click', () => {
      // A street stop must remain reachable even after a search hides it.
      const section = document.getElementById(link.hash.slice(1));
      if (section?.hidden) page.querySelector('.directory-controls').reset();
      page.querySelectorAll('.street-stops a').forEach(item => item.removeAttribute('aria-current'));
      link.setAttribute('aria-current', 'location');
    });
  });
})();
