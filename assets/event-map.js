/* Source-grounded regional calendar map. Same-origin data; no tiles, trackers or geolocation. */
(() => {
'use strict';
const NS='http://www.w3.org/2000/svg', W=1000,H=720,COS=Math.cos(43*Math.PI/180);
const sourceScript=document.currentScript?.src||new URL('/assets/event-map.js',location.href).href;
const locationURL=new URL('../data/event-locations.json',sourceScript);locationURL.searchParams.set('v','20261004-expanded');const dataURL=locationURL.href;
const instances=new WeakMap();let request;
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n};
const svgEl=(tag,attrs={})=>{const n=document.createElementNS(NS,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));return n};
const button=(label,fn,cls='em-button')=>{const b=el('button',cls,label);b.type='button';b.addEventListener('click',fn);return b};
const link=(label,url,cls='')=>{try{const u=new URL(url);if(u.protocol!=='https:')throw Error('Unsafe link');const a=el('a',cls,label);a.href=u.href;a.rel='noopener noreferrer';return a}catch{return el('span',cls,label.replace(' ↗',''))}};
const normalize=v=>String(v||'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');
const project=c=>[c[0]*COS,-c[1]];
const date=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',month:'short',day:'numeric',weekday:'short'});
function fit(groups,padding=.22){
 const points=groups.filter(g=>g.location).map(g=>project(g.location.coordinates));
 if(!points.length)return [-54.5,-44.9,-49.5,-40.6];
 const xs=points.map(x=>x[0]),ys=points.map(x=>x[1]);let x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
 let width=Math.max(x1-x0,.12),height=Math.max(y1-y0,.10);width*=1+padding*2;height*=1+padding*2;
 const ratio=W/H;if(width/height<ratio)width=height*ratio;else height=width/ratio;
 const cx=(x0+x1)/2,cy=(y0+y1)/2;return[cx-width/2,cy-height/2,cx+width/2,cy+height/2];
}
function groupEvents(events,data){
 const groups=new Map();
 for(const event of events){if(!event||!event.id)continue;const key=normalize(event.venue)+'|'+normalize(event.address);
  if(!groups.has(key)){const location=event.format==='Virtual'?null:data?.venues.find(v=>normalize(v.venue)===normalize(event.venue)&&normalize(v.state)===normalize(event.state)&&normalize(v.address)===normalize(event.address));groups.set(key,{key,venue:event.venue||event.city||'Event location',city:event.city||'',state:event.state||'',address:event.address||'',virtual:event.format==='Virtual',location,events:[]});}
  groups.get(key).events.push(event);
 }
 return [...groups.values()].sort((a,b)=>a.state.localeCompare(b.state)||a.city.localeCompare(b.city)||a.venue.localeCompare(b.venue)).map((g,i)=>({...g,number:i+1}));
}
function directions(group){return 'https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(group.venue+', '+group.address)}
function listVenues(state,groups){
 state.list.replaceChildren();
 for(const g of groups){const article=el('article','em-venue');article.dataset.mapVenue=g.key;const heading=el('h3');
  heading.append(el('span','em-key',String(g.number)),document.createTextNode(g.venue));article.append(heading,el('p','em-town',g.virtual?'Online · no travel needed':g.city+', '+g.state),el('p','em-address',g.address));
  const dates=el('ul','em-dates');for(const e of g.events){const li=el('li');let when=e.start;try{when=date.format(new Date(e.start))}catch{}const b=button(when+' · '+e.title,()=>{if(typeof state.onSelect==='function')state.onSelect(e.id);else{const target=document.getElementById('event-'+e.id);target?.focus();target?.scrollIntoView({block:'start'});}},'em-event-link');li.append(b);dates.append(li)}article.append(dates);
  const actions=el('div','em-venue-actions');if(!g.virtual)actions.append(link('Directions ↗',directions(g),'em-directions'));
  const source=g.location?.addressSource||g.events[0]?.sourceUrl;if(source)actions.append(link('Organizer ↗',source,'em-directions'));article.append(actions);
  if(!g.location&&!g.virtual)article.append(el('p','em-location-note','Location not pinned yet. Use the address and organizer directions.'));
  state.list.append(article);
 }
 if(!groups.length)state.list.append(el('p','em-empty','No dated events match these filters. Try another month or region.'));
}
function draw(state){
 const {groups,data,canvas,pins,bounds}=state;const [x0,y0,x1,y1]=bounds;
 const xy=c=>{const [x,y]=project(c);return[(x-x0)/(x1-x0)*W,(y-y0)/(y1-y0)*H]};
 const svg=svgEl('svg',{viewBox:`0 0 ${W} ${H}`,'aria-hidden':'true',focusable:'false',class:'em-geography'});
 svg.append(svgEl('rect',{x:0,y:0,width:W,height:H,fill:'#f6f2e6'}));
 for(const feature of data.basemap.geojson.features){const polygons=feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates;let path='';for(const rings of polygons){for(const ring of rings){path+=ring.map((c,i)=>{const [x,y]=xy(c);return(i?'L':'M')+x.toFixed(1)+','+y.toFixed(1)}).join('')+'Z'}}svg.append(svgEl('path',{d:path,fill:feature.properties.STUSAB==='MA'?'#dae3d4':'#e5eadb',stroke:'#7c9081','stroke-width':1.3,'vector-effect':'non-scaling-stroke','fill-rule':'evenodd'}));}
 const labels=[['VERMONT',-72.78,44.05],['NEW HAMPSHIRE',-71.56,43.60],['MAINE',-69.88,44.14],['MASSACHUSETTS',-72.15,42.22],['CONNECTICUT',-72.89,41.70],['RHODE ISLAND',-71.50,41.53]];
 for(const[label,lon,lat]of labels){const[x,y]=xy([lon,lat]);if(x>20&&x<W-20&&y>20&&y<H-20){const t=svgEl('text',{x,y,'text-anchor':'middle',class:'em-state-label'});t.textContent=label;svg.append(t)}}
 const north=svgEl('g',{transform:'translate(953 38)'});const n=svgEl('text',{'text-anchor':'middle',class:'em-north-label'});n.textContent='N';north.append(n,svgEl('path',{d:'M0 12L-8 34L0 28L8 34Z M0 28V53',fill:'#173c4a',stroke:'#173c4a','stroke-width':2}));svg.append(north);
 canvas.querySelector('.em-geography')?.remove();canvas.prepend(svg);pins.replaceChildren();
 const width=Math.max(canvas.clientWidth,300),height=width*H/W;
 let clusters=[];
 for(const group of groups.filter(g=>g.location)){const[x,y]=xy(group.location.coordinates);if(x<0||x>W||y<0||y>H)continue;const point={group,x,y};let near=clusters.find(c=>Math.hypot((c.x-x)*width/W,(c.y-y)*height/H)<58);
  if(!near)clusters.push({items:[group],x,y});else{near.items.push(group);near.x=(near.x*(near.items.length-1)+x)/near.items.length;near.y=(near.y*(near.items.length-1)+y)/near.items.length;}
 }
 // Merge newly overlapping clusters, so touch targets do not stack over one another.
 for(let changed=true;changed;){changed=false;outer:for(let i=0;i<clusters.length;i++)for(let j=i+1;j<clusters.length;j++){const a=clusters[i],b=clusters[j];if(Math.hypot((a.x-b.x)*width/W,(a.y-b.y)*height/H)<64){const total=a.items.length+b.items.length;a.x=(a.x*a.items.length+b.x*b.items.length)/total;a.y=(a.y*a.items.length+b.y*b.items.length)/total;a.items.push(...b.items);clusters.splice(j,1);changed=true;break outer}}}
 for(const cluster of clusters){const several=cluster.items.length>1;const text=several?cluster.items.length+' places':String(cluster.items[0].number);const b=button(text,()=>{
   state.selected=cluster.items.map(g=>g.key);if(several)state.bounds=fit(cluster.items,.55);
   listVenues(state,cluster.items);draw(state);state.selection.textContent=several?`Showing ${cluster.items.length} nearby places. Choose an event below.`:`Showing ${cluster.items[0].venue}. Choose an event below.`;
   state.listHeading.focus({preventScroll:true});if(window.matchMedia('(max-width: 700px)').matches)state.listHeading.scrollIntoView({block:'nearest',behavior:'auto'});
  },'em-pin'+(several?' em-cluster':''));
  b.style.left=(cluster.x/W*100)+'%';b.style.top=(cluster.y/H*100)+'%';const names=cluster.items.map(g=>g.venue+' in '+g.city).join('; ');b.setAttribute('aria-label',several?`Show ${cluster.items.length} nearby venues: ${names}`:`Show ${cluster.items[0].number}: ${names}`);b.title=names;
  if(!several){const city=el('span','em-pin-town',cluster.items[0].city);b.append(city)}
  const active=state.selected&&cluster.items.some(g=>state.selected.includes(g.key));b.setAttribute('aria-pressed',String(Boolean(active)));pins.append(b);
 }
 state.mapStatus.textContent=`${groups.filter(g=>g.location).length} mapped places · ${state.events.length} dated listings in your filters${state.events.some(e=>e.format==='Virtual')?' · online events listed alongside':''}`;
}
function build(state){
 state.observer?.disconnect();state.host.replaceChildren();const section=el('section','event-regional-map');state.host.append(section);
 const header=el('div','em-heading');header.append(el('p','em-eyebrow','FIND A LITTLE ADVENTURE'),el('h2','',state.events.every(e=>e.format==='Virtual')?'Join from home.':'Where shall we go?'),el('p','em-intro','Choose a place on the map, then a date. The same event filters apply here.'));section.append(header);
 if(!state.events.length){section.append(el('p','em-empty','No dated events match these filters. Try another month or region.'));return;}
 const tools=el('div','em-tools');const reset=button('Show all matching places',()=>{state.bounds=fit(state.groups);state.selected=null;listVenues(state,state.groups);draw(state);state.selection.textContent='All matching places are listed below.';});tools.append(reset);const listJump=button('Go to place list ↓',()=>{state.listHeading.focus();state.listHeading.scrollIntoView({block:'nearest',behavior:'auto'});});tools.append(listJump);section.append(tools);
 state.mapStatus=el('p','em-count');state.mapStatus.setAttribute('role','status');section.append(state.mapStatus);
 const layout=el('div','em-layout');const main=el('div','em-map-column');state.canvas=el('div','em-canvas');state.canvas.setAttribute('role','region');state.canvas.setAttribute('aria-label','Regional event location map; matching locations also listed below');state.pins=el('div','em-pins');state.canvas.append(state.pins);main.append(state.canvas,el('p','em-legend','Numbered pins match the place list. “Places” bubbles group nearby venues; select one to look closer.'));
 main.append(el('p','em-note','Regional location guide. Pins are approximate venue locations, not entrances, parking spaces or verified accessible routes.'));
 const credit=el('p','em-credit');credit.append('Geography: ',link('U.S. Census Bureau',state.data.basemap.source),'. Location sources checked '+new Date(state.data.checkedAt+'T12:00:00Z').toLocaleDateString('en-US',{timeZone:'UTC',month:'long',day:'numeric',year:'numeric'})+'.');main.append(credit);
 const aside=el('div','em-list-column');state.listHeading=el('h3','em-list-heading','Places & dates');state.listHeading.tabIndex=-1;state.selection=el('p','em-selection','All matching places are listed below.');state.selection.setAttribute('aria-live','polite');state.list=el('div','em-place-list');aside.append(state.listHeading,state.selection,state.list);layout.append(main,aside);section.append(layout);
 listVenues(state,state.selected?state.groups.filter(g=>state.selected.includes(g.key)):state.groups);draw(state);if(state.events.every(e=>e.format==='Virtual')){main.hidden=true;state.selection.textContent='These matching events are online. Choose a date for registration and joining details.'}
 if(typeof ResizeObserver!=='undefined'){let previous=state.canvas.clientWidth;state.observer=new ResizeObserver(()=>{const next=state.canvas.clientWidth;if(next&&Math.abs(next-previous)>10){previous=next;draw(state)}});state.observer.observe(state.canvas)}
}
async function render(host,events,onSelect){
 if(!host)return;let state=instances.get(host);if(!state){state={host,seq:0,signature:'',bounds:null,selected:null};instances.set(host,state)}
 const seq=++state.seq;state.events=Array.isArray(events)?events.slice():[];state.onSelect=onSelect;
 const signature=state.events.map(e=>[e.id,e.venue,e.address,e.start].join('|')).join('\n');const changed=signature!==state.signature;state.signature=signature;
 host.setAttribute('aria-busy','true');if(!host.children.length)host.append(el('p','em-loading','Loading the location map…'));
 try{
  request||=fetch(dataURL).then(r=>{if(!r.ok)throw Error('Map locations unavailable');return r.json()}).catch(e=>{request=null;throw e});const data=await request;if(seq!==state.seq)return;
  state.data=data;state.groups=groupEvents(state.events,data);if(changed||!state.bounds){state.bounds=fit(state.groups);state.selected=null}build(state);host.setAttribute('aria-busy','false');
 }catch(error){if(seq!==state.seq)return;host.setAttribute('aria-busy','false');host.replaceChildren();host.append(el('p','em-note','The regional map could not load. You can still choose an event or use venue directions below.'),button('Try the map again',()=>render(host,state.events,state.onSelect)));state.list=el('div','em-place-list');host.append(state.list);state.groups=groupEvents(state.events,null);listVenues(state,state.groups);}
}
window.AUsomeEventMap={render};
})();
