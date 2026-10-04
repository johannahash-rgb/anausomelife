#!/usr/bin/env python3
"""Build the owner-approved photo essays and their journal/library entry points."""
from pathlib import Path
from html import escape
from PIL import Image
from lxml import html
import json
import re

ROOT = Path(__file__).resolve().parent.parent
ROWS = json.loads((ROOT / 'content/family-field-notes.json').read_text())
CSS = '<link rel="stylesheet" href="/assets/family-field-notes.css?v=20261004-album">'
e = escape

def paragraphs(items):
    return ''.join('<p>'+e(p)+'</p>' for p in items)

def photograph(photo, eager=False):
    path = '/assets/family-notes/' + photo['file']
    with Image.open(ROOT / path.lstrip('/')) as im:
        w, h = im.size
    return ('<figure class="fn-photo"><img src="'+path+'" alt="'+e(photo['alt'])+
            f'" width="{w}" height="{h}" loading="'+('eager' if eager else 'lazy')+
            '" decoding="async"><figcaption>'+e(photo['caption'])+'</figcaption></figure>')

blog_path = ROOT / 'blog.html'
blog = blog_path.read_text()
masthead = re.search(r'<header class="mag-masthead">.*?</header>', blog, re.S).group()
footer = re.search(r'<footer class="mag-footer">.*?</footer>', blog, re.S).group()
edition = '<div class="edition-line"><span>New England &amp; the everyday</span><span>A family-life field guide</span></div>'

for row in ROWS:
    canonical = 'https://anausomelife.com/' + row['path']
    title, desc = e(row['title']), e(row['summary'])
    head = f'''<!doctype html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | An AUsome Life</title><meta name="description" content="{desc}">
<meta name="theme-color" content="#244b3e"><link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:type" content="article"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://anausomelife.com/assets/family-notes/{row['photo']['file']}">
<meta property="og:image:alt" content="{e(row['photo']['alt'])}"><link rel="icon" href="/favicon.ico">
<link rel="stylesheet" href="/assets/site.css?v=20261004"><link rel="stylesheet" href="/assets/magazine.css?v=20261004">
<link rel="stylesheet" href="/assets/editorial.css?v=20261003-mainstreet">
<link rel="stylesheet" href="/assets/illustrated-navigation.css?v=20261004-restore1">{CSS}
<script src="/assets/global-nav.js?v=20261004-full-footer" data-aal-global-nav="true" defer></script></head>
<body class="magazine-shell fn-page"><a class="skip" href="#main">Skip to content</a>{edition}{masthead}<main id="main">
<div class="wrap fn-breadcrumb"><a href="/blog.html">The journal</a> / Family field notes</div>
<header class="wrap fn-cover"><div><p class="fn-kicker">{e(row['category'])}</p><h1>{title}</h1>
<p class="fn-dek">{e(row['dek'])}</p><p class="fn-byline">JoHannah Ash · {e(row['place'])}</p>
<nav class="fn-jump" aria-label="In this field note"><a href="#story">Read the story ↓</a><a href="#planning-guide">The practical details ↓</a></nav></div>
{photograph(row['photo'], True)}</header>'''
    glance = '<dl class="wrap fn-glance" id="at-a-glance">'+''.join('<div><dt>'+e(k)+'</dt><dd>'+e(v)+'</dd></div>' for k,v in row['glance'])+'</dl>'
    story = '<article class="fn-story" id="story" aria-label="The family field note"><div class="fn-intro">'+paragraphs(row['intro'])+'</div>'
    for i, section in enumerate(row['sections']):
        story += f'<section id="guide-section-{i+1}"><h2>'+e(section['title'])+'</h2>'+paragraphs(section['paragraphs'])+'</section>'
        if i == 0:
            gallery = row.get('gallery', [])
            if gallery:
                story += '<div class="fn-gallery'+(' fn-single' if len(gallery)==1 else '')+'">'+''.join(photograph(p) for p in gallery)+'</div>'
            else:
                story += '<aside class="fn-pullquote">'+e(row['quote'])+'</aside>'
    story += '</article>'
    plan_title = 'A little room for the everyday.' if row['path'].startswith('flowers-') else 'Make it work for your day.'
    planning = '<section class="wrap fn-planning" id="planning-guide" aria-labelledby="planning-title"><p class="fn-kicker">The useful part</p><h2 id="planning-title">'+plan_title+'</h2><div class="fn-choices" id="visual-plan">'
    planning += ''.join('<div><h3>'+e(k)+'</h3><p>'+e(v)+'</p></div>' for k,v in row['choices'])+'</div>'
    planning += '<div class="fn-practical" id="practical-details">'+''.join('<details><summary>'+e(k)+'</summary><p>'+e(v)+'</p></details>' for k,v in row['practical'])+'</div>'
    links = row.get('sources') or row.get('related_tools', [])
    label = 'For current visit details' if row.get('sources') else 'A few useful companions'
    planning += '<div class="fn-sources"><p><strong>'+label+'</strong></p><ul>'+''.join('<li><a href="'+e(url)+'">'+e(label)+'</a></li>' for label,url in links)+'</ul></div></section>'
    related = '<nav class="wrap fn-related" aria-labelledby="more-title"><p class="fn-kicker">From the family album</p><h2 id="more-title">A few more good things.</h2><ul>'
    related += ''.join('<li><a href="/'+other['path']+'">'+e(other['title'])+' →</a></li>' for other in ROWS if other!=row)
    related += '</ul><p><a href="/blog.html">Back to the journal →</a></p></nav>'
    (ROOT / row['path']).write_text(head+glance+story+planning+related+'</main>'+footer+'<script src="/assets/site.js" defer></script></body></html>\n')

