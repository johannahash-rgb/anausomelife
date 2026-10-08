#!/usr/bin/env python3
"""Static site-wide links, assets, anchors, metadata, sitemap and optional external URL audit."""
import argparse,collections,concurrent.futures,html,json,os,posixpath,re,sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

SITE_HOSTS={"anausomelife.com","www.anausomelife.com"}
MEDIA_TAGS={"img","source","video","audio","track","iframe","script","embed"}
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs=[];self.ids=[];self.images=[];self.metadata={}
        self.lang=None;self.title="";self.in_title=False;self.h1=0;self.canonical=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="html":self.lang=a.get("lang")
        if tag=="title":self.in_title=True
        if tag=="h1":self.h1+=1
        if a.get("id"):self.ids.append(a["id"])
        if tag=="a" and a.get("name"):self.ids.append(a["name"])
        if tag in ("a","area","link") and a.get("href") is not None:
            self.refs.append((tag,"href",a["href"],self.getpos()[0]))
        if tag=="link" and "canonical" in a.get("rel","").lower():
            self.canonical.append(a.get("href",""))
        if tag in MEDIA_TAGS:
            for k in ("src","poster"):
                if a.get(k):self.refs.append((tag,k,a[k],self.getpos()[0]))
            if a.get("srcset"):
                for item in a["srcset"].split(","):
                    part=item.strip().split()
                    if part:self.refs.append((tag,"srcset",part[0],self.getpos()[0]))
        if tag=="form" and a.get("action"):self.refs.append((tag,"action",a["action"],self.getpos()[0]))
        if tag=="img":self.images.append((a.get("alt"),a.get("src",""),self.getpos()[0]))
        if tag=="meta":
            key=(a.get("name") or a.get("property") or "").lower()
            if key:self.metadata.setdefault(key,[]).append(a.get("content",""))
            if key in ("og:image","twitter:image") and a.get("content"):
                self.refs.append(("meta",key,a["content"],self.getpos()[0]))
    def handle_endtag(self,tag):
        if tag=="title":self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title+=data

def resolve(page,ref):
    ref=html.unescape(str(ref)).strip()
    if not ref:return "empty",None,""
    if ref=="#":return "placeholder",None,""
    if ref.startswith(("//","http://","https://")):
        parsed=urlparse("https:"+ref if ref.startswith("//") else ref)
        if parsed.hostname not in SITE_HOSTS:return "external",ref,""
        target=parsed.path or "/";fragment=parsed.fragment
    elif re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:",ref):return "scheme",ref,""
    else:
        parsed=urlparse(ref);target=parsed.path;fragment=parsed.fragment
    if not target:return "local",page,unquote(fragment)
    target=unquote(target)
    if any(t in target for t in (chr(36)+"{","{{","{%","<%")):return "dynamic",target,""
    rel=target.lstrip("/") if target.startswith("/") else posixpath.join(posixpath.dirname(page),target)
    if target.endswith("/") or not rel:rel=posixpath.join(rel,"index.html")
    rel=posixpath.normpath(rel)
    if rel.startswith("../"):return "path-traversal",rel,""
    return "local",rel,unquote(fragment)

def probe(url):
    for method in ("HEAD","GET"):
        try:
            request=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; SiteLinkAudit/1.0)"},method=method)
            with urlopen(request,timeout=8) as response:
                return {"url":url,"status":response.status,"classification":"ok"}
        except HTTPError as e:
            if method=="HEAD" and e.code in (403,405,429,501):continue
            return {"url":url,"status":e.code,"classification":"broken" if e.code in (404,410) else "blocked_or_uncertain"}
        except (URLError,TimeoutError,ConnectionError) as e:
            if method=="HEAD":continue
            return {"url":url,"status":None,"classification":"unreachable_or_uncertain","error":str(e)[:120]}
        except Exception as e:
            return {"url":url,"status":None,"classification":"unreachable_or_uncertain","error":str(e)[:120]}
    return {"url":url,"status":None,"classification":"unreachable_or_uncertain"}

