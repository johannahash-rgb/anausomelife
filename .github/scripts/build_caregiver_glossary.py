#!/usr/bin/env python3
"""Render the approved glossary into static, searchable, no-JavaScript-readable HTML."""
import html
import json
import re
from pathlib import Path

ART = {
    'Identity & support': 'journal-v2-320.webp',
    'Communication': 'care-clipboard-128.webp',
    'Sensory & regulation': 'outings-320.webp',
    'Behavior & learning': 'yankee-toolbox-128.webp',
    'IEP & school': 'directory-128.webp',
    'Rights & safety': 'family-organizer-320.webp',
}
ALIASES = {
    'AAC': 'AAC — Augmentative & Alternative Communication',
    'ADLs': 'ADLs — Activities of Daily Living',
    'IADLs': 'IADLs — Instrumental Activities of Daily Living',
    'Intellectual disability': 'Intellectual disability (ID)',
    'Apraxia of speech': 'Apraxia of speech / Childhood Apraxia of Speech (CAS)',
    'Minimally speaking': 'Minimally speaking / minimally verbal',
    'Gestalt language processing': 'Gestalt language processing (GLP)',
    'FBA': 'FBA — Functional Behavioral Assessment',
    'BIP / Behavior Support Plan': 'BIP / BSP — Behavior Intervention or Support Plan',
    'ABC': 'Antecedent–Behavior–Consequence (ABC)',
    'Replacement behavior': 'Replacement behavior / replacement skill',
    'Prompt fading': 'Prompt fading / prompt dependence',
    'Aided language modeling': 'Aided language modeling / AAC modeling',
    'Punishment': 'Punishment (behavioral definition)',
    'IDEA': 'IDEA — Individuals with Disabilities Education Act',
    'IEP': 'IEP — Individualized Education Program',
    'FAPE': 'FAPE — Free Appropriate Public Education',
    'LRE': 'LRE — Least Restrictive Environment',
    'IEE': 'IEE — Independent Educational Evaluation',
    'Reevaluation': 'Reevaluation / “three-year” evaluation',
    'Functional noncompliance': 'Functional noncompliance / safe refusal',
    'Pain communication': 'Pain communication / diagnostic overshadowing',
}


def esc(value):
    return html.escape(str(value), quote=True)


def slug(value):
    return 'term-' + re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def load_terms(root):
    terms = []
    for n in range(1, 16):
        path = root / 'assets' / f'caregiver-glossary-terms-{n}.js'
        source = path.read_text(encoding='utf-8')
        prefix = 'window.CG_TERMS=(window.CG_TERMS||[]).concat('
        if not source.startswith(prefix) or not source.rstrip().endswith(');'):
            raise ValueError(f'Unexpected glossary data format: {path}')
        terms.extend(json.loads(source[len(prefix):].rstrip()[:-2]))
    if len(terms) != 104 or len({t['term'] for t in terms}) != 104:
        raise ValueError('Expected 104 unique approved glossary entries')
    for term in terms:
        for field in ('term', 'cat', 'plain', 'why', 'look', 'ask', 'sources'):
            if not term.get(field):
                raise ValueError(f'Missing {field}: {term.get("term")}')
        if term['cat'] not in ART:
            raise ValueError('Unknown glossary category')
        for source in term['sources']:
            if not source['url'].startswith('https://'):
                raise ValueError('Further-reading link must use HTTPS')
    return sorted(terms, key=lambda t: t['term'].casefold())


def render_card(t, names):
    target = slug(t['term'])
    aliases = [a for a, title in ALIASES.items() if title == t['term']]
    source_links = ''.join(
        '<li><a href="' + esc(s['url']) + '" target="_blank" rel="noopener noreferrer">'
        + esc(s['label']) + ' <span aria-hidden="true">↗</span><span class="cg-sr"> (opens in a new tab)</span></a></li>'
        for s in t['sources'])
    related = []
    for short in t.get('related', []):
        title = ALIASES.get(short, short)
        if title in names and title != t['term']:
            related.append('<a href="#' + slug(title) + '">' + esc(short) + '</a>')
    note = ('<section><h3>Language &amp; practice note</h3><p class="cg-note">' + esc(t['note']) + '</p></section>') if t.get('note') else ''
    related_html = ('<section><h3>Related terms</h3><nav class="cg-related" aria-label="Related to ' + esc(t['term']) + '">' + ''.join(related) + '</nav></section>') if related else ''
    return f'''<details class="cg-term" id="{target}" data-category="{esc(t['cat'])}" data-name="{esc(t['term'])}" data-aliases="{esc(' | '.join(aliases))}">
<summary><img class="cg-term-icon" src="/assets/navigation-watercolors/{ART[t['cat']]}" alt="" width="44" height="44" loading="lazy"><span class="cg-summary-copy"><span class="cg-cat">{esc(t['cat'])}</span><h2>{esc(t['term'])}</h2><span class="cg-preview">{esc(t['plain'])}</span></span><span class="cg-plus" aria-hidden="true">+</span></summary>
<div class="cg-body"><section><h3>Plain English</h3><p>{esc(t['plain'])}</p></section><section><h3>Why caregivers should know this</h3><p>{esc(t['why'])}</p></section><section><h3>What it may look like</h3><p>{esc(t['look'])}</p></section><section><h3>A useful caregiver question</h3><blockquote>{esc(t['ask'])}</blockquote></section>{note}<section><h3>Read further</h3><ul class="cg-links">{source_links}</ul></section>{related_html}<a class="cg-permalink" href="#{target}">Link to this definition <span aria-hidden="true">↗</span></a></div></details>'''


def build(root):
    root = Path(root)
    page = root / 'caregiver-glossary.html'
    if not page.exists():
        return
    terms = load_terms(root)
    names = {t['term'] for t in terms}
    cards = '\n'.join(render_card(t, names) for t in terms)
    source = page.read_text(encoding='utf-8')
    marker = r'(<!-- GLOSSARY:START -->).*?(<!-- GLOSSARY:END -->)'
    if not re.search(marker, source, re.S):
        raise ValueError('Missing glossary render markers')
    source = re.sub(marker, lambda m: m[1] + '\n' + cards + '\n' + m[2], source, count=1, flags=re.S)
    page.write_text(source, encoding='utf-8')
    # Preserve the existing caregiver hub and add a small, contextual entry point.
    hub = root / 'family-roles.html'
    if hub.exists():
        text = hub.read_text(encoding='utf-8')
        if 'href="/caregiver-glossary.html"' not in text:
            anchor = '<h2 id="practical-title">What would help today?</h2>'
            if anchor not in text:
                raise ValueError('Caregiver hub anchor changed; review glossary link insertion')
            addition = '<p class="care-more-story"><a href="/caregiver-glossary.html">New: The caregiver’s glossary</a> — 104 plain-English terms for communication, sensory needs, behavior, rights and IEP meetings.</p>'
            hub.write_text(text.replace(anchor, anchor + addition, 1), encoding='utf-8')
    print('Rendered 104 caregiver glossary entries with source links and the existing site branding')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    build(parser.parse_args().root)
