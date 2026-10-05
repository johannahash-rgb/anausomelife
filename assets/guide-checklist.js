/* Printable checklists: all groups remain readable, including without JavaScript. */
(() => {
  'use strict';
  const root = document.querySelector('.ellis-review');
  if (!root) return;
  root.querySelectorAll('[data-guide-panel]').forEach(panel => {
    const checks = [...panel.querySelectorAll('input[type="checkbox"]')];
    const progress = panel.querySelector('[data-guide-progress]');
    const update = () => { if (progress) progress.textContent = `${checks.filter(c => c.checked).length} of ${checks.length} checked`; };
    checks.forEach(check => check.addEventListener('change', update));
    panel.querySelector('[data-guide-reset]')?.addEventListener('click', () => {
      checks.forEach(check => { check.checked = false; }); update();
    });
    update();
  });
  function revealHash() {
    let id; try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    let target = document.getElementById(id);
    while (target && root.contains(target)) {
      if (target.tagName === 'DETAILS') target.open = true;
      target = target.parentElement;
    }
  }
  window.addEventListener('hashchange', revealHash); revealHash();
  let saved = [];
  window.addEventListener('beforeprint', () => {
    if (saved.length) return;
    saved = [...root.querySelectorAll('details')].map(detail => ({ detail, open: detail.open }));
    saved.forEach(({ detail }) => { detail.open = true; });
  });
  window.addEventListener('afterprint', () => {
    saved.forEach(({ detail, open }) => { detail.open = open; }); saved = [];
  });
  root.querySelector('#er-print')?.addEventListener('click', () => window.print());
})();
