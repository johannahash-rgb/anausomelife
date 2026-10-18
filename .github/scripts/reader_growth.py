#!/usr/bin/env python3
"""Publish evidence summaries, a review index and a real RSS follow route.
Only finished reader content is published. No signup or measurement is invented.
"""
import argparse, html as escape_html, json, re
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from lxml import html

BASE='https://anausomelife.com'
VERSION='20261018-reader-growth-v1'
SUMMARIES={
 'eight-oclock-colombian-peaks-field-note.html': {
  'kind':'Firsthand taste note', 'anchor':'the-story',
  'evidence':['We bought it, he drank it','not a measured caffeine claim','No gift or payment was received'],
  'facts':[('What we used','Eight O’Clock Coffee 100% Colombian Peaks, in the whole-bean version.'),('What stood out','Michael kept asking for the same coffee. He describes his usual cup as smooth and full, without the bitterness he dislikes.'),('The limit','One person’s taste and everyday routine—not a blind comparison, a measured caffeine test or a documented long-term trial.')],
  'disclosure':'Bought by us. The article records no gift or payment at its original publication; the full disclosure also describes the brand inquiry.',
 },
 'little-things-that-help.html': {
  'kind':'A family experiment—not a product review', 'anchor':'the-tip',
  'evidence':['one-off experiment','not a product recommendation','Not sponsored, gifted or an affiliate link'],
  'facts':[('What we observed','A familiar drink and preferred straw were the starting point for one kitchen experiment.'),('The useful idea','Look at the small handling detail before replacing a familiar drink or routine.'),('The important limit','The photographed cap is not a recommended daily drinking setup or a cutting tutorial. The article points to a compatible purpose-made lid or lidded cup instead.')],
  'disclosure':'We purchased the milk. This independent family note is not sponsored, gifted or affiliate-linked.',
 },
 'things-weve-bought.html': {
  'kind':'Purchase records & buying questions', 'anchor':'the-story',
  'evidence':['This page does not give a hands-on verdict','October 2, 2026','two purchased-item links could not'],
  'facts':[('What the evidence shows','Purchase records for five specific kitchen, gift-drawer and storage items.'),('What it does not show','A purchase alone does not establish repeated use, durability or a recommendation. This page is not a set of hands-on reviews.'),('Before shopping','Listing checks are dated October 2, 2026; two links could not be independently reloaded then. Recheck the exact variant, seller, care instructions and return terms.')],
  'disclosure':'The product links are ordinary retailer links without affiliate tags. The original notes retain their dated listing-check status.',
 }
}

def owned(source,key,block,anchor):
 marker='<!-- aal-reader-growth:'+key+':start -->\n'+block+'\n<!-- aal-reader-growth:'+key+':end -->'
 pattern=r'<!-- aal-reader-growth:'+re.escape(key)+r':start -->.*?<!-- aal-reader-growth:'+re.escape(key)+r':end -->'
 if re.search(pattern,source,re.S):return re.sub(pattern,lambda _:marker,source,count=1,flags=re.S)
 match=re.search(anchor,source,re.S)
 if not match:raise ValueError('Missing insertion point: '+key)
 return source[:match.start()]+marker+'\n'+source[match.start():]

def summary(info):
 facts=''.join('<div><dt>'+escape_html.escape(k)+'</dt><dd>'+escape_html.escape(v)+'</dd></div>' for k,v in info['facts'])
 return '<section class="rg-summary wrap" id="review-summary" aria-labelledby="review-summary-title"><p class="rg-kicker">'+escape_html.escape(info['kind'])+'</p><h2 id="review-summary-title">The useful details, up front.</h2><dl>'+facts+'</dl><p class="rg-disclosure">'+escape_html.escape(info['disclosure'])+'</p><p class="rg-links"><a href="#'+info['anchor']+'">Read the full note</a><a href="/reviews.html">All reviews &amp; buying notes</a><a href="/disclosure.html">Disclosure standard</a></p></section>'

