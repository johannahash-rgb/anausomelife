/* Small DOM fixture; full Chromium interaction checks are documented separately. */
'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../assets/inquiry-builder.js'),'utf8');
class Element {
  constructor(value=''){this.value=value;this.hidden=true;this.textContent='';this.listeners={};this.href='';this.validity='';}
  addEventListener(type,callback){(this.listeners[type]??=[]).push(callback);}
  async emit(type){for(const callback of this.listeners[type]||[])await callback({preventDefault(){}});}
  focus(){this.focused=true;}
  select(){this.selected=true;}
  setCustomValidity(value){this.validity=value;}
}
function fixture(){
  const ids=['editorial-inquiry','inquiry-purpose','inquiry-output','inquiry-message','inquiry-email','inquiry-status','inquiry-output-notice','inquiry-details-help','inquiry-organization','inquiry-reference','inquiry-timing','inquiry-details','inquiry-prepare','inquiry-copy'];
  const elements=Object.fromEntries(ids.map(id=>[id,new Element()]));
  elements['inquiry-purpose'].value='product';
  elements['editorial-inquiry'].reportValidity=()=>!elements['inquiry-organization'].validity;
  const navigator={};
  vm.runInNewContext(source,{document:{getElementById:id=>elements[id]||null},navigator,encodeURIComponent,Error});
  return {elements,navigator};
}
(async()=>{
  vm.runInNewContext(source,{document:{getElementById:()=>null}});
  const {elements:e,navigator}=fixture();
  assert.equal(e['inquiry-prepare'].hidden,false);
  assert.equal(e['inquiry-output'].hidden,true);
  e['inquiry-organization'].value='  ';
  await e['inquiry-prepare'].emit('click');
  assert.match(e['inquiry-organization'].validity,/Please add/);
  e['inquiry-organization'].value='A & B Studio';
  await e['inquiry-organization'].emit('input');
  e['inquiry-details'].value='<img src=x> literal & text';
  for(const [purpose,subject] of Object.entries({product:'Product review proposal',travel:'Travel story proposal',press:'Press inquiry',licensing:'Photography or content request'})){
    e['inquiry-purpose'].value=purpose;
    await e['inquiry-purpose'].emit('change');
    assert.equal(e['inquiry-output'].hidden,true);
    await e['inquiry-prepare'].emit('click');
    const uri=new URL(e['inquiry-email'].href);
    assert.equal(uri.protocol,'mailto:');
    assert.equal(uri.pathname,'hello@anausomelife.com');
    assert.equal(uri.searchParams.get('subject'),subject+': A & B Studio');
    assert.match(uri.searchParams.get('body'),/<img src=x> literal & text/);
    assert.equal(e['inquiry-output'].hidden,false);
  }
  await e['inquiry-copy'].emit('click');
  assert.equal(e['inquiry-message'].selected,true);
  let copied='';navigator.clipboard={writeText:async text=>{copied=text;}};
  await e['inquiry-copy'].emit('click');
  assert.equal(copied,e['inquiry-message'].value);
  assert.match(e['inquiry-status'].textContent,/Copied/);
  await e['editorial-inquiry'].emit('input');
  assert.equal(e['inquiry-output'].hidden,true);
  e['inquiry-details'].value='An editorial idea. '.repeat(200);
  await e['inquiry-prepare'].emit('click');
  assert.match(e['inquiry-output-notice'].textContent,/shorten long drafts/);
  e['editorial-inquiry'].reportValidity=()=>false;
  e['inquiry-output'].hidden=true;
  await e['inquiry-prepare'].emit('click');
  assert.equal(e['inquiry-output'].hidden,true);
  assert.doesNotMatch(source,/\b(?:fetch|XMLHttpRequest|sendBeacon)\s*\(/);
  assert.doesNotMatch(source,/\b(?:localStorage|sessionStorage)\b/);
  console.log('Inquiry builder tests passed: purposes, validation, encoding, clipboard, stale drafts, long drafts, no submission.');
})().catch(error=>{console.error(error);process.exitCode=1;});
