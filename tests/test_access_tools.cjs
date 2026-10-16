/* DOM behavior tests. These do not simulate layout or replace browser/AT testing. */
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {parseHTML}=require('linkedom');
const api=require('../assets/access-tools.js');

function setup({storage=new Map(),blocked=false,local=true,voiceError=false,nativeDialog=true,reduced=false}={}){
  const {window:dom,document:doc}=parseHTML(`<!doctype html><html lang="en"><head></head><body>
  <header class="mag-masthead">Site</header><nav class="aal-wayfinder">Navigation</nav>
  <main id="main"><h1>A useful story</h1><p>Walk by the sea. Bring a warm coat and take a comfortable break along the path.</p>
  <h2 id="arrival">Arrival</h2><div>Text outside a paragraph.</div><p><a href="/calendar.html">Calendar</a> <a href="#arrival">Arrival details</a> <a href="javascript:alert(1)">Unsafe</a> <a id="marker">Marker</a></p>
  <ul><li>Bring water.<p>Take a break.</p></li></ul><img src="coast.webp" alt="A quiet seaside path"><img alt="">
  <form><label>Name<input value="PRIVATE INPUT"></label><p>PRIVATE FORM</p></form><textarea>PRIVATE TEXTAREA</textarea>
  <div contenteditable="true">PRIVATE EDITOR</div><p hidden>PRIVATE HIDDEN</p><p aria-hidden="true">PRIVATE ARIA</p>
  <details><summary>More details</summary><h2>Closed heading</h2><p>PRIVATE COLLAPSED</p></details>
  <script>PRIVATE SCRIPT</script><div style="display:none">PRIVATE STYLE</div><video autoplay></video></main><footer><nav></nav></footer>
  </body></html>`);
  const win={document:doc,Event:dom.Event,HTMLElement:dom.HTMLElement,HTMLSelectElement:dom.HTMLSelectElement,addEventListener:(...args)=>doc.addEventListener(...args)};
  let location=new URL('https://anausomelife.com/example.html');
  win.location={get href(){return location.href;},set href(v){location=new URL(v,location);},get pathname(){return location.pathname;},get hash(){return location.hash;},get origin(){return location.origin;}};win.innerHeight=640;
  Object.defineProperty(doc,'activeElement',{get(){return this._focus||this.body;},configurable:true});
  win.HTMLElement.prototype.focus=function(){this.ownerDocument._focus=this;};
  win.HTMLElement.prototype.select=function(){this._selected=true;};
  win.HTMLElement.prototype.scrollIntoView=function(){this._scrolled=true;};
  Object.defineProperty(win.HTMLElement.prototype,'open',{get(){return this.hasAttribute('open');},set(v){this.toggleAttribute('open',!!v);},configurable:true});
  win.HTMLElement.prototype.showModal=nativeDialog?function(){this.open=true;}:undefined;
  win.HTMLElement.prototype.close=function(){this.open=false;this.dispatchEvent(new win.Event('close'));};
  // LinkeDOM models markup; native select mutation, focus and dialogs are shimmed.
  Object.defineProperty(win.HTMLSelectElement.prototype,'value',{configurable:true,get(){return this.querySelector('option[selected]')?.value||this.querySelector('option')?.value||'';},set(v){this.querySelectorAll('option').forEach(o=>o.toggleAttribute('selected',o.value===String(v)));}});
  win.getComputedStyle=e=>({display:e.style.display||'block',visibility:e.style.visibility||'visible'});
  win.localStorage={getItem(k){if(blocked)throw Error('blocked');return storage.get(k)||null;},setItem(k,v){if(blocked)throw Error('blocked');storage.set(k,v);},removeItem(k){if(blocked)throw Error('blocked');storage.delete(k);}};
  win.matchMedia=()=>({matches:reduced,addEventListener(){}});
  const spoken=[];let cancels=0,mediaPauses=0,prints=0,copied='';
  doc.querySelector('video').pause=()=>mediaPauses++;
  win.SpeechSynthesisUtterance=function(text){this.text=text;};
  win.speechSynthesis={getVoices(){if(voiceError)throw Error('voice denied');return [{name:'Remote',lang:'en-US',localService:false},...(local?[{name:'On device',lang:'en-US',localService:true}]:[])];},speak(u){spoken.push(u);},cancel(){cancels++;},addEventListener(){}};
  Object.defineProperty(win,'navigator',{configurable:true,value:{clipboard:{writeText:async t=>{copied=t;}}}});
  win.print=()=>prints++;
  api.start(win);
  const q=s=>doc.querySelector(s);
  const click=s=>q(s).dispatchEvent(new win.Event('click',{bubbles:true,cancelable:true}));
  const set=(k,v)=>{const e=q(`[data-pref="${k}"]`);if(e.type==='checkbox')e.checked=v;else e.value=v;e.dispatchEvent(new win.Event(e.type==='range'?'input':'change',{bubbles:true}));};
  const key=(el,key,shiftKey=false)=>{const event=new win.Event('keydown',{bubbles:true,cancelable:true});event.key=key;event.shiftKey=shiftKey;el.dispatchEvent(event);return event;};
  return {win,doc,q,click,set,key,storage,spoken,get cancels(){return cancels;},get mediaPauses(){return mediaPauses;},get prints(){return prints;},get copied(){return copied;}};
}

