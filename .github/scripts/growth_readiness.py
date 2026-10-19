#!/usr/bin/env python3
"""Add static editorial inquiry routes to the publication artifact, idempotently.

This adds no tracking and makes no traffic, partner, outcome, or press claims.
Original article bodies, photo pixels, homepage composition, and top navigation
are preserved. Finished content is injected before the search index is rebuilt.
"""
import argparse
import html
import json
import re
from pathlib import Path
from lxml import html as dom

VERSION = '20261018-growth-v1'
BASE = 'https://anausomelife.com'
PRODUCTS = '''<section class="brand-section growth-section wrap" id="products" aria-labelledby="products-title">
<p class="eyebrow">For product &amp; PR teams</p><h2 id="products-title">Well made. Well used. Worth the space.</h2>
<p class="growth-intro">A canvas hamper that handles a full laundry day. A wool layer we reach for again. A kitchen tool that makes one everyday job easier. We are interested in beautiful, practical products with a reason to belong in real New England family life.</p>
<div class="growth-grid">
<article><span class="growth-number">01 / The fit</span><h3>Useful, not just photogenic.</h3><p>Home organization, linens, tabletop, kitchen tools, classic clothing, outerwear, travel gear and age-respectful family products. Premium pieces and good-value finds both belong when the usefulness is there.</p></article>
<article><span class="growth-number">02 / The work</span><h3>The details beyond the unboxing.</h3><p>We consider fit, measurements, setup, feel, cleaning, care, storage and the work a product leaves behind. A story may include original photographs, what worked, what did not and who the product may suit.</p></article>
<article><span class="growth-number">03 / The arrangement</span><h3>Agree the terms first.</h3><p>Propose a review sample or a loan with a clear return plan. We agree the editorial fit, testing window, any social coverage and any separate image rights before anything ships.</p></article>
</div>
<div class="growth-note"><strong>A sample is not a purchased verdict.</strong> Sending an item does not guarantee coverage or a positive review. Gifted, hosted, paid and affiliate relationships are disclosed. We do not offer paid customer-star reviews or therapeutic claims.</div>
<div class="growth-links"><a class="growth-button" href="mailto:hello@anausomelife.com?subject=Product%20review%20proposal">Propose a product for review</a><a href="#contact">Prepare an inquiry</a><a href="/how-we-choose.html">How we choose</a><a href="/disclosure.html">Our disclosure standard</a></div>
<details><summary>What should a product pitch include?</summary><p>The exact product and link, the everyday problem it solves, dimensions or sizing where relevant, availability, sample or loan terms, and your timing. Mention any requested deliverables or usage rights. Please wait for agreement before sending a package; shipping details are shared privately.</p></details>
<p><strong>Start with the work, not a logo list.</strong> Read our <a href="/little-things-that-help.html">everyday kitchen notes</a>, <a href="/eight-oclock-colombian-peaks-field-note.html">coffee field note</a> and <a href="/things-weve-bought.html">purchased-item notes</a>. These are examples of our editorial approach, not evidence of paid partnerships or laboratory testing.</p>
</section>'''
PRESS_DESK = '''<section class="brand-section growth-section wrap" id="press-desk" aria-labelledby="press-desk-title">
<p class="eyebrow">For journalists, editors &amp; producers</p><h2 id="press-desk-title">A useful story starts with a real day.</h2>
<p class="growth-intro">An AUsome Life is an independent Massachusetts-based publication about New England family life, places worth visiting and things worth keeping, with the practical access details left in. The website launched in October 2026.</p>
<div class="growth-grid">
<article><span class="growth-number">A reporting angle</span><h3>The information before the outing.</h3><p>What families need beyond a destination photograph: arrival, pacing, food, facilities and the option of a shorter visit.</p><p><a href="/guides/accessible-trails-new-england.html">Explore the New England trail guide</a></p></article>
<article><span class="growth-number">A tool to demonstrate</span><h3>Make the next step visible.</h3><p>Picture communication cards and a visual visit planner give families something concrete to prepare, adapt and take along.</p><p><a href="/communication-card-generator.html">Try the picture-card maker</a> · <a href="/visit-story.html">Open the visit planner</a></p></article>
<article><span class="growth-number">A lived perspective</span><h3>Participation, not a perfect day.</h3><p>Firsthand family stories about ordinary pleasures and the practical details that help make room for them. Personal experience is distinct from clinical expertise or an accessibility audit.</p><p><a href="/blog.html">Read the journal</a> · <a href="/language.html">Read our representation standard</a></p></article>
</div>
<div class="growth-links"><a class="growth-button" href="mailto:hello@anausomelife.com?subject=Press%20inquiry">Request an interview or background</a><a href="/downloads/an-ausome-life-press-facts.txt" download>Download publication facts (.txt)</a><a href="/press.html">Community mentions &amp; source links</a></div>
<p class="growth-note">Include your outlet, story angle, deadline and time zone. Ask about original photographs or a tool demonstration; availability and permissions are confirmed individually. Community shares and discovery listings are not presented as commissioned reporting, and family favorites are not a partner roster.</p>
</section>'''
CONTACT = '''<section class="brand-section growth-section wrap" id="contact" aria-labelledby="contact-title"><div class="growth-split">
<div><p class="eyebrow">A direct conversation</p><h2 id="contact-title">Let’s make a good story happen.</h2>
<p class="growth-intro">A product to consider, a place to visit, an interview or a photograph you would like to use? A few details are enough to begin.</p>
<p><a href="mailto:hello@anausomelife.com">hello@anausomelife.com</a></p><p><a href="https://www.instagram.com/anausomelife/">Find us on Instagram</a></p>
<p>We discuss the fit, scope and next steps directly. Audience figures, when requested, are supplied with their platform and reporting period; follower counts are not website traffic or reach.</p>
<p class="growth-note" id="inquiry-privacy">This prepares an email on your device. Nothing is submitted or stored by this form. Please leave private care records, shipping addresses and other sensitive family details out of the initial inquiry. You can email us directly without using this helper.</p>
</div><form class="growth-inquiry" id="editorial-inquiry" aria-label="Prepare an editorial inquiry" aria-describedby="inquiry-privacy" onsubmit="return false">
<label for="inquiry-purpose">What would you like to discuss?</label><select id="inquiry-purpose" name="purpose"><option value="product">Product review sample or loan</option><option value="travel">Travel or destination story</option><option value="press">Interview, press or editorial inquiry</option><option value="licensing">Photography or content permission</option></select>
<label for="inquiry-organization">Brand, organization or publication</label><input id="inquiry-organization" name="organization" required maxlength="120" autocomplete="organization" placeholder="For example: your publication or brand">
<label for="inquiry-reference">Product, property or story link <span class="growth-optional">(optional)</span></label><input id="inquiry-reference" name="reference" type="url" maxlength="500" placeholder="https://example.com/product">
<label for="inquiry-timing">Timing or deadline <span class="growth-optional">(optional)</span></label><input id="inquiry-timing" name="timing" maxlength="140" placeholder="For example: November, or Friday at noon Eastern">
<label for="inquiry-details">The idea &amp; proposed arrangement <span class="growth-optional">(optional)</span></label><textarea id="inquiry-details" name="details" maxlength="1200" rows="5" aria-describedby="inquiry-details-help" placeholder="What is the story, and what would you like to propose?"></textarea><p class="growth-field-help" id="inquiry-details-help">Product or model, the job it does, sample or loan terms, and your suggested testing window.</p>
<div class="growth-links"><button class="growth-button" id="inquiry-prepare" type="button" hidden>Prepare my email</button><a href="mailto:hello@anausomelife.com">Email directly instead</a></div>
<noscript><p>The optional draft helper needs JavaScript. Please use the email link above; no form is submitted here.</p></noscript>
<div class="growth-output" id="inquiry-output" hidden><h3>Your email draft</h3><p id="inquiry-output-notice">Your draft is ready, not sent.</p><label for="inquiry-message">Review and copy your message</label><textarea id="inquiry-message" rows="10" readonly></textarea><div class="growth-links"><a class="growth-button" id="inquiry-email" href="mailto:hello@anausomelife.com">Open my email app</a><button class="growth-button growth-button-secondary" id="inquiry-copy" type="button">Copy the full request</button></div></div>
<p class="growth-status" id="inquiry-status" role="status" aria-live="polite"></p></form></div></section>'''
PRESS_CALLOUT = '''<section class="growth-section growth-press-note wrap" aria-labelledby="press-contact-heading"><p class="eyebrow">Working on a story?</p><h2 id="press-contact-heading">The editor’s desk is open.</h2><p class="growth-intro">Find publication background, reporting angles, free tools to demonstrate and a direct editorial contact. The mentions below distinguish community shares and discovery listings from reported press coverage.</p><div class="growth-links"><a class="growth-button" href="/media/#press-desk">For journalists &amp; editors</a><a href="/downloads/an-ausome-life-press-facts.txt" download>Publication facts (.txt)</a><a href="mailto:hello@anausomelife.com?subject=Press%20inquiry">Send a press inquiry</a></div></section>'''
CONTACT_ROUTES = '''<section class="growth-section wrap" aria-labelledby="contact-routes-title"><p class="eyebrow">Find the right conversation</p><h2 id="contact-routes-title">For brands, places &amp; publications.</h2><div class="growth-grid"><article><h3>A product worth testing?</h3><p>See our editorial interests, sample and loan approach, and what to include before anything ships.</p><p><a href="/media/#products">Product review inquiries</a></p></article><article><h3>A place with a story?</h3><p>See published examples and a sample travel scope, with hosting, timing and rights agreed in advance.</p><p><a href="/media/#travel">Travel &amp; destination inquiries</a></p></article><article><h3>Reporting or sharing?</h3><p>Find publication facts, request an interview or ask about photographs and content permissions.</p><p><a href="/media/#press-desk">For journalists</a> · <a href="/media/#sharing">Sharing &amp; permissions</a></p></article></div></section>'''
PRODUCT_NOTES = '''<section class="growth-section wrap" aria-labelledby="review-notes-title"><p class="eyebrow">Before the buying checklist</p><h2 id="review-notes-title">Start with what we have actually used.</h2><p class="growth-intro">Firsthand notes, researched buying guides and practical checklists do different jobs. Look for the experience described and the disclosure on the individual story, rather than assuming every guide is a tested-product review.</p><div class="growth-links"><a href="/little-things-that-help.html">From our own kitchen</a><a href="/eight-oclock-colombian-peaks-field-note.html">The coffee field note</a><a href="/things-weve-bought.html">Things we have bought</a><a href="/how-we-choose.html">How we choose</a></div></section>'''