REVIEWS='''<section class="rg-hero wrap"><p class="rg-kicker">The useful everyday</p><h1>Reviews &amp; buying notes.</h1><p class="rg-deck">What we reach for again. What we are still figuring out. And the questions worth asking before something earns a place at home.</p><p>Firsthand experience, purchase records and researched guides are labeled separately. A beautiful photograph is not a test result, and a purchased item is not automatically a recommendation.</p><nav class="rg-links" aria-label="Review topics"><a href="#firsthand">From our own day</a><a href="#purchased">Purchased-item notes</a><a href="#choosing">Before you buy</a></nav></section>
<section class="wrap rg-section" id="firsthand" aria-labelledby="firsthand-title"><h2 id="firsthand-title">From our own day.</h2><div class="rg-grid">
<article class="rg-card"><figure><img src="/assets/ellis-misc/coffee-before-keys-v1.webp" alt="Decorative coffee, linen and keys still life; not an exact product photograph." loading="lazy" width="1536" height="1024"><figcaption>Original editorial illustration.</figcaption></figure><div><p class="rg-kicker">Firsthand taste note · Bought by us</p><h3>The coffee we bought again.</h3><p>Michael’s experience with Eight O’Clock Colombian Peaks: why he keeps choosing it, the morning routine and the limits of one person’s taste notes.</p><a href="/eight-oclock-colombian-peaks-field-note.html#review-summary" data-aal-goal="review_coffee">Read the coffee note</a></div></article>
<article class="rg-card"><figure><img src="/assets/family-notes/straw-lid-clear.webp" alt="Our photographed strawberry-milk and straw experiment; not a recommended daily lid setup." loading="lazy" width="1048" height="1400"><figcaption>Original family photograph. The article explains the experiment’s limits.</figcaption></figure><div><p class="rg-kicker">Family experiment · Not a product review</p><h3>The little detail at the kitchen counter.</h3><p>A familiar drink, a preferred straw and a reminder to look at the fiddly part first. This is not a tutorial for cutting drink lids.</p><a href="/little-things-that-help.html#review-summary" data-aal-goal="review_kitchen">Read the kitchen note</a></div></article></div></section>
<section class="wrap rg-section" id="purchased" aria-labelledby="purchased-title"><p class="rg-kicker">Records, not verdicts</p><h2 id="purchased-title">Things we have bought.</h2><p>Five specific kitchen, gift-drawer and storage purchases, with practical buying questions and no-buy alternatives. These records do not establish a hands-on review or long-term durability.</p><p class="rg-links"><a href="/things-weve-bought.html#review-summary" data-aal-goal="review_records">Read the purchased-item notes</a></p></section>
<section class="wrap rg-section" id="choosing" aria-labelledby="choosing-title"><p class="rg-kicker">Before anything goes in the cart</p><h2 id="choosing-title">Count the whole job.</h2><p>The useful questions go beyond looks: fit, setup, grip, cleaning, storage, refills, full cost and the way back if it does not suit.</p><p class="rg-links"><a href="/how-we-choose.html">How we choose</a><a href="/product-guides.html">Browse the buying guides</a><a href="/a-love-letter-to-buying-nothing.html">Start with buying nothing</a></p><p>For product and PR teams: <a href="/media/#products">propose a sample or loan</a>. The terms, testing window and any separate rights are agreed before anything ships.</p></section>'''
FOLLOW='''<section class="rg-hero wrap"><p class="rg-kicker">A little more An AUsome Life</p><h1>Keep the good things close.</h1><p class="rg-deck">Family stories, useful finds and New England days out, with the practical details left in.</p></section>
<section class="wrap rg-section" aria-labelledby="follow-rss-title"><p class="rg-kicker">For your reading list</p><h2 id="follow-rss-title">Follow the journal with RSS.</h2><p>Add our feed to the feed reader you already use. It brings together the journal’s recent-story selection and links to the full articles. You do not need to give this website an email address or create an account.</p><label for="journal-feed-address">Journal feed address</label><input id="journal-feed-address" type="url" value="https://anausomelife.com/feed.xml" readonly><p class="rg-links"><button type="button" id="copy-journal-feed" hidden>Copy feed address</button><a href="/feed.xml" data-aal-goal="rss_open">Open the RSS feed</a><a href="/blog.html">Read the journal here</a></p><p id="feed-copy-status" role="status" aria-live="polite"></p><p class="rg-small">Opening the feed may show XML text. That is normal: copy its address into your reader’s “Add feed” or “Follow website” field. Your chosen reader has its own privacy practices.</p></section>
<section class="wrap rg-section" aria-labelledby="follow-social-title"><p class="rg-kicker">From the camera roll</p><h2 id="follow-social-title">Find us on Instagram.</h2><p>Follow <strong>@anausomelife</strong> for the publication’s social posts, or stay here and explore the stories at your own pace.</p><p class="rg-links"><a href="https://www.instagram.com/anausomelife/" data-aal-goal="follow_instagram">Visit An AUsome Life on Instagram</a><a href="/reviews.html">Explore reviews &amp; buying notes</a></p></section>'''
INVITATION='<section class="wrap rg-invitation" id="follow-the-journal" aria-labelledby="follow-journal-title"><p class="rg-kicker">Keep reading</p><h2 id="follow-journal-title">Good things for your reading list.</h2><p>Follow the journal with RSS or find An AUsome Life on Instagram. No email signup is needed to read the stories.</p><p class="rg-links"><a href="/follow.html">Ways to follow</a><a href="/reviews.html">Reviews &amp; buying notes</a></p></section>'
PRIVACY='<section class="rg-section" id="site-measurement" aria-labelledby="measurement-title"><h2 id="measurement-title">Optional site measurement</h2><p id="measurement-state">Website analytics is not currently enabled. No analytics service is loaded by this site.</p><div id="measurement-controls" hidden><p>Optional measurement helps us understand visits and a small set of actions, such as opening a review or the RSS feed. It does not include text entered into tools or inquiries. Advertising features stay off.</p><p class="rg-links"><button type="button" id="measurement-allow">Allow optional measurement</button><button type="button" id="measurement-deny">Keep measurement off</button></p><p class="rg-small">The configured service is Google Analytics. Allowing measurement loads its script and may set analytics cookies; its requests include connection information such as your IP address. Our event fields omit query strings, form text and referring URLs. Your choice is remembered in this browser for up to six months when storage is available. You can change it here. Do Not Track and Global Privacy Control take precedence.</p></div><p id="measurement-choice-status" role="status" aria-live="polite"></p></section>'