test('malformed preferences cannot introduce values or activate opt-in storage',()=>{
  assert.equal(api.normalize(null).remember,false);assert.equal(api.normalize([]).size,'100');
  assert.equal(api.normalize({size:'999',theme:'url(secret)',remember:'true'}).theme,'original');
  assert.equal(api.normalize({guidePosition:999}).guidePosition,'90');
  assert.equal(api.normalize({size:150}).size,'150');
  assert.equal(api.safeHref('javascript:alert(1)','https://anausomelife.com'),null);
  assert.equal(api.safeHref(null,'https://anausomelife.com'),null);
  assert.equal(api.safeHref('/calendar.html','https://anausomelife.com/x'),'https://anausomelife.com/calendar.html');
  const parts=api.chunks('A long readable passage. '.repeat(30));
  assert.ok(parts.length>1);assert.ok(parts.every(p=>p.length<=180));assert.equal(parts.join(' '),'A long readable passage. '.repeat(30).trim());
});

test('settings apply without saving; consent persists; reset removes saved choices',()=>{
  const t=setup();assert.equal(t.storage.size,0);t.set('size','200');t.set('theme','dark');t.set('spacing',true);
  assert.equal(t.doc.documentElement.dataset.aalSize,'200');assert.ok(t.doc.documentElement.hasAttribute('data-aal-spacing'));assert.equal(t.storage.size,0);
  t.set('remember',true);assert.equal(JSON.parse(t.storage.get(api.KEY)).theme,'dark');
  t.set('remember',false);assert.equal(t.storage.size,0);
  t.set('remember',true);t.click('[data-reset]');assert.equal(t.storage.size,0);assert.equal(t.doc.documentElement.dataset.aalSize,'100');assert.ok(!t.doc.documentElement.hasAttribute('data-aal-spacing'));
});

test('stored settings restore only with explicit opt-in; blocked storage is nonfatal',()=>{
  let t=setup({storage:new Map([[api.KEY,JSON.stringify({theme:'dark',size:'150',remember:true})]])});assert.equal(t.doc.documentElement.dataset.aalTheme,'dark');
  t=setup({storage:new Map([[api.KEY,JSON.stringify({theme:'dark',remember:false})]])});assert.equal(t.doc.documentElement.dataset.aalTheme,'original');
  t=setup({storage:new Map([[api.KEY,'{bad JSON']])});assert.equal(t.doc.documentElement.dataset.aalSize,'100');
  t=setup({blocked:true});t.set('size','175');t.set('remember',true);assert.equal(t.doc.documentElement.dataset.aalSize,'175');assert.match(t.q('[data-storage-note]').textContent,/not allowing saved/);
});

