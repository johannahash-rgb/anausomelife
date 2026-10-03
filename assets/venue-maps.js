/* An AUsome Life venue orientation. No geolocation, trackers, route inference or remote map tiles. */
(() => {
  'use strict';
  const scriptURL = document.currentScript?.src || new URL('/assets/venue-maps.js', location.href).href;
  const dataURL = new URL('../data/venue-maps.json', scriptURL).href;
  let collection;
  const node = (tag, cls, text) => { const el = document.createElement(tag); if (cls) el.className = cls; if (text) el.textContent = text; return el; };
  const link = (label, href, cls = '') => { const a = node('a', cls, label); a.href = href; return a; };
  const slug = value => value.toLowerCase().replace(/^favorite-places-/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const sourceLinks = (venue, ids) => { const p = node('p','vm-citations'); (ids || []).forEach((id, i) => { const s = venue.sources.find(item => item.id === id); if (s) { if (i) p.append(' · '); p.append(link(s.label, s.url)); } }); return p; };
  function render(host, venue) {
    host.replaceChildren();
    const section = node('section', 'venue-map');
    const head = node('header', 'vm-header');
    head.append(node('p','vm-eyebrow','BEFORE WE GO / FIND OUR WAY'));
    head.append(node('h2','', venue.map ? 'A little map. A clearer plan.' : `Finding our way at ${venue.name}`));
    head.append(node('p', 'vm-summary', venue.summary));
    const status = node('p','vm-status',venue.statusLabel);head.append(status);section.append(head);
    if (venue.map) {
      const figure = node('figure','vm-figure');const picture = document.createElement('picture');
      const source = document.createElement('source');source.media='(max-width: 560px)';source.srcset=venue.map.mobile;
      const img = document.createElement('img');img.src=venue.map.desktop;img.alt=venue.map.alt;img.width=900;img.height=610;img.loading='lazy';img.decoding='async';
      picture.append(source,img);figure.append(picture);
      const caption=node('figcaption','vm-caption');caption.append(node('strong','',venue.map.mode+'. '),document.createTextNode(venue.map.routeStatus));figure.append(caption);section.append(figure);
      const actions=node('div','vm-actions');actions.append(link('Open larger map',venue.map.desktop,'vm-button'),link('Get printable map (PDF)',venue.map.printPdfUrl || venue.map.printUrl,'vm-button'));section.append(actions);
      const stops=node('ol','vm-stops');stops.setAttribute('aria-label','Map landmarks');
      venue.landmarks.forEach(stop => {const li=node('li');const details=node('details');const summary=node('summary');const number=node('span','vm-number',String(stop.number));number.setAttribute('aria-hidden','true');summary.append(number,document.createTextNode(stop.name));details.append(summary,node('p','',stop.detail),sourceLinks(venue,stop.sourceIds));li.append(details);stops.append(li);});section.append(stops);
    }
    if (venue.officialMaps?.length) { const actions=node('div','vm-actions');venue.officialMaps.forEach(item=>actions.append(link(item.label,item.url,'vm-button')));section.append(actions); }
    if (venue.facts?.length) {
      const facts=node('div','vm-facts');
      venue.facts.forEach(fact=>{const item=node('article','vm-fact');item.append(node('h3','',fact.label),node('p','',fact.text),sourceLinks(venue,fact.sourceIds));facts.append(item);});section.append(facts);
    }
    const unknown=node('details','vm-ask');unknown.open=Boolean(venue.map || venue.status==='arrival-notes');unknown.append(node('summary','','What to confirm before relying on this'));
    const list=node('ul');venue.unknowns.forEach(text=>list.append(node('li','',text)));unknown.append(list);section.append(unknown);
    const footer=node('footer','vm-footer');
    if (venue.reviewedAt) footer.append(node('p','',`Sources checked ${new Date(venue.reviewedAt+'T12:00:00Z').toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric',timeZone:'UTC'})}. Openings and conditions can change.`));
    if (venue.map) {const p=node('p','');p.append(link(venue.map.credit,venue.map.creditUrl),' · ',link('Download map data (ODbL)',venue.map.dataUrl));footer.append(p);}
    if (!venue.facts.length && venue.sources.length) venue.sources.forEach(s=>footer.append(link(s.label,s.url,'vm-source-link')));
    section.append(footer);host.append(section);
  }
  async function mount(scope=document) {
    const targets=[...(scope.matches?.('[data-venue-map]')?[scope]:[]),...scope.querySelectorAll('[data-venue-map]')].filter(x=>!x.dataset.venueMapLoaded);
    if (!targets.length) return;
    targets.forEach(el=>el.dataset.venueMapLoaded='loading');
    try {
      collection ||= fetch(dataURL).then(r=>{if(!r.ok)throw new Error('Map data unavailable');return r.json();}).catch(error=>{collection=null;throw error;});
      const data=await collection;
      targets.forEach(host=>{const key=slug(host.dataset.venueMap);const venue=data.venues.find(v=>slug(v.id)===key||(v.aliases||[]).some(a=>slug(a)===key));
        if(venue){render(host,venue);host.dataset.venueMapLoaded='true';}
        else{host.replaceChildren(node('p','vm-fallback','A venue map is not yet verified here. Use the venue’s current accessibility information and ask staff about the entrance, restroom and exit.'));host.dataset.venueMapLoaded='unavailable';}
      });
    } catch(error) {
      targets.forEach(host=>{host.replaceChildren(node('p','vm-fallback','The map could not load. The venue’s contact and accessibility information on this page can help you plan.'));const retry=node('button','vm-button','Try loading the map again');retry.type='button';retry.onclick=()=>{delete host.dataset.venueMapLoaded;mount(host);};host.append(retry);host.dataset.venueMapLoaded='error';});
    }
  }
  window.AUsomeVenueMaps={mount};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>mount());else mount();
})();
