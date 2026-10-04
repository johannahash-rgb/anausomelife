(() => {
  'use strict';
  const form=document.getElementById('cart-filters');
  if(!form) return;
  const rows=Array.from(document.querySelectorAll('.cart-row'));
  const count=document.getElementById('cart-count');
  const empty=document.getElementById('cart-empty');
  const names=['q','state','chain','status'];
  const params=new URLSearchParams(location.search);
  for(const name of names){const el=form.elements.namedItem(name);const value=params.get(name);if(value!==null) el.value=value;}
  function apply(updateURL=true){
    const q=form.elements.namedItem('q').value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let visible=0;
    for(const row of rows){
      const match=q.every(word=>row.dataset.search.includes(word)) && ['state','chain','status'].every(name=>!form.elements.namedItem(name).value||form.elements.namedItem(name).value===row.dataset[name]);
      row.hidden=!match;if(match) visible++;
    }
    count.textContent=visible+' of '+rows.length+' listings · all require a local availability check.';
    empty.hidden=visible>0;
    if(updateURL){const url=new URL(location.href);for(const name of names){const value=form.elements.namedItem(name).value.trim();if(value) url.searchParams.set(name,value);else url.searchParams.delete(name);}history.replaceState(null,'',url);}
  }
  form.addEventListener('submit',event=>{event.preventDefault();apply();});
  form.addEventListener('input',()=>apply());
  form.addEventListener('change',()=>apply());
  form.addEventListener('reset',()=>{setTimeout(()=>{for(const name of names) form.elements.namedItem(name).value='';apply();},0);});
  document.getElementById('cart-print').addEventListener('click',()=>window.print());
  apply(false);
})();
