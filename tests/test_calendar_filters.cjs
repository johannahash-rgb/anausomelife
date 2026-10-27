const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('node:crypto');
// Exercise the reviewed October 2026 fixtures at a fixed pre-expiry instant.
// Keep every state/filter coverage assertion intact as real event dates pass.
const NativeDate=globalThis.Date,fixtureNow=NativeDate.parse('2026-10-26T12:00:00Z');
class Date extends NativeDate {constructor(...args){super(...(args.length?args:[fixtureNow]))}static now(){return fixtureNow}}
class Node { constructor(tag='div'){this.tagName=tag;this.children=[];this.listeners={};this.dataset={};this.classList={add(){},toggle(){}};this.elements={};this.attributes={};this.hidden=false;this.value='';this.style={};}append(...n){this.children.push(...n)}prepend(...n){this.children.unshift(...n)}replaceChildren(...n){this.children=n}setAttribute(k,v){this.attributes[k]=v}addEventListener(k,f){this.listeners[k]=f}querySelector(){return null}querySelectorAll(){return []}scrollIntoView(){}focus(){} }
const form=new Node('form');for(let n of ['q','state','from','month','category','age','access','format','cost','dateRange','sensory','holiday'])form.elements[n]=new Node('select');const keys=['.event-list','.event-month-view','.event-summary','.event-empty','.event-error','[data-event-watchlist]','[data-organizer-directory]','[data-refresh-note]'];const map=Object.fromEntries(keys.map(x=>[x,new Node()]));map['form']=form;
const root=new Node();root.querySelector=s=>map[s]||null;const stateBox=new Node();const doc={querySelector:s=>s==='[data-events]'?root:s==='[data-state-index]'?stateBox:null,createElement:s=>new Node(s),createElementNS:(ns,s)=>{const n=new Node(s);n.namespaceURI=ns;return n},getElementById:()=>null};
const base=require('path').resolve(__dirname,'..');const data=JSON.parse(fs.readFileSync(base+'/data/events.json'));const art=JSON.parse(fs.readFileSync(base+'/data/event-illustrations.json'));const metadata=JSON.parse(fs.readFileSync(base+'/data/event-filters.json'));for(const [name,values]of Object.entries({age:['','all-ages','children','teens','adults','families','unspecified'],sensory:['','low','moderate','high','variable','unknown'],holiday:['','seasonal','halloween','christmas','santa','winter-holidays','winter-lights','holiday-performance','holiday-social','holiday-market'],access:['','sensory-friendly','wheelchair-step-free','adaptive-activities','caregiver-support','vision-support','hearing-support','unspecified']})){for(const value of values){const option=new Node('option');option.value=value;form.elements[name].append(option)}}
const context={document:doc,window:{listeners:{},addEventListener(k,f){this.listeners[k]=f},history:{replaceState(a,b,url){context.location.href=url}},matchMedia:()=>({matches:false})},location:{origin:'https://anausomelife.com',href:'https://anausomelife.com/calendar.html'},Intl,Date,URL,URLSearchParams,console,setTimeout:f=>f(),setInterval(){},requestAnimationFrame:f=>f(),fetch:async u=>({ok:true,json:async()=>u.includes('illustrations')?art:u.includes('event-filters')?metadata:data})};
vm.runInNewContext(fs.readFileSync(base+'/assets/events.js','utf8'),context);
function count(n,tag){return (n?.tagName===tag?1:0)+(n.children||[]).reduce((x,y)=>x+(typeof y==='object'?count(y,tag):0),0)}

