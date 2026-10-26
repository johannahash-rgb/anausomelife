"""Build overlapping editorial collections and caregiver routes from reviewed tags."""
import json
from html import escape as e
from pathlib import Path
from urllib.parse import urlencode
from lxml import html, etree

PINS=['/wayne-newton-flamingo-bucket-list-self-care.html','/get-in-the-photograph.html','/rangeley-grandparents-field-note.html']
def has(node,name):return name in (node.get('class') or '').split()
def read(root,name):return json.loads((root/'data'/name).read_text())
def badge(label,key,base,param='topic'):
    return '<a href="'+base+'?'+urlencode({param:key})+'#'+('browse-journal' if base=='/blog.html' else 'browse-support')+'">'+e(label)+'</a>'

def filters(identifier,config,care=False):
    choices=config['roles'] if care else config['formats'];param='role' if care else 'kind'
    title='Find support.' if care else 'Browse the journal.'
    noun='guides' if care else 'stories'
    s='<div class="aal-collection-heading"><h2 id="'+identifier+'-title">'+title+'</h2></div>'
    s+='<form class="aal-collection-filters aal-collection-simple" role="search" aria-label="'+('Search support guides' if care else 'Search the journal')+'"><div class="aal-filter-top aal-search-row"><label for="'+identifier+'-q">Search '+('support &amp; guides' if care else 'the journal')+'<input id="'+identifier+'-q" type="search" name="q" placeholder="'+('Try school or taking a break' if care else 'Search stories…')+'"></label></div>'
    s+='<details class="aal-filter-disclosure" data-collection-filters><summary>Filter '+noun+'<span data-filter-count></span></summary><div class="aal-filter-panel"><div class="aal-filter-top aal-filter-selects"><label for="'+identifier+'-kind">'+('Your role' if care else 'Kind of read')+'<select id="'+identifier+'-kind" name="'+param+'"><option value="">'+('Every role' if care else 'Every kind')+'</option>'+''.join('<option value="'+key+'">'+e(label)+'</option>' for key,label in choices.items())+'</select></label><label for="'+identifier+'-sort">Sort by<select name="sort" id="'+identifier+'-sort"><option value="featured">Editor’s picks</option><option value="az">Title A–Z</option></select></label></div>'
    s+='<fieldset><legend>'+('What would help?' if care else 'Topics')+'<span>Choose one or more. Results match all your choices.</span></legend><div class="aal-topic-options">'+''.join('<label><input type="checkbox" name="topic" value="'+key+'"><span>'+e(label)+'</span></label>' for key,label in config['topics'].items())+'</div></fieldset><div class="aal-filter-actions"><button type="submit">Show '+noun+'</button></div></div></details><div class="aal-active-filters" data-active-filters hidden><p data-active-filter-labels></p><button type="reset">Clear filters</button></div></form><p class="aal-collection-count" data-collection-status role="status" aria-live="polite"></p>'
    return s

def card(row,tags,config,docs,care=False):
    doc=docs[row['path']];base='/family-roles.html' if care else '/blog.html'
    image=row.get('image','');alt=''
    images=doc.xpath('//main//img')
    if image:
        matching=[n for n in images if n.get('src')==image];alt=matching[0].get('alt','') if matching else ''
    elif not care:
        images=[n for n in images if not any(x in (n.get('src') or '') for x in ['/navigation-watercolors/','/library-watercolors/','coastal-emblem'])]
        if images:image=images[0].get('src','');alt=images[0].get('alt','')
    s='<li data-collection-card data-topics="'+' '.join(tags['topics'])+'" data-kinds="'+' '.join(tags.get('formats',[]))+'" data-roles="'+' '.join(tags.get('roles',[]))+'" data-url="'+row['url']+'"><article class="aal-collection-card'+(' aal-support-card' if care else '')+'">'
    if image and not care:s+='<a class="aal-collection-photo" href="'+row['url']+'" tabindex="-1" aria-hidden="true"><img src="'+e(image,quote=True)+'" alt="'+e(alt,quote=True)+'" loading="lazy" decoding="async" width="640" height="480"></a>'
    search_labels=[config['topics'][k] for k in tags['topics']]+[config['formats'][k] for k in tags.get('formats',[])]+[config['roles'][k] for k in tags.get('roles',[])]
    s+='<div class="aal-collection-copy" data-search-labels="'+e(' '.join(search_labels),quote=True)+'">'
    if care:s+='<p class="aal-collection-kind">'+e(' · '.join(config['roles'][k] for k in tags.get('roles',[])) or 'For every role')+'</p>'
    s+='<h3><a href="'+row['url']+'">'+e(row['title'])+'</a></h3><p>'+e(row['summary'])+'</p></div></article></li>'
    return s

