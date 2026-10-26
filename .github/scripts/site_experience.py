#!/usr/bin/env python3
"""Build one static, accessible information architecture from the public edition.

Existing article bodies and URL aliases remain intact. Navigation, breadcrumbs,
the complete library and site map derive from this inventory on every release.
"""
import importlib.util
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from html import escape
from lxml import html, etree

VERSION = '20261026-wayfinding'
EXCLUDE = {'assets','content','docs','tests','tools','services','generator-api','downloads','node_modules','_site'}
SUPPORT = {'about.html','contact.html','privacy.html','disclosure.html','language.html','accessibility.html','press.html','thank-you-for-sharing-an-ausome-life.html','how-we-choose.html','reviews.html','follow.html','links.html','resources.html','site-map.html','start-here.html','library.html','index.html'}
TOOLS = {'picture-card-library.html','communication-card-generator.html','communication-notes.html','visit-story.html','family-planning-toolkit.html','aac-outing-note.html','congdons-choice-board.html','thrift-shop-choice-board.html','history-outing-picture-cards.html'}
def clean(value): return re.sub(r'\s+', ' ', value or '').strip()
def cls(doc,name): return doc.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," '+name+' ")]')
def url_for(rel): return '/' if rel=='index.html' else '/'+rel.removesuffix('index.html') if rel.endswith('/index.html') else '/'+rel
def render(doc): return html.tostring(doc,encoding='unicode',method='html',doctype='<!doctype html>')+'\n'
def art(name,size=128): return f'/assets/navigation-watercolors/{name}-{size}.webp'
def link(label,url): return '<a href="'+escape(url,quote=True)+'">'+escape(label)+'</a>'
def illustrated(label,url,image):
    return '<a class="aal-illustrated-link" href="'+escape(url,quote=True)+'"><img src="'+art(image)+'" alt="" width="48" height="48" loading="lazy" decoding="async"><span>'+escape(label)+'</span><span aria-hidden="true">↗</span></a>'

def documents(root):
    result={}
    for page in sorted(root.rglob('*.html')):
        rel=page.relative_to(root).as_posix()
        if any(p.startswith('.') or p in EXCLUDE for p in Path(rel).parts) or rel=='404.html' or rel.startswith('preview-'): continue
        doc=html.document_fromstring(page.read_text())
        if not doc.xpath('//main//h1') or doc.xpath('//meta[translate(@http-equiv,"REFSH","refsh")="refresh"]') or doc.xpath('//meta[@name="robots" and contains(@content,"noindex")]'):continue
        result[rel]=doc
    return result

def inventory(root,docs,chapters):
    editorial={r['url']:r for r in json.loads((root/'data/library.json').read_text())}
    story_links=set(docs['blog.html'].xpath('//main//a/@href')) if 'blog.html' in docs else set()
    preferred={c['url']:c['id'] for c in chapters}
    journal=json.loads((root/'data/journal-taxonomy.json').read_text()).get('entries',{}) if (root/'data/journal-taxonomy.json').exists() else {}
    result={}
    for rel,doc in docs.items():
        url=url_for(rel)
        canonical=doc.xpath('//link[@rel="canonical"]/@href')
        if canonical and urlsplit(canonical[0]).hostname in {'anausomelife.com','www.anausomelife.com'}:
            canonical_path=urlsplit(canonical[0]).path or '/'
            target=root/canonical_path.lstrip('/')
            if target.is_dir():target/='index.html'
            if target.is_file() and canonical_path!=url:continue
        old=editorial.get(url,{})
        title_node=doc.xpath('//main//h1')[0]
        for br in title_node.xpath('.//br'):br.tail=' '+(br.tail or '').lstrip()
        title=clean(title_node.text_content())
        summary=next(iter(doc.xpath('//meta[@name="description"]/@content')),'')
        category=old.get('category','')
        if rel in SUPPORT or rel.startswith('media/'):section='about'
        elif url in preferred:section=preferred[url]
        elif rel in TOOLS:section='tools'
        elif set(journal.get(url,{}).get('formats',[])) & {'journal-posts','photo-essays','reflections'}:section='journal'
        elif category=='stories' or old.get('format')=='Story' or rel in {'family-notebook.html','kid-fun.html','little-adventures.html','series.html'}:section='journal'
        elif category in {'home','style','beauty','brands'} or re.search(r'home|household|wardrobe|gift|product|little-fixes|little-things|black-book|things-weve',rel):section='home'
        elif category in {'family','advocacy','advice'} or re.search(r'communication|caregiver|family-|role|profound|aac-|parking|quiet-break|energy-is',rel):section='support'
        else:section='places'
        category=category or {'journal':'stories','places':'outings','tools':'family','home':'home','support':'family','about':'about'}[section]
        kind=old.get('format') or ('Tool' if rel in TOOLS else 'Story' if section=='journal' else 'Place' if rel.startswith('favorite-places/') or rel.startswith('favorite-places-') else 'Guide')
        if rel.startswith('topics/') or rel in {'blog.html','library.html','start-here.html','site-map.html','favorite-places.html','calendar.html','product-guides.html','little-black-book.html','series.html'}:kind='Directory'
        if rel in SUPPORT or rel.startswith('media/'):kind='Page'
        result[url]={'url':url,'path':rel,'title':title,'summary':summary,'section':section,'category':category,'format':kind,'image':old.get('image',''),'minutes':old.get('minutes',0)}
    return sorted(result.values(),key=lambda r:(list(editorial).index(r['url']) if r['url'] in editorial else 10000,r['title'].casefold()))

