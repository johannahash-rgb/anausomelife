/* No analytics. Search stays in the browser. */
(() => {
'use strict';
const fold = value => value.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
const main = document.querySelector('[data-library]');
if (main) {
 const form=main.querySelector('form'),input=form.elements.q,topic=form.elements.topic,type=form.elements.type,sort=form.elements.sort,status=main.querySelector('[data-result-status]'),box=main.querySelector('.library-results'),more=main.querySelector('.load-more'),empty=main.querySelector('.empty-state');
 const cards=[...box.querySelectorAll('.index-card')], firstOrder=new Map(cards.map((c,i)=>[c,i])); let index=new Map(),limit=18,indexReady=false;main.setAttribute('aria-busy','true');
 const json=url=>fetch(url).then(r=>{if(!r.ok)throw Error();return r.json()});
 Promise.all([json('/data/library.json'),json('/data/search-manifest.json').then(files=>Promise.all(files.map(file=>json(file))))]).then(([data,chunks])=>{index=new Map(data.map(a=>[a.url,a]));for(const row of chunks.flat()){const a=index.get(row.url);if(a)a.search=row.search;}indexReady=true;main.setAttribute('aria-busy','false');apply(false);}).catch(()=>{main.setAttribute('aria-busy','false');indexReady=true;apply(false);const note=document.createElement('p');note.className='search-load-note';note.textContent='Full-text search could not load. Titles, summaries and filters still work.';form.after(note);});
 function readUrl(){const p=new URLSearchParams(location.search);input.value=p.get('q')||'';topic.value=p.has('topic')?p.get('topic'):main.dataset.defaultTopic||'';type.value=p.get('type')||'';sort.value=p.get('sort')||'recommended';limit=18;}
 function apply(urlMode){const words=fold(input.value.trim()).split(/\s+/).filter(Boolean);let hits=[];for(const c of cards){const a=index.get(c.dataset.url),hay=fold(c.textContent+' '+(a?.search||'')+' '+(a?.topics||[]).join(' '));const match=(!topic.value||c.dataset.category===topic.value)&&(!type.value||c.dataset.format===type.value)&&words.every(w=>hay.includes(w));if(match)hits.push(c);c.hidden=true;}hits.sort((a,b)=>sort.value==='az'?a.querySelector('h3').textContent.localeCompare(b.querySelector('h3').textContent):sort.value==='short'?((index.get(a.dataset.url)?.minutes||999)-(index.get(b.dataset.url)?.minutes||999)):firstOrder.get(a)-firstOrder.get(b));for(const [i,c] of hits.entries()){box.append(c);c.hidden=i>=limit;}status.textContent=hits.length+' '+(hits.length===1?'useful read':'useful reads')+(hits.length>limit?' · showing '+Math.min(limit,hits.length):'')+(!indexReady?' · full-text search loading':'');empty.hidden=hits.length>0;more.hidden=hits.length<=limit;if(urlMode){const p=new URLSearchParams();if(input.value.trim())p.set('q',input.value.trim());if(topic.value)p.set('topic',topic.value);if(type.value)p.set('type',type.value);if(sort.value!=='recommended')p.set('sort',sort.value);const u=location.pathname+(p.size?'?'+p:'')+location.hash;history[urlMode==='push'?'pushState':'replaceState']({},'',u);}}
 form.addEventListener('submit',e=>{e.preventDefault();limit=18;apply('push')});input.addEventListener('input',()=>{limit=18;apply('replace')});[topic,type,sort].forEach(el=>el.addEventListener('change',()=>{limit=18;apply('push')}));
 function clear(){input.value='';topic.value='';type.value='';sort.value='recommended';limit=18;apply('push');input.focus();}
 form.addEventListener('reset',e=>{e.preventDefault();clear()});main.querySelector('[data-clear-all]').addEventListener('click',()=>{if(main.dataset.defaultTopic){location.href='/library.html';return}clear()});main.querySelector('[data-load-more]').addEventListener('click',()=>{const previous=limit;limit+=18;apply(false);const shown=[...box.children].filter(c=>!c.hidden);shown[previous]?.querySelector('a')?.focus()});window.addEventListener('popstate',()=>{readUrl();apply(false)});readUrl();apply(false);
}
const places=document.querySelector('[data-places]');if(places){const form=places.querySelector('form'),q=form.elements.q,state=form.elements.state,kind=form.elements.kind,rows=[...places.querySelectorAll('.place-row')],status=places.querySelector('[role=status]');function apply(){const terms=fold(q.value.trim()).split(/\s+/).filter(Boolean);let n=0;for(const r of rows){const kinds=(r.dataset.placeKind||'').split(/\s+/);const match=(!state.value||r.dataset.placeState.includes(state.value))&&(!kind.value||kinds.includes(kind.value))&&terms.every(t=>fold(r.textContent).includes(t));r.hidden=!match;if(match)n++;}status.textContent=n+' '+(n===1?'place':'places')+' to know';const empty=places.querySelector('.place-empty');if(empty)empty.hidden=n>0;const p=new URLSearchParams();if(q.value)p.set('q',q.value);if(state.value)p.set('state',state.value);if(kind.value)p.set('kind',kind.value);history.replaceState({},'',location.pathname+(p.size?'?'+p:''));}const p=new URLSearchParams(location.search);q.value=p.get('q')||'';state.value=p.get('state')||'';kind.value=p.get('kind')||'';q.addEventListener('input',apply);state.addEventListener('change',apply);kind.addEventListener('change',apply);form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('reset',e=>{e.preventDefault();q.value='';state.value='';kind.value='';apply();q.focus()});apply();}
document.querySelectorAll('[data-print]').forEach(b=>{if(!document.querySelector('script[src*="site.js"]'))b.addEventListener('click',()=>window.print())});
// Visual-first navigation and readable editorial cues.
const mastNav=document.querySelector('.mag-masthead nav');
if(mastNav&&!mastNav.querySelector('a[href="/blog.html"]')){
 const blog=document.createElement('a');blog.href='/blog.html';blog.textContent='Blog';
 const library=mastNav.querySelector('a[href="/library.html"]');mastNav.insertBefore(blog,library||mastNav.firstChild);
}
document.querySelectorAll('.visual-story .visual-step').forEach((step,i)=>{
 if(step.querySelector('.visual-step-icon'))return;
 const icons=['/assets/visuals/getting-there.svg','/assets/visuals/arriving.svg','/assets/visuals/choose.svg','/assets/visuals/break.svg','/assets/visuals/leaving.svg'];
 const img=document.createElement('img');img.src=icons[i%icons.length];img.alt='';img.className='visual-step-icon';step.prepend(img);
});
// Retain links to the original homepage's established practical notes.
if(location.pathname==='/'||location.pathname==='/index.html'){const legacy=['resources','guide','access-request','hotel-questions','communication','respect','when-plans-change','make-a-plan','everyday-life','practical-style','journal','standards'];if(legacy.includes(location.hash.slice(1)))location.replace('/field-notes.html'+location.hash);}
})();


