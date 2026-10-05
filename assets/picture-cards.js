/* Local-only picture card editor. No on-site AI image generation. */
(() => {
'use strict';
const root=document.querySelector('[data-picture-desk]');if(!root)return;
const get=s=>root.querySelector(s), canvas=get('#card-canvas'),ctx=canvas.getContext('2d');
const word=get('#card-word'),description=get('#card-description'),status=get('[data-card-status]'),sheet=get('[data-card-sheet]');
const size=get('#card-size'),file=get('#card-photo'),results=get('#card-options'),editor=get('#card-editor');
const catalog=[
 {id:'water',label:'water',description:'A clear glass of drinking water'},
 {id:'break',label:'break',description:'A white armchair with a navy striped cushion'},
 {id:'apple',label:'apple',description:'A whole red apple'},
 {id:'toilet',label:'toilet',description:'A white toilet with its lid raised'},
 {id:'coat',label:'coat',description:'A navy quilted jacket'},
 {id:'car',label:'car',description:'A navy blue family station wagon'}
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
 selectedId=card.id;file.value='';word.value=card.label;description.value=card.description;
 root.querySelectorAll('[data-card-option]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.cardOption===card.id)));
 photo=null;draw();revealEditor();setImage(srcFor(card.id));
}
function showOptions(scroll=true){
 results.hidden=false;
 get('[data-options-title]').textContent='Choose a familiar picture';
 get('[data-options-note]').textContent='Six starter illustrations. The apple means apple; the chair works for a break only if that is familiar to the person.';
 const cards=catalog;const grid=get('[data-picture-options]');grid.replaceChildren();
 cards.forEach(card=>{const button=document.createElement('button'),img=document.createElement('img'),label=document.createElement('span'),hint=document.createElement('small');button.type='button';button.className='studio-picture-option';button.dataset.cardOption=card.id;button.setAttribute('aria-pressed',String(card.id===selectedId));img.src=srcFor(card.id);img.alt='';img.width=180;img.height=150;label.textContent=card.label;hint.textContent=card.id==='break'?'Chair picture · use if familiar':'Use this picture';button.append(img,label,hint);button.addEventListener('click',()=>chooseCard(card));grid.append(button);});
 if(scroll){get('[data-options-title]').focus({preventScroll:true});results.scrollIntoView({behavior:'auto',block:'start'});}
}
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
window.addEventListener('pagehide',()=>{if(localUrl)URL.revokeObjectURL(localUrl);if(downloadUrl)URL.revokeObjectURL(downloadUrl);});draw();updateSheet();enableExport(false);showOptions(false);
})();
