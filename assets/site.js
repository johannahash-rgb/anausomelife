(() => {
  document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
  const input = document.getElementById('guide-search');
  if (input) {
    document.querySelector('[data-search-ui]').hidden = false;
    const cards = [...document.querySelectorAll('.guide-card')];
    const status = document.getElementById('search-status');
    function filter() {
      const query = input.value.trim().toLocaleLowerCase(); let visible = 0;
      cards.forEach(card => { const match = !query || card.textContent.toLocaleLowerCase().includes(query); card.hidden = !match; if(match) visible++; });
      status.textContent = query ? `${visible} ${visible === 1 ? 'guide' : 'guides'} found.` : '';
      document.getElementById('no-results').hidden = visible > 0;
    }
    input.addEventListener('input', filter);
    document.getElementById('clear-search').addEventListener('click', () => { input.value = ''; filter(); input.focus(); });
    window.addEventListener('pageshow', filter);
  }
})();
(() => {
  function fallback(box,text,status){
    let area=box.querySelector('.copy-fallback');
    if(!area){area=document.createElement('textarea');area.className='copy-fallback';area.readOnly=true;area.setAttribute('aria-label','Text to copy');box.append(area);}
    area.value=text;area.focus();area.select();status.textContent='Select and copy the text below.';
  }
  async function copy(box,text){const status=box.querySelector('.status');try{if(!navigator.clipboard)throw new Error('unavailable');await navigator.clipboard.writeText(text);status.textContent='Copied. Paste it into your notes or a message.';}catch(e){fallback(box,text,status);}}
  document.querySelectorAll('[data-checklist]').forEach(box=>{
    box.querySelector('[data-copy-checklist]')?.addEventListener('click',()=>{const lines=[box.querySelector('h3')?.textContent||'Checklist',...[...box.querySelectorAll('li')].map(li=>(li.querySelector('input')?.checked?'[x] ':'[ ] ')+li.textContent.trim())];copy(box,lines.join('\n'));});
    box.querySelector('[data-reset-checklist]')?.addEventListener('click',()=>{box.querySelectorAll('input[type=checkbox]').forEach(i=>i.checked=false);box.querySelector('.status').textContent='Checks reset.';box.querySelector('.copy-fallback')?.remove();});
  });
  const clearPrint=()=>{document.body.classList.remove('print-one');document.querySelectorAll('.print-section,.print-target').forEach(e=>e.classList.remove('print-section','print-target'));};
  window.addEventListener('afterprint',clearPrint);
  document.querySelectorAll('[data-print]').forEach(b=>b.addEventListener('click',clearPrint,true));
  document.querySelectorAll('[data-planner]').forEach(box=>{
    const inputs=[...box.querySelectorAll('input')];inputs.forEach(input=>{const output=document.createElement('span');output.className='print-field';output.setAttribute('aria-hidden','true');input.after(output);input.addEventListener('input',()=>output.textContent=input.value||'________________________________');output.textContent='________________________________';});
    box.querySelector('[data-copy-plan]').addEventListener('click',()=>copy(box,[box.querySelector('h3').textContent,...inputs.map(i=>i.dataset.label+': '+(i.value.trim()||'________'))].join('\n')));
    box.querySelector('[data-reset-plan]').addEventListener('click',()=>{inputs.forEach(i=>{i.value='';i.nextElementSibling.textContent='________________________________';});box.querySelector('.copy-fallback')?.remove();box.querySelector('.status').textContent='Entries cleared.';inputs[0].focus();});
    box.querySelector('[data-print-plan]').addEventListener('click',()=>{clearPrint();document.body.classList.add('print-one');box.classList.add('print-target');box.closest('.section').classList.add('print-section');window.print();});
  });
})();
