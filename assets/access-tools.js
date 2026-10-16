/* Optional reading preferences. No accounts, analytics, remote voices or content uploads. */
(function (factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => api.start(window), {once:true});
  else api.start(window);
})(function () {
  'use strict';
  const KEY = 'aal-reading-preferences-v1';
  const defaults = Object.freeze({size:'100',font:'original',theme:'original',spacing:false,links:false,targets:false,motion:false,guide:false,guidePosition:'45',remember:false});
  function normalize(value) {
    const input = value && typeof value === 'object' && !Array.isArray(value) ? value : {};
    const p = {...defaults};
    const choices = {size:['100','125','150','175','200'],font:['original','plain'],theme:['original','light','dark','warm']};
    Object.keys(choices).forEach(k => { if (choices[k].includes(String(input[k]))) p[k] = String(input[k]); });
    ['spacing','links','targets','motion','guide','remember'].forEach(k => { p[k] = input[k] === true; });
    if (Number.isFinite(Number(input.guidePosition))) p.guidePosition = String(Math.min(90,Math.max(10,Number(input.guidePosition))));
    return p;
  }
  function chunks(text, limit=180) {
    const words = String(text).replace(/\s+/g,' ').trim().split(' ').filter(Boolean), result=[];
    let current='';
    for (let word of words) {
      if (current && current.length+word.length+1 > limit) { result.push(current);current=''; }
      while (word.length > limit) { result.push(word.slice(0,limit));word=word.slice(limit); }
      if (word) current += (current?' ':'')+word;
      if (/[.!?]$/.test(current) && current.length>60) { result.push(current);current=''; }
    }
    if (current) result.push(current);
    return result;
  }
  function safeHref(href, base) {
    if(typeof href!=='string'||!href.trim())return null;
    try { const url=new URL(href,base); return ['http:','https:','mailto:','tel:'].includes(url.protocol)?url.href:null; }
    catch (_) { return null; }
  }
  function start(win) {
    const doc=win.document, root=doc.documentElement, main=doc.querySelector('main');
    if (!main || win.__AAL_ACCESS_TOOLS__) return;
    win.__AAL_ACCESS_TOOLS__=true;
    let prefs={...defaults}, storageAvailable=true, launchTarget=null, readerTarget=null;
    try { const saved=normalize(JSON.parse(win.localStorage.getItem(KEY)||'null')); if(saved.remember) prefs=saved; }
    catch (_) { storageAvailable=false; }
    const make=(tag,attrs={},text)=>{const e=doc.createElement(tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text!==undefined)e.textContent=text;return e;};
    const panel=make('dialog',{id:'aal-access-panel',class:'aal-access-dialog','aria-labelledby':'aal-access-title'});
    const reader=make('dialog',{id:'aal-reader',class:'aal-access-dialog aal-reader','aria-labelledby':'aal-reader-title'});
    const bar=make('div',{class:'aal-access-bar','data-aal-access-ui':''});
    const launch=make('button',{type:'button','data-aal-open-access':'','aria-haspopup':'dialog','aria-controls':'aal-access-panel'},'Accessibility & reading');
    const status=make('p',{class:'aal-access-status',role:'status','aria-live':'polite','aria-atomic':'true'});
    const line=make('div',{class:'aal-reading-guide','aria-hidden':'true'});line.hidden=true;
    const announce=text=>{status.textContent=text;};
    panel.innerHTML=`<div class="aal-access-heading"><div><p class="aal-access-kicker">Make yourself comfortable</p><h2 id="aal-access-title" tabindex="-1">Accessibility &amp; reading</h2></div><button type="button" data-close-panel>Close</button></div>
      <p class="aal-access-intro">Choose what helps. Changes apply here immediately; you can reset them any time.</p>
      <form class="aal-access-form">
      <fieldset><legend>Text &amp; color</legend><div class="aal-access-fields">
        <label for="aal-size">Text size<select id="aal-size" data-pref="size"><option value="100">Original · 100%</option><option value="125">Larger · 125%</option><option value="150">Larger · 150%</option><option value="175">Larger · 175%</option><option value="200">Largest · 200%</option></select></label>
        <label for="aal-font">Typeface<select id="aal-font" data-pref="font"><option value="original">Original type</option><option value="plain">Plain sans serif</option></select></label>
        <label for="aal-theme">Page colors<select id="aal-theme" data-pref="theme"><option value="original">Original colors</option><option value="light">High contrast · light</option><option value="dark">High contrast · dark</option><option value="warm">Warm paper</option></select></label></div>
        <label class="aal-access-check"><input type="checkbox" data-pref="spacing"> <span>More space between letters, words &amp; lines</span></label>
        <label class="aal-access-check"><input type="checkbox" data-pref="links"> <span>Underline links in the page</span></label>
      </fieldset>
      <details class="aal-access-options"><summary>Movement, focus &amp; controls</summary><div>
        <label class="aal-access-check"><input type="checkbox" data-pref="motion"> <span>Reduce motion &amp; pause autoplay media</span></label><p class="aal-access-note">Your device’s reduced-motion setting is also respected. You can still play a video yourself.</p>
        <label class="aal-access-check"><input type="checkbox" data-pref="targets"> <span>Make buttons &amp; controls larger</span></label>
        <label class="aal-access-check"><input type="checkbox" data-pref="guide"> <span>Show a reading line</span></label>
        <div data-guide-options hidden><label for="aal-guide-position">Reading line position</label><input id="aal-guide-position" type="range" min="10" max="90" step="5" data-pref="guidePosition" aria-describedby="aal-guide-help"><p id="aal-guide-help" class="aal-access-note">Move your pointer over text, or tap beside text on a touch screen. You can also use the arrow keys on this slider.</p></div>
      </div></details>
      <fieldset><legend>Read &amp; find your place</legend><div class="aal-access-actions"><button type="button" data-open-reader>Open reading view</button><button type="button" data-skip-main>Skip to main content</button></div><p class="aal-access-note">Reading view keeps the page’s words and links. Interactive tools stay on the original page. Read aloud is available there when your browser provides a device voice.</p>
        <label for="aal-heading-select">Jump to a section</label><div class="aal-heading-jump"><select id="aal-heading-select"><option value="">Choose a heading</option></select><button type="button" data-jump>Go</button></div>
      </fieldset>
      <div class="aal-access-memory"><label class="aal-access-check"><input type="checkbox" data-pref="remember"> <span>Remember my choices on this device</span></label><p class="aal-access-note" data-storage-note>Optional. Stored in this browser only. Leave off on a shared device.</p></div>
      <div class="aal-access-actions"><button type="button" data-reset>Reset all choices</button><button type="button" data-close-panel>Done</button></div></form>
      <p class="aal-access-note"><a href="/accessibility.html#reading-tools">Help &amp; access information</a> · <a href="mailto:hello@anausomelife.com?subject=Website%20access%20feedback">Tell us what could work better</a></p>`;
    panel.append(status);
    reader.innerHTML=`<div class="aal-access-heading"><div><p class="aal-access-kicker">Reading view</p><h2 id="aal-reader-title" tabindex="-1">A little more room to read</h2></div><button type="button" data-close-reader>Back to page</button></div><p class="aal-access-note">The page’s text, links and image descriptions. Forms and interactive tools remain on the original page.</p>
      <details class="aal-reader-controls"><summary>Listen, copy or print</summary><div>
      <div class="aal-access-fields"><label for="aal-voice">Device voice<select id="aal-voice"></select></label><label for="aal-rate">Reading speed<select id="aal-rate"><option value="0.8">Slower</option><option value="1" selected>Normal</option><option value="1.2">Faster</option></select></label></div>
      <div class="aal-access-actions"><button type="button" data-speak disabled>Read aloud</button><button type="button" data-pause disabled>Pause</button><button type="button" data-stop disabled>Stop</button><button type="button" data-copy>Copy reading text</button><button type="button" data-print-reader>Print reading view</button></div><p class="aal-access-note" data-voice-note></p><p class="aal-access-note">Listening starts only when you choose it. Continue restarts the current passage; closing this view stops speech.</p><p role="status" aria-live="polite" aria-atomic="true" data-reader-status></p><div data-copy-fallback hidden><label for="aal-reader-copy">Select and copy the reading text</label><textarea id="aal-reader-copy" readonly></textarea></div></div></details><div class="aal-reader-content"></div>`;
    bar.append(launch);
    const navigation=doc.querySelector('.aal-wayfinder')||doc.querySelector('.mag-masthead,.masthead');
    if(navigation)navigation.after(bar);else main.before(bar);
    doc.body.append(panel,reader,line);
    if(typeof panel.showModal==='function')doc.querySelectorAll('[data-aal-open-access]').forEach(button=>button.hidden=false);
    const controls=[...panel.querySelectorAll('[data-pref]')], headingSelect=panel.querySelector('#aal-heading-select');
    const readerContent=reader.querySelector('.aal-reader-content'), readerStatus=reader.querySelector('[data-reader-status]');
    const focus=e=>{if(!e)return;if(!e.hasAttribute('tabindex')&&!e.matches('button,input,select,textarea,a[href]'))e.setAttribute('tabindex','-1');e.focus({preventScroll:true});};
    const visible=e=>{for(let p=e;p;p=p.parentElement){if(p.hidden||p.getAttribute('aria-hidden')==='true')return false;if(p.tagName==='DETAILS'&&!p.open&&p!==e&&!p.querySelector('summary')?.contains(e))return false;const s=win.getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden')return false;}return true;};
    function sync(){controls.forEach(c=>{const v=prefs[c.dataset.pref];if(c.type==='checkbox')c.checked=v;else c.value=v;});panel.querySelector('[data-guide-options]').hidden=!prefs.guide;}
    function save(){
      try { if(prefs.remember)win.localStorage.setItem(KEY,JSON.stringify(prefs));else win.localStorage.removeItem(KEY);storageAvailable=true; }
      catch(_){storageAvailable=false;}
      panel.querySelector('[data-storage-note]').textContent=storageAvailable?(prefs.remember?'Choices saved in this browser. Uncheck to remove them.':'Choices apply to this page. Nothing is saved for your next visit.'):'This browser is not allowing saved preferences. Your choices still work on this page.';
    }
    const reduced=win.matchMedia?win.matchMedia('(prefers-reduced-motion: reduce)'):null;
    function quietMedia(){if(!prefs.motion&&!reduced?.matches)return;doc.querySelectorAll('video[autoplay],audio[autoplay]').forEach(media=>{try{media.pause();media.controls=true;}catch(_){}});}
    function apply(){
      ['size','font','theme'].forEach(k=>root.setAttribute('data-aal-'+k,prefs[k]));
      ['spacing','links','targets','motion'].forEach(k=>root.toggleAttribute('data-aal-'+k,prefs[k]));
      root.style.setProperty('--aal-text-scale',prefs.size+'%');
      line.hidden=!prefs.guide;line.style.top=prefs.guidePosition+'vh';
      quietMedia();sync();
    }
    function closePanel(restore=true){panel.close();if(restore)focus(launchTarget?.isConnected?launchTarget:launch);}
    function refreshHeadings(){
      headingSelect.replaceChildren(make('option',{value:''},'Choose a heading'));
      [...main.querySelectorAll('h1,h2,h3')].filter(visible).slice(0,100).forEach((h,i)=>{if(!h.id){let id='aal-jump-'+i;while(doc.getElementById(id))id+='x';h.id=id;}headingSelect.append(make('option',{value:h.id},h.textContent.trim()));});
    }
    function openPanel(target){
      if(typeof panel.showModal!=='function'){win.location.href='/accessibility.html#reading-tools';return;}
      doc.querySelectorAll('dialog[open]').forEach(d=>{if(d!==panel&&typeof d.close==='function')d.close();});
      launchTarget=target||launch;refreshHeadings();sync();panel.showModal();focus(panel.querySelector('h2'));panel.scrollTop=0;
    }
    function jump(target){closePanel(false);target.scrollIntoView({block:'start',behavior:'auto'});focus(target);}
    panel.querySelector('form').addEventListener('submit',e=>e.preventDefault());
    panel.querySelectorAll('[data-close-panel]').forEach(b=>b.addEventListener('click',()=>closePanel()));
    panel.addEventListener('cancel',e=>{e.preventDefault();closePanel();});
    controls.forEach(c=>c.addEventListener(c.type==='range'?'input':'change',()=>{prefs=normalize({...prefs,[c.dataset.pref]:c.type==='checkbox'?c.checked:c.value});apply();save();if(c.type!=='range')announce('Choices applied.');}));
    panel.querySelector('[data-reset]').addEventListener('click',()=>{prefs={...defaults};apply();save();announce('All reading choices reset. Your device’s own access settings still apply.');});
    panel.querySelector('[data-skip-main]').addEventListener('click',()=>jump(main));
    panel.querySelector('[data-jump]').addEventListener('click',()=>{const target=doc.getElementById(headingSelect.value);if(target&&main.contains(target))jump(target);else{announce('Choose a section first.');headingSelect.focus();}});
    doc.addEventListener('click',e=>{const target=e.target.closest('[data-aal-open-access]');if(target){e.preventDefault();openPanel(target);}});
    const footer=doc.querySelector('footer nav')||doc.querySelector('footer');
    if(footer){const f=make('button',{type:'button',class:'aal-access-footer','data-aal-open-access':'','aria-haspopup':'dialog','aria-controls':'aal-access-panel'},'Reading tools');footer.append(f);}
    function followPointer(e){if(!prefs.guide||doc.querySelector('dialog[open]')||!main.contains(e.target)||e.target.closest('a,button,input,select,textarea,summary,[role="button"]'))return;if(e.type==='pointermove'&&e.pointerType==='touch')return;line.style.top=Math.max(24,Math.min(win.innerHeight-24,e.clientY))+'px';}
    doc.addEventListener('pointermove',followPointer,{passive:true});doc.addEventListener('pointerup',followPointer,{passive:true});
    reduced?.addEventListener?.('change',quietMedia);quietMedia();
    doc.addEventListener('loadedmetadata',quietMedia,true);
    const skipTags=new Set(['SCRIPT','STYLE','FORM','BUTTON','INPUT','SELECT','TEXTAREA','NAV','DIALOG','TEMPLATE','NOSCRIPT','SVG','CANVAS','IFRAME','OBJECT','EMBED']);
    const keepTags=new Set(['H1','H2','H3','H4','H5','H6','P','UL','OL','LI','DL','DT','DD','BLOCKQUOTE','STRONG','EM','B','I','A','BR','TABLE','THEAD','TBODY','TR','TH','TD','CAPTION','FIGCAPTION','CODE','PRE','HR']);
    function copyReadable(node,parent){
      if(node.nodeType===3){parent.append(doc.createTextNode(node.textContent));return;}
      if(node.nodeType!==1||skipTags.has(node.tagName)||!visible(node)||node.closest('.aal-story-share,[data-aal-access-ui],[contenteditable],.copy-fallback,.print-field,[data-planner]'))return;
      if(node.tagName==='IMG'){const alt=(node.getAttribute('alt')||'').trim();if(alt)parent.append(make('p',{class:'aal-reader-image-note'},'Image description: '+alt));return;}
      if(['AUDIO','VIDEO'].includes(node.tagName)){parent.append(make('p',{},'Audio or video is available on the original page.'));return;}
      if(node.tagName==='DETAILS'&&!node.open){const summary=node.querySelector('summary');if(summary)parent.append(make('p',{},'Expandable section on the original page: '+summary.textContent.trim()));return;}
      let target=parent;
      if(keepTags.has(node.tagName)){
        target=make(node.tagName.toLowerCase());
        if(node.tagName==='A'){const href=safeHref(node.getAttribute('href'),win.location.href);if(href)target.setAttribute('href',href);}
        if(node.tagName==='TH')target.setAttribute('scope',node.getAttribute('scope')==='row'?'row':'col');
        if(['TD','TH'].includes(node.tagName))['colspan','rowspan'].forEach(a=>{const n=Number(node.getAttribute(a));if(Number.isInteger(n)&&n>1&&n<100)target.setAttribute(a,String(n));});
        if(node.tagName==='OL'&&node.getAttribute('start'))target.setAttribute('start',node.getAttribute('start'));
        if(node.getAttribute('lang'))target.setAttribute('lang',node.getAttribute('lang'));
        if(['ltr','rtl'].includes(node.getAttribute('dir')))target.setAttribute('dir',node.getAttribute('dir'));
        parent.append(target);
      }
      [...node.childNodes].forEach(child=>copyReadable(child,target));
    }
    function readingText(){return (readerContent.innerText||readerContent.textContent||'').trim();}
    let voices=[],speechIndex=0,speechParts=[],speechMode='stopped',speechToken=0,utterance=null;
    const synth=win.speechSynthesis, voiceSelect=reader.querySelector('#aal-voice'),rateSelect=reader.querySelector('#aal-rate');
    const speak=reader.querySelector('[data-speak]'),pause=reader.querySelector('[data-pause]'),stop=reader.querySelector('[data-stop]');
    function speechUI(){speak.disabled=!voices.length||speechMode==='reading';speak.textContent=speechMode==='paused'?'Continue':'Read aloud';pause.disabled=speechMode!=='reading';stop.disabled=speechMode==='stopped';voiceSelect.disabled=speechMode==='reading'||!voices.length;rateSelect.disabled=speechMode==='reading';}
    function stopSpeech(message=''){speechToken++;if(utterance&&synth)synth.cancel();utterance=null;speechMode='stopped';speechIndex=0;speechUI();if(message)readerStatus.textContent=message;}
    function updateVoices(){
      const before=voiceSelect.value;
      try{voices=synth&&typeof synth.getVoices==='function'&&typeof win.SpeechSynthesisUtterance==='function'?synth.getVoices().filter(v=>v.localService===true):[];}catch(_){voices=[];}
      voices.sort((a,b)=>Number(b.lang.toLowerCase().startsWith((root.lang||'en').slice(0,2).toLowerCase()))-Number(a.lang.toLowerCase().startsWith((root.lang||'en').slice(0,2).toLowerCase())));
      voiceSelect.replaceChildren();voices.forEach((v,i)=>voiceSelect.append(make('option',{value:String(i)},v.name+' · '+v.lang)));
      if(!voices.length)voiceSelect.append(make('option',{value:''},'No device voice available'));
      else if(before!==''&&Number(before)<voices.length)voiceSelect.value=before;
      reader.querySelector('[data-voice-note]').textContent=voices.length?'Uses a voice your browser identifies as running on this device. No reading text is sent to this website.':'Read aloud is unavailable here because the browser has not provided a local device voice. You can still use reading view or your device’s built-in spoken-content tools.';
      speechUI();
    }
    function nextSpeech(token){
      if(token!==speechToken||speechMode!=='reading')return;
      if(speechIndex>=speechParts.length){utterance=null;speechMode='stopped';speechIndex=0;speechUI();readerStatus.textContent='Finished reading.';return;}
      const voice=voices[Number(voiceSelect.value)];if(!voice){stopSpeech('That device voice is no longer available.');return;}
      utterance=new win.SpeechSynthesisUtterance(speechParts[speechIndex]);utterance.voice=voice;utterance.lang=voice.lang;utterance.rate=Number(rateSelect.value)||1;
      utterance.onend=()=>{if(token===speechToken){speechIndex++;nextSpeech(token);}};
      utterance.onerror=()=>{if(token===speechToken)stopSpeech('Reading stopped. You can try again or use your device’s spoken-content tools.');};
      try{synth.speak(utterance);}catch(_){stopSpeech('This browser could not start the device voice.');}
    }
    speak.addEventListener('click',()=>{updateVoices();if(!voices.length)return;if(speechMode!=='paused'){speechParts=chunks(readingText());speechIndex=0;}if(!speechParts.length){readerStatus.textContent='There is no reading text on this page.';return;}speechMode='reading';speechUI();readerStatus.textContent='Reading aloud.';nextSpeech(++speechToken);});
    pause.addEventListener('click',()=>{speechToken++;if(synth)synth.cancel();utterance=null;speechMode='paused';speechUI();readerStatus.textContent='Paused. Continue will restart this passage.';});
    stop.addEventListener('click',()=>stopSpeech('Reading stopped.'));
    synth?.addEventListener?.('voiceschanged',updateVoices);updateVoices();
    function closeReader(){stopSpeech();reader.close();focus(readerTarget?.isConnected?readerTarget:launch);}
    reader.querySelector('[data-close-reader]').addEventListener('click',closeReader);
    reader.addEventListener('cancel',e=>{e.preventDefault();closeReader();});
    reader.addEventListener('close',()=>{stopSpeech();doc.body.classList.remove('aal-print-reader');});
    win.addEventListener('pagehide',()=>stopSpeech());doc.addEventListener('visibilitychange',()=>{if(doc.hidden)stopSpeech();});
    panel.querySelector('[data-open-reader]').addEventListener('click',()=>{
      readerTarget=launchTarget||launch;readerContent.replaceChildren();[...main.childNodes].forEach(n=>copyReadable(n,readerContent));
      readerStatus.textContent='';reader.querySelector('[data-copy-fallback]').hidden=true;updateVoices();closePanel(false);reader.showModal();reader.scrollTop=0;focus(reader.querySelector('h2'));
    });
    readerContent.addEventListener('click',e=>{const link=e.target.closest('a[href]');if(!link)return;const url=new URL(link.href);if(url.origin===win.location.origin&&url.pathname===win.location.pathname&&url.hash){let id;try{id=decodeURIComponent(url.hash.slice(1));}catch(_){return;}const target=doc.getElementById(id);if(target){e.preventDefault();closeReader();target.scrollIntoView({block:'start',behavior:'auto'});focus(target);}}});
    reader.querySelector('[data-copy]').addEventListener('click',async()=>{
      const text=readingText()+'\n\n'+win.location.origin+win.location.pathname;
      try{if(!win.navigator.clipboard?.writeText)throw Error();await win.navigator.clipboard.writeText(text);readerStatus.textContent='Reading text copied.';reader.querySelector('[data-copy-fallback]').hidden=true;}
      catch(_){reader.querySelector('[data-copy-fallback]').hidden=false;const area=reader.querySelector('textarea');area.value=text;area.focus();area.select();readerStatus.textContent='Automatic copying is unavailable. Select and copy the text below.';}
    });
    reader.querySelector('[data-print-reader]').addEventListener('click',()=>{stopSpeech();doc.body.classList.add('aal-print-reader');win.print();});
    win.addEventListener('afterprint',()=>doc.body.classList.remove('aal-print-reader'));
    // Modal containment also covers browsers that let tabbing reach browser chrome.
    [panel,reader].forEach(dialog=>dialog.addEventListener('keydown',e=>{
      if(e.key!=='Tab')return;const items=[...dialog.querySelectorAll('a[href],button,input,select,textarea,summary,[tabindex="0"]')].filter(x=>!x.disabled&&visible(x));
      const first=items[0],last=items[items.length-1];if(!first){e.preventDefault();return;}
      if(e.shiftKey&&(doc.activeElement===first||doc.activeElement===dialog.querySelector('h2'))){e.preventDefault();last.focus();}
      else if(!e.shiftKey&&doc.activeElement===last){e.preventDefault();first.focus();}
    }));
    apply();
    if(!storageAvailable)panel.querySelector('[data-storage-note]').textContent='Saved preferences are unavailable in this browser. Your choices still work on this page.';
    if(prefs.remember&&storageAvailable)panel.querySelector('[data-storage-note]').textContent='Your saved choices are active in this browser. Uncheck to remove them.';
  }
  return {normalize,chunks,safeHref,start,KEY};
});