def masthead(chapters,active,current):
    primary=''.join('<a href="'+c['url']+'"'+(' aria-current="page"' if current==c['url'] else '')+(' data-current-section="true"' if active==c['id'] else '')+'><img src="'+art(c['art'])+'" alt="" width="44" height="44"><span>'+escape(c['label'])+'</span></a>' for c in chapters)
    menu=''.join('<details class="aal-menu-chapter" name="site-chapters"><summary><img src="'+art(c['art'])+'" alt="" width="76" height="76"><span><strong>'+escape(c['label'])+'</strong><small>'+escape(c['description'])+'</small></span></summary><nav aria-label="'+escape(c['label'])+'">'+''.join(illustrated(*item) for item in c['links'])+'</nav></details>' for c in chapters)
    return '<header class="aal-site-header" data-site-header><div class="aal-brand-row"><a class="aal-wordmark" href="/"><img src="/assets/coastal-emblem.webp" alt="" width="64" height="64"><span>An AUsome Life<small>The good New England life, at our own pace.</small></span></a><div class="aal-header-actions"><a href="/calendar.html">Calendar</a><a href="/library.html#library-search" data-site-search>Search</a></div></div><div class="aal-nav-row"><nav class="aal-primary" aria-label="Main navigation">'+primary+'</nav><details class="aal-explore" data-site-menu><summary><img src="'+art('menu-v2')+'" width="40" height="40" alt=""><span>Explore all</span></summary><div class="aal-menu-panel"><div class="aal-menu-welcome"><p class="eyebrow">Make yourself at home</p><p>What would make today a little better?</p><nav aria-label="Start exploring">'+illustrated('First visit? Start here','/start-here.html','menu-v2')+illustrated('Every page, A–Z','/site-map.html','directory-v2')+'</nav></div><div class="aal-menu-chapters">'+menu+'</div><nav class="aal-menu-bottom" aria-label="More about An AUsome Life">'+illustrated('Our story','/about.html','family-film')+illustrated('Contact','/contact.html','journal-v2')+illustrated('Accessibility','/accessibility.html','care-clipboard')+'</nav></div></details></div></header>'

def footer(chapters):
    groups=[('Explore',[(c['label'],c['url']) for c in chapters]),('Make a plan',[('Calendar & events','/calendar.html'),('Visual visit planner','/visit-story.html'),('Make a picture card','/communication-card-generator.html'),('Caregiver glossary','/caregiver-glossary.html')]),('Stay a little longer',[('Every guide & story','/library.html'),('Complete site map','/site-map.html'),('Our story','/about.html'),('Contact','/contact.html')]),('Press & partnerships',[('Press & community','/press.html'),('Brands & destinations','/media/'),('For journalists','/media/#press-desk'),('Sharing & content use','/media/#sharing')])]
    return '<footer class="aal-site-footer mag-footer" data-site-footer><div class="wrap"><div class="aal-footer-intro"><a class="footer-wordmark" href="/">An AUsome Life</a><p>Simple good things.<br>The practical details left in.</p></div><div class="aal-footer-groups">'+''.join('<nav aria-label="'+escape(title)+'"><h2>'+escape(title)+'</h2>'+''.join(link(*i) for i in links)+'</nav>' for title,links in groups)+'</div><div class="footer-small">'+''.join(link(*i) for i in [('Language & representation','/language.html'),('Disclosure','/disclosure.html'),('Privacy','/privacy.html'),('Accessibility','/accessibility.html'),('Instagram','https://www.instagram.com/anausomelife/')])+'<span>© 2026 An AUsome Life · New England</span></div></div></footer>'

