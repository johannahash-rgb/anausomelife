#!/usr/bin/env python3
"""Refresh universal search from current public page text; never regenerates editorial pages."""
from pathlib import Path
from lxml import html
import json,re
ROOT=Path(__file__).resolve().parent.parent
rows=[]
for p in sorted(ROOT.rglob('*.html')):
 rel=p.relative_to(ROOT).as_posix()
 if rel.startswith(('.git/','docs/','tests/')) or rel=='404.html':continue
 try:d=html.fromstring(p.read_text())
 except Exception:continue
 if d.xpath('//meta[translate(@http-equiv,"REFSH","refsh")="refresh"]'):continue
 main=d.xpath('//main');h=d.xpath('//h1');desc=d.xpath('//meta[@name="description"]/@content')
 if not main or not h:continue
 for e in main[0].xpath('.//script|.//style'):e.drop_tree()
 text=lambda s:re.sub(r'\s+',' ',s).strip()
 title=text(h[0].text_content())
 url='/' if rel=='index.html' else '/'+rel
 category='family' if any(v in rel for v in ['family','paternal','communication','little-adventures','kid-fun','profound','maternal-role','grandparent-role','sibling-role','extended-family-role','coparent-role','support-professional-role','respite-partner-role','caregiver-handover']) else 'outings' if any(v in rel for v in ['favorite-places','calendar','weekend','visit-story']) else 'guide'
 rows.append({'url':url,'title':title,'summary':desc[0] if desc else '', 'category':category,'format':'Tool' if rel in ['communication-card-generator.html','communication-notes.html','visit-story.html'] else 'Story' if rel=='little-adventures.html' else 'Page','search':text(main[0].text_content())})
events=json.loads((ROOT/'data/events.json').read_text())
for event in events.get('events',[]):
 if event.get('reviewRequired') or event.get('cancelled') or event.get('status') in ('review','cancelled','canceled'):continue
 rows.append({'url':'/calendar.html#event-'+event['id'],'title':event['title'],'summary':' · '.join(str(event.get(k,'')) for k in ['venue','city','state','start']),'category':'outings','format':'Event','search':json.dumps(event,ensure_ascii=False)})
for event in events.get('watchlist',[]):
 rows.append({'url':'/calendar.html#watchlist','title':event['title']+' — date watchlist','summary':event.get('note',''),'category':'outings','format':'Watchlist','search':json.dumps(event,ensure_ascii=False)})
(ROOT/'data/site-index.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
print('Indexed',len(rows),'public pages and event entries')

# Small independently cacheable chunks keep publication and client parsing bounded.
chunk_dir=ROOT/'data/site-search';chunk_dir.mkdir(exist_ok=True)
chunks=[];batch=[];size=0
for row in rows:
 encoded=json.dumps(row,ensure_ascii=False,separators=(',',':'))
 if batch and size+len(encoded.encode('utf-8'))>48000:
  chunks.append(batch);batch=[];size=0
 batch.append(row);size+=len(encoded.encode('utf-8'))
if batch:chunks.append(batch)
manifest=[]
for i,batch in enumerate(chunks):
 name=f'data/site-search/chunk-{i:02d}.json'
 (ROOT/name).write_text(json.dumps(batch,ensure_ascii=False,separators=(',',':'))+'\n')
 manifest.append('/'+name+'?v=20261004-illustrated')
(ROOT/'data/site-index-manifest.json').write_text(json.dumps(manifest,separators=(',',':'))+'\n')
print('Wrote',len(chunks),'bounded search chunks')
