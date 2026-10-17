"""Publish contextual, static reading paths without requiring menus or JavaScript."""
import argparse
import json
import re
from pathlib import Path
from lxml import html, etree

REPO = Path(__file__).resolve().parents[2]
VERSION = '20261016-fuller-design'
ART = '/assets/navigation-watercolors/'

def card(url, title, description, kind, image):
    return dict(url=url, title=title, description=description, kind=kind, image=image)

CARDS = {
    'care': card('/family-roles.html', 'Family & caregiver support', 'Find practical help, time for yourself, and ideas to enjoy together.', 'Start here', ART+'yankee-toolbox-320.webp'),
    'handover': card('/caregiver-handover-guide.html', 'Make a clear caregiver handover', 'What the next supporter needs to know, and who is taking responsibility.', 'Practical guide', ART+'care-clipboard-320.webp'),
    'plans': card('/family-planning-toolkit.html', 'Make a small plan for the day', 'Fill in, copy or print a leaving-the-house card, day plan or household handoff.', 'Fill-in tool', ART+'family-organizer-320.webp'),
    'wayne': card('/wayne-newton-flamingo-bucket-list-self-care.html', 'A night for me: meeting Wayne Newton', 'A bucket-list wish and a little room for your own good things.', 'Family story', '/assets/wayne-newton-flamingo-2026/wayne-newton-stage-duet.jpg'),
    'photo': card('/get-in-the-photograph.html', 'Get in the photograph.', 'A note on motherhood, family memories, and being in the picture.', 'Family story', '/assets/get-in-the-photograph/mother-and-son-waterfront.jpeg'),
    'rangeley': card('/rangeley-grandparents-field-note.html', 'A little lake time in Rangeley', 'Grandparents, autumn water, and room to slow down together.', 'Family story', '/assets/rangeley-grandparents/lakeside-pause.jpeg'),
    'gardner': card('/isabella-stewart-gardner-museum-date.html', 'A date at the Gardner', 'Time for two, one lovely stop, and the practical museum details.', 'Family story', '/assets/gardner-museum-date/together-at-the-gardner.jpeg'),
    'dairy': card('/october-ice-cream-dairy-joy-weston.html', 'October ice cream at Dairy Joy', 'A red picnic table, family company, and an ordinary afternoon worth keeping.', 'Family story', '/assets/dairy-joy-october/grandpa-steve-james-ruby.jpeg'),
    'little-fixes': card('/the-little-fixes.html', 'The little fixes that help', 'A familiar drink, a useful straw, and the details that make a difference.', 'From our own day', '/assets/family-notes/straw-lid-clear.webp'),
    'places': card('/favorite-places.html', 'Find a place to go', 'Browse familiar stops, access notes and New England outing ideas.', 'Places to explore', ART+'outings-320.webp'),
    'visit': card('/visit-story.html', 'Make a visual visit plan', 'Put the next outing into pictures and words you can edit.', 'Planning tool', ART+'care-clipboard-320.webp'),
    'shorter': card('/shorter-visit-plan.html', 'Plan the shorter version', 'Choose one good part, a pause and a comfortable way to finish.', 'Practical guide', ART+'outings-320.webp'),
    'parking': card('/disabled-parking-placards-new-england.html', 'Disabled parking & placards', 'Find the New England application links and passenger-use guidance.', 'Practical guide', ART+'parking-volvo-128.webp'),
    'cards': card('/communication-card-generator.html', 'Make a picture card', 'Choose a clear image and a useful word, then print or save your card.', 'Communication tool', ART+'picture-cards-320.webp'),
    'communication': card('/multimodal-communication.html', 'Support different ways to communicate', 'Keep familiar communication, real choices and time to answer close by.', 'Practical guide', ART+'picture-cards-320.webp'),
    'journal': card('/blog.html', 'Read the journal', 'Real family days, favorite places, and small things worth noticing.', 'More stories', ART+'family-organizer-320.webp'),
    'home': card('/at-home.html', 'Make home work a little better', 'Start with a recurring difficulty and one useful change.', 'At home', ART+'home-320.webp'),
    'reset': card('/household-reset.html', 'A reset for the time you have', 'Choose a five-, fifteen- or thirty-minute version.', 'Practical guide', ART+'household-brush-320.webp'),
    'products': card('/product-guides.html', 'Explore useful finds', 'Read the practical details before choosing something for family life.', 'Product guides', ART+'yankee-toolbox-320.webp'),
    'school': card('/topics/advocacy.html', 'School & advocacy', 'Find meeting preparation, clear requests and useful record keeping.', 'Browse the guides', ART+'care-clipboard-320.webp'),
    'agenda': card('/guides/one-page-parent-agenda.html', 'Prepare a one-page parent agenda', 'Give your priorities, questions and next steps a clear place.', 'Practical guide', ART+'family-organizer-320.webp'),
    'media': card('/media/', 'Work with An AUsome Life', 'Published examples, collaboration ideas and content-use requests.', 'For brands', ART+'family-organizer-320.webp'),
    'press': card('/press.html', 'Press & community mentions', 'See where our stories and planning tools have been shared.', 'In the community', ART+'family-organizer-320.webp'),
}
GROUPS = {
    'care': ('Family & caregiver support', '/family-roles.html', ['photo','handover','care','plans','wayne']),
    'communication': ('Communication & picture cards', '/multimodal-communication.html', ['little-fixes','cards','care','visit','communication']),
    'outings': ('Places & days out', '/favorite-places.html', ['dairy','visit','places','shorter','parking']),
    'home': ('Home & useful finds', '/at-home.html', ['little-fixes','reset','products','plans','home']),
    'school': ('School & advocacy', '/topics/advocacy.html', ['agenda','school','care','handover']),
    'stories': ('The journal', '/blog.html', ['rangeley','care','journal','dairy','photo']),
    'media': ('Press & partnerships', '/media/', ['press','media','journal','gardner']),
    'general': ('The library', '/library.html', ['photo','care','places','journal']),
}
OVERRIDES = {
    'maternal-role.html': ['photo','handover','care'],
    'grandparent-role.html': ['rangeley','handover','care'],
    'paternal-role.html': ['dairy','plans','care'],
    'coparent-role.html': ['gardner','plans','care'],
    'respite-partner-role.html': ['wayne','handover','care'],
    'caregiver-handover-guide.html': ['gardner','plans','care'],
    'family-planning-toolkit.html': ['dairy','handover','care'],
    'family-roles.html': ['gardner','parking','journal'],
    'wayne-newton-flamingo-bucket-list-self-care.html': ['gardner','handover','care'],
    'isabella-stewart-gardner-museum-date.html': ['wayne','handover','care'],
    'get-in-the-photograph.html': ['rangeley','plans','care'],
    'rangeley-grandparents-field-note.html': ['photo','shorter','care'],
    'disabled-parking-placards-new-england.html': ['dairy','shorter','care'],
    'blog.html': ['care','places','products'],
    'family-notebook.html': ['photo','visit','journal'],
    'the-little-fixes.html': ['dairy','cards','products'],
    'topics/family.html': ['care','photo','plans'],
}
CARE = set(OVERRIDES) - {'blog.html','family-notebook.html','the-little-fixes.html','disabled-parking-placards-new-england.html'}
POLICIES = {'privacy.html','disclosure.html','accessibility.html','language.html'}
RELATED = {'aal-more','er-related','fn-related','related','related-guides','related-links'}
REPLACE_RELATED = {'family-roles.html','family-planning-toolkit.html','caregiver-handover-guide.html'}