def prepare(root,docs,rows):
    if not (root/'data/journal-taxonomy.json').exists():return
    configs=[('blog.html','journal-taxonomy.json','browse-journal',False),('family-roles.html','caregiver-taxonomy.json','browse-support',True)]
    by_url={r['url']:r for r in rows}
    for page,filename,identifier,care in configs:
        if page not in docs:continue
        config=read(root,filename);entries={url:tags for url,tags in config['entries'].items() if url in by_url}
        doc=docs[page];main=doc.xpath('//main')[0]
        old_ids=[]
        for node in list(main.xpath('.//*[@data-collection]')):
            old_ids.extend(node.xpath('.//*[@id]/@id'));node.getparent().remove(node)
        if not care:
            for node in list(main):
                if any(has(node,n) for n in ['journal-recent','landing-jumps','fn-album','journal-features','journal-notebook','journal-index']):
                    old_ids.extend(node.xpath('.//*[@id]/@id'))
                    if node.get('id'):old_ids.append(node.get('id'))
                    main.remove(node)
        if not care:
            for old in main.xpath('.//nav[@data-journal-quick]'):old.getparent().remove(old)
        ordered=list(entries)
        if not care:ordered=[u for u in PINS if u in entries]+[u for u in ordered if u not in PINS]
        s='<section class="aal-collection wrap" id="'+identifier+'" data-collection="'+('support' if care else 'journal')+'" aria-labelledby="'+identifier+'-title">'+filters(identifier,config,care)
        s+='<ol class="'+('aal-support-list' if care else 'journal-recent-list')+'" data-collection-results>'+''.join(card(by_url[url],entries[url],config,docs,care) for url in ordered)+'</ol><div class="aal-collection-empty" data-collection-empty hidden><h3>No matches with those filters.</h3><p>Remove a topic or try a shorter search.</p><button type="button" data-collection-clear>Show everything</button></div><button type="button" data-collection-more hidden>Show more '+('guides' if care else 'stories')+'</button><noscript><p>All entries are shown below. Filtering uses JavaScript; every story and guide link works without it.</p></noscript></section>'
        section=html.fragment_fromstring(s)
        if care:
            anchor=doc.get_element_by_id('practical',None)
            if anchor is not None:anchor.addnext(section)
            else:main.append(section)
        else:
            intro=next((n for n in main if has(n,'landing-introduction')),None)
            if intro is not None:intro.addnext(section)
            else:main.append(section)
        current=set(doc.xpath('//*[@id]/@id'))
        for anchor in old_ids:
            if anchor not in current:section.append(etree.Element('span',id=anchor));current.add(anchor)
        for old in doc.xpath('//script[contains(@src,"/assets/collection-browse.js")] | //link[contains(@href,"/assets/collection-browse.css")]'):old.getparent().remove(old)
        etree.SubElement(doc.xpath('//body')[0],'script',src='/assets/collection-browse.js?v=20261026-calm',defer='')
        etree.SubElement(doc.xpath('//head')[0],'link',rel='stylesheet',href='/assets/collection-browse.css?v=20261026-calm')
        # Visible topic links on the articles themselves lead back to filtered collections.
        for url,tags in entries.items():
            row=by_url[url];article=docs[row['path']];article_main=article.xpath('//main')[0]
            for old in article_main.xpath('.//nav[@data-article-collection=$kind]',kind='support' if care else 'journal'):old.getparent().remove(old)
            nav='<nav class="aal-article-topics wrap" aria-label="'+('Explore related support' if care else 'Explore related journal topics')+'" data-article-collection="'+('support' if care else 'journal')+'"><span>'+('Support topics' if care else 'In the journal')+'</span>'
            if not care:nav+=''.join(badge(config['formats'][key],key,'/blog.html','kind') for key in tags['formats'])
            nav+=''.join(badge(config['topics'][key],key,'/family-roles.html' if care else '/blog.html') for key in tags['topics'])+'</nav>'
            article_main.insert(0,html.fragment_fromstring(nav))
            row.setdefault('topics',[]).extend(config['topics'][key] for key in tags['topics'] if config['topics'][key] not in row.get('topics',[]))
    print('Built journal and caregiver collections with overlapping topics')
