#!/usr/bin/env python3
"""Compatibility entry point and final integration for the glossary edition."""
import argparse, importlib.util, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('glossary_v2',HERE/'glossary_v2.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
_original_revise=core.revise

def reviewed_revise(terms,sources):
    terms=_original_revise(terms,sources)
    advocacy={'label':'ASAN: For Whose Benefit? (includes Easy Read and Plain Language)','url':'https://autisticadvocacy.org/policy/briefs/intervention-ethics/','kind':'Autistic-led critique'}
    for term in terms:
        if term['term'] in ('ABA — Applied Behavior Analysis','Social validity','Neurodiversity-affirming practice'):
            term['sources'].append(dict(advocacy))
        if term['term']=='Gestalt language processing (GLP)':
            term['sources'].extend([
                {'label':'Lorang and colleagues: GLP/NLA—concerns and common ground','url':'https://pubs.asha.org/doi/10.1044/2025_PERSP-25-00055','kind':'Research-informed critique'},
                {'label':'Blanc and colleagues: the proposed NLA framework','url':'https://pubs.asha.org/doi/10.1044/2023_PERSP-23-00098','kind':'Proponents’ viewpoint; not proof of effectiveness'}])
        if term['term']=='Massachusetts N1 & N2 notices':
            term['sources'].append({'label':'Massachusetts DESE: Notice of School District Refusal to Act','url':'https://www.doe.mass.edu/specialeducation/iep/refusal-to-act/','kind':'Massachusetts official form'})
        if term['term'] in ('Supported decision-making','Autonomy & self-determination'):
            term['sources'].append({'label':'ASAN: self-determination and the right to make choices','url':'https://autisticadvocacy.org/self-determination/','kind':'Autistic-led rights guidance'})
    return terms
core.revise=reviewed_revise

CSS='''/* Final glossary integration: native no-JS reading and unobscured headings. */
.cg-root:not(.cg-enhanced) .cg-workspace{display:block}
.cg-root:not(.cg-enhanced) .cg-start nav{display:none!important}
.cg-tools>summary{display:flex;align-items:center;justify-content:center;gap:8px;white-space:nowrap}
.cg-tools>summary::after{display:inline!important;position:static!important;font-size:12px;margin:0!important}
.cg-term{scroll-margin-top:calc(var(--cg-toolbar-height,180px) + 18px)}
.cg-sidebar{top:calc(var(--cg-toolbar-height,160px) + 20px)}
.cg-mobile-start{display:none}
@media(max-width:760px){
.cg-root .cg-start{display:none}
.cg-root .cg-mobile-start{display:block;margin-top:18px;border:1px solid var(--cg-line);border-radius:12px;background:var(--cg-soft);padding:0 15px;font-size:14px}
.cg-mobile-start>summary{min-height:48px;padding:12px 0;font-weight:700}
.cg-mobile-start nav{display:grid;gap:4px;padding-bottom:12px}
.cg-mobile-start nav button{display:flex;justify-content:space-between;gap:10px;background:transparent;border:0;border-top:1px solid var(--cg-line);font-size:14px;border-radius:0;padding:11px 0}
.cg-root .cg-reading-row #cg-compare{display:none}
.cg-tools>summary{min-height:44px;font-size:13px}
.cg-tools>div{top:51px}
.cg-term{scroll-margin-top:calc(var(--cg-toolbar-height,205px) + 18px)}
}
@media print{.cg-mobile-start{display:none!important}}
'''
JS='''/* Final glossary toolbar measurements and compact mobile menu. */
(()=>{const root=document.querySelector('.cg-v2.cg-enhanced');if(!root)return;
const toolbar=root.querySelector('#cg-search-tools');
const measure=()=>{if(toolbar)root.style.setProperty('--cg-toolbar-height',Math.ceil(toolbar.getBoundingClientRect().height)+'px');};
measure();if(typeof ResizeObserver==='function')new ResizeObserver(measure).observe(toolbar);else window.addEventListener('resize',measure);
root.querySelectorAll('[data-tool="compare"]').forEach(button=>button.addEventListener('click',()=>root.querySelector('#cg-compare').click()));
})();
'''

def build(root):
    root=Path(root);core.build(root)
    page=root/'caregiver-glossary.html'
    if not page.exists():return
    text=page.read_text()
    text=text.replace('<button data-tool="questions">Print my saved questions</button>','<button data-tool="questions">Print my saved questions</button><button data-tool="compare">Often mixed-up terms</button>',1)
    aside=re.search(r'<aside class="cg-start">(.*?)</aside>',text,re.S)
    if aside:
        nav=re.search(r'<nav[^>]*data-js>(.*?)</nav>',aside[1],re.S)
        if nav:
            mobile='<details class="cg-mobile-start" data-js><summary>Not sure? Browse by situation</summary><nav aria-label="Situations on a small screen">'+nav[1]+'</nav></details>'
            marker='<p class="cg-reassure">You do not need to learn every word. Find the one you need today.</p>'
            text=text.replace(marker,marker+mobile,1)
    page.write_text(text,encoding='utf-8')
    for path,addition,marker in [(root/'assets/caregiver-glossary.css',CSS,'/* Final glossary integration:'),(root/'assets/caregiver-glossary.js',JS,'/* Final glossary toolbar measurements')]:
        source=path.read_text()
        if marker not in source:path.write_text(source+'\n'+addition,encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('.'))
    build(parser.parse_args().root)