def group_for(relative, categories):
    if relative in CARE or relative.endswith('-role.html') or relative in {'family-agreements.html','profoundly-awesome.html','older-teen-edit.html','quiet-break-plan.html'}:
        return 'care'
    if re.search(r'communication|aac-|picture-card|visit-story', relative): return 'communication'
    if relative.startswith('media/') or relative in {'media.html','media-kit.html','press.html','thank-you-for-sharing-an-ausome-life.html'}: return 'media'
    if relative in {'blog.html','family-notebook.html','kid-fun.html','little-adventures.html'}: return 'stories'
    if relative in {'favorite-places.html','calendar.html','field-notes.html','new-england-weekends.html','shorter-visit-plan.html','accessible-new-england-trails.html','disabled-parking-placards-new-england.html'} or relative.startswith('favorite-places'): return 'outings'
    category=categories.get('/'+relative,'')
    return {'family':'care','outings':'outings','home':'home','style':'home','beauty':'home','brands':'home','advocacy':'school','stories':'stories','holidays':'outings'}.get(category,'general')

def page_url(relative):
    return '/'+relative.removesuffix('index.html') if relative.endswith('/index.html') else '/'+relative

def selected_cards(relative, group):
    result=[]
    for key in OVERRIDES.get(relative,[]) + GROUPS[group][2] + ['journal','care','places']:
        entry=CARDS[key]
        if entry['url']==page_url(relative) or entry['url'] in [c['url'] for c in result]: continue
        result.append(entry)
        if len(result)==3: break
    return result

def has_class(node, names):
    return bool(set((node.get('class') or '').split()) & set(names))

def remove_preserving_anchors(node):
    """Keep existing fragment destinations when replacing a navigation block."""
    parent=node.getparent()
    if parent is None:return
    for target in node.xpath('.//*[@id]/@id')+([node.get('id')] if node.get('id') else []):
        if target=='reader-next-title':continue
        marker=etree.Element('span',id=target)
        parent.insert(parent.index(node),marker)
    parent.remove(node)

