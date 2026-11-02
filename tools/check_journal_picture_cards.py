#!/usr/bin/env python3
"""Check curated article-card coverage and local artwork references."""
import json,re
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
catalog_source=(ROOT/'assets/card-catalog.js').read_text()
catalog=json.loads(catalog_source.split('window.AALCardCatalog = ',1)[1].strip().rstrip(';'))
by_id={card['id']:card for card in catalog}
assert len(catalog)==len(by_id), 'Duplicate picture-card IDs'
assert 'tulip' in by_id and 'tulip-farm' in by_id
assert all(face not in by_id for face in ('happy','sad','tired','hurt'))
assert sum(bool(card.get('photoRealistic')) for card in catalog)==448
# Pixel-reviewed sprite mappings: retain stable card IDs, not erroneous sheet numbers.
# These two cards also appear as static sprites in the time-change article.
article=(ROOT/'we-dont-fall-back-overnight.html').read_text()
for card_id, sheet, cell, label, position in (
    ('photo-08-dinner-plate', '07', 0, 'dinner plate', '0 0'),
    ('photo-15-pill-organizer', '14', 15, 'pill organizer', '100% 100%'),
):
    card=by_id[card_id]
    image=f'/assets/card-collection/photoreal/set-{sheet}.webp'
    assert (card['image'], card['cell'], card['label']) == (image, cell, label), card_id
    expected=(f'aria-label="A {label} on a plain background" '
              f'style="background-image:url(\'{image}\');background-position:{position}"')
    assert expected in article, (card_id, 'article sprite differs from reviewed mapping')
manifest=json.loads((ROOT/'data/journal-picture-cards.json').read_text())
class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.refs=[];self.cards=[];self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if a.get('data-story-card'):self.cards.append(a['data-story-card'])
        if tag in ('img','script') and a.get('src'):self.refs.append(a['src'])
for post in manifest['posts']:
    raw=(ROOT/post['path']).read_text()
    doc=Page();doc.feed(raw)
    assert doc.cards==post['cards'], (post['path'],'card selection differs')
    assert len(doc.ids)==len(set(doc.ids)), (post['path'],'duplicate HTML IDs')
    assert doc.h1==1, (post['path'],'expected one main headline')
    assert raw.count('data-story-cards')==1
    assert '/assets/journal-picture-cards.css?' in raw
    assert '/assets/journal-picture-cards.js?' in raw
    assert '/picture-card-library.html?cards='+','.join(post['cards']) in raw
    for card_id in post['cards']:
        assert card_id in by_id, (post['path'],card_id)
    if post.get('sketch'):
        assert post['sketch']['path'] in doc.refs, post['path']
        assert 'Original editorial illustration' in post['sketch']['caption']
    for src in doc.refs:
        if src.startswith('/') and not src.startswith('//'):
            assert (ROOT/src.split('?')[0].split('#')[0].lstrip('/')).is_file(), (post['path'],src)
for card in catalog:
    assert (ROOT/card['image'].lstrip('/')).is_file(), card['image']
for row in json.loads((ROOT/'content/family-field-notes.json').read_text()):
    post=next(p for p in manifest['posts'] if p['path']==row['path'])
    assert row['pictureCards']==post['cards']
    assert row['sketch']==post['sketch']
    assert row['pictureCardsHtml'] in (ROOT/row['path']).read_text()
for page in ('picture-card-library.html','communication-card-generator.html'):
    raw=(ROOT/page).read_text()
    assert ('700+' in raw or '723' in raw) and '448' in raw and 'photorealistic' in raw
    assert 'journal-card-sets' in raw and 'tulip-farm' in raw
assert 'params.get(\'cards\')' in (ROOT/'assets/card-collection.js').read_text()
assert 'article photos are not communication symbols' in (ROOT/'assets/article-picture-card.js').read_text()
print(f"PASS: {len(manifest['posts'])} story URLs, {len(catalog)} unique cards, artwork and generator references.")
