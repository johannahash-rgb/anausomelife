/* Enhance reviewed sharing packages, with a simple link-sharing fallback for other stories.
   Captions and permitted downloads remain readable without JavaScript. No data is submitted. */
(() => {
  'use strict';
  function start() {
    const main = document.querySelector('main');
    const heading = main?.querySelector('h1');
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    if (!main || !heading || !canonical) return;
    let page;
    try { page = new URL(canonical, location.origin); } catch (_) { return; }
    if (page.protocol !== 'https:' || !['anausomelife.com','www.anausomelife.com'].includes(page.hostname)) return;
    const isStory = main.querySelector('.aal-story-share,.fn-story,.er-story,.love-body,.journal-prose,.article-body') || /(?:field-note|favorite-places\/|favorite-places-)/.test(page.pathname);
    if (!isStory || page.pathname.startsWith('/media/')) return;
    page.search = ''; page.hash = '';
    const url = page.href;
    const title = heading.textContent.replace(/\s+/g,' ').trim();
    let section = main.querySelector('.aal-story-share');
    if (section?.dataset.aalShareReady) return;
    const authored = Boolean(section);
    if (!section) {
      section = document.createElement('section');
      section.className='aal-story-share';section.setAttribute('aria-labelledby','aal-share-title');
      section.innerHTML='<h2 id="aal-share-title">A story worth passing along.</h2><p>Send it to someone making a plan, or share the link with your readers.</p><div class="aal-story-actions"><button type="button" data-share-native hidden>Share story <svg class="aal-inline-arrow" aria-hidden="true" focusable="false" viewBox="0 0 24 24"><path d="M5 19 19 5M5 5h14v14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></button><button type="button" data-copy-link>Copy story link</button><button type="button" data-copy-caption>Copy caption &amp; credit</button><a data-reuse-link>Request photos or reuse <svg class="aal-inline-arrow" aria-hidden="true" focusable="false" viewBox="0 0 24 24"><path d="M5 19 19 5M5 5h14v14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></a></div><p class="aal-share-status" role="status"></p><div data-share-fallback hidden><label for="aal-share-copy">Select and copy this text</label><textarea id="aal-share-copy" readonly></textarea></div><p class="brand-note">Share the story link freely. For family photographs, excerpts or advertising, ask about permissions and available formats.</p>';
    }
    section.dataset.aalShareReady='true';
    const reviewedCaption=section.querySelector('[data-share-caption]')?.textContent.trim();
    const caption=reviewedCaption || `${title}\nFrom An AUsome Life · @anausomelife\n${url}`;
    const shareText=section.dataset.shareSummary || 'From An AUsome Life';
    const status=section.querySelector('.aal-share-status');
    const fallback=section.querySelector('[data-share-fallback]');
    const field=fallback?.querySelector('textarea') || section.querySelector('textarea');
    const reuse=section.querySelector('[data-reuse-link]');
    if(reuse) reuse.href='/media/?story='+encodeURIComponent(url)+'#sharing';
    async function copy(value,message){
      try { if (!navigator.clipboard?.writeText) throw new Error('clipboard-unavailable');await navigator.clipboard.writeText(value);fallback.hidden=true;status.textContent=message; }
      catch (_) { fallback.hidden=false;field.value=value;field.focus();field.select();status.textContent='Automatic copying is unavailable. The text is selected below for you to copy.'; }
    }
    function bind(selector,value,message){
      const button=section.querySelector(selector);
      if(button){button.hidden=false;button.addEventListener('click',()=>copy(value,message));}
    }
    bind('[data-copy-link]',url,'Story link copied.');
    bind('[data-copy-caption]',caption,'Caption and credit copied.');
    section.querySelectorAll('[data-copy-share-text]').forEach(button=>{
      const id=button.dataset.copyShareText;
      if(!/^[A-Za-z][\w-]*$/.test(id || '')) return;
      const source=section.querySelector('#'+id);
      if(!source?.textContent.trim()) return;
      button.hidden=false;
      button.addEventListener('click',()=>copy(source.textContent.trim(),button.dataset.copyStatus || 'Text copied.'));
    });
    const nativeButton=section.querySelector('[data-share-native]');
    if (typeof navigator.share==='function' && nativeButton) {
      nativeButton.hidden=false;
      nativeButton.addEventListener('click',async()=>{try{await navigator.share({title,text:shareText,url});status.textContent='Story shared.';}catch(error){if(error.name!=='AbortError')await copy(url,'Story link copied.');}});
    }
    if (!authored) {
      const next=main.querySelector('.reader-next');
      if(next) next.before(section);else main.append(section);
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