def start_content(chapters):
    cards=''.join('<section class="aal-entrance"><img src="'+art(c['art'],320)+'" alt="" width="160" height="160" loading="lazy"><div><p class="eyebrow">'+escape(c['label'])+'</p><h2>'+escape(c['title'])+'</h2><p>'+escape(c['description'])+'</p><a class="aal-entrance-cta" href="'+c['url']+'">Explore '+escape(c['label'].lower())+' <span aria-hidden="true">↗</span></a><details><summary>More in this chapter</summary><nav aria-label="More in '+escape(c['label'])+'">'+''.join(illustrated(*i) for i in c['links'][1:])+'</nav></details></div></section>' for c in chapters)
    return '<section class="aal-welcome wrap"><div><p class="eyebrow">Welcome to An AUsome Life</p><h1>One good thing.<br>Then see where it takes you.</h1><p class="aal-welcome-dek">A place to go. A story to linger over. A little help with the plan.</p><p>Choose what you came for. The practical details will be close by.</p><a class="aal-entrance-cta" href="#choose-a-chapter">Find your starting point ↓</a></div><figure><img src="/assets/editorial/autumn-table.webp" alt="Apples, a navy sweater and a notebook beside a green New England window." width="1536" height="1024" fetchpriority="high"><figcaption>Original editorial illustration</figcaption></figure></section><div class="aal-chapter-entrances wrap" id="choose-a-chapter">'+cards+'</div><section class="aal-day-plan wrap" aria-labelledby="one-good-day"><p class="eyebrow">Putting it together</p><h2 id="one-good-day">A day out, in three small steps.</h2><ol><li>'+link('Find one place you would enjoy','/favorite-places.html')+'<p>A favorite stop, a little fresh air, or a reason to take the long way.</p></li><li>'+link('Picture the visit','/visit-story.html')+'<p>Put the arrival, the good part, and the way home into a short plan.</p></li><li>'+link('Make room for a choice','/picture-card-library.html')+'<p>Bring pictures for what to do, something to eat, or time for a break.</p></li></ol></section><section class="aal-directory-invitation wrap"><h2>Looking for something specific?</h2><p>'+link('Search every guide and story','/library.html#library-search')+' or '+link('browse the complete site map','/site-map.html')+'.</p></section>'

def build_map(root,docs,rows,chapters):
    template=docs['start-here.html']
    doc=html.document_fromstring(render(template));main=doc.xpath('//main')[0];main.clear();main.set('id','main')
    labels=[(c['id'],c['label']) for c in chapters]+[('about','About & useful information')]
    intro='<div class="aal-map wrap"><p class="eyebrow">Every chapter, every page</p><h1>The whole field guide.</h1><p>Browse by chapter or '+link('search in your own words','/library.html#library-search')+'. Existing bookmarks still bring you to the same places.</p><nav class="aal-map-jumps" aria-label="Site map chapters">'+''.join(link(label,'#map-'+key) for key,label in labels)+'</nav>'
    for key,label in labels:
        entries=sorted((r for r in rows if r['section']==key),key=lambda r:r['title'].casefold())
        intro+='<section id="map-'+key+'"><h2>'+escape(label)+'</h2><ul>'+''.join('<li>'+link(r['title'],r['url'])+'<span>'+r['format']+'</span></li>' for r in entries)+'</ul></section>'
    intro+='</div>'
    for node in html.fragments_fromstring(intro):main.append(node)
    doc.xpath('//title')[0].text='Complete site map | An AUsome Life'
    for selector,value,attribute in [('//link[@rel="canonical"]','https://anausomelife.com/site-map.html','href'),('//meta[@name="description"]','Every An AUsome Life story, guide, place and practical tool, organized by chapter.','content')]:
        for node in doc.xpath(selector):node.set(attribute,value)
    for node in doc.xpath('//meta[starts-with(@property,"og:") or starts-with(@name,"twitter:")]'):node.getparent().remove(node)
    for key,value in {'og:title':'Complete site map | An AUsome Life','og:description':'Every story, place, guide and practical tool, organized by chapter.','og:url':'https://anausomelife.com/site-map.html','og:type':'website','og:image':'https://anausomelife.com/assets/editorial/autumn-table.webp','og:image:alt':'Original New England still-life editorial illustration.'}.items():
        etree.SubElement(doc.xpath('//head')[0],'meta',property=key,content=value)
    for key,value in {'twitter:card':'summary_large_image','twitter:title':'Complete site map | An AUsome Life','twitter:description':'Every story, place, guide and practical tool, organized by chapter.','twitter:image':'https://anausomelife.com/assets/editorial/autumn-table.webp','twitter:image:alt':'Original New England still-life editorial illustration.'}.items():
        etree.SubElement(doc.xpath('//head')[0],'meta',name=key,content=value)
    root.joinpath('site-map.html').write_text(render(doc))
    docs['site-map.html']=doc

