#!/usr/bin/env python3
"""Apply reviewed social previews to source HTML and the GitHub Pages artifact.

Selections live outside the hosted artifact in docs/social-preview-selections.json.
There is deliberately no inferred image, page-order score, or global fallback.
Run after page generators. --check validates assets AND the static HTML without edits.
"""
import argparse
import hashlib
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlparse
from PIL import Image

DOMAIN = 'https://anausomelife.com'
REPO = Path(__file__).resolve().parents[2]
DEFAULT_SELECTIONS = REPO / 'docs/social-preview-selections.json'
HEAD = re.compile(r'(<head\b[^>]*>)(.*?)(</head\s*>)', re.I | re.S)
META = re.compile(r'<meta\b[^>]*>', re.I)
MANAGED = {'og:title', 'og:description', 'og:type', 'og:url', 'og:site_name', 'og:locale',
           'og:image', 'og:image:url', 'og:image:secure_url', 'og:image:type',
           'og:image:width', 'og:image:height', 'og:image:alt',
           'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image',
           'twitter:image:src', 'twitter:image:alt'}

class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}; self.canonicals = []; self.title = ''; self.in_title = False
        self.redirect = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta':
            key = (a.get('property') or a.get('name') or '').lower()
            self.meta.setdefault(key, []).append(a.get('content', ''))
            self.redirect |= a.get('http-equiv', '').lower() == 'refresh'
        if tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append(a.get('href', ''))
        if tag == 'title': self.in_title = True
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title += data
    def first(self, key):
        return next((v.strip() for v in self.meta.get(key, []) if v.strip()), '')

def shorten(text, limit):
    text = ' '.join(text.split())
    if len(text) <= limit: return text
    return text[:limit - 1].rsplit(' ', 1)[0].rstrip(' ,;:') + '…'

def local_file(root, value):
    # Reviewed paths are local and root-relative, without query, fragments or traversal.
    if not value.startswith('/') or value.startswith('//') or urlparse(value).query or urlparse(value).fragment:
        raise ValueError(f'Expected a root-relative asset path: {value}')
    path = (root / value.lstrip('/')).resolve()
    if not path.is_relative_to(root.resolve()): raise ValueError('Asset escapes site root')
    if not path.is_file(): raise ValueError(f'Missing image: {value}')
    return path

def validate_asset(root, choice):
    path = local_file(root, choice['image'])
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        im.load()  # Header checks alone miss truncated JPEGs and broken pixel streams.
        if im.format not in {'JPEG', 'PNG', 'WEBP'}: raise ValueError('Unsupported image format')
        if (im.width, im.height) != (choice['width'], choice['height']):
            raise ValueError('Image dimensions differ from reviewed selection')
        if Image.MIME[im.format] != choice['mime']: raise ValueError('Incorrect image MIME type')
        if min(im.size) < 144 or max(im.size) > 4096: raise ValueError('Image dimensions outside card bounds')
        if choice['card'] == 'summary_large_image' and (im.width < 300 or im.height < 157):
            raise ValueError('Image too small for a large card')
    if path.stat().st_size >= 5_000_000: raise ValueError('Image exceeds 5 MB card budget')
    if hashlib.sha256(path.read_bytes()).hexdigest() != choice['sha256']:
        raise ValueError('Image bytes changed; review the selection before publication')
    if not choice['alt'].strip() or len(choice['alt']) > 420: raise ValueError('Missing or overlong image description')
    if choice['card'] not in {'summary', 'summary_large_image'}: raise ValueError('Unsupported card type')
    if choice['type'] not in {'website', 'article'}: raise ValueError('Unsupported Open Graph type')
    if not choice.get('provenance'): raise ValueError('Missing provenance record')