def public_page(root,path,title,description,body):
 template=(root/'contact.html').read_text(encoding='utf-8')
 header=re.search(r'<header\b.*?</header>',template,re.S)
 footer=re.search(r'<footer\b.*?</footer>',template,re.S)
 if not header or not footer:raise ValueError('Missing shared page shell')
 e=escape_html.escape
 return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+e(title)+' | An AUsome Life</title><meta name="description" content="'+e(description,quote=True)+'"><link rel="canonical" href="'+BASE+'/'+path+'"><meta property="og:title" content="'+e(title,quote=True)+'"><meta property="og:description" content="'+e(description,quote=True)+'"><meta property="og:type" content="website"><meta property="og:url" content="'+BASE+'/'+path+'"><meta property="og:image" content="'+BASE+'/assets/catalog-hero.webp"><meta property="og:image:alt" content="Original editorial still-life illustration."><meta property="og:site_name" content="An AUsome Life"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="'+BASE+'/assets/catalog-hero.webp"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/magazine.css"><link rel="stylesheet" href="/assets/illustrated-navigation.css"><link rel="stylesheet" href="/assets/editorial.css?v='+VERSION+'"><link rel="stylesheet" href="/assets/access-tools.css?v='+VERSION+'"><link rel="stylesheet" href="/assets/reader-growth.css?v='+VERSION+'"><link rel="alternate" type="application/rss+xml" title="An AUsome Life journal" href="/feed.xml"></head><body class="magazine-shell reader-growth"><a class="skip-link" href="#main">Skip to content</a>'+header[0]+'<main id="main">'+body+'</main>'+footer[0]+'<script src="/assets/global-nav.js?v='+VERSION+'" defer></script><script src="/assets/access-tools.js?v='+VERSION+'" defer></script><script src="/assets/reader-growth.js?v='+VERSION+'" defer></script></body></html>\n'


