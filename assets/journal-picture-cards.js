/* Purpose-selected symbols only. Never extracts article or family photographs. */
(() => {
'use strict';
const catalog=new Map((window.AALCardCatalog||[]).map(card=>[card.id,card]));
const images=new Map();
function getImage(src){
  if(!images.has(src)) images.set(src,new Promise((resolve,reject)=>{
    const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>{images.delete(src);reject(new Error('The picture could not load. Please try again.'));};img.src=src;
  }));
  return images.get(src);
}
function source(card,img){
  if(card.crop)return card.crop;
  if(Number.isInteger(card.cell)){const w=img.naturalWidth/4,h=img.naturalHeight/4;return [(card.cell%4)*w,Math.floor(card.cell/4)*h,w,h];}
  return [0,0,img.naturalWidth,img.naturalHeight];
}
function drawObject(ctx,card,img,x,y,width,height){
  const [sx,sy,sw,sh]=source(card,img),scale=Math.min(width/sw,height/sh),w=sw*scale,h=sh*scale;
  ctx.drawImage(img,sx,sy,sw,sh,x+(width-w)/2,y+(height-h)/2,w,h);
}
async function render(card){
  const img=await getImage(card.image),canvas=document.createElement('canvas');canvas.width=canvas.height=900;
  const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,900,900);ctx.strokeStyle='#173c4c';ctx.lineWidth=7;ctx.strokeRect(10,10,880,880);
  drawObject(ctx,card,img,55,35,790,685);ctx.beginPath();ctx.moveTo(14,749);ctx.lineTo(886,749);ctx.lineWidth=2;ctx.stroke();
  let size=72;ctx.font='600 '+size+'px Arial,sans-serif';while(ctx.measureText(card.label).width>810&&size>24)ctx.font='600 '+(--size)+'px Arial,sans-serif';
  ctx.fillStyle='#173c4c';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(card.label,450,820);return canvas;
}
document.querySelectorAll('[data-story-cards]').forEach(section=>{
  const status=section.querySelector('[data-story-card-status]');
  section.querySelectorAll('[data-story-card]').forEach(tile=>{
    const card=catalog.get(tile.dataset.storyCard),button=tile.querySelector('[data-story-card-download]');if(!card||!button)return;
    button.hidden=false;
    const preview=tile.querySelector('.aal-pc-image');
    if(card.crop)getImage(card.image).then(img=>{const canvas=document.createElement('canvas');canvas.width=canvas.height=400;canvas.setAttribute('aria-hidden','true');const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,400,400);drawObject(ctx,card,img,0,0,400,400);preview.style.backgroundImage='none';preview.replaceChildren(canvas);}).catch(()=>{});
    button.addEventListener('click',async()=>{
      button.disabled=true;status.textContent='Preparing '+card.label+'…';
      try{const canvas=await render(card),blob=await new Promise((resolve,reject)=>canvas.toBlob(value=>value?resolve(value):reject(new Error('Could not prepare the file.')),'image/png'));
        const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=card.id+'-picture-card.png';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),60000);
        status.textContent=card.label+' PNG is ready. Check your downloads.';
      }catch(error){status.textContent=error.message+' You can also open the card in the collection below.';}
      finally{button.disabled=false;}
    });
  });
});
})();
