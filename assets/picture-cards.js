/* Local card editor plus a safe, backend-ready image-generation handoff. */
(() => {
'use strict';
const root=document.querySelector('[data-picture-desk]');if(!root)return;
const get=s=>root.querySelector(s), canvas=get('#card-canvas'),ctx=canvas.getContext('2d');
const word=get('#card-word'),description=get('#card-description'),status=get('[data-card-status]'),sheet=get('[data-card-sheet]');
const size=get('#card-size'),file=get('#card-photo'),situation=get('#card-situation'),results=get('#card-options'),editor=get('#card-editor');
const imageApi=(document.querySelector('meta[name="ausome-image-api"]')?.content||'').trim();
const catalog=[
 {id:'water',label:'water',description:'A clear glass of drinking water',terms:/\b(water|drink|thirst\w*)\b/},
 {id:'break',label:'break',description:'A white armchair with a navy striped cushion',terms:/\b(break|quiet|rest|sit|chair|calm|loud|noise|noisy|overwhelm\w*)\b/},
 {id:'apple',label:'apple',description:'A whole red apple',terms:/\b(apple|snack|food|eat|hungr\w*)\b/},
 {id:'toilet',label:'toilet',description:'A white toilet with its lid raised',terms:/\b(toilet|bathroom|restroom|loo|potty)\b/},
 {id:'coat',label:'coat',description:'A navy quilted jacket',terms:/\b(coat|jacket|cold|dress\w*)\b/},
 {id:'car',label:'car',description:'A navy blue family station wagon',terms:/\b(car|drive|driving|ride|travel|leave|leaving|go|home)\b/}
];
let photo=null,localUrl=null,downloadUrl=null,loadId=0,selectedId=null;
const palettes={navy:'#173c4c',pine:'#2e513f',cranberry:'#772f41',black:'#171717'};
const palette=get('#card-color'),lettering=get('#card-lettering'),typeSize=get('#card-type-size');
function cardLabel(){const value=word.value.trim()||'my word';return lettering.value==='upper'?value.toLocaleUpperCase():value;}
const srcFor=id=>`/assets/card-studio/${id}.webp`;
function announce(message){status.textContent=message;}
function draw(){
 ctx.fillStyle='#fff';ctx.fillRect(0,0,900,900);ctx.strokeStyle=palettes[palette.value]||palettes.navy;ctx.lineWidth=8;ctx.strokeRect(4,4,892,892);
 if(photo){const ratio=Math.min(820/photo.naturalWidth,684/photo.naturalHeight),w=photo.naturalWidth*ratio,h=photo.naturalHeight*ratio;ctx.drawImage(photo,(900-w)/2,32+(684-h)/2,w,h);}
 ctx.beginPath();ctx.moveTo(4,748);ctx.lineTo(896,748);ctx.lineWidth=4;ctx.stroke();
 const label=cardLabel();let fontSize=Number(typeSize.value)||76;ctx.font=`600 ${fontSize}px Arial, sans-serif`;
 while(ctx.measureText(label).width>814&&fontSize>28)ctx.font=`600 ${--fontSize}px Arial, sans-serif`;
 ctx.fillStyle=palettes[palette.value]||palettes.navy;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(label,450,823);
 canvas.setAttribute('aria-label',`${label}: ${description.value.trim()||'selected picture'}`);
}
function enableExport(enabled){get('[data-save-card]').disabled=!enabled;get('[data-add-card]').disabled=!enabled;}
function revealEditor(){editor.hidden=false;get('#editor-heading').focus({preventScroll:true});editor.scrollIntoView({behavior:'auto',block:'start'});}
function setImage(src,owned=false){
 const request=++loadId,next=new Image();enableExport(false);announce('Opening your picture…');
 next.onload=()=>{if(request!==loadId){if(owned)URL.revokeObjectURL(src);return;}if(localUrl)URL.revokeObjectURL(localUrl);localUrl=owned?src:null;photo=next;draw();enableExport(true);announce(owned?'Your photo is ready. Add its familiar word, then save or print.':'Picture ready. Keep this word, or change it to the word you use.');};
 next.onerror=()=>{if(owned)URL.revokeObjectURL(src);if(request!==loadId)return;photo=null;draw();enableExport(false);announce('This picture could not be opened. Choose another picture or upload a JPG, PNG or WebP.');};next.src=src;
}
function chooseCard(card){
 selectedId=card.id;file.value='';word.value=card.label;description.value=card.description;get('#image-subject').value=card.description;setPrompt();
 root.querySelectorAll('[data-card-option]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.cardOption===card.id)));
 photo=null;draw();revealEditor();setImage(srcFor(card.id));
}
function matchingCards(text){
 const normalized=text.toLowerCase(),matched=catalog.filter(card=>card.terms.test(normalized));if(matched.length)return matched;
 if(/\b(restaurant|cafe|café|diner|lunch|dinner)\b/.test(normalized))return catalog.filter(c=>['water','break','toilet'].includes(c.id));
 if(/\b(outside|outing|walk|park|getting ready)\b/.test(normalized))return catalog.filter(c=>['water','coat','car'].includes(c.id));return [];
}
function showOptions(all=false){
 const text=situation.value.trim(),matched=matchingCards(text),cards=all||!matched.length?catalog:matched;results.hidden=false;
 get('[data-options-title]').textContent=all?'Choose a starting picture':matched.length?'A few pictures to start with':'Start with a picture, or use your own';
 get('[data-options-note]').textContent=!all&&text&&!matched.length?'We do not have an exact picture for that yet. Browse these, add your own photo, or create a new picture below.':'These are suggestions from our starter collection. Choose a picture that means the right thing to you.';
 const grid=get('[data-picture-options]');grid.replaceChildren();
 cards.forEach(card=>{const button=document.createElement('button'),img=document.createElement('img'),label=document.createElement('span'),hint=document.createElement('small');button.type='button';button.className='studio-picture-option';button.dataset.cardOption=card.id;button.setAttribute('aria-pressed',String(card.id===selectedId));img.src=srcFor(card.id);img.alt='';img.width=180;img.height=150;label.textContent=card.label;hint.textContent=card.id==='break'?'Chair picture · use if familiar':'Use this picture';button.append(img,label,hint);button.addEventListener('click',()=>chooseCard(card));grid.append(button);});
 get('[data-options-title]').focus({preventScroll:true});results.scrollIntoView({behavior:'auto',block:'start'});get('#image-subject').value=text||'the object I need to communicate';setPrompt();
}
get('#situation-form').addEventListener('submit',event=>{event.preventDefault();showOptions();});
root.querySelectorAll('[data-example]').forEach(button=>button.addEventListener('click',()=>{situation.value=button.dataset.example;showOptions();}));
root.querySelectorAll('[data-browse-pictures]').forEach(button=>button.addEventListener('click',()=>showOptions(true)));
root.querySelectorAll('[data-choose-photo]').forEach(button=>button.addEventListener('click',()=>file.click()));
file.addEventListener('change',()=>{const f=file.files?.[0];if(!f)return;if(!['image/jpeg','image/png','image/webp'].includes(f.type)||f.size>12*1024*1024){get('[data-upload-status]').textContent='Choose a JPG, PNG or WebP up to 12 MB. Export HEIC photos as JPG first.';file.value='';return;}get('[data-upload-status]').textContent='';selectedId=null;photo=null;word.value='';description.value='';root.querySelectorAll('[data-card-option]').forEach(button=>button.setAttribute('aria-pressed','false'));draw();revealEditor();setImage(URL.createObjectURL(f),true);word.focus({preventScroll:true});});
word.addEventListener('input',()=>{word.removeAttribute('aria-invalid');draw();});description.addEventListener('input',draw);
[palette,lettering,typeSize].forEach(control=>control.addEventListener('change',()=>{get('[data-color-swatch]').style.backgroundColor=palettes[palette.value];draw();announce('Preview updated. Saved cards on your sheet keep their original settings.');}));
function download(blob,name){if(!blob){announce('The image could not be saved. Please try another picture.');return;}if(downloadUrl)URL.revokeObjectURL(downloadUrl);downloadUrl=URL.createObjectURL(blob);const a=get('[data-card-download]');a.href=downloadUrl;a.download=name;a.hidden=false;a.textContent='Download '+name;a.click();announce('Your PNG is ready. If it did not save automatically, use the download link.');}
function ready(){if(!photo){announce('Choose a picture first.');return false;}if(!word.value.trim()){word.setAttribute('aria-invalid','true');announce('Add the word you want underneath your picture.');word.focus();return false;}return true;}
get('[data-save-card]').addEventListener('click',()=>{if(!ready())return;draw();canvas.toBlob(blob=>download(blob,`${word.value.trim().replace(/[^\p{L}\p{N}-]+/gu,'-')}.png`),'image/png');});
function updateSheet(){const count=sheet.children.length;get('[data-sheet-count]').textContent=count?`${count} ${count===1?'card':'cards'} ready to print.`:'Your saved cards will appear here.';get('[data-print-cards]').disabled=!count;get('[data-clear-cards]').disabled=!count;sheet.style.setProperty('--card-size',`${size.value}in`);get('[data-size-label]').textContent=`${size.value} inches`;}
size.addEventListener('change',updateSheet);
get('[data-add-card]').addEventListener('click',()=>{if(!ready())return;if(sheet.children.length>=6){announce('Six cards are ready. Print or remove one before adding another.');return;}draw();const card=document.createElement('figure'),img=document.createElement('img'),remove=document.createElement('button');card.className='printable-picture';img.src=canvas.toDataURL('image/png');img.alt=canvas.getAttribute('aria-label');remove.type='button';remove.textContent='Remove';remove.setAttribute('aria-label',`Remove ${word.value.trim()} card`);remove.addEventListener('click',()=>{card.remove();updateSheet();get('[data-add-card]').focus();});card.append(img,remove);sheet.append(card);updateSheet();announce('Added to your sheet. Choose another picture or print your sheet below.');});
get('[data-clear-cards]').addEventListener('click',()=>{if(confirm('Remove every card from this sheet? Your current preview stays.')){sheet.replaceChildren();updateSheet();announce('Sheet cleared.');}});
get('[data-print-cards]').addEventListener('click',()=>window.print());
const subject=get('#image-subject'),prompt=get('#image-prompt-text');
function setPrompt(){const context=situation.value.trim();
const unsafe=/\b(porn(?:ography|ographic)?|nudes?|naked|sexual(?:ized|isation|ization)?|sexually|erotic|fetish|gore|gory|dismember(?:ment|ed)?|behead(?:ing|ed)?|tortur(?:e|ing)|swastika|nazi|deepfake|revenge porn)\b/i.test(subject.value+' '+context);
get('[data-copy-image-prompt]').disabled=unsafe;
if(unsafe){prompt.value='';get('[data-prompt-status]').textContent='Please choose a family-friendly everyday object, activity or place. This tool cannot prepare that image request.';return false;}
get('[data-prompt-status]').textContent='';prompt.value=`Create one photorealistic communication-card picture. Requested subject: ${subject.value.trim()||'the object I name'}. ${context?`The situation is: ${context}. Use this only to clarify the subject, not as a request for a busy scene. `:''}An AUsome Life aesthetic: Nantucket meets Vermont; refined, preppy New England, natural materials, true-to-life detail, warm daylight, restrained navy, cream and pine green where appropriate. Show one complete familiar object or one clearly recognizable action, centered on a clean white background. Retain the subject's real colors and recognizable shape. No added props, lettering, words, logos, border or collage. Realistic photographic detail, no cartoon or watercolor. Square composition with breathing room. Do not invent a real place, specific person's likeness, or actual product details. For an actual person, entrance, menu item or personal possession, use my supplied reference photograph. The card's familiar word will be added separately underneath. Content requirements: lawful, family-friendly, respectful and non-deceptive. No sexual content, graphic violence, hate imagery, harassment, exploitation, or deceptive real-person images. Preserve dignity; never portray disability as spectacle. Use only original or authorized visual references. Do not copy a protected character, logo, recognizable artwork, branded interface or specific published photograph. Do not remove a watermark or impersonate a person. If a request depends on third-party rights that are not established, offer an original unbranded alternative. Do not describe AI output as copyright-free or legally cleared.`;return true;}
subject.addEventListener('input',setPrompt);situation.addEventListener('input',setPrompt);setPrompt();
async function copyImagePrompt(){
 if(!setPrompt())return false;
 try{await navigator.clipboard.writeText(prompt.value);get('[data-prompt-status]').textContent='Copied. Your prompt is ready.';return true;}
 catch(_){prompt.focus();prompt.select();get('[data-prompt-status]').textContent='Select and copy the prompt below.';return false;}
}
async function generateNewPicture(){
 if(!setPrompt())return;
 const buttons=[...root.querySelectorAll('[data-generate-new-picture]')],genStatus=get('[data-imagegen-status]')||get('[data-prompt-status]');
 buttons.forEach(button=>button.disabled=true);
 if(!imageApi){
  const copied=await copyImagePrompt();
  if(copied){
   genStatus.textContent='Your approved image prompt is copied. Opening ChatGPT now…';
   sessionStorage.setItem('aal-picture-return','1');
   window.location.assign('https://chatgpt.com/');
  }else{
   genStatus.textContent='Your browser blocked automatic copying. Copy the prompt shown below, then use the Open ChatGPT link.';
   let link=get('[data-open-chatgpt]');
   if(!link){
    link=document.createElement('a');
    link.href='https://chatgpt.com/';
    link.className='button secondary';
    link.dataset.openChatgpt='';
    link.textContent='Open ChatGPT';
    get('[data-prompt-status]').after(link);
   }
  }
  buttons.forEach(button=>button.disabled=false);
  return;
 }
 try{
  genStatus.textContent='Creating your picture…';
  const response=await fetch(imageApi,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({subject:subject.value.trim(),situation:situation.value.trim()})});
  const data=await response.json().catch(()=>({}));
  if(!response.ok||!data.imageDataUrl)throw new Error('image generation failed');
  selectedId=null;file.value='';description.value=data.description||subject.value.trim();if(!word.value.trim()&&data.suggestedWord)word.value=String(data.suggestedWord).slice(0,36);
  root.querySelectorAll('[data-card-option]').forEach(button=>button.setAttribute('aria-pressed','false'));
  photo=null;draw();revealEditor();setImage(data.imageDataUrl);
  genStatus.textContent='Your new picture is ready. Add or confirm the familiar word, then save or print.';
 }catch(_){
  genStatus.textContent='We could not create that picture right now. Your words are still here. Try again, use a starter picture, or upload your own photo.';
 }finally{buttons.forEach(button=>button.disabled=false);}
}
get('[data-copy-image-prompt]').addEventListener('click',copyImagePrompt);
root.querySelectorAll('[data-generate-new-picture]').forEach(button=>button.addEventListener('click',generateNewPicture));
window.addEventListener('pagehide',()=>{if(localUrl)URL.revokeObjectURL(localUrl);if(downloadUrl)URL.revokeObjectURL(downloadUrl);});draw();updateSheet();enableExport(false);
})();