def desired_metadata(source, choice):
    match = HEAD.search(source)
    if not match: raise ValueError('Not a complete HTML page')
    parsed = Head(); parsed.feed(match.group(2))
    if parsed.redirect or any('noindex' in v.lower() for v in parsed.meta.get('robots', [])):
        raise ValueError('Redirect/noindex pages must not receive editorial previews')
    if len(parsed.canonicals) != 1: raise ValueError('Expected one canonical link')
    canonical = parsed.canonicals[0]
    url = urlparse(canonical)
    if url.scheme != 'https' or url.netloc != 'anausomelife.com' or url.query or url.fragment:
        raise ValueError('Expected a clean absolute HTTPS canonical URL')
    title = parsed.first('og:title') or parsed.title.strip()
    description = parsed.first('og:description') or parsed.first('description')
    if not title or not description: raise ValueError('Missing editorial title or description')
    image = DOMAIN + quote(choice['image'], safe='/')
    values = {
        'og:type': choice['type'], 'og:site_name': 'An AUsome Life', 'og:locale': 'en_US',
        'og:title': title, 'og:description': description, 'og:url': canonical,
        'og:image': image, 'og:image:secure_url': image, 'og:image:type': choice['mime'],
        'og:image:width': str(choice['width']), 'og:image:height': str(choice['height']),
        'og:image:alt': choice['alt'], 'twitter:card': choice['card'],
        'twitter:title': shorten(title, 70), 'twitter:description': shorten(description, 200),
        'twitter:image': image, 'twitter:image:alt': choice['alt'],
    }
    return match, parsed, values

def render(source, choice):
    match, parsed, values = desired_metadata(source, choice)
    def remove_managed(m):
        tag = Head(); tag.feed(m.group())
        return '' if any(k in MANAGED for k in tag.meta) else m.group()
    head = META.sub(remove_managed, match.group(2))
    head = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)*', '\n\n', head).rstrip()
    tags = []
    for key, value in values.items():
        attr = 'property' if key.startswith('og:') else 'name'
        tags.append(f'<meta {attr}="{key}" content="{html.escape(value, quote=True)}">')
    return source[:match.start(2)] + head + '\n' + '\n'.join(tags) + '\n' + source[match.end(2):]

def check_metadata(source, choice):
    _, parsed, values = desired_metadata(source, choice)
    failures = [f'{key}: missing, duplicated or different from reviewed value'
                for key, value in values.items() if parsed.meta.get(key) != [value]]
    failures += [f'{key}: obsolete duplicate image tag' for key in MANAGED - values.keys() if key in parsed.meta]
    return failures

def apply(root, selections, check=False):
    root = root.resolve(); changes = []; errors = []; assets = set()
    # Validate the entire selection before changing any page.
    prepared = []
    for relative, choice in selections['pages'].items():
        try:
            path = (root / relative).resolve()
            if not path.is_relative_to(root) or not relative.endswith('.html'):
                raise ValueError('Page escapes site root or is not HTML')
            if relative.startswith(('content/', 'preview-', 'assets/venue-maps/')):
                raise ValueError('Fragments, previews and print pages are excluded')
            asset_key = (choice['image'], choice['sha256'], choice['width'], choice['height'], choice['mime'], choice['card'], choice['alt'])
            if asset_key not in assets: validate_asset(root, choice); assets.add(asset_key)
            source = path.read_text(encoding='utf-8')
            if check:
                errors.extend(f'{relative}: {e}' for e in check_metadata(source, choice))
            else:
                updated = render(source, choice)
                if updated != source: prepared.append((path, updated)); changes.append(relative)
        except (OSError, ValueError, KeyError) as e: errors.append(f'{relative}: {e}')
    if errors: return {'selected': len(selections['pages']), 'changed': 0, 'errors': errors}
    for path, updated in prepared: path.write_text(updated, encoding='utf-8')
    return {'selected': len(selections['pages']), 'changed': len(changes), 'errors': [],
            'distinct_images': len({c['image'] for c in selections['pages'].values()}),
            'pending': sorted(selections.get('pending', {}))}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('_site'))
    p.add_argument('--selections', type=Path, default=DEFAULT_SELECTIONS)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    result = apply(args.root, json.loads(args.selections.read_text()), args.check)
    print('SOCIAL_METADATA_SUMMARY', json.dumps(result))
    return bool(result['errors'])

if __name__ == '__main__': sys.exit(main())
