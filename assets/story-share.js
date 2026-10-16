/* Native link sharing and explicit reuse requests. No visitor data is submitted. */
(() => {
  'use strict';
  function start() {
    const main = document.querySelector('main');
    const heading = main?.querySelector('h1');
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    if (!main || !heading || !canonical || main.querySelector('.aal-story-share')) return;
    const page = new URL(canonical, location.origin);
    if (!['anausomelife.com','www.anausomelife.com'].includes(page.hostname)) return;
    const isStory = main.querySelector('.fn-story,.er-story,.love-body,.journal-prose,.article-body') || /(?:field-note|favorite-places\/|favorite-places-)/.test(page.pathname);
    if (!isStory || page.pathname.startsWith('/media/')) return;
    page.search = ''; page.hash = '';
    const url = page.href;
    const title = heading.textContent.replace(/\s+/g,' ').trim();
    const caption = `${title}\nFrom An AUsome Life · @anausomelife\n${url}`;
    const section = document.createElement('section');
    section.className='aal-story-share';section.setAttribute('aria-labelledby','aal-share-title');
    section.innerHTML='<h2 id="aal-share-title">A story worth passing along.</h2><p>Send it to someone making a plan, or share the link with your readers.</p><div class="aal-story-actions"><button type="button" data-share-native hidden>Share story <svg class="aal-inline-arrow" aria-hidden="true" focusable="false" viewBox="0 0 24 24"><path d="M5 19 19 5M5 5h14v14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></button><button type="button" data-copy-link>Copy story link</button><button type="button" data-copy-caption>Copy caption &amp; credit</button><a data-reuse-link>Request photos or reuse <svg class="aal-inline-arrow" aria-hidden="true" focusable="false" viewBox="0 0 24 24"><path d="M5 19 19 5M5 5h14v14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></a></div><p class="aal-share-status" role="status"></p><div data-share-fallback hidden><label for="aal-share-copy">Select and copy this text</label><textarea id="aal-share-copy" readonly></textarea></div><p class="brand-note">For photo downloads, excerpts, or advertising, ask us about permissions and available formats.</p>';
    const status=section.querySelector('.aal-share-status');
    const fallback=section.querySelector('[data-share-fallback]');
    const field=section.querySelector('textarea');
    section.querySelector('[data-reuse-link]').href='/media/?story='+encodeURIComponent(url)+'#sharing';
    async function copy(value,message){
      try { if (!navigator.clipboard?.writeText) throw new Error('clipboard-unavailable');await navigator.clipboard.writeText(value);fallback.hidden=true;status.textContent=message; }
      catch (_) { fallback.hidden=false;field.value=value;field.focus();field.select();status.textContent='Automatic copying is unavailable. The text is selected below for you to copy.'; }
    }
    section.querySelector('[data-copy-link]').addEventListener('click',()=>copy(url,'Story link copied.'));
    section.querySelector('[data-copy-caption]').addEventListener('click',()=>copy(caption,'Caption and credit copied.'));
    if (typeof navigator.share==='function') {
      const button=section.querySelector('[data-share-native]');button.hidden=false;
      button.addEventListener('click',async()=>{try{await navigator.share({title,text:'From An AUsome Life',url});status.textContent='Story shared.';}catch(error){if(error.name!=='AbortError')await copy(url,'Story link copied.');}});
    }
    main.append(section);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