def build_library(doc,rows):
    box=doc.get_element_by_id('library-results');box.clear();box.set('class','library-results');box.set('id','library-results');box.set('tabindex','-1')
    for row in rows:
        article=etree.SubElement(box,'article',{'class':'index-card','data-url':row['url'],'data-category':row['category'],'data-format':row['format'],'data-section':row['section']})
        if row['image']:
            fig=etree.SubElement(article,'figure',{'class':'library-entry-art'})
            etree.SubElement(fig,'img',src=row['image'],alt='',width='320',height='240',loading='lazy',decoding='async')
        body=etree.SubElement(article,'div');etree.SubElement(body,'p',{'class':'entry-meta'}).text=row['format']
        heading=etree.SubElement(body,'h3');etree.SubElement(heading,'a',href=row['url']).text=row['title']
        etree.SubElement(body,'p').text=row['summary']
    for node in doc.xpath('//*[@data-result-status]'):node.text=f'{len(rows)} pages to explore'
    for node in doc.xpath('//*[@data-library]//noscript'):node.clear();etree.SubElement(node,'p').text=f'All {len(rows)} pages are linked here. Search and filters use JavaScript; every page link works without it.'
    for select in doc.xpath('//select[@name="type"]'):
        select.clear();select.set('name','type');etree.SubElement(select,'option',value='').text='Every format'
        for kind in sorted(set(r['format'] for r in rows)):etree.SubElement(select,'option').text=kind
    for select in doc.xpath('//select[@name="topic"]'):
        if not select.xpath('./option[@value="about"]'):etree.SubElement(select,'option',value='about').text='About & useful information'

def apply_shell(doc,rel,row,chapters):
    head=doc.xpath('//head')[0];body=doc.xpath('//body')[0];main=doc.xpath('//main')[0]
    for node in cls(doc,'edition-line')+doc.xpath('//header[contains(@class,"masthead") or @data-site-header]')+doc.xpath('//nav[@class="aal-wayfinder"]'):
        node.getparent().remove(node)
    anchor=main
    while anchor.getparent() is not body:anchor=anchor.getparent()
    body.insert(list(body).index(anchor),html.fragment_fromstring(masthead(chapters,row['section'],row['url'])))
    for node in doc.xpath('//footer[contains(@class,"mag-footer") or @data-site-footer]'):node.getparent().remove(node)
    body.insert(list(body).index(anchor)+1,html.fragment_fromstring(footer(chapters)))
    if not doc.xpath('//link[contains(@href,"/assets/site-experience.css")]'):
        etree.SubElement(head,'link',rel='stylesheet',href='/assets/site-experience.css?v='+VERSION)
    if not doc.xpath('//script[contains(@src,"/assets/global-nav.js")]'):
        etree.SubElement(head,'script',src='/assets/global-nav.js?v='+VERSION,defer='',**{'data-aal-global-nav':'true'})
    # Replace only breadcrumbs, preserving all article bodies and their anchors.
    for node in list(dict.fromkeys(main.xpath('.//nav[@aria-label="Breadcrumb"]')+cls(main,'reader-breadcrumb')+cls(main,'breadcrumbs')+cls(main,'article-crumb')+cls(main,'breadcrumb')+cls(main,'aal-breadcrumb'))):
        if node.getparent() is not None:node.getparent().remove(node)
    if rel!='index.html':
        parent=next((c for c in chapters if c['id']==row['section']),{'label':'The library','url':'/library.html'})
        crumb='<nav class="reader-breadcrumb aal-route wrap" aria-label="Breadcrumb">'+link('Home','/')
        if parent['url']!=row['url']:crumb+='<span aria-hidden="true">/</span>'+link(parent['label'],parent['url'])
        crumb+='</nav>'
        main.insert(0,html.fragment_fromstring(crumb))
    # Do not add a second set of local controls to tools, catalogues, or policies.
    for node in cls(main,'aal-on-this-page'):node.getparent().remove(node)
    has_contents=doc.xpath('//*[contains(@class,"toc") or @aria-label="On this page" or @aria-label="On this page navigation"]')
    if row['format'] in {'Story','Place','Guide'} and rel not in TOOLS and not has_contents:
        sections=[];used=set(doc.xpath('//*[@id]/@id'))
        for h in main.xpath('.//h2'):
            if any(set((a.get('class') or '').split()) & {'reader-next','aal-story-share','aal-more','er-related','fn-related'} for a in h.iterancestors()):continue
            title=clean(h.text_content())
            if not title or len(title)>90:continue
            anchor=h.get('id')
            if not anchor:
                base='section-'+re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-');anchor=base;i=2
                while anchor in used:anchor=base+'-'+str(i);i+=1
                h.set('id',anchor);used.add(anchor)
            sections.append((title,'#'+anchor))
        if 3<=len(sections)<=12:
            toc='<details class="aal-on-this-page wrap"><summary>In this '+('story' if row['format']=='Story' else 'guide')+'</summary><nav aria-label="On this page">'+''.join(link(*i) for i in sections)+'</nav></details>'
            main.insert(1,html.fragment_fromstring(toc))
    return doc