def apply_to_page(source, relative, categories):
    if relative=='index.html' or relative.startswith(('assets/','content/','docs/','tests/','downloads/')): return source
    if '/assets/global-nav.js' not in source or '<main' not in source.lower(): return source
    doc=html.document_fromstring(source)
    if doc.xpath('//meta[translate(@http-equiv,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="refresh"]') or doc.xpath('//meta[@name="robots" and contains(@content,"noindex")]'): return source
    mains=doc.xpath('//main');heads=doc.xpath('//head');titles=doc.xpath('//main//h1')
    if len(mains)!=1 or not heads or not titles: return source
    main=mains[0];group=group_for(relative,categories);name,parent,unused=GROUPS[group]
    old_labels={'The family & caregiver field notes','Explore all family & caregiver field notes','Family & caregiver field notes','All family roles','Family roles','Family roles: small wins, shared rituals, real life'}
    for link in doc.xpath('//a[@href="/family-roles.html"]'):
        for node in link.iter():
            if node.text and node.text.strip() in old_labels:node.text='Family & caregiver support'
    # Keep hand-selected local stories and related guides. Replace the older
    # generic block only where it adds little, or where the caregiver path is revised.
    for node in list(doc.iter()):
        if has_class(node, {'reader-next','reader-breadcrumb'}):
            node.getparent().remove(node)
    related=[node for node in doc.iter() if has_class(node,RELATED)]
    for node in related:
        generic=has_class(node,{'aal-more'}) or 'More practical guides' in node.text_content()
        if generic or relative in REPLACE_RELATED or relative.endswith('-role.html'):
            remove_preserving_anchors(node)
    has_related=any(has_class(node,RELATED) for node in doc.iter())
    existing_crumb=any(has_class(node,{'article-crumb','aal-breadcrumb','breadcrumb','breadcrumbs'}) or (node.tag=='nav' and node.get('aria-label')=='Breadcrumb') for node in main.iter())
    if not existing_crumb:
        crumb=etree.Element('nav',{'class':'reader-breadcrumb','aria-label':'Breadcrumb'})
        a=etree.SubElement(crumb,'a',href='/');a.text='Home'
        if parent!=page_url(relative):
            sep=etree.SubElement(crumb,'span',{'aria-hidden':'true'});sep.text='/'
            a=etree.SubElement(crumb,'a',href=parent);a.text=name
        main.insert(0,crumb)
    if relative not in POLICIES:
        section=etree.SubElement(main,'div',{'class':'reader-next reader-next--compact'} if has_related else {'class':'reader-next'})
        if not has_related:
            section.tag='section';section.set('aria-labelledby','reader-next-title')
            eyebrow=etree.SubElement(section,'p',{'class':'eyebrow'});eyebrow.text='Stories & useful next steps'
            h2=etree.SubElement(section,'h2',id='reader-next-title');h2.text='Keep exploring.'
            grid=etree.SubElement(section,'div',{'class':'reader-next-grid'})
            for item in selected_cards(relative,group):
                a=etree.SubElement(grid,'a',{'class':'reader-next-card','href':item['url']})
                etree.SubElement(a,'img',src=item['image'],alt='',loading='lazy',decoding='async',width='180',height='180')
                copy=etree.SubElement(a,'div')
                kind=etree.SubElement(copy,'span',{'class':'reader-kind'});kind.text=item['kind']
                h3=etree.SubElement(copy,'h3');h3.text=item['title']
                p=etree.SubElement(copy,'p');p.text=item['description']
        nav=etree.SubElement(section,'nav',{'class':'reader-exits','aria-label':'Explore more'})
        exits=[]
        for href,label in [(parent,name),('/blog.html','All stories'),('/family-roles.html','Family & caregiver support'),('/library.html','Search every guide')]:
            if href!=page_url(relative) and href not in exits:
                a=etree.SubElement(nav,'a',href=href);a.text=label
                exits.append(href)
    if not doc.xpath('//link[contains(@href,"/assets/reader-pathways.css")]'):
        etree.SubElement(heads[0],'link',rel='stylesheet',href='/assets/reader-pathways.css?v='+VERSION)
    return html.tostring(doc,encoding='unicode',method='html',doctype='<!doctype html>')+'\n'

def prepare(root):
    categories={r['url']:r.get('category','') for r in json.loads((REPO/'data/library.json').read_text()) if r.get('url')}
    changed=0
    for page in root.rglob('*.html'):
        relative=page.relative_to(root).as_posix()
        if any(part.startswith('.') or part in {'node_modules','docs','tests','content','assets','downloads'} for part in Path(relative).parts):continue
        source=page.read_text();updated=apply_to_page(source,relative,categories)
        if updated!=source:page.write_text(updated);changed+=1
    print('Prepared contextual reading paths on',changed,'pages')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    prepare(parser.parse_args().root)
