"""Keep reading primary and secondary tools optional, without changing their behavior."""
from lxml import etree

VERSION = '20261026-reading-ease'

def cls(root, name):
    return root.xpath('.//*[contains(concat(" ",normalize-space(@class)," ")," '+name+' ")]')

def text(node):
    return ' '.join(node.text_content().split())

def disclosure(node, label, kind='section', heading=False):
    parent=node.getparent()
    if parent is None or parent.get('data-reading-ease'):
        return parent
    details=etree.Element('details',{'class':'aal-ease-details aal-ease-'+kind,'data-reading-ease':kind})
    summary=etree.SubElement(details,'summary')
    if heading:
        titles=node.xpath('.//h2')
        if titles:
            title=titles[0];title.getparent().remove(title);summary.append(title)
        else:summary.text=label
    else:summary.text=label
    parent.replace(node,details);details.append(node)
    return details

def preserve_remove(node, destination=None):
    parent=node.getparent()
    if parent is None:return
    for key in node.xpath('.//*[@id]/@id')+([node.get('id')] if node.get('id') else []):
        marker=etree.Element('span',id=key)
        target=destination if destination is not None else node
        target.addprevious(marker)
    parent.remove(node)

def filters(form, nodes, label):
    nodes=[n for n in nodes if n.getparent() is form and not n.get('data-reading-ease')]
    if not nodes:return
    details=etree.Element('details',{'class':'aal-ease-details aal-ease-filters','data-reading-ease':'filters'})
    summary=etree.SubElement(details,'summary');summary.text=label
    etree.SubElement(summary,'span',{'data-ease-selected':''})
    panel=etree.SubElement(details,'div',{'class':'aal-ease-filter-fields'})
    nodes[0].addprevious(details)
    for node in nodes:panel.append(node)

