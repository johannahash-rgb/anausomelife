"""Build the Menauhant photo essay from the owner's supplied reflection and media."""
from pathlib import Path
import hashlib, html, json, re
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SLUG='menauhant-beach-the-art-of-letting-go.html'
URL='https://anausomelife.com/'+SLUG
TITLE='The Beautiful Art of Letting Go'
DEK='Three pairs of bare feet, an October ocean, and a father learning when to take a step back. An afternoon at Menauhant Beach in Falmouth.'
PHOTOS={
 'IMG_0035.jpeg':('James lifts an arm as he moves across the sand toward the glittering water at Menauhant Beach.','James, with a whole afternoon in front of him.'),
 'IMG_0130.jpeg':('Michael, wearing a blue jacket and shorts, looks down at the clear water around his bare feet.','Eventually, Dad took his shoes off, too.'),
 'IMG_0103.jpeg':('Bare feet stand together in shallow, clear seawater over rippled sand.','The part of the afternoon none of us had planned.'),
 'IMG_0277.jpeg':('James stands barefoot at the water’s edge, looking across the sunlit sea.','At the edge of the water.'),
 'IMG_0286.jpeg':('James looks down toward the sand as a small wave recedes behind him.','A wave comes in. A wave goes out.'),
 'IMG_0217.jpeg':('Michael and James stand together at the shoreline, with small waves and a stone jetty behind them.','A little room, and his father still there.'),
 'IMG_0039.jpeg':('James stands on the beach facing the bright sea, his long shadow falling across the sand.','A teenager, an October afternoon, and the sea.'),
 'IMG_0290.jpeg':('James stands at the edge of the water beneath a wide blue sky at Menauhant Beach.','For a little while, there was nowhere else to be.'),
 'IMG_0383.jpeg':('James’s mother turns toward the beach while standing barefoot in the sunlit shallows.','The lovely impulse that started it all.'),
 'IMG_0389.jpeg':('James’s mother shades her eyes with one hand and looks across the glittering water.','A moment of her own.'),
 'IMG_0395.jpeg':('James’s mother stands in clear ankle-deep water as a small wave reaches the sand.','Sunlight, salt water, and a little time.'),
 'IMG_0396.jpeg':('James and his mother stand beside one another at the water’s edge, with their shadows across the beach.','The two people I love most.'),
 'IMG_0397.jpeg':('James turns toward the camera while standing barefoot at the edge of a small wave.','His own afternoon.'),
 'IMG_0398.jpeg':('James lifts his arms as he moves along the sunlit waterline.','There was nothing for me to organize.'),
 'IMG_0400.jpeg':('James watches a wave wash around his feet beside the stone jetty.','The sea had his attention.'),
}
def fig(name,eager=False,trim=False):
 alt,cap=PHOTOS[name]
 attrs='fetchpriority="high"' if eager else 'loading="lazy"'
 preview='previews/'+name if (ROOT/'assets/menauhant/previews'/name).exists() else name
 width,height=Image.open(ROOT/'assets/menauhant'/preview).size
 return f'<figure class="beach-figure{(" frame-trim" if trim else "")}"><a href="/assets/menauhant/{name}" data-beach-photo aria-label="View full photograph: {html.escape(alt,quote=True)}"><img src="/assets/menauhant/{preview}" width="{width}" height="{height}" alt="{html.escape(alt,quote=True)}" decoding="async" {attrs}></a><figcaption>{cap}</figcaption></figure>'
def spread(a,b,trim=False):return '<div class="beach-spread">'+fig(a,trim=trim)+fig(b,trim=trim)+'</div>'
def link(url,text):return f'<a href="{html.escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">{text}</a>'

