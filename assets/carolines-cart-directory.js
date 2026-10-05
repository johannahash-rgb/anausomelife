(() => {
'use strict';
const form=document.getElementById('cart-filters');if(!form)return;
const rows=Array.from(document.querySelectorAll('.cart-row'));
const list=document.querySelector('.cart-list');
const count=document.getElementById('cart-count'),empty=document.getElementById('cart-empty');
const stateNames={CT:'Connecticut',ME:'Maine',MA:'Massachusetts',NH:'New Hampshire',RI:'Rhode Island',VT:'Vermont'};
const names=['q','state','chain','status','sort'];
const mapControls=Array.from(document.querySelectorAll('[data-map-state]'));
const badges=Array.from(document.querySelectorAll('[data-state-count]'));
const value=name=>form.elements.namedItem(name).value;
const params=new URLSearchParams(location.search);
for(const name of names){const el=form.elements.namedItem(name),v=params.get(name);if(v!==null)el.value=v;}
if(!value('sort'))form.elements.namedItem('sort').value='state';
function apply(updateURL=true){
 const words=value('q').trim().toLowerCase().split(/\s+/).filter(Boolean);
 const state=value('state');let visible=0;const totals={};
 for(const row of rows){
  const matchesOther=words.every(word=>row.dataset.search.includes(word))&&['chain','status'].every(name=>!value(name)||value(name)===row.dataset[name]);
  if(matchesOther)totals[row.dataset.state]=(totals[row.dataset.state]||0)+1;
  row.hidden=!(matchesOther&&(!state||row.dataset.state===state));if(!row.hidden)visible++;
 }
 const order=value('sort');
 const key=r=>order==='town'?[r.dataset.searchTown,r.dataset.state,r.dataset.chain]:order==='retailer'?[r.dataset.chain,r.dataset.state,r.dataset.searchTown]:[stateNames[r.dataset.state],r.dataset.searchTown,r.dataset.chain];
 const sorted=rows.slice().sort((a,b)=>key(a).join('|').localeCompare(key(b).join('|')));
 sorted.forEach(row=>list.append(row));
 count.textContent=visible+' of '+rows.length+' listings · all require a local availability check.';empty.hidden=visible>0;
 for(const control of mapControls){const active=control.dataset.mapState===state;control.classList.toggle('is-selected',active);control.setAttribute(control.tagName==='BUTTON'?'aria-pressed':'aria-current',String(active));}
 for(const badge of badges){const total=badge.dataset.stateCount?(totals[badge.dataset.stateCount]||0):Object.values(totals).reduce((a,b)=>a+b,0);badge.textContent=total+' '+(total===1?'listing':'listings');}
 document.getElementById('cart-map-selection').textContent=state?stateNames[state]+': '+visible+' matching '+(visible===1?'listing.':'listings.'):'Showing all six states: '+visible+' matching listings.';
 if(updateURL){const url=new URL(location.href);for(const name of names){const v=value(name).trim();if(v&&!(name==='sort'&&v==='state'))url.searchParams.set(name,v);else url.searchParams.delete(name);}history.replaceState(null,'',url);}
}
for(const row of rows)row.dataset.searchTown=row.querySelector('.cart-town').textContent.trim().toLowerCase();
for(const control of mapControls)control.addEventListener('click',event=>{event.preventDefault();form.elements.namedItem('state').value=control.dataset.mapState;apply();});
form.addEventListener('submit',event=>{event.preventDefault();apply();});form.addEventListener('input',()=>apply());form.addEventListener('change',()=>apply());
form.addEventListener('reset',()=>setTimeout(()=>{for(const name of names)form.elements.namedItem(name).value=name==='sort'?'state':'';apply();},0));
document.getElementById('cart-print').addEventListener('click',()=>window.print());apply(false);
})();
