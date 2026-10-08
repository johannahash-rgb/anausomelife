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


/* Favorite Places copy + share tools */
(() => {
  if (!document.body.classList.contains('favorite-place-page')) return;
  const actions = document.querySelector('#print .no-print.actions');
  const checklist = document.querySelector('#print .place-checklist');
  const title = document.querySelector('.favorite-hero h1')?.textContent.trim() || document.title;
  const place = document.querySelector('.favorite-place-name')?.textContent.trim() || '';
  if (!actions || !checklist) return;

  const status = document.createElement('p');
  status.className = 'copy-note favorite-tool-status';
  status.setAttribute('role','status');
  status.setAttribute('aria-live','polite');
  actions.after(status);

  const copyButton = document.createElement('button');
  copyButton.type = 'button';
  copyButton.className = 'button secondary';
  copyButton.textContent = 'Copy checklist';

  const shareButton = document.createElement('button');
  shareButton.type = 'button';
  shareButton.className = 'text-link';
  shareButton.textContent = 'Share this place';

  actions.append(copyButton, shareButton);

  const checklistText = () => {
    const items = [...checklist.querySelectorAll('li')].map(li => '- ' + li.textContent.replace(/^□\s*/, '').trim());
    return [title, place, '', 'Before we go:', ...items, '', location.href].join('\n');
  };

  async function copy(value, success) {
    try {
      if (!navigator.clipboard || !window.isSecureContext) throw new Error('clipboard unavailable');
      await navigator.clipboard.writeText(value);
      status.textContent = success;
    } catch (_) {
      const area = document.createElement('textarea');
      area.className = 'copy-fallback';
      area.readOnly = true;
      area.value = value;
      status.before(area);
      area.focus();
      area.select();
      status.textContent = 'Select and copy the text above.';
    }
  }

  copyButton.addEventListener('click', () => copy(checklistText(), 'Checklist copied.'));

  shareButton.addEventListener('click', async () => {
    const data = { title: title + ' | Favorite Places', text: title + ' — ' + place, url: location.href };
    try {
      if (navigator.share) {
        await navigator.share(data);
        status.textContent = 'Guide shared.';
      } else {
        await copy(location.href, 'Link copied.');
      }
    } catch (error) {
      if (error.name !== 'AbortError') await copy(location.href, 'Link copied.');
    }
  });
})();


/* Shared site-wide wayfinding + universal search */
(() => {
  if (document.querySelector('script[data-aal-global-nav]')) return;
  const s=document.createElement('script');
  s.src='/assets/global-nav.js?v=20261005-practical';
  s.dataset.aalGlobalNav='true';
  s.async=false;
  document.head.append(s);
})();


/* Media kit: inclusive creative, visual communication and caregiver reach */
(() => {
  if (!document.body.classList.contains('media-one') || document.getElementById('inclusive-creative')) return;
  const work = document.getElementById('work-with-us');
  if (!work) return;

  const grid = work.querySelector('.media-grid');
  if (grid) {
    const card = document.createElement('article');
    card.className = 'media-card';
    card.innerHTML = '<h3>Accessible picture-communication creative</h3><p>Each agreed product collaboration can include a custom, age-respectful PECS/AAC-style picture-communication card featuring the actual product. It is practical editorial content a brand may be able to reshare with credit and agreed usage rights—not a generic inclusion graphic or a therapeutic claim.</p>';
    grid.append(card);
  }

  const section = document.createElement('section');
  section.className = 'media-section wrap';
  section.id = 'inclusive-creative';
  section.setAttribute('aria-labelledby', 'inclusive-creative-title');
  section.innerHTML = `
    <div class="media-section-head">
      <div><p class="eyebrow">Accessible creative</p><h2 id="inclusive-creative-title">Access is part of the story—and part of the deliverable.</h2></div>
      <p class="intro">We do more than mention accessibility in a caption. For an agreed product feature, An AUsome Life can create a simple picture-communication visual around the actual product: something a person may use to recognize it, request it, choose between options, understand what comes next, or take part in a familiar routine.</p>
    </div>
    <div class="media-grid">
      <article class="media-card"><h3>A useful brand asset</h3><p>The visual gives a brand a concrete example of inclusive product education for social, accessibility, caregiver, community or customer-support channels. Organic resharing can be included when agreed; paid media, advertising and broader commercial use remain separately licensed.</p></article>
      <article class="media-card"><h3>Example: a pool bag</h3><p>A card might read <strong>“Pack the swim bag → go to the pool”</strong> and show a swimsuit, towel, AAC device, snack, the actual bag and the pool. The sequence, words, symbols and photographs are adapted to the product and real routine rather than forcing every person into one template.</p></article>
      <article class="media-card"><h3>Useful beyond autism</h3><p>Clear visual information may help some nonspeaking people, AAC users, people with intellectual, developmental or cognitive disabilities, people with aphasia, emerging readers and the family members or caregivers helping plan the day. Individual needs differ, and we say so.</p></article>
      <article class="media-card"><h3>Broader practical access</h3><p>Our access notes can also cover sensory information, mobility, cognitive load, setup, transport, changing and bathroom logistics, cleaning, caregiver workload and the number of steps between interest and successful use.</p></article>
      <article class="media-card"><h3>More than one in four adults</h3><p>CDC reported that more than one in four U.S. adults—over 70 million people—reported a disability in 2022 data. That does not mean every person needs the same adaptation; it does mean disability access belongs in mainstream consumer communication.</p></article>
      <article class="media-card"><h3>Nearly one in four are caregivers</h3><p>The 2025 AARP and National Alliance for Caregiving study found that 63 million Americans—nearly one in four adults—provided ongoing care for an adult or a child with a complex medical condition or disability. Caregivers frequently help research, choose, purchase, pack, set up and use products.</p></article>
    </div>
    <p class="media-note"><strong>Sources:</strong> <a href="https://www.cdc.gov/media/releases/2024/s0716-adult-disability.html" target="_blank" rel="noopener noreferrer">CDC, Disability and Health Data System update using 2022 BRFSS data ↗</a>; <a href="https://www.aarp.org/press/releases/2025-07-24-new-report-reveals-crisis-point-for-americas-63-million-family-caregivers.html" target="_blank" rel="noopener noreferrer">AARP and National Alliance for Caregiving, <em>Caregiving in the U.S. 2025</em> ↗</a>. These populations overlap and should not be added together as a combined market total.</p>
  `;
  work.after(section);

  const nav = document.querySelector('.media-nav .wrap');
  if (nav && !nav.querySelector('a[href="#inclusive-creative"]')) {
    const link = document.createElement('a');
    link.href = '#inclusive-creative';
    link.textContent = 'Accessible creative';
    const travelLink = nav.querySelector('a[href="#travel"]');
    nav.insertBefore(link, travelLink || null);
  }
})();
