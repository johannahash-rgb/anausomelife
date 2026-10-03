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
      const favoriteHub = document.body.classList.contains('favorite-hub');
      const noun = favoriteHub ? (visible === 1 ? 'place' : 'places') : (visible === 1 ? 'guide' : 'guides');
      status.textContent = query ? `${visible} ${noun} found.` : '';
      const noResults = document.getElementById('no-results');
      if (noResults) noResults.hidden = visible > 0;
      if (favoriteHub) {
        document.querySelectorAll('.favorite-group').forEach(section => {
          const sectionCards = [...section.querySelectorAll('.guide-card')];
          section.hidden = !!query && sectionCards.every(card => card.hidden);
        });
      }
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

(() => {
  const clearFavoritePrint = () => {
    document.body.classList.remove('favorite-print-one');
    document.querySelectorAll('.favorite-print-section,.favorite-print-target').forEach(el => el.classList.remove('favorite-print-section','favorite-print-target'));
  };
  window.addEventListener('afterprint', clearFavoritePrint);
  document.querySelectorAll('[data-print-favorite]').forEach(button => {
    button.addEventListener('click', () => {
      clearFavoritePrint();
      const target = button.closest('.favorite-print-card');
      const section = target?.closest('.section');
      if (!target || !section) return window.print();
      document.body.classList.add('favorite-print-one');
      target.classList.add('favorite-print-target');
      section.classList.add('favorite-print-section');
      window.print();
    });
  });
})();


/* Favorite Places printable guide */
(() => {
  const buttons = document.querySelectorAll('[data-print-place]');
  if (!buttons.length) return;
  const clear = () => document.body.classList.remove('print-place');
  buttons.forEach(button => button.addEventListener('click', () => {
    clear();
    document.body.classList.add('print-place');
    window.print();
  }));
  window.addEventListener('afterprint', clear);
})();