def audit(root,external_limit):
    excluded={".git","_site","node_modules"}
    assets={str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and not excluded.intersection(p.relative_to(root).parts)}
    pages={p:root/p for p in sorted(assets) if p.endswith(".html")}
    documents={};issues=[];external=collections.defaultdict(set);counts=collections.Counter()
    for path,file in pages.items():
        try:
            doc=Page();doc.feed(file.read_text(encoding="utf-8",errors="replace"));documents[path]=doc
        except Exception as e:issues.append({"severity":"high","kind":"read-failed","page":path,"error":str(e)[:120]})
    for path,doc in documents.items():
        if not doc.title.strip():issues.append({"severity":"medium","kind":"missing-title","page":path})
        if not doc.lang:issues.append({"severity":"medium","kind":"missing-lang","page":path})
        if not doc.metadata.get("description"):issues.append({"severity":"medium","kind":"missing-description","page":path})
        if doc.h1!=1:issues.append({"severity":"medium","kind":"h1-count","page":path,"count":doc.h1})
        if not doc.canonical:issues.append({"severity":"low","kind":"missing-canonical","page":path})
        if not doc.metadata.get("og:image"):issues.append({"severity":"low","kind":"missing-social-image","page":path})
        for label,n in collections.Counter(doc.ids).items():
            if n>1:issues.append({"severity":"medium","kind":"duplicate-id","page":path,"id":label,"count":n})
        for alt,src,line in doc.images:
            if alt is None:issues.append({"severity":"medium","kind":"missing-img-alt","page":path,"line":line,"src":src})
        for tag,attr,ref,line in doc.refs:
            counts["references"]+=1
            kind,target,fragment=resolve(path,ref)
            if kind=="external":
                counts["external_references"]+=1
                if target.startswith("https://"):external[target].add(path)
            elif kind in ("scheme","dynamic"):counts[kind+"_references"]+=1
            elif kind in ("empty","placeholder","path-traversal"):
                issues.append({"severity":"medium","kind":kind,"page":path,"line":line,"ref":ref})
            elif kind=="local":
                counts["local_references"]+=1
                if target not in assets:
                    alternatives=[target+".html",posixpath.join(target,"index.html")]
                    fix=next((t for t in alternatives if t in assets),None)
                    issues.append({"severity":"high","kind":"missing-local-target","page":path,"line":line,"ref":ref,"resolved":target,"suggestion":fix})
                elif fragment and target in documents and fragment not in documents[target].ids:
                    issues.append({"severity":"high","kind":"missing-fragment","page":path,"line":line,"ref":ref,"resolved":target,"fragment":fragment})
    for css in sorted(p for p in assets if p.endswith(".css")):
        content=(root/css).read_text(encoding="utf-8",errors="replace")
        for url in re.findall(r'url\(\s*[\'"]?([^\)\'"]+)',content,flags=re.I):
            if url.strip().startswith(("#","data:")):continue
            counts["css_urls"]+=1
            kind,target,_=resolve(css,url)
            if kind=="local" and target not in assets:
                issues.append({"severity":"high","kind":"missing-css-asset","page":css,"ref":url,"resolved":target})
            if kind=="external" and target.startswith("https://"):external[target].add(css)
    sitemap_urls=[]
    if (root/"sitemap.xml").exists():
        sitemap_urls=re.findall(r"<loc>\s*(.*?)\s*</loc>",(root/"sitemap.xml").read_text(errors="replace"),flags=re.I)
        for url in sitemap_urls:
            kind,target,_=resolve("sitemap.xml",url)
            if kind=="local" and target not in assets:
                issues.append({"severity":"high","kind":"sitemap-missing-target","page":"sitemap.xml","ref":url,"resolved":target})
    if (root/"robots.txt").exists():
        for line in (root/"robots.txt").read_text(errors="replace").splitlines():
            if line.lower().startswith("sitemap:"):
                kind,target,_=resolve("robots.txt",line.partition(":")[2].strip())
                if kind=="local" and target not in assets:issues.append({"severity":"high","kind":"robots-missing-sitemap","page":"robots.txt","ref":line})
    # Follow user-facing links stored in the site's JSON catalogs and navigation data.
    urlkeys={"url","href","link","linkurl","route","pathname","src","source","image","imageurl","image_url","cover","thumbnail","logo","poster","download","canonical","path","page","photo","photourl","mapurl"}
    def walk_json(value,path,key=""):
        if isinstance(value,dict):
            for k,v in value.items():walk_json(v,path,str(k))
        elif isinstance(value,list):
            for v in value:walk_json(v,path,key)
        elif isinstance(value,str):
            lower=key.lower().replace("-","_")
            isref=lower in urlkeys or lower.endswith(("_url","url","_href","_src","_link"))
            if not isref:return
            ref=value.strip()
            if not ref or not (ref.startswith(("/",".","http:","https:","#")) or re.search(r"\.(?:html|png|jpe?g|webp|svg|pdf|js|css)(?:[#?]|$)",ref,re.I)):return
            counts["json_references"]+=1
            kind,target,fragment=resolve(path,ref)
            if kind=="external" and target.startswith("https://"):external[target].add(path)
            elif kind=="local":
                # Some data catalogs deliberately store repo-root paths without '/'.
                basename=unquote(ref.split("#")[0].split("?")[0]).lstrip("/")
                if target not in assets and not ref.startswith(("/","./","../","http")) and basename in assets:
                    counts["json_site_root_paths"]+=1
                elif target not in assets:
                    issues.append({"severity":"high","kind":"json-missing-local-target","page":path,"field":key,"ref":ref,"resolved":target})
                elif fragment and target=="calendar.html" and fragment.startswith("event-"):
                    # assets/events.js creates these IDs and now supports archived deep links.
                    counts["javascript_rendered_calendar_anchors"]+=1
                elif fragment and target in documents and fragment not in documents[target].ids:
                    issues.append({"severity":"high","kind":"json-missing-fragment","page":path,"field":key,"ref":ref,"resolved":target})
    for path in sorted(p for p in assets if p.endswith(".json")):
        try:walk_json(json.loads((root/path).read_text(encoding="utf-8")),path)
        except Exception as e:issues.append({"severity":"medium","kind":"invalid-json","page":path,"error":str(e)[:150]})
    # Check simple, literal rooted script references; dynamic routes are excluded.
    for path in sorted(p for p in assets if p.endswith((".js",".cjs",".mjs"))):
        js=(root/path).read_text(encoding="utf-8",errors="replace")
        for ref in re.findall(r'''["'\x60](/[^"'\x60 <>{}]+\.(?:html|js|css|png|jpg|jpeg|webp|svg|pdf)(?:[#?][^"'\x60]*)?)["'\x60]''',js):
            counts["js_static_references"]+=1
            kind,target,fragment=resolve(path,ref)
            if kind=="local" and target not in assets:
                issues.append({"severity":"medium","kind":"js-static-path-suspect","page":path,"ref":ref,"resolved":target})
    # Include sources for external errors in the downloaded audit.
    urls=sorted(external,key=lambda u:(-len(external[u]),u))[:external_limit]
    external_results=[]
    if urls:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            external_results=list(pool.map(probe,urls))
    kinds=collections.Counter(x["kind"] for x in issues)
    return {"scope":"All HTML page references, same-site anchors, image alt, CSS url() paths, sitemap, metadata and sampled external HTTP links; not a full keyboard or JS interaction audit.",
            "counts":{"pages":len(documents),"repo_files":len(assets),"unique_external":len(external),"sitemap_entries":len(sitemap_urls),**counts},
            "issue_counts":dict(kinds),"issues":issues,"external_results":external_results,"external_sources":{url:sorted(source) for url,source in external.items()}}
