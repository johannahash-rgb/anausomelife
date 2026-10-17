#!/usr/bin/env python3
"""Restore the library's approved art without rebuilding or replacing its catalog."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION = '20261016-fuller-design'
TOPICS = [
    ('home', 'At home', 'The everyday, made easier', 'home'),
    ('outings', 'Out & about', 'A good New England day', 'outings'),
    ('family', 'Family life', 'Communication & care', 'family'),
    ('stories', 'Family stories', 'From our camera roll', 'stories'),
    ('advocacy', 'School & advocacy', 'The useful details', 'advocacy'),
    ('holidays', 'Days to celebrate', 'Make the occasion yours', 'holidays'),
]
# All media already appears in its linked article. Preserve full frame and pixels.
ART = {
    '/autumn-simple-joys-james-ruby.html': ('/assets/family-notes/james-ruby-autumn.jpeg', 'James walking Ruby along a leaf-strewn road.'),
    '/little-things-that-help.html': ('/assets/family-notes/straw-lid-source-full.webp', 'A family photograph of a strawberry milk bottle with a straw through its lid.'),
    '/a-love-letter-to-buying-nothing.html': ('/assets/family-notes/boston-buy-nothing-print.jpg', 'A framed Boston alphabet print shared by a neighbor.'),
    '/my-small-world-autism-friendly-welcome.html': ('/assets/my-small-world/welcome-shop.webp', 'Original editorial illustration of a welcoming toy shop.'),
    '/fort-taber-snowshoes-field-note.html': ('/assets/family-notes/fort-taber-snowshoe-family.webp', 'A family photograph from the Fort Taber snowshoe outing.'),
    '/apple-orchard-afternoon.html': ('/assets/family-notes/doe-orchards-family.webp', 'A family photograph from Doe Orchards.'),
    '/wegmans-carolines-cart-field-note.html': ('/assets/family-notes/wegmans-carolines-cart.webp', 'A family photograph with Caroline’s Cart and a bouquet at Wegmans.'),
    '/margaritas-waltham-field-note.html': ('/assets/margaritas-waltham/jukebox-watercolor-v1.png', 'Original editorial illustration of the Margaritas jukebox.'),
    '/von-trapp-family-field-note.html': ('/assets/family-notes/von-trapp-table.webp', 'A family photograph at the table at the von Trapp lodge.'),
    '/wicked-tulips-family-field-note.html': ('/assets/family-notes/wicked-tulips-2019-smile.jpg', 'A family photograph from the tulip field.'),
    '/flowers-fidgets-and-clutter.html': ('/assets/family-notes/flowers-fidgets-clutter.webp', 'A family photograph of flowers and everyday things at home.'),
    '/aac-outing-note.html': ('/assets/destination-guides/communication-outing-note-20261004.webp', 'Original editorial illustration for an outing communication note.'),
}

def browsing():
    links = ''.join(f'<a class="library-topic" data-library-topic="{key}" href="/topics/{key}.html"><img src="/assets/library-watercolors/{art}-128.webp" srcset="/assets/library-watercolors/{art}-128.webp 128w, /assets/library-watercolors/{art}-320.webp 320w" sizes="(max-width:540px) 48px, (max-width:900px) 60px, 88px" alt="" width="88" height="88" decoding="async"><strong>{escape(label)}</strong><span>{escape(note)}</span></a>' for key,label,note,art in TOPICS)
    return '<section class="library-browse wrap" aria-labelledby="library-browse-title"><div class="library-browse-head"><h2 id="library-browse-title">A few lovely places to begin.</h2><a href="#library-search">Search every topic ↓</a></div><nav class="library-topic-grid" aria-label="Browse the library by topic">'+links+'</nav></section>'

def decorate(source):
    # Idempotent, preserving each existing article and its current ordering.
    source = re.sub(r'<section class="library-browse wrap".*?</section>', '', source, flags=re.S)
    source = re.sub(r'<figure class="library-entry-art">.*?</figure>', '', source, flags=re.S)
    if 'data-default-topic=""' not in source:
        return source
    source = source.replace('<section class="library-workspace', browsing()+'<section class="library-workspace', 1)
    css = f'<link rel="stylesheet" href="/assets/library-browse.css?v={VERSION}">'
    source = re.sub(r'<link[^>]+href="/assets/library-browse.css[^>]*>', '', source)
    source = source.replace('</head>', css+'</head>')
    source = re.sub(r'/assets/magazine\.js\?v=[^"\s]+', '/assets/magazine.js?v='+VERSION, source)
    source = source.replace('<div class="library-results">', '<div class="library-results" id="library-results" tabindex="-1">')
    def add_art(match):
        opening,url=match.group(0),match.group(1)
        art = ART.get(url)
        if not art:return opening
        src,alt=art
        if not (ROOT/src.lstrip('/')).exists():raise FileNotFoundError(src)
        return opening+f'<figure class="library-entry-art"><img src="{src}" alt="{escape(alt,quote=True)}" width="320" height="200" loading="lazy" decoding="async"></figure>'
    source = re.sub(r'<article class="index-card"[^>]*data-url="([^"]+)"[^>]*>', add_art, source)
    return source

if __name__ == '__main__':
    path=ROOT/'library.html'
    path.write_text(decorate(path.read_text()))
    print('Applied illustrated library topics and 12 article images; catalog preserved.')