BEACH_CARDS=['beach','towel','photo-13-running-shoes','socks','water','photo-25-seashell','sun-hat','sunscreen','break','help','stop','all-done']
catalog_source=(ROOT/'assets/card-catalog.js').read_text()
card_catalog={c['id']:c for c in json.loads(catalog_source.split('window.AALCardCatalog = ',1)[1].strip().rstrip(';'))}
def beach_cards():
 cards=[]
 for key in BEACH_CARDS:
  c=card_catalog[key];label=html.escape(c['label'],quote=True);description=html.escape(c['description'],quote=True)
  style='background-image:url('+c['image']+');'
  if 'cell' in c:style+=f"background-size:400% 400%;background-position:{c['cell']%4/3*100}% {c['cell']//4/3*100}%;"
  cards.append(f'<div class="aal-pc-card" data-story-card="{key}"><a class="aal-pc-face" href="/picture-card-library.html?card={key}" aria-label="Edit or print {label} card"><span class="aal-pc-image" role="img" aria-label="{description}" style="{style}"></span><span class="aal-pc-label">{label}</span></a><button class="aal-pc-download" type="button" data-story-card-download hidden aria-label="Download {label} picture card as PNG">Download PNG ↓</button></div>')
 return '<details class="beach-details" id="beach-picture-cards"><summary><span class="number" aria-hidden="true">04</span>Beach picture cards · choose, download &amp; print</summary><section class="aal-story-cards beach-card-content" data-story-cards aria-labelledby="beach-cards-title"><h3 id="beach-cards-title">Words to take to the shore.</h3><p>Choose the pictures that are familiar and useful. For example: “towel,” “help,” or “all done.” Keep the person’s usual communication available, too.</p><div class="aal-pc-actions"><a href="/picture-card-library.html?cards='+','.join(BEACH_CARDS)+'#cc-sheet">Edit or print all 12 beach cards →</a></div><div class="aal-pc-grid">'+''.join(cards)+'</div><p class="aal-pc-note">Generic AI-generated object and place pictures with simple communication symbols; the beach card is not a photograph of Menauhant. These independent picture communication cards are not official PECS® materials. This set was prepared after our visit.</p><p class="aal-pc-status" role="status" aria-live="polite" data-story-card-status></p></section></details>'

