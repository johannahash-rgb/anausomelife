/* An AUsome Life — global wayfinding + universal search. No analytics; search stays in the browser. */
(() => {
  'use strict';
  if (window.__AAL_GLOBAL_NAV__) return;
  window.__AAL_GLOBAL_NAV__ = true;

  document.querySelectorAll('use[href^="/assets/editorial-icons.svg#"]').forEach(use => use.setAttribute('href', use.getAttribute('href').replace('/assets/editorial-icons.svg#','/assets/editorial-icons.svg?v=20261003-journal#')));
  const fold = value => (value || '').toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const esc = value => (value || '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const icon = name => {
    const drawings={home:'home',compass:'compass',outing:'compass',family:'heart',talk:'picture',calendar:'calendar',book:'address-book',journal:'journal',search:'search',menu:'menu'};
    if(drawings[name])return '<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><use href="/assets/editorial-icons.svg?v=20261003-journal#'+drawings[name]+'"></use></svg>';
    return ({
    home:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11.2 12 4l9 7.2v8.3a.5.5 0 0 1-.5.5h-5.2v-6.2H8.7V20H3.5a.5.5 0 0 1-.5-.5z"/><path d="M1.8 12.2 12 4l10.2 8.2"/></svg>',
    search:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.6"/><path d="m16 16 5 5"/></svg>',
    compass:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m15.8 8.2-2.1 5.5-5.5 2.1 2.1-5.5z"/></svg>',
    outing:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16M6 17l4.2-7 2.3 3.3L15 9l3 8M8 7.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/></svg>',
    family:'<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="8" r="2.7"/><circle cx="16.4" cy="9" r="2.2"/><path d="M3.5 19c.5-4 2.1-6 4.8-6s4.3 2 4.8 6M12.8 18.5c.4-3 1.6-4.6 3.8-4.6 2.1 0 3.4 1.5 3.8 4.6"/></svg>',
    talk:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5h16v10H9l-5 4z"/><path d="M8 10h8M8 13h5"/></svg>',
    calendar:'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="1"/><path d="M7 3v4M17 3v4M3.5 9h17M7 13h3M12 13h3M7 16h3"/></svg>',
    book:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5c3.5-.7 6.1 0 8 2v11c-1.9-2-4.5-2.7-8-2zM20 5.5c-3.5-.7-6.1 0-8 2v11c1.9-2 4.5-2.7 8-2z"/></svg>',
    close:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 5 14 14M19 5 5 19"/></svg>'
  }[name] || '');
  };

  const style = document.createElement('style');
  style.id = 'aal-global-nav-style';
  style.textContent = `
    .aal-wayfinder{position:sticky;top:0;z-index:70;background:rgba(251,248,241,.97);border-bottom:1px solid #d4d6cc;box-shadow:0 6px 22px rgba(23,60,76,.055);backdrop-filter:blur(12px)}
    .aal-wayfinder-inner{width:min(1180px,calc(100% - 42px));margin:auto;display:grid;grid-template-columns:repeat(8,minmax(76px,1fr));align-items:stretch}
    .aal-wayfinder a,.aal-wayfinder button{appearance:none;border:0;border-right:1px solid #e1e0d8;background:transparent;color:#173c4c;text-decoration:none;min-height:68px;padding:8px 8px 7px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;font:600 .69rem/1.15 Arial,Helvetica,sans-serif;letter-spacing:.015em;text-align:center;cursor:pointer}
    .aal-wayfinder a:first-child{border-left:1px solid #e1e0d8}.aal-wayfinder a:hover,.aal-wayfinder button:hover,.aal-wayfinder [aria-current="page"]{background:#eef2ef}.aal-wayfinder svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.55;stroke-linecap:round;stroke-linejoin:round;flex:none}.aal-wayfinder .aal-search-shortcut{font-size:.58rem;font-weight:500;color:#65757b;letter-spacing:.04em}.aal-wayfinder-label{display:block;white-space:nowrap}
    .aal-search-dialog{width:min(860px,calc(100vw - 28px));max-height:min(82vh,780px);padding:0;border:1px solid #52656c;background:#fffdf8;color:#173c4c;box-shadow:0 24px 90px rgba(16,51,76,.24)}.aal-search-dialog::backdrop{background:rgba(16,51,76,.52);backdrop-filter:blur(2px)}
    .aal-search-shell{padding:26px}.aal-search-top{display:flex;align-items:flex-start;justify-content:space-between;gap:24px}.aal-search-top .eyebrow{margin:0 0 7px}.aal-search-top h2{font:400 clamp(2rem,5vw,3.2rem)/1 Georgia,serif;margin:0;color:#173c4c}.aal-search-close{width:44px;height:44px;border:1px solid #d4d6cc!important;background:#fff!important;display:grid!important;place-items:center!important;padding:0!important}.aal-search-close svg{width:20px;height:20px;fill:none;stroke:#173c4c;stroke-width:1.6;stroke-linecap:round}
    .aal-search-form{margin-top:24px}.aal-search-input-wrap{display:grid;grid-template-columns:1fr auto;border:2px solid #173c4c;background:white}.aal-search-input-wrap input{border:0!important;padding:17px 18px!important;font-size:1.05rem!important;min-width:0;background:white!important}.aal-search-input-wrap button{border:0;border-left:1px solid #d4d6cc;background:#173c4c;color:white;padding:0 22px;font-weight:700;cursor:pointer}.aal-search-hint{font-size:.76rem;color:#52656c;margin:9px 0 0}.aal-search-chips{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 4px}.aal-search-chips button{border:1px solid #cfd5d2;background:#fbf8f1;color:#173c4c;padding:8px 12px;min-height:38px;font-size:.76rem;cursor:pointer}.aal-search-chips button:hover{background:#eef2ef}
    .aal-search-results{margin-top:24px;border-top:1px solid #d4d6cc;max-height:44vh;overflow:auto}.aal-search-empty{padding:24px 0;color:#52656c}.aal-search-result{display:grid;grid-template-columns:100px 1fr auto;gap:18px;align-items:center;padding:17px 0;border-bottom:1px solid #e1e0d8;text-decoration:none;color:#173c4c}.aal-search-result:hover h3{text-decoration:underline;text-underline-offset:4px}.aal-search-result .aal-result-kind{font-size:.61rem;letter-spacing:.11em;text-transform:uppercase;color:#65757b}.aal-search-result h3{font:400 1.2rem/1.2 Georgia,serif;margin:0}.aal-search-result p{font-size:.79rem;line-height:1.5;color:#52656c;margin:5px 0 0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.aal-search-result .aal-go{font-size:1.2rem}.aal-search-footer{display:flex;justify-content:space-between;gap:18px;align-items:center;padding-top:18px;font-size:.78rem}.aal-search-footer a{font-weight:700}.aal-search-status{color:#52656c}
    .aal-unified-nav .mag-masthead nav,.aal-unified-nav .masthead nav{display:none}.aal-unified-nav .mag-masthead{padding-block:14px}.aal-wayfinder a,.aal-wayfinder button{font-size:.875rem;min-height:72px}.aal-search-shortcut{display:none!important}.aal-search-hint,.aal-search-chips button,.aal-search-result p,.aal-search-footer,.aal-search-result .aal-result-kind{font-size:.875rem}.aal-search-result{grid-template-columns:90px 1fr}.aal-search-result .aal-go{display:none}.aal-search-result h3{font-size:1.3rem}.aal-search-input-wrap input{font-size:1rem!important}.aal-section-dialog{box-sizing:border-box;width:min(1100px,calc(100vw - 24px));max-height:88vh;overflow:auto;border:1px solid #7a8e8f;background:#fffdf8;color:#173c4c;padding:28px}.aal-section-dialog::backdrop{background:#173c4caa}.aal-section-head{display:flex;justify-content:space-between;align-items:start;gap:20px;border-bottom:1px solid #bcc9c5;padding-bottom:20px}.aal-section-head h2{font:400 clamp(1.8rem,4vw,2.6rem)/1.1 Georgia;margin:8px 0}.aal-section-head button{min-height:44px;padding:10px 16px;border:1px solid #173c4c;background:#fff;color:#173c4c;font:1rem Arial;cursor:pointer}.aal-section-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;padding-top:24px}.aal-section-grid h3{font:400 1.45rem Georgia;margin:0 0 12px}.aal-section-grid a{display:block;padding:10px 0;font:1rem/1.35 Arial;color:#173c4c;text-underline-offset:4px}.aal-section-grid a[aria-current]{font-weight:bold}.aal-section-dialog :focus-visible,.aal-wayfinder :focus-visible,.aal-search-dialog :focus-visible{outline:3px solid #b8432d;outline-offset:3px}
    @media(max-width:820px){.aal-wayfinder-inner{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));overflow:visible}.aal-wayfinder a,.aal-wayfinder button{min-width:0;font-size:.875rem;min-height:63px;padding:8px 2px;word-break:normal}.aal-wayfinder-label{white-space:normal}.aal-section-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.aal-section-dialog{padding:18px}.aal-search-result{grid-template-columns:1fr}.aal-wayfinder svg{height:19px}.aal-unified-nav .mag-masthead{padding-block:10px}.aal-wayfinder{position:relative}}
    @media print{.aal-section-dialog{display:none!important}}
    .aal-start-link{font-weight:700!important}
    @media(max-width:820px){.aal-wayfinder{position:relative}.aal-wayfinder-inner{width:100%;display:flex;overflow-x:auto;scroll-snap-type:x proximity;scrollbar-width:none}.aal-wayfinder-inner::-webkit-scrollbar{display:none}.aal-wayfinder a,.aal-wayfinder button{min-width:88px;border-bottom:0;scroll-snap-align:start}.aal-wayfinder a:first-child{border-left:0}.aal-search-shortcut{display:none}.aal-search-shell{padding:20px}.aal-search-result{grid-template-columns:78px 1fr;gap:12px}.aal-search-result .aal-go{display:none}.aal-search-footer{align-items:flex-start;flex-direction:column}}
    @media(max-width:520px){.aal-wayfinder a,.aal-wayfinder button{min-width:82px;min-height:64px;font-size:.65rem}.aal-wayfinder svg{width:20px;height:20px}.aal-search-input-wrap{grid-template-columns:1fr}.aal-search-input-wrap button{min-height:46px;border-left:0;border-top:1px solid #d4d6cc}.aal-search-result{grid-template-columns:1fr}.aal-search-result .aal-result-kind{margin-bottom:-6px}}
    @media(max-width:520px){.aal-wayfinder a,.aal-wayfinder button{font-size:.875rem;min-width:0}.aal-search-shell{padding:16px}}
    @media print{.aal-wayfinder,.aal-search-dialog{display:none!important}}

    .aal-wayfinder svg{width:27px;height:27px;stroke-width:1.4}.aal-wayfinder-label{line-height:1.25}.aal-wayfinder a,.aal-wayfinder button{min-height:58px;font-size:.84rem}
    @media(max-width:820px){.aal-wayfinder-inner{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr))!important;width:calc(100% - 18px);overflow:visible;gap:0}.aal-wayfinder a,.aal-wayfinder button{min-width:0!important;min-height:56px!important;padding:7px 3px;font-size:.78rem!important;flex-direction:column!important;gap:4px!important}.aal-wayfinder svg{height:24px!important;width:24px!important}.aal-wayfinder-label{white-space:normal}.aal-wayfinder{position:relative}}
  `;
  document.head.append(style);
  if (!document.querySelector('link[href*="/assets/editorial.css"]')) {
    const theme=document.createElement('link');theme.rel='stylesheet';theme.href='/assets/editorial.css?v=20261003-mainstreet';document.head.append(theme);
  }


  const shortcuts = [
    {label:'Home',href:'/',icon:'home',match:['/','/index.html']},
    {label:'Find anything',action:'search',icon:'search',hint:'⌘K'},
    {label:'Menu',action:'sections',icon:'menu'},
    {label:'Outings',href:'/favorite-places.html',icon:'outing',match:['/favorite-places.html'],prefix:'/favorite-places/'},
    {label:'Journal',href:'/blog.html',icon:'journal',match:['/blog.html','/older-teen-swim-guide.html','/hotel-pool-checklist.html','/pool-weekend-kit.html']},
    {label:'Make cards',href:'/communication-card-generator.html',icon:'talk',match:['/communication-card-generator.html','/visit-story.html','/aac-outing-note.html']},
    {label:'Calendar',href:'/calendar.html',icon:'calendar',match:['/calendar.html']},
    {label:'Directory',href:'/little-black-book.html',icon:'book',match:['/little-black-book.html']}
  ];

  const sectionGroups=[["Begin here", [["The visual directory", "/start-here.html"], ["Every guide", "/library.html"], ["The blog", "/blog.html"], ["Meet us", "/about.html"]]], ["Out & about", [["Favorite places", "/favorite-places.html"], ["Calendar & maps", "/calendar.html"], ["New England weekends", "/new-england-weekends.html"], ["Make a visit story", "/visit-story.html"]]], ["Communication", [["Picture card maker", "/communication-card-generator.html"], ["Notes & profiles", "/communication-notes.html"], ["Multimodal guide", "/multimodal-communication.html"], ["AAC outing note", "/aac-outing-note.html"]]], ["Family life", [["Family roles", "/family-roles.html"], ["Paternal field notes", "/paternal-role.html"], ["Family agreements", "/family-agreements.html"], ["Plans & handoffs", "/family-planning-toolkit.html"]]], ["Little adventures", [["Kid fun & videos", "/kid-fun.html"], ["The little boot story", "/little-adventures.html"], ["One simple game", "/paternal-football-card.html"], ["The family notebook", "/family-notebook.html"]]], ["Home & wardrobe", [["At home", "/at-home.html"], ["Household reset", "/household-reset.html"], ["Family wardrobe", "/family-wardrobe.html"], ["School & advocacy", "/topics/advocacy.html"]]], ["Useful discoveries", [["Brands & organizations", "/little-black-book.html"], ["Product guides", "/product-guides.html"], ["Coffee field note", "/eight-oclock-colombian-peaks-field-note.html"], ["Copyable field notes", "/field-notes.html"]]], ["Our editorial rules", [["Language & representation", "/language.html"], ["How we choose", "/how-we-choose.html"], ["Disclosure", "/disclosure.html"], ["Privacy", "/privacy.html"], ["Accessibility", "/accessibility.html"], ["Contact", "/contact.html"]]]];
  const current = location.pathname.replace(/\/+$/,'') || '/';
  const bar = document.createElement('nav');
  bar.className = 'aal-wayfinder';
  bar.setAttribute('aria-label','Site shortcuts');
  bar.innerHTML = '<div class="aal-wayfinder-inner">' + shortcuts.map(item => {
    const active = item.match?.includes(current) || (item.prefix && current.startsWith(item.prefix));
    if (item.action === 'sections') return `<button type="button" data-aal-open-sections aria-haspopup="dialog">${icon(item.icon)}<span class="aal-wayfinder-label">${item.label}</span></button>`;
    if (item.action === 'search') return `<button type="button" data-aal-open-search aria-haspopup="dialog">${icon(item.icon)}<span class="aal-wayfinder-label">${item.label}</span><span class="aal-search-shortcut">${item.hint}</span></button>`;
    return `<a href="${item.href}"${active?' aria-current="page"':''}>${icon(item.icon)}<span class="aal-wayfinder-label">${item.label}</span></a>`;
  }).join('') + '</div>';

  const edition = document.querySelector('.edition-line');
  const masthead = document.querySelector('.mag-masthead,.masthead,header');
  if (masthead) masthead.after(bar); else if (edition) edition.after(bar); else document.body.prepend(bar);

  const sectionDialog=document.createElement('dialog');
  sectionDialog.className='aal-section-dialog';sectionDialog.setAttribute('aria-labelledby','aal-section-title');
  sectionDialog.innerHTML='<div class="aal-section-head"><div><p class="eyebrow">The whole field guide</p><h2 id="aal-section-title">Where would you like to go?</h2></div><button type="button" data-close-sections aria-label="Close all sections">Close</button></div><div class="aal-section-grid">'+sectionGroups.map(([heading,links])=>'<section><h3>'+esc(heading)+'</h3>'+links.map(([label,url])=>'<a href="'+url+'"'+(current===url?' aria-current="page"':'')+'>'+esc(label)+'</a>').join('')+'</section>').join('')+'</div>';
  document.body.append(sectionDialog);document.body.classList.add('aal-unified-nav');
  const sectionButton=bar.querySelector('[data-aal-open-sections]');
  sectionButton.addEventListener('click',()=>{sectionDialog.showModal();document.documentElement.style.overflow='hidden'});
  sectionDialog.querySelector('[data-close-sections]').addEventListener('click',()=>sectionDialog.close());
  sectionDialog.addEventListener('click',e=>{if(e.target===sectionDialog)sectionDialog.close()});
  sectionDialog.addEventListener('close',()=>{document.documentElement.style.overflow='';sectionButton.focus()});

  const primaryNav = document.querySelector('.mag-masthead nav,.masthead nav');
  if (primaryNav && !primaryNav.querySelector('a[href="/start-here.html"]')) {
    const start = document.createElement('a'); start.href='/start-here.html'; start.textContent='Start here'; start.className='aal-start-link';
    primaryNav.prepend(start);
  }

  const dialog = document.createElement('dialog');
  dialog.className = 'aal-search-dialog';
  dialog.setAttribute('aria-label','Search An AUsome Life');
  dialog.innerHTML = `
    <div class="aal-search-shell">
      <div class="aal-search-top"><div><p class="eyebrow">Search the whole site</p><h2>What do you need?</h2></div><button type="button" class="aal-search-close" aria-label="Close search">${icon('close')}</button></div>
      <form class="aal-search-form" action="/library.html" method="get" role="search">
        <div class="aal-search-input-wrap"><input name="q" type="search" autocomplete="off" spellcheck="true" placeholder="Try pool, family rules, AAC, Maine, IEP, hotel…" aria-label="Search everything"><button type="submit">Search everything</button></div>
        <p class="aal-search-hint">Search titles, summaries, places, tools and the words inside our guides.</p>
      </form>
      <div class="aal-search-chips" aria-label="Popular searches"><button type="button" data-q="family rules">Family rules</button><button type="button" data-q="communication">Communication</button><button type="button" data-q="accessible outings">Accessible outings</button><button type="button" data-q="hotel pool">Hotel + pool</button><button type="button" data-q="IEP school">School + IEP</button><button type="button" data-q="Maine">Maine</button></div>
      <div class="aal-search-results" data-aal-results aria-live="polite"><p class="aal-search-empty">Start typing and the most useful matches will appear here.</p></div>
      <div class="aal-search-footer"><span class="aal-search-status" data-aal-status>Tip: press / from almost anywhere to search.</span><a href="/start-here.html">Browse the visual directory →</a></div>
    </div>`;
  document.body.append(dialog);

  const input = dialog.querySelector('input[name=q]');
  const results = dialog.querySelector('[data-aal-results]');
  const status = dialog.querySelector('[data-aal-status]');
  let data = null;

  const staticItems = [
    {url:'/family-agreements.html',title:'Family agreements',summary:'Communication, choice, short outings, clear handoffs and privacy.',category:'family',format:'Guide',aliases:'family rules house rules internal rules routine agreements'},
    {url:'/little-adventures.html',title:'Little adventures',summary:'An original illustrated New England story with optional read-aloud and a gentle tune.',category:'family',format:'Story',aliases:'kids children fun preppy songs boot wheels videos'},
    {url:'/communication-notes.html',title:'Communication notes and profiles',summary:'Make a written support card, one-page profile or AI-ready prompt.',category:'family',format:'Tool',aliases:'caregiver handoff communication passport notes'},
    {url:'/start-here.html',title:'Start here: the visual directory',summary:'The clearest map of the site: outings, communication, family plans, school, home, style, products, calendar and more.',category:'start here',format:'Directory',aliases:'where do i start site map visual directory icons navigation'},
    {url:'/blog.html',title:'The blog',summary:'Stories, field notes and practical ideas from An AUsome Life.',category:'stories',format:'Blog',aliases:'journal posts articles family notebook'},
    {url:'/library.html',title:'The library',summary:'Every useful guide, place, toolkit, story and advice note in one searchable directory.',category:'library',format:'Directory',aliases:'everything all guides search index'},
    {url:'/favorite-places.html',title:'Favorite places',summary:'New England places with the practical details left in.',category:'outings',format:'Directory',aliases:'outings accessible places new england travel day trips'},
    {url:'/calendar.html',title:'The calendar',summary:'Things to do, seasonal events and outing ideas.',category:'outings',format:'Calendar',aliases:'events what is happening today weekend fall halloween trunk treat'},
    {url:'/little-black-book.html',title:'The little black book',summary:'Brands, businesses, places and organizations we use, love or support.',category:'directory',format:'Directory',aliases:'brands businesses organizations partners links favorite companies'},
    {url:'/family-planning-toolkit.html',title:'Family rules, routines & handoffs',summary:'Leaving-the-house cards, day plans, handoffs and practical family structure.',category:'family',format:'Toolkit',aliases:'family rules house rules routine schedule plan internal rules handoff command center'},
    {url:'/family-command-center-guide.html',title:'A family command center that earns its wall space',summary:'A simple place everyone knows to check for today, tomorrow and the things that are easy to forget.',category:'home',format:'Guide',aliases:'family rules schedule calendar routines household'},
    {url:'/communication-card-generator.html',title:'Communication card maker',summary:'Make a clear, visual communication card quickly.',category:'family',format:'Tool',aliases:'AAC pecs visual choice card non speaking communication picture icon'},
    {url:'/visit-story.html',title:'Visual visit planner',summary:'See the visit first with clear picture steps and editable words.',category:'family',format:'Tool',aliases:'social story outing visual schedule first then visit plan'},
    {url:'/aac-outing-note.html',title:'AAC-friendly outing note',summary:'A short handoff for staff, hosts or activity leaders.',category:'family',format:'Toolkit',aliases:'AAC touchchat communication nonverbal nonspeaking'},
    {url:'/field-notes.html',title:'Practical field notes',summary:'Copyable access requests, hotel questions, communication notes and backup plans.',category:'tools',format:'Field notes',aliases:'access request script words to ask hotel questions plans change'},
    {url:'/profoundly-awesome.html',title:'Profound autism: a whole, interesting life',summary:'High support needs, privacy, preferences, age-respectful choices and ordinary pleasure.',category:'family',format:'Guide',aliases:'profound autism high support needs severe autism dignity'},
    {url:'/topics/advocacy.html',title:'School & advocacy',summary:'Prepare the question. Keep the useful record.',category:'advocacy',format:'Topic',aliases:'IEP school special education meeting records transportation'},
    {url:'/family-wardrobe.html',title:'Family wardrobe',summary:'Comfortable, classic clothes built around what people actually want to wear.',category:'style',format:'Guide',aliases:'clothes sensory wardrobe joggers shoes outfit'},
    {url:'/at-home.html',title:'At home',summary:'Meals, household systems and the small things that make an ordinary day easier.',category:'home',format:'Topic',aliases:'house home organization meals routines'},
    {url:'/product-guides.html',title:'Product guides',summary:'Useful things chosen for real family life.',category:'products',format:'Directory',aliases:'products shopping gear things we bought'},
    {url:'/about.html',title:'Our story',summary:'What An AUsome Life is and the point of view behind it.',category:'about',format:'Page',aliases:'about meet us who are you mission'},
    {url:'/accessibility.html',title:'Accessibility',summary:'How the site approaches access and usability.',category:'site',format:'Page',aliases:'website accessibility disabled screen reader keyboard'},
    {url:'/contact.html',title:'Contact',summary:'Get in touch with An AUsome Life.',category:'site',format:'Page',aliases:'email contact reach us'}
  ];

  let loading = null;
  async function loadData(){
    if (data) return data;
    if (loading) return loading;
    loading = (async()=>{
      try {
        const response=await fetch('/data/site-index.json?v=village-20261003');
        if(!response.ok) throw Error('Search unavailable');
        const rows=await response.json();
        const aliases=new Map(staticItems.map(item=>[item.url,item]));
        const seen=new Set(rows.map(item=>item.url));
        data=[...rows.map(item=>({...aliases.get(item.url),...item,aliases:((aliases.get(item.url)||{}).aliases||'')+' '+(item.aliases||'')})),...staticItems.filter(item=>!seen.has(item.url))];
      } catch (_) { data=staticItems; }
      return data;
    })();
    return loading;
  }

  const scoreItem = (item, words) => {
    const title = fold(item.title); const summary = fold(item.summary); const aliases = fold(item.aliases); const locationText=fold(item.location); const body=fold(item.search);
    let score = 0;
    for (const word of words) {
      if (!word) continue;
      if (title === word) score += 18;
      if (title.startsWith(word)) score += 10;
      if (title.includes(word)) score += 8;
      if (aliases.includes(word)) score += 7;
      if (locationText.includes(word)) score += 6;
      if (summary.includes(word)) score += 4;
      if (body.includes(word)) score += 2;
      if (!(title+' '+summary+' '+aliases+' '+locationText+' '+body+' '+fold(item.category)+' '+fold(item.format)).includes(word)) return -1;
    }
    return score - ((item.minutes || 0) * .02);
  };

  let searchRevision=0;
  async function search(value){
    const revision=++searchRevision;
    const q = value.trim();
    if (!q) { results.innerHTML='<p class="aal-search-empty">Start typing and the most useful matches will appear here.</p>'; status.textContent='Tip: press / from almost anywhere to search.'; return; }
    status.textContent='Searching the site…';
    const words=fold(q).split(/\s+/).filter(Boolean); const rows=await loadData();
    if(revision!==searchRevision)return;
    const hits=rows.map(item=>({item,score:scoreItem(item,words)})).filter(x=>x.score>=0).sort((a,b)=>b.score-a.score || (a.item.title||'').localeCompare(b.item.title||''));
    status.textContent=hits.length ? `${hits.length} ${hits.length===1?'match':'matches'}` : 'No close match yet';
    results.innerHTML = hits.length ? hits.map(({item})=>`<a class="aal-search-result" href="${esc(item.url)}"><span class="aal-result-kind">${esc(item.format || item.category || 'Page')}</span><span><h3>${esc(item.title)}</h3><p>${esc(item.summary || item.location || '')}</p></span><span class="aal-go" aria-hidden="true">→</span></a>`).join('') : `<p class="aal-search-empty">No close match for “${esc(q)}.” Try fewer words, or browse All sections.</p>`;
  }

  dialog.querySelector('form').addEventListener('submit',e=>{e.preventDefault();clearTimeout(debounce);search(input.value)});
  let debounce;
  input.addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(()=>search(input.value),90)});
  dialog.querySelectorAll('[data-q]').forEach(button=>button.addEventListener('click',()=>{input.value=button.dataset.q;search(input.value);input.focus()}));
  dialog.querySelector('.aal-search-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
  dialog.addEventListener('close',()=>{document.documentElement.style.overflow='';});

  function openSearch(seed=''){
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open','');
    document.documentElement.style.overflow='hidden';
    if(seed){input.value=seed;search(seed)}
    requestAnimationFrame(()=>input.focus());
    loadData();
  }
  document.querySelectorAll('[data-aal-open-search]').forEach(button=>button.addEventListener('click',()=>openSearch()));
  document.querySelectorAll('.nav-search,a[href="/library.html#library-search"]').forEach(link=>link.addEventListener('click',e=>{e.preventDefault();openSearch()}));
  document.addEventListener('keydown',e=>{
    const target=e.target; const typing=target && (target.matches('input,textarea,select') || target.isContentEditable);
    if ((e.metaKey||e.ctrlKey) && e.key.toLowerCase()==='k'){e.preventDefault();openSearch();return;}
    if (!typing && e.key==='/'){e.preventDefault();openSearch();}
    if (e.key==='Escape' && dialog.open) dialog.close();
  });
})();