// 2026-10-03 sortable black book
(() => {
 const book=document.querySelector('[data-black-book]');
 if(book){
  const form=book.querySelector('.directory-controls'),q=form.elements.q,kind=form.elements.kind,relationship=form.elements.relationship,sort=form.elements.sort;
  const cards=[...book.querySelectorAll('[data-directory-card]')],sections=[...book.querySelectorAll('[data-directory-section]')],status=book.querySelector('[role=status]'),empty=book.querySelector('.directory-empty');
  const original=new Map(cards.map((c,i)=>[c,i]));
  const foldBook=v=>(v||'').toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  function apply(){
   const terms=foldBook(q.value.trim()).split(/\s+/).filter(Boolean);let shown=0;
   for(const c of cards){
    const kinds=(c.dataset.kind||'').split(/\s+/),hay=foldBook(c.textContent+' '+(c.dataset.location||'')+' '+(c.dataset.name||''));
    const ok=(!kind.value||kinds.includes(kind.value))&&(!relationship.value||c.dataset.relationship===relationship.value)&&terms.every(t=>hay.includes(t));
    c.hidden=!ok;if(ok)shown++;
   }
   for(const section of sections){
    const grid=section.querySelector('.directory-grid');if(!grid)continue;
    const sectionCards=[...grid.querySelectorAll('[data-directory-card]')];
    sectionCards.sort((a,b)=>sort.value==='az'?(a.dataset.name||'').localeCompare(b.dataset.name||''):sort.value==='za'?(b.dataset.name||'').localeCompare(a.dataset.name||''):original.get(a)-original.get(b));
    sectionCards.forEach(c=>grid.append(c));section.hidden=!sectionCards.some(c=>!c.hidden);
   }
   status.textContent=shown+' '+(shown===1?'entry':'entries')+' in the little black book';empty.hidden=shown>0;
   const p=new URLSearchParams();if(q.value)p.set('q',q.value);if(kind.value)p.set('kind',kind.value);if(relationship.value)p.set('relationship',relationship.value);if(sort.value!=='featured')p.set('sort',sort.value);
   history.replaceState({},'',location.pathname+(p.size?'?'+p:'')+location.hash);
  }
  const p=new URLSearchParams(location.search);q.value=p.get('q')||'';kind.value=p.get('kind')||'';relationship.value=p.get('relationship')||'';sort.value=p.get('sort')||'featured';
  q.addEventListener('input',apply);[kind,relationship,sort].forEach(el=>el.addEventListener('change',apply));form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('reset',e=>{e.preventDefault();q.value='';kind.value='';relationship.value='';sort.value='featured';apply();q.focus()});apply();
 }
 const nav=document.querySelector('.mag-masthead nav');
 if(nav&&!nav.querySelector('a[href="/little-black-book.html"]')){
  const a=document.createElement('a');a.href='/little-black-book.html';a.textContent='The black book';
  const cal=nav.querySelector('a[href="/calendar.html"]');nav.insertBefore(a,cal||nav.querySelector('.nav-search'));
 }
})();

/* Shared site-wide wayfinding + universal search */
(() => {
  if (document.querySelector('script[data-aal-global-nav]')) return;
  const s=document.createElement('script');
  s.src='/assets/global-nav.js?v=editorial-20261003';
  s.dataset.aalGlobalNav='true';
  s.async=false;
  document.head.append(s);
})();
