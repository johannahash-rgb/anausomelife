#!/usr/bin/env python3
"""Build the static magazine, search index and sourced guide pages. No dependencies beyond stdlib + lxml."""
from pathlib import Path
from lxml import html as LH
from html import escape as E
import re,json,math,shutil
ROOT=Path(__file__).resolve().parent.parent
BASE='https://anausomelife.com'
VERSION='magazine-20261003'
CATS={
'home':('At home','A little order. A good meal. Room to live.'),
'outings':('Out & about','New England, one good stop at a time.'),
'family':('Family life','Communication, choice and the support that fits.'),
'style':('Getting dressed','Classic clothes that feel like themselves.'),
'beauty':('The little refresh','Salons, small rituals and feeling like you.'),
'holidays':('Days to celebrate','Keep the meaning. Make the plan your own.'),
'advocacy':('School & advocacy','Prepare the question. Keep the useful record.'),
'advice':('A good question','Thoughtful answers to everyday family dilemmas.'),
'brands':('The little black book','Good places and useful discoveries, with the relationships clear.'),
'stories':('The family notebook','The moments, places and details worth keeping.')}
ALIASES={'celebrations':'holidays','school':'advocacy','access':'family','wardrobe':'style'}
def txt(s):return re.sub(r'\s+',' ',LH.fromstring('<div>'+s+'</div>').text_content()).strip()
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def read(p):return (ROOT/p).read_text()
def write(p,s):f=ROOT/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s)
def head(title,desc,path):
 return f'<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | An AUsome Life</title><meta name="description" content="{E(desc,quote=True)}"><meta name="theme-color" content="#163b4b"><link rel="canonical" href="{BASE}{path}"><meta property="og:title" content="{E(title,quote=True)}"><meta property="og:description" content="{E(desc,quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{BASE}{path}"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/assets/site.css?v={VERSION}"><link rel="stylesheet" href="/assets/magazine.css?v={VERSION}"></head>'
def header(current=''):
 links=[('/library.html','The library'),('/favorite-places.html','Favorite places'),('/calendar.html','The calendar'),('/about.html','Our story')]
 nav=''.join(f'<a href="{p}"'+(' aria-current="page"' if p==current else '')+f'>{s}</a>' for p,s in links)
 return '<a class="skip" href="#main">Skip to content</a><div class="edition-line"><span>New England &amp; the everyday</span><span>A family-life field guide</span></div><header class="mag-masthead"><a class="mag-brand" href="/" aria-label="An AUsome Life home"><img src="/assets/coastal-emblem.webp" alt="" width="80" height="80"><span>An AUsome Life<small>Beautiful. Useful. Lived in.</small></span></a><nav aria-label="Main navigation">'+nav+'<a class="nav-search" href="/library.html#library-search">Search <span aria-hidden="true">↗</span></a></nav></header>'
def footer():return '<footer class="mag-footer"><div class="wrap"><div><a class="footer-wordmark" href="/">An AUsome Life</a><p>Simple good things.<br>The practical details left in.</p></div><nav aria-label="Footer navigation"><a href="/library.html">The library</a><a href="/favorite-places.html">Favorite places</a><a href="/calendar.html">The calendar</a><a href="/visit-story.html">Visual visit planner</a><a href="/little-black-book.html">The little black book</a><a href="/contact.html">Contact</a><a href="/media/">Media &amp; partnerships</a></nav><div class="footer-small"><a href="/language.html">Language &amp; representation</a><a href="/disclosure.html">Disclosure</a><a href="/privacy.html">Privacy</a><a href="/accessibility.html">Accessibility</a><a href="https://www.instagram.com/anausomelife/">Instagram ↗</a><span>© 2026 An AUsome Life · New England</span></div></div></footer>'
def page(title,desc,path,body,cls='',script=''):
 return head(title,desc,path)+f'<body class="magazine-shell {cls}">'+header(path)+'<main id="main">'+body+'</main>'+footer()+f'<script src="/assets/magazine.js?v={VERSION}" defer></script>'+script+'</body></html>'