def owned(source, key, block, anchor):
    """Insert once; update only the block this module owns on subsequent builds."""
    marked = '<!-- aal-growth:' + key + ':start -->\n' + block + '\n<!-- aal-growth:' + key + ':end -->'
    pattern = r'<!-- aal-growth:' + re.escape(key) + r':start -->.*?<!-- aal-growth:' + re.escape(key) + r':end -->'
    if re.search(pattern, source, re.S):
        return re.sub(pattern, lambda _: marked, source, count=1, flags=re.S)
    match = re.search(anchor, source, re.S)
    if not match:
        raise ValueError('Cannot find insertion anchor for ' + key)
    return source[:match.start()] + marked + '\n' + source[match.start():]


def before_section(identifier):
    return r'<section\b(?=[^>]*\bid="' + re.escape(identifier) + r'")[^>]*>'


def finish_footer(source):
    def update(match):
        footer = match[0]
        footer = footer.replace('>Media Kit &amp; partnerships</a>', '>Brands &amp; partnerships</a>')
        footer = footer.replace('>Media &amp; partnerships</a>', '>Brands &amp; partnerships</a>')
        if '/media/#press-desk' not in footer and '</nav>' in footer:
            footer = footer.replace('</nav>', '<a href="/media/#press-desk">For journalists</a></nav>', 1)
        return footer
    return re.sub(r'<footer\b.*?</footer>', update, source, flags=re.S)