def apply(doc, relative):
    main=doc.xpath('//main')[0]
    # Earlier publishing steps can replace a generated section inside its wrapper.
    # Remove the now-empty wrapper before folding the replacement section.
    for group in main.xpath('.//details[@data-reading-ease]'):
        if not any(child.tag != 'summary' for child in group):
            group.getparent().remove(group)
    # Rebuild this single secondary group because the collection generator refreshes its navs.
    old=main.xpath('.//details[@data-reading-ease="related"]')
    navs=cls(main,'aal-article-topics')+cls(main,'er-meta')+cls(main,'ed-tool-nav')+cls(main,'fn-breadcrumb')
    for group in old:
        for node in list(group):
            if node.tag!='summary' and node not in navs:navs.append(node)
        group.getparent().remove(group)
    if navs:
        group=etree.Element('details',{'class':'aal-ease-details aal-ease-related wrap','data-reading-ease':'related'})
        etree.SubElement(group,'summary').text='Explore related topics'
        for node in navs:group.append(node)
        before=next((n for n in main if set((n.get('class') or '').split())&{'er-related','fn-related','reader-next','aal-more'}),None)
        if before is not None:before.addprevious(group)
        else:main.append(group)

    # A contents menu belongs after the introduction, never ahead of the title.
    for menu in cls(main,'aal-on-this-page'):
        cover=next((n for n in main if n.xpath('.//h1')),None)
        if cover is not None:cover.addnext(menu)
    for nav in cls(main,'on-page'):
        if nav.getparent().tag=='details':continue
        links=nav.xpath('.//a')
        if len(links)<2:preserve_remove(nav)
        else:disclosure(nav,'On this page','contents')

    # Remove repeated cover artwork and exact repeated deck text, retaining unique introductions.
    for cover in cls(main,'er-cover'):
        lead=cls(cover,'er-lead');welcome=cls(cover,'er-welcome')
        if not lead or not welcome:continue
        sources=set(lead[0].xpath('.//img/@src'))
        for figure in welcome[0].xpath('.//figure'):
            imgs=figure.xpath('.//img/@src')
            if imgs and all(src in sources for src in imgs):preserve_remove(figure)
        decks=cls(cover,'er-deck')
        for p in cls(welcome[0],'er-welcome-copy'):
            if decks and text(p)==text(decks[0]):preserve_remove(p)
        if not welcome[0].xpath('.//figure'):
            welcome[0].set('class',(welcome[0].get('class') or '')+' aal-ease-welcome' if 'aal-ease-welcome' not in (welcome[0].get('class') or '') else welcome[0].get('class'))

    # Generated worksheet guides repeat their opening paragraphs in the detailed section.
    # Keep the authored prose in its first reading position; keep every unique list/detail.
    if main.xpath('.//*[@data-guide-panel]'):
        originals={}
        for scene in cls(main,'er-story-grid')+cls(main,'er-pedicab-scene'):
            for p in scene.xpath('.//p'):
                if len(text(p))>=100:originals[(text(p),tuple(p.xpath('.//a/@href')))]=p
        for practical in cls(main,'er-practical'):
            for p in list(practical.xpath('.//p')):
                key=(text(p),tuple(p.xpath('.//a/@href')))
                if key in originals and not p.xpath('.//img|.//input|.//button'):
                    preserve_remove(p,originals[key])
        for section in cls(main,'er-map-destination'):
            if not section.xpath('.//*[@data-guide-panel]'):continue
            wrapped=disclosure(section,'Use the optional checklist','worksheet')
            practical=cls(main,'er-practical')
            if practical and wrapped is not None:practical[-1].addnext(wrapped)

    # Directory search remains the obvious first action.
    for form in cls(main,'library-controls'):
        filters(form,cls(form,'filter-row'),'Filter results')
    for browse in cls(main,'library-browse'):
        wrapped=disclosure(browse,'Browse by topic','browse')
        workspace=cls(main,'library-workspace')
        if workspace:workspace[0].addnext(wrapped)
    for form in cls(main,'place-filters'):
        nodes=[n for n in form if n.xpath('.//select[@name="kind"]') or n.get('type')=='reset']
        filters(form,nodes,'More filters')
    if relative=='favorite-places.html':
        features=cls(main,'journal-features');workspace=cls(main,'places-workspace')
        if features and workspace:workspace[0].addnext(disclosure(features[0],'A few places to begin','browse'))
    for form in cls(main,'directory-controls'):
        existing=cls(form,'street-filter-grid')
        if existing:
            for reset in form.xpath('.//button[@type="reset"]'):existing[0].append(reset)
            for redundant in form.xpath('./details[@data-reading-ease="filters"]'):
                redundant.getparent().remove(redundant)
        else:
            filters(form,[n for n in form if not n.xpath('.//input[@name="q"]') and n.tag!='details'],'Filter the directory')

    # The calendar keeps place, date and search up front; secondary choices stay available.
    for start in cls(main,'calendar-start'):
        disclosure(start,'Quick ways to choose an outing','calendar-start')
    for toggle in cls(main,'calendar-view-toggle'):
        disclosure(toggle,'Calendar and map views','views')
    for form in cls(main,'event-filters'):
        primary=cls(form,'event-primary-filters');advanced=cls(form,'event-advanced-filters')
        if primary and advanced:
            for label in primary[0].xpath('./label[.//select[@name="cost"]]'):advanced[0].append(label)
            for note in form.xpath('./p[@id="event-cost-help"]'):advanced[0].append(note)

    # Picture search before optional collection lists; all editing/printing contracts remain.
    for toolbar in cls(main,'cc-tools'):
        filters(toolbar,[n for n in toolbar if n.xpath('.//select') or n.get('data-reset') is not None],'Filter pictures')
    for nav in cls(main,'cc-category-index'):
        toolbar=cls(main,'cc-tools')
        if toolbar and nav.getparent() is toolbar[0].getparent():toolbar[0].addnext(nav)
    for sets in cls(main,'cc-journal-sets'):
        cards=main.xpath('.//*[@id="cc-cards"]')
        if cards:cards[0].addnext(sets)

    # Choose one worksheet or note section instead of facing every input at once.
    if relative=='family-planning-toolkit.html':
        for planner in main.xpath('.//*[@data-planner]'):
            section=next((a for a in planner.iterancestors() if a.tag=='section'),None)
            if section is not None:disclosure(section,'Choose a planning card','planning-card',heading=True)
    if relative=='communication-notes.html':
        form=doc.get_element_by_id('comm-form',None)
        if form is not None:
            for fieldset in list(form.xpath('./fieldset'))[1:]:
                legend=fieldset.find('legend')
                disclosure(fieldset,text(legend) if legend is not None else 'More details','note-step')
        for section in cls(main,'field-notes-section'):disclosure(section,'Ready-made notes to borrow','notes')
        for section in cls(main,'maker-output'):
            section.set('tabindex','-1');section.set('data-ease-output','')

    # Story extras remain usable, shareable and reachable by their existing fragments.
    for name,label in [('aal-story-cards','Picture cards for this story'),('aal-story-share','Share this story')]:
        for node in cls(main,name):
            if node.xpath('.//h1'):continue
            if not any(a.tag=='details' for a in node.iterancestors()):disclosure(node,label,'story-extra')
    # Keep broad exits in one optional block when a page already has chosen next reads.
    for node in cls(main,'reader-next--compact'):
        disclosure(node,'More places to explore','exits')

    # Every heading break is a real word boundary, including in narrow layouts and spoken labels.
    for br in main.xpath('.//h1//br|.//h2//br|.//h3//br'):
        br.tail=' '+(br.tail or '').lstrip()
    head=doc.xpath('//head')[0];body=doc.xpath('//body')[0]
    for old in doc.xpath('//link[contains(@href,"/assets/reading-ease.css")]|//script[contains(@src,"/assets/reading-ease.js")]'):old.getparent().remove(old)
    etree.SubElement(head,'link',rel='stylesheet',href='/assets/reading-ease.css?v='+VERSION)
    etree.SubElement(body,'script',src='/assets/reading-ease.js?v='+VERSION,defer='')