function assertReviewedArtworkCoverage(){
  // Every dated record remains covered, even after it expires from the live UI.
  for(const event of data.events){
    const row=art.events[event.id];
    assert(row,'Missing watercolor mapping: '+event.id);
    assert.match(row.src,/^\/assets\/event-sketches\/[a-z0-9-]+\.webp$/);
    assert(fs.statSync(base+row.src).isFile(),'Missing watercolor file: '+event.id);
  }

  // This immutable release record protects the 61 new sessions independently
  // of active dates, without imposing the new studyId schema on legacy art.
  const release=JSON.parse(fs.readFileSync(base+'/docs/calendar-watercolors-2026-10-19.json','utf8'));
  const added=new Set(release.addedEventIds);
  assert.equal(release.addedEventIds.length,61,'Release must account for all 61 additions');
  assert.equal(added.size,61,'Addition IDs must be unique');
  assert.equal(release.studies.length,23,'Each reviewed program group needs its own fresh study');
  assert.equal(new Set(release.studies.map(study=>study.id)).size,23,'Study IDs must be unique');
  assert.equal(new Set(release.studies.map(study=>study.src)).size,23,'Study files must be distinct');
  assert.equal(new Set(release.studies.map(study=>study.sha256)).size,23,'Study image contents must be distinct');
  const eventById=new Map(data.events.map(event=>[event.id,event]));
  const studyById=new Map(release.studies.map(study=>[study.id,study]));
  function isLaterProgramSession(id,row){
    if(added.has(id)||!studyById.has(row.studyId))return false;
    const originalId=row.reusedFromEvent,original=eventById.get(originalId),event=eventById.get(id);
    assert(added.has(originalId),'Later session must name an original reviewed session: '+id);
    assert(original&&event,'Later session must name existing events: '+id);
    assert.equal(event.sourceId,original.sourceId,'Artwork reuse must stay with the same organizer: '+id);
    assert.equal(event.venue,original.venue,'Artwork reuse must stay at the same venue: '+id);
    assert(Date.parse(event.start)>Date.parse(original.start),'Reuse must belong to a later session: '+id);
    assert.equal(row.studyId,art.events[originalId].studyId,'Later session must keep the original study: '+id);
    const study=studyById.get(row.studyId);
    for(const key of ['src','alt','width','height'])assert.equal(row[key],study[key],id+': '+key);
    return true;
  }
  // Later sessions can explicitly reuse their reviewed program's study. They
  // are not legacy artwork against which the October 19 release was checked.
  const legacySources=new Set([
    ...Object.entries(art.events).filter(([id,row])=>!added.has(id)&&!isLaterProgramSession(id,row)).map(([,row])=>row.src),
    ...Object.values(art.watchlist).map(row=>row.src)
  ]);
  const assigned=[];
  for(const study of release.studies){
    assert.equal(study.reviewed,true,'Unreviewed study: '+study.id);
    assert.match(study.src,/^\/assets\/event-sketches\/[a-z0-9-]+\.webp$/);
    assert(!legacySources.has(study.src),'New sessions must receive fresh artwork: '+study.id);
    assert.equal(study.width,720);
    assert.equal(study.height,480);
    assert(study.alt.trim().length>25,'Study needs a useful image description: '+study.id);
    assert(study.eventIds.length>0,'Study must belong to a named program: '+study.id);
    assert.match(study.sha256,/^[a-f0-9]{64}$/);
    const bytes=fs.readFileSync(base+study.src);
    assert.equal(bytes.toString('ascii',0,4),'RIFF','Expected WebP container: '+study.src);
    assert.equal(bytes.toString('ascii',8,12),'WEBP','Expected WebP image: '+study.src);
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),study.sha256,'Reviewed image bytes changed: '+study.id);
    for(const [index,id] of study.eventIds.entries()){
      assert(added.has(id),'Study includes an event outside this release: '+id);
      const event=eventById.get(id),row=art.events[id];
      assert(event,'Unknown event in study: '+id);
      assert(row,'Missing new session artwork: '+id);
      for(const key of ['src','alt','width','height'])assert.equal(row[key],study[key],id+': '+key);
      assert.equal(row.studyId,study.id,'Session points to the wrong program study: '+id);
      for(const key of ['title','venue','start'])assert.equal(row[key],event[key],id+': '+key);
      if(index===0){
        assert(!row.reusedFromEvent,'The first session must own its fresh study: '+id);
      }else{
        assert.equal(row.reusedFromEvent,study.eventIds[0],'Reuse must name the first session in the same reviewed program: '+id);
        assert.equal(art.events[row.reusedFromEvent].studyId,study.id);
        assert.equal(art.events[row.reusedFromEvent].src,row.src);
      }
      assigned.push(id);
    }
  }
  assert.deepEqual(assigned.sort(),[...added].sort(),'Every new session must appear in exactly one reviewed study');
}
setImmediate(()=>{try{const live=data.events.filter(e=>new Date(e.end)>new Date()&&!e.reviewRequired&&!['cancelled','review'].includes(e.status));assert.equal(map['.event-list'].children.length,live.length);assert.equal(map['.event-list'].children.filter(x=>x.children.some(y=>y.tagName==='figure')).length,live.length,'Every listing must show its watercolor outside closed details');assert(map['.event-list'].children.every(x=>count(x,'figure')===1),'Exactly one watercolor per listing');assertReviewedArtworkCoverage();assert.equal(stateBox.children.length,7);assert.deepEqual(form.elements.month.children.map(option=>option.value),[...new Set(live.map(event=>event.start.slice(0,7)))].sort(),'Month choices must cover every active data month exactly once');for(const age of ['all-ages','children','teens','adults','families','unspecified']){form.elements.age.value=age;form.listeners.change();assert.equal(map['.event-list'].children.length,live.filter(e=>age==='unspecified'?!metadata.events[e.id].ageGroups.length:metadata.events[e.id].ageGroups.includes(age)).length,age)}form.elements.age.value='';
for(const access of ['sensory-friendly','wheelchair-step-free','adaptive-activities','caregiver-support','vision-support','hearing-support','unspecified']){form.elements.access.value=access;form.listeners.change();assert.equal(map['.event-list'].children.length,live.filter(e=>access==='unspecified'?!metadata.events[e.id].accessFeatures.length:metadata.events[e.id].accessFeatures.includes(access)).length,access)}form.elements.access.value='';
form.elements.age.value='teens';form.elements.access.value='vision-support';form.elements.state.value='MA';form.elements.month.value='2026-11';form.listeners.change();assert.deepEqual(map['.event-list'].children.map(c=>c.id),['event-carroll-cane-quest-2026-11-11']);
form.elements.age.value='';form.elements.access.value='';form.elements.state.value='';form.elements.month.value='';form.elements.format.value='Virtual';form.listeners.change();assert.equal(map['.event-list'].children.length,live.filter(e=>e.format==='Virtual').length);form.elements.format.value='';
form.elements.cost.value='free';form.listeners.change();assert.deepEqual(map['.event-list'].children.map(c=>c.id).sort(),live.filter(e=>e.costCategory==='free').map(e=>'event-'+e.id).sort());assert(!map['.event-list'].children.some(c=>c.id.startsWith('event-bcm-')||c.id.startsWith('event-cmnh-')),'Member-only discounts must not count as free admission');for(const state of ['CT','MA','ME','NH','RI','VT']){form.elements.state.value=state;form.listeners.change();assert(map['.event-list'].children.length>0,'Free dated listings in '+state)}form.elements.cost.value='';form.elements.state.value='';
form.elements.dateRange.value='weekend';form.listeners.change();assert(map['.event-list'].children.every(c=>{const e=live.find(e=>'event-'+e.id===c.id),day=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',weekday:'short'}).format(new Date(e.start));return day==='Sun'||day==='Sat'}),'Weekend results only');form.elements.dateRange.value='';
form.elements.month.value='2026-11';form.listeners.change();assert.equal(map['.event-list'].children.length,live.filter(e=>e.start.startsWith('2026-11')).length);form.elements.state.value='VT';form.listeners.change();assert.equal(map['.event-list'].children.length,live.filter(e=>e.start.startsWith('2026-11')&&e.state==='VT').length);form.elements.month.value='';form.elements.state.value='';form.elements.q.value='nutcracker';form.listeners.change();const nutcrackerIds=live.filter(event=>event.title.toLocaleLowerCase().includes('nutcracker')).map(event=>'event-'+event.id).sort();assert(nutcrackerIds.length>0,'The search fixture must include a Nutcracker performance');assert.deepEqual(map['.event-list'].children.map(card=>card.id).sort(),nutcrackerIds,'Search must return all listed Nutcracker performances');form.elements.q.value='zznonexistent';form.listeners.change();assert.equal(map['.event-list'].children.length,0);assert.equal(map['.event-empty'].hidden,false);form.elements.q.value='';form.elements.state.value='ME';form.elements.month.value='2026-11';form.elements.dateRange.value='';form.listeners.change();assert.equal(new URL(context.location.href).searchParams.get('state'),'ME');assert.equal(new URL(context.location.href).searchParams.get('month'),'2026-11');context.location.href='https://anausomelife.com/calendar.html?state=MA&age=teens&access=vision-support&month=2026-11&view=month';context.window.listeners.popstate();assert.equal(form.elements.state.value,'MA');assert.deepEqual(map['.event-list'].children.map(c=>c.id),['event-carroll-cane-quest-2026-11-11']);assert.equal(map['.event-month-view'].hidden,false);assert.equal(new URL(context.location.href).searchParams.get('view'),'month');
// Seasonal and sensory filters must compose with the existing filters and URL state.
for(const key of Object.keys(form.elements))form.elements[key].value='';
for(const level of ['low','moderate','high','variable','unknown']){form.elements.sensory.value=level;form.listeners.change();assert.equal(map['.event-list'].children.length,live.filter(e=>metadata.events[e.id].sensory.level===level).length,level)}
form.elements.sensory.value='low';form.elements.holiday.value='halloween';form.elements.state.value='MA';form.listeners.change();
const expectedHalloweenLow=live.filter(event=>event.state==='MA'&&metadata.events[event.id].sensory.level==='low'&&metadata.events[event.id].holidays.includes('halloween')).map(event=>'event-'+event.id).sort();assert.deepEqual(map['.event-list'].children.map(card=>card.id).sort(),expectedHalloweenLow,'Halloween, sensory and state filters must include every matching session');
assert(!map['.event-list'].children.some(c=>c.id.includes('longhill')),'Effects restart during Long Hill hour; it cannot be classified low throughout');
assert.equal(new URL(context.location.href).searchParams.get('sensory'),'low');assert.equal(new URL(context.location.href).searchParams.get('holiday'),'halloween');
context.location.href='https://anausomelife.com/calendar.html?holiday=santa&sensory=unknown&view=month';context.window.listeners.popstate();
assert.deepEqual(map['.event-list'].children.map(c=>c.id),['event-northshore-santa-2026-12-06']);assert.equal(map['.event-month-view'].hidden,false);
form.elements.sensory.value='low';form.elements.holiday.value='';form.elements.state.value='VT';form.elements.cost.value='free';form.elements.age.value='adults';form.listeners.change();
assert(map['.event-list'].children.some(c=>c.id==='event-echo-sensory-2026-11-08'),'Free adult-friendly ECHO dates must be discoverable');
form.elements.sensory.value='';form.elements.holiday.value='seasonal';form.elements.state.value='';form.elements.cost.value='';form.elements.age.value='';form.listeners.change();
assert.equal(map['.event-list'].children.length,live.filter(e=>metadata.events[e.id].holidays.length>0).length);
console.log('PASS: '+live.length+' active records; every age/access selection; combined age/access/state/month; virtual mode; all watercolors visible outside disclosures; empty state.');}catch(e){console.error(e);process.exitCode=1}});
