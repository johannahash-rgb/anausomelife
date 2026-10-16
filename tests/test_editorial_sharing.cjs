const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
class Element{
 constructor(){this.value='';this.textContent='';this.hidden=false;this.listeners={};this.nodes={};this.children=[];this.valid=true;}
 addEventListener(name,fn){this.listeners[name]=fn;}
 querySelector(selector){return this.nodes[selector]||null;}
 setAttribute(name,value){this[name]=value;}
 append(node){this.children.push(node);}
 focus(){this.focused=true;} select(){this.selected=true;}
 reportValidity(){return this.valid;}
}
function brandHarness(query='',clipboard){
 const names=['brand-request','brand-story','brand-name','brand-use','brand-details','brand-credit-text','brand-request-output','brand-request-text','brand-email-link','brand-copy-request','brand-copy-status','brand-prepare'];
 const ids=Object.fromEntries(names.map(n=>[n,new Element()]));
 const selectors={'[data-copy-credit]':new Element(),'[data-credit-status]':new Element()};
 ids['brand-request-output'].hidden=true;ids['brand-credit-text'].textContent='An AUsome Life · @anausomelife · anausomelife.com';
 class Data{get(k){return {brand:ids['brand-name'].value,usage:ids['brand-use'].value,details:ids['brand-details'].value}[k];}}
 const ctx={document:{getElementById:n=>ids[n],querySelector:s=>selectors[s]},navigator:{clipboard},location:{search:query},URL,URLSearchParams,FormData:Data};
 vm.runInNewContext(fs.readFileSync(root+'/assets/brand-room.js','utf8'),ctx);return {ids,selectors};
}
function storyHarness({article=true,hasNext=false,clipboard,share,canonical='https://anausomelife.com/october-ice-cream-dairy-joy-weston.html?tracking=yes#photo'}={}){
 const main=new Element(),heading=new Element();heading.textContent='October ice cream at Dairy Joy.';
 main.nodes.h1=heading;if(article)main.nodes['.fn-story,.er-story,.love-body,.journal-prose,.article-body']=new Element();
 if(hasNext){const next={before(node){main.children.splice(main.children.indexOf(next),0,node);}};main.nodes['.reader-next']=next;main.children.push(next);}
 const section=new Element();['.aal-share-status','[data-share-fallback]','textarea','[data-reuse-link]','[data-copy-link]','[data-copy-caption]','[data-share-native]'].forEach(k=>section.nodes[k]=new Element());section.nodes['[data-share-fallback]'].hidden=true;section.nodes['[data-share-native]'].hidden=true;
 const ctx={document:{readyState:'complete',querySelector:s=>s==='main'?main:s==='link[rel="canonical"]'?{href:canonical}:null,createElement:()=>section},location:{origin:'https://anausomelife.com'},navigator:{clipboard,share},URL};
 vm.runInNewContext(fs.readFileSync(root+'/assets/story-share.js','utf8'),ctx);return {main,section};
}
(async()=>{
 let copied='';const clipboard={writeText:async text=>{copied=text;}};
 const good=brandHarness('?story='+encodeURIComponent('https://anausomelife.com/a-story.html?utm=x#part'),clipboard);
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
 let shared;const native=storyHarness({share:async data=>{shared=data;}});await native.section.nodes['[data-share-native]'].listeners.click();assert.equal(shared.title,'October ice cream at Dairy Joy.');
 const cancel=storyHarness({share:async()=>{const e=new Error();e.name='AbortError';throw e;}});await cancel.section.nodes['[data-share-native]'].listeners.click();assert.equal(cancel.section.nodes['.aal-share-status'].textContent,'');
 assert.equal(storyHarness({article:false,canonical:'https://anausomelife.com/library.html'}).main.children.length,0);
 assert.equal(storyHarness({canonical:'https://elsewhere.example/'}).main.children.length,0);
 console.log('PASS: share links, caption credits, native sharing and cancellation, clipboard fallback, reuse deep links, query validation, email encoding, invalid form, and no automatic submission.');
})().catch(e=>{console.error(e);process.exitCode=1;});