def build_feed(root):
 doc=html.fromstring((root/'blog.html').read_text())
 cards=doc.xpath('//ol[contains(concat(" ",normalize-space(@class)," ")," journal-recent-list ")]/li')
 if not cards:raise ValueError('Journal feed requires the actual recent-story list')
 ET.register_namespace('atom','http://www.w3.org/2005/Atom')
 rss=ET.Element('rss',version='2.0');channel=ET.SubElement(rss,'channel')
 for key,value in [('title','An AUsome Life — Journal'),('link',BASE+'/blog.html'),('description','Stories from the journal’s recent-story selection. Read each complete story on An AUsome Life.'),('language','en-us')]:ET.SubElement(channel,key).text=value
 ET.SubElement(channel,'{http://www.w3.org/2005/Atom}link',href=BASE+'/feed.xml',rel='self',type='application/rss+xml')
 seen=set()
 for card in cards:
  href=next(iter(card.xpath('.//a/@href')),'');parts=urlsplit(href)
  if parts.scheme or parts.netloc or not parts.path.startswith('/') or '..' in Path(parts.path).parts:raise ValueError('Unexpected journal destination')
  path=root/parts.path.lstrip('/')
  if path.is_dir():path/='index.html'
  d=html.fromstring(path.read_text()); canonical=d.xpath('//link[@rel="canonical"]/@href')
  if not canonical or not canonical[0].startswith(BASE+'/'):raise ValueError('Missing journal canonical')
  if d.xpath('//meta[contains(@content,"noindex")]') or d.xpath('//meta[translate(@http-equiv,"REFSH","refsh")="refresh"]'):continue
  url=canonical[0]
  if url in seen:continue
  seen.add(url)
  headings=d.xpath('//h1');description=d.xpath('//meta[@name="description"]/@content')
  if len(headings)!=1 or not description:raise ValueError('Missing journal headline or summary')
  item=ET.SubElement(channel,'item')
  ET.SubElement(item,'title').text=' '.join(headings[0].text_content().split())
  ET.SubElement(item,'link').text=url
  ET.SubElement(item,'guid',isPermaLink='true').text=url
  ET.SubElement(item,'description').text=description[0]
 # Publication timestamps are optional in RSS. Do not manufacture dates or rewrite
 # every story as newly published just because the site rebuilt.
 ET.indent(rss,space='  ')
 (root/'feed.xml').write_bytes(ET.tostring(rss,encoding='utf-8',xml_declaration=True)+b'\n')
 return len(seen)


