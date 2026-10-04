/* An AUsome Life — stable sitewide navigation. Keep this menu consistent across every page. */
(() => {
  'use strict';
  if (window.__AAL_NAV_20261004__) return;
  window.__AAL_NAV_20261004__ = true;

  if (!document.querySelector('link[href*="immersive-v2.css"]')) {
    const l=document.createElement('link');
    l.rel='stylesheet';
    l.href='/assets/immersive-v2.css?v=20261004-1';
    document.head.append(l);
  }

  const currentPath=(location.pathname.replace(/\/+$/,'')||'/');
  const items=[
    ['Home','/',['/','/index.html']],
    ['Outings','/outings.html',['/outings.html','/favorite-places.html']],
    ['New England','/new-england.html',['/new-england.html','/new-england-weekends.html']],
    ['Travel','/travel.html',['/travel.html']],
    ['At Home','/at-home.html',['/at-home.html']],
    ['Resources','/resources.html',['/resources.html','/library.html','/start-here.html']],
    ['About','/about.html',['/about.html']]
  ];

  const mast=document.querySelector('.mag-masthead,.masthead,header');
  let nav=mast?.querySelector('nav[aria-label="Main navigation"],nav');
  if (!nav && mast) {
    nav=document.createElement('nav');
    nav.setAttribute('aria-label','Main navigation');
    mast.append(nav);
  }
  if (nav) {
    const activeFor=(href,aliases)=>{
      if (aliases.includes(currentPath)) return true;
      if (href==='/outings.html' && (currentPath.startsWith('/favorite-places/') || currentPath.startsWith('/favorite-places-'))) return true;
      if (href==='/resources.html' && (currentPath.startsWith('/guides/') || ['/visit-story.html','/communication-card-generator.html','/aac-outing-note.html','/field-notes.html','/family-planning-toolkit.html'].includes(currentPath))) return true;
      return false;
    };
    nav.innerHTML=items.map(([label,href,aliases])=>`<a href="${href}"${activeFor(href,aliases)?' aria-current="page"':''}>${label}</a>`).join('')+
      '<button class="aal-nav-search" type="button" aria-label="Search the site" title="Search">⌕</button>'+
      '<span class="aal-nav-motto" aria-hidden="true"><b>GOOD<br>PEOPLE</b><b>BRIGHTER<br>TOMORROW</b></span>'+
      '<span class="aal-display-tools"><button type="button" data-aal-font="down" aria-label="Decrease text size">A</button><button type="button" data-aal-font="up" aria-label="Increase text size">A</button><button type="button" data-aal-theme aria-label="Toggle light and dark display">◐</button></span>';
  }

  const search=document.createElement('dialog');
  search.className='aal-search-dialog-v2';
  search.innerHTML='<form method="get" action="/library.html"><button class="aal-search-close-v2" type="button" aria-label="Close search">×</button><p class="eyebrow">Find anything</p><h2>What are you looking for?</h2><div><input name="q" type="search" autocomplete="off" placeholder="Try pool, Maine, AAC, hotel, apple picking…" aria-label="Search An AUsome Life"><button type="submit">Search</button></div><p><a href="/resources.html">Or browse resources →</a></p></form>';
  document.body.append(search);
  document.querySelector('.aal-nav-search')?.addEventListener('click',()=>{search.showModal();requestAnimationFrame(()=>search.querySelector('input')?.focus())});
  search.querySelector('.aal-search-close-v2')?.addEventListener('click',()=>search.close());
  search.addEventListener('click',e=>{if(e.target===search)search.close()});

  const root=document.documentElement;
  const sizeKey='aal-font-scale';
  let scale=parseFloat(localStorage.getItem(sizeKey)||'1');
  const applyScale=()=>{root.style.setProperty('--aal-font-scale',String(Math.min(1.18,Math.max(.92,scale))))};
  applyScale();
  document.querySelector('[data-aal-font="up"]')?.addEventListener('click',()=>{scale=Math.min(1.18,scale+.05);localStorage.setItem(sizeKey,String(scale));applyScale()});
  document.querySelector('[data-aal-font="down"]')?.addEventListener('click',()=>{scale=Math.max(.92,scale-.05);localStorage.setItem(sizeKey,String(scale));applyScale()});
  const themeKey='aal-display-theme';
  if(localStorage.getItem(themeKey)==='ink')document.body.classList.add('aal-ink-mode');
  document.querySelector('[data-aal-theme]')?.addEventListener('click',()=>{document.body.classList.toggle('aal-ink-mode');localStorage.setItem(themeKey,document.body.classList.contains('aal-ink-mode')?'ink':'light')});

  document.body.classList.add('aal-immersive-site');
  if (!document.querySelector('script[src*="image-audit.js"]')) {
    const audit=document.createElement('script');
    audit.src='/assets/image-audit.js?v=20261004-1';
    audit.defer=true;
    document.body.append(audit);
  }
})();