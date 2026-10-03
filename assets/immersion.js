/* Shared editorial landmarks. All content and tools continue to work without this layer. */
(() => {
  'use strict';
  const path = location.pathname;
  const main = document.querySelector('main');
  const footer = document.querySelector('.mag-footer');
  if (!main || !footer) return;
  const el = (tag, cls, text) => { const n=document.createElement(tag); if(cls)n.className=cls;if(text)n.textContent=text;return n; };
  const img = (src, cls) => {const n=el('img',cls);n.src='/assets/'+src;n.alt='';n.loading='lazy';return n;};
  const groups = {
    outings:{name:'Out & about',url:'/favorite-places.html',art:'catalog-outings.webp',links:[['/calendar.html','What’s on','Find an event and read its field notes.','catalog-celebrations.webp'],['/visit-story.html','See the visit first','Make a picture plan for the outing.','catalog-road-notes.webp'],['/family-notebook.html','The family notebook','Keep a little of the good day.','orchard-afternoon-clean.jpg']]},
    communication:{name:'Communication',url:'/multimodal-communication.html',art:'catalog-quiet-kit.webp',links:[['/communication-card-generator.html','A picture + a word','Make a card with a familiar image.','card-water.webp'],['/visit-story.html','A plan you can see','Pictures and words for the next visit.','catalog-road-notes.webp'],['/multimodal-communication.html','Every way to communicate','Keep familiar communication close.','catalog-quiet-kit.webp']]},
    family:{name:'Family life',url:'/family-roles.html',art:'catalog-family.webp',links:[['/paternal-role.html','The paternal field notes','Simple things to enjoy together.','catalog-hosting.webp'],['/family-planning-toolkit.html','Share the plan','Useful cards for the household handoff.','catalog-advice.webp'],['/family-agreements.html','Our family agreements','Choice, privacy, dignity and room to pause.','catalog-family.webp']]},
    home:{name:'At home',url:'/at-home.html',art:'catalog-home.webp',links:[['/household-reset.html','A small household reset','Choose the time you have.','catalog-home.webp'],['/family-wardrobe.html','Comfort, with character','Familiar clothes that work for you.','catalog-style.webp'],['/family-planning-toolkit.html','Put the plan on paper','Keep the useful details together.','catalog-advice.webp']]},
    play:{name:'Little adventures',url:'/kid-fun.html',art:'little-boot-story.webp',links:[['/little-adventures.html','Meet the little boot','An original story to share.','little-boot-story.webp'],['/favorite-places.html','Find a real adventure','New England, one good stop at a time.','catalog-outings.webp'],['/visit-story.html','Make a picture plan','See your own outing before you go.','catalog-road-notes.webp']]},
    general:{name:'The library',url:'/library.html',art:'catalog-advice.webp',links:[['/favorite-places.html','A good day out','Places, access notes and little discoveries.','catalog-outings.webp'],['/communication-card-generator.html','Take a picture card','A familiar image and a useful word.','card-water.webp'],['/family-roles.html','Life together','Shared rituals and a part for everyone.','catalog-family.webp']]}
  };
  const category = /communication|aac-|visit-story/.test(path)?'communication':/kid-fun|little-adventures/.test(path)?'play':/favorite-places|calendar|weekend/.test(path)?'outings':/family|paternal|profound/.test(path)?'family':/home|household|pantry|wardrobe|topics\/(home|style)/.test(path)?'home':'general';
  const group = groups[category];
  const isHome = path==='/' || path==='/index.html';
  const isTool = /communication-card-generator|communication-notes|visit-story/.test(path);
  const isPolicy = /\/(privacy|disclosure|language|accessibility|contact|media-kit|product-testing-brief)\.html|\/media\//.test(path);
  const brand = document.querySelector('.mag-brand small');
  if (brand) brand.textContent='In pursuit of the Good New England Life';
  if (!footer.querySelector('.footer-emblem')) footer.querySelector('.footer-wordmark')?.before(img('coastal-emblem.webp','footer-emblem'));
  if (!isHome && !isTool && !document.querySelector('.article-crumb, .breadcrumbs, .breadcrumb, .aal-breadcrumb, nav[aria-label="Breadcrumb"]')) {
    const crumb=el('nav','aal-breadcrumb wrap');crumb.setAttribute('aria-label','Breadcrumb');
    const home=el('a','','Home');home.href='/';crumb.append(home,el('span','','/'));
    const current=main.querySelector('h1')?.textContent.trim();
    if(group.url!==path){const link=el('a','',group.name);link.href=group.url;crumb.append(link,el('span','','/'));}
    const label=el('span','',current||document.title.split('|')[0].trim());label.setAttribute('aria-current','page');crumb.append(label);main.prepend(crumb);
  }
  if (!isHome && !isPolicy && !document.querySelector('.aal-more')) {
    const more=el('section','aal-more');more.setAttribute('aria-labelledby','aal-more-title');
    const inner=el('div','wrap');const title=el('h2','','A little more to explore.');title.id='aal-more-title';inner.append(title);
    const grid=el('div','aal-more-grid');
    let links=group.links.filter(row=>row[0]!==path);
    for(const row of groups.general.links)if(links.length<3 && row[0]!==path && !links.some(x=>x[0]===row[0]))links.push(row);
    links.slice(0,3).forEach(([href,title,description,art])=>{const a=el('a');a.href=href;const copy=el('div');copy.append(el('strong','',title),el('span','',description));a.append(copy);grid.append(a);});
    inner.append(grid);more.append(inner);footer.before(more);
  }
})();
