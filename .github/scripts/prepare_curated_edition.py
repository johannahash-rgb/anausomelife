#!/usr/bin/env python3
"""Keep shared navigation and editorial assets current in the published artifact."""
import argparse,re,html
from html.parser import HTMLParser
from pathlib import Path
VERSION='20261016-family-organizer'
class Meta(HTMLParser):
    def __init__(self):super().__init__();self.tags={}
    def handle_starttag(self,tag,attrs):
        if tag=='meta':
            a=dict(attrs);self.tags[a.get('property') or a.get('name')]=a.get('content','')
def complete_social(source):
    if '</head>' not in source:return source
    parsed=Meta();parsed.feed(source.split('</head>',1)[0]);tags=parsed.tags
    if not tags.get('og:image'):return source
    desired={'twitter:card':'summary_large_image','twitter:image':tags['og:image'],
             'twitter:image:alt':tags.get('og:image:alt','An AUsome Life'),
             'og:site_name':'An AUsome Life'}
    extra=[]
    for key,value in desired.items():
        if key not in tags:
            attr='property' if key.startswith('og:') else 'name'
            extra.append('<meta '+attr+'="'+key+'" content="'+html.escape(value,quote=True)+'">')
    return source.replace('</head>',''.join(extra)+'</head>',1)

def prepare(root):
    count=0
    for page in root.rglob('*.html'):
        if any(p in {'.git','docs','tests','node_modules'} for p in page.relative_to(root).parts):continue
        s=page.read_text(encoding='utf-8');before=s
        s=complete_social(s)
        for asset in ['editorial.css','global-nav.js']:
            s=re.sub(r'(/assets/'+re.escape(asset)+r')(?:\?[^"\s<>]+)?',r'\1?v='+VERSION,s)
        if 'class="curated-home"' in s:
            s=re.sub(r'<script[^>]+src="/assets/home-dynamic.js[^>]*></script>','',s)
        if s!=before:page.write_text(s,encoding='utf-8');count+=1
    print('Prepared editorial assets on',count,'pages')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    prepare(parser.parse_args().root)