def art(cat):
 opts=[f'assets/catalog-{ {'beauty':'manicure','advocacy':'advice','holidays':'celebrations','brands':'tote','stories':'outings'}.get(cat,cat)}.webp',f'assets/catalog-{ {"beauty":"style","advocacy":"advice","holidays":"celebrations","brands":"tote","stories":"outings"}.get(cat,cat)}.webp','assets/catalog-home.webp']
 return '/'+next(p for p in opts if (ROOT/p).exists())
def image(src,alt='',cls='',lazy=True):return f'<img src="{E(src)}" alt="{E(alt,quote=True)}" class="{cls}" loading="'+('lazy' if lazy else 'eager')+'" decoding="async">'
def card(a,illustrated=False):
 media=image(a.get('image') or art(a['category'])) if illustrated else ''
 return f'<article class="index-card" data-category="{a["category"]}" data-format="{a["format"]}" data-url="{a["url"]}">'+media+f'<div><p class="entry-meta">{E(CATS[a["category"]][0])} <span>·</span> {E(a["format"])}'+(f' <span>·</span> {a["minutes"]} min' if a.get('minutes') else '')+f'</p><h3><a href="{a["url"]}">{E(a["title"])}</a></h3><p>{E(a["summary"])}</p></div></article>'
# Existing pages keep their content and URLs. These are the preferred directory routes.
DUPES={'book-barn-niantic','codman-community-farms','decordova-sculpture-park','drumlin-farm','gilsland-farm','kittery-food-mart-fort-mcclary','lifetime-burlington','llbean-freeport','misty-harbor-resort','nubble-lighthouse','rococo-ice-cream'}
OMIT={'index.html','404.html','about.html','accessibility.html','contact.html','disclosure.html','privacy.html','product-guides.html','favorite-places.html','links.html','series.html','language.html'}
CAT_EXIST={
'home':['at-home','household-reset','family-command-center-guide','last-minute-guests-pantry-kit'],
'outings':['new-england-weekends','pool-weekend-kit','rainy-day-outing-plan','shorter-visit-plan','hotel-pool-checklist','food-away-from-home-guide'],
'family':['older-teen-edit','profoundly-awesome','multimodal-communication','aac-outing-note','quiet-break-plan','caregiver-handover-guide','older-teen-swim-guide','family-planning-toolkit'],
'style':['family-wardrobe','sensory-clothing-checklist','photo-day-prep'],
'holidays':['gifts-worth-giving','last-minute-gift-kit','photo-gifts-from-your-camera-roll'],
'brands':['things-weve-bought','how-we-choose']}
catmap={n:c for c,ns in CAT_EXIST.items() for n in ns}
def existing_records():
 out=[]
 baseline=ROOT.parent/'magazine-baseline'
 scan=baseline if baseline.exists() else ROOT
 for f in sorted(scan.rglob('*.html')):
  rel=f.relative_to(scan).as_posix()
  if rel in OMIT or rel.startswith(('media/','guides/','topics/')):continue
  s=f.read_text(); d=LH.fromstring(s)
  if not d.xpath('//h1') or d.xpath('//meta[translate(@http-equiv,"REFSH","refsh")="refresh"]'):continue
  isplace=rel.startswith('favorite-places')
  if rel.startswith('favorite-places/') and f.stem in DUPES:continue
  if not isplace and f.stem not in catmap:continue
  title=txt(LH.tostring(d.xpath('//h1')[0],encoding='unicode'))
  if isplace and ': ' in title:title=title.split(': ',1)[0]
  desc=d.xpath('//meta[@name="description"]/@content');summ=desc[0] if desc else ''
  if len(summ)>205:summ=summ[:202].rsplit(' ',1)[0]+'…'
  main=d.xpath('//main');body=txt(LH.tostring(main[0],encoding='unicode')) if main else ''
  cat='outings' if isplace else catmap.get(f.stem,'family')
  fmt='Place' if isplace else ('Toolkit' if any(x in f.stem for x in ['kit','checklist','note']) else 'Guide')
  imgs=d.xpath('//main//figure//img/@src'); img=next((v for v in imgs if not v.endswith('.svg')),'')
  a=dict(slug=f.stem,url='/'+rel,title=title,summary=summ,category=cat,format=fmt,minutes=max(1,math.ceil(len(body.split())/220)),image=img,search=body,existing=True)
  if isplace:
   loc=d.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," favorite-place-name ")]/text()');a['location']=' '.join(loc).strip()
   if not a['location']:
    # Existing metadata contains a location paragraph immediately after the title.
    hn=d.xpath('//h1')[0]; nxt=hn.getnext(); a['location']=txt(LH.tostring(nxt,encoding='unicode')) if nxt is not None and nxt.tag=='p' else 'New England'
   if not any(st in a['location'] for st in ['Maine','Massachusetts','Connecticut','Rhode Island']): a['location']='New England'
  out.append(a)
 out.append(dict(slug='little-black-book',url='/little-black-book.html',title='The little black book',summary='Eight businesses from our published Favorite Places, with field notes and official links.',category='brands',format='Guide',minutes=2,image='/assets/catalog-tote.webp',search='brands businesses favorites logos ice cream books groceries shopping',existing=True))
 out.append(dict(slug='family-notebook',url='/family-notebook.html',title='From the family camera roll',summary='Original photographs from an orchard afternoon, the Book Barn, York and the L.L.Bean trout pond.',category='stories',format='Story',minutes=1,image='/assets/orchard-afternoon-clean.jpg',search='photographs family stories orchard New England Book Barn York L.L.Bean trout pond',existing=True))
 return out