def add_metadata(source, relative):
    """Fill omissions only; preserve existing authored previews and canonical URLs."""
    parsed = dom.fromstring(source)
    if any('noindex' in x.lower() for x in parsed.xpath('//meta[@name="robots"]/@content')):
        return source
    title = ' '.join(parsed.xpath('//title/text()')).strip()
    description = parsed.xpath('//meta[@name="description"]/@content')
    canonical = parsed.xpath('//link[@rel="canonical"]/@href')
    if not title or not description or not canonical:
        return source
    tags = {x.get('property') or x.get('name'): x.get('content', '') for x in parsed.xpath('//head/meta')}
    fallback = BASE + '/assets/catalog-hero.webp'
    desired = {'og:type':'website', 'og:site_name':'An AUsome Life', 'og:title':title,
               'og:description':description[0], 'og:url':canonical[0], 'og:image':fallback,
               'twitter:card':'summary_large_image', 'twitter:title':tags.get('og:title', title),
               'twitter:description':tags.get('og:description', description[0])}
    image = tags.get('og:image') or fallback
    alt = tags.get('og:image:alt') or ('Original editorial watercolor of a canvas tote, folded towels, a notebook and a cup of coffee.' if image == fallback else 'An AUsome Life')
    desired.update({'twitter:image':image, 'twitter:image:alt':alt})
    if not tags.get('og:image'):
        desired.update({'og:image:alt':alt, 'og:image:type':'image/webp', 'og:image:width':'1536', 'og:image:height':'1024'})
    extra = []
    for key, value in desired.items():
        if key not in tags:
            attribute = 'property' if key.startswith('og:') else 'name'
            extra.append('<meta ' + attribute + '="' + key + '" content="' + html.escape(value, quote=True) + '">')
    if relative in {'media/index.html', 'press.html'} and not parsed.xpath('//script[@type="application/ld+json"]'):
        data = {'@context':'https://schema.org', '@type':'WebPage', '@id':canonical[0], 'url':canonical[0], 'name':title,
                'isPartOf':{'@type':'WebSite', 'name':'An AUsome Life', 'url':BASE + '/',
                            'publisher':{'@type':'Organization', 'name':'An AUsome Life', 'url':BASE + '/', 'email':'hello@anausomelife.com'}}}
        extra.append('<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c') + '</script>')
    return source.replace('</head>', '\n'.join(extra) + '\n</head>', 1) if extra else source


