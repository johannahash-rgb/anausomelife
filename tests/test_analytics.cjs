'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../assets/analytics.js'),'utf8');
class Element {
 constructor(){this.hidden=true;this.textContent='';this.listeners={};}
 addEventListener(type,fn){(this.listeners[type]??=[]).push(fn);}
 emit(type){for(const fn of this.listeners[type]||[])fn({target:this});}
}
async function fixture(options={}){
 const ids=Object.fromEntries(['measurement-state','measurement-controls','measurement-allow','measurement-deny','measurement-choice-status'].map(id=>[id,new Element()]));
 const scripts=[],store=new Map(),listeners={};let requests=0;
 if(options.stored!==undefined)store.set('aal-measurement-choice-v1',options.stored);
 const window={__AAL_PENDING_EVENTS__:[{name:'secret',params:{email:'private@example.com'}}]};
 const location={href:'https://anausomelife.com/privacy.html?email=private@example.com#private'};
 const document={getElementById:id=>ids[id]||null,
  querySelector:s=>s.startsWith('link')?{href:options.canonical||'https://anausomelife.com/privacy.html?private=secret'}:null,
  createElement:()=>({}),head:{append:s=>scripts.push(s)},addEventListener:(name,fn)=>listeners[name]=fn};
 const localStorage={getItem:k=>{if(options.storageBlocked)throw Error();return store.get(k)||null;},removeItem:k=>store.delete(k),setItem:(k,v)=>{if(options.storageBlocked)throw Error();store.set(k,v);}};
 const navigator=options.navigator||{};
 const config=options.config||{ga4MeasurementId:'G-TEST12345',analyticsEnabled:true,analyticsPrivacyReviewed:true};
 const fetch=()=>{requests++;return Promise.resolve({ok:true,json:()=>Promise.resolve(config)});};
 vm.runInNewContext(source,{window,document,localStorage,navigator,location,fetch,URL,Date,Set,Number,JSON,Array,encodeURIComponent});
 await new Promise(resolve=>setImmediate(resolve));
 return {ids,scripts,store,window,listeners,requests};
}
(async()=>{
 let x=await fixture({config:{ga4MeasurementId:''}});
 assert.equal(x.scripts.length,0);assert.equal(x.ids['measurement-controls'].hidden,true);assert.equal(x.window.AALAnalytics.active,false);
 x=await fixture({config:{ga4MeasurementId:'G-TEST12345'}});assert.equal(x.scripts.length,0);
 for(const navigator of [{doNotTrack:'1'},{globalPrivacyControl:true}]){
  x=await fixture({navigator,stored:JSON.stringify({allowed:true,at:Date.now()})});assert.equal(x.requests,0);assert.equal(x.scripts.length,0);
 }
 x=await fixture({canonical:'https://anausomelife.com/communication-card-generator.html'});assert.equal(x.requests,0);
 for(const stored of ['not json',JSON.stringify({allowed:'yes',at:Date.now()}),JSON.stringify({allowed:true,at:Date.now()-181*86400000}),JSON.stringify({allowed:true,at:Date.now()+86400000})]){
  x=await fixture({stored});assert.equal(x.scripts.length,0);
 }
 x=await fixture();
 assert.equal(x.scripts.length,0);assert.equal(x.window.__AAL_PENDING_EVENTS__.length,0);assert.equal(x.ids['measurement-controls'].hidden,false);
 assert.equal(x.window.AALAnalytics.track('site_action',{action_name:'rss_open',link_url:'mailto:private@example.com?body=secret'}),false);
 x.ids['measurement-allow'].emit('click');assert.equal(x.scripts.length,1);assert.equal(x.scripts[0].referrerPolicy,'no-referrer');
 assert.equal(x.window.dataLayer[0][0],'consent');assert.equal(x.window.dataLayer[0][2].analytics_storage,'denied');
 x.scripts[0].onload();assert.equal(x.window.AALAnalytics.active,true);
 assert.equal(x.window.AALAnalytics.track('site_action',{action_name:'rss_open',link_url:'secret',email:'private@example.com'}),true);
 assert.equal(x.window.AALAnalytics.track('site_action',{action_name:'rss_open'}),false);
 assert.equal(x.window.AALAnalytics.track('site_action',{action_name:'secret'}),false);
 assert.equal(x.window.AALAnalytics.track('inquiry_sent',{action_name:'rss_open'}),false);
 const serial=JSON.stringify(x.window.dataLayer);
 assert.doesNotMatch(serial,/secret|private@example|\?private|link_url/);
 assert.match(serial,/https:\/\/anausomelife.com\/privacy.html/);
 const n=x.window.dataLayer.length;x.ids['measurement-deny'].emit('click');assert.equal(x.window.AALAnalytics.active,false);
 assert.equal(x.window['ga-disable-G-TEST12345'],true);
 assert.equal(x.window.AALAnalytics.track('site_action',{action_name:'rss_copy'}),false);assert.equal(x.window.dataLayer.length,n);
 x=await fixture({storageBlocked:true});assert.equal(x.scripts.length,0);x.ids['measurement-allow'].emit('click');assert.equal(x.scripts.length,1);
 x=await fixture({stored:JSON.stringify({allowed:true,at:Date.now()})});assert.equal(x.scripts.length,1);x.scripts[0].onerror();assert.equal(x.window.AALAnalytics.active,false);
 assert.doesNotMatch(source,/queued\.push|analytics_storage:\s*'granted'[\s\S]*ad_storage:\s*'granted'/);
 console.log('Analytics tests passed: off by default; explicit gates and consent; privacy signals; no private values or backlog; withdrawal; storage and load failures.');
})().catch(e=>{console.error(e);process.exitCode=1;});