def load_new():
 p=ROOT/'content/articles.json'
 return json.loads(p.read_text()) if p.exists() else [json.loads(f.read_text()) for f in sorted((ROOT/'content/articles').glob('*.json'))]

def build_articles(records):
 new=[]
 for a in load_new():
  a=dict(a);a['category']=ALIASES.get(a['category'],a['category']); a['url']='/guides/'+a['slug']+'.html';a['summary']=a.get('summary',a.get('dek',''));a['format']={'Practical guide':'Guide','Editorial advice question':'Advice','Researched occasion guide':'Guide','Question & answer':'Advice'}.get(a.get('format','Guide'),a.get('format','Guide'));a['minutes']=max(1,math.ceil(len(txt(a['body_html']).split())/220));a['image']=a.get('image') or ('/assets/'+{'one-week-tech-trial':'catalog-quiet-kit.webp','offline-outing-folder':'catalog-road-notes.webp','scan-it-on-your-phone':'catalog-road-notes.webp','holiday-meal-two-timetables':'catalog-hosting.webp','the-grocery-list-handoff':'catalog-hosting.webp','easter-at-ocean-house':'catalog-celebrations.webp'}.get(a['slug'],'') if a['slug'] in ['one-week-tech-trial','offline-outing-folder','scan-it-on-your-phone','holiday-meal-two-timetables','the-grocery-list-handoff','easter-at-ocean-house'] else art(a['category']));a['search']=txt(a['body_html']);new.append(a)
 allr=records+new
 for a in new:
  dom=LH.fromstring('<div>'+a['body_html']+'</div>');toc=[]
  for i,h in enumerate(dom.xpath('.//h2')): h.set('id',h.get('id') or 'section-'+str(i+1));toc.append((h.get('id'),h.text_content()))
  body=''.join(LH.tostring(ch,encoding='unicode') for ch in dom)
  source='<details class="source-panel"><summary>Sources &amp; editorial notes</summary><p>Reviewed '+E(a.get('sourceCheckDate',a.get('updatedAt','October 2026')))+'. General planning information; individual circumstances and current policies can differ.</p><ul>'
  for s in a.get('sources',[]):source+=f'<li><a href="{E(s["url"],quote=True)}">{E(s.get("title",s["url"]))} ↗</a>'+(' — '+E(s['note']) if s.get('note') else '')+'</li>'
  source+='</ul>'+('<p>'+E(a['jurisdiction'])+'</p>' if a.get('jurisdiction') else '')+'</details>'
  related=[r for r in allr if r['slug'] in a.get('related_slugs',[])][:3]
  if len(related)<3: related+=[r for r in allr if r['category']==a['category'] and r['slug']!=a['slug'] and r not in related][:3-len(related)]
  top=f'<div class="wrap article-crumb"><a href="/">Home</a><span>/</span><a href="/library.html">The library</a><span>/</span><a href="/topics/{a["category"]}.html">{E(CATS[a["category"]][0])}</a></div><header class="article-heading wrap"><img class="chapter-art" src="{a["image"]}" alt="" width="180" height="180"><p class="eyebrow">{E(CATS[a["category"]][0])} · {E(a["format"])} · {a["minutes"]} minute read</p><h1>{E(a["title"])}</h1><p class="article-dek">{E(a["summary"])}</p><div class="article-utility"><span>By An AUsome Life · Editorial guide</span><button type="button" data-print>Print this guide</button></div></header>'
  jump='<aside class="article-toc"><details open><summary>In this guide</summary><ol>'+''.join(f'<li><a href="#{id}">{E(t)}</a></li>' for id,t in toc)+'</ol></details></aside>'
  content=f'<div class="article-layout wrap">{jump}<article class="article-body">{body}{source}</article></div><section class="section reading-section"><div class="wrap"><p class="eyebrow">Keep the useful thread</p><h2>A little more help.</h2><div class="entry-grid">'+''.join(card(r) for r in related)+'</div></div></section>'
  write(a['url'][1:],page(a['title'],a['summary'],a['url'],top+content,'long-read'))
 return allr

