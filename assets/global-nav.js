/* Progressive site navigation. All destinations remain usable without JavaScript. */
(() => {
  'use strict';
  if(window.__AAL_GLOBAL_NAV__)return;
  window.__AAL_GLOBAL_NAV__=true;
  const addAsset=(kind,path)=>{
    const attr=kind==='script'?'src':'href';
    if(document.querySelector(`${kind}[${attr}*="${path}"]`))return;
    const node=document.createElement(kind);node.setAttribute(attr,path+'?v=20261026-wayfinding');
    if(kind==='link')node.rel='stylesheet';else node.defer=true;
    document.head.append(node);
  };
  addAsset('link','/assets/access-tools.css');addAsset('script','/assets/access-tools.js');
  addAsset('link','/assets/site-experience.css');addAsset('script','/assets/analytics.js');
  addAsset('script','/assets/story-share.js');
  if(document.body.classList.contains('journal-place'))addAsset('script','/assets/journal-place.js');
  if(document.querySelector('.ellis-review'))addAsset('link','/assets/editorial-art-direction.css');
  const fold=value=>(value||'').toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const esc=value=>String(value||'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const menu=document.querySelector('[data-site-menu]');
  const closeMenu=()=>{if(menu)menu.open=false;};
  document.addEventListener('click',event=>{if(menu?.open&&!menu.contains(event.target))closeMenu();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&menu?.open){closeMenu();menu.querySelector('summary').focus();}});
  const dialog=document.createElement('dialog');dialog.className='aal-search-dialog';dialog.setAttribute('aria-labelledby','aal-search-title');
  dialog.innerHTML=`<div class="aal-search-shell"><div class="aal-search-top"><div><p class="eyebrow">The whole field guide</p><h2 id="aal-search-title">Find your good thing.</h2></div><button class="aal-search-close" type="button" aria-label="Close search">Close</button></div><form role="search"><label for="aal-search-input">Search stories, places, guides & tools</label><div class="aal-search-input-wrap"><input id="aal-search-input" type="search" name="q" placeholder="Try Maine, pool, picture cards…" autocomplete="off"><button type="submit">Search</button></div></form><div class="aal-search-chips" aria-label="Try a search"><button type="button" data-q="Maine">Maine</button><button type="button" data-q="picture cards">Picture cards</button><button type="button" data-q="pool">A pool day</button><button type="button" data-q="caregiver">Caregiver support</button></div><p data-aal-status role="status" aria-live="polite">Search in your own words.</p><div class="aal-search-results" data-aal-results></div><div class="aal-search-footer"><a href="/library.html" data-all-results>Open the full library</a><a href="/site-map.html">Browse every page</a></div></div>`;
  document.body.append(dialog);
  const input=dialog.querySelector('input'),results=dialog.querySelector('[data-aal-results]'),status=dialog.querySelector('[data-aal-status]'),allResults=dialog.querySelector('[data-all-results]');
  let data=null,loading=null,limited=false,revision=0,debounce,returnFocus,oldOverflow='';
  const staticItems = [
    {url:'/family-agreements.html',title:'Family agreements',summary:'Communication, choice, short outings, clear handoffs and privacy.',category:'family',format:'Guide',aliases:'family rules house rules internal rules routine agreements'},
    {url:'/little-adventures.html',title:'Little adventures',summary:'An original illustrated New England story with optional read-aloud and a gentle tune.',category:'family',format:'Story',aliases:'kids children fun preppy songs boot wheels videos'},
    {url:'/communication-notes.html',title:'Communication notes and profiles',summary:'Make a written support card, one-page profile or AI-ready prompt.',category:'family',format:'Tool',aliases:'caregiver handoff communication passport notes'},
    {url:'/start-here.html',title:'Start here: the visual directory',summary:'The clearest map of the site: outings, communication, family plans, school, home, style, products, calendar and more.',category:'start here',format:'Directory',aliases:'where do i start site map visual directory icons navigation'},
    {url:'/blog.html',title:'The journal',summary:'Stories, field notes and practical ideas from An AUsome Life.',category:'stories',format:'Blog',aliases:'journal posts articles family notebook'},
    {url:'/library.html',title:'The library',summary:'Every useful guide, place, toolkit, story and advice note in one searchable directory.',category:'library',format:'Directory',aliases:'everything all guides search index'},
    {url:'/favorite-places.html',title:'Favorite places',summary:'New England places with the practical details left in.',category:'outings',format:'Directory',aliases:'outings accessible places new england travel day trips'},
    {url:'/calendar.html',title:'The calendar',summary:'Things to do, seasonal events and outing ideas.',category:'outings',format:'Calendar',aliases:'events what is happening today weekend fall halloween trunk treat'},
    {url:'/little-black-book.html',title:'The little black book',summary:'Brands, businesses, places and organizations we use, love or support.',category:'directory',format:'Directory',aliases:'brands businesses organizations partners links favorite companies'},
    {url:'/family-roles.html',title:'Family & caregiver support',summary:'Practical help for sharing care, days out, time for yourself and real family stories.',category:'family',format:'Start here',aliases:'caregiver help support respite self care mother father grandparent sibling family roles'},
    {url:'/family-planning-toolkit.html',title:'Day plans & household handoffs',summary:'Fill in, copy or print a leaving-the-house card, day plan or household handoff.',category:'family',format:'Toolkit',aliases:'family rules house rules routine schedule plan internal rules handoff command center'},
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


  const getJSON=async url=>{const response=await fetch(url);if(!response.ok)throw Error('Search unavailable');return response.json();};
  async function loadData(){
    if(data)return data;if(loading)return loading;
    loading=(async()=>{
      try {
        let rows;
        try {const files=await getJSON('/data/site-index-manifest.json?v=20261026-wayfinding');rows=(await Promise.all(files.map(getJSON))).flat();}
        catch(_){rows=await getJSON('/data/site-index.json?v=20261026-wayfinding');}
        const aliases=new Map(staticItems.map(row=>[row.url,row]));
        const seen=new Set(rows.map(row=>row.url));
        data=[...rows.map(row=>({...aliases.get(row.url),...row,aliases:aliases.get(row.url)?.aliases||''})),...staticItems.filter(row=>!seen.has(row.url))];limited=false;return data;
      }catch(_){limited=true;return staticItems;}finally{loading=null;}
    })();return loading;
  }
  function score(item,words){
    const title=fold(item.title),summary=fold(item.summary),aliases=fold(item.aliases),body=fold(item.search),hay=title+' '+summary+' '+aliases+' '+body;
    if(!words.every(word=>hay.includes(word)))return -1;
    return words.reduce((total,word)=>total+(title.includes(word)?10:0)+(summary.includes(word)?4:0)+(aliases.includes(word)?6:0),0);
  }
  async function search(){
    const current=++revision,q=input.value.trim();
    allResults.href='/library.html'+(q?'?q='+encodeURIComponent(q):'');
    if(!q){results.replaceChildren();status.textContent='Search in your own words.';return;}
    status.textContent='Searching…';const rows=await loadData();if(current!==revision)return;
    const words=fold(q).split(/\s+/).filter(Boolean),hits=rows.map(item=>({item,score:score(item,words)})).filter(row=>row.score>=0).sort((a,b)=>b.score-a.score||a.item.title.localeCompare(b.item.title));
    status.textContent=(limited?'Full search is temporarily unavailable. Showing key pages only. ':'' )+(hits.length?hits.length+' matches'+(hits.length>30?' · first 30 shown':''):'No close match. Try fewer words or browse the site map.');
    results.innerHTML=hits.slice(0,30).map(({item})=>`<a class="aal-search-result" href="${esc(item.url)}"><span>${esc(item.format||'Page')}</span><div><h3>${esc(item.title)}</h3><p>${esc(item.summary)}</p></div></a>`).join('');
  }
  function openSearch(event){
    if(event&&(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey))return;
    if(typeof dialog.showModal!=='function')return;
    event?.preventDefault();if(dialog.open){input.focus();return;}
    returnFocus=document.activeElement;oldOverflow=document.documentElement.style.overflow;closeMenu();
    dialog.showModal();document.documentElement.style.overflow='hidden';input.focus();loadData();
  }
  document.querySelectorAll('[data-site-search],.nav-search,[data-aal-open-search]').forEach(node=>node.addEventListener('click',openSearch));
  dialog.querySelector('form').addEventListener('submit',event=>{event.preventDefault();clearTimeout(debounce);search();});
  input.addEventListener('input',()=>{clearTimeout(debounce);++revision;debounce=setTimeout(search,120);});
  dialog.querySelectorAll('[data-q]').forEach(button=>button.addEventListener('click',()=>{clearTimeout(debounce);input.value=button.dataset.q;search();input.focus();}));
  dialog.querySelector('.aal-search-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{const r=dialog.getBoundingClientRect();if(event.target===dialog&&(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom))dialog.close();});
  dialog.addEventListener('close',()=>{++revision;clearTimeout(debounce);document.documentElement.style.overflow=oldOverflow;returnFocus?.focus({preventScroll:true});});
  document.addEventListener('keydown',event=>{
    if([...document.querySelectorAll('dialog[open]')].some(other=>other!==dialog))return;
    const typing=event.target?.matches('input,textarea,select,[contenteditable="true"]');
    if(((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k')||(!typing&&!event.altKey&&event.key==='/')){event.preventDefault();openSearch();}
  });
})();
