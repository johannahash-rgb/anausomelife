"""Check documented media safeguards. This is not legal clearance or moderation."""
import argparse,json,re,sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

class Page(HTMLParser):
 def __init__(self): super().__init__();self.media=[];self.affiliate=False;self.text=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('img','video','audio','source','iframe'):
   for key in ('src','poster'):
    if a.get(key):self.media.append(a[key])
   if a.get('srcset'):
    self.media.extend(item.strip().split()[0] for item in a['srcset'].split(',') if item.strip())
  if tag=='a' and re.search(r'amzn\.to|[?&](?:tag|ascsubtag|aff|affid|affiliate_id)=|shareasale|rstyle\.me|skimresources|impact\.com',a.get('href',''),re.I):self.affiliate=True
 def handle_data(self,text):self.text.append(text)

def audit(root):
 failures=[];warnings=[];counts={'pages':0,'remote_media':0,'affiliate_pages':0}
 source=root/'content/business-logos.json';logos=json.loads(source.read_text()) if source.exists() else {}
 blocked={v.get('retiredAsset') or v.get('asset') for v in logos.values() if v.get('reuseStatus')!='cleared' or not v.get('permissionEvidence')}
 for p in root.rglob('*.html'):
  if any(part.startswith('.') for part in p.relative_to(root).parts):continue
  counts['pages']+=1;doc=Page();doc.feed(p.read_text());name=str(p.relative_to(root))
  for src in doc.media:
   if src in blocked:failures.append(f'{name}: media reuse not cleared: {src}')
   if src.startswith(('https://','http://','//')):
    counts['remote_media']+=1;warnings.append(f'{name}: review external media permissions and privacy: {urlparse(src).netloc}')
   if src.startswith('/') and not src.startswith('//') and not (root/src.split('?')[0].split('#')[0].lstrip('/')).exists():failures.append(f'{name}: missing local media: {src}')
  if doc.affiliate:
   counts['affiliate_pages']+=1;warnings.append(f'{name}: manually check clear disclosure next to each endorsement/link; a footer policy is insufficient')
 return {'scope':'HTML media references, documented retired logos, known affiliate-link patterns. Not a complete rights or legal review.','counts':counts,'failures':failures,'manual_review':sorted(set(warnings))}

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();result=audit(a.root);print(json.dumps(result,indent=2));sys.exit(bool(result['failures']))
