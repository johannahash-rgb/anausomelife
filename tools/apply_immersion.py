#!/usr/bin/env python3
"""Apply the shared visual layer after older page generators, without replacing their content."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent.parent
VERSION = 'editorial-20261003'
for p in ROOT.rglob('*.html'):
    if any(x in p.parts for x in ('.git', 'content')):
        continue
    s = p.read_text()
    if '<main' not in s or '<footer' not in s:
        continue
    if p == ROOT / 'index.html':
        s = re.sub(r'(<main\b[^>]*>).*?(</main>)', lambda m: m[1] + '\n' + (ROOT/'content/home-entrance.html').read_text() + '\n' + m[2], s, count=1, flags=re.S)
        s = s.replace('<title>An AUsome Life | An AUsome Life</title>', '<title>An AUsome Life | The Good New England Life</title>')
    if '/assets/immersion.css' not in s:
        s = s.replace('</head>', f'<link rel="stylesheet" href="/assets/immersion.css?v={VERSION}"></head>')
    if '/assets/immersion.js' not in s:
        s = s.replace('</body>', f'<script src="/assets/immersion.js?v={VERSION}" defer></script></body>')
    if '/assets/editorial.css' not in s:
        s = s.replace('</head>', '<link rel="stylesheet" href="/assets/editorial.css?v=20261003-mainstreet"></head>')
    s = re.sub(r'(/assets/(?:magazine|site)\.js)\?[^"\s]+', rf'\1?v={VERSION}', s)
    s = s.replace('Beautiful. Useful. Lived in.', 'In pursuit of the Good New England Life')
    p.write_text(s)
print('Applied the shared visual layer and current homepage')
