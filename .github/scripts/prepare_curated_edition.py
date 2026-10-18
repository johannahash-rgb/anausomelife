#!/usr/bin/env python3
"""Keep shared navigation and editorial assets current in the published artifact."""
import argparse,re,html,importlib.util
from html.parser import HTMLParser
from pathlib import Path
VERSION='20261018-growth-readiness'
VERSIONED_ASSETS=(
    'editorial.css','global-nav.js','access-tools.css','access-tools.js',
    'reader-pathways.css','brand-design.css','brand-banner.css','brand-banner.js',
    'library-browse.css','card-catalog.js','card-collection.js','card-collection.css',
    'immersion.js','story-share.js',
)
JOURNAL_PINS=(
    '/wayne-newton-flamingo-bucket-list-self-care.html',
    '/get-in-the-photograph.html',
    '/rangeley-grandparents-field-note.html',
)

def refresh_asset_versions(source):
    """Use one edition version even for assets injected by a later transform."""
    for asset in VERSIONED_ASSETS:
        source=re.sub(r'(/assets/'+re.escape(asset)+r')(?:\?[^"\s<>]+)?',r'\1?v='+VERSION,source)
    return source

def readable_heading_breaks(source):
    """A responsive line break must still separate words when hidden by CSS."""
    return re.sub(r'<h[1-6]\b[^>]*>.*?</h[1-6]>',lambda match:re.sub(r'(<br\s*/?>)(?=\S)',r'\1 ',match[0],flags=re.I),source,flags=re.S|re.I)

def pin_journal_stories(source):
    """Keep the owner's selected stories ahead of newly added journal entries."""
    match=re.search(r'(<ol class="journal-recent-list"[^>]*>)(.*?)(</ol>)',source,re.S)
    if not match:return source
    cards=re.findall(r'<li>.*?</li>',match.group(2),re.S)
    pinned=[]
    for url in JOURNAL_PINS:
        found=[card for card in cards if 'href="'+url+'"' in card]
        if len(found)!=1:raise ValueError('Expected one journal card for '+url)
        pinned.append(found[0])
    ordered=pinned+[card for card in cards if card not in pinned]
    body='\n  '+'\n\n  '.join(ordered)+'\n'
    return source[:match.start(2)]+body+source[match.end(2):]

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
        s=readable_heading_breaks(s)
        if page.relative_to(root).as_posix()=='blog.html':
            s=pin_journal_stories(s)
        s=complete_social(s)
        s=refresh_asset_versions(s)
        # Add the tools to complete pages, including those without shared navigation.
        # Leave redirect pages and reusable content fragments alone.
        if re.search(r'<main\b',s,re.I) and '</head>' in s:
            if '/assets/access-tools.css' not in s:
                s=s.replace('</head>','<link rel="stylesheet" href="/assets/access-tools.css?v='+VERSION+'"></head>',1)
            if '/assets/access-tools.js' not in s:
                s=s.replace('</body>','<script src="/assets/access-tools.js?v='+VERSION+'" defer></script></body>',1)
        if 'class="curated-home"' in s:
            s=re.sub(r'<script[^>]+src="/assets/home-dynamic.js[^>]*></script>','',s)
        if s!=before:page.write_text(s,encoding='utf-8');count+=1
    print('Prepared editorial assets on',count,'pages')
    spec=importlib.util.spec_from_file_location('reader_pathways',Path(__file__).with_name('reader_pathways.py'))
    pathways=importlib.util.module_from_spec(spec);spec.loader.exec_module(pathways)
    pathways.prepare(root)
    spec=importlib.util.spec_from_file_location('growth_readiness',Path(__file__).with_name('growth_readiness.py'))
    growth=importlib.util.module_from_spec(spec);spec.loader.exec_module(growth)
    growth.prepare(root)
    # Contextual modules may add a stylesheet using their own older version.
    # Normalize those newly inserted references in this build, not the next one.
    for page in root.rglob('*.html'):
        if any(p in {'.git','docs','tests','node_modules'} for p in page.relative_to(root).parts):continue
        source=page.read_text(encoding='utf-8')
        updated=refresh_asset_versions(source)
        if updated!=source:page.write_text(updated,encoding='utf-8')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    prepare(parser.parse_args().root)
