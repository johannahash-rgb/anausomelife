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
    additions=[
        dict(term='Multilingual communication & AAC',cat='Communication',
             plain='Communication support that includes the languages a person uses with family and community.',
             detail='AAC assessment should consider the person’s languages, vocabulary, communication partners and cultural context. A system that works only in English may leave someone unable to participate with important people in their life.',
             why='A family should not have to choose between communication access and their home language.',
             look='A person uses one language with a grandparent and another at school. Their communication board or device needs useful vocabulary and partner support for both settings.',
             do='Tell the SLP which languages matter, who uses them and when. Ask about multilingual vocabulary, switching languages and trained interpretation for assessment or meetings.',
             ask='How will this communication system help me communicate with my family in the languages we actually use?',
             note='Knowing more than one language is not itself a communication disorder. A translated word list alone does not establish that a system is accessible or culturally appropriate.',
             sources=[{'label':'ASHA: Multilingual service delivery','url':'https://www.asha.org/practice-portal/professional-issues/multilingual-service-delivery/','kind':'Professional guidance'},{'label':'ASHA: Augmentative and alternative communication','url':'https://www.asha.org/practice-portal/professional-issues/augmentative-and-alternative-communication/','kind':'Clinical guidance'}],related=['AAC','Communication partner','Multimodal communication']),
        dict(term='Plain language & Easy Read',cat='Identity & support',
             plain='Two ways to make information easier to understand. They are related, but not identical.',
             detail='Plain language uses familiar words, clear organization and direct explanations. Easy Read typically adds shorter text, generous spacing and pictures that support each idea. A page is not necessarily Easy Read just because it has pictures or a larger-text button.',
             why='People need usable information to take part in decisions about their lives.',
             look='A service sends a long care document. The person asks for a short explanation, relevant pictures and time to discuss one decision at a time.',
             do='Ask what format the person prefers. Check understanding without turning the conversation into a test, and offer another explanation when needed.',
             ask='Can you explain the choices in a format I can understand and give me time to ask questions?',
             note='This glossary uses plain-language explanations; it is not a validated Easy Read edition. Pictures and simplified wording should support access without replacing important details.',
             sources=[{'label':'ASAN: Plain Language Resources','url':'https://autisticadvocacy.org/resources/','kind':'Autistic-led accessible resources'}],related=['Supported decision-making','Communication Bill of Rights']),
        dict(term='Self-advocacy & supported self-advocacy',cat='Rights & safety',
             plain='Expressing what matters to you and having help to do that when you need it.',
             detail='Self-advocacy can include speech, AAC, gestures, signs, choosing between options or clearly refusing. Supporters can help someone understand choices and communicate a view without substituting their own preference. Advocacy is not reserved for people who can speak, read or manage a meeting independently.',
             why='A caregiver’s knowledge matters, and the disabled person’s own preferences also need a reliable way into decisions.',
             look='Before a planning meeting, someone reviews accessible choices with a trusted supporter. During the meeting, the team addresses them directly and waits for their response.',
             do='Ask the person how they want to participate. Record what they expressed, what was observed and what a supporter is interpreting as separate information.',
             ask='What support would let me have more say in this decision?',
             note='An interpretation of behavior is not automatically a confirmed statement of the person’s wishes. Be transparent about uncertainty and keep offering accessible ways to agree, disagree or change course.',
             sources=[{'label':'ASAN: What we believe','url':'https://autisticadvocacy.org/about-asan/what-we-believe/','kind':'Autistic-led rights perspective'},{'label':'NJC: Communication Bill of Rights, third edition','url':'https://www.asha.org/njc/communication-bill-of-rights/','kind':'Communication rights guidance'}],related=['Assent','Autonomy & self-determination','Supported decision-making'])
    ]
    for item in additions:
        item['flag']=''
        terms.append(item)
    for term in terms:
        if term['term']=='Disability justice & intersectionality':
            term['do']='Ask whose access needs are being missed: people of color, LGBTQ+ people, multilingual families, people with intellectual disabilities and people with fewer financial resources. Offer concrete participation supports, and avoid asking one person to represent everyone.'
            term['sources'].append({'label':'ASAN: Civil rights are disability rights','url':'https://autisticadvocacy.org/about-asan/solidarity/','kind':'Autistic-led rights perspective'})
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
    text=text.replace('Updated October 20, 2026.', 'Updated October 21, 2026.')
    text=text.replace('We use autistic person by default and respect individual preference.', 'This guide welcomes disabled readers, family members, paid supporters and professionals. We use autistic person by default and respect individual preference. Language, race, income, gender and family structure can affect access; nobody should have to use the perfect vocabulary to ask for help.')
    text=text.replace('20261020-expanded-v2','20261021-inclusive-v3')
    page.write_text(text,encoding='utf-8')
    for path,addition,marker in [(root/'assets/caregiver-glossary.css',CSS,'/* Final glossary integration:'),(root/'assets/caregiver-glossary.js',JS,'/* Final glossary toolbar measurements')]:
        source=path.read_text()
        if marker not in source:path.write_text(source+'\n'+addition,encoding='utf-8')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('.'))
    build(parser.parse_args().root)