def topic_options(selected=''):return '<option value="">Every topic</option>'+''.join(f'<option value="{k}"'+(' selected' if k==selected else '')+f'>{E(v[0])}</option>' for k,v in CATS.items())
def catalog(records,path='/library.html',topic=''):
 title=CATS[topic][0] if topic else 'The library'
 desc=CATS[topic][1] if topic else 'A place for the question in front of you.'
 display=records
 hero=f'<section class="library-heading wrap"><p class="eyebrow">The An AUsome Life directory</p><h1>{E(title)}.</h1><p class="article-dek">{E(desc)}</p><p class="quiet-copy">Good guides, useful lists and New England field notes. Read a little. Find the part you need.</p></section>'
 ui='<section class="library-workspace wrap" data-library data-default-topic="'+topic+'"><form class="library-controls" role="search"><div class="search-field"><label for="library-search">What would make today easier?</label><div><input id="library-search" name="q" type="search" placeholder="Try pool, laundry, an IEP meeting…" autocomplete="off"><button type="submit" aria-label="Search the library">Search</button></div></div><div class="filter-row"><label>Topic<select name="topic">'+topic_options(topic)+'</select></label><label>Read or do<select name="type"><option value="">Every format</option><option>Guide</option><option>Place</option><option>Toolkit</option><option>Advice</option><option>Story</option></select></label><label>Arrange by<select name="sort"><option value="recommended">Recommended</option><option value="az">A–Z</option><option value="short">Shortest read</option></select></label><button class="reset-link" type="reset">Reset filters</button></div></form><div class="results-bar"><p data-result-status role="status" aria-live="polite">'+str(len(display))+' useful reads</p><a href="/library.html">Browse every topic</a></div><div class="library-results">'+''.join(card(a) for a in display)+'</div><div class="empty-state" hidden><h2>No exact match. A smaller search might help.</h2><p>Try one word, choose another topic, or clear the filters.</p><button class="button secondary" type="button" data-clear-all>Show all guides</button></div><div class="load-more" hidden><button class="button secondary" type="button" data-load-more>Show more guides</button></div><noscript><p>All '+str(len(display))+' guides are shown below the filters. Search and filters work with JavaScript enabled; every guide link works without it.</p></noscript></section>'
 return page(title,'Browse practical family-life guides by topic and format.',path,hero+ui,'library-page')

