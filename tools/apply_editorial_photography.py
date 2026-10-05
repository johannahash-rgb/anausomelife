#!/usr/bin/env python3
"""Retire decorative postcard art; preserve real photos and useful diagrams."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
PHOTO = '/assets/editorial/'
VERSION = '20261003-mainstreet'

def replacement(src):
    if src.startswith('/assets/favorites/') or src.startswith('/assets/favorite-'):
        if 'llbean' in src:
            return '/assets/outing-studio/freeport-boot.webp', 'Freeport-inspired editorial illustration.'
        if any(k in src for k in ('coast','marginal','kittery','walden')):
            return PHOTO+'coastal-walk.webp', 'New England coastal illustration.'
        if any(k in src for k in ('farm','wildwood','minute-man','decordova','frog-pond')):
            return PHOTO+'farm-meadow.webp', 'New England countryside illustration.'
        if any(k in src for k in ('pool','lifetime','misty','aquarium')):
            return PHOTO+'autumn-table.webp', 'Editorial still-life illustration for a day out.'
        return PHOTO+'main-street.webp', 'Illustration of a fictional New England village.'
    if src.startswith('/assets/catalog-') or src.startswith('/assets/guide-'):
        return PHOTO+'autumn-table.webp', 'New England still-life illustration.'
    if src.startswith('/assets/sketches/') and not src.endswith('family-roles-map.svg'):
        if any(k in src for k in ('outdoors','farm','football')):
            return PHOTO+'farm-meadow.webp', 'New England countryside illustration.'
        if any(k in src for k in ('books','everyday','treat','stay')):
            return PHOTO+'main-street.webp', 'Illustration of a fictional New England Main Street.'
        if 'water' in src:
            return PHOTO+'coastal-walk.webp', 'New England coastal illustration.'
        return PHOTO+'autumn-table.webp', 'New England still-life illustration.'
    return None

def image(match):
    tag = match.group(0)
    found = re.search(r'src="([^"]+)"', tag)
    choice = replacement(found.group(1)) if found else None
    if not choice: return tag
    src, alt = choice
    tag = tag.replace(found.group(0), 'src="'+src+'"')
    tag = re.sub(r'alt="[^"]*"', 'alt="'+alt+'"', tag)
    return tag

def figure(match):
    text = match.group(0)
    changed = re.sub(r'<img\b[^>]*>', image, text)
    if changed == text: return text
    image_tag = re.search(r'<img\b[^>]*>', changed).group(0)
    caption = re.search(r'alt="([^"]*)"', image_tag).group(1)
    if '<figcaption' in changed:
        changed = re.sub(r'<figcaption\b[^>]*>.*?</figcaption>', '<figcaption>'+caption+'</figcaption>', changed, flags=re.S)
    else:
        changed = changed.replace('</figure>', '<figcaption>'+caption+'</figcaption></figure>')
    return changed

count = 0
for path in sorted(ROOT.rglob('*.html')):
    rel=path.relative_to(ROOT).as_posix()
    if rel.startswith(('.git/','docs/','tests/','services/','generator-api/')): continue
    old=path.read_text()
    if '<main' not in old: continue
    new=re.sub(r'<figure\b[^>]*>.*?</figure>', figure, old, flags=re.S)
    new=re.sub(r'<img\b[^>]*>', image, new)
    # Every article gets the layer directly; stale shared scripts cannot omit it.
    css='<link rel="stylesheet" href="/assets/editorial.css?v='+VERSION+'">'
    if re.search(r'<link[^>]+href="/assets/editorial.css[^>]+>',new):
        new=re.sub(r'<link[^>]+href="/assets/editorial.css[^>]+>',css,new)
    else: new=new.replace('</head>',css+'</head>')
    if 'class="ellis-review' in new and '/assets/editorial-art-direction.css' not in new:
        new=new.replace('</head>', '<link rel="stylesheet" href="/assets/editorial-art-direction.css?v=20261004-watercolor"></head>')
    new=re.sub(r'/assets/global-nav\.js(?:\?v=[^"\s]+)?', '/assets/global-nav.js?v=20261004-art-direction', new)
    for asset in ('magazine','immersion'):
        new=re.sub(r'/assets/'+asset+r'\.js\?v=[^"\s]+','/assets/'+asset+'.js?v='+VERSION,new)
    new=new.replace('<a class="skip" href="#main">Skip to content</a><a class="skip" href="#main">Skip to content</a>','<a class="skip" href="#main">Skip to content</a>')
    if new!=old:path.write_text(new);count+=1
print('Updated photography and shared article styling on',count,'pages')
