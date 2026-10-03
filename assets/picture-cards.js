/* Local-only picture cards. No network upload or persistent personal data. */
(() => {
  'use strict';
  const root = document.querySelector('[data-picture-desk]');
  if (!root) return;
  const get = s => root.querySelector(s);
  const canvas = get('#card-canvas'), ctx = canvas.getContext('2d');
  const word = get('#card-word'), description = get('#card-description');
  const status = get('[role=status]'), sheet = get('[data-card-sheet]');
  const size = get('#card-size'), file = get('#card-photo');
  let photo = null, localUrl = null, loadId = 0;
  function draw() {
    ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, 900, 900);
    ctx.strokeStyle = '#172f3e'; ctx.lineWidth = 8; ctx.strokeRect(4, 4, 892, 892);
    if (photo) {
      const ratio = Math.min(820 / photo.naturalWidth, 684 / photo.naturalHeight);
      const w = photo.naturalWidth * ratio, h = photo.naturalHeight * ratio;
      ctx.drawImage(photo, (900-w)/2, 32 + (684-h)/2, w, h);
    }
    ctx.beginPath(); ctx.moveTo(4, 748); ctx.lineTo(896, 748); ctx.lineWidth=4; ctx.stroke();
    const label = word.value.trim() || 'my word';
    let fontSize = 76;
    ctx.font = `600 ${fontSize}px Arial, sans-serif`;
    while(ctx.measureText(label).width > 814 && fontSize > 28) ctx.font=`600 ${--fontSize}px Arial, sans-serif`;
    ctx.fillStyle='#172f3e'; ctx.textAlign='center'; ctx.textBaseline='middle'; ctx.fillText(label, 450, 823);
    canvas.setAttribute('aria-label', `${label}: ${description.value.trim() || 'selected picture'}`);
  }
  function setImage(src, owned = false) {
    const request = ++loadId, next = new Image();
    get('[data-save-card]').disabled = true; get('[data-add-card]').disabled = true;
    next.onload = () => {
      if(request !== loadId) { if(owned) URL.revokeObjectURL(src); return; }
      if(localUrl) URL.revokeObjectURL(localUrl);
      localUrl = owned ? src : null; photo = next; draw();
      get('[data-save-card]').disabled = false; get('[data-add-card]').disabled = false;
      status.textContent = owned ? 'Picture added. It stays in this tab.' : 'Starting illustration selected. Change the word if needed.';
    };
    next.onerror = () => {
      if(owned) URL.revokeObjectURL(src);
      if(request !== loadId) return;
      status.textContent='That picture could not be opened. Choose a JPG, PNG or WebP.';
      get('[data-save-card]').disabled = !photo; get('[data-add-card]').disabled = !photo;
    };
    next.src = src;
  }
  file.addEventListener('change', () => {
    const f=file.files?.[0]; if(!f) return;
    if(!['image/jpeg','image/png','image/webp'].includes(f.type) || f.size>12*1024*1024) {
      status.textContent='Choose a JPG, PNG or WebP up to 12 MB. For HEIC, export a JPG first.'; file.value=''; return;
    }
    setImage(URL.createObjectURL(f), true);
  });
  root.querySelectorAll('[data-preset]').forEach(button=>button.addEventListener('click',()=>{
    word.value=button.dataset.label;
    description.value=`Illustration for ${button.dataset.label}`;
    setImage(button.dataset.preset==='water'?'/assets/card-water.webp':`/assets/visuals/${button.dataset.preset}.svg`); draw();
  }));
  word.addEventListener('input',draw); description.addEventListener('input',draw);
  function download(blob, name) {
    if(!blob) { status.textContent='The image could not be saved. Please try another picture.'; return; }
    const url=URL.createObjectURL(blob), a=document.createElement('a'); a.href=url; a.download=name;
    a.click(); setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  get('[data-save-card]').addEventListener('click',()=>{
    draw(); canvas.toBlob(blob=>download(blob, `${(word.value.trim()||'picture-card').replace(/[^\p{L}\p{N}-]+/gu,'-')}.png`),'image/png');
    status.textContent='Your PNG is ready to download.';
  });
  function updateSheet() {
    const count=sheet.children.length;
    get('[data-sheet-count]').textContent=count ? `${count} ${count===1?'card':'cards'} ready to print.` : 'No cards added yet.';
    get('[data-print-cards]').disabled=!count; get('[data-clear-cards]').disabled=!count;
    sheet.style.setProperty('--card-size',`${size.value}in`);
  }
  size.addEventListener('change',updateSheet);
  get('[data-add-card]').addEventListener('click',()=>{
    if(sheet.children.length>=6) { status.textContent='Six cards are ready. Print or remove one before adding another.'; return; }
    draw(); const card=document.createElement('figure'), img=document.createElement('img'), remove=document.createElement('button');
    card.className='printable-picture'; img.src=canvas.toDataURL('image/png'); img.alt=canvas.getAttribute('aria-label');
    remove.type='button'; remove.textContent='Remove'; remove.setAttribute('aria-label',`Remove ${word.value.trim()||'picture'} card`);
    remove.addEventListener('click',()=>{card.remove();updateSheet();get('[data-add-card]').focus();});
    card.append(img,remove);sheet.append(card);updateSheet();status.textContent='Card added to your sheet.';
  });
  get('[data-clear-cards]').addEventListener('click',()=>{if(confirm('Remove every card from this sheet? Your current preview stays.')){sheet.replaceChildren();updateSheet();status.textContent='Sheet cleared.';}});
  get('[data-print-cards]').addEventListener('click',()=>window.print());
  const subject=get('#image-subject'), prompt=get('#image-prompt-text');
  function setPrompt(){prompt.value=`Create one realistic pen-and-watercolor illustration of ${subject.value.trim()||'the object I name'}, isolated on plain white. Show the complete object clearly, with true-to-life proportions and strong contrast. Refined New England field-guide style, restrained navy accents. No scene, text, lettering, border, logo, face, extra objects or decorative background. This will be a picture communication card; recognition matters more than ornament. Do not infer a person's feelings or invent a real venue. Square image.`;}
  subject.addEventListener('input',setPrompt);setPrompt();
  get('[data-copy-image-prompt]').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(prompt.value);status.textContent='Image prompt copied. Paste into your image tool, then add the finished image here.';}catch(_){prompt.focus();prompt.select();status.textContent='Select and copy the prompt below.';}});
  window.addEventListener('pagehide',()=>{if(localUrl)URL.revokeObjectURL(localUrl)});
  draw();updateSheet();setImage('/assets/card-water.webp');
})();
