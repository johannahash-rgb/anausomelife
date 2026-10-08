(() => {
'use strict';
const form=document.getElementById('cart-filters');if(!form)return;
const $=id=>document.getElementById(id),rows=Array.from(document.querySelectorAll('.cart-row')),list=document.querySelector('.cart-list');
const states={CT:'Connecticut',ME:'Maine',MA:'Massachusetts',NH:'New Hampshire',RI:'Rhode Island',VT:'Vermont'};
const names=['q','state','chain','status','sort'],mapControls=Array.from(document.querySelectorAll('[data-map-state]'));
const value=name=>form.elements.namedItem(name).value;
const normalize=s=>s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[’']/g,'').replace(/[^a-z0-9]+/g,' ').trim();
const statusNames={policy:'Retailer policy',chain:'Chain report',historical:'Older local report'};
let current=[],dragged=false;
for(const row of rows){row.dataset.searchTown=row.querySelector('.cart-town').textContent.trim().toLowerCase();row.dataset.normalSearch=normalize(row.dataset.search);}
function loadURL(){const params=new URLSearchParams(location.search);for(const name of names){const el=form.elements.namedItem(name),v=params.get(name)|| (name==='sort'?'state':'');if(el.tagName==='SELECT'&&!Array.from(el.options).some(o=>o.value===v)){el.value=name==='sort'?'state':'';}else el.value=v;}}
function apply(updateURL=true){
 const words=normalize(value('q')).split(' ').filter(Boolean),state=value('state'),totals={};current=[];
 for(const row of rows){const other=words.every(w=>row.dataset.normalSearch.includes(w))&&['chain','status'].every(n=>!value(n)||value(n)===row.dataset[n]);if(other)totals[row.dataset.state]=(totals[row.dataset.state]||0)+1;row.hidden=!(other&&(!state||row.dataset.state===state));if(!row.hidden)current.push(row);}
 const order=value('sort'),key=r=>order==='town'?[r.dataset.searchTown,r.dataset.chain]:order==='retailer'?[r.dataset.chain,states[r.dataset.state],r.dataset.searchTown]:[states[r.dataset.state],r.dataset.searchTown,r.dataset.chain];
 rows.slice().sort((a,b)=>key(a).join('|').localeCompare(key(b).join('|'))).forEach(row=>list.append(row));current=Array.from(list.children).filter(row=>!row.hidden);
 $('cart-count').textContent=current.length+' '+(current.length===1?'store':'stores')+' to call'+(state?' in '+states[state]:'');$('cart-empty').hidden=current.length>0;
 for(const control of mapControls){const active=control.dataset.mapState===state;control.classList.toggle('is-selected',active);control.setAttribute(control.tagName==='BUTTON'?'aria-pressed':'aria-current',String(active));if(control.classList.contains('cart-map-state')){const st=control.dataset.mapState;control.setAttribute('aria-label',states[st]+': '+(totals[st]||0)+' matching listings');control.querySelector('title').textContent=states[st]+' · '+(totals[st]||0)+' matching listings';}}
 document.querySelectorAll('[data-state-count]').forEach(b=>{const n=b.dataset.stateCount?(totals[b.dataset.stateCount]||0):Object.values(totals).reduce((a,b)=>a+b,0);b.textContent=n+' '+(n===1?'listing':'listings');});
 $('cart-map-selection').textContent=state?states[state]+' selected':'All six states';$('cart-results-jump').textContent='View '+current.length+' '+(current.length===1?'store':'stores');
 $('cart-download').disabled=!current.length;
 const chips=$('cart-active-filters');chips.replaceChildren();for(const name of ['q','state','chain','status']){if(!value(name))continue;const button=document.createElement('button');button.type='button';const label=name==='state'?states[value(name)]:name==='status'?statusNames[value(name)]:value(name);button.textContent=label+' ×';button.setAttribute('aria-label','Remove '+label+' filter');button.addEventListener('click',()=>{form.elements.namedItem(name).value='';apply();form.elements.namedItem(name).focus();});chips.append(button);}
 if(updateURL){const url=new URL(location.href);if(rows.some(r=>'#'+r.id===url.hash))url.hash='';for(const name of names){const v=value(name).trim();if(v&&!(name==='sort'&&v==='state'))url.searchParams.set(name,v);else url.searchParams.delete(name);}history.replaceState(null,'',url);}
}
function clear(){for(const n of names)form.elements.namedItem(n).value=n==='sort'?'state':'';apply();resetMap();}
for(const control of mapControls)control.addEventListener('click',event=>{event.preventDefault();if(dragged)return;form.elements.namedItem('state').value=control.dataset.mapState;apply();});
form.addEventListener('submit',event=>{event.preventDefault();apply();$('cart-results').focus();});
form.addEventListener('input',()=>apply());form.addEventListener('change',()=>apply());form.addEventListener('reset',event=>{event.preventDefault();clear();});
$('cart-empty-reset').addEventListener('click',()=>{clear();$('cart-query').focus();});
window.addEventListener('popstate',()=>{loadURL();apply(false);});
$('cart-results-jump').addEventListener('click',()=>{requestAnimationFrame(()=>$('cart-results').focus());});
$('cart-print').addEventListener('click',()=>window.print());
async function copy(text,button,message){try{await navigator.clipboard.writeText(text);$('cart-feedback').textContent=message;const old=button.textContent;button.textContent='Copied';setTimeout(()=>button.textContent=old,2200);}catch{let input=$('cart-copy-fallback');if(!input){input=document.createElement('input');input.id='cart-copy-fallback';input.className='cart-link-fallback';input.readOnly=true;button.after(input);}input.value=text;input.setAttribute('aria-label','Select and copy this text');input.focus();input.select();$('cart-feedback').textContent='Select and copy the text shown.';}}
$('cart-share').addEventListener('click',event=>copy(location.href,event.currentTarget,'Search link copied.'));
$('cart-copy-script').addEventListener('click',event=>copy($('cart-call-script').textContent,event.currentTarget,'Call-ahead script copied.'));
$('cart-download').addEventListener('click',()=>{
 const fields=['Store','Town and state','Address','Phone','Evidence','Source checked / confirmation','Store details','Directions'];
 const records=current.map(r=>[r.querySelector('h3').textContent,r.querySelector('.cart-town').textContent,r.querySelector('.cart-address').textContent,r.querySelector('a[href^="tel:"]').textContent.replace(/^Call /,''),r.querySelector('.cart-label').textContent,r.querySelector('.cart-evidence .cart-small').innerText||r.querySelector('.cart-evidence .cart-small').textContent,r.querySelector('.cart-actions a:nth-child(3)').href,r.querySelector('.cart-actions a:nth-child(2)').href]);
 const cell=v=>'"'+String(v).replace(/"/g,'""')+'"',csv=[fields,...records].map(r=>r.map(cell).join(',')).join('\r\n');
 const url=URL.createObjectURL(new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='carolines-cart-'+(value('state')||'new-england').toLowerCase()+'-results.csv';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);$('cart-feedback').textContent=current.length+' listings downloaded. Call ahead to confirm availability.';
});
// Geographic state outlines remain authoritative; no store coordinates are inferred.
const svg=document.querySelector('.cart-state-map'),base={x:0,y:0,w:700,h:660};let view={...base},pointer=null;
function draw(){svg.setAttribute('viewBox',`${view.x} ${view.y} ${view.w} ${view.h}`);const zoomed=view.w<700;svg.classList.toggle('is-zoomed',zoomed);$('cart-zoom-out').disabled=!zoomed;$('cart-zoom-in').disabled=view.w<=140;$('cart-map-reset').disabled=!zoomed;}
function resetMap(){view={...base};draw();}
function clamp(){view.x=Math.max(0,Math.min(700-view.w,view.x));view.y=Math.max(0,Math.min(660-view.h,view.y));}
function zoom(factor){let cx=view.x+view.w/2,cy=view.y+view.h/2;const selected=svg.querySelector('.cart-map-state.is-selected path');if(factor<1&&selected){const box=selected.getBBox();cx=box.x+box.width/2;cy=box.y+box.height/2;}view.w=Math.max(140,Math.min(700,view.w*factor));view.h=view.w*660/700;view.x=cx-view.w/2;view.y=cy-view.h/2;clamp();draw();}
$('cart-zoom-in').addEventListener('click',()=>zoom(.65));$('cart-zoom-out').addEventListener('click',()=>zoom(1/.65));$('cart-map-reset').addEventListener('click',resetMap);
svg.addEventListener('keydown',event=>{if(event.key==='Escape'){resetMap();return;}if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)||view.w===700)return;event.preventDefault();const step=view.w*.13;view.x+=(event.key==='ArrowRight'?step:event.key==='ArrowLeft'?-step:0);view.y+=(event.key==='ArrowDown'?step:event.key==='ArrowUp'?-step:0);clamp();draw();});
svg.addEventListener('pointerdown',event=>{dragged=false;if(view.w===700||event.button!==0)return;pointer={id:event.pointerId,x:event.clientX,y:event.clientY,vx:view.x,vy:view.y};});
svg.addEventListener('pointermove',event=>{if(!pointer||pointer.id!==event.pointerId)return;const dx=event.clientX-pointer.x,dy=event.clientY-pointer.y;if(Math.abs(dx)+Math.abs(dy)>8){dragged=true;svg.setPointerCapture(event.pointerId);svg.classList.add('is-dragging');}if(!dragged)return;const rect=svg.getBoundingClientRect(),scale=Math.max(view.w/rect.width,view.h/rect.height);view.x=pointer.vx-dx*scale;view.y=pointer.vy-dy*scale;clamp();draw();});
function release(){pointer=null;svg.classList.remove('is-dragging');setTimeout(()=>dragged=false,0);}svg.addEventListener('pointerup',release);svg.addEventListener('pointercancel',release);
if(window.matchMedia('(max-width:760px)').matches)$('browse-map').open=false;
loadURL();apply(false);draw();
// A shared store link reveals its record even when an old filter would hide it.
const target=location.hash.slice(1),linked=rows.find(r=>r.id===target);if(linked){if(linked.hidden){for(const n of names)form.elements.namedItem(n).value=n==='sort'?'state':'';apply();}requestAnimationFrame(()=>linked.scrollIntoView({block:'start'}));}
})();
