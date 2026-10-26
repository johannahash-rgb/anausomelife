/* Native disclosures: preserve deep links, printing and clear active choices. */
(() => {
  'use strict';
  function reveal(){
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
    const target=id&&document.getElementById(id);if(!target)return;
    let changed=false;
    for(let p=target.parentElement;p;p=p.parentElement){if(p.tagName==='DETAILS'&&!p.open){p.open=true;changed=true;}}
    if(target.tagName==='DETAILS'&&!target.open){target.open=true;changed=true;}
    if(changed)requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'instant'}));
  }
  window.addEventListener('hashchange',reveal);reveal();
  document.addEventListener('click',event=>{
    const a=event.target.closest('a[href^="#"]');
    if(a&&a.hash===location.hash)requestAnimationFrame(reveal);
  });
  document.querySelectorAll('[data-reading-ease="filters"]').forEach(details=>{
    const selected=details.querySelector('[data-ease-selected]');
    function sync(){
      const labels=[...details.querySelectorAll('select')].filter(s=>s.selectedIndex>0).map(s=>s.options[s.selectedIndex].textContent.trim());
      const label=labels.length?' · '+labels.join(' · '):'';
      if(selected.textContent!==label)selected.textContent=label;
    }
    details.addEventListener('change',sync);
    details.closest('form')?.addEventListener('reset',()=>setTimeout(sync,0));
    window.addEventListener('popstate',()=>setTimeout(sync,0));
    // Catalogue choices can be populated after initial load.
    new MutationObserver(sync).observe(details,{childList:true,subtree:true});
    sync();
  });
  document.querySelectorAll('details[data-reading-ease]').forEach(details=>details.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&details.open){event.preventDefault();event.stopPropagation();details.open=false;details.querySelector(':scope > summary')?.focus();}
  }));
  let printState=[];
  window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details[data-reading-ease]')].map(d=>[d,d.open]);for(const [d] of printState)d.open=true;});
  window.addEventListener('afterprint',()=>{for(const [d,open] of printState)d.open=open;printState=[];});
  const form=document.getElementById('comm-form'),output=document.querySelector('[data-ease-output]');
  if(form&&output){
    const buttons=[...output.querySelectorAll('button')],paper=document.getElementById('output-paper');
    const sync=()=>{const ready=!paper.textContent.includes('Ready when you are.');buttons.forEach(b=>{if(b.id!=='share-generator')b.disabled=!ready;});};
    new MutationObserver(sync).observe(paper,{childList:true,subtree:true});sync();
    form.addEventListener('submit',()=>requestAnimationFrame(()=>{output.scrollIntoView({block:'start',behavior:'instant'});output.focus({preventScroll:true});}));
  }
})();