def prepare(root):
 root=Path(root)
 for name,info in SUMMARIES.items():
  p=root/name;s=p.read_text(encoding='utf-8')
  if not all(text in html.fromstring(s).text_content() for text in info['evidence']):raise ValueError('Recheck review evidence: '+name)
  s=owned(s,'review-summary',summary(info),r'<section\b(?=[^>]*\bid="'+info['anchor']+r'")[^>]*>')
  p.write_text(s,encoding='utf-8')
 for name,title,description,body in [
  ('reviews.html','Reviews & buying notes','Firsthand coffee notes, a kitchen experiment and verified purchases, clearly separated from buying guides. Read the evidence and limitations before shopping.',REVIEWS),
  ('follow.html','Follow the journal','Follow An AUsome Life with the journal RSS feed or on Instagram. Family stories, useful finds and New England outings without an email signup.',FOLLOW)]:
  (root/name).write_text(public_page(root,name,title,description,body),encoding='utf-8')
 for p in root.rglob('*.html'):
  rel=p.relative_to(root).as_posix()
  if any(part.startswith('.') or part in {'assets','content','downloads','docs','tools','tests','node_modules'} for part in p.relative_to(root).parts):continue
  s=p.read_text(encoding='utf-8')
  if '<main' not in s or '</head>' not in s or rel=='404.html' or rel.startswith('preview-'):continue
  if any('noindex' in v.lower() for v in html.fromstring(s).xpath('//meta[@name="robots"]/@content')):continue
  if rel=='blog.html':s=owned(s,'journal-follow',INVITATION,r'</main>')
  if rel in {'product-guides.html','media/index.html'}:
   s=owned(s,'review-index-link','<aside class="wrap rg-index-link"><p><strong>Start with the evidence.</strong> <a href="/reviews.html">Explore reviews &amp; buying notes</a>—firsthand experience, purchase records and researched guides, clearly labeled.</p></aside>',r'</main>')
  if rel=='privacy.html':s=owned(s,'measurement',PRIVACY,r'</main>')
  if 'rg-' in s and '/assets/reader-growth.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/assets/reader-growth.css?v='+VERSION+'"></head>',1)
  if not re.search(r'<link\b[^>]*type="application/rss\+xml"',s):s=s.replace('</head>','<link rel="alternate" type="application/rss+xml" title="An AUsome Life journal" href="/feed.xml"></head>',1)
  def footer(match):
   f=match[0]
   for url,label in [('/reviews.html','Reviews &amp; buying notes'),('/follow.html','Follow the journal')]:
    if 'href="'+url+'"' not in f:f=f.replace('</nav>','<a href="'+url+'">'+label+'</a></nav>',1)
   return f
  s=re.sub(r'<footer\b.*?</footer>',footer,s,flags=re.S)
  p.write_text(s,encoding='utf-8')
 nav=root/'assets/global-nav.js'
 if nav.exists():
  s=nav.read_text();s=re.sub(r'/assets/analytics\.js\?[^\'"\s<]+','/assets/analytics.js?v='+VERSION,s);nav.write_text(s)
 count=build_feed(root)
 sitemap=root/'sitemap.xml'
 tree=ET.parse(sitemap);ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
 for path in ['reviews.html','follow.html']:
  url=BASE+'/'+path
  if not any(e.text==url for e in tree.findall('.//'+ns+'loc')):ET.SubElement(ET.SubElement(tree.getroot(),ns+'url'),ns+'loc').text=url
 ET.register_namespace('',ns[1:-1]);tree.write(sitemap,encoding='utf-8',xml_declaration=True)
 print('Published 3 evidence summaries, 2 reader pages and',count,'journal RSS entries')


def check(root):
 root=Path(root)
 for name in ['reviews.html','follow.html',*SUMMARIES]:
  d=html.fromstring((root/name).read_text())
  ids=d.xpath('//*[@id]/@id')
  assert len(ids)==len(set(ids)),name+' duplicate IDs'
  assert len(d.xpath('//h1'))==1,name+' headings'
  sections=d.xpath('//main') if name in {'reviews.html','follow.html'} else d.xpath('//*[@id="review-summary"]')
  assert sections,name+' summary'
  for href in sections[0].xpath('.//a/@href'):
   u=urlsplit(href)
   if u.scheme or u.netloc:continue
   p=root/u.path.lstrip('/') if u.path else root/name
   if p.is_dir():p/='index.html'
   assert p.is_file(),href
   if u.fragment and p.suffix=='.html':assert html.fromstring(p.read_text()).xpath('//*[@id=$id]',id=u.fragment),href
  if name in {'reviews.html','follow.html'}:
   assert not d.xpath('//header//a[contains(@href,"/media/")]')
   for src in d.xpath('//img/@src'):assert (root/src.lstrip('/')).is_file(),src
 feed=ET.parse(root/'feed.xml');items=feed.findall('./channel/item')
 assert items and len({i.findtext('guid') for i in items})==len(items)
 for item in items:assert item.findtext('link')==item.findtext('guid')
 print('Reader publication checks passed:',len(items),'RSS entries; review summaries, routes and assets verified')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--check',action='store_true');args=parser.parse_args();check(args.root) if args.check else prepare(args.root)
