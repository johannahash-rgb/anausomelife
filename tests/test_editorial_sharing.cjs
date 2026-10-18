const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
class Element{
 constructor(){this.value='';this.textContent='';this.hidden=false;this.listeners={};this.nodes={};this.children=[];this.valid=true;this.scrollCalls=[];this.clientWidth=400;this.dataset={};this.lists={};}
 addEventListener(name,fn){this.listeners[name]=fn;}
 querySelector(selector){return this.nodes[selector]||null;}
 querySelectorAll(selector){return this.lists[selector]||[];}
 setAttribute(name,value){this[name]=value;}
 append(node){this.children.push(node);}
 focus(){this.focused=true;} select(){this.selected=true;}
 reportValidity(){return this.valid;}
 scrollBy(options){this.scrollCalls.push(options);}
}
function brandHarness(query='',clipboard){
 const names=['brand-request','brand-story','brand-name','brand-use','brand-details','brand-credit-text','brand-request-output','brand-request-text','brand-email-link','brand-copy-request','brand-copy-status','brand-prepare'];
 const ids=Object.fromEntries(names.map(n=>[n,new Element()]));
 const selectors={'[data-copy-credit]':new Element(),'[data-credit-status]':new Element()};
 const reel=new Element(),viewport=new Element(),prev=new Element(),next=new Element();viewport.clientWidth=400;reel.nodes['.brand-marquee']=viewport;reel.nodes['[data-brand-scroll="prev"]']=prev;reel.nodes['[data-brand-scroll="next"]']=next;
 ids['brand-request-output'].hidden=true;ids['brand-credit-text'].textContent='An AUsome Life · @anausomelife · anausomelife.com';
 class Data{get(k){return {brand:ids['brand-name'].value,usage:ids['brand-use'].value,details:ids['brand-details'].value}[k];}}
 const ctx={document:{getElementById:n=>ids[n],querySelector:s=>selectors[s],querySelectorAll:s=>s==='[data-brand-marquee]'?[reel]:[]},navigator:{clipboard},location:{search:query},URL,URLSearchParams,FormData:Data};
 vm.runInNewContext(fs.readFileSync(root+'/assets/brand-room.js','utf8'),ctx);return {ids,selectors,reel,viewport,prev,next};
}
function storyHarness({article=true,hasNext=false,clipboard,share,authored=false,canonical='https://anausomelife.com/october-ice-cream-dairy-joy-weston.html?tracking=yes#photo'}={}){
 const main=new Element(),heading=new Element();heading.textContent='October ice cream at Dairy Joy.';
 main.nodes.h1=heading;if(article)main.nodes['.fn-story,.er-story,.love-body,.journal-prose,.article-body']=new Element();
 if(hasNext){const next={before(node){main.children.splice(main.children.indexOf(next),0,node);}};main.nodes['.reader-next']=next;main.children.push(next);}
 const section=new Element();['.aal-share-status','[data-share-fallback]','textarea','[data-reuse-link]','[data-copy-link]','[data-copy-caption]','[data-share-native]'].forEach(k=>section.nodes[k]=new Element());section.nodes['[data-share-fallback]'].hidden=true;section.nodes['[data-share-native]'].hidden=true;
 if(authored){
  main.nodes['.aal-story-share']=section;main.children.push(section);
  section.dataset.shareSummary='A free picture choice board for your next visit.';
  const caption=new Element();caption.textContent='Planning a Congdon’s stop? An AUsome Life made a free board.\n\nhttps://anausomelife.com/congdons-doughnuts-wells-maine.html\n@anausomelife';section.nodes['[data-share-caption]']=caption;
  const short=new Element();short.textContent='A free board to take along.\nFrom @anausomelife';section.nodes['#short-caption']=short;
  const button=new Element();button.hidden=true;button.dataset={copyShareText:'short-caption',copyStatus:'Short caption copied.'};
  const missing=new Element();missing.hidden=true;missing.dataset.copyShareText='missing-caption';
  section.lists['[data-copy-share-text]']=[button,missing];
 }
 const ctx={document:{readyState:'complete',querySelector:s=>s==='main'?main:s==='link[rel="canonical"]'?{href:canonical}:null,createElement:()=>section},location:{origin:'https://anausomelife.com'},navigator:{clipboard,share},URL};
 const run=()=>vm.runInNewContext(fs.readFileSync(root+'/assets/story-share.js','utf8'),ctx);run();return {main,section,run};
}
(async()=>{
 let copied='';const clipboard={writeText:async text=>{copied=text;}};
 const good=brandHarness('?story='+encodeURIComponent('https://anausomelife.com/a-story.html?utm=x#part'),clipboard);
 good.prev.listeners.click();assert.equal(good.viewport.scrollCalls[0].left,-312);assert.equal(good.viewport.scrollCalls[0].behavior,'smooth');
 good.next.listeners.click();assert.equal(good.viewport.scrollCalls[1].left,312);assert.equal(good.viewport.scrollCalls[1].behavior,'smooth');
 assert.equal(good.ids['brand-story'].value,'https://anausomelife.com/a-story.html');
 for(const url of ['https://evil.example/story','javascript:alert(1)','https://anausomelife.com.evil.example/story'])assert.equal(brandHarness('?story='+encodeURIComponent(url)).ids['brand-story'].value,'');
 const b=good.ids;b['brand-name'].value='Example & Company';b['brand-use'].value='Brand website or newsletter';b['brand-details'].value='The waterfront photo — November.';
 b['brand-prepare'].listeners.click();assert.equal(b['brand-request-output'].hidden,false);assert(b['brand-request-text'].focused);
 const mail=new URL(b['brand-email-link'].href);assert.equal(mail.pathname,'hello@anausomelife.com');assert.equal(mail.searchParams.get('subject'),'Content request: Example & Company');assert(mail.searchParams.get('body').includes('The waterfront photo — November.'));assert(mail.searchParams.get('body').includes('permission terms'));
 await b['brand-copy-request'].listeners.click();assert.equal(copied,b['brand-request-text'].value);
 const invalid=brandHarness();invalid.ids['brand-request'].valid=false;invalid.ids['brand-prepare'].listeners.click();assert(invalid.ids['brand-request-output'].hidden);
 let prevented=false;b['brand-request'].listeners.submit({preventDefault(){prevented=true;}});assert(prevented,'No form data is sent to the server');
 const fallback=brandHarness();fallback.ids['brand-request-text'].value='Request';await fallback.ids['brand-copy-request'].listeners.click();assert(fallback.ids['brand-request-text'].selected);
 const s=storyHarness({clipboard});assert.equal(s.main.children.length,1);await s.section.nodes['[data-copy-link]'].listeners.click();assert.equal(copied,'https://anausomelife.com/october-ice-cream-dairy-joy-weston.html');
 const ordered=storyHarness({hasNext:true});assert.equal(ordered.main.children.length,2);assert.equal(ordered.main.children[0],ordered.section,'Sharing appears before onward reading');
 await s.section.nodes['[data-copy-caption]'].listeners.click();assert(copied.includes('An AUsome Life · @anausomelife'));assert(!copied.includes('tracking'));
 const reuse=new URL(s.section.nodes['[data-reuse-link]'].href,'https://anausomelife.com');assert.equal(reuse.hash,'#sharing');assert.equal(reuse.searchParams.get('story'),'https://anausomelife.com/october-ice-cream-dairy-joy-weston.html');
 const f=storyHarness();await f.section.nodes['[data-copy-link]'].listeners.click();assert.equal(f.section.nodes['[data-share-fallback]'].hidden,false);assert(f.section.nodes.textarea.selected);
 const reviewed=storyHarness({authored:true,clipboard});assert.equal(reviewed.main.children.length,1,'An authored package is enhanced, not duplicated');
 await reviewed.section.nodes['[data-copy-caption]'].listeners.click();assert.equal(copied,reviewed.section.nodes['[data-share-caption]'].textContent,'Copy uses the reviewed story-specific caption');
 const short=reviewed.section.lists['[data-copy-share-text]'][0];assert.equal(short.hidden,false);await short.listeners.click();assert.equal(copied,reviewed.section.nodes['#short-caption'].textContent);assert.equal(reviewed.section.nodes['.aal-share-status'].textContent,'Short caption copied.');
 const missing=reviewed.section.lists['[data-copy-share-text]'][1];assert(missing.hidden);assert(!missing.listeners.click,'An absent text target leaves its control hidden');
 const existing=reviewed.section.nodes['[data-copy-caption]'].listeners.click;reviewed.run();assert.equal(reviewed.section.nodes['[data-copy-caption]'].listeners.click,existing,'Repeated script initialization preserves one handler');assert.equal(reviewed.main.children.length,1);
 const reviewedFallback=storyHarness({authored:true});await reviewedFallback.section.lists['[data-copy-share-text]'][0].listeners.click();assert.equal(reviewedFallback.section.nodes.textarea.value,reviewedFallback.section.nodes['#short-caption'].textContent);assert(reviewedFallback.section.nodes.textarea.selected);
 let shared;const native=storyHarness({share:async data=>{shared=data;}});await native.section.nodes['[data-share-native]'].listeners.click();assert.equal(shared.title,'October ice cream at Dairy Joy.');
 const reviewedNative=storyHarness({authored:true,share:async data=>{shared=data;}});await reviewedNative.section.nodes['[data-share-native]'].listeners.click();assert.equal(shared.text,'A free picture choice board for your next visit.');
 const cancel=storyHarness({share:async()=>{const e=new Error();e.name='AbortError';throw e;}});await cancel.section.nodes['[data-share-native]'].listeners.click();assert.equal(cancel.section.nodes['.aal-share-status'].textContent,'');
 assert.equal(storyHarness({article:false,canonical:'https://anausomelife.com/library.html'}).main.children.length,0);
 assert.equal(storyHarness({canonical:'https://elsewhere.example/'}).main.children.length,0);
 assert.equal(storyHarness({canonical:'javascript:alert(1)'}).main.children.length,0);
 console.log('PASS: reviewed captions, short-copy controls, authored package reuse, native sharing and cancellation, clipboard fallback, canonical links, reuse deep links, query validation, email encoding, invalid form, and no automatic submission.');
})().catch(e=>{console.error(e);process.exitCode=1;});
