/* Self-contained deterministic downloadable picture card for eligible An AUsome Life stories. No AI, no API. */
(() => {
  'use strict';
  function clean(value){ return String(value || '').replace(/\s+/g,' ').trim(); }
  function slugify(value){
    return clean(value).toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')
      .replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'') || 'picture-card';
  }
  function loadImage(src){
    return new Promise((resolve,reject)=>{
      const img=new Image();
      img.decoding='async';
      img.onload=()=>resolve(img);
      img.onerror=reject;
      img.src=src;
    });
  }
  function fitContain(img,x,y,w,h){
    const ratio=Math.min(w/img.naturalWidth,h/img.naturalHeight);
    const dw=img.naturalWidth*ratio,dh=img.naturalHeight*ratio;
    return {x:x+(w-dw)/2,y:y+(h-dh)/2,w:dw,h:dh};
  }
  function wrapLines(ctx,text,maxWidth,maxLines=2){
    const words=clean(text).split(' ').filter(Boolean);
    if(!words.length)return [''];
    const lines=[];let current=words.shift();
    for(const word of words){
      const trial=current+' '+word;
      if(ctx.measureText(trial).width<=maxWidth||lines.length>=maxLines-1)current=trial;
      else{lines.push(current);current=word;}
    }
    lines.push(current);
    if(lines.length>maxLines){
      const overflow=lines.splice(maxLines-1).join(' ');
      lines[maxLines-1]=overflow;
    }
    return lines.slice(0,maxLines);
  }
  async function downloadCard({image,label,place='',description=''}) {
    const img=await loadImage(image);
    const canvas=document.createElement('canvas');
    canvas.width=1200;canvas.height=1200;
    const ctx=canvas.getContext('2d');
    const navy='#173c4c',pine='#2e513f';

    ctx.fillStyle='#fff';ctx.fillRect(0,0,1200,1200);
    ctx.strokeStyle=navy;ctx.lineWidth=14;ctx.strokeRect(16,16,1168,1168);
    ctx.strokeStyle=pine;ctx.lineWidth=3;ctx.strokeRect(34,34,1132,1132);

    const box={x:74,y:72,w:1052,h:770};
    ctx.fillStyle='#fffdf8';ctx.fillRect(box.x,box.y,box.w,box.h);
    const fitted=fitContain(img,box.x,box.y,box.w,box.h);
    ctx.drawImage(img,fitted.x,fitted.y,fitted.w,fitted.h);

    ctx.beginPath();ctx.moveTo(74,878);ctx.lineTo(1126,878);
    ctx.strokeStyle=navy;ctx.lineWidth=3;ctx.stroke();

    const word=clean(label);
    let fontSize=word.length>34?58:74,lines=[];
    for(;fontSize>=46;fontSize-=2){
      ctx.font=`700 ${fontSize}px Arial,Helvetica,sans-serif`;
      lines=wrapLines(ctx,word,1010,2);
      if(lines.every(line=>ctx.measureText(line).width<=1010))break;
    }
    ctx.fillStyle=navy;ctx.textAlign='center';ctx.textBaseline='middle';
    const labelY=place?965:1005,gap=fontSize*1.05,startY=labelY-((lines.length-1)*gap)/2;
    lines.forEach((line,i)=>ctx.fillText(line,600,startY+i*gap));

    if(place){
      ctx.font='400 34px Arial,Helvetica,sans-serif';
      ctx.fillStyle='#52656c';ctx.fillText(clean(place),600,1102);
    }
    canvas.setAttribute('aria-label',description?`${word}: ${clean(description)}`:word);

    const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
    if(!blob)throw new Error('Could not prepare PNG.');
    const url=URL.createObjectURL(blob),a=document.createElement('a');
    a.href=url;a.download=`${slugify(word)}-picture-card.png`;
    document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1500);
  }

  function start(){
    if(document.body.classList.contains('picture-card-page')||document.body.classList.contains('picture-card-library-page'))return;
    const existing=document.querySelector('[data-aal-article-picture-card]');
    if(existing?.dataset.aalArticlePictureCardVersion==='static4')return;
    if(existing)existing.remove();

    const main=document.querySelector('main'),h1=main?.querySelector('h1');
    if(!main||!h1)return;

    const selectors=[
      '.favorite-cover img','.favorite-hero-art img','.hero figure img',
      '.notebook-story-cover img','.coffee-hero figure img','.coffee-hero img',
      '.journal-place-hero img','.field-note-hero img','.er-family-photo img',
      'article > figure img','article figure img','main section figure img'
    ];
    let hero=null;
    for(const selector of selectors){
      const candidate=main.querySelector(selector);
      if(candidate){hero=candidate;break;}
    }
    if(!hero)return;

    const rawSrc=hero.currentSrc||hero.getAttribute('src')||'';
    if(!rawSrc)return;
    const imageUrl=new URL(rawSrc,location.href);
    if(imageUrl.origin!==location.origin)return;

    const exact=document.querySelector('meta[name="aal-picture-card-label"]')?.content?.trim();
    const heading=clean(h1.textContent);
    const isPlace=document.body.classList.contains('favorite-place-page')||document.body.classList.contains('favorite-page');
    let label=exact||heading;
    if(!exact&&isPlace&&label.includes(':'))label=label.split(':')[0].trim();
    if(!exact&&!isPlace&&label.length>34){
      const firstClause=label.split(/[,;:—–]/)[0].trim();
      if(firstClause.length>=4)label=firstClause;
    }
    if(!label)return;

    const place=document.querySelector('meta[name="aal-picture-card-place"]')?.content?.trim()
      ||clean(main.querySelector('.favorite-place-name')?.textContent)
      ||(isPlace?clean(main.querySelector('.hero .lede')?.textContent):'')
      ||'';
    const description=hero.getAttribute('alt')?.trim()||heading;

    if(!document.getElementById('aal-article-picture-card-style')){
      const style=document.createElement('style');
      style.id='aal-article-picture-card-style';
      style.textContent=`
        .aal-article-card-box{margin:18px 0 8px;display:flex;flex-wrap:wrap;gap:10px;align-items:center}
        .aal-article-card-button{appearance:none;border:1px solid #173c4c;background:#fffdf8;color:#173c4c;min-height:44px;padding:10px 15px;font:700 .88rem/1.2 Arial,Helvetica,sans-serif;cursor:pointer}
        .aal-article-card-button:hover{background:#eef2ef}.aal-article-card-button:disabled{opacity:.62;cursor:wait}
        .aal-article-card-note{font:400 .76rem/1.4 Arial,Helvetica,sans-serif;color:#52656c}
        .aal-article-card-status{flex-basis:100%;font:400 .78rem/1.4 Arial,Helvetica,sans-serif;color:#52656c;margin:0}
        @media print{.aal-article-card-box{display:none!important}}
      `;
      document.head.append(style);
    }

    const box=document.createElement('div');
    box.className='aal-article-card-box';box.dataset.aalArticlePictureCard='';box.dataset.aalArticlePictureCardVersion='static4';
    const button=document.createElement('button');
    button.type='button';button.className='aal-article-card-button';button.textContent='Download picture card';
    const note=document.createElement('span');
    note.className='aal-article-card-note';note.textContent='Uses this page’s existing picture · no AI';
    const status=document.createElement('p');
    status.className='aal-article-card-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
    box.append(button,note,status);

    const actionRow=h1.closest('section,article')?.querySelector('.actions');
    if(actionRow)actionRow.insertAdjacentElement('afterend',box);
    else{
      const header=h1.closest('header');
      if(header)header.append(box);
      else h1.insertAdjacentElement('afterend',box);
    }

    window.__AAL_ARTICLE_PICTURE_CARD__=true;

    button.addEventListener('click',async()=>{
      button.disabled=true;status.textContent='Preparing your PNG…';
      try{
        await downloadCard({image:imageUrl.href,label,place,description});
        status.textContent='Picture card ready.';
      }catch(_){
        status.textContent='We could not prepare this card in your browser. Try the ready-made card library instead.';
      }finally{button.disabled=false;}
    });
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
