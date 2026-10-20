/* Progressive enhancement: all 104 definitions remain readable without this file. */
(() => {
  'use strict';
  const root = document.querySelector('.cg-root');
  if (!root) return;
  const input = document.getElementById('cg-search');
  const count = document.getElementById('cg-count');
  const clear = document.getElementById('cg-clear');
  const grid = document.getElementById('cg-grid');
  const chips = [...root.querySelectorAll('[data-category-filter]')];
  const cards = [...root.querySelectorAll('.cg-term')];
  if (!input || !grid || !cards.length) return;
  const normalize = value => value.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim();
  const rows = cards.map((el, index) => ({el, index, name: normalize(el.dataset.name), aliases: normalize(el.dataset.aliases || ''), text: normalize(el.textContent), category: el.dataset.category}));
  let category = 'All';
  let timer;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const scrollTo = el => el.scrollIntoView({block: 'start', behavior: reducedMotion.matches ? 'auto' : 'smooth'});
  const status = document.getElementById('cg-empty');
  function filter() {
    const query = normalize(input.value);
    const words = query.split(' ').filter(Boolean);
    let visible = 0;
    rows.forEach(row => {
      const matches = (category === 'All' || category === row.category) && words.every(word => (row.name + ' ' + row.aliases + ' ' + row.text).includes(word));
      row.el.hidden = !matches;
      if (matches) visible++;
      row.el.style.order = query ? String(row.name === query ? -3 : row.name.startsWith(query) || row.aliases.split(' ').includes(query) ? -2 : row.name.includes(query) ? -1 : row.index) : String(row.index);
    });
    count.textContent = visible + (visible === 1 ? ' term' : ' terms') + (category === 'All' ? '' : ' · ' + category);
    chips.forEach(chip => chip.setAttribute('aria-pressed', String(chip.dataset.categoryFilter === category)));
    clear.hidden = !input.value && category === 'All';
    status.hidden = visible !== 0;
  }
  function reset() { clearTimeout(timer); input.value = ''; category = 'All'; filter(); }
  function revealHash(focus) {
    const id = location.hash.slice(1);
    const target = document.getElementById(id);
    if (!target || !target.classList.contains('cg-term')) return;
    if (target.hidden) reset();
    target.open = true;
    requestAnimationFrame(() => {
      scrollTo(target);
      if (focus) target.querySelector('summary').focus({preventScroll:true});
    });
  }
  input.addEventListener('input', () => {clearTimeout(timer); timer = setTimeout(filter, 120);});
  input.addEventListener('keydown', e => {if (e.key === 'Escape') {reset(); input.focus();} if (e.key === 'Enter') {e.preventDefault();clearTimeout(timer); filter(); const first = [...cards].filter(c => !c.hidden).sort((a,b)=>Number(a.style.order)-Number(b.style.order))[0]; if (first) {first.open=true; scrollTo(first); first.querySelector('summary').focus({preventScroll:true});}}});
  clear.addEventListener('click', () => {reset(); input.focus();});
  chips.forEach(chip => chip.addEventListener('click', () => {category=chip.dataset.categoryFilter; filter();}));
  root.querySelectorAll('[data-jump]').forEach(button => button.addEventListener('click', () => {input.value=''; category=button.dataset.jump; filter(); scrollTo(document.getElementById('cg-search-tools'));}));
  root.querySelectorAll('[data-lookup]').forEach(button => button.addEventListener('click', () => {category='All';input.value=button.dataset.lookup;filter();scrollTo(document.getElementById('cg-search-tools'));}));
  root.querySelectorAll('[data-tool]').forEach(button => button.addEventListener('click', () => {
    const action = button.dataset.tool;
    if (action === 'print') window.print();
    else cards.filter(c => !c.hidden).forEach(c => c.open = action === 'open');
    const menu = button.closest('.cg-tools'); if (menu) menu.open=false;
  }));
  root.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#term-"]');
    if (!link) return;
    const hash = link.getAttribute('href');
    if (location.hash === hash) {event.preventDefault(); revealHash(true);}
  });
  window.addEventListener('hashchange', () => revealHash(true));
  let priorPrint = [];
  window.addEventListener('beforeprint', () => {priorPrint=cards.map(c=>c.open);cards.filter(c=>!c.hidden).forEach(c=>c.open=true);});
  window.addEventListener('afterprint', () => {cards.forEach((c,i)=>c.open=priorPrint[i]);});
  root.classList.add('cg-enhanced');
  filter();
  revealHash(false);
})();