template=(ROOT/'kohinoor-indian-restaurant-mashpee.html').read_text()
masthead=re.search(r'<div class="edition-line">.*?</header>',template,re.S).group()
footer=re.search(r'<footer class="mag-footer">.*?</footer>',template,re.S).group()
schema={'@context':'https://schema.org','@type':'BlogPosting','headline':TITLE,'description':DEK,'datePublished':'2026-10-25','dateModified':'2026-10-25','author':{'@type':'Organization','name':'An AUsome Life'},'publisher':{'@type':'Organization','name':'An AUsome Life'},'image':['https://anausomelife.com/assets/menauhant/IMG_0035.jpeg'],'mainEntityOfPage':URL}
head=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{TITLE} · Menauhant Beach | An AUsome Life</title><meta name="description" content="{html.escape(DEK,quote=True)}"><link rel="canonical" href="{URL}"><meta name="theme-color" content="#183d50"><link rel="icon" href="/favicon.ico">
<link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/magazine.css"><link rel="stylesheet" href="/assets/editorial.css?v=20261003-mainstreet"><link rel="stylesheet" href="/assets/illustrated-navigation.css"><link rel="stylesheet" href="/assets/family-field-notes.css"><link rel="stylesheet" href="/assets/journal-picture-cards.css?v=20261025"><link rel="stylesheet" href="/assets/menauhant.css?v=20261025-cards">
<meta property="og:title" content="An October afternoon at Menauhant Beach | An AUsome Life"><meta property="og:description" content="{html.escape(DEK,quote=True)}"><meta property="article:published_time" content="2026-10-25"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script><script src="/assets/global-nav.js?v=20261004-art-direction" data-aal-global-nav="true" defer></script></head>
<body class="magazine-shell fn-page beach-page"><a class="skip" href="#main">Skip to content</a>{masthead}<main id="main">
<nav class="wrap fn-breadcrumb" aria-label="Breadcrumb"><a href="/blog.html">The journal</a> / Menauhant Beach, Cape Cod</nav>
<header class="wrap beach-cover"><div><p class="beach-kicker">Falmouth, Massachusetts · October by the sea</p><h1>{TITLE}</h1><p class="fn-dek">Three pairs of bare feet, an October ocean, and a father learning when to take a step back.</p><p class="fn-byline">A reflection from James’s dad · <time datetime="2026-10-25">October 25, 2026</time></p><nav class="beach-jumps" aria-label="In this story"><a href="#reflection">Read the reflection</a><a href="#beach-films">Watch the afternoon</a><a href="#shore-notes">Explore the beach</a><a href="#beach-picture-cards">Beach picture cards</a></nav></div>{fig('IMG_0035.jpeg',True)}</header>
<article class="beach-story" id="reflection" aria-label="A father’s reflection">
<p class="lead">My wife took off her shoes first.</p>
<p>We had stopped at Menauhant Beach in Falmouth early on Sunday afternoon. It was October, and this was a detour, not a swimming expedition. Nevertheless, off came her shoes and socks, and into the ocean she went.</p>
<p>James saw his mother in the water and followed. Before long, I had abandoned my own shoes and socks and joined them.</p>
<p>The water was ice cold. Bracing, certainly. Invigorating, if you were feeling generous. It was also rather difficult to argue with the two people already enjoying it.</p>
{spread('IMG_0130.jpeg','IMG_0103.jpeg')}
<h2>A little room</h2>
<p>My first instinct was to follow James closely. Watch each step. Anticipate the next one. It is a familiar reflex when you have spent years attending to a child’s safety: you begin to move before you have quite decided whether you need to.</p>
<p>This time, I stopped myself.</p>
<p>I was still watching. But I hung back.</p>
<p>James has worked extraordinarily hard on his spatial awareness and his understanding of physical safety. There are hours of effort behind the things I was watching him do: learning, repetition, trying again. I knew that work. I had been there for it.</p>
<p>Now I needed to make a little room for what it had made possible.</p>
<blockquote class="beach-quote">James needed the freedom to be a teenager.</blockquote>
<p>He danced in the water. He ran from the incoming waves. His unmistakable sounds of delight carried across the beach. He was choosing when to approach, when to retreat, and when to do the whole thing again.</p>
<p>There was nothing for me to organize. He was thoroughly occupied with his own afternoon.</p>
{spread('IMG_0398.jpeg','IMG_0400.jpeg')}
<p>I found that more moving than I had expected. So much of being his father involves helping him find his way through the world. It is possible to become so accustomed to helping that you fail to notice the moment when your help can take a quieter form.</p>
<p>I could be there and let this belong to him.</p>
<h2>And there was my wife</h2>
<p>She had waded farther out, shielding her eyes from the afternoon sun and looking toward the horizon.</p>
<p class="short-line">She looked absolutely beautiful.</p>
<div class="beach-spread beach-last-photo">{fig('IMG_0389.jpeg')}</div>
<p>I loved seeing her that way. She was enjoying the water, the sunlight, the simple pleasure of having followed an impulse. For a little while, she had something that belonged to her.</p>
<p>Family life, especially with a child who has significant support needs, asks a great deal of your attention. Schedules, concerns, the next thing that needs doing. Even on a good day, some part of you is usually looking ahead.</p>
<p>Here she was, looking out.</p>
<p>And here was James, dancing with the tide.</p>
<p>I stood back and watched the two people I love most in the world.</p>
{spread('IMG_0383.jpeg','IMG_0396.jpeg')}
<h2>Before the shoes went back on</h2>
<p>There was no ceremony to mark any of this. No carefully arranged activity, no formal acknowledgment of the work that had brought James to this particular stretch of water.</p>
<p>There was my son enjoying himself. There was my wife enjoying herself. And there was the unexpected pleasure of realizing that I could simply enjoy them.</p>
<p>Letting go, even a little, asks you to trust the work your child has done. It also asks you to recognize that the moment is his. James did not need me to give his afternoon a meaning. He already knew what he wanted to do with it.</p>
<p>My wife, meanwhile, had reminded me how much can begin with taking your shoes off.</p>
<div class="beach-spread beach-last-photo">{fig('IMG_0290.jpeg')}</div>
<p>Eventually, we would have to put them back on. The schedules and responsibilities would still be there.</p>
<p>But for a little while, on a beach in Falmouth, I watched my son move forward and my wife stand in the sun. I was glad I had joined them. I was glad, too, that I had known when to stand back.</p>
<p class="closing"><em>Three pairs of bare feet. One ice-cold ocean. And a moment of freedom I won’t soon forget.</em></p>
</article>
<section class="beach-films" id="beach-films" aria-labelledby="films-title"><p class="beach-kicker">From the camera roll</p><h2 id="films-title">A little of the afternoon, moving.</h2><p>Two quiet beach films. Press play when you’re ready; these web versions are silent.</p>
<div class="beach-film-grid"><figure><video controls playsinline preload="none" poster="/assets/menauhant/shoreline-poster.jpg" aria-label="James moving along the beach at Menauhant, 49 seconds, silent" aria-describedby="film-one-description"><source src="/assets/menauhant/shoreline.mp4" type="video/mp4"><a href="/assets/menauhant/shoreline.mp4">Open the shoreline video</a></video><figcaption>At his own pace · 49 seconds</figcaption><details><summary>Read a description of this film</summary><p id="film-one-description">James stands barefoot on the sand beside the water. Small waves wash up and recede as he moves along the shoreline. Sunlight glitters across the sea; a stone jetty stretches out farther along the beach.</p></details></figure>
<figure><video controls playsinline preload="none" poster="/assets/menauhant/waves-poster.jpg" aria-label="James watching the waves at Menauhant, 20 seconds, silent" aria-describedby="film-two-description"><source src="/assets/menauhant/waves.mp4" type="video/mp4"><a href="/assets/menauhant/waves.mp4">Open the waves video</a></video><figcaption>The water comes back again · 20 seconds</figcaption><details><summary>Read a description of this film</summary><p id="film-two-description">Seen from the beach, James faces the sea with his trousers rolled above his bare feet. The sunlight catches the small waves in front of him as they come toward the sand and draw back.</p></details></figure></div></section>
<section class="beach-album" aria-labelledby="album-title"><p class="beach-kicker">Photographs by both of us</p><h2 id="album-title">A few more moments to keep.</h2><details class="beach-details"><summary>Open the rest of the album · six photographs</summary><div class="beach-album-grid">{''.join(fig(n,trim=n in ('IMG_0277.jpeg','IMG_0286.jpeg')) for n in ['IMG_0217.jpeg','IMG_0039.jpeg','IMG_0395.jpeg','IMG_0397.jpeg','IMG_0277.jpeg','IMG_0286.jpeg'])}</div></details></section>
<section class="beach-companion" id="shore-notes" aria-labelledby="shore-title"><header><p class="beach-kicker">A companion to the afternoon</p><h2 id="shore-title">The shore has a story, too.</h2><p class="intro">I studied geology during my freshman year at the University of Rhode Island, before transferring. A shoreline has more than one story: the people who have gathered there, and the water, weather, and sand that keep changing it.</p><p>A little history, a little science, and the practical details for finding this stretch of Falmouth.</p></header>
<details class="beach-details"><summary><span class="number" aria-hidden="true">01</span>Before our footprints: a short history</summary><div class="beach-detail-body">
<p>The history of this coast reaches far beyond its summer hotels. The Mashpee Wampanoag Tribe describes a presence in present-day Massachusetts and eastern Rhode Island extending more than 12,000 years. Its {link('https://mashpeewampanoagtribe-nsn.gov/culture','history and culture resources')} are a place to begin with the people whose homeland this region remains.</p>
<h3>A hotel, six cottages, and a wharf</h3><p>In 1874, seven jewelers from Attleboro and John Tobey of East Falmouth formed the Menauhant Land and Wharf Company to establish a summer cottage community. Between 1875 and 1880, they built a hotel, six cottages, and a 120-foot wharf near Central Avenue and Menauhant Road.</p>
<p>The hotel accommodated 150 guests. There were tennis courts, a baseball field, horses, bowling, and Saturday-evening dancing to an orchestra. It burned on June 17, 1918. The neighborhood survived; Jewelers Avenue still recalls those early developers. These details come from Kathy Lanson and Leonard Miele’s {link('https://woodsholemuseum.org/oldpages/sprtsl/v33n2-hotels.pdf','“Resort Hotels of Falmouth,” published by the Woods Hole Historical Museum')}.</p>
<h3>A beach still being made</h3><p>The present shore has its own history of care. In 2007, the town acquired 1.9 acres at the western end of Menauhant with town funds, Community Preservation Act funds, and help from The 300 Committee. The land trust describes the added beachfront as both public shoreline and a source of sand that helps nourish Menauhant. {link('https://300committee.org/conservation-lands-2/haddad-beachfront/','Read about the Haddad Beachfront.')}</p>
<p>The beach is not a fixed stage on which the years pass. Waves, winds, and tides continue to move its sand. There is something fitting about coming here to watch someone grow.</p></div></details>
<details class="beach-details"><summary><span class="number" aria-hidden="true">02</span>Warm sunshine. Cold water. Why?</summary><div class="beach-detail-body">
<p><strong>“Ice cold” describes how it felt to us; we did not record a water temperature.</strong> The bright blue photographs do not tell you how the sea felt around our ankles.</p>
<p>Water takes much more energy to heat and cool than land does. That gives the ocean a slower seasonal rhythm: it stores warmth and releases it gradually. An October afternoon can feel lovely in direct sunshine without bringing the water anywhere close to summer-swimming comfort. The {link('https://www.usgs.gov/water-science-school/science/specific-heat-capacity-and-water','U.S. Geological Survey explains this high heat capacity')}.</p>
<p>There is another difference your feet notice immediately. Water removes heat from the body much faster than air at the same temperature. So a temperature that feels quite manageable on your face can feel startlingly cold around your ankles. {link('https://www.mass.gov/info-details/ice-and-cold-water-safety','Massachusetts’ cold-water guidance')} explains the contrast.</p>
<p>Sunshine is not a water-safety test. The {link('https://www.weather.gov/safety/coldwater','National Weather Service')} cautions that unexpectedly cold water can affect breathing and movement. Check local conditions, keep the supervision and support your family needs, and have dry layers ready.</p></div></details>
<details class="beach-details"><summary><span class="number" aria-hidden="true">03</span>Find Menauhant: map &amp; visiting notes</summary><div class="beach-detail-body">
<p><strong>Menauhant Beach · Menauhant Road · East Falmouth, Massachusetts.</strong> The beach faces Vineyard Sound, with an inlet connecting to Bournes Pond.</p>
<p>{link('https://www.google.com/maps/search/?api=1&query=Menauhant+Beach+East+Falmouth+MA','Open Menauhant Beach in Google Maps')}</p>
<iframe title="Map showing Menauhant Beach in East Falmouth" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="https://maps.google.com/maps?q=Menauhant%20Beach%20East%20Falmouth%20MA&amp;output=embed"></iframe>
<p>The town distinguishes <strong>Menauhant East</strong>, listed as public-welcome parking in its seasonal guidance, from <strong>Menauhant West</strong>, listed for resident-sticker parking. Check the {link('https://www.falmouthma.gov/151/Beach','Falmouth Beach Department')} for current parking rules, fees, closures, and staffed hours before setting out. Summer listings do not establish October services.</p>
<p><strong>Access planning:</strong> the Beach Department lists reservable adapted beach wheelchairs during its service season. Confirm availability for your date, the best access point, restroom arrangements, and your own needs with the department at <a href="tel:+15085488623">508-548-8623</a>. Our photographs show sand and an uneven waterline; this visit was not a full accessibility assessment.</p>
<p><strong>A note from the family:</strong> giving James room here meant watching while allowing him to lead his own moment. Keep the supervision and water-safety supports your family needs.</p>
<p>For a simple shoreline stop: bring a towel, dry socks, a change of layers, and whatever communication supports your family uses. Walking, watching, and leaving when you are ready all count as a beach visit.</p><p class="source-note">Visitor sources checked October 25, 2026. Conditions, staffing, and access can change.</p></div></details>
{beach_cards()}
</section>
'''

graphic_alt='Cream graphic with navy and green lettering: Three pairs of bare feet. One October ocean. Menauhant Beach, Falmouth. A father’s reflection on love, trust, and making room. Read the story at anausomelife.com/menauhant/. An AUsome Life / @anausomelife. No family photograph appears.'
share=f'''<section class="aal-story-share" id="share-this-story" aria-labelledby="share-title" data-share-summary="A father’s reflection on an October afternoon at Menauhant Beach: family photographs, quiet films, local history, and room to enjoy the day."><h2 id="share-title">Pass along a little sea air.</h2><p>A story about family, attention, and the pleasure of an unplanned afternoon.</p><div class="aal-story-actions"><button type="button" data-share-native hidden>Share story</button><button type="button" data-copy-link hidden>Copy story link</button><button type="button" data-copy-caption hidden>Copy caption &amp; credit</button></div><p class="aal-share-status" role="status"></p><div data-share-fallback hidden><label for="beach-share-copy">Select and copy this text</label><textarea id="beach-share-copy" readonly></textarea></div><details class="aal-share-package"><summary>Sharing graphics, captions &amp; image descriptions</summary><div class="beach-share-grid">'''
for kind,height in [('feed',1350),('story',1920)]:
 share+=f'<figure><img src="/downloads/menauhant-social-{kind}.png" width="1080" height="{height}" alt="{graphic_alt}" loading="lazy"><figcaption>{kind.capitalize()} graphic · 1080 × {height}</figcaption><p><a href="/downloads/menauhant-social-{kind}.png" download>Download the {kind} graphic</a></p></figure>'
share+=f'''</div><p class="aal-share-permission">You may share only menauhant-social-feed.png and menauhant-social-story.png unchanged in organic social posts or Stories with An AUsome Life / @anausomelife credit and a link to this story. This permission does not cover family photographs, videos, other site content, edits, or paid advertising.</p><h3>A suggested caption</h3><p class="aal-share-copy-text" data-share-caption>A spontaneous stop at Menauhant Beach in Falmouth became an afternoon worth keeping. James’s dad reflects on watching his son enjoy the waves, seeing his wife have a moment of her own, and learning when to take a step back. Read the photo essay, watch the quiet beach films, and explore the local history and cold-water notes from An AUsome Life.
{URL}
Credit: An AUsome Life / @anausomelife</p><h3>A short Story caption</h3><p class="aal-share-copy-text" id="beach-short-caption">Three pairs of bare feet. One October ocean. A family afternoon at Menauhant Beach, Falmouth, from An AUsome Life / @anausomelife.
{URL}</p><button type="button" data-copy-share-text="beach-short-caption" hidden>Copy Story caption</button><h3>Image description</h3><p id="beach-graphic-alt">{graphic_alt}</p><button type="button" data-copy-share-text="beach-graphic-alt" hidden>Copy image description</button><p>Independent editorial materials from An AUsome Life. <a data-reuse-link href="/media/#sharing">Ask about specific image use.</a></p></details></section>
<nav class="wrap fn-related" aria-label="Related stories"><h2>Stay a little longer.</h2><ul><li><a href="/get-in-the-photograph.html">For the mother behind the camera: get in the photograph.</a></li><li><a href="/kohinoor-indian-restaurant-mashpee.html">A little heat on Cape Cod: dinner at Kohinoor.</a></li></ul><p><a href="/blog.html">Return to the journal</a></p></nav></main>
<dialog class="beach-lightbox" id="beach-lightbox" aria-label="Full-size beach photographs"><form method="dialog"><button type="submit">Close photograph</button></form><img alt=""><p data-photo-caption></p><div class="photo-controls"><button type="button" data-photo-prev aria-label="Previous photograph">Previous</button><span data-photo-count aria-live="polite"></span><button type="button" data-photo-next aria-label="Next photograph">Next</button></div></dialog>
{footer}<script src="/assets/site.js" defer></script><script src="/assets/story-share.js?v=20261025" defer></script><script src="/assets/menauhant.js?v=20261025" defer></script><script src="/assets/card-catalog.js?v=20261025" defer></script><script src="/assets/journal-picture-cards.js?v=20261025" defer></script></body></html>'''
(ROOT/SLUG).write_text(head+share)

# Exact typography, with no family photo reuse in the downloadable sharing package.
serif='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
sans='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def social(kind,height):
 im=Image.new('RGB',(1080,height),'#faf8f1');d=ImageDraw.Draw(im)
 navy='#183d50';green='#315b50'; pad=84
 def lines(text,y,size,font=serif,color=navy,gap=1.24):
  f=ImageFont.truetype(font,size)
  for line in text.split('\n'):
   d.text((pad,y),line,font=f,fill=color);y+=int(size*gap)
  return y
 y=110 if kind=='feed' else 215
 y=lines('AN AUSOME LIFE',y,28,sans,green)+65
 y=lines('Three pairs\nof bare feet.',y,76)+30
 y=lines('One October\nocean.',y,76)+50
 d.line((pad,y,996,y),fill='#9daea4',width=2); y+=45
 y=lines('MENAUHANT BEACH · FALMOUTH',y,25,sans,green)+30
 y=lines('A father’s reflection on love,\ntrust, and making room.',y,36)+42
 y=lines('Read the story',y,25,sans,green)+8
 y=lines('anausomelife.com/menauhant/',y,27,sans)
 lines('An AUsome Life / @anausomelife',height-125,24,sans,green)
 dest=ROOT/f'downloads/menauhant-social-{kind}.png';im.save(dest)
 return {'path':dest.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'dimensions':[1080,height]}
outputs=[social('feed',1350),social('story',1920)]
(ROOT/'menauhant').mkdir(exist_ok=True)
(ROOT/'menauhant/index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url=/{SLUG}"><link rel="canonical" href="{URL}"><title>Menauhant Beach | An AUsome Life</title></head><body><p><a href="/{SLUG}">Read the Menauhant Beach story.</a></p></body></html>')
records=[]
for name,(alt,_) in PHOTOS.items():
 p=ROOT/'assets/menauhant'/name
 records.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size),'alt':alt,'basis':('Original photograph resent by Michael as a Gmail attachment; original bytes preserved, orientation-normalized resized preview supplied without retouching.' if name in ['IMG_0383.jpeg','IMG_0389.jpeg','IMG_0395.jpeg','IMG_0396.jpeg','IMG_0397.jpeg','IMG_0398.jpeg','IMG_0400.jpeg'] else 'Original owner-uploaded photograph; bytes preserved. Display frame may conceal a small strip at the lower edge; full photograph opens on activation.')})
provenance={'created':'2026-10-25','canonical_story':URL,'authorization_basis':'Owner requested a finished beautiful beach story from the supplied family photographs, two videos, and Michael’s emailed reflection, using his established voice and expandable history/temperature sections. Standing site direction supplies publishing and sharing-package defaults.','reflection':'Michael’s Menauhant beach email, dated October 25, 2026. The owner additionally confirmed his freshman-year geology studies at the University of Rhode Island before transferring. Edited for concision and the established public family-privacy convention. No invented quotations or measured water temperature.','sources':records,'video_sources':{'IMG_0303.mp4':'shoreline.mp4','IMG_0096.mp4':'waves.mp4'},'video_edits':'Full-duration, silent H.264 web renditions; no synthetic frames, faces, or scene changes. Posters extracted from the supplied videos. Originals retained in the owner’s uploads.','photo_sources':'Eight owner uploads and seven original JPEG attachments resent by Michael in Menauhant pictures #1 and #2, October 25, 2026. All fifteen originals included. Unrelated Library filename match excluded. No face or smile edits; the supplied mother photographs are candid profile/back views. Preview renditions change only orientation and resolution, with original files linked.','picture_cards':{'ids':BEACH_CARDS,'basis':'Reuse of existing site-owned card artwork and communication symbols. Each selected picture visually checked against its label. No family photographs used as communication symbols. Created after the visit; independent cards, not official PECS materials.'},'photo_rights':'Owner-authorized family photographs supplied by the owner and Michael for this publication. No family-media redistribution license.','scoped_organic_sharing_intent':{'assets_only':[o['path'] for o in outputs],'permitted_intended_use':'Only these original typographic graphics, unchanged organic sharing with credit and canonical story link.','scope_limits':'No family photographs, videos, paid media, edits, or archive-wide license.'},'outputs':outputs,'validation':{'reviewed':'2026-10-25','visual_review':'Verified desktop page and 390-pixel framed mobile layout; full-size photo viewer, next/close controls, native history/temperature disclosures, album, and both videos. Phone layout has no horizontal overflow. Original file hashes match all seven resent photographs. Story-sharing, social-metadata, accessibility-publication, asset-reference, rights-scope, JavaScript syntax, and private-name checks passed.'},'brand_accounts':{'status':'No third-party social handles guessed or tagged.'}}
(ROOT/'docs/menauhant-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
registry=ROOT/'docs/story-sharing-approvals.json'; data=json.loads(registry.read_text());data['packages'][SLUG]={'provenance':'docs/menauhant-provenance.json','reviewed':'2026-10-25'};registry.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
selections=ROOT/'docs/social-preview-selections.json';data=json.loads(selections.read_text());hero=records[0]
data['pages'][SLUG]={'image':'/'+hero['path'],'alt':hero['alt'],'width':1152,'height':1536,'mime':'image/jpeg','sha256':hero['sha256'],'card':'summary_large_image','type':'article','kind':'original-family-photograph','provenance':['docs/menauhant-provenance.json'],'selection_reason':'The actual beach visit, using the unchanged owner-supplied photograph of James moving toward the water.'};selections.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
blog=ROOT/'blog.html';s=blog.read_text()
if '/'+SLUG not in s:
 marker='<li><article class="journal-recent-story"><a class="journal-recent-link" href="/i-love-las-vegas-without-drinking-or-gambling.html"'
 card=f'<li><article class="journal-recent-story"><a class="journal-recent-link" href="/{SLUG}" aria-labelledby="recent-story-menauhant"><figure class="journal-recent-photo"><img src="/assets/menauhant/IMG_0035.jpeg" alt="{PHOTOS["IMG_0035.jpeg"][0]}" width="1152" height="1536" loading="lazy" style="object-fit:contain"></figure><div class="journal-recent-copy"><p class="journal-recent-place">Menauhant Beach · Falmouth, Cape Cod</p><h3 id="recent-story-menauhant">{TITLE}</h3><p class="journal-recent-description">Three pairs of bare feet, an October ocean, and a father learning when to take a step back. A family photo essay with two beach films.</p><span class="journal-recent-read">Read the reflection →</span></div></a></article></li>\n\n'
 assert marker in s
 blog.write_text(s.replace(marker,card+marker,1))
print('Created Menauhant story, sharing graphics, provenance, preview selection, and journal entry.')
