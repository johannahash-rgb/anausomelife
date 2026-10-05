/* Add a brand in brand-registry.json; every banner reads the same registry. */
(()=>{'use strict';
const roots=[...document.querySelectorAll('[data-brand-banner]')];if(!roots.length)return;
const source=document.currentScript?.dataset.registry||'/assets/brand-registry.json?v=20261005-favorites';
const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el};
const readCats=value=>(value||'all').split(/[ ,]+/).filter(Boolean);
fetch(source,{credentials:'same-origin'}).then(r=>{if(!r.ok)throw Error('Brand registry unavailable');return r.json()}).then(data=>{
 roots.forEach((root,index)=>{
  if(root.dataset.brandInitialized)return;root.dataset.brandInitialized='true';
  const allowed=readCats(root.dataset.categories),filters=root.dataset.filters==='true';
  const permitted=data.brands.filter(b=>allowed.includes('all')||b.categories.some(c=>allowed.includes(c)));
  if(!permitted.length)return;
  root.classList.add('aal-brands');root.replaceChildren();
  const tools=node('div','aal-brand-tools'),filterBar=node('div','aal-brand-filters'),controls=node('div','aal-brand-controls'),count=node('span','aal-brand-count'),prev=node('button','','←'),pause=node('button','','Pause'),next=node('button','','→');
  filterBar.setAttribute('aria-label','Filter brands by category');
  [prev,pause,next].forEach(b=>b.type='button');prev.setAttribute('aria-label','Scroll to previous brands');next.setAttribute('aria-label','Scroll to next brands');
  const viewport=node('div','aal-brand-viewport'),rail=node('div','aal-brand-rail');viewport.id='aal-brand-viewport-'+index;viewport.tabIndex=0;viewport.setAttribute('role','region');viewport.setAttribute('aria-label',root.dataset.label||'Illustrated brands and places');viewport.append(rail);[prev,pause,next].forEach(b=>b.setAttribute('aria-controls',viewport.id));
  controls.append(count,prev,pause,next);if(filters)tools.append(filterBar);tools.append(controls);root.append(tools,viewport);
  const hint=node('p','aal-brand-hint','Original editorial sketches. Swipe or use the arrows to browse.');root.append(hint);
  let selected='all',isPaused=false,hovering=false,focused=false,visible=false,last=0,holdUntil=0,cycleWidth=0,frame=0,canLoop=false,carry=0;
  function updatePause(){const stopped=isPaused||reduced.matches;pause.textContent=stopped?'Play':'Pause';pause.setAttribute('aria-label',stopped?'Start automatic brand scrolling':'Pause automatic brand scrolling');pause.setAttribute('aria-pressed',String(stopped));if(reduced.matches){pause.hidden=true;hint.textContent='Original editorial sketches. Swipe or use the arrows to browse.'}else{pause.hidden=false}}
  function measure(){const first=rail.firstElementChild;cycleWidth=first?first.getBoundingClientRect().width:0;canLoop=cycleWidth>viewport.clientWidth;const clone=rail.children[1];if(clone)clone.hidden=!canLoop;}
  function render(){const brands=permitted.filter(b=>selected==='all'||b.categories.includes(selected));const list=node('ul','aal-brand-set');list.setAttribute('aria-label','Brand names');brands.forEach(b=>{const item=node('li','aal-brand-entry');if(b.image){const img=new Image();img.src=b.image;img.alt=b.alt||'';img.width=256;img.height=256;img.loading='lazy';img.decoding='async';item.append(img)}else{item.classList.add('aal-brand-entry-text')}item.append(node('span','aal-brand-label',b.name));if(b.note)item.append(node('span','aal-brand-note',b.note));list.append(item)});const clone=list.cloneNode(true);clone.setAttribute('aria-hidden','true');clone.querySelectorAll('img').forEach(img=>img.alt='');rail.replaceChildren(list,clone);viewport.scrollLeft=0;count.textContent=brands.length+' '+(brands.length===1?'name':'names');filterBar.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.category===selected)));measure();last=0;}
  if(filters)data.categories.filter(c=>c.id==='all'||permitted.some(b=>b.categories.includes(c.id))).forEach(c=>{const b=node('button','',c.label);b.type='button';b.dataset.category=c.id;b.setAttribute('aria-pressed',String(c.id===selected));b.addEventListener('click',()=>{selected=c.id;holdUntil=performance.now()+2500;render()});filterBar.append(b)});
  pause.addEventListener('click',()=>{isPaused=!isPaused;updatePause()});
  function manual(direction){holdUntil=performance.now()+5000;if(direction<0&&viewport.scrollLeft<1&&canLoop)viewport.scrollLeft=cycleWidth;viewport.scrollBy({left:direction*Math.max(168,viewport.clientWidth*.68),behavior:reduced.matches?'auto':'smooth'})}
  prev.addEventListener('click',()=>manual(-1));next.addEventListener('click',()=>manual(1));
  viewport.addEventListener('pointerdown',()=>{holdUntil=performance.now()+7000});viewport.addEventListener('wheel',()=>{holdUntil=performance.now()+5000},{passive:true});viewport.addEventListener('keydown',()=>{holdUntil=performance.now()+7000});
  root.addEventListener('mouseenter',()=>hovering=true);root.addEventListener('mouseleave',()=>{hovering=false;last=0});viewport.addEventListener('focusin',()=>focused=true);viewport.addEventListener('focusout',e=>{if(!viewport.contains(e.relatedTarget)){focused=false;last=0}});
  viewport.addEventListener('scroll',()=>{if(canLoop&&viewport.scrollLeft>=cycleWidth)viewport.scrollLeft-=cycleWidth},{passive:true});
  new ResizeObserver(measure).observe(viewport);new IntersectionObserver(es=>{visible=es[0].isIntersecting;last=0},{rootMargin:'120px'}).observe(root);
  function tick(now){if(!root.isConnected){cancelAnimationFrame(frame);return}const dt=last?Math.min(now-last,60):0;last=now;if(visible&&!document.hidden&&!isPaused&&!reduced.matches&&!hovering&&!focused&&now>holdUntil&&canLoop){carry+=dt*.022;const step=Math.floor(carry);if(step){viewport.scrollLeft+=step;carry-=step}}else carry=0;frame=requestAnimationFrame(tick)}
  render();updatePause();reduced.addEventListener('change',()=>{updatePause();last=0});frame=requestAnimationFrame(tick);
 });
}).catch(error=>{console.warn(error.message);roots.forEach(root=>root.classList.add('aal-brands-fallback'))});
})();