def prepare(root):
    root = Path(root)
    changed = 0
    for page in root.rglob('*.html'):
        relative = page.relative_to(root).as_posix()
        if any(x.startswith('.') or x in {'assets','content','downloads','docs','tools','tests','node_modules'} for x in page.relative_to(root).parts):
            continue
        source = page.read_text(encoding='utf-8')
        if '<main' not in source or '</head>' not in source or relative.startswith('preview-') or relative == '404.html':
            continue
        original = source
        if relative == 'media/index.html':
            # Preserve this authored edition's sections and navigation, as on press.html.
            if not dom.fromstring(source).xpath('//main[@id="main"][@data-media-edition="family-press-20261019"]'):
                source = owned(source, 'products', PRODUCTS, before_section('testing'))
                source = owned(source, 'press', PRESS_DESK, before_section('contact'))
                source, number = re.subn(before_section('contact') + r'.*?</section>', lambda _: CONTACT, source, count=1, flags=re.S)
                if number != 1:
                    raise ValueError('Expected exactly one media contact section')
                nav = '<nav class="brand-subnav wrap" aria-label="For brands"><a href="#work-with-us">Ways to work together</a><a href="#selected-work">Published stories</a><a href="#products">Product reviews</a><a href="#travel">Travel proposal</a><a href="#press-desk">For journalists</a><a href="#sharing">Share a story</a><a href="#contact">Get in touch</a></nav>'
                source, number = re.subn(r'<nav\b(?=[^>]*\bclass="brand-subnav\b)[^>]*>.*?</nav>', lambda _: nav, source, count=1, flags=re.S)
                if number != 1:
                    raise ValueError('Expected media section navigation')
            # Route the product offer to the broader review brief, preserving #testing.
            source = source.replace('href="#testing">See our product approach', 'href="#products">See our product approach')
            if '/assets/inquiry-builder.js' not in source:
                source = source.replace('</body>', '<script defer src="/assets/inquiry-builder.js?v=' + VERSION + '"></script></body>', 1)
        elif relative == 'press.html':
            # The revised press page has an authored media desk and contact panel.
            # Do not insert a redundant generated callout into that layout.
            if 'id="press-contact"' not in source:
                source = owned(source, 'press-callout', PRESS_CALLOUT, r'<section\b(?=[^>]*\bclass="press-section\b)[^>]*>')
        elif relative == 'contact.html':
            anchor = r'<section\b(?=[^>]*\bclass="reader-next\b)[^>]*>' if 'class="reader-next"' in source else r'</main>'
            source = owned(source, 'contact-routes', CONTACT_ROUTES, anchor)
        elif relative == 'product-guides.html':
            # Immediately after the introductory hero, before the long guide directory.
            key = 'product-notes'
            marker = r'<!-- aal-growth:' + key + r':start -->.*?<!-- aal-growth:' + key + r':end -->\s*'
            source = re.sub(marker, '', source, flags=re.S)
            main = re.search(r'<main\b[^>]*>', source)
            end = source.find('</section>', main.end()) if main else -1
            if end < 0:
                raise ValueError('Expected a product-guide introduction')
            end += len('</section>')
            source = source[:end] + '\n<!-- aal-growth:' + key + ':start -->\n' + PRODUCT_NOTES + '\n<!-- aal-growth:' + key + ':end -->\n' + source[end:].lstrip('\n')
        if ('growth-section' in source or relative == 'press.html') and '/assets/growth-readiness.css' not in source:
            source = source.replace('</head>', '<link rel="stylesheet" href="/assets/growth-readiness.css?v=' + VERSION + '">\n</head>', 1)
        source = finish_footer(source)
        source = add_metadata(source, relative)
        if source != original:
            page.write_text(source, encoding='utf-8')
            changed += 1
    # The fallback footer used by the existing navigation must match static HTML.
    nav_path = root / 'assets/global-nav.js'
    if nav_path.exists():
        source = nav_path.read_text(encoding='utf-8')
        old = r'<a href=\"/media/\">Media Kit &amp; partnerships</a>'
        new = r'<a href=\"/media/\">Brands &amp; partnerships</a><a href=\"/media/#press-desk\">For journalists</a>'
        updated = source.replace(old, new)
        if updated != source:
            nav_path.write_text(updated, encoding='utf-8')
    print('Prepared editorial inquiry routes and sharing metadata on', changed, 'pages')
    return changed