test('one discreet entry, labels, modal focus, escape and section navigation',()=>{
  const t=setup();api.start(t.win);assert.equal(t.doc.querySelectorAll('.aal-access-bar').length,1);
  assert.ok(t.q('.aal-wayfinder').nextElementSibling.matches('.aal-access-bar'));
  t.click('.aal-access-bar button');assert.ok(t.q('#aal-access-panel').open);assert.equal(t.doc.activeElement.id,'aal-access-title');
  for(const input of t.doc.querySelectorAll('input,select,textarea')){
    if(input.closest('main'))continue;
    assert.ok(input.closest('label')||t.q(`label[for="${input.id}"]`),'Every field has a visible label');
  }
  assert.ok(!t.q('#aal-heading-select').textContent.includes('Closed heading'));
  t.q('#aal-access-panel').dispatchEvent(new t.win.Event('cancel',{cancelable:true}));assert.ok(!t.q('#aal-access-panel').open);assert.ok(t.doc.activeElement.matches('.aal-access-bar button'));
  t.click('.aal-access-bar button');t.q('#aal-heading-select').value='arrival';t.click('[data-jump]');assert.equal(t.doc.activeElement.id,'arrival');assert.ok(t.q('#arrival')._scrolled);
});

test('focus wraps without entering controls inside closed disclosures',()=>{
  const t=setup();t.click('.aal-access-bar button');const first=t.q('[data-close-panel]'),last=t.q('#aal-access-panel a:last-child');
  last.focus();assert.ok(t.key(last,'Tab').defaultPrevented);assert.equal(t.doc.activeElement,first);
  first.focus();t.key(first,'Tab',true);assert.equal(t.doc.activeElement,last);
  t.click('[data-open-reader]');const back=t.q('[data-close-reader]');back.focus();t.key(back,'Tab');assert.equal(t.doc.activeElement,back); // Native Tab advances to summary; no false trap.
  t.q('.aal-reader-content').querySelectorAll('a').forEach(a=>a.removeAttribute('href'));
  const summary=t.q('.aal-reader-controls summary');summary.focus();assert.ok(t.key(summary,'Tab').defaultPrevented);assert.equal(t.doc.activeElement,back);
});

test('reading view retains useful text and safe links while excluding private inputs',()=>{
  const t=setup();t.click('.aal-access-bar button');t.click('[data-open-reader]');const content=t.q('.aal-reader-content');
  assert.ok(t.q('#aal-reader').open);assert.ok(!t.q('#aal-access-panel').open);assert.match(content.textContent,/Text outside a paragraph/);assert.match(content.textContent,/Image description: A quiet seaside path/);
  assert.doesNotMatch(content.textContent,/PRIVATE/);assert.equal(content.querySelector('a').getAttribute('href'),'https://anausomelife.com/calendar.html');
  assert.equal([...content.querySelectorAll('a')].find(a=>a.textContent==='Unsafe').hasAttribute('href'),false);
  assert.equal([...content.querySelectorAll('a')].find(a=>a.textContent==='Marker').hasAttribute('href'),false);
  assert.equal(content.querySelectorAll('input,textarea,form,script,[contenteditable]').length,0);
  t.click('[data-close-reader]');assert.ok(t.doc.activeElement.matches('.aal-access-bar button'));
});

