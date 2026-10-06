/* Reviewed local artwork + private local photo editor. No generation or upload API. */
(() => {
  'use strict';
  const entries = window.AALCardCatalog || [], root = document.querySelector('[data-card-collection]');
  if (!root || !entries.length) return;
  const $ = selector => root.querySelector(selector), byId = new Map(entries.map(c => [c.id,c]));
  const grid = $('[data-card-grid]'), search = $('#cc-search'), category = $('#cc-category');
  const dialog = $('#cc-editor'), canvas = $('#cc-canvas'), label = $('#cc-label');
  const description = $('#cc-description'), color = $('#cc-color'), lettering = $('#cc-lettering');
  const sheetList = $('[data-sheet-list]'), selection = new Map(), images = new Map();
  const palettes = {navy:'#173c4c',pine:'#2e513f',cranberry:'#772f41',black:'#111111'};
  const categories = window.AALCardCategories || [...new Set(entries.map(c=>c.category))];
  const FAVORITES = 'New England favorites';
  let page = 0, active = null, renderVersion = 0, activeReady = false, uploadUrl = null, downloadUrl = null, customId = 0;
  const PAGE_SIZE = 25;
  const norm = value => String(value || '').toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const slug = word => norm(word).replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'') || 'picture-card';
  const status = (message,error=false) => {const el=$('[data-status]');el.textContent=message;el.classList.toggle('error',error);};
  function element(tag,className,text) {const el=document.createElement(tag);if(className)el.className=className;if(text!==undefined)el.textContent=text;return el;}
  function picture(card) {
    const frame=element('span','cc-picture');frame.setAttribute('role','img');frame.setAttribute('aria-label',card.description || card.label);
    if(card.crop) {
      const c=element('canvas');c.width=c.height=360;c.style.width='100%';c.style.height='100%';frame.append(c);
      getImage(card.image).then(img=>{const ctx=c.getContext('2d'),[x,y,w,h]=card.crop,scale=Math.min(360/w,360/h);ctx.fillStyle='#fff';ctx.fillRect(0,0,360,360);ctx.drawImage(img,x,y,w,h,(360-w*scale)/2,(360-h*scale)/2,w*scale,h*scale);}).catch(()=>{frame.setAttribute('aria-label','Picture unavailable: '+card.label);});
    } else if(Number.isInteger(card.cell)) {
      frame.style.backgroundImage=`url("${card.image}")`;frame.style.backgroundSize='400% 400%';
      frame.style.backgroundPosition=`${(card.cell%4)*100/3}% ${Math.floor(card.cell/4)*100/3}%`;
    } else {const img=element('img');img.src=card.image;img.alt='';img.loading='lazy';img.decoding='async';frame.append(img);}
    return frame;
  }
  function getImage(src) {
    if(!images.has(src)) images.set(src,new Promise((resolve,reject)=>{
      const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>{images.delete(src);reject(new Error('The picture could not load. Please try again.'));};image.src=src;
    }));
    return images.get(src);
  }
  async function renderCard(card, options={}) {
    const img=await getImage(card.image), c=options.canvas || document.createElement('canvas');c.width=900;c.height=900;
    const ctx=c.getContext('2d'), ink=palettes[options.color] || palettes.navy;
    ctx.fillStyle='#fff';ctx.fillRect(0,0,900,900);
    ctx.strokeStyle=ink;ctx.lineWidth=7;ctx.strokeRect(10,10,880,880);
    let sx=0,sy=0,sw=img.naturalWidth,sh=img.naturalHeight;
    if(card.crop){[sx,sy,sw,sh]=card.crop;}else if(Number.isInteger(card.cell)){sw/=4;sh/=4;sx=(card.cell%4)*sw;sy=Math.floor(card.cell/4)*sh;}
    const ratio=Math.min(790/sw,685/sh),w=sw*ratio,h=sh*ratio;
    ctx.drawImage(img,sx,sy,sw,sh,(900-w)/2,35+(685-h)/2,w,h);
    ctx.beginPath();ctx.moveTo(14,749);ctx.lineTo(886,749);ctx.lineWidth=2;ctx.stroke();
    const text=options.upper?card.label.toLocaleUpperCase():card.label;let font=options.large?85:72;
    ctx.font=`600 ${font}px Arial,sans-serif`;
    while(ctx.measureText(text).width>810 && font>24)ctx.font=`600 ${--font}px Arial,sans-serif`;
    ctx.fillStyle=ink;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,450,820);
    c.setAttribute('aria-label',`${text}: ${card.description || 'picture'}`);return c;
  }
  const toBlob = c => new Promise((resolve,reject)=>c.toBlob(b=>b?resolve(b):reject(new Error('Could not prepare the file.')),'image/png'));
  function saveBlob(blob,name,link) {
    if(downloadUrl)URL.revokeObjectURL(downloadUrl);downloadUrl=URL.createObjectURL(blob);
    const a=link || element('a');a.href=downloadUrl;a.download=name;a.textContent='Download '+name;a.hidden=false;
    if(!link)document.body.append(a);a.click();if(!link)a.remove();
  }
  const packButton=$('[data-download-pack]');
  if(packButton){packButton.disabled=false;packButton.onclick=async()=>{
    const progress=$('[data-pack-status]');packButton.disabled=true;progress.textContent='Preparing your PNG collection…';
    try{
      const response=await fetch('/downloads/picture-cards-278-png-parts.json');if(!response.ok)throw new Error();
      const pack=await response.json(),parts=[];
      for(let i=0;i<pack.parts.length;i++){
        progress.textContent=`Preparing download: ${i+1} of ${pack.parts.length}…`;
        const part=pack.parts[i],res=await fetch(part.url);if(!res.ok)throw new Error();const bytes=await res.arrayBuffer();if(bytes.byteLength!==part.size)throw new Error();
        if(window.crypto?.subtle){const digest=await crypto.subtle.digest('SHA-256',bytes),hash=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');if(hash!==part.sha256)throw new Error();}
        parts.push(bytes);
      }
      saveBlob(new Blob(parts,{type:'application/zip'}),pack.filename);progress.textContent='Your complete PNG collection is ready. Check your downloads.';
    }catch(_){progress.textContent='The download was interrupted. Please try again, or download a category PDF.';}
    finally{packButton.disabled=false;}
  };}
  async function download(card,options={},link) {
    const c=await renderCard(card,options);saveBlob(await toBlob(c),slug(card.label)+'-picture-card.png',link);
  }
  function matches() {
    const tokens=norm(search.value).trim().split(/\s+/).filter(Boolean);
    return entries.filter(c=>(category.value==='all'||(category.value===FAVORITES?c.featured:c.category===category.value))&&tokens.every(t=>norm(`${c.label} ${c.category} ${c.keywords||''} ${c.brand||''}`).includes(t)));
  }
  function updateSheet() {
    const n=selection.size;
    $('[data-selected-count]').textContent=`${n} ${n===1?'card':'cards'} selected`;
    $('[data-sheet-count]').textContent=n?`${n} ${n===1?'card':'cards'} ready to print. Cards appear in the order you added them.`:'Choose cards above to build your own set.';
    $('[data-selection-bar]').hidden=!n;$('[data-print]').disabled=!n;$('[data-clear]').disabled=!n;
    sheetList.replaceChildren();
    for(const [key,card] of selection) {
      const item=element('figure','cc-sheet-card'),face=element('div','cc-card-face');face.append(picture(card));if(!card.completeCard)face.append(element('h3','',card.label));
      const remove=element('button','','Remove');remove.type='button';remove.setAttribute('aria-label',`Remove ${card.label} from print set`);
      remove.onclick=()=>{selection.delete(key);updateSheet();syncButtons();status(`${card.label} removed from your set.`);$('[data-sheet-heading]').focus();};item.append(face,remove);sheetList.append(item);
    }
  }
  function syncButtons() {
    root.querySelectorAll('[data-add-id]').forEach(button=>{const selected=selection.has(button.dataset.addId);button.setAttribute('aria-pressed',String(selected));button.textContent=selected?'✓ Added':'+ Add';button.setAttribute('aria-label',`${selected?'Remove':'Add'} ${byId.get(button.dataset.addId)?.label || 'card'} ${selected?'from':'to'} print set`);});
  }
  function toggleCard(card) {
    if(selection.has(card.id)){selection.delete(card.id);status(`${card.label} removed.`);}else{selection.set(card.id,{...card});status(`${card.label} added to your print set.`);}
    updateSheet();syncButtons();
  }
  function renderGrid() {
    const cards=matches(), pages=Math.max(1,Math.ceil(cards.length/PAGE_SIZE));page=Math.min(page,pages-1);grid.replaceChildren();
    $('[data-result-count]').textContent=`${cards.length} of ${entries.length} cards${search.value?' match your search':''}`;
    $('[data-result-heading]').textContent=category.value==='all'?'All pictures':category.value;
    root.querySelectorAll('[data-category-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.categoryChoice===category.value)));
    const categoryPdf=$('[data-category-pdf]');categoryPdf.hidden=category.value==='all';
    if(!categoryPdf.hidden){categoryPdf.href='/downloads/picture-cards-'+slug(category.value)+'.pdf';categoryPdf.textContent='Download category PDF';}
    $('[data-category-note]').textContent=category.value===FAVORITES?'Familiar New England objects, with simple everyday words. Brand references appear below the pictures.':category.value==='all'?'New England favorites first, then everyday cards grouped by category.':'Choose individual cards, download this category, or add the matching cards to your print set.';
    $('[data-add-results]').textContent=`Add ${cards.length} ${cards.length===1?'card':'cards'}`;$('[data-add-results]').disabled=!cards.length;
    if(!cards.length){const empty=element('div','cc-empty');empty.append(element('strong','','No pictures found.'),element('p','','Try one word, such as “water”, “shoes” or “pool”, choose All categories, or make a card with your own photo.'));grid.append(empty);}
    let lastGroup='';
    for(const card of cards.slice(page*PAGE_SIZE,(page+1)*PAGE_SIZE)) {
      const group=category.value==='all'?(card.featured?FAVORITES:card.category):category.value;
      if(category.value==='all'&&group!==lastGroup){const h=element('h3','cc-group-heading',group);grid.append(h);lastGroup=group;}
      const tile=element('article','cc-tile'), face=element('button','cc-card-face');face.type='button';face.setAttribute('aria-label',`Edit ${card.label} card`);face.append(picture(card),element('span','cc-card-label',card.label));face.onclick=()=>openEditor(card);
      const actions=element('div','cc-tile-actions'), save=element('button','','↓ PNG'), add=element('button','','+ Add');save.type=add.type='button';save.setAttribute('aria-label',`Download ${card.label} PNG`);add.dataset.addId=card.id;
      save.onclick=async()=>{save.disabled=true;status(`Preparing ${card.label}…`);try{await download(card);status(`${card.label} PNG is ready. Check your downloads.`);}catch(error){status(error.message,true);}finally{save.disabled=false;}};
      add.onclick=()=>toggleCard(card);actions.append(save,add);tile.append(face);
      if(card.brand){const credit=element('a','cc-brand',card.brand+' · illustration');credit.href=card.brandUrl;credit.target='_blank';credit.rel='noopener';credit.setAttribute('aria-label',card.brand+' reference for '+card.label+' (opens in new tab)');tile.append(credit);}
      tile.append(actions);grid.append(tile);
    }
    $('[data-page]').textContent=`Page ${page+1} of ${pages}`;$('[data-prev]').disabled=page===0;$('[data-next]').disabled=page===pages-1;$('[data-pagination]').hidden=pages===1;syncButtons();
  }
  function editorCard(){return {...active,label:label.value.trim(),description:description.value.trim()};}
  function editorOptions(){return {color:color.value,upper:lettering.value==='upper',large:$('#cc-word-size').value==='large'};}
  function editorStatus(text,error=false){const el=$('[data-editor-status]');el.textContent=text;el.classList.toggle('error',error);}
  async function updatePreview() {
    const version=++renderVersion;activeReady=false;$('[data-editor-download]').disabled=true;$('[data-editor-add]').disabled=true;
    if(!active?.image)return;
    try {
      const rendered=await renderCard({...editorCard(),label:label.value.trim()||'your word'},editorOptions());
      if(version!==renderVersion)return;canvas.getContext('2d').drawImage(rendered,0,0);canvas.setAttribute('aria-label',rendered.getAttribute('aria-label'));
      activeReady=true;$('[data-editor-download]').disabled=false;$('[data-editor-add]').disabled=false;
    }catch(error){if(version===renderVersion)editorStatus(error.message,true);}
  }
  function openEditor(card) {
    active={...card};label.value=card.label;description.value=card.description||'';color.value='navy';lettering.value='entered';$('#cc-word-size').value='normal';
    label.removeAttribute('aria-invalid');$('[data-editor-link]').hidden=true;editorStatus(card.kind==='symbol'?'Use this symbol only if its meaning is familiar. You can replace it with a photo.':card.brand?'Original illustration inspired by '+card.brand+'. Change the word to the one you use.':'Change the word if you like. Your picture stays clear and uncluttered.');
    canvas.width=canvas.height=900;canvas.getContext('2d').clearRect(0,0,900,900);dialog.showModal();updatePreview();
  }
  function validEditor(){if(!activeReady){editorStatus('Wait for your picture to finish loading.',true);return false;}if(!label.value.trim()){label.setAttribute('aria-invalid','true');label.focus();editorStatus('Add a word or short phrase for this card.',true);return false;}return true;}
  function readyForFile(){const file=$('#cc-photo');file.value='';file.click();}
  root.querySelectorAll('[data-photo]').forEach(b=>b.onclick=readyForFile);
  $('#cc-photo').onchange=async event=>{
    const file=event.target.files?.[0];if(!file)return;
    if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>12*1024*1024){const message='Choose a JPG, PNG or WebP up to 12 MB. Convert HEIC photos to JPG first.';status(message,true);if(dialog.open)editorStatus(message,true);return;}
    const url=URL.createObjectURL(file);
    try {
      const image=await getImage(url),c=document.createElement('canvas'),ratio=Math.min(1,1500/Math.max(image.naturalWidth,image.naturalHeight));c.width=Math.round(image.naturalWidth*ratio);c.height=Math.round(image.naturalHeight*ratio);c.getContext('2d').drawImage(image,0,0,c.width,c.height);
      const card={id:'custom-'+(++customId),label:dialog.open?label.value:'',description:'My own photo',image:c.toDataURL('image/png'),category:'My photos'};
      if(dialog.open){active=card;description.value=card.description;editorStatus('Your photo is ready. Add the word you use.');updatePreview();}else openEditor(card);
      label.focus();status('Your photo stays in this tab. Save before closing.');
    }catch(error){status('That photo could not be opened. Try a JPG or PNG.',true);if(dialog.open)editorStatus('That photo could not be opened. Try a JPG or PNG.',true);}
    finally{URL.revokeObjectURL(url);images.delete(url);}
  };
  $('[data-close]').onclick=()=>dialog.close();dialog.addEventListener('close',()=>{++renderVersion;activeReady=false;});
  [label,description].forEach(el=>el.addEventListener('input',()=>{label.removeAttribute('aria-invalid');updatePreview();}));
  [color,lettering,$('#cc-word-size')].forEach(el=>el.onchange=updatePreview);
  $('[data-editor-download]').onclick=async()=>{if(!validEditor())return;const btn=$('[data-editor-download]');btn.disabled=true;editorStatus('Preparing your PNG…');try{await download(editorCard(),editorOptions(),$('[data-editor-link]'));editorStatus('Your card is ready. Use the download link if it did not save automatically.');}catch(error){editorStatus(error.message,true);}finally{btn.disabled=false;}};
  $('[data-editor-add]').onclick=async()=>{
    if(!validEditor())return;const card=editorCard(),options=editorOptions();
    try {const rendered=await renderCard(card,options),key=`edited-${++customId}`;selection.set(key,{id:key,label:options.upper?card.label.toLocaleUpperCase():card.label,description:card.description,image:rendered.toDataURL('image/png'),completeCard:true});updateSheet();syncButtons();editorStatus('Added to your print set. You can close this window and choose another.');status(`${card.label} added to your print set.`);}catch(error){editorStatus(error.message,true);}
  };
  $('[data-add-results]').onclick=()=>{const cards=matches();cards.forEach(card=>selection.set(card.id,{...card}));updateSheet();syncButtons();status(`${cards.length} matching cards added. Your set now has ${selection.size} cards.`);};
  $('[data-clear]').onclick=()=>{if(!confirm('Remove every card from this print set? Downloaded files will stay on your device.'))return;selection.clear();updateSheet();syncButtons();status('Print set cleared.');};
  $('[data-view-sheet]').onclick=()=>{$('[data-sheet-heading]').focus();$('#cc-sheet').scrollIntoView({block:'start',behavior:'auto'});};
  $('[data-print]').onclick=async()=>{
    if(!selection.size)return;const button=$('[data-print]');button.disabled=true;status('Preparing your printable cards…');$('[data-sheet-status]').textContent='Preparing your printable cards…';
    try {
      const printArea=document.querySelector('[data-print-area]');printArea.replaceChildren();const size=Number($('#cc-print-size').value);printArea.style.setProperty('--cc-print-size',size+'in');
      const perPage=size===2?12:size===3?6:2;let pageEl;
      const cards=Array.from(selection.values());
      for(let i=0;i<cards.length;i++) {
        if(i%perPage===0){pageEl=element('div','cc-print-page');printArea.append(pageEl);}
        const card=cards[i],img=element('img','cc-print-card');img.alt=card.label;img.src=card.completeCard?card.image:(await renderCard(card)).toDataURL('image/png');pageEl.append(img);
      }
      await Promise.all([...printArea.querySelectorAll('img')].map(img=>img.decode()));
      document.body.classList.add('cc-printing');status('Print view is ready. Choose your printer or Save as PDF.');$('[data-sheet-status]').textContent='Ready. Print at 100% / actual size, with browser headers and footers off.';
      window.print();
    }catch(error){status('Printing could not be prepared. Try fewer cards or use the ready-made PDF.',true);$('[data-sheet-status]').textContent='Could not prepare the print set. Try fewer cards or download the ready-made PDF.';document.body.classList.remove('cc-printing');}
    finally{button.disabled=false;}
  };
  window.addEventListener('afterprint',()=>document.body.classList.remove('cc-printing'));
  search.oninput=()=>{page=0;renderGrid();};category.onchange=()=>{page=0;renderGrid();};
  $('[data-reset]').onclick=()=>{search.value='';category.value='all';page=0;renderGrid();search.focus();};
  $('[data-prev]').onclick=()=>{page--;renderGrid();$('#cc-cards').scrollIntoView({block:'start'});$('[data-result-heading]').focus();};
  $('[data-next]').onclick=()=>{page++;renderGrid();$('#cc-cards').scrollIntoView({block:'start'});$('[data-result-heading]').focus();};
  for(const name of [FAVORITES,...categories]){const opt=element('option','',name);opt.value=name;category.append(opt);}
  for(const name of ['all',FAVORITES,...categories]){
    const button=element('button',name===FAVORITES?'cc-category-favorite':'');button.type='button';button.dataset.categoryChoice=name;button.setAttribute('aria-pressed',String(name==='all'));
    const n=name==='all'?entries.length:name===FAVORITES?entries.filter(c=>c.featured).length:entries.filter(c=>c.category===name).length;
    button.append(element('span','',name==='all'?'All cards':name),element('span','cc-category-count',String(n)));
    button.onclick=()=>{category.value=name;page=0;renderGrid();};$('[data-categories]').append(button);
  }
  root.querySelectorAll('[data-featured]').forEach(el=>{const card=byId.get(el.dataset.featured);if(card)el.prepend(picture(card));});
  updateSheet();renderGrid();
  const params=new URLSearchParams(location.search),requested=params.get('card'),requestedCategory=params.get('category');
  if([FAVORITES,...categories].includes(requestedCategory)){category.value=requestedCategory;renderGrid();}
  if(requested&&byId.has(requested))openEditor(byId.get(requested));
  // Shared renderer also supports the prebuilt downloadable packs.
  window.AALCardCollection={entries,renderCard,getImage};
})();
