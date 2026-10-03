"""Apply the maintained short introductions without replacing existing field notes."""
from pathlib import Path
import json,re
from html import escape
ROOT=Path(__file__).resolve().parents[1]
notes=json.loads((ROOT/'data/outing-openings.json').read_text())
places=json.loads((ROOT/'data/places.json').read_text())
aliases={'decordova-sculpture-park':'decordova','misty-harbor-resort':'misty-harbor-wells','nubble-lighthouse':'york-nubble','rococo-ice-cream':'rococo-kennebunk'}
paths={p['url'].lstrip('/'):p['slug'] for p in places}
for f in (ROOT/'favorite-places').glob('*.html'):
    k=aliases.get(f.stem,f.stem)
    key=k if k in notes else 'favorite-places-'+k
    if key in notes: paths[str(f.relative_to(ROOT))]=key
icon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false"><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3zM9 3v15M15 6v15"/></svg>'
for relative,key in paths.items():
    p=ROOT/relative;s=p.read_text();n=notes[key]
    s=re.sub(r'\n?<!-- field-welcome:start -->.*?<!-- field-welcome:end -->\n?', '',s,flags=re.S)
    section=f'''\n<!-- field-welcome:start --><section class="field-welcome" aria-labelledby="field-welcome-title"><div class="wrap"><div><p class="eyebrow">{icon}{escape(n['kind'])}</p><h2 id="field-welcome-title">{escape(n['title'])}</h2><p class="field-memory">{escape(n['story'])}</p></div><aside><strong>A little plan to begin</strong><p>{escape(n['tip'])}</p><a class="field-plan-link" href="/visit-story.html?place={escape(key)}">{icon}Make our visit plan</a><p class="field-context">Keep one good thing. Leave room to change your mind.</p></aside></div></section><!-- field-welcome:end -->\n'''
    hero=re.search(r'<section\b[^>]*class="[^"]*\b(?:hero|favorite-hero)\b[^"]*"[^>]*>.*?</section>',s,re.S)
    if not hero: raise ValueError('No hero in '+relative)
    s=s[:hero.end()]+section+s[hero.end():]
    css='<link rel="stylesheet" href="/assets/outing-studio.css?v=20261003-outings">'
    if 'assets/outing-studio.css' not in s:s=s.replace('</head>',css+'</head>')
    p.write_text(s)
print(f'Updated {len(notes)} introductions across {len(paths)} guide pages.')