test('speech uses only local voices, starts on request, pauses, resumes and cancels',()=>{
  const t=setup();assert.equal(t.spoken.length,0);t.click('.aal-access-bar button');t.click('[data-open-reader]');
  assert.equal(t.q('#aal-voice').options.length,1);assert.doesNotMatch(t.q('#aal-voice').textContent,/Remote/);
  t.click('[data-speak]');assert.equal(t.spoken.length,1);assert.equal(t.spoken[0].voice.localService,true);const first=t.spoken[0];
  t.click('[data-pause]');assert.equal(t.q('[data-speak]').textContent,'Continue');assert.equal(t.cancels,1);first.onend();assert.equal(t.spoken.length,1);
  t.click('[data-speak]');assert.equal(t.spoken[1].text,first.text);t.spoken[1].onend();assert.equal(t.spoken.length,3);
  t.click('[data-close-reader]');assert.ok(t.cancels>=2);const count=t.spoken.length;t.spoken.at(-1).onend();assert.equal(t.spoken.length,count);
});

test('unavailable or blocked voices leave reader usable with an explanation',()=>{
  for(const config of [{local:false},{voiceError:true}]){const t=setup(config);t.click('.aal-access-bar button');t.click('[data-open-reader]');assert.ok(t.q('[data-speak]').disabled);assert.match(t.q('[data-voice-note]').textContent,/unavailable/);assert.match(t.q('.aal-reader-content').textContent,/A useful story/);}
});

test('copy excludes private fields, has a selectable fallback, and print cleans up',async()=>{
  const t=setup();t.click('.aal-access-bar button');t.click('[data-open-reader]');t.click('[data-copy]');await Promise.resolve();
  assert.doesNotMatch(t.copied,/PRIVATE/);assert.match(t.copied,/https:\/\/anausomelife.com\/example.html/);assert.match(t.copied,/Text outside a paragraph/);
  t.win.navigator.clipboard.writeText=async()=>{throw Error('not allowed');};t.click('[data-copy]');await Promise.resolve();await Promise.resolve();
  assert.ok(!t.q('[data-copy-fallback]').hidden);assert.ok(t.q('#aal-reader-copy')._selected);assert.doesNotMatch(t.q('#aal-reader-copy').value,/PRIVATE/);
  t.click('[data-print-reader]');assert.equal(t.prints,1);assert.ok(t.doc.body.classList.contains('aal-print-reader'));t.click('[data-close-reader]');assert.ok(!t.doc.body.classList.contains('aal-print-reader'));
});

test('device and chosen reduced motion pause autoplay without starting media',()=>{
  let t=setup({reduced:true});assert.ok(t.mediaPauses>0);assert.equal(t.q('video').controls,true);
  t=setup();assert.equal(t.mediaPauses,0);t.set('motion',true);assert.ok(t.mediaPauses>0);t.set('guide',true);assert.ok(!t.q('.aal-reading-guide').hidden);t.set('guidePosition','70');assert.equal(t.q('.aal-reading-guide').style.top,'70vh');
});

test('a browser without native dialogs gets the accessible help page',()=>{
  const t=setup({nativeDialog:false});t.click('.aal-access-bar button');assert.equal(t.win.location.pathname,'/accessibility.html');assert.equal(t.win.location.hash,'#reading-tools');
});

test('tool styles parse and text, focus and control edges have useful contrast',()=>{
  const fs=require('node:fs');const CSSOM=require('cssom');const css=fs.readFileSync(require('node:path').join(__dirname,'../assets/access-tools.css'),'utf8');
  assert.ok(CSSOM.parse(css).cssRules.length>40);
  function light(hex){const h=hex.slice(1);const full=h.length===3?[...h].map(c=>c+c).join(''):h;const c=full.match(/../g).map(x=>parseInt(x,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722;}
  const contrast=(a,b)=>{const x=light(a),y=light(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
  for(const rule of CSSOM.parse(css).cssRules){if(!rule.style?.getPropertyValue('--aal-paper'))continue;const value=k=>rule.style.getPropertyValue('--aal-'+k);
    assert.ok(contrast(value('ink'),value('paper'))>=4.5);assert.ok(contrast(value('link'),value('paper'))>=4.5);assert.ok(contrast(value('line'),value('paper'))>=3);assert.ok(contrast(value('focus'),value('paper'))>=3);
  }
});