def prepare(root):
    if not (root/'data/site-structure.json').exists():return
    config=json.loads((root/'data/site-structure.json').read_text());chapters=config['chapters'];docs=documents(root)
    rows=inventory(root,docs,chapters)
    if 'start-here.html' in docs:
        main=docs['start-here.html'].xpath('//main')[0]
        old_ids=main.xpath('.//*[@id]/@id');main.clear();main.set('id','main')
        for node in html.fragments_fromstring(start_content(chapters)):main.append(node)
        for anchor in old_ids:
            if anchor not in main.xpath('.//*[@id]/@id'):main.append(etree.Element('span',id=anchor))
        build_map(root,docs,rows,chapters)
    rows=inventory(root,docs,chapters)
    spec=importlib.util.spec_from_file_location('collection_browse',Path(__file__).with_name('collection_browse.py'))
    collections=importlib.util.module_from_spec(spec);spec.loader.exec_module(collections)
    collections.prepare(root,docs,rows)
    if 'library.html' in docs:build_library(docs['library.html'],rows)
    spec=importlib.util.spec_from_file_location('page_simplicity',Path(__file__).with_name('page_simplicity.py'))
    simplicity=importlib.util.module_from_spec(spec);spec.loader.exec_module(simplicity)
    by_url={r['url']:r for r in rows}
    for rel,doc in docs.items():
        row=by_url.get(url_for(rel))
        if not row:
            canonical=doc.xpath('//link[@rel="canonical"]/@href')
            row=by_url.get(urlsplit(canonical[0]).path) if canonical else None
        if not row:continue
        apply_shell(doc,rel,row,chapters)
        simplicity.apply(doc,rel)
        footer_nav=doc.xpath('//footer//nav[@aria-label="Stay a little longer"]')[0]
        for destination,label in [('follow.html','Follow the journal'),('reviews.html','Reviews & buying notes')]:
            if (root/destination).exists():etree.SubElement(footer_nav,'a',href='/'+destination).text=label
        (root/rel).write_text(render(doc))
    # Error recovery uses the same navigation without entering the search inventory.
    recovery=root/'404.html'
    if recovery.exists():
        doc=html.document_fromstring(recovery.read_text())
        for node in doc.xpath('//meta[@name="robots"]'):node.getparent().remove(node)
        etree.SubElement(doc.xpath('//head')[0],'meta',name='robots',content='noindex')
        row={'url':'/404.html','section':'about','format':'Page','title':'Page not found'}
        apply_shell(doc,'404.html',row,chapters)
        for node in doc.xpath('//main//*[contains(concat(" ",@class," ")," lede ")]'):
            node.text='Let’s find your way back. Search every story and guide, or choose a chapter above.'
        for node in doc.xpath('//main//a[@href="/product-guides.html"]'):
            node.set('href','/library.html#library-search');node.text='Search the whole site'
        recovery.write_text(render(doc))
    (root/'data/page-directory.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
    # HTML and XML directory listings share the same canonical inventory.
    (root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>https://anausomelife.com'+escape(r['url'])+'</loc></url>\n' for r in sorted(rows,key=lambda r:r['url']))+'</urlset>\n')
    print('Site experience:',len(docs),'pages;',len(rows),'canonical destinations;',dict(Counter(r['section'] for r in rows)))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('.'))
    prepare(parser.parse_args().root.resolve())