def check(root):
    root = Path(root)
    media = dom.fromstring((root / 'media/index.html').read_text())
    for identifier in ['products','testing','press-desk','contact','editorial-inquiry','brands','selected-work','travel','sharing']:
        assert len(media.xpath('//*[@id=$identifier]', identifier=identifier)) == 1, identifier
    assert not media.xpath('//header//a[contains(@href,"/media/")]'), 'Media must stay out of top navigation'
    assert media.xpath('//*[@data-brand-banner]'), 'Preserve the tried-and-true reel'
    assert media.xpath('//form[@id="editorial-inquiry"]//button[@id="inquiry-prepare"][@type="button"][@hidden]')
    for page in ['media/index.html','press.html','contact.html','product-guides.html']:
        parsed = dom.fromstring((root / page).read_text())
        ids = parsed.xpath('//*[@id]/@id')
        assert len(ids) == len(set(ids)), 'Duplicate IDs: ' + page
        assert len(parsed.xpath('//h1')) == 1, 'Heading structure: ' + page
        assert parsed.xpath('//link[contains(@href,"growth-readiness.css")]'), 'Missing new stylesheet: ' + page
        assert parsed.xpath('//footer//a[@href="/media/#press-desk"]'), 'Missing press footer: ' + page
    for page in root.rglob('*.html'):
        rel = page.relative_to(root).as_posix()
        if rel.startswith(('assets/','content/','downloads/','preview-')) or rel == '404.html':
            continue
        parsed = dom.fromstring(page.read_text())
        if not parsed.xpath('//main') or any('noindex' in x.lower() for x in parsed.xpath('//meta[@name="robots"]/@content')):
            continue
        if parsed.xpath('//meta[@name="description"]') and parsed.xpath('//link[@rel="canonical"]'):
            assert parsed.xpath('//meta[@property="og:image"]/@content'), 'Missing share image: ' + rel
            assert parsed.xpath('//meta[@name="twitter:card"]/@content'), 'Missing share card: ' + rel
    assert (root / 'downloads/an-ausome-life-press-facts.txt').is_file()
    print('Editorial growth publication checks passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    check(args.root) if args.check else prepare(args.root)
