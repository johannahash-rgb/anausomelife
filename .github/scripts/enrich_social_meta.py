#!/usr/bin/env python3
"""Add page-specific Open Graph and Twitter image metadata to public HTML during deployment.

Uses existing, approved article photos or illustrations only; never synthesizes images.
Redirect shells, site fragments and print pages are left alone.
"""
import argparse,html,json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,urljoin

DOMAIN="https://anausomelife.com/"
FALLBACK="/assets/editorial/coastal-walk.webp"
IMAGE_PATTERN=re.compile(r"\.(?:png|jpe?g|webp)(?:$|[?#])",re.I)
class Images(HTMLParser):
    def __init__(self):super().__init__();self.images=[]
    def handle_starttag(self,tag,attrs):
        if tag=="img":self.images.append(dict(attrs))
def metadata(page,root):
    source=page.read_text(encoding="utf-8",errors="replace")
    head=re.search(r"<head\b[^>]*>(.*?)</head\s*>",source,re.I|re.S)
    if not head:return False,"not-a-full-page"
    body=head.group(1)
    if re.search(r'<meta\b[^>]*http-equiv=["\']refresh["\']',body,re.I):return False,"redirect"
    if re.search(r'<meta\b[^>]*property=["\']og:image["\']',body,re.I):return False,"already-present"
    title_match=re.search(r"<title[^>]*>(.*?)</title\s*>",body,re.I|re.S)
    if not title_match:return False,"no-title"
    title=html.unescape(re.sub(r"<[^>]+>","",title_match.group(1))).strip()
    if not title:return False,"empty-title"
    img=Images();img.feed(source)
    preferred=None;preferred_alt="";preferred_score=-1000
    for i,v in enumerate(img.images):
        ref=(v.get("src") or "").split("#")[0].split("?")[0]
        if not ref or ref.startswith(("http://","https://","//","data:")) or not IMAGE_PATTERN.search(ref):continue
        url=urljoin(DOMAIN+str(page.relative_to(root)),ref)
        local=urlparse(url).path.lstrip("/")
        file=root/local
        if not file.is_file():continue
        try:size=file.stat().st_size
        except OSError:continue
        if size<15000:continue
        alt=html.unescape(v.get("alt") or "").strip()
        lower=ref.lower()
        if "coastal-emblem" in lower or "favicon" in lower or "logo" in lower:continue
        score=5 if alt else 0
        if "fetchpriority" in v and v["fetchpriority"]=="high":score+=30
        if v.get("loading")=="eager":score+=22
        if "/family-outings/" in lower or "/family-notes/" in lower:score+=7
        if "/long-guide-studies/" in lower:score+=6
        if "/navigation-" in lower or "/brand-sketches/" in lower:score-=12
        if v.get("width","").isdigit() and int(v["width"])>=1000:score+=4
        if v.get("height","").isdigit() and int(v["height"])>=630:score+=4
        score-=i*0.85
        if score>preferred_score:
            preferred=url;preferred_alt=alt;preferred_score=score
    if not preferred:
        fallback_file=root/FALLBACK.lstrip("/")
        if not fallback_file.is_file():return False,"no-fallback-image"
        preferred=urljoin(DOMAIN,FALLBACK)
        preferred_alt="An AUsome Life — New England family life and practical outings"
    descmatch=re.search(r'<meta\b[^>]*name=["\']description["\'][^>]*content=(["\'])(.*?)\1',body,re.I|re.S)
    desc=html.unescape(descmatch.group(2)) if descmatch else ""
    canonicalmatch=re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=(["\'])(.*?)\1',body,re.I|re.S)
    canonical=canonicalmatch.group(2) if canonicalmatch else urljoin(DOMAIN,str(page.relative_to(root)))
    if "/preview-" in canonical or page.name.startswith("preview-"):return False,"preview"
    def esc(t):return html.escape(str(t),quote=True)
    extras=[]
    if not re.search(r'<meta\b[^>]*property=["\']og:type["\']',body,re.I):
        page_kind="website" if page.name in {"index.html","blog.html","about.html","library.html","favorite-places.html","calendar.html","contact.html","kid-fun.html","picture-card-library.html","communication-card-generator.html","visit-story.html","privacy.html","accessibility.html"} or "/topics/" in "/"+str(page.relative_to(root)) else "article"
        extras.append('<meta property="og:type" content="'+page_kind+'">')
    if not re.search(r'<meta\b[^>]*property=["\']og:site_name["\']',body,re.I):extras.append('<meta property="og:site_name" content="An AUsome Life">')
    if not re.search(r'<meta\b[^>]*property=["\']og:title["\']',body,re.I):extras.append('<meta property="og:title" content="'+esc(title)+'">')
    if desc and not re.search(r'<meta\b[^>]*property=["\']og:description["\']',body,re.I):
        extras.append('<meta property="og:description" content="'+esc(desc)+'">')
    if not re.search(r'<meta\b[^>]*property=["\']og:url["\']',body,re.I):extras.append('<meta property="og:url" content="'+esc(canonical)+'">')
    extras.append('<meta property="og:image" content="'+esc(preferred)+'">')
    extras.append('<meta property="og:image:alt" content="'+esc(preferred_alt)+'">')
    if not re.search(r'<meta\b[^>]*name=["\']twitter:card["\']',body,re.I):extras.append('<meta name="twitter:card" content="summary_large_image">')
    if not re.search(r'<meta\b[^>]*name=["\']twitter:image["\']',body,re.I):extras.append('<meta name="twitter:image" content="'+esc(preferred)+'">')
    close=head.end()-len("</head>")
    source=source[:close]+"\n"+"\n".join(extras)+"\n"+source[close:]
    page.write_text(source,encoding="utf-8")
    return True,"specific-photo-or-art" if preferred_score>=0 else "fallback"
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("_site"));args=p.parse_args()
    root=args.root.resolve();stats={};changed=[]
    for page in sorted(root.rglob("*.html")):
        status,reason=metadata(page,root)
        stats[reason]=stats.get(reason,0)+1
        if status:changed.append(str(page.relative_to(root)))
    print("SOCIAL_METADATA_SUMMARY",json.dumps({"counts":stats,"updated":len(changed),"first_updated":changed[:15]}))
if __name__=="__main__":main()