def main():
 existing=existing_records();records=build_articles(existing)
 write('data/library.json',json.dumps([{k:v for k,v in a.items() if k in ['slug','url','title','summary','category','format','minutes','image','topics','location']} for a in records],ensure_ascii=False,separators=(',',':')))
 search_files=[]
 for i in range(0,len(records),10):
  path='data/search-'+str(i//10+1)+'.json'; search_files.append('/'+path)
  write(path,json.dumps([{'url':a['url'],'search':a.get('search','')} for a in records[i:i+10]],ensure_ascii=False,separators=(',',':')))
 write('data/search-manifest.json',json.dumps(search_files))
 write('library.html',catalog(records))
 for cat in CATS:write('topics/'+cat+'.html',catalog(records,'/topics/'+cat+'.html',cat))
 # Archive the former homepage's resource-rich content rather than discarding it.
 baseline=ROOT.parent/'magazine-baseline'
 if baseline.exists() and not (ROOT/'field-notes.html').exists():
  old=(baseline/'index.html').read_text().replace('href="https://anausomelife.com/"','href="https://anausomelife.com/field-notes.html"');write('field-notes.html',old)
 places=[a for a in records if a['format']=='Place'];write('data/places.json',json.dumps([{k:v for k,v in a.items() if k in ['slug','url','title','summary','location','image','storyPhoto']} for a in places],ensure_ascii=False,indent=2))
 # Magazine front page: a compact cover, an editorial selection, a useful directory.
 feature_slugs=['household-reset','multimodal-communication','last-minute-gift-kit']
 featured=[a for s in feature_slugs for a in records if a['slug']==s]
 latest=[a for wanted in ['wet-weather-entryway','virtual-iep-meeting-opening','the-pedicure-menu'] for a in records if a['slug']==wanted]
 hero='<section class="cover wrap"><div class="cover-copy"><p class="eyebrow">The everyday, thoughtfully arranged</p><h1>Room for<br>a good day.</h1><p>Beautiful, useful ideas for family life with profound autism. A little planning. A little pleasure. The practical details that make room for both.</p><a class="editorial-link" href="/library.html">Find your useful thing <span aria-hidden="true">→</span></a></div><figure>'+image('/assets/catalog-hero.webp','Watercolor still life of a navy tote, folded towels, a notebook, a cup and a leafy branch.','',False)+'<figcaption>Small things. A little more possibility.</figcaption></figure></section>'
 cats=['home','outings','family','style','beauty','holidays','advocacy','advice']
 dirs='<section class="section topic-section wrap"><div class="section-line"><div><p class="eyebrow">A well-organized little world</p><h2>What brings you here?</h2></div><a href="/library.html">See the whole library ↗</a></div><div class="topic-grid">'+''.join(f'<a href="/topics/{k}.html">'+image(art(k))+f'<strong>{E(CATS[k][0])}</strong><span>{E(CATS[k][1])}</span></a>' for k in cats)+'</div></section>'
 picks='<section class="section cream-section"><div class="wrap"><div class="section-line"><div><p class="eyebrow">The useful edit</p><h2>A good place to begin.</h2></div><a href="/library.html">All the guides ↗</a></div><div class="entry-grid">'+''.join(card(a,True) for a in (latest or featured))+'</div></div></section>'
 placefeat='<section class="section wrap home-field"><div><p class="eyebrow">Out &amp; about</p><h2>One good place.<br>A plan that fits.</h2><p>Where to park. What to ask. Where to pause. A directory of New England places with room for a shorter visit.</p><div class="actions"><a class="button" href="/favorite-places.html">Explore the places</a><a class="text-link" href="/calendar.html">See what’s on</a></div><a class="quiet-link" href="/visit-story.html">Make a visual plan for your visit →</a></div><figure>'+image('/assets/york-maine-clean.jpg','A family photograph from a visit to York, Maine.')+'<figcaption>York, Maine · From the family camera roll</figcaption></figure></section>'
 notes='<section class="section notebook-section wrap"><div class="section-line"><div><p class="eyebrow">A few practical details</p><h2>Keep these close.</h2></div></div><div class="quick-links"><a href="/family-planning-toolkit.html"><span>01</span><strong>A plan for the week</strong><p>Simple, editable planning cards.</p></a><a href="/field-notes.html#access-request"><span>02</span><strong>The words to ask</strong><p>Borrow an access-request note.</p></a><a href="/visit-story.html"><span>03</span><strong>See the visit first</strong><p>Make a photo-by-photo outing plan.</p></a></div></section>'
 about='<section class="about-strip"><div class="wrap"><p class="eyebrow">One family’s point of view</p><h2>High support needs.<br>A whole, interesting life.</h2><p>Autism is part of the life here. So are New England, favorite clothes, good food, ordinary pleasures and the people we love.</p><a class="editorial-link" href="/about.html">Meet An AUsome Life →</a><br><a class="quiet-link" href="/family-notebook.html">From the family camera roll →</a></div></section>'
 compat='<details class="legacy-links wrap"><summary>Looking for the planning notes?</summary><p>The original checklists, copyable requests and communication notes are together in the <a href="/field-notes.html">practical field notes</a>.</p></details>'
 write('index.html',page('An AUsome Life','Beautiful, useful family-life ideas, New England outings and practical details for life with profound autism.','/',hero+dirs+picks+placefeat+notes+about+compat,'mag-home'))
 # One directory entry per place, with simple geographic browsing and full detail behind each title.
 rows=''.join(f'<article class="place-row" data-place-state="{E(a.get("location","New England"))}"><div><p class="entry-meta">{E(a.get("location","New England"))}</p><h2><a href="{a["url"]}">{E(a["title"])}</a></h2><p>{E(a["summary"])}</p><a class="story-link" href="/visit-story.html?place={a["slug"]}">Make a visual visit plan →</a></div><span class="place-arrow" aria-hidden="true">↗</span></article>' for a in places)
 directory='<section class="library-heading wrap"><p class="eyebrow">The New England field guide</p><h1>Favorite places.</h1><p class="article-dek">Less itinerary. More good day.</p><p class="quiet-copy">The easy version, the practical details and the questions still worth asking. Every place has a visual visit planner you can make your own.</p></section><section class="wrap places-workspace" data-places><form class="place-filters" role="search"><label>Find a place<input name="q" type="search" placeholder="Try beach, books, pool or ice cream"></label><label>Where?<select name="state"><option value="">All New England</option><option>Maine</option><option>Massachusetts</option><option>Connecticut</option><option>Rhode Island</option></select></label><button type="reset" class="reset-link">Clear</button></form><p class="directory-count" role="status" aria-live="polite">'+str(len(places))+' places to know</p><div class="place-list">'+rows+'</div><div class="place-empty empty-state" hidden><h2>No places match yet.</h2><p>Try a different word or choose all New England.</p></div><p class="directory-note">Access is personal, and venues change. Read the linked official source and confirm anything that determines whether your visit can work. Photos are identified where used; illustrations are decorative.</p></section>'
 directory=directory.replace('<option>Maine</option>','<option>Maine</option>')
 write('favorite-places.html',page('Favorite places','A detailed directory of New England places, practical access notes and editable visual visit plans.','/favorite-places.html',directory,'places-page'))
 write('content/catalog-summary.json',json.dumps({'libraryEntries':len(records),'uniquePlaces':len(places),'newArticles':len(load_new()),'categories':{c:len([a for a in records if a['category']==c]) for c in CATS}},indent=2))
 print('Built',len(records),'library entries;',len(places),'unique places;',len(load_new()),'new guides')
if __name__=='__main__':main()