# Replace only our marked module on later runs.
album = '<!-- family-album:start --><section class="wrap fn-album" id="camera-roll-notes" aria-labelledby="album-title"><p class="eyebrow">Opened from the family album</p><h2 id="album-title">Five moments worth keeping.</h2><div class="fn-album-layout">'
album += photograph(ROWS[3]['photo'])+'<ol>'
album += ''.join('<li><h3><a href="/'+r['path']+'">'+e(r['title'])+'</a></h3><p>'+e(r['summary'])+'</p></li>' for r in ROWS)
album += '</ol></div></section><!-- family-album:end -->'
if '<!-- family-album:start -->' in blog:
    blog = re.sub(r'<!-- family-album:start -->.*?<!-- family-album:end -->', album, blog, flags=re.S)
else:
    blog = blog.replace('<section class="wrap journal-features">', album+'\n<section class="wrap journal-features">', 1)
if '/assets/family-field-notes.css' not in blog:
    blog = blog.replace('</head>', CSS+'</head>')
blog_path.write_text(blog)

# The library renders real links without JavaScript; its JSON augments search.
library_path = ROOT / 'library.html'
library = library_path.read_text()
data_path = ROOT / 'data/library.json'
data = json.loads(data_path.read_text())
paths = {'/'+r['path'] for r in ROWS}
data = [r for r in data if r['url'] not in paths]
cards = ''
entries = []
for row in ROWS:
    url = '/'+row['path']
    category = 'home' if row['path'].startswith('flowers-') else 'stories'
    entries.append({'slug':Path(row['path']).stem, 'url':url, 'title':row['title'], 'summary':row['summary'], 'category':category, 'format':'Story', 'minutes':4, 'image':'/assets/family-notes/'+row['photo']['file']})
    library = re.sub(r'<article\b[^>]*data-url="'+re.escape(url)+r'"[^>]*>.*?</article>', '', library, flags=re.S)
    cards += '<article class="index-card" data-category="'+category+'" data-format="Story" data-url="'+url+'"><div><p class="entry-meta">Family field note · Story</p><h3><a href="'+url+'">'+e(row['title'])+'</a></h3><p>'+e(row['summary'])+'</p><span class="read-time">4 minute read</span></div></article>'
library, count = re.subn(r'(<div\b[^>]*class="library-results"[^>]*>)',lambda m:m.group()+cards,library,count=1)
assert count == 1, 'Library results container changed'
total = len(re.findall(r'<article\b[^>]*class="index-card"',library))
library = re.sub(r'All \d+ guides are shown',f'All {total} guides are shown',library)
library_path.write_text(library)
data_path.write_text(json.dumps(entries+data,ensure_ascii=False,indent=2)+'\n')

sitemap_path = ROOT / 'sitemap.xml'
sitemap = sitemap_path.read_text()
for row in ROWS:
    url='https://anausomelife.com/'+row['path']
    if '<loc>'+url+'</loc>' not in sitemap:
        sitemap=sitemap.replace('</urlset>','<url><loc>'+url+'</loc></url>\n</urlset>')
sitemap_path.write_text(sitemap)

# Keep unrelated search entries exactly as maintained elsewhere in the repository.
updates = {}
for path in [r['path'] for r in ROWS] + ['blog.html', 'library.html']:
    doc = html.fromstring((ROOT/path).read_text())
    main = doc.xpath('//main')[0]
    for node in main.xpath('.//script|.//style'):
        node.drop_tree()
    text = lambda value: re.sub(r'\s+', ' ', value).strip()
    category = 'home' if path.startswith('flowers-') else 'stories'
    updates['/'+path] = {'url':'/'+path, 'title':text(doc.xpath('//h1')[0].text_content()),
        'summary':doc.xpath('//meta[@name="description"]/@content')[0],
        'category':category, 'format':'Story' if path in {r['path'] for r in ROWS} else 'Page',
        'search':text(main.text_content())}

def update_rows(existing):
    return [updates.get(r['url'],r) for r in existing]

index_path = ROOT/'data/site-index.json'
existing = json.loads(index_path.read_text())
known = {r['url'] for r in existing}
existing = update_rows(existing) + [r for url,r in updates.items() if url not in known]
index_path.write_text(json.dumps(existing,ensure_ascii=False,separators=(',',':'))+'\n')
manifest_path = ROOT/'data/site-index-manifest.json'
manifest = json.loads(manifest_path.read_text())
seen = set()
for url in manifest:
    path = ROOT/url.split('?')[0].lstrip('/')
    items = json.loads(path.read_text())
    seen.update(r['url'] for r in items)
    revised = update_rows(items)
    if revised != items:
        path.write_text(json.dumps(revised,ensure_ascii=False,separators=(',',':'))+'\n')
missing = [r for url,r in updates.items() if url not in seen]
if missing:
    relative='data/site-search/family-field-notes.json'
    (ROOT/relative).write_text(json.dumps(missing,ensure_ascii=False,separators=(',',':'))+'\n')
    manifest.append('/'+relative+'?v=20261004-album')
    manifest_path.write_text(json.dumps(manifest,separators=(',',':'))+'\n')
print(f'Built {len(ROWS)} photo essays, journal module, library links, sitemap and scoped search entries.')