def main():
    p=argparse.ArgumentParser();p.add_argument("--root",default=".");p.add_argument("--external-limit",type=int,default=0);p.add_argument("--strict",action="store_true");a=p.parse_args()
    result=audit(Path(a.root).resolve(),a.external_limit)
    Path("site-audit-report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("SITE_AUDIT_SUMMARY",json.dumps({"counts":result["counts"],"issue_counts":result["issue_counts"],"external_probes":len(result["external_results"])}),flush=True)
    for issue in result["issues"]:
        if issue["severity"]=="high":print("SITE_AUDIT_HIGH",json.dumps(issue,ensure_ascii=False),flush=True)
    for x in result["external_results"]:
        if x["classification"]=="broken":print("EXTERNAL_LINK_BROKEN",json.dumps(x),flush=True)
    summary=os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a") as f:
            f.write("## An AUsome Life — site-wide audit\n")
            f.write(f"- HTML pages: {result['counts']['pages']}\n- References checked: {result['counts']['references']}\n")
            f.write(f"- Broken local paths: {result['issue_counts'].get('missing-local-target',0)}\n")
            f.write(f"- Missing anchors: {result['issue_counts'].get('missing-fragment',0)}\n")
            f.write(f"- External URLs probed: {len(result['external_results'])}\n")
            f.write("- Detailed JSON available as workflow artifact.\n")
    if a.strict and any(x["severity"]=="high" for x in result["issues"]):sys.exit(1)
if __name__=="__main__":main()
